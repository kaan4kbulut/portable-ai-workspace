#!/usr/bin/env bash
# Install Claude Code (native installer, user-local) when missing. Idempotent. No login.
set -euo pipefail
if command -v claude >/dev/null 2>&1; then echo "[OK] $(claude --version 2>/dev/null | head -1)"; exit 0; fi
curl -fsSL https://claude.ai/install.sh -o /tmp/claude-install.sh && bash /tmp/claude-install.sh >/dev/null; rm -f /tmp/claude-install.sh
export PATH="$HOME/.local/bin:$PATH"
echo "[OK] $(claude --version 2>/dev/null | head -1). Giriş: claude → /login"
