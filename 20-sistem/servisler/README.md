---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../kurulum/README.md, ../../30-programlar/yerel-modeller/README.md, ../../10-donanim/README.md]
---
# 20-sistem/servisler — systemd kullanıcı birimleri

`<ad>.service` dosyaları; `kur.sh --genel` bunları `~/.config/systemd/user/`'a bağlar, kullanıcı `systemctl --user enable --now <ad>` der.
İlk aday: `llama-server.service` (Aşama 5). Birim dosyalarında mutlak yol yerine `%h` (home) kullan.

**Girer:** user-level birimler. **Girmez:** sistem (root) birimleri (→ `../cihazlar/<makine>/sudo-*.sh`), sır.

## Kısa tanım

systemd kullanıcı birimlerinin depodaki yeridir. İncelenen klasörde yalnızca bu README vardır;
`.service` dosyası henüz yoktur.

## Ne işe yarar?

Kullanıcı hesabı altında çalışacak servis tanımlarını bir arada tutar.
[Kurulum](../kurulum/README.md) betiği `--genel` seçeneğiyle buradaki `.service`
dosyalarını kullanıcı systemd dizinine bağlayacak şekilde yazılmıştır.
[Yerel modeller](../../30-programlar/yerel-modeller/README.md) sayfası,
yukarıda aday olarak anılan `llama-server` için ilgili kayıttır.

## Nasıl çalıştırılır / bağlanılır?

Depo kökünden `bash 20-sistem/kurulum/kur.sh --genel` mevcut `.service` dosyalarını
`~/.config/systemd/user/` altına bağlar; bu seçenek başka global araç ayarlarını da bağlar.
README'deki etkinleştirme komutu `systemctl --user enable --now <ad>` biçimindedir;
`<ad>` mevcut birimin adıyla değiştirilir. Şu anda klasörde birim bulunmadığı için
buradan etkinleştirilecek servis yoktur. Bu incelemede kurulum veya servis komutu çalıştırılmadı.

Bağlantı adresi ve portu: -.

## Açık eksikler

- Servis sürümü ve resmi kaynak URL'leri: -. `70-kutuphane/` taramasında ilgili bilgi bulunamadı.
- `llama-server.service` aday olarak kayıtlıdır; birim dosyası ve çalıştırma parametreleri yoktur.
  “Aşama 5” ifadesinin güncel planla uyumu: -.
- **Eskimiş:** yukarıdaki `../cihazlar/<makine>/sudo-*.sh` yolu mevcut yerleşime uymaz;
  makineye özgü kurulumların yeri [10-donanim](../../10-donanim/README.md) katmanıdır.
  Eski metin korunmuştur.
- Canlı systemd durumu ve servis erişimi doğrulanmadı.
