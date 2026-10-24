---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [BAKIMCI.md, bilinen-sorunlar.md, onarimlar/README.md, ../denetim/README.md, ../kurulum/README.md]
---
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

## Ne işe yarar?

Düzen denetiminin bulgularını bakım ajanına iletir; sorun geçmişini ve yeniden kullanılabilir
onarım reçetelerini bir arada tutar. [Bilinen sorunlar](bilinen-sorunlar.md),
[onarım reçeteleri](onarimlar/README.md) ve [ajan tanımı](BAKIMCI.md) yerel başvuru kaynaklarıdır.

## Nasıl çalıştırılır / bağlanılır?

Depo kökünden:

```bash
# Kullanım seçeneklerini gösterir; bakım başlatmaz.
bash 20-sistem/bakim/bakim.sh --help
# Denetim bulgularını seçilen CLI'a teşhis için iletir.
bash 20-sistem/bakim/bakim.sh --raporla --cli claude
# Varsayılan onarım akışını başlatır.
bash 20-sistem/bakim/bakim.sh
# Güncelleme durumunu raporlar; ağ sorguları ve git fetch yapabilir.
bash 20-sistem/bakim/guncelle.sh
```

Çalıştırıcı Bash, ortak kurulum yardımcıları ve kurulu bir `claude`, `codex` veya `opencode`
komutu kullanır; varsayılan seçim bu sırayladır. Giriş durumunu kendisi kontrol etmez.
Bakım çıktısı `20-sistem/gunluk/bakim-YYYY-MM-DD-HHMM.md`, güncelleme raporu
`20-sistem/durum/<host>/guncelleme-raporu.md` yoluna yazılır.
`--raporla` ajana değişiklik yapmamasını söyler; çalıştırıcının günlük/dizin yazmasını engellemez.
Bu incelemede bakım ve güncelleme akışları çalıştırılmadı.

## Açık eksikler

- Bağımsız bakım sürümü ve resmi kaynak URL'leri: -. `70-kutuphane/` içinde ilgili kayıt bulunamadı.
- `bakim.sh` içindeki Codex/opencode dalları Aşama 2 doğrulamasını bekliyor;
  uyarı metninde rapor kipi belirtilse de bu dallara özel salt okunur kip seçeneği aktarılmıyor.
- Canlı onarım, CLI girişleri ve güncelleme sorgularının bu makinedeki çalışma durumu: -.
