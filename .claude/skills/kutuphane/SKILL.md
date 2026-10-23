---
name: kutuphane
description: >-
  "/kutuphane <konu>" bir konuyu kaynaklı araştırıp 70-kutuphane/arastirmalar/ altına rapor yazar; "/kutuphane tara" denetim + kuyruk + harita çalıştırır. "araştır", "kütüphane", "sayfaları tara", "harita güncelle" dendiğinde kullan.
---
# /kutuphane

Argümana göre davran.

## `/kutuphane tara`
1. `python3 20-sistem/kutuphaneci/kutuphaneci.py denetle`
2. `python3 20-sistem/kutuphaneci/kutuphaneci.py kuyruk`
3. `python3 20-sistem/kutuphaneci/kutuphaneci.py harita`
4. Bulguları öncelik sırasıyla kısa göster (kaç bulgu, kaç iş bekliyor, en önemli 5).
5. Kullanıcıya sor: bekleyen işler `calistir` ile işlensin mi? Önce `calistir --kuru` ile ne olacağını göster; onay gelmeden gerçek çalıştırma yapma (agy/claude kota harcar; codex yalnız açıkça istenirse `--isci codex`).

## `/kutuphane <konu>`
1. `70-kutuphane/arastirmalar/DIZIN.md` ve `00-cekirdek/HARITA.md` içinde konu zaten var mı bak; varsa özetle ve yalnızca eksiği araştır.
2. `kutuphaneci` alt ajanıyla (Agent aracı, `subagent_type: kutuphaneci`) konuyu araştır; rapor `70-kutuphane/arastirmalar/<konu>/<YYYY-MM-DD>-<ad>.md` olur, "Kaynak denetimi:" satırı ve DIZIN.md bağlantısı zorunludur.
3. Sonunda `kutuphaneci.py denetle` çalıştırıp yeni rapor için bulgu çıkıp çıkmadığına bak; raporun özetini ve dosya yolunu ver.

Kural: `00-cekirdek/ANAYASA.md` ve `60-hafiza/kararlar/` değiştirilmez; karar gerekiyorsa `/karar` öner.
