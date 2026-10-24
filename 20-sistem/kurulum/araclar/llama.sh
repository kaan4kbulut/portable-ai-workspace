#!/usr/bin/env bash
# Install llama.cpp (prebuilt Ubuntu CUDA 12.8 build, no sudo) and the local model weights. Idempotent.
# Binaries: 30-programlar/dis-kaynaklar/llama.cpp/<tag>/   Weights: 30-programlar/yerel-modeller/agirliklar/
# Every download is checked against its published SHA256; a mismatch is deleted and reported.
# Usage: bash 20-sistem/kurulum/araclar/llama.sh [--yalniz-ikili | --yalniz-model]
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$DIR/../lib/ortak.sh"
KOK="$(atolye_koku)"

ETIKET=b11528  # 2026-10-09; pinned on purpose, bump deliberately
URL="https://github.com/ggml-org/llama.cpp/releases/download/$ETIKET"
IKILI=(
  "llama-$ETIKET-bin-ubuntu-cuda-12.8-x64.tar.gz 18cd04bb540cbe3e7b2dbf0a590f2ec81d9ed33e199c2848b5fcb4f40f52a45d"
  "cudart-llama-$ETIKET-bin-ubuntu-cuda-12.8-x64.tar.gz 89c53f1633e4008b58c853c04c74e1eaca53ff5e62ddb2fc746ad3fc273b8c1d"
)
# repo file sha256 (Hugging Face LFS oid)
MODELLER=(
  "unsloth/Qwen3.5-4B-GGUF Qwen3.5-4B-UD-Q4_K_XL.gguf b252c5610a42ca82d20fe2a12813e9d069eed89292907e26c783eeb0bc961bc7"
  "unsloth/Qwen3.5-9B-GGUF Qwen3.5-9B-UD-Q4_K_XL.gguf 6f5d30666c2d8ae16a306e616d95341dcf3cc46810df84d7e6f5a7d1e4c1b293"
  "Qwen/Qwen3-Embedding-0.6B-GGUF Qwen3-Embedding-0.6B-Q8_0.gguf 06507c7b42688469c4e7298b0a1e16deff06caf291cf0a5b278c308249c3e439"
  "unsloth/Qwen3.6-35B-A3B-GGUF Qwen3.6-35B-A3B-UD-IQ4_XS.gguf 649d7508507b84638732c4f52c24c8b15843c6dca2f3ff793ae07c14a67ebbb3"
)

indir_dogrula() {  # indir_dogrula <url> <hedef> <sha256>
  local url=$1 hedef=$2 sha=$3
  if [ -f "$hedef" ] && [ "$(sha256sum "$hedef" | cut -d' ' -f1)" = "$sha" ]; then ok "zaten var: $(basename "$hedef")"; return 0; fi
  log "indiriliyor: $(basename "$hedef")"
  curl -fL --retry 3 -C - -o "$hedef.part" "$url"
  if [ "$(sha256sum "$hedef.part" | cut -d' ' -f1)" != "$sha" ]; then
    rm -f "$hedef.part"; hata "SHA256 uyuşmadı: $(basename "$hedef")"; return 1
  fi
  mv "$hedef.part" "$hedef"; ok "doğrulandı: $(basename "$hedef")"
}

if [ "${1:-}" != "--yalniz-model" ]; then
  adim "llama.cpp $ETIKET (CUDA 12.8)"
  D="$KOK/30-programlar/dis-kaynaklar/llama.cpp/$ETIKET"
  mkdir -p "$D/indirilen"
  for satir in "${IKILI[@]}"; do
    read -r ad sha <<<"$satir"
    indir_dogrula "$URL/$ad" "$D/indirilen/$ad" "$sha"
    tar -xzf "$D/indirilen/$ad" -C "$D"
  done
  SUNUCU="$(find "$D" -name llama-server -type f | head -1)"
  [ -n "$SUNUCU" ] && ok "llama-server: ${SUNUCU#"$KOK"/}" || hata "llama-server arşivde bulunamadı"
fi

if [ "${1:-}" != "--yalniz-ikili" ]; then
  adim "model ağırlıkları"
  A="$KOK/30-programlar/yerel-modeller/agirliklar"
  mkdir -p "$A"
  for satir in "${MODELLER[@]}"; do
    read -r repo ad sha <<<"$satir"
    indir_dogrula "https://huggingface.co/$repo/resolve/main/$ad" "$A/$ad" "$sha" || true
  done
fi
