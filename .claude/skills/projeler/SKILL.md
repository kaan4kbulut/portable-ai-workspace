---
name: projeler
description: 40-projeler/DIZIN.md tablosunu, aktif projelerin DURUM.md başlığını ve git durumunu gösterir; planlı projeyi klonlamayı önerir. "projeler", "hangi projeler var", "ai-radar'ı klonla" dendiğinde kullan.
---
# /projeler — proje listesi

1. `40-projeler/DIZIN.md` tablosunu oku (ad, repo, durum, son dokunma).
2. Her **aktif** proje için: `40-projeler/aktif/<ad>/DURUM.md` ilk başlığı ve "Durum" satırı; klasör git reposuysa
   `git -C 40-projeler/aktif/<ad> status --porcelain | wc -l` ve push edilmemiş commit sayısı (`rev-list --count @{u}..HEAD`).
   Klasör yoksa "klonlanmamış" yaz.
3. Tablo: ad · durum · son dokunma · başlık · git (değişiklik / itilmemiş). Aktif projeyi (`20-sistem/durum/<host>/aktif-proje.txt`) işaretle.
4. **Planlı** proje varsa sor: klonlansın mı? Onaylanırsa `gh repo clone <sahip>/<ad> 40-projeler/aktif/<ad>` (repo DIZIN'den),
   ardından `DIZIN.md` durumunu `aktif`, `son dokunma`yı bugün yap; DURUM.md yoksa `00-cekirdek/sablonlar/belge/durum.md` şablonundan aç.
5. Yeni proje isteniyorsa önce `80-arsiv/`, `90-gelen-kutusu/`, `60-hafiza/` ve `gh repo list kaan4kbulut` içinde ara; aynı işi yapan ikincisini açma.
