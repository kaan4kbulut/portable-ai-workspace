#!/usr/bin/env python3
"""SessionEnd hook: record machine-local session summary to 10-sistem/durum/<host>/son-oturum.json.

Raw material for /kapat and kapat.sh (touched files, cwd, timestamps). Never writes into tracked files.
"""
import json
import os
import socket
import subprocess
import sys
import time


def git_degisenler(kok):
    try:
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10, cwd=kok)
        return [s[3:] for s in r.stdout.splitlines() if s.strip()]
    except Exception:  # noqa: BLE001
        return []


def main():
    try:
        girdi = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        girdi = {}
    kok = os.environ.get("CLAUDE_PROJECT_DIR") or girdi.get("cwd") or os.getcwd()
    host = socket.gethostname().split(".")[0]
    durum = os.path.join(kok, "10-sistem", "durum", host)
    try:
        os.makedirs(durum, exist_ok=True)
    except OSError:
        sys.exit(0)
    kayit = {
        "session_id": girdi.get("session_id", ""),
        "bitis": time.strftime("%Y-%m-%d %H:%M"),
        "makine": host,
        "cwd": girdi.get("cwd", kok),
        "neden": girdi.get("reason", ""),
        "degisen_dosyalar": git_degisenler(kok)[:60],
    }
    try:
        with open(os.path.join(durum, "son-oturum.json"), "w", encoding="utf-8") as f:
            json.dump(kayit, f, ensure_ascii=False, indent=1)
    except OSError:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
