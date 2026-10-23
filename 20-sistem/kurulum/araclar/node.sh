#!/usr/bin/env bash
# Install Node 24 via nvm (user-local) when node is missing. Idempotent.
set -euo pipefail
if command -v node >/dev/null 2>&1; then echo "[OK] node $(node -v)"; exit 0; fi
export NVM_DIR="$HOME/.nvm"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh -o /tmp/nvm-install.sh
  bash /tmp/nvm-install.sh >/dev/null; rm -f /tmp/nvm-install.sh
fi
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"
nvm install 24 >/dev/null && nvm alias default 24 >/dev/null
echo "[OK] node $(node -v) (nvm)"
