#!/usr/bin/env bash
# Antigravity CLI (agy): no stable public installer verified yet; report status, install manually.
set -euo pipefail
if command -v agy >/dev/null 2>&1; then echo "[OK] agy $(agy --version 2>/dev/null | head -1)"; exit 0; fi
echo "[UYARI] agy yok. Elle kur (bkz. 30-programlar/agy/README.md), sonra: agy install"
exit 0
