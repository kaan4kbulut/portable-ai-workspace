#!/usr/bin/env python3
"""Kutuphaneci: offline audit of entity pages and research reports, a persistent
job queue and a quota-aware worker loop that drives the official CLIs.

Usage (from anywhere inside the repo):
    python3 20-sistem/kutuphaneci/kutuphaneci.py denetle
    python3 20-sistem/kutuphaneci/kutuphaneci.py kuyruk [--ekle TUR KONU]
    python3 20-sistem/kutuphaneci/kutuphaneci.py calistir [--kuru] [--sinir N] [--isci agy|claude|codex]
    python3 20-sistem/kutuphaneci/kutuphaneci.py harita

Python 3 stdlib only. No network access in this module itself; only the worker
CLIs may use the network, and they run with their own official login.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import socket
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    import fcntl
except ImportError:
    fcntl = None
    try:
        import msvcrt
    except ImportError:
        msvcrt = None

# Layers inside-out: (id, folder).
KATMANLAR = [
    ("cekirdek", "00-cekirdek"),
    ("donanim", "10-donanim"),
    ("sistem", "20-sistem"),
    ("programlar", "30-programlar"),
    ("projeler", "40-projeler"),
    ("arayuz", "50-arayuz"),
    ("hafiza", "60-hafiza"),
    ("kutuphane", "70-kutuphane"),
]
KLASOR = dict(KATMANLAR)
# Layers whose direct sub-folders are entities that must have a page.
VARLIK_KATMANLARI = ("donanim", "sistem", "programlar", "projeler", "arayuz")
ZORUNLU_ALANLAR = ("katman", "surum", "son_kontrol", "kaynaklar", "baglar")
BAYATLIK_GUN = 30
YOK_SAYILAN = {"durum", "testler", "__pycache__", "node_modules", ".git", "sablon", "sablonlar"}  # templates are not entities
# containers whose children are separate repos; their pages live in <katman>/sayfalar/<ad>.md (ANAYASA 12.1)
KAPSAYICI = {"aktif", "deneme", "sayfalar"}
ARASTIRMA = "70-kutuphane/arastirmalar"
ISCI_SIRASI = ("agy", "claude")  # codex only on explicit request (scarce quota)
ENV_TEMIZLE = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY")
KOTA_RE = re.compile(
    r"(?i)(quota.{0,40}(?:exceed|exhaust|reach|limit)|rate.?limit.{0,30}(?:exceed|reach|error)|"
    r"usage.?limit.{0,30}(?:reach|exceed)|(?:hit|reached|exceeded).{0,30}(?:usage|rate).?limit|"
    r"limit reached|resource.?exhausted|kota.{0,30}(?:doldu|aşıldı|bitti|hatası)|too many requests|\b429\b)")
TURLER = ("arastir", "duzelt", "haber", "sayfa_guncelle", "sayfa_yaz")
ISTEM_KLASORU = Path(__file__).resolve().parent / "istemler"


# ---------------------------------------------------------------- basics

def kok_bul(baslangic=None) -> Path:
    """Repo root = nearest parent holding 00-cekirdek/ANAYASA.md."""
    yol = Path(baslangic or Path(__file__).resolve().parent).resolve()
    for aday in [yol, *yol.parents]:
        if (aday / "00-cekirdek" / "ANAYASA.md").is_file():
            return aday
    raise SystemExit("Atölye kökü bulunamadı (00-cekirdek/ANAYASA.md yok).")


def durum_klasoru(kok: Path) -> Path:
    host = socket.gethostname().split(".")[0] or "bilinmiyor"
    return kok / "20-sistem" / "durum" / host / "kutuphaneci"


def _oku(yol: Path) -> str:
    try:
        return yol.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def _yukle(yol: Path, varsayilan):
    try:
        return json.loads(_oku(yol)) if yol.exists() else varsayilan
    except ValueError:
        return varsayilan


def _kaydet(yol: Path, deger) -> None:
    """Atomic JSON write: temp file in the same folder, then replace."""
    yol.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(yol.parent), prefix=yol.name + ".",
                                     suffix=".tmp", delete=False) as gecici:
        gecici.write(json.dumps(deger, ensure_ascii=False, indent=2) + "\n")
    os.replace(gecici.name, yol)


def _damga() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _goreli(yol: Path, kok: Path) -> str:
    return yol.relative_to(kok).as_posix()


@contextmanager
def _kuyruk_kilidi(durum: Path):
    """Non-blocking OS lock so two workers never run on the same queue.

    Raises BlockingIOError when busy. Without fcntl/msvcrt we refuse to run.
    """
    if fcntl is None and msvcrt is None:
        raise SystemExit("Bu platformda dosya kilidi yok; eşzamanlı çalışma güvenli değil, çıkıldı.")
    durum.mkdir(parents=True, exist_ok=True)
    with (durum / "kutuphaneci.lock").open("a+b") as tutamac:
        if not tutamac.seek(0, 2):
            tutamac.write(b"0")
            tutamac.flush()
        tutamac.seek(0)
        try:
            if fcntl is not None:
                fcntl.flock(tutamac.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                msvcrt.locking(tutamac.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as hata:
            raise BlockingIOError(str(hata)) from hata
        try:
            yield
        finally:
            tutamac.seek(0)
            if fcntl is not None:
                fcntl.flock(tutamac.fileno(), fcntl.LOCK_UN)
            else:
                msvcrt.locking(tutamac.fileno(), msvcrt.LK_UNLCK, 1)


# ------------------------------------------------------------ front-matter

def _tirnak_bol(metin: str) -> list[str]:
    """Split on ',' outside quotes."""
    parcalar, simdiki, tirnak = [], "", ""
    for ch in metin:
        if tirnak:
            simdiki += ch
            if ch == tirnak:
                tirnak = ""
        elif ch in "'\"":
            tirnak = ch
            simdiki += ch
        elif ch == ",":
            parcalar.append(simdiki)
            simdiki = ""
        else:
            simdiki += ch
    parcalar.append(simdiki)
    return parcalar


def _kapanis_bul(ham: str) -> int:
    """Index of the ']' closing a list that starts at ham[0], ignoring quoted text; -1 if none."""
    tirnak = ""
    for i, ch in enumerate(ham):
        if tirnak:
            if ch == tirnak:
                tirnak = ""
        elif ch in "'\"":
            tirnak = ch
        elif ch == "]":
            return i
    return -1


def _skaler(ham: str) -> str:
    """Quoted value keeps '#' and ',' inside; unquoted value loses a trailing ' # comment'."""
    ham = ham.strip()
    if ham[:1] in ("'", '"'):
        son = ham.find(ham[0], 1)
        return ham[1:son] if son > 0 else ham[1:]
    return re.sub(r"\s+#.*$", "", ham).strip()


def on_madde_oku(metin: str):
    """Parse the leading '---' block. Returns dict or None when there is none.

    Supports `key: value`, quoted values and inline lists `[a, "b,c"]`. A trailing
    ' # comment' is cut outside quotes. Unsupported (block-style) lists yield an
    empty string value, which the audit reports as a bad field.
    """
    metin = metin.lstrip("\ufeff")
    satirlar = metin.splitlines()
    if not satirlar or satirlar[0].strip() != "---":
        return None
    sonuc = {}
    for satir in satirlar[1:]:
        if satir.strip() == "---":
            return sonuc
        eslesme = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", satir)
        if not eslesme:
            continue
        ham = eslesme.group(2).strip()
        if ham.startswith("["):
            kapanis = _kapanis_bul(ham)
            if kapanis > 0:
                ogeler = [_skaler(o) for o in _tirnak_bol(ham[1:kapanis])]
                sonuc[eslesme.group(1)] = [o for o in ogeler if o]
                continue
        sonuc[eslesme.group(1)] = _skaler(ham)
    return None  # never closed


def _gezin(klasor: Path):
    """Yield *.md files below klasor, skipping ignored folders and nested repos."""
    if not klasor.is_dir():
        return
    for ad in sorted(os.listdir(klasor)):
        yol = klasor / ad
        if yol.is_dir():
            # a child holding .git is another repo (e.g. 40-projeler/aktif/<ad>); .git may be a file in worktrees
            if ad in YOK_SAYILAN or ad.startswith(".") or (yol / ".git").exists():
                continue
            yield from _gezin(yol)
        elif ad.endswith(".md"):
            yield yol


def varliklari_bul(kok: Path) -> list[dict]:
    """All entity pages (markdown with front-matter that declares `katman`)."""
    liste = []
    for katman, klasor in KATMANLAR:
        for yol in _gezin(kok / klasor):
            if yol.name == "HARITA.md":
                continue
            metin = _oku(yol)
            veri = on_madde_oku(metin)
            if veri is None or "katman" not in veri:
                continue
            baslik = re.search(r"(?m)^#\s+(.+)$", metin)
            ad = baslik.group(1).strip() if baslik else (
                yol.parent.name if yol.name.lower() == "readme.md" else yol.stem)
            liste.append({"yol": yol, "goreli": _goreli(yol, kok), "klasor_katman": katman,
                          "veri": veri, "ad": ad})
    return liste


def _link_hedefleri(metin: str):
    """Relative/inline/reference link targets outside code blocks."""
    metin = re.sub(r"```.*?```|~~~.*?~~~", "", metin, flags=re.S)
    metin = re.sub(r"`[^`\n]+`", "", metin)
    for desen in (r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)", r"(?m)^\s*\[[^\]\n]+\]:\s*(<[^>]+>|\S+)"):
        for m in re.finditer(desen, metin):
            yield m.group(1).strip("<>")


def _yerel_mi(hedef: str) -> bool:
    return bool(hedef) and not hedef.startswith(("#", "/", "\\")) and not urlsplit(hedef).scheme


def _bag_coz(sayfa: Path, hedef: str) -> Path:
    yol = (sayfa.parent / unquote(urlsplit(hedef).path)).resolve()
    return yol / "README.md" if yol.is_dir() else yol


# ------------------------------------------------------------------ audit

def denetle(kok=None, bugun=None, yaz=True) -> dict:
    """Offline audit; no network, no model. Returns {'bulgular': [...], ...}."""
    kok = Path(kok) if kok else kok_bul()
    bugun = bugun or date.today()
    bulgular = []

    def ekle(kod, konu, neden, oncelik, tur, katman="", dosyalar=()):
        bulgular.append({"kod": kod, "konu": konu, "neden": neden, "oncelik": oncelik,
                         "tur": tur, "katman": katman, "dosyalar": list(dosyalar)})

    # 1. entity pages
    varliklar = varliklari_bul(kok)
    for v in varliklar:
        veri, goreli = v["veri"], v["goreli"]
        eksik = [a for a in ZORUNLU_ALANLAR if a not in veri]
        if eksik:
            ekle("eksik_alan", goreli, "Ön madde alanı eksik: " + ", ".join(eksik), 3,
                 "sayfa_guncelle", v["klasor_katman"], [goreli])
        elif veri["katman"] != v["klasor_katman"]:
            ekle("yanlis_katman", goreli, f"katman '{veri['katman']}' ama sayfa {v['klasor_katman']} katmanında.",
                 3, "duzelt", v["klasor_katman"], [goreli])
        if "son_kontrol" in veri:
            try:
                eski = (bugun - date.fromisoformat(str(veri["son_kontrol"]))).days > BAYATLIK_GUN
            except ValueError:
                eski = True
            if eski:
                ekle("bayat_sayfa", goreli, f"son_kontrol geçersiz ya da {BAYATLIK_GUN} günden eski.", 4,
                     "sayfa_guncelle", v["klasor_katman"], [goreli])
        baglar = veri.get("baglar", [])
        for bag in baglar if isinstance(baglar, list) else []:
            if _yerel_mi(bag) and not _bag_coz(v["yol"], bag).exists():
                ekle("kirik_bag", f"{goreli} → {bag}", "baglar girdisinin hedefi yok.", 3, "duzelt",
                     v["klasor_katman"], [goreli])

    # 2. entity folders without a page
    sayfa_klasorleri = [v["yol"].parent for v in varliklar]
    for katman in VARLIK_KATMANLARI:
        taban = kok / KLASOR[katman]
        if not taban.is_dir():
            continue
        for alt in sorted(p for p in taban.iterdir()
                          if p.is_dir() and p.name not in YOK_SAYILAN | KAPSAYICI and not p.name.startswith(".")):
            if not any(k == alt or alt in k.parents for k in sayfa_klasorleri):
                ekle("sayfa_yok", _goreli(alt, kok), "Varlık klasörünün küre sayfası (ön madde) yok.", 5,
                     "sayfa_yaz", katman, [_goreli(alt, kok)])

    # 3. research reports
    arastirma = kok / ARASTIRMA
    dizinli = {(arastirma / unquote(urlsplit(t).path)).resolve()
               for t in _link_hedefleri(_oku(arastirma / "DIZIN.md")) if _yerel_mi(t)}
    for yol in _gezin(arastirma):
        goreli = _goreli(yol, kok)
        metin = _oku(yol)
        for hedef in dict.fromkeys(_link_hedefleri(metin)):
            if _yerel_mi(hedef) and not _bag_coz(yol, hedef).exists():
                ekle("kirik_baglanti", f"{goreli} → {hedef}", "Göreli bağlantının hedefi yok.", 3, "duzelt",
                     "kutuphane", [goreli])
        if yol.name in ("DIZIN.md", "README.md"):  # index pages, not reports
            continue
        if yol.resolve() not in dizinli:
            ekle("dizinsiz_rapor", goreli, "Rapor DIZIN.md içinde bağlı değil.", 4, "duzelt", "kutuphane", [goreli])
        ilk = "\n".join(metin.splitlines()[:30])
        if not re.search(r"(?mi)^\s*(?:>\s*)?(?:\*\*)?Kaynak denetimi\s*(?:\*\*)?\s*:", ilk):
            ekle("kaynak_denetimi_yok", goreli, "Raporun başında 'Kaynak denetimi:' satırı yok.", 3, "duzelt",
                 "kutuphane", [goreli])

    bulgular.sort(key=lambda b: (b["oncelik"], b["kod"], b["konu"]))
    sonuc = {"tarih": _damga(), "varlik_sayisi": len(varliklar), "bulgular": bulgular}
    if yaz:
        _kaydet(durum_klasoru(kok) / "denetim.json", sonuc)
    return sonuc


def denetim_yazdir(sonuc: dict) -> None:
    print(f"Denetim: {sonuc['varlik_sayisi']} varlık sayfası, {len(sonuc['bulgular'])} bulgu.")
    for b in sonuc["bulgular"]:
        print(f"  [{b['oncelik']}] {b['kod']}: {b['konu']} — {b['neden']}")


# ------------------------------------------------------------------ queue

def _is_kimligi(kod, tur, katman, konu) -> str:
    return hashlib.sha256(f"{kod}|{tur}|{katman}|{konu}".encode("utf-8")).hexdigest()[:16]


def kuyruk(kok=None, denetim=None, ekle=None) -> list[dict]:
    """Merge audit findings into the queue; same finding = same id (sha256).

    ekle: optional (tur, konu) manual job (research / news).
    """
    kok = Path(kok) if kok else kok_bul()
    durum = durum_klasoru(kok)
    with _kuyruk_kilidi(durum):
        return _kuyruk(kok, durum, denetim, ekle)


def _kuyruk(kok, durum, denetim=None, ekle=None) -> list[dict]:
    denetim = denetim if denetim is not None else denetle(kok)
    sira = _yukle(durum / "kuyruk.json", [])
    bilinen = {i["id"]: i for i in sira}
    adaylar = list(denetim["bulgular"])
    if ekle:
        tur, konu = ekle
        if tur not in TURLER:
            raise SystemExit(f"Bilinmeyen iş türü: {tur} (geçerli: {', '.join(TURLER)})")
        adaylar.append({"kod": "elle", "tur": tur, "konu": konu, "katman": "", "oncelik": 2,
                        "neden": "Elle eklendi.", "dosyalar": []})
    gorulen = set()
    for b in adaylar:
        anahtar = _is_kimligi(b["kod"], b["tur"], b.get("katman", ""), b["konu"])
        gorulen.add(anahtar)
        if anahtar in bilinen:
            is_ = bilinen[anahtar]
            is_.update({"neden": b["neden"], "oncelik": b["oncelik"]})
            if is_["durum"] == "bitti":  # same finding is back: reopen
                is_.update(durum="bekliyor", sonuc="Bulgu yeniden göründü; iş yeniden açıldı.")
            continue
        yeni = {"id": anahtar, "kod": b["kod"], "tur": b["tur"], "konu": b["konu"],
                "katman": b.get("katman", ""), "oncelik": b["oncelik"], "neden": b["neden"],
                "durum": "bekliyor", "olusturma": _damga(), "son_deneme": None,
                "dosyalar": b.get("dosyalar", [])}
        sira.append(yeni)
        bilinen[anahtar] = yeni
    for is_ in sira:  # finding gone and job never started => nothing left to do
        if is_["durum"] == "bekliyor" and is_["id"] not in gorulen and is_.get("kod") != "elle":
            is_.update(durum="bitti", sonuc="Bulgu artık yok.")
    sira.sort(key=lambda i: (i["oncelik"], i["olusturma"], i["id"]))
    _kaydet(durum / "kuyruk.json", sira)
    print(f"Kuyruk: {len(sira)} iş; {sum(i['durum'] == 'bekliyor' for i in sira)} bekliyor.")
    return sira


# ---------------------------------------------------------------- workers

def istem_olustur(is_: dict) -> str:
    # job types keep their ids (sayfa_yaz); prompt files follow the kebab-case naming rule (sayfa-yaz.md)
    sablon = _oku(ISTEM_KLASORU / f"{is_['tur'].replace('_', '-')}.md")
    for anahtar in ("konu", "katman", "neden"):
        sablon = sablon.replace("{{" + anahtar + "}}", str(is_.get(anahtar, "")))
    return sablon + "\nİlgili dosyalar: " + ", ".join(is_.get("dosyalar") or [])


def isci_komutu(isci: str, kok: Path, istem: str) -> list[str]:
    if isci == "agy":
        return ["agy", "-p", istem, "--model", "gemini-4-argon-high", "--output-format", "stream-json",
                "--dangerously-skip-permissions", "--sandbox"]
    if isci == "codex":
        return ["codex", "exec", "-s", "workspace-write", "-C", str(kok), istem]
    if isci == "claude":
        return ["claude", "-p", istem, "--agent", "kutuphaneci"]
    raise ValueError(f"Bilinmeyen işçi: {isci}")


def cikti_metni(isci: str, stdout: str) -> str:
    """agy stream-json: final text is result.response of the event:"result" line."""
    if isci != "agy":
        return stdout
    son = None
    for satir in stdout.splitlines():
        try:
            olay = json.loads(satir)
        except ValueError:
            continue
        if isinstance(olay, dict) and olay.get("event") == "result":
            sonuc = olay.get("result")
            if isinstance(sonuc, dict) and "response" in sonuc:
                son = str(sonuc["response"])
    return son if son is not None else stdout


def _gunluk(durum: Path, is_: dict, sonuc: str, isci: str) -> None:
    durum.mkdir(parents=True, exist_ok=True)
    konu = re.sub(r"[\r\n]+", " ", is_["konu"])
    with (durum / "gunluk.log").open("a", encoding="utf-8") as akis:
        akis.write(f"{_damga()} {is_['id']} {isci or '-'} {sonuc} {konu}\n")


def _isci_calistir(isci, kok, istem, zaman_asimi):
    """Returns (state, text): state in bitti|basarisiz|kota|yok|zaman_asimi."""
    env = {k: v for k, v in os.environ.items() if k not in ENV_TEMIZLE}
    try:
        proc = subprocess.run(isci_komutu(isci, kok, istem), cwd=str(kok), env=env, stdin=subprocess.DEVNULL, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=zaman_asimi)
    except FileNotFoundError:
        return "yok", f"{isci} komutu bulunamadı."
    except subprocess.TimeoutExpired:
        return "zaman_asimi", f"{isci} zaman aşımı."
    metin = cikti_metni(isci, proc.stdout or "")
    tum = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if KOTA_RE.search(tum):
        return "kota", tum[-2000:]
    return ("bitti" if proc.returncode == 0 else "basarisiz"), metin[-2000:]


def calistir(kok=None, sinir=2, isci=None, kuru=False, zaman_asimi=1800) -> list[dict]:
    """Run the highest-priority waiting jobs. Quota limit => job stays 'bekliyor'."""
    kok = Path(kok) if kok else kok_bul()
    durum = durum_klasoru(kok)
    siralar = (isci,) if isci else ISCI_SIRASI
    if kuru:
        return _calistir(kok, durum, sinir, siralar, True, zaman_asimi)
    try:
        with _kuyruk_kilidi(durum):
            return _calistir(kok, durum, sinir, siralar, False, zaman_asimi)
    except BlockingIOError:
        print("Başka bir kütüphaneci işçisi çalışıyor; çıkıldı.")
        return []


def _calistir(kok, durum, sinir, siralar, kuru, zaman_asimi) -> list[dict]:
    sira = _yukle(durum / "kuyruk.json", [])
    if not kuru:
        for is_ in sira:
            if is_["durum"] == "yapiliyor":
                is_.update(durum="bekliyor", sonuc="Önceki süreç kesildi; yeniden denenebilir.")
        _kaydet(durum / "kuyruk.json", sira)
    secilen = sorted((i for i in sira if i["durum"] == "bekliyor"),
                     key=lambda i: (i["oncelik"], i["olusturma"], i["id"]))[:max(0, sinir)]
    if kuru:
        print("Kuru çalışma: işçi çağrılmaz; kuyruk ve günlük değişmez.")
        for is_ in secilen:
            print(f"{is_['oncelik']} · {is_['tur']} · {is_['konu']} ({is_['id']}) → işçi sırası: {', '.join(siralar)}")
        return secilen
    for is_ in secilen:
        is_.update(durum="yapiliyor", son_deneme=_damga())
        _kaydet(durum / "kuyruk.json", sira)
        istem = istem_olustur(is_)
        kullanilan, sonuc_durumu, metin = "", "bekliyor", "Hiçbir işçi çalıştırılamadı (kota/yok/zaman aşımı)."
        for aday in siralar:
            d, m = _isci_calistir(aday, kok, istem, zaman_asimi)
            if d in ("kota", "yok", "zaman_asimi"):  # try the next worker
                metin = m
                continue
            kullanilan, sonuc_durumu, metin = aday, d, m
            break
        is_.update(durum=sonuc_durumu, isci=kullanilan, sonuc=metin)
        _kaydet(durum / "kuyruk.json", sira)
        _gunluk(durum, is_, sonuc_durumu, kullanilan)
        print(f"{is_['konu']}: {sonuc_durumu}")
    return secilen


# -------------------------------------------------------------------- map

def _kenarlar(kok: Path, varliklar: list[dict]) -> list[tuple[str, str]]:
    kimlik = {v["yol"].resolve(): v["goreli"] for v in varliklar}
    kenar = []
    for v in varliklar:
        baglar = v["veri"].get("baglar", [])
        for bag in baglar if isinstance(baglar, list) else []:
            if _yerel_mi(bag):
                hedef = kimlik.get(_bag_coz(v["yol"], bag))
                if hedef and hedef != v["goreli"]:
                    kenar.append((v["goreli"], hedef))
    return kenar


def _rel(hedef: Path, kimden: Path) -> str:
    return os.path.relpath(hedef, kimden).replace(os.sep, "/")


def harita_md(kok: Path, varliklar: list[dict], kenar) -> str:
    giden = {}
    for a, b in kenar:
        giden.setdefault(a, []).append(b)
    satirlar = ["# Atölye haritası (küre)", "",
                "Bu dosya `kutuphaneci.py harita` ile üretilir; elle düzenleme. Katmanlar içten dışa sıralıdır.", ""]
    for katman, klasor in KATMANLAR:
        grup = sorted((v for v in varliklar if v["klasor_katman"] == katman), key=lambda v: v["goreli"])
        satirlar += [f"## {klasor}", ""]
        if not grup:
            satirlar += ["(sayfa yok)", ""]
            continue
        for v in grup:
            satirlar.append(f"- [{v['ad']}]({_rel(v['yol'], kok / '00-cekirdek')}) · sürüm "
                            f"{v['veri'].get('surum', '-')} · son kontrol {v['veri'].get('son_kontrol', '?')}")
            for hedef in giden.get(v["goreli"], []):
                satirlar.append(f"  - bağ: [{hedef}]({_rel(kok / hedef, kok / '00-cekirdek')})")
        satirlar.append("")
    return "\n".join(satirlar).rstrip() + "\n"


def harita_html(kok: Path, varliklar: list[dict], kenar) -> str:
    """Self-contained SVG: concentric rings (core at the centre), no external libs."""
    merkez = 500
    noktalar = {}
    halkalar = []
    for i, (katman, klasor) in enumerate(KATMANLAR):
        grup = sorted((v for v in varliklar if v["klasor_katman"] == katman), key=lambda v: v["goreli"])
        yaricap = 0 if i == 0 and len(grup) <= 1 else (28 if i == 0 else 40 + i * 62)
        halkalar.append((klasor, yaricap))
        for j, v in enumerate(grup):
            aci = 2 * math.pi * j / max(len(grup), 1) + i * 0.55 - math.pi / 2
            noktalar[v["goreli"]] = (merkez + yaricap * math.cos(aci), merkez + yaricap * math.sin(aci), i, v)
    parcalar = []
    for klasor, r in halkalar:
        if r:
            parcalar.append(f'<circle class="halka" cx="{merkez}" cy="{merkez}" r="{r}"/>')
            parcalar.append(f'<text class="etiket" x="{merkez}" y="{merkez - r - 4}" text-anchor="middle">'
                            f'{html.escape(klasor)}</text>')
    for a, b in kenar:
        if a in noktalar and b in noktalar:
            parcalar.append(f'<line class="bag" x1="{noktalar[a][0]:.1f}" y1="{noktalar[a][1]:.1f}" '
                            f'x2="{noktalar[b][0]:.1f}" y2="{noktalar[b][1]:.1f}"/>')
    for goreli, (x, y, i, v) in noktalar.items():
        href = html.escape(_rel(v["yol"], kok / "50-arayuz"), quote=True)
        ad = html.escape(v["ad"])
        parcalar.append(f'<a href="{href}"><circle class="nokta k{i}" cx="{x:.1f}" cy="{y:.1f}" r="7">'
                        f'<title>{ad} ({html.escape(goreli)})</title></circle></a>')
        parcalar.append(f'<text class="ad" x="{x + 10:.1f}" y="{y + 4:.1f}">{ad}</text>')
    renkler = ["#b45309", "#0f766e", "#1d4ed8", "#7c3aed", "#be123c", "#047857", "#a16207", "#475569"]
    renk_css = "\n".join(f".k{i}{{fill:{c}}}" for i, c in enumerate(renkler))
    olcek = html.escape(f"{len(varliklar)} varlık, {len(kenar)} bağ")
    govde = "\n".join(parcalar)
    return f"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atölye haritası</title>
<style>
:root{{--zemin:#fafaf7;--yazi:#1c1c1a;--halka:#cfcfc8;--bag:#8a8a80}}
@media (prefers-color-scheme:dark){{:root{{--zemin:#16161a;--yazi:#e8e8e3;--halka:#3a3a42;--bag:#77777f}}}}
body{{margin:0;background:var(--zemin);color:var(--yazi);font-family:system-ui,sans-serif}}
header{{padding:12px 16px}} h1{{font-size:1.1rem;margin:0}} p{{margin:4px 0 0;font-size:.85rem;opacity:.8}}
svg{{display:block;width:100%;max-width:900px;height:auto;margin:0 auto}}
.halka{{fill:none;stroke:var(--halka);stroke-width:1}} .bag{{stroke:var(--bag);stroke-width:1;opacity:.6}}
.etiket{{fill:var(--yazi);font-size:11px;opacity:.6}} .ad{{fill:var(--yazi);font-size:10px}}
.nokta{{stroke:var(--zemin);stroke-width:2}} a:hover .nokta{{r:10}}
{renk_css}
</style></head><body>
<header><h1>Atölye haritası</h1><p>{olcek} · merkez çekirdek, dışa doğru katmanlar. Otomatik üretilir.</p></header>
<svg viewBox="0 0 1000 1000" role="img" aria-label="Katmanlı atölye haritası">
{govde}
</svg></body></html>
"""


def harita(kok=None) -> None:
    kok = Path(kok) if kok else kok_bul()
    varliklar = varliklari_bul(kok)
    kenar = _kenarlar(kok, varliklar)
    (kok / "00-cekirdek").mkdir(parents=True, exist_ok=True)
    (kok / "50-arayuz").mkdir(parents=True, exist_ok=True)
    (kok / "00-cekirdek" / "HARITA.md").write_text(harita_md(kok, varliklar, kenar), encoding="utf-8")
    (kok / "50-arayuz" / "harita.html").write_text(harita_html(kok, varliklar, kenar), encoding="utf-8")
    print(f"Harita: {len(varliklar)} varlık, {len(kenar)} bağ → 00-cekirdek/HARITA.md, 50-arayuz/harita.html")


# -------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Kütüphaneci")
    alt = ap.add_subparsers(dest="komut", required=True)
    alt.add_parser("denetle")
    k = alt.add_parser("kuyruk")
    k.add_argument("--ekle", nargs=2, metavar=("TUR", "KONU"))
    c = alt.add_parser("calistir")
    c.add_argument("--kuru", action="store_true")
    c.add_argument("--sinir", type=int, default=2)
    c.add_argument("--isci", choices=("agy", "claude", "codex"))
    alt.add_parser("harita")
    a = ap.parse_args(argv)
    if a.komut == "denetle":
        denetim_yazdir(denetle())
    elif a.komut == "kuyruk":
        kuyruk(ekle=tuple(a.ekle) if a.ekle else None)
    elif a.komut == "calistir":
        calistir(sinir=a.sinir, isci=a.isci, kuru=a.kuru)
    else:
        harita()
    return 0


if __name__ == "__main__":
    sys.exit(main())
