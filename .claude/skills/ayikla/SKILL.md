---
name: ayikla
description: 90-gelen-kutusu/'ndaki her öğe için ANAYASA "ne nereye gider" tablosuna göre hedef önerir (taşı / arşivle / sil / bekle), onaylananları uygular, AYIKLAMA.md'yi günceller. Haftalık gözden geçirmede ya da "gelen kutusunu ayıkla" dendiğinde kullan.
---
# /ayikla — gelen kutusu ayıklama

1. `90-gelen-kutusu/` içeriğini listele (README.md ve AYIKLAMA.md hariç); her öğe için yaş (gün) hesapla.
2. Her öğe için `00-cekirdek/ANAYASA.md` madde 5 tablosuna göre **tek** hedef öner:
   `taşı → <yol>` · `arşivle → 80-arsiv/YYYY-MM-DD-<ad>/ (NEDEN.md ile)` · `sil` (yalnızca kendi ürettiğimiz çöp:
   log, geçici çıktı) · `bekle` (en fazla bir kez; AYIKLAMA.md'de bekleme sayısı tutulur).
   Aynı türde 3+ öğe birikmişse ve hiçbir yere sığmıyorsa **yeni alt klasör** öner (ANAYASA 6.3): şablon
   `00-cekirdek/sablonlar/bolum/`, README zorunlu, `/karar` kaydı, `SURUM.md` minor.
3. Öneri tablosunu kullanıcıya sun: `| öğe | yaş | öneri | hedef | neden |`. Onay iste.
4. Onaylananları uygula: taşıma `git mv` (izleniyorsa) ya da `mv`; arşive giden her öğe için `NEDEN.md`
   (`00-cekirdek/sablonlar/belge/neden.md`). Silme yalnızca açık onayla.
5. `90-gelen-kutusu/AYIKLAMA.md`: son ayıklama tarihi, bekleyenler listesi (öğe · bekleme sayısı · neden).
6. 30 günü geçen ve hâlâ bekleyen öğe varsa kullanıcıya ayrıca söyle.
