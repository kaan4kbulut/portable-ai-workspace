---
name: {{ad}}
description: "{{ad}} ana menüsü: makine, kimlik, sürüm, git, araçlar, aktif proje, gelen kutusu, son devir notu ve denetim panosunu basar; tüm komutları katmanlara göre listeler ve ne yapılacağını sorar. Argümansız `/{{ad}}`, 'menü', 'ne yapabilirim', 'durum göster' dendiğinde kullan."
---
# /{{ad}} — ana menü

Bu dosya `00-cekirdek/sablonlar/beceri/ana-menu.md` şablonundan `/kur` ile üretilir; üretilen kopyayı değil şablonu düzenle.
Salt okunur: pano sırasında hiçbir dosya değişmez.

## 1. Pano (en fazla 12 satır)
Verileri paralel topla, boş olanı "—" yaz:
1. **Makine / kimlik:** `hostname -s`; `10-donanim/<makine>/` sayfasından makine adı; `00-cekirdek/kimlik.json` içinden `ad`.
2. **Sürüm:** `SURUM.md` ilk `## X.Y.Z` başlığı.
3. **Git:** dal, kısa HEAD, değişiklik sayısı, push edilmemiş commit sayısı (`git rev-list --count @{u}..HEAD`).
4. **Araçlar:** `claude`, `codex`, `opencode`, `agy`, `gh` sürümü + giriş durumu (yalnızca aracın kendi komutu:
   `gh auth status`, `codex login status`, `opencode auth list`; claude için kullanıcıya `/status` denetletilir;
   agy için sürüm yeterli). Kimlik dosyası okunmaz.
5. **Aktif proje:** `20-sistem/durum/<host>/aktif-proje.txt`, yoksa `40-projeler/DIZIN.md` ilk "aktif" satırı.
6. **Gelen kutusu:** `90-gelen-kutusu/` öğe sayısı (README.md ve AYIKLAMA.md hariç), 30 günü geçen var mı.
7. **Son devir notu:** `60-hafiza/oturumlar/` en yeni dosya + "Sonraki" bölümünün ilk maddesi.
8. **Denetim:** `bash 20-sistem/denetim/denetle.sh --hizli | tail -1`.

## 2. Menü
Komutları katmana göre grupla (tam katalog: `50-arayuz/komutlar.md`):

| Katman | Komutlar |
|---|---|
| Çekirdek | `/{{ad}}` menü · `/kur` ilk kurulum · `/karar` karar kaydı |
| Donanım | `/donanim` makine bilgisi |
| Sistem | `/baslat` gün başı · `/kapat` gün sonu · `/denetle` düzen denetimi · `/bakim` onarım |
| Programlar | `/araclar` CLI'lar ve görev çalıştırma · `/programlar` kurulu program/servis envanteri |
| Projeler | `/projeler` proje listesi ve klonlama · `/yayinla` açık iskelet sürümü |
| Hafıza / gelen | `/ayikla` gelen kutusu ayıklama |
| Kütüphane | `/kutuphane <konu>` araştırma · `/kutuphane tara` bayat sayfa, sürüm ve harita taraması |

## 3. Sor
"Ne yapalım?" diye tek soru sor; pano denetimde hata ya da gelen kutusunda 30 günü geçen öğe gösteriyorsa
önce onu öner. Kullanıcı seçene kadar değişiklik yapma.
