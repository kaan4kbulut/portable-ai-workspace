#!/usr/bin/env python3
"""Stop hook: once per session, remind to write a handover note with /kapat. Never blocks.

20-sistem/durum/<host>/son-hatirlatma.txt holds the last 20 reminded session_ids (one file, bounded; concurrent sessions ok).
Silent when stop_hook_active.
"""
import json
import os
import socket
import sys


def main():
    try:
        girdi = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        sys.exit(0)
    if girdi.get("stop_hook_active"):
        sys.exit(0)
    kok = os.environ.get("CLAUDE_PROJECT_DIR") or girdi.get("cwd") or os.getcwd()
    host = socket.gethostname().split(".")[0]
    sid = (girdi.get("session_id") or "bilinmiyor")[:36]
    durum = os.path.join(kok, "20-sistem", "durum", host)
    isaret = os.path.join(durum, "son-hatirlatma.txt")
    try:
        with open(isaret, encoding="utf-8") as f:
            onceki = [s.strip() for s in f if s.strip()]
    except OSError:
        onceki = []
    if sid in onceki:
        sys.exit(0)
    try:
        os.makedirs(durum, exist_ok=True)
        with open(isaret, "w", encoding="utf-8") as f:
            f.write("\n".join((onceki + [sid])[-20:]) + "\n")
    except OSError:
        sys.exit(0)
    print(json.dumps({
        "systemMessage": "Atölye: oturumu bitirmeden önce `/kapat` ile devir notu yaz (60-hafiza/oturumlar/)."
    }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
