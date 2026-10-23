---
name: kapat
description: Oturum sonu devir notu yazar (40-hafiza/oturumlar/), DURUM.md ve DIZIN.md'yi günceller, commit önerir. Oturumu bitirmeden önce, "kapat", "devir notu", "bugünü kaydet" dendiğinde kullan.
---
# /kapat — oturum devir notu

Amaç: bu oturumda yapılanı başka bir makinede, başka bir CLI'da, bir hafta sonra devam edilebilecek biçimde kaydetmek.
Atölyede Claude otomatik hafızası kapalıdır; **bu not tek süreklilik kaynağıdır.**

## Adımlar
1. Makine adını ve zamanı al: `hostname -s`, `date +%Y-%m-%d-%H%M`. Makine kısa adı: `10-sistem/cihazlar/<x>/profil.md`
   içindeki `hostname:` satırıyla eşleşiyorsa `<x>`, yoksa hostname'in kendisi.
2. Ham maddeyi topla: `git status --short`, `git diff --stat`, varsa `10-sistem/durum/<host>/son-oturum.json`
   (`degisen_dosyalar`), bu oturumda konuşulanlar.
3. `80-sablonlar/belge/oturum-notu.md` şablonunu kullanarak
   `40-hafiza/oturumlar/YYYY/YYYY-MM-DD-HHMM-<makine>-<konu>.md` dosyasını yaz (`<konu>` 1-3 kelime, kebab-case).
   Bölümler sabit ve hepsi dolu: **Yapılan / Sonraki / Açık sorular / Dokunulan dosyalar / Karar gereken / Makine**.
   "Sonraki" somut olsun: bir sonraki oturumun ilk 3 adımı.
4. Dokunulan projeler için `30-projeler/aktif/<ad>/DURUM.md` "Durum" ve "Sonraki" bölümlerini güncelle;
   `30-projeler/DIZIN.md` "son dokunma" sütununu bugünle değiştir.
5. Bu oturumda karar alındıysa ve KARARLAR.md'ye yazılmadıysa `/karar` akışını uygula.
6. `bash 10-sistem/denetim/denetle.sh --hizli` çalıştır; hata varsa notun "Açık sorular"ına ekle.
7. Commit **önerisi** sun (mesaj taslağıyla); kullanıcı istemeden commit/push yapma.

## Çıktı
Kullanıcıya 5 satır: not dosyasının yolu, "Sonraki" maddeleri, karar gerekenler, denetim özeti, commit önerisi.
