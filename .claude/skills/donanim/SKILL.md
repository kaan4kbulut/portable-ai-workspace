---
name: donanim
description: Bu makinenin donanım bilgisini 10-donanim/<makine>/ sayfaları ve canlı sistem verisiyle (işletim sistemi, CPU, RAM, disk, GPU, tailscale) gösterir. "donanım", "makine bilgisi", "ne kadar RAM/disk var", "GPU var mı" dendiğinde kullan.
---
# /donanim — makine bilgisi

Salt okunur.
1. Makineyi bul: `hostname -s`; `10-donanim/` altında `hostname:` satırı eşleşen klasör. Yoksa "bu makinenin sayfası yok" de, sayfa taslağı öner.
2. Sayfa: `10-donanim/<makine>/` belgelerinden kayıtlı özellikleri (rol, kapasite, notlar) özetle.
3. Canlı veri:
   - `hostnamectl` (işletim sistemi, çekirdek, mimari)
   - `lscpu` içinden Model name, CPU(s), Thread(s) per core
   - `free -h` (RAM, takas)
   - `df -h .` (deponun bulunduğu disk, doluluk)
   - GPU: `command -v nvidia-smi` varsa `nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv`; yoksa "GPU yok / sürücü yok"
   - `tailscale status`: yalnızca düğüm adları ve çevrimiçi/değil; tailscale yoksa söyle
4. Sapma: sayfadaki kayıtlı değerle canlı değer farklıysa (RAM, GPU, disk) belirt, sayfa güncellemesi öner; onaysız yazma.
5. Çıktı: kısa tablo (alan · kayıtlı · canlı).
