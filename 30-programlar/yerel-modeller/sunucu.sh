#!/usr/bin/env bash
# Start llama-server on the local GPU with a measured preset; listens on 127.0.0.1 only (never exposed).
# Usage: bash 30-programlar/yerel-modeller/sunucu.sh [orta|hizli|ajan|gomme] [--kuru]
#   orta  Qwen3.5-9B   :8080  all layers on GPU (~68 tok/s)            default worker
#   hizli Qwen3.5-4B   :8081  all layers on GPU (~113 tok/s)           classification, summaries
#   ajan  Qwen3.6-35B-A3B :8080  experts of 16 layers on CPU (~47 tok/s)  agent/code; needs the GPU alone
#   gomme Qwen3-Embedding-0.6B :8082  embeddings
# Install binaries/weights first: bash 20-sistem/kurulum/araclar/llama.sh
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KOK="$(cd "$DIR/../.." && pwd)"
ETIKET=b11528
B="$KOK/30-programlar/dis-kaynaklar/llama.cpp/$ETIKET"
A="$DIR/agirliklar"

profil="${1:-orta}"
case "$profil" in
  orta)  model=Qwen3.5-9B-UD-Q4_K_XL.gguf;          port=8080; ek=(-ngl 99 -c 32768 -np 2) ;;
  hizli) model=Qwen3.5-4B-UD-Q4_K_XL.gguf;          port=8081; ek=(-ngl 99 -c 16384 -np 2) ;;
  ajan)  model=Qwen3.6-35B-A3B-UD-IQ4_XS.gguf;      port=8080; ek=(-ngl 99 -ncmoe 18 -c 32768 -np 1) ;;
  gomme) model=Qwen3-Embedding-0.6B-Q8_0.gguf;      port=8082; ek=(-ngl 99 -c 8192 --embedding --pooling last) ;;
  *) printf '[HATA] profil · %s · orta|hizli|ajan|gomme\n' "$profil" >&2; exit 2 ;;
esac

SUNUCU="$B/llama-$ETIKET/llama-server"
[ -x "$SUNUCU" ] || { printf '[HATA] llama-server yok · %s · bash 20-sistem/kurulum/araclar/llama.sh\n' "${SUNUCU#"$KOK"/}" >&2; exit 2; }
[ -f "$A/$model" ] || { printf '[HATA] ağırlık yok · %s · bash 20-sistem/kurulum/araclar/llama.sh --yalniz-model\n' "$model" >&2; exit 2; }

export LD_LIBRARY_PATH="$B/cudart-llama-$ETIKET-bin-ubuntu-cuda-12.8-x64:$B/llama-$ETIKET${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
komut=("$SUNUCU" -m "$A/$model" --alias "yerel-$profil" --host 127.0.0.1 --port "$port" --no-webui -fa on "${ek[@]}")
if [ "${2:-}" = "--kuru" ]; then printf '%q ' "${komut[@]}"; printf '\n'; exit 0; fi
exec "${komut[@]}"
