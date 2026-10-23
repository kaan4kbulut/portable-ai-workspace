---
name: baslat
description: Oturum başında "bugün nereden devam" özeti çıkarır: son devir notu, aktif proje DURUM.md, bekleyen kararlar, gelen kutusu, denetim. "başla", "nerede kalmıştık", "bugün ne yapıyoruz" dendiğinde kullan.
---
# /baslat — nerede kalmıştık

1. Oturum başında hook'un bastığı bağlamı (son devir notları, KARARLAR başı, aktif proje, denetim) kullan;
   yoksa aynı kaynakları oku: `40-hafiza/oturumlar/` en yeni 2 not, `30-projeler/DIZIN.md`, aktif projenin `DURUM.md`'si,
   `70-gelen-kutusu/AYIKLAMA.md`, `00-cekirdek/PLAN.md` ilk açık `[ ]` maddesi.
2. Kullanıcıya en fazla 10 satır: **Son oturum** (ne yapıldı), **Sonraki 3 adım** (devir notundan), **Karar gereken**,
   **Gelen kutusu** (öğe sayısı, 30 günü geçen var mı), **Denetim** (hata/uyarı), **Plan** (açık aşama).
3. Öneri: "şununla başlayalım" diye tek madde seç ve nedenini söyle. Kullanıcı seçene kadar değişiklik yapma.
