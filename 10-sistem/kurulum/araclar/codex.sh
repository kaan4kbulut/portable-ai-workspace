#!/usr/bin/env bash
# Install OpenAI Codex CLI via npm (needs node) when missing. Idempotent. No login.
set -euo pipefail
if command -v codex >/dev/null 2>&1; then echo "[OK] $(codex --version 2>/dev/null | head -1)"; exit 0; fi
export NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
command -v npm >/dev/null 2>&1 || { echo "[UYARI] npm yok; önce araclar/node.sh"; exit 1; }
npm install -g @openai/codex >/dev/null
echo "[OK] $(codex --version 2>/dev/null | head -1). Giriş: codex login"
