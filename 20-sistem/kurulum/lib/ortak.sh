#!/usr/bin/env bash
# Shared helpers for atölye scripts. Source it: source "$DIR/lib/ortak.sh"  (never execute directly)
# Provides: log/uyar/hata, komut_var, atolye_koku, makine_adi, fs_turu, cevrimici_mi, yedekle_ve_bagla, surum_al

# ---- output ----------------------------------------------------------------
log()  { printf '%s\n' "$*"; }
ok()   { printf '[OK] %s\n' "$*"; }
uyar() { printf '[UYARI] %s\n' "$*"; }
hata() { printf '[HATA] %s\n' "$*" >&2; }
adim() { printf '\n==> %s\n' "$*"; }

komut_var() { command -v "$1" >/dev/null 2>&1; }

# ---- location --------------------------------------------------------------
# Root = the directory that contains 00-cekirdek/ANAYASA.md, found by walking up from the caller's dir.
atolye_koku() {
  local d="${1:-$PWD}"
  while [ "$d" != "/" ]; do
    [ -f "$d/00-cekirdek/ANAYASA.md" ] && { printf '%s\n' "$d"; return 0; }
    d=$(dirname "$d")
  done
  return 1
}

# ---- machine ---------------------------------------------------------------
# Short machine name: the 10-donanim/<x>/profil.md whose "hostname:" line matches, else "misafir".
makine_adi() {
  local kok="$1" host
  host=$(hostname -s 2>/dev/null || hostname)
  local p
  for p in "$kok"/10-donanim/*/profil.md; do
    [ -f "$p" ] || continue
    if grep -qiE "^hostname:\s*${host}\s*$" "$p"; then
      basename "$(dirname "$p")"; return 0
    fi
  done
  printf 'misafir\n'
}

hostname_kisa() { hostname -s 2>/dev/null || hostname; }

# Filesystem type of a path (ext4, exfat, vfat, ntfs, fuseblk, ...).
fs_turu() { stat -f -c %T "$1" 2>/dev/null || printf 'bilinmiyor\n'; }

# True when the fs cannot hold symlinks / exec bits.
fs_kisitli() {
  case "$(fs_turu "$1")" in
    exfat|msdos|vfat|fuseblk|ntfs|fat*) return 0 ;;
    *) return 1 ;;
  esac
}

# ---- network ---------------------------------------------------------------
cevrimici_mi() {
  local kok="$1"
  ( cd "$kok" && timeout 4 git ls-remote --exit-code origin HEAD >/dev/null 2>&1 )
}

# ---- versions --------------------------------------------------------------
surum_al() {  # surum_al <komut> -> first line of --version or "yok"
  if komut_var "$1"; then "$1" --version 2>/dev/null | head -1 || printf 'bilinmiyor\n'; else printf 'yok\n'; fi
}

# ---- symlink helper (machine side only; never inside the repo) --------------
# yedekle_ve_bagla <kaynak> <hedef> [--kopya]
#   - target already links to source: skip
#   - target is a real file/dir: move aside as <hedef>.yedek-YYYYMMDD-HHMMSS, then link
#   - --kopya: copy instead of link (for files that must be real, e.g. ~/.claude/CLAUDE.md)
yedekle_ve_bagla() {
  local kaynak="$1" hedef="$2" kip="${3:-}"
  [ -e "$kaynak" ] || { uyar "kaynak yok, atlandı: $kaynak"; return 0; }
  mkdir -p "$(dirname "$hedef")"
  if [ -L "$hedef" ] && [ "$(readlink -f "$hedef")" = "$(readlink -f "$kaynak")" ] && [ "$kip" != "--kopya" ]; then
    ok "zaten bağlı: $hedef"; return 0
  fi
  if [ -e "$hedef" ] || [ -L "$hedef" ]; then
    if [ "$kip" = "--kopya" ] && [ -f "$hedef" ] && cmp -s "$kaynak" "$hedef"; then
      ok "zaten aynı: $hedef"; return 0
    fi
    local yedek="$hedef.yedek-$(date +%Y%m%d-%H%M%S)"
    mv "$hedef" "$yedek"
    uyar "mevcut dosya yedeklendi: $yedek"
  fi
  if [ "$kip" = "--kopya" ]; then
    cp "$kaynak" "$hedef"; ok "kopyalandı: $hedef"
  else
    ln -s "$kaynak" "$hedef"; ok "bağlandı: $hedef -> $kaynak"
  fi
}
