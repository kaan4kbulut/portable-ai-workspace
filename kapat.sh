#!/usr/bin/env bash
# End-of-day routine. Usage: bash kapat.sh
#   quick check → handover-note reminder (drafts one from son-oturum.json if missing) → uncommitted summary (atölye + projects)
#   → asks before commit, asks before push (only when online). Never pushes on its own.
set -uo pipefail

ATOLYE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$ATOLYE"
# shellcheck source=10-sistem/kurulum/lib/ortak.sh
source "$ATOLYE/10-sistem/kurulum/lib/ortak.sh"
HOST=$(hostname_kisa); MAKINE=$(makine_adi "$ATOLYE"); DURUM="$ATOLYE/10-sistem/durum/$HOST"
GUNLUK="$ATOLYE/10-sistem/gunluk"; mkdir -p "$GUNLUK" "$DURUM"
BUGUN=$(date +%Y-%m-%d); YIL=$(date +%Y); LOG="$GUNLUK/kapat-$BUGUN.log"

adim "Kapanış · $MAKINE · $BUGUN" | tee -a "$LOG"
bash "$ATOLYE/10-sistem/denetim/denetle.sh" --hizli | tail -1 | tee -a "$LOG"

# handover note
NOT=$(ls "$ATOLYE/40-hafiza/oturumlar/$YIL/$BUGUN"-*-"$MAKINE"-*.md 2>/dev/null | tail -1)
if [ -n "$NOT" ]; then
  ok "devir notu var: ${NOT#$ATOLYE/}" | tee -a "$LOG"
else
  mkdir -p "$ATOLYE/40-hafiza/oturumlar/$YIL"
  TASLAK="$ATOLYE/40-hafiza/oturumlar/$YIL/$(date +%Y-%m-%d-%H%M)-$MAKINE-taslak.md"
  DEGISEN=$(git status --porcelain | sed 's/^...//' | head -30)
  [ -f "$DURUM/son-oturum.json" ] && DEGISEN="$DEGISEN
$(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print('\n'.join(d.get('degisen_dosyalar',[])))" "$DURUM/son-oturum.json" 2>/dev/null)"
  sed -e "s/{{tarih}}/$(date +%Y-%m-%d\ %H:%M)/" -e "s/{{makine}}/$MAKINE/" -e "s/{{konu}}/TODO/" \
      "$ATOLYE/80-sablonlar/belge/oturum-notu.md" > "$TASLAK"
  printf '\n<!-- kapat.sh taslağı; dokunulan dosyalar (git + son oturum): -->\n%s\n' "$(printf '%s\n' "$DEGISEN" | sort -u | sed 's/^/- /')" >> "$TASLAK"
  uyar "bugün devir notu yoktu; taslak yazıldı: ${TASLAK#$ATOLYE/} → metin alanlarını doldur (ya da Claude'da /kapat)" | tee -a "$LOG"
fi

# update report (one line)
if [ -f "$DURUM/guncelleme-raporu.md" ]; then
  g=$(grep -c 'GÜNCELLE' "$DURUM/guncelleme-raporu.md" 2>/dev/null || echo 0)
  [ "$g" -gt 0 ] && uyar "güncelleme bekleyen $g araç (bkz. 10-sistem/durum/$HOST/guncelleme-raporu.md)"
fi

# uncommitted summary
echo; echo "Atölye:"; git status --short | head -20
for p in 30-projeler/aktif/*/; do
  [ -d "$p/.git" ] || continue
  k=$(git -C "$p" status --porcelain | wc -l); i=$(git -C "$p" rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
  [ "$k" -gt 0 ] || [ "$i" -gt 0 ] && echo "Proje $(basename "$p"): $k değişiklik, $i push edilmemiş commit"
done

if [ -n "$(git status --porcelain)" ] && [ -t 0 ]; then
  read -rp "Atölyeyi commit et? [e/H] " c
  if [ "${c:-h}" = "e" ]; then
    read -rp "Commit mesajı (type(scope): özet): " m
    git add -A && git commit -q -m "${m:-chore(atolye): gün sonu}" && ok "commit atıldı" | tee -a "$LOG"
  fi
fi
if [ -t 0 ] && cevrimici_mi "$ATOLYE"; then
  i=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
  if [ "$i" -gt 0 ]; then
    read -rp "$i commit push edilsin mi? [e/H] " p
    [ "${p:-h}" = "e" ] && git push -q && ok "push tamam" | tee -a "$LOG"
  fi
fi
ok "kapanış bitti ($LOG)"
