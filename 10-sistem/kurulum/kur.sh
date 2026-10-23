#!/usr/bin/env bash
# Idempotent machine setup for the atölye. Usage: bash 10-sistem/kurulum/kur.sh [--kuru] [--genel] [--yeniden-bagla <hedef>]
#   --kuru          show what would be done, change nothing
#   --genel         also link global CLI config (~/.claude, ~/.codex, ~/.config/opencode, ~/.gemini) to the repo
#   --yeniden-bagla re-link one global target that a tool overwrote (see denetle.sh --tam)
# Never logs in to any service and never reads credential files.
set -euo pipefail

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib/ortak.sh
source "$DIR/lib/ortak.sh"
KOK=$(atolye_koku "$DIR") || { echo "atölye kökü bulunamadı (00-cekirdek/ANAYASA.md yok)"; exit 2; }

KURU=0; GENEL=0; YENIDEN=""
while [ $# -gt 0 ]; do
  case "$1" in
    --kuru) KURU=1 ;;
    --genel) GENEL=1 ;;
    --yeniden-bagla) YENIDEN="$2"; shift ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) hata "bilinmeyen seçenek: $1"; exit 2 ;;
  esac
  shift
done

calistir() { if [ "$KURU" = 1 ]; then log "  [kuru] $*"; else "$@"; fi; }

HOST=$(hostname_kisa)
MAKINE=$(makine_adi "$KOK")
FS=$(fs_turu "$KOK")
DURUM="$KOK/10-sistem/durum/$HOST"
GUNLUK="$KOK/10-sistem/gunluk"
ZAMAN=$(date +%Y-%m-%d-%H%M)

adim "Atölye kurulumu · makine: $MAKINE ($HOST) · fs: $FS · kök: $KOK"
[ "$KURU" = 1 ] && uyar "kuru çalışma: hiçbir şey değişmeyecek"

# ---------------------------------------------------------------- 1. durum/
adim "1/8 Makine durumu dizini"
calistir mkdir -p "$DURUM" "$GUNLUK"
if [ "$KURU" = 0 ]; then
  {
    echo "# Otomatik makine profili ($HOST)"
    echo "- tarih: $ZAMAN"
    echo "- makine: $MAKINE"
    echo "- os: $(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || uname -s)"
    echo "- arch: $(uname -m)"
    echo "- fs: $FS"
    for a in claude codex opencode agy gh git node uv python3 docker; do
      echo "- $a: $(surum_al "$a")"
    done
  } > "$DURUM/profil-otomatik.md"
  {
    for a in claude codex opencode agy gh node uv; do
      komut_var "$a" && echo "$(echo "$a" | tr a-z A-Z)_YOLU=$(command -v "$a")"
    done
  } > "$DURUM/yollar.env"
  ok "profil-otomatik.md ve yollar.env yazıldı"
fi

# ---------------------------------------------------------------- 2. apt
adim "2/8 Sistem paketleri"
PAKETLER="$KOK/10-sistem/cihazlar/$MAKINE/paketler.txt"
if komut_var apt-get && [ -f "$PAKETLER" ] && sudo -n true 2>/dev/null; then
  eksik=$(grep -vE '^\s*(#|$)' "$PAKETLER" | while read -r p; do dpkg -s "$p" >/dev/null 2>&1 || echo "$p"; done | tr '\n' ' ')
  if [ -n "${eksik// }" ]; then
    log "  eksik: $eksik"
    calistir sudo apt-get install -y -q $eksik
  else ok "paketler tam"; fi
else
  uyar "apt/sudo yok ya da paketler.txt yok; sistem paketleri atlandı (elle: $PAKETLER)"
fi

# ---------------------------------------------------------------- 3. araçlar
adim "3/8 Araçlar (eksikse kurulur, giriş yapılmaz)"
if cevrimici_mi "$KOK" || timeout 4 curl -fsI https://github.com >/dev/null 2>&1; then
  for s in node uv gh claude codex opencode agy docker; do
    [ -f "$DIR/araclar/$s.sh" ] || continue
    if [ "$KURU" = 1 ]; then log "  [kuru] bash araclar/$s.sh"; else bash "$DIR/araclar/$s.sh" || uyar "$s kurulamadı (bkz. yukarı)"; fi
  done
else
  uyar "çevrimdışı: araç kurulumu atlandı. Eksikler: $(for a in node uv gh claude codex opencode agy; do komut_var "$a" || printf '%s ' "$a"; done)"
fi

# ---------------------------------------------------------------- 4. git
adim "4/8 Git kimliği ve depo ayarları"
if [ -z "$(git config --global user.name || true)" ]; then
  if [ "$KURU" = 1 ] || [ ! -t 0 ]; then uyar "git user.name boş; etkileşimli çalıştır ya da: git config --global user.name 'Ad'"; else
    read -rp "git user.name: " GN; git config --global user.name "$GN"
    read -rp "git user.email: " GE; git config --global user.email "$GE"
  fi
fi
calistir git config --global init.defaultBranch main
calistir git config --global pull.rebase false
if ! git config --global --get-all safe.directory 2>/dev/null | grep -qx "$KOK"; then
  calistir git config --global --add safe.directory "$KOK"
fi
if fs_kisitli "$KOK"; then
  uyar "kısıtlı dosya sistemi ($FS): filemode/symlinks kapatılıyor, ignorecase açılıyor"
  calistir git -C "$KOK" config core.filemode false
  calistir git -C "$KOK" config core.symlinks false
  calistir git -C "$KOK" config core.ignorecase true
fi
calistir git -C "$KOK" config core.hooksPath 10-sistem/denetim/git-hooks
ok "core.hooksPath = 10-sistem/denetim/git-hooks"

# ---------------------------------------------------------------- 5. dizinler
adim "5/8 Git dışı çalışma dizinleri"
for d in 30-projeler/aktif 30-projeler/deneme 90-dis-kaynaklar 20-araclar/yerel-modeller/agirliklar 10-sistem/gunluk; do
  calistir mkdir -p "$KOK/$d"
done
ok "dizinler hazır"

# ---------------------------------------------------------------- 6. genel bağlantılar
adim "6/8 Global CLI bağlantıları"
if [ "$GENEL" = 1 ] || [ -n "$YENIDEN" ]; then
  bagla() {  # bagla <kaynak-goreli> <hedef> [--kopya]
    local k="$KOK/$1" h="$2" kip="${3:-}"
    [ -n "$YENIDEN" ] && [ "$h" != "$YENIDEN" ] && return 0
    if [ "$KURU" = 1 ]; then log "  [kuru] $h -> $1 $kip"; else yedekle_ve_bagla "$k" "$h" $kip; fi
  }
  # Claude: CLAUDE.md must be a real file with the absolute import path filled in
  if [ -f "$KOK/20-araclar/claude-code/genel/CLAUDE.md.sablon" ]; then
    tmp=$(mktemp); sed "s#__ATOLYE__#$KOK#g" "$KOK/20-araclar/claude-code/genel/CLAUDE.md.sablon" > "$tmp"
    if [ "$KURU" = 1 ]; then log "  [kuru] ~/.claude/CLAUDE.md (kopya, yol dolduruldu)"; else yedekle_ve_bagla "$tmp" "$HOME/.claude/CLAUDE.md" --kopya; fi
    rm -f "$tmp"
  fi
  bagla 20-araclar/claude-code/genel/settings.json "$HOME/.claude/settings.json"
  for s in "$KOK"/.claude/skills/*/; do
    [ -d "$s" ] || continue; n=$(basename "$s")
    bagla ".claude/skills/$n" "$HOME/.claude/skills/$n"
    bagla ".claude/skills/$n" "$HOME/.codex/skills/$n"
  done
  bagla 00-cekirdek/AGENTS.md "$HOME/.codex/AGENTS.md"
  if [ -f "$KOK/20-araclar/codex/genel/config.toml" ]; then
    if grep -qiE '(api_key|token|secret)\s*=' "$KOK/20-araclar/codex/genel/config.toml"; then
      hata "codex config.toml sır içeriyor, bağlanmadı"
    else bagla 20-araclar/codex/genel/config.toml "$HOME/.codex/config.toml"; fi
  fi
  bagla 00-cekirdek/AGENTS.md "$HOME/.config/opencode/AGENTS.md"
  bagla 20-araclar/opencode/genel/opencode.json "$HOME/.config/opencode/opencode.json"
  bagla 20-araclar/agy/genel/mcp_config.json "$HOME/.gemini/config/mcp_config.json"
  for u in "$KOK"/10-sistem/servisler/*.service; do
    [ -f "$u" ] || continue; bagla "10-sistem/servisler/$(basename "$u")" "$HOME/.config/systemd/user/$(basename "$u")"
  done
  [ "$KURU" = 0 ] && [ -z "$YENIDEN" ] && echo "genel=1" >> "$DURUM/ilk-kurulum.txt"
else
  log "  atlandı (--genel verilmedi). Proje kapsamı (.claude/) zaten yeterli; klasör dışında da aynı kurallar istenirse: kur.sh --genel"
fi

# ---------------------------------------------------------------- 7. ilk kurulum kaydı
adim "7/8 Kurulum kaydı"
if [ "$KURU" = 0 ]; then
  grep -q '^tarih=' "$DURUM/ilk-kurulum.txt" 2>/dev/null || {
    echo "tarih=$ZAMAN"; echo "makine=$MAKINE"; echo "surum=$(grep -m1 -oE '^## [0-9]+\.[0-9]+\.[0-9]+' "$KOK/SURUM.md" | cut -c4-)"
  } >> "$DURUM/ilk-kurulum.txt"
  ok "$DURUM/ilk-kurulum.txt"
fi

# ---------------------------------------------------------------- 8. denetim
adim "8/8 Denetim"
if [ "$KURU" = 0 ]; then
  bash "$KOK/10-sistem/denetim/denetle.sh" --tam | tee "$GUNLUK/kur-$ZAMAN.log" || true
  log ""; log "günlük: $GUNLUK/kur-$ZAMAN.log"
fi
log ""; ok "kurulum bitti. Sonraki: her CLI'a bu makinede kendi girişinle gir (claude → /login, codex login, opencode auth login, agy)."
