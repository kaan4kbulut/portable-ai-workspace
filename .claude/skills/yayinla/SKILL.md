---
name: yayinla
description: >-
  Açık iskelet sürümünü yayınlar - sürüm artışı kararı, etiket, yayinla.sh ile iskelet üretimi, fark gösterimi, onaydan sonra
  iki repoya commit+etiket+push ve GitHub release. "yayınla", "sürüm çıkar", "açık iskeleti güncelle" dendiğinde kullan.
---
# /yayinla — sürüm yayını

Geri alınması zor her adımdan önce onay al; onaysız commit, push ya da release yok.

1. **Ön koşul:** `git status --porcelain` boş, `bash 20-sistem/denetim/denetle.sh --tam` hatasız, `gh auth status` tamam. Değilse dur, söyle.
2. **Sürüm kararı:** `SURUM.md` kuralı: major = üst bölüm/ANAYASA, minor = alt klasör/beceri/hook/betik, patch = metin/şablon.
   Son sürümden beri `git log` ve değişiklikleri incele; **seçenek + kanıt + öneri** sun (ör. "minor: 3 yeni beceri"). Karar kullanıcının.
3. `SURUM.md` başına yeni `## X.Y.Z — YYYY-MM-DD` bölümünü yaz (kısa madde listesi); ANAYASA başlık sürümü uyuşmalı (`denetle.sh` bakar). Değişikliği göster.
4. Açık repo temiz mi: `git -C 40-projeler/aktif/portable-ai-workspace status --porcelain` boş olmalı; değilse dur ve söyle.
   Sonra `bash 20-sistem/yayin/yayinla.sh --kuru` çalıştır ve çıktıyı (eklenen, değişen, **silinecek** dosyalar dahil) göster.
   **Açık onay almadan** gerçek üretimi (`bash 20-sistem/yayin/yayinla.sh`) çalıştırma.
   Sır ya da kişisel iz uyarısı çıkarsa dur; `20-sistem/yayin/kisisel.txt` düzeltmesini öner.
5. Üretimden sonra açık iskelet farkı: `git -C 40-projeler/aktif/portable-ai-workspace status --short` ve `diff --stat`; kişisel bir şey sızdı mı bak.
6. **Onay iste** (özel repo + açık repo, sürüm `vX.Y.Z`). Onaylanırsa sırayla:
   - özel repo: `git add -A`, commit (`chore(surum): vX.Y.Z`), `git tag vX.Y.Z`, `git push` ve `git push origin vX.Y.Z`
   - açık repo (`40-projeler/aktif/portable-ai-workspace`): aynı commit/etiket/push
   - iki repoda `gh release create vX.Y.Z --notes-file <not>`; not dosyası `SURUM.md`'den ilgili bölümün geçici kopyasıdır (scratchpad), depoya yazılmaz.
7. Çıktı: sürüm, iki reponun etiket/release bağlantıları, atlanan adımlar. Kaydedilmesi gereken bir seçim varsa `/karar`.
