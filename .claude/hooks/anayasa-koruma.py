#!/usr/bin/env python3
"""PreToolUse hook (Edit | Write | MultiEdit): second layer protecting 00-cekirdek/ANAYASA.md.

settings.json already denies it; this hook catches path variants (../, symlink-resolved, absolute).
Blocks with exit 2 so the reason reaches Claude.
"""
import json
import os
import sys

ANAYASA = "00-cekirdek/ANAYASA.md"


def main():
    try:
        girdi = json.load(sys.stdin)
    except Exception:  # noqa: BLE001
        sys.exit(0)
    kok = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or girdi.get("cwd") or os.getcwd())
    ti = girdi.get("tool_input", {}) or {}
    hedef = ti.get("file_path") or ti.get("path") or ""
    if not hedef:
        sys.exit(0)
    mutlak = os.path.realpath(hedef if os.path.isabs(hedef) else os.path.join(kok, hedef))
    if mutlak == os.path.join(kok, ANAYASA) or os.path.basename(mutlak) == "ANAYASA.md":
        sys.stderr.write(
            "anayasa-koruma: 00-cekirdek/ANAYASA.md yalnızca insan tarafından düzenlenir. "
            "Değişiklik önerini (madde, eski/yeni metin, gerekçe) kullanıcıya sun.\n"
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
