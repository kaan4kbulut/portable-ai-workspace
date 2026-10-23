#!/usr/bin/env bash
# Run the embedded maintenance agent. Usage: bash 10-sistem/bakim/bakim.sh [--raporla] [--otomatik] [--cli claude|codex|opencode]
#   --raporla   diagnose only, change nothing
#   --otomatik  non-interactive (used by basla.sh on first run / CI); still never runs sudo/apt/login
#   --cli       force a CLI; default: first installed of claude → codex → opencode (login is not checked here)
# Feeds BAKIMCI.md + denetle.sh --tam output + bilinen-sorunlar.md to the CLI in print mode.
set -uo pipefail

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=../kurulum/lib/ortak.sh
source "$DIR/../kurulum/lib/ortak.sh"
KOK=$(atolye_koku "$DIR") || { echo "[HATA] atölye kökü bulunamadı"; exit 2; }
cd "$KOK"

RAPOR=0; OTOMATIK=0; CLI=""
while [ $# -gt 0 ]; do
  case "$1" in
    --raporla) RAPOR=1 ;;
    --otomatik) OTOMATIK=1 ;;
    --cli) CLI="$2"; shift ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) hata "bilinmeyen seçenek: $1"; exit 2 ;;
  esac
  shift
done

HOST=$(hostname_kisa); MAKINE=$(makine_adi "$KOK")
GUNLUK="$KOK/10-sistem/gunluk"; mkdir -p "$GUNLUK"
ZAMAN=$(date +%Y-%m-%d-%H%M)
RAPOR_DOSYA="$GUNLUK/bakim-$ZAMAN.md"

adim "Bakımcı · $MAKINE ($HOST) · kip: $([ "$RAPOR" = 1 ] && echo rapor || echo onarım)"

DENETIM=$(bash "$KOK/10-sistem/denetim/denetle.sh" --tam 2>&1 || true)
printf '%s\n' "$DENETIM" | tail -1
if ! printf '%s\n' "$DENETIM" | grep -qE '^\[(HATA|UYARI)\]'; then
  ok "denetim temiz; bakımcıya gerek yok"
  exit 0
fi

# pick a CLI
if [ -z "$CLI" ]; then
  if komut_var claude; then CLI=claude
  elif komut_var codex; then CLI=codex
  elif komut_var opencode; then CLI=opencode
  else
    hata "hiçbir CLI yok; teşhis raporu yazılıyor: $RAPOR_DOSYA"
    { echo "# Bakım teşhisi (CLI yok) · $HOST · $ZAMAN"; echo; echo '```'; echo "$DENETIM"; echo '```'; } > "$RAPOR_DOSYA"
    exit 1
  fi
fi

ISTEM=$(cat <<EOF
$(cat "$DIR/BAKIMCI.md")

---
## Bu çalıştırma
- Makine: $MAKINE ($HOST), tarih: $ZAMAN
- Kip: $([ "$RAPOR" = 1 ] && echo "RAPOR (hiçbir şey değiştirme)" || echo "ONARIM")
- Etkileşim: $([ "$OTOMATIK" = 1 ] && echo "yok; soru sorma, yetki dışı olanı listele" || echo "var")

## denetle.sh --tam çıktısı
\`\`\`
$DENETIM
\`\`\`

## bilinen-sorunlar.md
$(cat "$DIR/bilinen-sorunlar.md")

## onarimlar/
$(ls "$DIR/onarimlar" 2>/dev/null | grep -v README.md || echo "(boş)")
EOF
)

log "  CLI: $CLI · rapor: $RAPOR_DOSYA"
case "$CLI" in
  claude)
    # project scope (.claude/) applies: hooks, deny rules, bakimci agent definition
    if [ "$RAPOR" = 1 ]; then
      claude -p "$ISTEM" --permission-mode plan 2>&1 | tee "$RAPOR_DOSYA"
    else
      claude -p "$ISTEM" --permission-mode acceptEdits 2>&1 | tee "$RAPOR_DOSYA"
    fi ;;
  codex)
    uyar "codex çalıştırıcısı Aşama 2'de doğrulanacak; şimdilik rapor kipinde"
    codex exec "$ISTEM" 2>&1 | tee "$RAPOR_DOSYA" ;;
  opencode)
    uyar "opencode çalıştırıcısı Aşama 2'de doğrulanacak; şimdilik rapor kipinde"
    opencode run "$ISTEM" 2>&1 | tee "$RAPOR_DOSYA" ;;
  *) hata "bilinmeyen CLI: $CLI"; exit 2 ;;
esac

echo "---"
bash "$KOK/10-sistem/denetim/denetle.sh" --tam | tail -1
