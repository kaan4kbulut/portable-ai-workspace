#!/usr/bin/env bash
# Install GitHub CLI user-locally (binary tarball into ~/.local/bin) when missing. Idempotent. No login.
set -euo pipefail
if command -v gh >/dev/null 2>&1; then echo "[OK] $(gh --version | head -1)"; exit 0; fi
ARCH=$(uname -m); case "$ARCH" in x86_64) A=amd64 ;; aarch64|arm64) A=arm64 ;; *) echo "[UYARI] gh: desteklenmeyen mimari $ARCH"; exit 1 ;; esac
VER=$(curl -fsSL https://api.github.com/repos/cli/cli/releases/latest | grep -m1 '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')
TMP=$(mktemp -d); curl -fsSL "https://github.com/cli/cli/releases/download/v${VER}/gh_${VER}_linux_${A}.tar.gz" | tar -xz -C "$TMP"
mkdir -p "$HOME/.local/bin"; cp "$TMP"/gh_*/bin/gh "$HOME/.local/bin/gh"; rm -rf "$TMP"
echo "[OK] gh $VER kuruldu (~/.local/bin). Giriş: gh auth login"
