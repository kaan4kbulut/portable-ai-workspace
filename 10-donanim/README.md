---
katman: donanim
surum: "-"
son_kontrol: YYYY-MM-DD
kaynaklar: []
baglar: [../30-programlar/README.md, ../00-cekirdek/PLAN.md]
---

# 10-donanim — Donanım katmanı

Atölyenin çalıştığı ya da eriştiği makineler: makine başına bir klasör (`<makine>/README.md` varlık sayfası, `profil.md`,
o makineye özgü kurulum betikleri). `kur.sh`, makinenin kısa `hostname` değerini `profil.md` içindeki `hostname:` satırıyla
eşleştirir; eşleşme yoksa makine `misafir` sayılır.

| Makine | Rol | Sayfa |
|---|---|---|
| `ornek` | örnek profil; kendi makinen için kopyala | [ornek/profil.md](ornek/profil.md) |
| `misafir` | tanınmayan makine (varsayılan) | [misafir/profil.md](misafir/profil.md) |

**Girer:** makine sayfası, profil, makineye özgü kurulum betiği. **Girmez:** IP adresi, seri numarası, kimlik/anahtar.
