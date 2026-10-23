#!/usr/bin/env bash
# Atölye entry point. Usage: bash basla.sh [--genel] [--ayri-hesap] [--claude|--codex|--opencode|--agy] [--sadece-pano] [-- <cli args>]
#   first run on a machine → kur.sh; then: git safety, online check + pull, denetle.sh --tam, status board, exec the CLI.
#   --genel       pass to kur.sh (link global CLI config to the repo)
#   --ayri-hesap  experimental: CLAUDE_CONFIG_DIR inside 10-sistem/durum/<host>/claude-config (git-ignored)
#   --sadece-pano print the board and exit (no CLI)
# Never logs in; never reads credential files.
set -uo pipefail

ATOLYE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ATOLYE"
# shellcheck source=10-sistem/kurulum/lib/ortak.sh
source "$ATOLYE/10-sistem/kurulum/lib/ortak.sh"

GENEL=0; AYRI=0; CLI=claude; PANO=0; CLI_ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --genel) GENEL=1 ;;
    --ayri-hesap) AYRI=1 ;;
    --claude) CLI=claude ;; --codex) CLI=codex ;; --opencode) CLI=opencode ;; --agy) CLI=agy ;;
    --sadece-pano) PANO=1 ;;
    --) shift; CLI_ARGS=("$@"); break ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) hata "bilinmeyen seçenek: $1"; exit 2 ;;
  esac
  shift
done

HOST=$(hostname_kisa); MAKINE=$(makine_adi "$ATOLYE"); FS=$(fs_turu "$ATOLYE")
DURUM="$ATOLYE/10-sistem/durum/$HOST"

# 1. first run on this machine
if [ ! -f "$DURUM/ilk-kurulum.txt" ]; then
  adim "Bu makinede ilk açılış ($HOST) → kurulum"
  bash "$ATOLYE/10-sistem/kurulum/kur.sh" $([ "$GENEL" = 1 ] && echo --genel) || uyar "kur.sh uyarıyla bitti"
elif [ "$GENEL" = 1 ]; then
  bash "$ATOLYE/10-sistem/kurulum/kur.sh" --genel
fi
mkdir -p "$DURUM"

# 2. git safety (cheap, idempotent)
git config --global --get-all safe.directory 2>/dev/null | grep -qx "$ATOLYE" || git config --global --add safe.directory "$ATOLYE"
[ "$(git config core.hooksPath 2>/dev/null)" = "10-sistem/denetim/git-hooks" ] || git config core.hooksPath 10-sistem/denetim/git-hooks
if fs_kisitli "$ATOLYE"; then
  git config core.filemode false; git config core.symlinks false; git config core.ignorecase true
fi

# 3. network + pull
if cevrimici_mi "$ATOLYE"; then
  AG="çevrimiçi"
  if [ -z "$(git status --porcelain)" ]; then
    git pull -q --ff-only 2>/dev/null && AG="çevrimiçi · pull tamam" || AG="çevrimiçi · pull atlandı (çakışma/ff değil)"
  else
    AG="çevrimiçi · pull atlandı (commit'lenmemiş değişiklik var)"
  fi
else
  AG="çevrimdışı (pull ve giriş denetimi atlandı)"
fi

# 4. check
DENETIM=$(bash "$ATOLYE/10-sistem/denetim/denetle.sh" --tam 2>&1); RC=$?
printf '%s\n' "$DENETIM" > "$DURUM/son-denetim.txt"
OZET=$(printf '%s\n' "$DENETIM" | tail -1)

# 5. board
SON_NOT=$(ls "$ATOLYE"/40-hafiza/oturumlar/*/*.md 2>/dev/null | grep -v README | sort | tail -1)
AKTIF=$(cat "$DURUM/aktif-proje.txt" 2>/dev/null || true)
[ -z "$AKTIF" ] && AKTIF=$(grep -E '^\|' 30-projeler/DIZIN.md 2>/dev/null | grep -i '| aktif' | head -1 | cut -d'|' -f2 | tr -d ' `')
GELEN=$(find 70-gelen-kutusu -mindepth 1 -maxdepth 1 ! -name README.md ! -name AYIKLAMA.md 2>/dev/null | wc -l)
echo
echo "┌─ ATÖLYE ─────────────────────────────────────────────────"
echo "│ makine : $MAKINE ($HOST) · fs: $FS · $AG"
echo "│ sürüm  : $(grep -m1 -oE '^## [0-9.]+' SURUM.md | cut -c4-) · git: $(git rev-parse --short HEAD 2>/dev/null) · $(git status --porcelain | wc -l) değişiklik"
echo "│ araçlar: claude $(surum_al claude | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) · codex $(surum_al codex | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) · opencode $(surum_al opencode | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) · agy $(surum_al agy | head -1) · gh $(surum_al gh | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
echo "│ giriş  : $(printf '%s\n' "$DENETIM" | grep -E '^\[(OK|UYARI)\] giriş' | sed -E 's/^\[OK\] giriş: /✓/; s/^\[UYARI\] giriş · ([a-z]+).*/✗\1/' | tr '\n' ' ')"
echo "│ proje  : ${AKTIF:-—} · gelen kutusu: $GELEN öğe · son not: $(basename "${SON_NOT:-yok}")"
echo "│ denetim: $OZET"
echo "└──────────────────────────────────────────────────────────"
if [ "$RC" = 2 ]; then
  printf '%s\n' "$DENETIM" | grep -E '^\[HATA\]' | head -5
  if [ -t 0 ] && [ "$PANO" = 0 ]; then
    read -rp "Hatalar var. Bakımcı onarsın mı? [e/H] " c
    [ "${c:-h}" = "e" ] && bash "$ATOLYE/10-sistem/bakim/bakim.sh"
  fi
fi
[ "$PANO" = 1 ] && exit "$RC"

# 6. launch
if [ "$AYRI" = 1 ] && [ "$CLI" = claude ]; then
  export CLAUDE_CONFIG_DIR="$DURUM/claude-config"; mkdir -p "$CLAUDE_CONFIG_DIR"
  uyar "deneysel: CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR (kimlik bu klasörde kalır; git dışı)"
fi
komut_var "$CLI" || { hata "$CLI kurulu değil (10-sistem/kurulum/araclar/$CLI.sh)"; exit 2; }
echo "→ $CLI başlatılıyor (giriş yoksa aracın kendi login komutunu kullan)"
exec "$CLI" "${CLI_ARGS[@]}"
