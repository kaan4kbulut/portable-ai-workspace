#!/usr/bin/env python3
"""SessionStart hook: inject workspace context (stdout goes into Claude's context). Never blocks.

Prints, within ~80 lines:
  1. first-run warning for this machine (10-sistem/durum/<host>/ missing)
  2. the 2 newest handover notes from 40-hafiza/oturumlar/
  3. head of 40-hafiza/kararlar/KARARLAR.md
  4. DURUM.md of the active project (durum/<host>/aktif-proje.txt or first 'aktif' row in 30-projeler/DIZIN.md)
  5. quick structure check summary (denetle.sh --hizli)
"""
import glob
import os
import re
import socket
import subprocess
import sys

SINIR = 80


def oku(yol, n):
    try:
        with open(yol, encoding="utf-8", errors="replace") as f:
            return [satir.rstrip("\n") for satir in f.readlines()[:n]]
    except OSError:
        return []


def main():
    kok = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    host = socket.gethostname().split(".")[0]
    cikti = ["# Atölye oturum bağlamı"]

    durum = os.path.join(kok, "10-sistem", "durum", host)
    if not os.path.isdir(durum):
        cikti.append(f"- UYARI: bu makinede ({host}) ilk kurulum yapılmamış. Önce `bash basla.sh` çalıştır.")

    notlar = sorted(glob.glob(os.path.join(kok, "40-hafiza", "oturumlar", "*", "*.md")))
    notlar = [n for n in notlar if os.path.basename(n) != "README.md"][-2:]
    if notlar:
        cikti.append("")
        cikti.append("## Son devir notları")
        for n in reversed(notlar):
            cikti.append(f"### {os.path.relpath(n, kok)}")
            cikti.extend(oku(n, 18))
    else:
        cikti.append("- Henüz devir notu yok (oturum sonunda `/kapat`).")

    kararlar = os.path.join(kok, "40-hafiza", "kararlar", "KARARLAR.md")
    satirlar = oku(kararlar, 20)
    if satirlar:
        cikti.append("")
        cikti.append("## KARARLAR.md (baş)")
        cikti.extend(satirlar)

    proje = ""
    ap = oku(os.path.join(durum, "aktif-proje.txt"), 1)
    if ap and ap[0].strip():
        proje = ap[0].strip()
    else:
        for s in oku(os.path.join(kok, "30-projeler", "DIZIN.md"), 60):
            if "|" in s and re.search(r"\baktif\b", s) and not s.startswith("| ad"):
                hucreler = [h.strip().strip("`") for h in s.strip("|").split("|")]
                if hucreler and hucreler[0] and hucreler[0] != "ad":
                    proje = hucreler[0]
                    break
    if proje:
        d = os.path.join(kok, "30-projeler", "aktif", proje, "DURUM.md")
        ds = oku(d, 15)
        cikti.append("")
        cikti.append(f"## Aktif proje: {proje}")
        cikti.extend(ds if ds else [f"- {os.path.relpath(d, kok)} yok ya da proje klonlanmamış."])

    denetle = os.path.join(kok, "10-sistem", "denetim", "denetle.sh")
    if os.path.isfile(denetle):
        try:
            r = subprocess.run(["bash", denetle, "--hizli"], capture_output=True, text=True, timeout=15, cwd=kok)
            hata = len(re.findall(r"^\[HATA\]", r.stdout, re.M))
            uyari = len(re.findall(r"^\[UYARI\]", r.stdout, re.M))
            cikti.append("")
            cikti.append(f"## Denetim (hızlı): {hata} hata, {uyari} uyarı" + (" → `/bakim` çalıştır" if hata else ""))
            if hata or uyari:
                cikti.extend([s for s in r.stdout.splitlines() if s.startswith("[HATA]") or s.startswith("[UYARI]")][:8])
        except Exception as e:  # noqa: BLE001
            cikti.append(f"- denetle.sh çalıştırılamadı: {e}")

    print("\n".join(cikti[:SINIR]))
    sys.exit(0)


if __name__ == "__main__":
    main()
