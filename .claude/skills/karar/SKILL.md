---
name: karar
description: Bir kararı 60-hafiza/kararlar/KARARLAR.md'ye biçimli kaydeder (tarih, karar, gerekçe/kanıt); değişen eski kararı "geçersiz" işaretler. "karar ver", "kararı kaydet", "bunu not al" dendiğinde ya da önemli bir seçim netleşince kullan.
argument-hint: "[kararın kısa özeti]"
---
# /karar — karar kaydı

1. Kararı tek cümleye indir; gerekçeyi ve kanıtı (ölçüm, belge, kullanıcı sözü) ayır. Kanıt yoksa "gerekçe: tercih" de.
2. `60-hafiza/kararlar/KARARLAR.md`'de aynı konuda eski kayıt var mı ara (`rg -n "<anahtar kelime>"`).
   Varsa eski satırı silme; başına `~~` sonuna `~~ **geçersiz** (YYYY-MM-DD, neden)` ekle.
3. Yeni kaydı dosyanın **en üstündeki** tarih başlığına (yoksa bugünün `## YYYY-MM-DD` başlığını aç) şu biçimde ekle
   (`00-cekirdek/sablonlar/belge/karar-kaydi.md`):
   `- **<karar>.** <gerekçe/kanıt>. (Kaynak: <kullanıcı/ölçüm/belge>)`
4. Karar atölye düzenini değiştiriyorsa (yeni bölüm, ANAYASA maddesi) `SURUM.md`'ye satır hatırlat; ANAYASA değişikliğini
   kullanıcı yapar.
5. Kullanıcıya eklenen satırı ve varsa geçersiz işaretlenen satırı göster. Commit yapma.
