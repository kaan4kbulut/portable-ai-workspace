#!/usr/bin/env bash
# Install cc-safety-net (destructive-command guard hook) at a pinned version via npm. Idempotent. No login.
# Pin policy: newest release that is at least 7 days old; bump only after reading its changelog.
set -euo pipefail
SURUM="2.6.12"
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
if command -v cc-safety-net >/dev/null 2>&1 && [ "$(cc-safety-net --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" = "$SURUM" ]; then
  echo "[OK] cc-safety-net $SURUM"; exit 0
fi
command -v npm >/dev/null 2>&1 || { echo "[UYARI] npm yok; önce araclar/node.sh"; exit 1; }
npm install -g "cc-safety-net@$SURUM" >/dev/null
echo "[OK] cc-safety-net $(cc-safety-net --version 2>/dev/null | head -1) (sabit: $SURUM)"
