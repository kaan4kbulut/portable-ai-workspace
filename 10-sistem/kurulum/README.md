# 10-sistem/kurulum — Kurulum

| Dosya | Görev |
|---|---|
| `kur.sh [--kuru] [--genel] [--yeniden-bagla h]` | İdempotent: makine durumu, apt (sudo varsa), eksik araçlar (kullanıcı-yerel), git kimliği/ayarı, `core.hooksPath`, git dışı dizinler, isteğe bağlı global bağlantılar, denetim |
| `lib/ortak.sh` | Tüm betiklerin ortak yardımcıları (`atolye_koku`, `makine_adi`, `fs_turu`, `cevrimici_mi`, `yedekle_ve_bagla`) |
| `araclar/<ad>.sh` | Araç başına kurucu; `komut_var || kur`; **giriş yapmaz** |

`--genel`: proje kapsamı dışında da aynı kurallar istenirse `~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.gemini`
içine bağlantı kurar (mevcut dosya `.yedek-<zaman>` olarak saklanır). USB/başka makine için gerekmez.
Kısıtlı dosya sisteminde (exFAT/NTFS) `core.filemode=false`, `core.symlinks=false`, `core.ignorecase=true` ayarlanır.

**Girer:** kurulum betikleri. **Girmez:** denetim (→ `../denetim/`), makine profilleri (→ `../cihazlar/`).
