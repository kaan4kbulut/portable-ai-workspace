# 20-araclar — Araçlar

İşletim sisteminin **programlar** katmanı: her aracın git'te duran ayarı, notları ve bilgisi. Proje kapsamı (`.claude/`,
kök `AGENTS.md`, `opencode.json`) zaten kendi kendine yeter; buradaki `genel/` kopyaları yalnızca klasör **dışında** da
aynı kuralları isteyenler için `kur.sh --genel` ile makineye bağlanır.

| Klasör | İçerik |
|---|---|
| `claude-code/` | `genel/CLAUDE.md.sablon` (→ `~/.claude/CLAUDE.md`, yol doldurulur), `genel/settings.json` (→ `~/.claude/settings.json`), `notlar.md` |
| `codex/` | `genel/config.toml` (→ `~/.codex/config.toml`; Aşama 2), `notlar.md` |
| `opencode/` | `genel/opencode.json` (→ `~/.config/opencode/opencode.json`; Aşama 2), `notlar.md` |
| `agy/` | `genel/mcp_config.json`, README (agy'nin okuduğu dosyalar) |
| `gh/` | `takma-adlar.yml` (`gh alias import`) |
| `docker/` | `compose/` dosyaları (llama-server vb.) |
| `mcp/` | sunucu başına `tanim.json`; `mcp-derle.sh` kök `.mcp.json`'u üretir (Aşama 5) |
| `yerel-modeller/` | `modeller.md` kaydı, `yapilandirma/`, `olcumler/`, `agirliklar/` (git dışı) |

Beceriler burada değil `.claude/skills/` altındadır (tek kanonik yer; Codex'e `kur.sh --genel` dağıtır).

**Girer:** araç ayarı, araç notu, model kaydı. **Girmez:** kimlik/giriş dosyası, araç önbelleği, oturum kaydı, model ağırlığı (git dışı klasörde).
