---
katman: programlar
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: [https://modelcontextprotocol.io, https://github.com/modelcontextprotocol/modelcontextprotocol]
baglar: [../README.md, ../claude-code/README.md, ../codex/README.md, ../opencode/README.md, ../agy/README.md]
---

# Model Context Protocol (`mcp`)

## Nedir
AI kodlama ajanlarının (istemci) dış veri kaynaklarına, yerel araçlara ve servislere (sunucu) JSON-RPC 2.0 üzerinden standart biçimde bağlanmasını sağlayan açık protokoldür.
Tek bir ikili program değil; dört CLI'ın (`claude`, `codex`, `opencode`, `agy`) ortak kullandığı araç genişletme katmanıdır.

## Atölyedeki rolü
- **Tek kaynaklı araç köprüsü:** Her araç için ayrı MCP ayarı elle yazılmaz; sunucu başına tek bir `<ad>/tanim.json` tutulur ve tüm CLI'ların MCP yapılandırmaları bu tanımdan türetilir (`30-programlar/mcp/README.md`, `00-cekirdek/ANAYASA.md`).
- 2026-10-23 itibarıyla temiz başlangıç ilkesi gereği hiçbir araçta etkin MCP sunucusu yoktur; masaüstüne bağlı eski MCP'ler Codex ayarından temizlenmiştir (`00-cekirdek/PLAN.md` Altyapı 0).

## Kurulum ve giriş
- Bağımsız bir kurulum betiği yoktur; sunucular `npx`/`uvx`/ikili komutlarla ilgili ajan tarafından başlatılır.
- Atölyede sunucu tanımı `30-programlar/mcp/<ad>/tanim.json` (yeni yerleşimde `30-programlar/mcp/<ad>/tanim.json`) olarak eklenir:
  `{"type":"stdio|http","command":"...","args":[...],"env":{"ANAHTAR":"${ANAHTAR}"}}`
- Kimlik veya API anahtarı gerektiren MCP sunucularında değerler yalnızca `${ENV}` ortam değişkeni referansıyla verilir; tanım dosyasına açık sır yazılmaz.

## Etkileşimsiz çağırma
Dört CLI'da bu makinede (`--help` ile) doğrulanan MCP yönetim alt komutları:
```bash
claude mcp list
codex mcp --help
opencode mcp --help
agy mcp list
```
- Tek seferlik çalışma zamanı yüklemesi (Claude Code): `claude -p --mcp-config .mcp.json --strict-mcp-config "istem"`.

## Okuduğu dosyalar
Resmi belgelere ve atölye yapısına göre her aracın okuduğu MCP yapılandırma dosyaları:
- **Atölye kaynak tanımı:** `30-programlar/mcp/<ad>/tanim.json` (sunucu başına tek kanonik tanım).
- **Claude Code:** Proje kökünde `.mcp.json` ve kullanıcı genelinde `~/.claude.json` (veya `--mcp-config <dosya>`).
- **Codex CLI:** `~/.codex/config.toml` ve proje `.codex/config.toml` içindeki `[mcp_servers.<ad>]` tabloları.
- **OpenCode:** Proje `opencode.json` ve global `~/.config/opencode/opencode.json` içindeki `mcp` alanı.
- **Antigravity CLI (`agy`):** Proje `.agents/mcp_config.json` ve global `~/.gemini/config/mcp_config.json` (`kur.sh --genel` ile `30-programlar/agy/genel/mcp_config.json` bağlanır).

## Dikkat
- **Sır yasağı (`AGENTS.md` Kesin kural 4):** `.mcp.json`, `mcp_config.json` veya `tanim.json` içine asla açık token/API anahtarı yazılmaz; `sir-desenleri.txt` pre-commit aşamasında engeller.
- **Abonelik sınırı (`AGENTS.md` Kesin kural 1):** Hiçbir MCP sunucusu abonelik OAuth token'larını (`~/.claude/.credentials.json`, `~/.codex/auth.json`, `~/.gemini/`) okuyacak veya başka bir modele aktaracak şekilde yapılandırılmaz.
- **Bağımlılık disiplini:** Gerçekten ihtiyaç duyulmayan MCP sunucusu eklenmez (bağlam penceresini şişirir ve saldırı yüzeyini büyütür).

## Eksikler
- `<ad>/tanim.json` dosyalarını kök `.mcp.json`, `config.toml`, `opencode.json` ve `mcp_config.json` biçimlerine derleyen `mcp-derle.sh` betiği henüz yazılmadı.
- İlk gerçek MCP sunucusu eklendiğinde dört CLI'da uçtan uca doğrulama yapılacak.
