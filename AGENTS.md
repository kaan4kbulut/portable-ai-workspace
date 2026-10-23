@00-cekirdek/AGENTS.md

# Atölye: ajan sınırları

Önce `00-cekirdek/AGENTS.md` dosyasını oku ve uygula.
Codex, opencode ve agy `@` içe aktarmasını genişletmez; dosyayı açıkça oku.
Harita `README.md`, düzen kuralları `00-cekirdek/ANAYASA.md` içindedir.
ANAYASA yalnızca insan tarafından düzenlenir.

## Bu kök çekirdek ajanın alanıdır

Codex, opencode, agy veya çekirdek ajan olarak çalışmayan sıradan bir Claude
oturumuysan kökte ve `00-cekirdek/`, `10-donanim/`, `20-sistem/`, `60-hafiza/`
içinde dosya oluşturma, düzenleme veya taşıma.
Çalışmanı `40-projeler/<ad>/` içindeki kendi reposunda veya çağrıldığın çalışma
klasöründe yap; çağrılma konumu yukarıdaki kök/çekirdek yasağını kaldırmaz.
Salt okunur sorular, incelemeler ve dosya okumaları serbesttir.

## Depo disiplini

- Kararları ve oturum devirlerini ortak kurallardaki hafıza akışına kaydet.
- Yeni dosyalar için Aşama B yerleşimini kullan: araç ayarları
  `30-programlar/<arac>/genel/`, belirsiz içerik `90-gelen-kutusu/`.
- Depo içinde symlink oluşturma; betikleri `bash yol/betik.sh` ile çağır.
- Yolları depo konumundan göreli çöz; kaldırılanları gerekçesiyle arşive taşı.
- Yeni araç açmadan önce mevcut kayıtları ve arşivi ara.
- Kimlik dosyalarını okuma; giriş durumunu yalnız aracın kendi komutuyla sor.
- Kullanıcı istemeden commit veya push yapma.
