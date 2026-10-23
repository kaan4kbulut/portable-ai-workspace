# 10-sistem/cihazlar — Makine profilleri ve kurulum betikleri

Makine başına bir klasör. `profil.md` içindeki `hostname:` satırı `kur.sh`/`basla.sh`'ın makineyi tanımasını sağlar;
eşleşme yoksa makine `misafir` sayılır. Kalıcı cihaz bilgisi (rol, donanım, tarihçe) `40-hafiza/cihazlar/<ad>.md`'de;
burada **kurulumla ilgili** olan durur.

| Klasör | İçerik |
|---|---|
| `<makine>/profil.md` | `hostname:`, rol, kısa donanım, özel notlar |
| `<makine>/paketler.txt` | apt paketleri (kur.sh sudo varsa kurar) |
| `<makine>/sudo-*.sh` | root gerektiren tek seferlik kurulumlar (elle, `sudo bash ...`) |
| `<makine>/*.sh` | kullanıcı düzeyi makineye özgü betikler |
| `misafir/` | tanınmayan makine için en küçük profil |

**Girer:** makineye özgü kurulum. **Girmez:** makinenin geçici durumu (→ `../durum/`), kimlik/şifre/anahtar.
