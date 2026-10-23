#!/usr/bin/env bash
# Install opencode (user-local) when missing. Idempotent. No login.
set -euo pipefail
if command -v opencode >/dev/null 2>&1; then echo "[OK] opencode $(opencode --version 2>/dev/null | head -1)"; exit 0; fi
curl -fsSL https://opencode.ai/install -o /tmp/opencode-install.sh && bash /tmp/opencode-install.sh >/dev/null; rm -f /tmp/opencode-install.sh
export PATH="$HOME/.opencode/bin:$PATH"
echo "[OK] opencode $(opencode --version 2>/dev/null | head -1). Giriş: opencode auth login"
