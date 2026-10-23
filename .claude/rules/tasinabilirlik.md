# Taşınabilirlik kuralları (her dosya için)

- Depo içinde symlink oluşturma (`ln -s` engellidir). Paylaşılan içerik tek yerde durur, gerekirse makine tarafına `kur.sh --genel` bağlar.
- Büyük/küçük harf farkıyla aynı ada sahip iki dosya/klasör oluşturma (exFAT, Windows).
- 50 MB'tan büyük dosya depoya girmez: `90-dis-kaynaklar/` ya da `20-araclar/yerel-modeller/agirliklar/` (ikisi de git dışı).
- Dosya ve klasör adları: küçük harf, aksansız, kebab-case; tarihli öğeler `YYYY-MM-DD-...` (ANAYASA madde 3).
- `~/` ya da `/home/...` ile başlayan yolu depodaki hiçbir dosyaya yazma. Makineye özgü yol gerekiyorsa `10-sistem/durum/<host>/yollar.env`.
- Yeni klasör açınca aynı commit'te `README.md` (ne girer / ne girmez) ekle.
