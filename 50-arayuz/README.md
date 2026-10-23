# 50-arayuz — Arayüz katmanı

Kullanıcının atölyeyle konuştuğu yüzey. Kullanıcı betik çalıştırmaz; her şey Claude Code içinde bir slash komutudur.
Depo kökünde `claude` çekirdek ajanı açar (`.claude/settings.json` içindeki `agent` anahtarı); ana menü `/<ad>` komutudur
(`<ad>`, `00-cekirdek/kimlik.json`'dadır).

| Parça | Ne |
|---|---|
| `komutlar.md` | Tüm komutların kataloğu: komut, katman, ne yapar, neyin yerine geçer |
| Durum çubuğu | Claude Code status line: makine, dal, denetim özeti (tanım `.claude/` ayarlarında) |
| `harita.html` | Atölyenin görsel haritası (katmanlar, komutlar); `00-cekirdek/HARITA.md`'den üretilir |
| Uzaktan erişim | Tailscale üzerinden başka cihazdan aynı oturum (kurulum `20-sistem/ag/`) |

Beceriler tek kanonik yerde, `.claude/skills/` altında durur; bu klasör onların **belgesidir**, kopyası değildir.

**Girer:** komut kataloğu, durum çubuğu notları, harita, uzaktan erişim kullanım notu.
**Girmez:** beceri dosyaları (→ `.claude/skills/`), ağ kurulumu (→ `20-sistem/ag/`), sır.
