# Bilinen sorunlar

Bakımcı ajanın ilk baktığı yer. Her yeni sorun bir satır; tekrarlanabilir onarım `onarimlar/<ad>.sh`. En yeni üste.

| tarih | makine | belirti | neden | onarım | betik |
|---|---|---|---|---|---|
| — | — | `git commit` "dubious ownership" (USB/başka uid) | git safe.directory | `kur.sh` ekler | `onarimlar/git-safe-directory.sh` |
| — | — | `./x.sh: Permission denied` | exFAT'ta çalıştırma biti yok | `bash yol/x.sh` ile çağır | — |
| — | — | global ayar symlink'i gerçek dosyaya dönmüş | araç "yaz + yeniden adlandır" yapar | `onarimlar/kopuk-bag.sh` | `onarimlar/kopuk-bag.sh` |
