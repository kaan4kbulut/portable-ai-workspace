# 10-sistem/servisler — systemd kullanıcı birimleri

`<ad>.service` dosyaları; `kur.sh --genel` bunları `~/.config/systemd/user/`'a bağlar, kullanıcı `systemctl --user enable --now <ad>` der.
İlk aday: `llama-server.service` (Aşama 5). Birim dosyalarında mutlak yol yerine `%h` (home) kullan.

**Girer:** user-level birimler. **Girmez:** sistem (root) birimleri (→ `../cihazlar/<makine>/sudo-*.sh`), sır.
