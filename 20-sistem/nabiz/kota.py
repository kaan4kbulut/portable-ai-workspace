#!/usr/bin/env python3
"""Abonelik kotası okuyucusu: claude, codex, agy için kalan kota tahmini + kip.

Kullanım: python3 20-sistem/nabiz/kota.py [--json | --agy-yenile]
  --agy-yenile  yalnız agy önbelleğini tazeler, çıktı basmaz (durum-satiri.py arka planda çağırır)

Kaynaklar (yalnızca resmi çıktılar; giriş/anahtar dosyaları okunmaz):
  claude  durum-satiri.py'nin yazdığı 20-sistem/durum/<host>/kota-claude.json
          (Claude Code'un statusLine'a verdiği rate_limits alanı)
  codex   ~/.codex/sessions/**/rollout-*.jsonl içindeki son `rate_limits` kaydı
  agy     `agy -p /quota --output-format json` (model çağırmaz); 5 dk önbellek. İki grup ayrı satır:
          agy (Gemini) ve agy-claude (agy içindeki Claude Opus/Sonnet + GPT-OSS; Claude Max'ten ayrı kota)
  opencode  kota API'si yok: n/a

Kip: bağlayıcı (en az kalan) pencere <= %10 ise dolu, <= %25 ise idareli.
Daha fazla kalanda mevcut tempo hesabı bol / normal / idareli seçer.
Sıfırlanmış pencereler %100 kalan sayılır; eski verinin kipi bilinmiyor olur.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HAFTA_S = 7 * 86400
AYRILAN = 0.25          # 5 saatlik pencerede sahibine ayrılan pay
ONDE_SINIR = 0.15       # haftalık kullanım düzgün tempodan bu kadar öndeyse idareli
BOL_ESIK = 0.20         # ayrılan payın bu kadar üstünde yer varsa bol
ESKI_S = 6 * 3600       # bundan eski veri => bilinmiyor
AGY_ONBELLEK_S = 300
AGY_ZAMAN_ASIMI_S = 20
ARACLAR = ("claude", "codex", "agy", "agy-claude", "opencode")


# --- kök / makine ------------------------------------------------------------------
def kok_bul(baslangic: Path | None = None) -> Path:
    """00-cekirdek/ANAYASA.md içeren üst klasör."""
    p = (baslangic or Path(__file__)).resolve()
    for d in [p, *p.parents]:
        if (d / "00-cekirdek" / "ANAYASA.md").is_file():
            return d
    raise SystemExit("atölye kökü bulunamadı (00-cekirdek/ANAYASA.md yok)")


def makine() -> str:
    return socket.gethostname().split(".")[0]


def durum_klasoru(kok: Path, host: str | None = None) -> Path:
    return kok / "20-sistem" / "durum" / (host or makine())


def _atomik_yaz(yol: Path, metin: str) -> None:
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = yol.with_name(f".{yol.name}.{os.getpid()}.tmp")
    try:
        gecici.write_text(metin, encoding="utf-8")
        os.replace(gecici, yol)
    finally:
        gecici.unlink(missing_ok=True)


# --- kip ---------------------------------------------------------------------------
def _kullanilan(w: dict | None, simdi: float) -> float | None:
    """Pencere {kullanilan: 0..1, sifirlanma: epoch}; sıfırlanmış pencere 0'dan başlar."""
    if not w:
        return None
    return 0.0 if simdi >= w["sifirlanma"] else w["kullanilan"]


def kip_hesapla(five: dict | None, week: dict | None, zaman: float | None,
                simdi: float, saglayici: str = "claude") -> str:
    if zaman is None or simdi - zaman > ESKI_S or (five is None and week is None):
        return "bilinmiyor"
    f, h = _kullanilan(five, simdi), _kullanilan(week, simdi)
    en_cok = max(x for x in (f, h) if x is not None)
    if en_cok >= 0.90:
        return "dolu"
    if en_cok >= 0.75:
        return "idareli"
    kalan_s = (five["sifirlanma"] - simdi) if five and five["sifirlanma"] > simdi else None
    pay = 0.0 if (kalan_s is not None and kalan_s <= 1800) else AYRILAN
    onde = 0.0
    if h is not None and week and simdi < week["sifirlanma"]:
        gecen = 1 - (week["sifirlanma"] - simdi) / HAFTA_S
        onde = h - max(0.0, min(1.0, gecen))
    f_kalan = 1 - f if f is not None else 1.0
    if kalan_s is not None and kalan_s <= 1800 and f_kalan >= 0.10:
        return "bol"          # pencere bitmek üzere, kalan pay boşa gitmesin
    if saglayici == "codex" and f is not None and f < 0.50:
        if f_kalan < pay:
            return "idareli"
        return "bol" if (f_kalan - pay >= BOL_ESIK and onde <= 0) else "normal"
    if f_kalan < pay or onde > ONDE_SINIR:
        return "idareli"
    return "bol" if (f_kalan - pay >= BOL_ESIK and onde <= 0) else "normal"


def kalan_yuzde(five: dict | None, week: dict | None, simdi: float) -> int | None:
    """En kısıtlı pencerenin kalan yüzdesi."""
    kul = [x for x in (_kullanilan(five, simdi), _kullanilan(week, simdi)) if x is not None]
    return None if not kul else round((1 - max(kul)) * 100)


def baglayici_bul(five: dict | None, week: dict | None, simdi: float) -> str | None:
    """En az kalan pencere; eşitlikte 5 saatlik pencere seçilir."""
    pencereler = [(ad, _kullanilan(w, simdi)) for ad, w in (("5s", five), ("hafta", week)) if w]
    return max(pencereler, key=lambda p: p[1])[0] if pencereler else None


def _pencere(kullanilan_yuzde, sifirlanma) -> dict | None:
    if not isinstance(kullanilan_yuzde, (int, float)) or isinstance(kullanilan_yuzde, bool):
        return None
    if not isinstance(sifirlanma, (int, float)) or isinstance(sifirlanma, bool):
        return None
    return {"kullanilan": max(0.0, min(1.0, kullanilan_yuzde / 100)), "sifirlanma": float(sifirlanma)}


def _sonuc(arac: str, five: dict | None, week: dict | None, zaman: float | None,
           kaynak: str, simdi: float, not_: str = "") -> dict:
    return {
        "arac": arac,
        "baglayici": baglayici_bul(five, week, simdi) if zaman is not None and simdi - zaman <= ESKI_S else None,
        "kalan_yuzde": kalan_yuzde(five, week, simdi) if (zaman and simdi - zaman <= ESKI_S) else None,
        "kip": kip_hesapla(five, week, zaman, simdi, arac),
        "pencereler": {"5s": five, "hafta": week},
        "kaynak": kaynak,
        "zaman": datetime.fromtimestamp(zaman).astimezone().isoformat(timespec="seconds") if zaman else None,
        "not": not_,
    }


def _bilinmiyor(arac: str, kaynak: str, not_: str) -> dict:
    return {"arac": arac, "baglayici": None, "kalan_yuzde": None, "kip": "bilinmiyor", "pencereler": {"5s": None, "hafta": None},
            "kaynak": kaynak, "zaman": None, "not": not_}


# --- claude ------------------------------------------------------------------------
def claude_onbellek_yolu(kok: Path, host: str | None = None) -> Path:
    return durum_klasoru(kok, host) / "kota-claude.json"


def claude_oku(kok: Path, simdi: float, host: str | None = None) -> dict:
    yol = claude_onbellek_yolu(kok, host)
    kaynak = "durum-satiri.py önbelleği (statusLine rate_limits)"
    try:
        d = json.loads(yol.read_text(encoding="utf-8"))
        zaman = float(d["zaman"])
    except (OSError, ValueError, KeyError, TypeError):
        return _bilinmiyor("claude", kaynak, "veri yok: statusLine kurulu değil ya da henüz yanıt alınmadı (yalnızca Pro/Max)")
    five = _pencere(d.get("five_hour_used_percentage"), d.get("five_hour_resets_at"))
    week = _pencere(d.get("seven_day_used_percentage"), d.get("seven_day_resets_at"))
    return _sonuc("claude", five, week, zaman, kaynak, simdi)


def claude_onbellege_yaz(kok: Path, durum_json: dict, simdi: float, host: str | None = None) -> bool:
    """statusLine girdisinden rate_limits'i önbelleğe yazar; alan yoksa eski önbellek korunur."""
    rl = durum_json.get("rate_limits") if isinstance(durum_json, dict) else None
    if not isinstance(rl, dict):
        return False
    out: dict = {"zaman": simdi}
    for ad, anahtar in (("five_hour", "five_hour"), ("seven_day", "seven_day")):
        w = rl.get(anahtar)
        if isinstance(w, dict):
            out[f"{ad}_used_percentage"] = w.get("used_percentage")
            out[f"{ad}_resets_at"] = w.get("resets_at")
    if len(out) == 1:
        return False
    _atomik_yaz(claude_onbellek_yolu(kok, host), json.dumps(out, ensure_ascii=False))
    return True


# --- codex -------------------------------------------------------------------------
def codex_oturum_klasoru() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex")) / "sessions"


def _son_rollout(oturumlar: Path) -> list[Path]:
    """En yeni rollout dosyaları (son 3 gün klasörü, yeniden eskiye)."""
    try:
        gunler = sorted(p for p in oturumlar.glob("*/*/*") if p.is_dir())
    except OSError:
        return []
    dosyalar: list[Path] = []
    for gun in reversed(gunler[-3:]):
        try:
            dosyalar += sorted(gun.glob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        except OSError:
            continue
    return dosyalar[:10]


def codex_dosyadan(yol: Path, kuyruk: int = 256 * 1024) -> tuple[dict, float] | None:
    """Dosyadaki son rate_limits kaydı ve kaydın kendi zamanı (yoksa dosya mtime)."""
    try:
        with yol.open("rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - kuyruk))
            satirlar = f.read().decode(errors="replace").splitlines()
        mtime = yol.stat().st_mtime
    except OSError:
        return None
    def olay_zamani(o) -> float:
        z = o.get("timestamp") if isinstance(o, dict) else None
        try:
            return datetime.fromisoformat(z.replace("Z", "+00:00")).timestamp()
        except (AttributeError, ValueError):
            return mtime
    for satir in reversed(satirlar):
        if '"rate_limits"' not in satir:
            continue
        try:
            olay = json.loads(satir)
        except ValueError:
            continue
        yuk = olay.get("payload") if isinstance(olay, dict) else None
        rl = (yuk or olay).get("rate_limits") if isinstance(yuk or olay, dict) else None
        if isinstance(rl, dict):
            return rl, olay_zamani(olay)
    return None


def codex_oku(simdi: float, oturumlar: Path | None = None) -> dict:
    kaynak = "Codex oturum kaydı rate_limits"
    for yol in _son_rollout(oturumlar or codex_oturum_klasoru()):
        bulgu = codex_dosyadan(yol)
        if not bulgu:
            continue
        rl, mtime = bulgu
        five = week = None
        for slot in ("primary", "secondary"):
            w = rl.get(slot)
            if not isinstance(w, dict):
                continue
            sifir = w.get("resets_at")
            if sifir is None and isinstance(w.get("resets_in_seconds"), (int, float)):
                sifir = mtime + w["resets_in_seconds"]
            pen = _pencere(w.get("used_percent"), sifir)
            if not pen:
                continue
            if (w.get("window_minutes") or 0) >= 1440:
                week = pen
            else:
                five = pen
        if five or week:
            return _sonuc("codex", five, week, mtime, kaynak, simdi)
    return _bilinmiyor("codex", kaynak, "veri yok: Codex ile bir oturum çalıştırınca rate_limits kaydı oluşur")


# --- agy ---------------------------------------------------------------------------
def _agy_calistir(yol: str) -> dict | None:
    """Own process group: on timeout the whole tree is killed so held pipes cannot hang us."""
    try:
        p = subprocess.Popen([yol, "-p", "/quota", "--output-format", "json"], stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                             cwd=os.path.expanduser("~"), start_new_session=True)
    except OSError:
        return None
    try:
        cikti, _ = p.communicate(timeout=AGY_ZAMAN_ASIMI_S)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        p.communicate()
        return None
    try:
        return json.loads(cikti[cikti.index("{"):])
    except ValueError:
        return None


AGY_GRUPLARI = {"gemini": ("agy", ("gemini",)), "claude": ("agy-claude", ("claude", "gpt"))}


def agy_oku(kok: Path, simdi: float, host: str | None = None, calistir=_agy_calistir,
            yenile: bool = True, grup: str = "gemini") -> dict:
    """yenile=False: agy çalıştırılmaz, önbellek yaşı ne olursa olsun kullanılır (statusLine için).
    grup: agy has separate quota groups; "gemini" (row "agy") or "claude" (Claude + GPT models, row "agy-claude")."""
    arac, anahtarlar = AGY_GRUPLARI[grup]
    kaynak = "agy -p /quota --output-format json"
    onbellek = durum_klasoru(kok, host) / "kota-agy.json"
    veri, zaman = None, None
    try:
        d = json.loads(onbellek.read_text(encoding="utf-8"))
        if isinstance(d.get("veri"), dict) and (not yenile or simdi - float(d["zaman"]) <= AGY_ONBELLEK_S):
            veri, zaman = d["veri"], float(d["zaman"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    if veri is None and not yenile:
        return _bilinmiyor(arac, kaynak, "agy önbelleği yok")
    if veri is None:
        yol = shutil.which("agy") or ""
        if not yol:
            return _bilinmiyor(arac, kaynak, "agy kurulu değil")
        ham = calistir(yol)
        veri = ((ham or {}).get("command") or {}).get("data") if isinstance(ham, dict) else None
        if not isinstance(veri, dict):
            return _bilinmiyor(arac, kaynak, "agy /quota yanıt vermedi (giriş yapılmamış olabilir; giriş agy'nin kendi komutuyla)")
        zaman = simdi
        try:
            _atomik_yaz(onbellek, json.dumps({"zaman": zaman, "veri": veri}, ensure_ascii=False))
        except OSError:
            pass
    # Gruplar arasında pencere başına en kısıtlı olan alınır.
    en_kotu: dict[str, dict] = {}
    gruplar = veri.get("groups")
    gruplar = [g for g in gruplar if isinstance(g, dict)] if isinstance(gruplar, list) else []
    adli = [g for g in gruplar if isinstance(g.get("name"), str)]
    if adli:  # named groups: keep only this group's buckets (min across groups hid the free Gemini quota)
        gruplar = [g for g in adli if any(k in g["name"].lower() for k in anahtarlar)]
    for g in gruplar:
        kovalar = g.get("buckets") if isinstance(g, dict) else None
        for b in kovalar if isinstance(kovalar, list) else []:
            if not isinstance(b, dict):
                continue
            frac, anahtar = b.get("remaining_fraction"), ("5s" if b.get("window") == "5h" else "hafta")
            try:
                sifir = datetime.fromisoformat(b["reset_time"].replace("Z", "+00:00")).timestamp()
            except (KeyError, ValueError, AttributeError):
                continue
            if not isinstance(frac, (int, float)) or isinstance(frac, bool):
                continue
            pen = _pencere((1 - frac) * 100, sifir)
            if pen and (anahtar not in en_kotu or pen["kullanilan"] > en_kotu[anahtar]["kullanilan"]):
                en_kotu[anahtar] = pen
    if not en_kotu:
        return _bilinmiyor(arac, kaynak, f"agy kota verisi boş ({grup} grubu)")
    return _sonuc(arac, en_kotu.get("5s"), en_kotu.get("hafta"), zaman, kaynak, simdi)


# --- toplu -------------------------------------------------------------------------
def hepsi(kok: Path, simdi: float | None = None, host: str | None = None, agy: bool = True) -> list[dict]:
    simdi = time.time() if simdi is None else simdi
    sonuc = [claude_oku(kok, simdi, host), codex_oku(simdi)]
    if agy:
        sonuc.append(agy_oku(kok, simdi, host))
        sonuc.append(agy_oku(kok, simdi, host, yenile=False, grup="claude"))  # same cache, second group
    sonuc.append(_bilinmiyor("opencode", "yok", "n/a: kota bilgisi sağlanmıyor"))
    sonuc[-1]["kip"] = "n/a"
    return sonuc


def _metin(s: dict, simdi: float | None = None) -> str:
    simdi = time.time() if simdi is None else simdi
    parcalar = []
    if s["kalan_yuzde"] is not None:
        for ad, w in s["pencereler"].items():
            if w is None:
                continue
            sifir = datetime.fromtimestamp(w["sifirlanma"]).astimezone()
            saat = sifir.strftime("%H:%M")
            if ad == "hafta":
                saat = ("Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz")[sifir.weekday()] + " " + saat
            kalan = kalan_yuzde(w, None, simdi)
            parcalar.append(f"{ad} %{kalan} kalan (sıfırlanma {saat})")
    kalan = " · ".join(parcalar) or "bilinmiyor"
    satir = f"{s['arac']:<9} {kalan:<14} kip={s['kip']:<10} kaynak={s['kaynak']}"
    if s["zaman"]:
        satir += f" · {s['zaman']}"
    if s["not"]:
        satir += f"\n{'':<9} not: {s['not']}"
    return satir


def main(argv: list[str]) -> int:
    kok = kok_bul()
    if "--agy-yenile" in argv:
        agy_oku(kok, time.time())
        return 0
    sonuc = hepsi(kok)
    if "--json" in argv:
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    else:
        print("\n".join(_metin(s) for s in sonuc))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
