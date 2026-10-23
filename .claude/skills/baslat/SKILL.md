---
name: baslat
description: >-
  Günü başlatır - git güvenliği, çevrimiçi denetimi ve güvenli pull, tam denetim, pano ve "nerede kalmıştık" özeti.
  "başla", "güne başla", "nerede kalmıştık", "bugün ne yapıyoruz" dendiğinde kullan.
---
# /baslat — gün başı

Git güvenliği, güvenli pull, denetim, pano ve gün başı özeti. Giriş yapmaz, kimlik dosyası okumaz.

1. **Git güvenliği:** `core.hooksPath` değeri `20-sistem/denetim/git-hooks` değilse ayarla. `safe.directory` içinde
   depo yoksa ekle. Dosya sistemi exFAT/NTFS gibi kısıtlıysa `core.filemode=false`, `core.symlinks=false`,
   `core.ignorecase=true` (ayrıntı: `20-sistem/kurulum/lib/ortak.sh`).
2. **Ağ ve pull:** çevrimiçi mi bak (`git ls-remote --exit-code origin HEAD`, kısa zaman aşımıyla). Çevrimdışıysa pull ve
   giriş denetimini atla, söyle. Çevrimiçi **ve** `git status --porcelain` boşsa `git pull --ff-only`; değilse atla ve nedenini yaz.
3. **Denetim:** önce `mkdir -p 20-sistem/durum/<host>`; sonra `bash 20-sistem/denetim/denetle.sh --tam` çalıştır, çıktıyı
   `20-sistem/durum/<host>/son-denetim.txt`'e yaz, çıkış kodunu sakla (2 = hata), son satırı özet say.
4. **Pano:** `/<ad>` menüsündeki pano alanlarının aynısı (makine, sürüm, git, araçlar+giriş, aktif proje,
   gelen kutusu, son devir notu, denetim).
5. **Nerede kalmıştık:** `60-hafiza/oturumlar/` en yeni 2 not, `40-projeler/DIZIN.md`, aktif projenin `DURUM.md`'si,
   `90-gelen-kutusu/AYIKLAMA.md`, `00-cekirdek/PLAN.md` ilk açık `[ ]` maddesi.
6. Kullanıcıya en fazla 10 satır: **Son oturum**, **Sonraki 3 adım**, **Karar gereken**, **Gelen kutusu**, **Denetim**, **Plan**.
7. Denetim hata verdiyse `/bakim` öner. Tek madde "şununla başlayalım" seç, nedenini söyle; kullanıcı seçene kadar değişiklik yapma.
