---
name: denetle
description: Atölye düzen denetimini (10-sistem/denetim/denetle.sh) çalıştırır, bulguları açıklar, düzeltme planı çıkarır. "denetle", "düzen kontrolü", "her şey yolunda mı" dendiğinde kullan.
argument-hint: [--hizli | --commit | --tam]
---
# /denetle — düzen denetimi

1. `bash 10-sistem/denetim/denetle.sh ${ARGUMENTS:---tam}` çalıştır (çevrimdışıysa giriş/uzak denetimleri "atlandı" çıkar; normaldir).
2. Çıktıyı grupla: HATA (engelleyici), UYARI, atlanan. Her bulgu için hangi ANAYASA maddesini ihlal ettiğini ve
   `10-sistem/denetim/kurallar/` içindeki hangi kural dosyasından geldiğini söyle.
3. Daha önce görülmüş mü: `10-sistem/bakim/bilinen-sorunlar.md`'de ara. Varsa oradaki onarımı öner.
4. Düzeltme planı: her bulgu için tek komut ya da tek düzenleme. Yıkıcı adım (silme, taşıma) için onay iste.
5. Onaylananları uygula ya da kullanıcı isterse `/bakim` ile bakımcı ajanına devret.
6. Sonunda denetimi yeniden çalıştır ve çıkış kodunu bildir (0 temiz, 1 uyarı, 2 hata).
