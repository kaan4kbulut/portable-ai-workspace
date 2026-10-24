# 70-kutuphane — Kütüphane

İşletim sisteminin **belgeler** katmanı: zamanla eskimeyen bilgi. Kategori başına klasör, konu başına `.md`.
Her belge başında `kaynak:` ve `tarih:` satırı; iddia varsa kanıt bağlantısı.

| Klasör | İçerik |
|---|---|
| `araclar/` | CLI/araç kullanım notları, karşılaştırmalar (Claude Code, Codex, opencode, agy, gh, docker…) |
| `arastirmalar/` | kaynaklı araştırma raporları, konu başına klasör, `DIZIN.md` |
| `modeller/` | model kartları, ölçüm özetleri, seçim tabloları |
| `saglayicilar/` | Anthropic/OpenAI/Google… kullanım şartı özetleri, kota tabloları (kimlik yok) |
| `teknoloji/` | dil, çerçeve, altyapı notları |
| `bilgi/` | genel; alt klasör konu başına |

İçe aktarım (Aşama 5): eski `1nn5/KUTUPHANE` (~6900 dosya) **seçici** gelir: `gh api` ile dizin listesi → `90-gelen-kutusu/`'na
10'ar öğe → `/ayikla` ile buraya. Toplu kopya yok.

**Girer:** kalıcı bilgi belgesi. **Girmez:** karar (→ `60-hafiza/`), ham indirme (→ `90-gelen-kutusu/`), araç ayarı (→ `30-programlar/`).
