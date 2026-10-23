#!/usr/bin/env bash
# Install uv (Python manager) user-locally when missing. Idempotent.
set -euo pipefail
if command -v uv >/dev/null 2>&1; then echo "[OK] $(uv --version)"; exit 0; fi
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && sh /tmp/uv-install.sh >/dev/null; rm -f /tmp/uv-install.sh
export PATH="$HOME/.local/bin:$PATH"
echo "[OK] $(uv --version)"
