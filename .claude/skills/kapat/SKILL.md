---
name: kapat
description: >-
  Günü kapatır - hızlı denetim, devir notu (60-hafiza/oturumlar/), DURUM.md ve DIZIN.md güncelleme, commit ve push önerisi.
  "kapat", "devir notu", "bugünü kaydet", "günü bitir" dendiğinde kullan.
---
# /kapat — gün sonu ve devir notu

Amaç: bu oturumu başka makinede, başka CLI'da, bir hafta sonra devam edilebilir biçimde kaydetmek. Atölyede bu not tek süreklilik kaynağıdır.

1. Makine ve zaman: `hostname -s`, `date +%Y-%m-%d-%H%M`; makine kısa adı `10-donanim/<x>/` sayfasındaki `hostname:` ile eşleşen `<x>`, yoksa hostname.
2. `mkdir -p 20-sistem/gunluk 20-sistem/durum/<host>`. `bash 20-sistem/denetim/denetle.sh --hizli` komutunu boru kullanmadan çalıştır:
   tam çıktıyı ve çıkış kodunu koru (2 = hata), özet satırını `20-sistem/gunluk/kapat-YYYY-MM-DD.log` dosyasına ekle
   (devir notu yolu, güncelleme uyarısı, commit/push sonucu da aynı loga eklenir). Hata varsa notun "Açık sorular"ına yaz.
3. Ham madde: `git status --short`, `git diff --stat`, varsa `20-sistem/durum/<host>/son-oturum.json` (`degisen_dosyalar`),
   bu oturumda konuşulanlar. Bugün aynı makinede not zaten varsa yenisini açma, onu güncelle.
4. `00-cekirdek/sablonlar/belge/oturum-notu.md` şablonuyla `60-hafiza/oturumlar/YYYY/YYYY-MM-DD-HHMM-<makine>-<konu>.md` yaz
   (`<konu>` 1-3 kelime kebab-case). Bölümler sabit ve dolu: **Yapılan / Sonraki / Açık sorular / Dokunulan dosyalar / Karar gereken / Makine**.
   "Sonraki" somut: bir sonraki oturumun ilk 3 adımı.
5. Dokunulan projeler için `40-projeler/aktif/<ad>/DURUM.md` "Durum" ve "Sonraki" bölümlerini, `40-projeler/DIZIN.md` "son dokunma" sütununu güncelle.
6. Alınıp KARARLAR'a yazılmamış karar varsa `/karar` akışını uygula.
7. `20-sistem/durum/<host>/guncelleme-raporu.md` içinde "GÜNCELLE" geçiyorsa tek satır uyar.
8. Commit edilmemiş değişiklikleri özetle: atölye (`git status --short`) ve `40-projeler/aktif/*/` altındaki her repo (değişiklik, push edilmemiş commit).
9. **Sor:** atölye commit edilsin mi? Evetse mesaj taslağı sun (`type(scope): özet`), onayla, `git add -A` ve commit.
   Sonra çevrimiçi ve push edilmemiş commit varsa **ayrıca sor**: push edilsin mi? Kullanıcı demeden asla commit/push yapma.
10. Çıktı 5 satır: not yolu, "Sonraki" maddeleri, karar gerekenler, denetim özeti, commit/push durumu.
