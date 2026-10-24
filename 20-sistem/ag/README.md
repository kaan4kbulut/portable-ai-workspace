---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [tailscale.md, ../../10-donanim/monster/README.md, ../../10-donanim/lenovo/README.md, ../../10-donanim/honor/README.md]
---
# 20-sistem/ag — Ağ

Tailscale tailnet düzeni, hangi servisin hangi arayüzden açık olduğu, erişim kuralları. **Anahtar, auth key, şifre asla.**

**Girer:** ağ topolojisi notu, ufw/serve kuralları (metin). **Girmez:** kimlik bilgisi, sunucu kurulum betiği (→ `../cihazlar/`).

## Ne işe yarar?

Cihazların Tailscale adlarını, rollerini ve servis erişim sınırlarını bir arada tutar.
Ağ kaydı [Tailscale](tailscale.md) sayfasındadır; makine ayrıntıları
[MONSTER](../../10-donanim/monster/README.md),
[LENOVO](../../10-donanim/lenovo/README.md) ve
[HONOR](../../10-donanim/honor/README.md) sayfalarındadır.

## Nasıl çalıştırılır / bağlanılır?

Bu klasör belge içerir; çalıştırılacak bir betik yoktur. Yerel kayıtlara göre erişim Tailscale
tailnet üzerinden sağlanır. Düğüm adları [tailscale.md](tailscale.md) dosyasındadır; uzak masaüstü
RDP 3389 ve yerel model sunucusu erişimi yalnızca `tailscale0` üzerinden sınırlandırılmıştır.
`tailscale serve` kullanımı yalnızca tailnet içindir.

Tailscale kurulum/giriş komutu: -. Yerel model sunucusunun bağlantı adresi ve portu: -.
Bu incelemede canlı bağlantı veya güvenlik duvarı doğrulaması yapılmadı.

## Açık eksikler

- Ağ düzeninin sürümü ve resmi kaynak URL'leri: -. `70-kutuphane/` taramasında ilgili belge bulunamadı.
- **Eskimiş:** yukarıdaki `../cihazlar/` yönlendirmesinin hedefi yoktur; makineye özgü
  kurulumlar `../../10-donanim/` altındadır. Eski metin korunmuştur.
- Tailscale kaydında LENOVO yeniden kurulumda görünüyor; güncel düğüm adı ve bağlantı durumu doğrulanmalı.
- Tailscale kaydında eski `monster` Windows ve `1nn-monster` düğümlerinin kaldırılması bekliyor;
  tamamlanma durumu: -.
- Etkin ufw/serve kuralları ve servislerin güncel erişim durumu doğrulanmalı.
