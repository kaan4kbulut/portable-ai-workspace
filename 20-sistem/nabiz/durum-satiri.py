#!/usr/bin/env python3
"""Claude Code statusLine command: caches the quota part and prints one compact status line.

stdin: the JSON Claude Code sends (rate_limits.five_hour / seven_day, context_window).
stdout: <ad> · <makine> · git ±N · gelen N · denetim H/U · bağlam %B 46k/200k
        · claude 5s%X hf%Y · codex 5s%X hf%Y · agy 5s%X hf%Y · agy-claude 5s%X hf%Y   (percentages = remaining)
No network, no model call; target < 200 ms. agy is read from its cache only; a stale cache
is refreshed by a detached `kota.py --agy-yenile` (at most once per AGY_DENEME_S).
Never fails: on any error it still prints a line.
"""
from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

DIZIN = Path(__file__).resolve().parent


def _kota_yukle():
    spec = importlib.util.spec_from_file_location("nabiz_kota", DIZIN / "kota.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ad_bul(kok: Path) -> str:
    try:
        d = json.loads((kok / "00-cekirdek" / "kimlik.json").read_text(encoding="utf-8"))
        for anahtar in ("ad", "isim", "name"):
            if isinstance(d.get(anahtar), str) and d[anahtar].strip():
                return d[anahtar].strip()
    except (OSError, ValueError, AttributeError):
        pass
    return kok.name


GIT_ZAMAN_ASIMI_S = 0.3
GIT_ONBELLEK_S = 30


def git_degisiklik(kok: Path) -> str:
    try:
        p = subprocess.run(["git", "-C", str(kok), "status", "--porcelain"], capture_output=True, text=True,
                           timeout=GIT_ZAMAN_ASIMI_S, check=False)
        return str(len([s for s in p.stdout.splitlines() if s.strip()])) if p.returncode == 0 else "?"
    except (OSError, subprocess.SubprocessError):
        return "?"


def git_onbellekli(kok: Path, durum: Path, simdi: float) -> str:
    """git özetini 30 sn önbellekler; zaman aşımında ('?') eski değer korunur."""
    yol = durum / "durum-satiri-onbellek.json"
    eski = None
    try:
        d = json.loads(yol.read_text(encoding="utf-8"))
        eski = str(d["git"])
        if 0 <= simdi - float(d["zaman"]) < GIT_ONBELLEK_S:
            return eski
    except (OSError, ValueError, KeyError, TypeError):
        pass
    taze = git_degisiklik(kok)
    if taze == "?":
        return eski if eski is not None else "?"
    try:
        durum.mkdir(parents=True, exist_ok=True)
        gecici = yol.with_name(f".{yol.name}.{os.getpid()}.tmp")
        gecici.write_text(json.dumps({"zaman": simdi, "git": taze}), encoding="utf-8")
        os.replace(gecici, yol)
    except OSError:
        pass
    return taze


def gelen_sayisi(kok: Path) -> str:
    try:
        yok = {"README.md", "AYIKLAMA.md", ".gitkeep"}
        return str(len([p for p in (kok / "90-gelen-kutusu").iterdir() if p.name not in yok]))
    except OSError:
        return "?"


def denetim(durum: Path) -> str:
    """son-denetim.txt: [HATA]/[UYARI] satırları sayılır; yoksa '?'."""
    try:
        metin = (durum / "son-denetim.txt").read_text(encoding="utf-8")
    except OSError:
        return "?/?"
    h = len(re.findall(r"^\[HATA\]", metin, re.M))
    u = len(re.findall(r"^\[UYARI\]", metin, re.M))
    return f"{h}/{u}"


AGY_DENEME_S = 120


def agy_tazele(kota, durum: Path, simdi: float) -> bool:
    """Starts a detached agy cache refresh when the cache is stale; throttled by a stamp file."""
    try:
        zaman = float(json.loads((durum / "kota-agy.json").read_text(encoding="utf-8"))["zaman"])
        if simdi - zaman <= kota.AGY_ONBELLEK_S:
            return False
    except (OSError, ValueError, KeyError, TypeError):
        pass
    damga = durum / "kota-agy-deneme.txt"
    try:
        durum.mkdir(parents=True, exist_ok=True)
        with open(damga, "a+", encoding="utf-8") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)  # another statusLine holds it: skip
            except OSError:
                return False
            if simdi - os.fstat(f.fileno()).st_mtime < AGY_DENEME_S and os.fstat(f.fileno()).st_size:
                return False
            f.seek(0)
            f.truncate()
            f.write(str(simdi))
            f.flush()
            subprocess.Popen([sys.executable, "-I", str(DIZIN / "kota.py"), "--agy-yenile"], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return True
    except OSError:
        return False


def _bin(n: float) -> str:
    return f"{n / 1000:.0f}k" if n < 999_500 else f"{n / 1_000_000:.1f}M"


def baglam(girdi: dict) -> str:
    """Context usage of this session: '%23 46k/200k'; '?' before the first reply."""
    cw = girdi.get("context_window")
    if not isinstance(cw, dict):
        return "?"
    boyut = cw.get("context_window_size")
    cu = cw.get("current_usage") if isinstance(cw.get("current_usage"), dict) else {}
    alanlar = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    dolu = sum(v for k in alanlar if isinstance(v := cu.get(k), (int, float)) and not isinstance(v, bool))
    yuzde = cw.get("used_percentage")
    if not isinstance(yuzde, (int, float)) or isinstance(yuzde, bool):
        if not (isinstance(boyut, (int, float)) and boyut > 0 and dolu):
            return "?"
        yuzde = dolu / boyut * 100
    metin = f"%{round(yuzde)}"
    if dolu and isinstance(boyut, (int, float)) and boyut > 0:
        metin += f" {_bin(dolu)}/{_bin(boyut)}"
    return metin


def kota_parcasi(s: dict, simdi: float, kota) -> str:
    """'claude 5s%48 hf%6': remaining percentage of each window; '?' when unknown or stale."""
    if s.get("kalan_yuzde") is None:
        return f"{s['arac']} ?"
    pencereler = s.get("pencereler") or {}
    parca = [f"{etiket}%{kota.kalan_yuzde(w, None, simdi)}"
             for ad, etiket in (("5s", "5s"), ("hafta", "hf")) if (w := pencereler.get(ad))]
    return f"{s['arac']} {' '.join(parca) or '?'}"


def isler_ozeti(kok: Path) -> str | None:
    """'işler 2▶ 1⚠' from 20-sistem/kadro/isler.py; None when the registry is missing or broken."""
    try:
        spec = importlib.util.spec_from_file_location("nabiz_isler", kok / "20-sistem" / "kadro" / "isler.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.ozet()
    except Exception:  # noqa: BLE001 - the status line must never fail
        return None


def satir_uret(kok: Path, kota, girdi: dict, simdi: float, host: str | None = None, codex_oturumlar: Path | None = None) -> str:
    host = host or kota.makine()
    try:
        kota.claude_onbellege_yaz(kok, girdi, simdi, host)
    except OSError:
        pass
    durum = kota.durum_klasoru(kok, host)
    agy_tazele(kota, durum, simdi)
    araclar = (kota.claude_oku(kok, simdi, host), kota.codex_oku(simdi, codex_oturumlar),
               kota.agy_oku(kok, simdi, host, yenile=False), kota.agy_oku(kok, simdi, host, yenile=False, grup="claude"))
    return " · ".join([
        ad_bul(kok), host, f"git ±{git_onbellekli(kok, durum, simdi)}", f"gelen {gelen_sayisi(kok)}",
        f"denetim {denetim(durum)}", f"bağlam {baglam(girdi)}", *filter(None, [isler_ozeti(kok)]),
        *(kota_parcasi(s, simdi, kota) for s in araclar),
    ])


def main() -> int:
    try:
        girdi = json.loads(sys.stdin.read() or "{}")
        if not isinstance(girdi, dict):
            girdi = {}
    except ValueError:
        girdi = {}
    try:
        kota = _kota_yukle()
        try:
            kok = kota.kok_bul(DIZIN)
        except SystemExit:  # root not found from script location: fall back to project dir / cwd
            kok = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        print(satir_uret(kok, kota, girdi, time.time()))
    except (Exception, SystemExit) as e:  # statusLine must never crash
        print(f"{Path(os.getcwd()).name} · durum satırı hatası: {type(e).__name__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
