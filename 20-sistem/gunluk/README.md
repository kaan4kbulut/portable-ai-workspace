---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../kurulum/README.md, ../denetim/README.md, ../bakim/README.md, ../durum/README.md, ../../60-hafiza/oturumlar/README.md]
---
# 20-sistem/gunluk — Betik günlükleri (git dışı)

`kur-<zaman>.log`, `bakim-<zaman>.md`, `kapat-<tarih>.log`. 30 günden eskisi silinebilir (bakımcı önerir).
**Girmez:** oturum devir notları (→ `60-hafiza/oturumlar/`), kimlik bilgisi.

## Kısa tanım

Kurulum, bakım ve oturum kapatma işlemlerinin yerel çıktılarını tutan günlük klasörüdür.
İçeriği git dışıdır; yalnızca bu README Git'te izlenir.

## Ne işe yarar?

- [Kurulum](../kurulum/README.md) sonunda çalışan [denetimin](../denetim/README.md)
  standart çıktısını `kur-YYYY-MM-DD-HHMM.log` dosyasında saklar; kurulumun tüm çıktısının kaydı değildir.
- [Bakım](../bakim/README.md) raporları `bakim-YYYY-MM-DD-HHMM.md` biçiminde tutulur.
- `/kapat` akışı özet satırlarını `kapat-YYYY-MM-DD.log` dosyasına ekler.

[Makineye özgü geçici durum](../durum/README.md) ve
[oturum devir notları](../../60-hafiza/oturumlar/README.md) ayrı yerlerde tutulur.

## Nasıl çalıştırılır / bağlanılır?

Klasör bağımsız bir program veya bağlantı hizmeti değildir. Mevcut kayıtları depo kökünden
`ls 20-sistem/gunluk` ile listeleyip ilgili dosyayı bir metin okuyucuyla açabilirsiniz.
Kayıtlar ilgili kurulum, bakım veya `/kapat` akışı tarafından üretilir.

30 günden eski kayıtlar için yukarıdaki bakımcı önerisi geçerlidir; silme işlemi kullanıcı
onayı gerektirir, yaş sınırı tek başına silme izni değildir.

## Açık eksikler

- Bağımsız sürüm ve resmi kaynak URL'leri: -.
- `70-kutuphane/` içinde bu klasörle ilgili ek belge bulunamadı.
- İnceleme sırasında klasörde yalnızca README vardı; gerçek günlük üretimi ve saklama süreci çalıştırılarak sınanmadı.
