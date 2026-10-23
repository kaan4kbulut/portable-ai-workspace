#!/usr/bin/env bash
# Update check (report only, applies nothing). Usage: bash 20-sistem/bakim/guncelle.sh
# Compares installed CLI versions with latest published, atölye vs remote, and lists project repos behind their remotes.
# Writes 20-sistem/durum/<host>/guncelleme-raporu.md
set -uo pipefail

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=../kurulum/lib/ortak.sh
source "$DIR/../kurulum/lib/ortak.sh"
KOK=$(atolye_koku "$DIR") || { echo "[HATA] atölye kökü bulunamadı"; exit 2; }
cd "$KOK"
HOST=$(hostname_kisa); DURUM="$KOK/20-sistem/durum/$HOST"; mkdir -p "$DURUM"
RAPOR="$DURUM/guncelleme-raporu.md"

son_npm() { timeout 8 npm view "$1" version 2>/dev/null || echo "?"; }
son_gh()  { timeout 8 curl -fsSL "https://api.github.com/repos/$1/releases/latest" 2>/dev/null | grep -m1 '"tag_name"' | sed -E 's/.*"v?([^"]+)".*/\1/' || echo "?"; }

{
  echo "# Güncelleme raporu · $HOST · $(date +%Y-%m-%d\ %H:%M)"
  echo
  if ! cevrimici_mi "$KOK" && ! timeout 4 curl -fsI https://github.com >/dev/null 2>&1; then
    echo "- çevrimdışı: sürüm karşılaştırması yapılamadı"
  else
    echo "| araç | kurulu | son | durum |"; echo "|---|---|---|---|"
    satir() { local ad="$1" kurulu="$2" son="$3" d="="; [ "$son" != "?" ] && [ "$kurulu" != "$son" ] && d="GÜNCELLE"; echo "| $ad | $kurulu | $son | $d |"; }
    komut_var claude   && satir claude   "$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" "$(son_npm @anthropic-ai/claude-code)"
    komut_var codex    && satir codex    "$(codex --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" "$(son_npm @openai/codex)"
    komut_var opencode && satir opencode "$(opencode --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" "$(son_npm opencode-ai)"
    komut_var gh       && satir gh       "$(gh --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" "$(son_gh cli/cli)"
    komut_var uv       && satir uv       "$(uv --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)" "$(son_gh astral-sh/uv)"
    komut_var node     && satir node     "$(node -v | tr -d v)" "$(son_npm node | head -1)"
    komut_var agy      && echo "| agy | $(agy --version 2>/dev/null | head -1) | ? | agy update ile kontrol |"
    echo
    git fetch -q origin 2>/dev/null || true
    geri=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0); ileri=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
    echo "- atölye: uzak $geri ileride, yerel $ileri push edilmemiş"
  fi
  echo
  echo "## Projeler"
  for p in 40-projeler/aktif/*/; do
    [ -d "$p/.git" ] || continue
    git -C "$p" fetch -q origin 2>/dev/null || true
    g=$(git -C "$p" rev-list --count HEAD..@{u} 2>/dev/null || echo 0); i=$(git -C "$p" rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
    k=$(git -C "$p" status --porcelain | wc -l)
    echo "- $(basename "$p"): uzak $g ileride · $i push edilmemiş · $k değişiklik"
    [ -f "$p/package.json" ] && echo "  - npm: \`npm outdated\` ile bak"
    [ -f "$p/pyproject.toml" ] && echo "  - python: \`uv lock --upgrade --dry-run\` ile bak"
  done
  echo
  echo "Uygulamak için: araç → 20-sistem/kurulum/araclar/<ad>.sh (önce kaldır) ya da aracın kendi güncelleme komutu; atölye → git pull."
} | tee "$RAPOR"
