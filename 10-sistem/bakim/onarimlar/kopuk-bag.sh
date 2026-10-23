#!/usr/bin/env bash
# Fix: a tool replaced a global config symlink with a real file. Usage: bash kopuk-bag.sh <hedef> <depo-kaynak>
# Shows the diff, copies the tool's version into the repo (so nothing is lost), then re-links. Idempotent.
set -euo pipefail
HEDEF="$1"; KAYNAK="$2"
[ -L "$HEDEF" ] && { echo "[OK] zaten symlink: $HEDEF"; exit 0; }
[ -f "$HEDEF" ] || { echo "[UYARI] hedef yok: $HEDEF"; exit 1; }
echo "--- fark (araç sürümü → depo):"; diff "$KAYNAK" "$HEDEF" || true
cp "$HEDEF" "$KAYNAK" && mv "$HEDEF" "$HEDEF.yedek-$(date +%Y%m%d-%H%M%S)" && ln -s "$KAYNAK" "$HEDEF"
echo "[OK] depo güncellendi ve yeniden bağlandı: $HEDEF -> $KAYNAK (değişikliği gözden geçirip commit et)"
