#!/usr/bin/env python3
"""Stop hook: once per session, remind to write a handover note with /kapat. Never blocks.

Marker file 10-sistem/durum/<host>/oturum-<session_id>.isaret prevents repeats. Silent when stop_hook_active.
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
    durum = os.path.join(kok, "10-sistem", "durum", host)
    isaret = os.path.join(durum, f"oturum-{sid}.isaret")
    if os.path.exists(isaret):
        sys.exit(0)
    try:
        os.makedirs(durum, exist_ok=True)
        open(isaret, "w").close()
    except OSError:
        sys.exit(0)
    print(json.dumps({
        "systemMessage": "Atölye: oturumu bitirmeden önce `/kapat` ile devir notu yaz (40-hafiza/oturumlar/)."
    }, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
