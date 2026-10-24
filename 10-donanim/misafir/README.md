---
katman: donanim
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../README.md, ./profil.md, ../../20-sistem/kurulum/kur.sh, ../../20-sistem/kurulum/lib/ortak.sh]
---

# Misafir

## Kısa tanım ve kullanım amacı

Kayıtlı cihaz profilleriyle hostname eşleşmesi bulunamayan makinelerin varsayılan profilidir. USB ile geçici kullanılan bir bilgisayar, arkadaşın bilgisayarı veya geçici VM bu kapsama girebilir; belirli bir fiziksel cihazı tanımlamaz.

- Hostname: - (kayıtlı profille eşleşme yok).
- Donanım, işletim sistemi ve sürümü: -
- Amaç: tanınmayan makinede atölyenin taşınabilir kurulum akışını kullanmak.

## Nasıl çalıştırılır / bağlanılır

Depo kökünden kurulum planını görmek için:

```bash
bash 20-sistem/kurulum/kur.sh --kuru
```

Kurulumu uygulamak için aynı komut `--kuru` olmadan çalıştırılır. [Makine algılama yordamı](../../20-sistem/kurulum/lib/ortak.sh), kısa hostname değerini `10-donanim/*/profil.md` dosyalarındaki `hostname:` satırıyla karşılaştırır; eşleşme bulamazsa `misafir` döndürür.

Bu klasörde `paketler.txt` bulunmadığından [kurulum betiği](../../20-sistem/kurulum/kur.sh) sistem paketi adımını atlar. Çevrimiçi olduğunda araç kurucularını çağırır; Docker kurucusu kurulum yapmadan sudo gerektiren adımları bildirir. CLI girişleri her makinede aracın kendi giriş akışıyla ayrı yapılır.

Uzak bağlantı adresi ve yöntemi: -

## Açık eksikler ve sınırlar

- [Profildeki](./profil.md) “yalnızca kullanıcı-yerel kurucular” ifadesi tam bir yalıtım garantisi olarak **eskimiş** kabul edilmelidir: betikte misafire özel genel bir engel yoktur; kurulum genel Git ayarlarını değiştirir ve `--genel` verilirse kullanıcı düzeyindeki araç ayarlarını bağlar. Bu sayfa betik incelemesine dayanır; misafir makinede kurulum testi yapılmadı.
- Kalıcı makineye geçiş için ayrı `10-donanim/<ad>/profil.md` ve gerçek `hostname:` kaydı gerekir; mevcut misafir profili belirli bir cihaza dönüştürülmez.
- `70-kutuphane/` taramasında misafire özel bilgi belgesi veya resmi kaynak URL'si bulunmadı; `kaynaklar` bu nedenle boştur.
- Bu klasörde yalnız profil ve varlık sayfası bulunur; geçici makine ölçümleri kurulum tarafından `20-sistem/durum/<hostname>/` altında tutulur.
