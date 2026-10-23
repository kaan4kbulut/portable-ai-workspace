#!/usr/bin/env python3
"""Sürüm nabzı: izlenen araçların kurulu ve son sürümünü karşılaştırır (yalnızca GET, ağ yalnızca burada).

Kullanım: python3 20-sistem/nabiz/takip.py [--rapor-yok]
Girdi : 20-sistem/nabiz/izlenenler.txt   (ad · tur · kimlik · komut [· sabit=X.Y.Z])
Çıktı : 20-sistem/durum/<host>/guncelleme-raporu.md (git dışı)
Çıkış : 0 her şey güncel; 1 yeni sürüm / destek bitişi / eksik kurulum / çevrimdışı.
Hiçbir şey kurmaz ya da yükseltmez. Sabitlenmiş araçlarda yalnızca "en az 7 gün önce yayımlanmış en yeni sürüm" raporlanır.
"""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

ZAMAN_ASIMI_S = 8
EN_FAZLA_BAYT = 8 * 1024 * 1024
BEKLEME_GUN = 7
SURUM = re.compile(r"(?<!\d)(\d+)\.(\d+)(?:\.(\d+))?(?![\w.-]*\w)")
TURLER = ("npm", "pypi", "github", "eol")


class CevrimDisi(Exception):
    """Ağ erişilemiyor."""


def kok_bul(baslangic: Path | None = None) -> Path:
    p = (baslangic or Path(__file__)).resolve()
    for d in [p, *p.parents]:
        if (d / "00-cekirdek" / "ANAYASA.md").is_file():
            return d
    raise SystemExit("atölye kökü bulunamadı (00-cekirdek/ANAYASA.md yok)")


def makine() -> str:
    return socket.gethostname().split(".")[0]


# --- ağ / süreç (testlerde taklit edilir) -------------------------------------------
def al(url: str) -> bytes:
    istek = urllib.request.Request(url, method="GET", headers={"User-Agent": "atolye-nabiz/1"})
    try:
        with urllib.request.urlopen(istek, timeout=ZAMAN_ASIMI_S) as yanit:
            govde = yanit.read(EN_FAZLA_BAYT + 1)
    except urllib.error.HTTPError:
        raise
    except (urllib.error.URLError, OSError) as e:
        raise CevrimDisi(str(e)) from e
    if len(govde) > EN_FAZLA_BAYT:
        raise ValueError("yanıt çok büyük")
    return govde


def calistir(komut: list[str]) -> str:
    p = subprocess.run(komut, capture_output=True, text=True, timeout=ZAMAN_ASIMI_S, check=False)
    if p.returncode:
        raise ValueError("sürüm okunamadı")
    return p.stdout.strip() or p.stderr.strip()


# --- ayrıştırma --------------------------------------------------------------------
def surum_ayikla(metin: str) -> str | None:
    m = SURUM.search(metin or "")
    return m.group(0) if m else None


def surum_demeti(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.split("."))


def izlenenleri_oku(yol: Path) -> list[dict]:
    satirlar = []
    for ham in yol.read_text(encoding="utf-8").splitlines():
        ham = ham.strip()
        if not ham or ham.startswith("#"):
            continue
        k = [x.strip() for x in ham.split("·")]
        if len(k) < 3 or k[1] not in TURLER:
            continue
        ek = {}
        for x in k[4:]:
            if "=" in x:
                a, b = x.split("=", 1)
                ek[a.strip()] = b.strip()
        satirlar.append({"ad": k[0], "tur": k[1], "kimlik": k[2],
                         "komut": k[3].split() if len(k) > 3 and k[3] else [], "sabit": ek.get("sabit")})
    return satirlar


def son_surum(oge: dict, getir, simdi: datetime) -> tuple[str | None, str]:
    """(son sürüm, not). Ağ yoksa CevrimDisi yükselir."""
    tur, kimlik = oge["tur"], oge["kimlik"]
    if tur == "npm":
        paket = quote(kimlik, safe="@").replace("/", "%2f")
        if oge["sabit"]:
            # Sabit araç: yayın zamanına bakıp en az 7 gün önce yayımlanmış en yeni kararlı sürümü bul.
            veri = json.loads(getir(f"https://registry.npmjs.org/{paket}"))
            sinir = simdi - timedelta(days=BEKLEME_GUN)
            adaylar = []
            for s, z in (veri.get("time") or {}).items():
                if re.fullmatch(r"\d+\.\d+\.\d+", s):
                    t = datetime.fromisoformat(z.replace("Z", "+00:00"))
                    if t <= sinir:
                        adaylar.append(s)
            if not adaylar:
                return None, "7 günü doldurmuş sürüm bulunamadı"
            return max(adaylar, key=surum_demeti), f"en yeni sürüm >= {BEKLEME_GUN} gün"
        return json.loads(getir(f"https://registry.npmjs.org/{paket}/latest"))["version"], ""
    if tur == "pypi":
        return json.loads(getir(f"https://pypi.org/pypi/{quote(kimlik, safe='')}/json"))["info"]["version"], ""
    if tur == "github":
        kok = ET.fromstring(getir(f"https://github.com/{kimlik}/releases.atom"))
        ns = "{http://www.w3.org/2005/Atom}"
        for e in kok.findall(ns + "entry"):
            baslik = e.findtext(ns + "title", "")
            bag = (e.find(ns + "link").get("href", "") if e.find(ns + "link") is not None else "")
            s = surum_ayikla(baslik) or surum_ayikla(bag.rsplit("/", 1)[-1])
            if s:
                return s, ""
        return None, "sürüm bulunamadı"
    if tur == "eol":
        veri = json.loads(getir(f"https://endoflife.date/api/{quote(kimlik, safe='')}.json"))
        return str(veri[0].get("latest")), json.dumps({"cycles": veri[:6]}, ensure_ascii=False)
    return None, "bilinmeyen tür"


def eol_durumu(notu: str, kurulu: str, simdi: datetime) -> str:
    try:
        cycles = json.loads(notu)["cycles"]
    except (ValueError, KeyError):
        return ""
    for c in cycles:
        if kurulu.split(".")[0] == str(c.get("cycle")).split(".")[0]:
            e = c.get("eol")
            if e is True or (isinstance(e, str) and e < simdi.date().isoformat()):
                return "DESTEK BİTMİŞ"
            return "destek sürüyor"
    return ""


def degerlendir(oge: dict, kurulu: str | None, son: str | None, cevrimdisi: bool, eol: str = "") -> tuple[str, bool]:
    """(durum metni, sorun mu)."""
    if kurulu is None:
        return "kurulu değil / okunamadı", True
    if cevrimdisi:
        return "çevrimdışı", True
    if son is None:
        return "denetlenemedi", True
    if eol == "DESTEK BİTMİŞ":
        return f"DESTEK BİTMİŞ; son {son}", True
    if oge["sabit"]:
        if kurulu != oge["sabit"]:
            return f"sabit {oge['sabit']} ama kurulu {kurulu}", True
        if surum_demeti(son) > surum_demeti(oge["sabit"]):
            return f"sabit {oge['sabit']}; aday {son} (yalnızca raporla, otomatik yükseltme yok)", False
        return f"sabit {oge['sabit']}; güncel", False
    if surum_demeti(kurulu) > surum_demeti(son):
        return "kurulu sürüm daha yeni", False
    if kurulu == son or (surum_demeti(kurulu) == surum_demeti(son)):
        return "güncel", False
    k, n = surum_demeti(kurulu), surum_demeti(son)
    if k[:2] == n[:2] and oge["tur"] != "eol":
        return f"bilgi: yama farkı ({son})", False
    if k[0] != n[0] and oge["tur"] != "eol":
        return "BÜYÜK SÜRÜM: kırıcı değişiklikleri incele", True
    if oge["tur"] == "eol":  # node: ana sürüm içinde yama farkı sorun sayılmaz
        return f"yeni yama var ({son})" if surum_demeti(kurulu)[0] == surum_demeti(son)[0] else "güncel (destek sürüyor)", False
    return "yeni sürüm var; elle incele", True


def rapor_uret(izlenen: list[dict], getir=al, calistir_=calistir, simdi: datetime | None = None) -> tuple[str, int]:
    simdi = simdi or datetime.now(timezone.utc)
    satirlar, sorun, sayac_ag = [], 0, 0
    for oge in izlenen:
        kurulu = None
        if oge["komut"]:
            try:
                kurulu = surum_ayikla(calistir_(oge["komut"]))
            except (OSError, ValueError, subprocess.SubprocessError):
                kurulu = None
        son, not_, cevrimdisi = None, "", False
        try:
            son, not_ = son_surum(oge, getir, simdi)
        except CevrimDisi:
            cevrimdisi = True
        except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, ET.ParseError):
            son = None
        eol = ""
        if oge["tur"] == "eol" and son and kurulu:
            eol = eol_durumu(not_, kurulu, simdi)
            not_ = ""
        durum, s = degerlendir(oge, kurulu, son, cevrimdisi, eol)
        sorun += s
        sayac_ag += cevrimdisi
        hucre = lambda v: str(v if v is not None else "bilinmiyor").replace("|", "/").replace("\n", " ")[:200]
        satirlar.append(f"| {hucre(oge['ad'])} | {hucre(kurulu or 'yok')} | {hucre(son or 'bilinmiyor')} | {hucre(durum)} |")
    baslik = [f"# Güncelleme raporu: {simdi:%Y-%m-%d %H:%M} UTC", "",
              "Yalnızca okuma; hiçbir şey kurulmadı ya da yükseltilmedi.", ""]
    if izlenen and sayac_ag == len(izlenen):
        baslik += ["**Çevrimdışı:** son sürümler alınamadı; yalnızca kurulu sürümler gösterilir.", ""]
    govde = ["| Araç | Kurulu | Son | Durum |", "|---|---|---|---|", *satirlar, "",
             "Kaynaklar: npm kayıt defteri, PyPI JSON, GitHub releases.atom, endoflife.date.",
             f"Sabitlenmiş araçlar için politika: en yeni sürüm en az {BEKLEME_GUN} gün önce yayımlanmış olmalı; otomatik yükseltme önerilmez."]
    return "\n".join(baslik + govde) + "\n", (1 if sorun else 0)


def main(argv: list[str]) -> int:
    kok = kok_bul()
    izlenen = izlenenleri_oku(kok / "20-sistem" / "nabiz" / "izlenenler.txt")
    metin, kod = rapor_uret(izlenen)
    if "--rapor-yok" not in argv:
        hedef = kok / "20-sistem" / "durum" / makine() / "guncelleme-raporu.md"
        hedef.parent.mkdir(parents=True, exist_ok=True)
        gecici = hedef.with_name(f".{hedef.name}.{os.getpid()}.tmp")
        gecici.write_text(metin, encoding="utf-8")
        os.replace(gecici, hedef)
    print(metin)
    return kod


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
