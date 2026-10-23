# 20-sistem/bakim — Gömülü bakım ajanı

Atölye hangi makineye giderse gitsin orada çıkan sorunları teşhis edip onaran, **her onarımdan öğrenen** ajan. Repoyla
taşınır, kurulum gerektirmez; Claude Code'da `/bakim` ya da `bakimci` alt ajanı, terminalden `bakim.sh`.

| Dosya | Görev |
|---|---|
| `BAKIMCI.md` | Ajanın talimatı ve yetki sınırı; tek kaynak (Claude alt ajanı `.claude/agents/bakimci.md` bunu içerir; Codex/opencode için prompt) |
| `bakim.sh [--raporla] [--otomatik] [--cli x]` | Çalıştırıcı: `denetle.sh --tam` → bulgu varsa CLI'a BAKIMCI.md + bulgular + bilinen sorunlar verilir |
| `guncelle.sh` | Araç sürümleri, atölye ve proje repolarının uzak durumu; yalnızca rapor (`durum/<host>/guncelleme-raporu.md`) |
| `bilinen-sorunlar.md` | Belirti → neden → onarım tablosu; ajan her yeni sorunda satır ekler |
| `onarimlar/<ad>.sh` | Tekrarlanabilir onarım reçeteleri |

Öğrenme döngüsü (her onarımdan sonra zorunlu): bilinen-sorunlar satırı → genel ders `60-hafiza/ogrenilenler/` →
tekrarlanabilirse `onarimlar/` betiği → denetim yakalayamadıysa `../denetim/kurallar/` kuralı → makineye özgü not `../durum/<host>/notlar.md`.

Yetki: `20-sistem/**`, `60-hafiza/ogrenilenler/**`, README'ler, taşıma. Dokunmaz: `00-cekirdek/`, proje kodu, kimlik dosyaları, `KARARLAR.md`.
Çalıştırmaz: sudo/apt, `rm -r`, `git push`, `login` (tam komut olarak listeler).

**Girer:** bakım/onarım/güncelleme. **Girmez:** denetim kuralları (→ `../denetim/`), kurulum (→ `../kurulum/`).
