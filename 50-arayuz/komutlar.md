# Komut kataloğu

Hepsi Claude Code içinde slash komutu. `<ad>` = `00-cekirdek/kimlik.json` adı.

| komut | katman | ne yapar | yerine geçtiği |
|---|---|---|---|
| `/<ad>` | çekirdek | Pano (makine, sürüm, git, araçlar, proje, gelen kutusu, denetim) ve komut menüsü | `basla.sh --sadece-pano` |
| `/kur` | çekirdek | İlk kurulum: ad onayı, `kimlik.json`, ana menü becerisi, çekirdek ajan, `kur.sh` | `basla.sh` ilk açılış dalı |
| `/karar` | çekirdek | Kararı `60-hafiza/kararlar/KARARLAR.md`'ye kaydeder | (aynı; yol güncellemesi Aşama B'de) |
| `/donanim` | donanım | `10-donanim/<makine>/` sayfası ve canlı CPU, RAM, disk, GPU, tailscale | yeni |
| `/baslat` | sistem | Git güvenliği, güvenli pull, tam denetim, pano, "nerede kalmıştık" | `basla.sh` + eski `/baslat` |
| `/kapat` | sistem | Devir notu, DURUM/DIZIN güncelleme, commit ve push önerisi (onaylı) | `kapat.sh` + eski `/kapat` |
| `/denetle` | sistem | Düzen denetimi, bulgu açıklama, düzeltme planı | (aynı; yol güncellemesi Aşama B'de) |
| `/bakim` | sistem | Bakımcı ajanla teşhis ve onarım | (aynı; yol güncellemesi Aşama B'de) |
| `/araclar` | programlar | CLI envanteri (sürüm, giriş, rol, kota); `/araclar <arac> <görev>` etkileşimsiz çalıştırır | yeni |
| `/programlar` | programlar | Kurulu program/servis envanteri, eksik `30-programlar` sayfaları | yeni |
| `/projeler` | projeler | `40-projeler/DIZIN.md`, DURUM başlıkları, git durumu, klonlama | yeni |
| `/yayinla` | projeler | Sürüm kararı, etiket, açık iskelet üretimi, release | `yayinla.sh`'in elle çağrılması |
| `/ayikla` | hafıza / gelen | `90-gelen-kutusu/` öğeleri için hedef önerir, uygular | (aynı; yol güncellemesi Aşama B'de) |

Yeni komut eklenince bu tabloya ve `00-cekirdek/sablonlar/beceri/ana-menu.md` menüsüne aynı değişiklikte eklenir.
