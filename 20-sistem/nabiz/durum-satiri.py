#!/usr/bin/env python3
"""Claude Code statusLine command: caches the quota part and prints one compact status line.

stdin: the JSON Claude Code sends (rate_limits.five_hour / seven_day: used_percentage, resets_at).
stdout: <ad> · <makine> · git ±N · gelen N · denetim H/U · kota claude X% codex Y%
No network, no model call; target < 200 ms. Never fails: on any error it still prints a line.
"""
from __future__ import annotations

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


def satir_uret(kok: Path, kota, girdi: dict, simdi: float, host: str | None = None, codex_oturumlar: Path | None = None) -> str:
    host = host or kota.makine()
    try:
        kota.claude_onbellege_yaz(kok, girdi, simdi, host)
    except OSError:
        pass
    parcalar = []
    for s in (kota.claude_oku(kok, simdi, host), kota.codex_oku(simdi, codex_oturumlar)):
        y = s["kalan_yuzde"]
        parcalar.append(f"{s['arac']} {'?' if y is None else str(y) + '%'}")
    return " · ".join([
        ad_bul(kok), host, f"git ±{git_onbellekli(kok, kota.durum_klasoru(kok, host), simdi)}", f"gelen {gelen_sayisi(kok)}",
        f"denetim {denetim(kota.durum_klasoru(kok, host))}", "kota " + " ".join(parcalar),
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
