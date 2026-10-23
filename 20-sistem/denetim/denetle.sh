#!/usr/bin/env bash
# Structure/health check for the atölye. Usage: bash 20-sistem/denetim/denetle.sh [--hizli|--commit|--tam]
#   --hizli  structure invariants only (default; ~1 s; used by the SessionStart hook)
#   --commit staged files only, errors block the commit (used by git-hooks/pre-commit)
#   --tam    everything: + global links, tool versions, logins (via each tool's own command), git remote state, projects
# Exit: 0 clean · 1 warnings · 2 errors. Output lines: [HATA|UYARI|OK|BILGI] kural · yol · öneri
set -uo pipefail
export LC_ALL=C   # byte-wise [a-z] ranges; Turkish locale breaks ERE ranges

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=../kurulum/lib/ortak.sh
source "$DIR/../kurulum/lib/ortak.sh"
KOK=$(atolye_koku "$DIR") || { echo "[HATA] atölye kökü bulunamadı"; exit 2; }
KURAL="$DIR/kurallar"
KIP="${1:---hizli}"
cd "$KOK"

HATA=0; UYARI=0
h() { printf '[HATA] %s\n' "$*"; HATA=$((HATA+1)); }
u() { printf '[UYARI] %s\n' "$*"; UYARI=$((UYARI+1)); }
o() { printf '[OK] %s\n' "$*"; }
b() { printf '[BILGI] %s\n' "$*"; }

oku_liste() { grep -vE '^\s*(#|$)' "$1" 2>/dev/null || true; }

# Files under inspection: tracked (+ staged in --commit); untracked-but-not-ignored are inspected for naming/secrets too.
if [ "$KIP" = "--commit" ]; then
  mapfile -t DOSYALAR < <(git diff --cached --name-only --diff-filter=ACMR)
else
  mapfile -t DOSYALAR < <(git ls-files; git ls-files --others --exclude-standard)
fi

# ---------------------------------------------------------------- root entries
mapfile -t IZINLI < <(oku_liste "$KURAL/izinli-kokler.txt")
for e in $(ls -A "$KOK"); do
  [ "$e" = ".git" ] && continue
  if ! printf '%s\n' "${IZINLI[@]}" | grep -qx "$e"; then
    h "kök-dışı · $e · 90-gelen-kutusu/'na taşı ya da kurallar/izinli-kokler.txt'e ekle (ANAYASA 4.3)"
  fi
done

# ---------------------------------------------------------------- naming
DIZIN_RE=$(oku_liste "$KURAL/ad-regex.txt" | sed -n '1p')
DOSYA_RE=$(oku_liste "$KURAL/ad-regex.txt" | sed -n '2p')
mapfile -t ISTISNA < <(oku_liste "$KURAL/istisnalar.txt")
istisna_mi() { local p="$1" i; for i in "${ISTISNA[@]}"; do case "$p" in $i|$i/*|*/$i|*/$i/*) return 0 ;; esac; done; return 1; }

for f in "${DOSYALAR[@]}"; do
  [ -e "$f" ] || continue
  istisna_mi "$f" && continue
  IFS='/' read -ra parcalar <<< "$f"
  n=${#parcalar[@]}
  for ((i=0; i<n-1; i++)); do
    d="${parcalar[$i]}"
    istisna_mi "$(IFS=/; echo "${parcalar[*]:0:i+1}")" && break
    [[ "$d" =~ $DIZIN_RE ]] || { h "adlandırma · $(IFS=/; echo "${parcalar[*]:0:i+1}")/ · küçük harf, aksansız, kebab-case (ANAYASA 3)"; break; }
  done
  ad="${parcalar[$((n-1))]}"
  [[ "$ad" =~ $DOSYA_RE ]] || h "adlandırma · $f · dosya adı kurala uymuyor (ANAYASA 3)"
  case "$ad" in
    *[Tt][Oo][Kk][Ee][Nn]*|*[Ss][Ee][Cc][Rr][Ee][Tt]*|auth.json|.credentials*) h "yasak-ad · $f · sır ima eden ad depoda yasak (ANAYASA 3.5)" ;;
  esac
done

# case-insensitive collisions
dup=$(printf '%s\n' "${DOSYALAR[@]}" | tr 'A-Z' 'a-z' | sort | uniq -d | head -5)
[ -n "$dup" ] && h "büyük-küçük-çakışma · $(echo "$dup" | tr '\n' ' ')· exFAT/Windows'ta çakışır"

# symlinks inside the repo
for f in "${DOSYALAR[@]}"; do [ -L "$f" ] && h "symlink · $f · depo içinde symlink yasak (ANAYASA 2.2)"; done

# big files
for f in "${DOSYALAR[@]}"; do
  [ -f "$f" ] || continue
  sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
  [ "$sz" -gt 52428800 ] && h "büyük-dosya · $f · $((sz/1048576)) MB; 30-programlar/dis-kaynaklar/ ya da agirliklar/ (git dışı)"
done

# secrets
if [ -s "$KURAL/sir-desenleri.txt" ] && [ ${#DOSYALAR[@]} -gt 0 ]; then
  while IFS= read -r desen; do
    [ -z "$desen" ] && continue
    # process substitution, not a pipe: h() must run in this shell so the error is counted (and blocks a commit)
    while read -r f; do
      h "sır · $f · desen eşleşti: $desen (AGENTS.md Kesin kural 4)"
    done < <(if [ "$KIP" = "--commit" ]; then
               # scan what will actually be committed (the index), not the working-tree file
               git grep --cached -lE "$desen" -- "${DOSYALAR[@]}" 2>/dev/null | grep -v 'sir-desenleri.txt$'
             else
               printf '%s\n' "${DOSYALAR[@]}" | grep -v 'sir-desenleri.txt$' | xargs -r -d '\n' grep -lE "$desen" 2>/dev/null
             fi)
  done < <(oku_liste "$KURAL/sir-desenleri.txt")
fi

# "./script" calls in tracked docs/scripts (portability)
while read -r s; do u "nokta-betik · $s · bash yol/betik.sh kullan (ANAYASA 2.2)"; done < <(
  grep -rnE '(^|[[:space:]"])\./[a-z0-9-]+\.(sh|py)\b' --include='*.sh' --include='*.json' --include='*.py' \
    --exclude-dir=.git --exclude-dir=dis-kaynaklar --exclude-dir=40-projeler --exclude-dir=node_modules . 2>/dev/null \
    | grep -v 'denetle.sh' | head -5)

# skill/agent frontmatter: an unquoted value containing ": " is invalid YAML and the skill silently fails to load
for f in "${DOSYALAR[@]}"; do
  case "$f" in .claude/skills/*/SKILL.md|.claude/agents/*.md) ;; *) continue ;; esac
  [ -f "$f" ] || continue
  while read -r s; do
    h "yaml · $f · tırnaksız değerde ': ' var, beceri yüklenmez: ${s:0:60}… → \"…\" ya da >- kullan"
  done < <(awk 'NR==1 && $0!="---"{exit} NR>1 && $0=="---"{exit} NR>1' "$f" | grep -E '^[a-z-]+: [^"'"'"'>|].*: ' | head -1)
done

# ---------------------------------------------------------------- README per tracked dir, depth
mapfile -t DIZINLER < <(printf '%s\n' "${DOSYALAR[@]}" | xargs -r -d '\n' -n1 dirname | sort -u | grep -v '^\.$')
for d in "${DIZINLER[@]}"; do
  [ -d "$d" ] || continue
  istisna_mi "$d" && continue
  derinlik=$(awk -F/ '{print NF}' <<< "$d")
  [ "$derinlik" -gt 4 ] && u "derinlik · $d/ · ${derinlik} seviye (en çok 4, ANAYASA 4.1)"
  if [ ! -f "$d/README.md" ]; then
    # dirs that are themselves leaf containers of a documented parent don't need README (skills/<ad>, oturumlar/<yil>, cihazlar/<makine>)
    case "$d" in
      .claude/skills/*|.claude/rules|.claude/agents|.claude/hooks|.claude|60-hafiza/oturumlar/*|10-donanim/*|20-sistem/kurulum/araclar|20-sistem/kurulum/lib|20-sistem/denetim/kurallar|20-sistem/denetim/git-hooks|00-cekirdek/sablonlar/*|30-programlar/*/genel|80-arsiv/*) ;;
      *) if [ "$KIP" = "--commit" ]; then h "readme-yok · $d/ · README.md ekle (ANAYASA 4.2)"; else u "readme-yok · $d/ · README.md ekle (ANAYASA 4.2)"; fi ;;
    esac
  fi
done

# ---------------------------------------------------------------- indexes, inbox age, versions
for p in 40-projeler/aktif/*/; do
  [ -d "$p" ] || continue; n=$(basename "$p")
  grep -qE "^\|\s*\`?$n\`?\s*\|" 40-projeler/DIZIN.md 2>/dev/null || u "dizin · 40-projeler/aktif/$n · DIZIN.md'de satırı yok"
done
for p in 30-programlar/dis-kaynaklar/*/; do
  [ -d "$p" ] || continue; n=$(basename "$p")
  grep -qE "^\|\s*\`?$n\`?\s*\|" 30-programlar/dis-kaynaklar/DIZIN.md 2>/dev/null || u "dizin · 30-programlar/dis-kaynaklar/$n · DIZIN.md'de satırı yok"
done
if [ -d 90-gelen-kutusu ]; then
  while read -r f; do u "gelen-kutusu · $f · 30 günden eski; /ayikla (ANAYASA 6.2)"; done < <(
    find 90-gelen-kutusu -mindepth 1 -maxdepth 1 ! -name README.md ! -name AYIKLAMA.md -mtime +30 2>/dev/null | head -5)
fi
anayasa_v=$(grep -m1 -oE '^Sürüm: [0-9]+\.[0-9]+' 00-cekirdek/ANAYASA.md | cut -d' ' -f2)
surum_v=$(grep -m1 -oE '^## [0-9]+\.[0-9]+' SURUM.md | cut -d' ' -f2)
# ANAYASA 10.2: the header carries N.0 and matches the last MAJOR in SURUM.md (minor/patch never touch the header)
[ -n "$anayasa_v" ] && [ -n "$surum_v" ] && [ "${anayasa_v%%.*}" != "${surum_v%%.*}" ] && u "sürüm · ANAYASA $anayasa_v ≠ SURUM.md $surum_v (major) · birini güncelle (ANAYASA 10.2)"

# ---------------------------------------------------------------- --tam extras
if [ "$KIP" = "--tam" ]; then
  HOST=$(hostname_kisa); DURUM="20-sistem/durum/$HOST"
  if cevrimici_mi "$KOK"; then CEVRIM=1; b "ağ: çevrimiçi"; else CEVRIM=0; b "ağ: çevrimdışı (uzak/giriş denetimleri atlandı)"; fi

  # tool versions
  for a in claude codex opencode agy gh git node uv python3; do
    v=$(surum_al "$a"); [ "$v" = "yok" ] && u "araç · $a · kurulu değil (20-sistem/kurulum/araclar/$a.sh)" || b "araç: $a · $v"
  done

  # logins via the tools' own commands only
  if [ "$CEVRIM" = 1 ]; then
    komut_var gh && { timeout 8 gh auth status >/dev/null 2>&1 && o "giriş: gh" || u "giriş · gh · gh auth login"; }
    komut_var codex && { timeout 8 codex login status >/dev/null 2>&1 && o "giriş: codex" || u "giriş · codex · codex login"; }
    komut_var opencode && { timeout 8 opencode auth list 2>/dev/null | grep -qiE 'anthropic|openai|google|[a-z]' && o "giriş: opencode" || u "giriş · opencode · opencode auth login"; }
    komut_var claude && b "giriş: claude · elle kontrol (claude içinde /status); kota harcamamak için otomatik sorgu yok"
  fi

  # global links (only on machines where kur.sh --genel ran)
  if grep -q '^genel=1' "$DURUM/ilk-kurulum.txt" 2>/dev/null; then
    for cift in \
      "$HOME/.claude/settings.json:30-programlar/claude-code/genel/settings.json" \
      "$HOME/.codex/AGENTS.md:00-cekirdek/AGENTS.md" \
      "$HOME/.config/opencode/AGENTS.md:00-cekirdek/AGENTS.md" \
      "$HOME/.config/opencode/opencode.json:30-programlar/opencode/genel/opencode.json"; do
      hedef="${cift%%:*}"; kaynak="$KOK/${cift#*:}"
      case "$hedef" in
        "$HOME/.codex/AGENTS.md") [ ! -f "$KOK/30-programlar/codex/genel/AGENTS.md" ] || kaynak="$KOK/30-programlar/codex/genel/AGENTS.md" ;;
        "$HOME/.config/opencode/AGENTS.md") [ ! -f "$KOK/30-programlar/opencode/genel/AGENTS.md" ] || kaynak="$KOK/30-programlar/opencode/genel/AGENTS.md" ;;
      esac
      [ -e "$kaynak" ] || continue
      if [ -L "$hedef" ] && [ "$(readlink -f "$hedef")" = "$(readlink -f "$kaynak")" ]; then o "bağ: $hedef"
      elif [ -e "$hedef" ]; then h "bağ-kopuk · $hedef · araç dosyayı yeniden yazmış; kur.sh --yeniden-bagla $hedef (önce diff'e bak)"
      else u "bağ-yok · $hedef · kur.sh --genel"; fi
    done
  fi

  # git state
  [ -z "$(git status --porcelain)" ] && o "git: çalışma ağacı temiz" || u "git · $(git status --porcelain | wc -l) değişiklik commit'lenmemiş · /kapat sonrası commit"
  if [ "$CEVRIM" = 1 ]; then
    git fetch -q origin 2>/dev/null || true
    geri=$(git rev-list --count HEAD..@{u} 2>/dev/null || echo 0); ileri=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
    [ "$geri" -gt 0 ] && u "git · uzak $geri commit ileride · git pull"
    [ "$ileri" -gt 0 ] && u "git · $ileri commit push edilmemiş · git push"
  fi
  for p in 40-projeler/aktif/*/; do
    [ -d "$p/.git" ] || continue
    k=$(git -C "$p" status --porcelain | wc -l); [ "$k" -gt 0 ] && u "proje · $p · $k değişiklik commit'lenmemiş"
  done
  [ -d "$DURUM" ] || u "makine · $DURUM yok · /kur (ilk kurulum)"
fi

# ---------------------------------------------------------------- summary
echo "---"
echo "denetim ($KIP): $HATA hata, $UYARI uyarı"
[ "$HATA" -gt 0 ] && exit 2
[ "$UYARI" -gt 0 ] && exit 1
exit 0
