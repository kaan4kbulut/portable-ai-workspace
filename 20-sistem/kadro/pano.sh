#!/usr/bin/env bash
# Live job dashboard (tool, agent, model, effort, task, state, quota, GPU). Usage: bash 20-sistem/kadro/pano.sh
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -I "$DIR/isler.py" pano --izle
