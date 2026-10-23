---
name: bakim
description: Bakımcı ajanı çalıştırır: denetim bulgularını, kopuk yolları, eksik araçları, bu makineye özgü sorunları teşhis eder ve yetki sınırı içinde onarır; her onarımı bilinen-sorunlar.md ve ogrenilenler/'e işler. "bakım", "onar", "bu makinede sorun var", "eksikleri kontrol et" dendiğinde kullan.
argument-hint: [--raporla]
---
# /bakim — gömülü bakım ajanı

1. `bash 10-sistem/denetim/denetle.sh --tam` çıktısını ve `10-sistem/bakim/bilinen-sorunlar.md`'yi topla.
   `$ARGUMENTS` içinde `--raporla` varsa **hiçbir değişiklik yapma**, yalnızca teşhis ve plan.
2. `bakimci` alt ajanını çağır (Agent aracı, `subagent_type: bakimci`). Ona şunları ver: denetim çıktısı, bilinen
   sorunlar, makine adı (`hostname -s`), bu oturumda kullanıcının tarif ettiği belirti, rapor/onarım kipi.
   Ajanın talimatı `10-sistem/bakim/BAKIMCI.md`'dedir; yetki sınırı oradadır (00-cekirdek ve proje koduna dokunmaz,
   sudo/apt gerektirenleri listeler).
3. Ajanın raporunu kullanıcıya özetle: onarılanlar · onarılamayanlar (neden, kullanıcıdan ne gerekiyor) · öğrenilenler
   (bilinen-sorunlar.md / ogrenilenler/ / onarimlar/ / denetim kuralına eklenenler).
4. Onarım sonrası `denetle.sh --tam` tekrar çalıştır, çıkış kodunu bildir.
5. Güncelleme kontrolü istenirse `bash 10-sistem/bakim/guncelle.sh` çıktısını da ekle.
