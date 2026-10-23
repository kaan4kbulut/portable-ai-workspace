#!/usr/bin/env bash
# Docker: report only (needs root/apt); install is a machine-specific sudo step in 10-donanim/<makine>/.
set -euo pipefail
if command -v docker >/dev/null 2>&1; then echo "[OK] $(docker --version)"; exit 0; fi
echo "[UYARI] docker yok; sudo gerektirir: sudo apt-get install -y docker.io docker-compose-v2 && sudo usermod -aG docker \$USER"
exit 0
