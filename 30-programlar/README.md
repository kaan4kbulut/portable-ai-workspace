---
katman: programlar
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: [https://code.claude.com/docs, https://developers.openai.com/codex, https://opencode.ai/docs, https://antigravity.google]
baglar: [../10-donanim/README.md, ../10-donanim/monster/README.md, ../00-cekirdek/AGENTS.md, ../60-hafiza/kararlar/KARARLAR.md]
---

# 30-programlar — Programlar Katmanı

Atölyenin **programlar** katmanı: kullanılan her CLI aracının, protokolün, koruma kancasının ve yerel model sunucusunun tek kanonik varlık sayfası, git'te izlenen ayar şablonları ve kullanım sözleşmesi burada durur. Proje kapsamı (`.claude/`, kök `AGENTS.md`, `opencode.json`) kendi kendine yeter; `genel/` altındaki şablonlar yalnızca atölye klasörü dışında da aynı kuralları isteyen makinelerde `bash 20-sistem/kurulum/kur.sh --genel` ile kullanıcı ev dizinine bağlanır.

## Katman dizini

| Varlık | Sürüm (MONSTER) | Atölyedeki rolü | Kurulum betiği | Giriş / durum komutu |
|---|---|---|---|---|
| [`claude-code/`](./claude-code/README.md) | `2.1.309` | Çekirdek ajan, birincil yazıcı ve orkestratör (kota: Max 5x, geniş) | `20-sistem/kurulum/araclar/claude.sh` | `claude auth login` · `claude auth status` (`/status`) |
| [`codex/`](./codex/README.md) | `0.164.0` | Çapraz güvenlik/kod inceleyici ve zor hata uzmanı (kota: Plus, kıt) | `20-sistem/kurulum/araclar/codex.sh` | `codex login` · `codex login status` |
| [`opencode/`](./opencode/README.md) | `2.1.3` | Ücretsiz, açık API veya yerel model işçisi | `20-sistem/kurulum/araclar/opencode.sh` | `opencode auth login` · `opencode auth list` |
| [`agy/`](./agy/README.md) | `1.4.6` | Geniş kotalı araştırma, salt okunur haritalama ve yardımcı ajan (kota: AI Ultra, geniş) | `20-sistem/kurulum/araclar/agy.sh` | `agy` (etkileşimli giriş) · `agy changelog` |
| [`gh/`](./gh/README.md) | `2.103.0` | Repo envanteri (`gh repolar`), PR/issue ve çift repo sürüm (`release`) yönetimi | `20-sistem/kurulum/araclar/gh.sh` | `gh auth login` · `gh auth status` |
| [`docker/`](./docker/README.md) | `29.1.3` | Yerel model (`llama-server` CUDA) ve yalıtılmış servis konteyner çalışma zamanı | `20-sistem/kurulum/araclar/docker.sh` | `docker login` · `docker info` |
| [`mcp/`](./mcp/README.md) | `-` | Dört CLI için tek kaynaklı (`tanim.json` → `.mcp.json`) araç genişletme protokolü | — (`mcp-derle.sh` planlı) | `claude mcp list` · `agy mcp list` |
| [`yerel-modeller/`](./yerel-modeller/README.md) | `-` | MONSTER GPU'da `llama.cpp` (`server-cuda`) ile özet/sınıflandırma/arama modelleri | Docker `server-cuda` (Altyapı 3) | `curl http://127.0.0.1:8080/health` |
| [`cc-safety-net/`](./cc-safety-net/README.md) | `2.6.12` | Ayrıştırıcı tabanlı yıkıcı komut ve sır erişimi engelleme kancası (`PreToolUse`) | `20-sistem/kurulum/araclar/cc-safety-net.sh` | `cc-safety-net status` · `cc-safety-net doctor` |

## Ortak ilkeler
- **Resmi CLI + kendi girişi (`AGENTS.md` Kesin kural 1):** Her araç yalnızca kendi resmi CLI komutuyla ve o makinedeki kendi oturumuyla çalışır. `~/.claude/.credentials.json`, `~/.codex/auth.json`, `~/.gemini/` ve `~/.config/gh/hosts.yml` asla okunmaz, kopyalanmaz ve ağ geçitlerine verilmez.
- **Yazan ≠ inceleyen:** Kod yazan ajan ile inceleyen ajan farklı sağlayıcıdan seçilir (örn. Claude yazar, `codex exec -s read-only` inceler).
- **Becerilerin yeri:** Ortak beceriler burada değil `.claude/skills/` altındadır (`kur.sh --genel` diğer araçlara dağıtır).

**Girer:** varlık sayfası (`README.md`), genel ayar şablonu (`genel/`), MCP sunucu tanımı, Compose dosyası, model kaydı ve ölçüm raporu.
**Girmez:** kimlik/oturum dosyası, araç önbelleği, konuşma geçmişi, GGUF model ağırlıkları (`agirliklar/` git dışıdır).
