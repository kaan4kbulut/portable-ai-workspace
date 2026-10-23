# 20-sistem — Sistem

İşletim sisteminin **init + servisler** katmanı: atölyeyi bir makineye uyduran, sağlığını denetleyen, onaran her şey.

| Klasör | Görev |
|---|---|
| `kurulum/` | `kur.sh` (idempotent kurulum, araçlar, git ayarı, isteğe bağlı global bağlantılar), `lib/ortak.sh`, `araclar/*.sh` |
| `denetim/` | `denetle.sh` + veri olarak kurallar; `git-hooks/pre-commit` |
| `bakim/` | gömülü bakım ajanı: `BAKIMCI.md`, `bakim.sh`, `guncelle.sh`, `bilinen-sorunlar.md`, `onarimlar/` |
| `yayin/` | açık iskelet reposunu (portable-ai-workspace) kişisel içeriksiz üretir: `yayinla.sh`, `kisisel.txt` |
| `yedek/` | commit/push edilmemiş raporu (Aşama 4 `yedekle.sh`) |
| `ag/` | Tailscale/ağ düzeni (anahtar yok) |
| `servisler/` | systemd `--user` birimleri |
| `durum/` | makineye özgü geçici durum (git dışı) |
| `gunluk/` | betik günlükleri (git dışı) |

Çekirdek ajanda: `/kur` (ilk kurulum), `/baslat` (gün başı), `/kapat` (gün sonu), `/<ad>` (pano).

**Girer:** kurulum, denetim, bakım, ağ, servis. **Girmez:** araç ayarları (→ `30-programlar/`), kurallar (→ `00-cekirdek/`), kararlar (→ `60-hafiza/`).
