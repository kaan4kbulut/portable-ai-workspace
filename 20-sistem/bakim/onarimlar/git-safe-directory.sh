#!/usr/bin/env bash
# Fix: git "dubious ownership" on a repo cloned/mounted under another uid (USB, shared disk). Adds safe.directory. Idempotent.
set -euo pipefail
KOK=$(git rev-parse --show-toplevel 2>/dev/null || cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
git config --global --get-all safe.directory 2>/dev/null | grep -qx "$KOK" && { echo "[OK] safe.directory zaten var: $KOK"; exit 0; }
git config --global --add safe.directory "$KOK" && echo "[OK] safe.directory eklendi: $KOK"
