# 00-cekirdek — Çekirdek

Atölyenin **kernel**'i: yalnızca kurallar ve ana plan. Her CLI (Claude Code, Codex, opencode, agy) buradan beslenir.

| Dosya | Görev | Kim düzenler |
|---|---|---|
| `ANAYASA.md` | Atölye düzeninin kuralları (taşınabilirlik, adlandırma, ne nereye, yaşam döngüsü, sürümleme) | yalnızca insan |
| `AGENTS.md` | Dört CLI'ın ortak çalışma kuralları; kök `AGENTS.md` bunu `@` ile içerir | insan + ajan (küçük ekler) |
| `CLAUDE-EK.md` | Yalnızca Claude Code'a özel ekler; global `~/.claude/CLAUDE.md` şablonu bunu içerir | insan + ajan |
| `PLAN.md` | Aşamalı ana plan; her aşama karar noktasıyla biter | insan + ajan |
| `ILKELER.md` | (Aşama F) 1nn5 `00_TEMEL.md`'den seçilen çalışma ilkeleri | insan |

**ANAYASA'nın üç koruma katmanı:**
1. settings `deny`,
2. `anayasa-koruma.py` ve `yikici-koruma.py` hook'ları,
3. dosya izni `444`: `kur.sh` her kurulumda uygular; exFAT'ta uygulanamaz.

Düzenlemek için (insan): `chmod u+w 00-cekirdek/ANAYASA.md`, düzenle, `chmod 444 00-cekirdek/ANAYASA.md`; ardından `SURUM.md`
major satırı ve `KARARLAR.md` kaydı.

**Girer:** kural, ilke, plan. **Girmez:** betik, kod, not, karar kaydı (kararlar `40-hafiza/kararlar/`), cihaz bilgisi (`40-hafiza/cihazlar/`).
