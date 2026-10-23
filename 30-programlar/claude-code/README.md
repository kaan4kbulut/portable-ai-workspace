---
katman: programlar
surum: 2.1.309
son_kontrol: 2026-10-23
kaynaklar: [https://code.claude.com/docs, https://github.com/anthropics/claude-code]
baglar: [../README.md, ../../10-donanim/monster/README.md, ../cc-safety-net/README.md, ../codex/README.md, ../agy/README.md, ../mcp/README.md]
---

# Claude Code (`claude`)

## Nedir
Anthropic'in terminal tabanlı ajan kodlama aracıdır (`2.1.309 (Claude Code)`).
Atölyede varsayılan etkileşimli geliştirme ortamı ve çekirdek ajan giriş noktası olarak çalışır.

## Atölyedeki rolü
- **Birincil yazıcı ve çekirdek ajan:** Planlama, kod yazma, düzenleme ve beceri/alt ajan orkestrasyonunu yürütür (`00-cekirdek/AGENTS.md`, `60-hafiza/kararlar/KARARLAR.md`).
- Klasörde `claude` açıldığında settings `agent` anahtarıyla çekirdek ajan (`/kaan4kbulut`) devreye girer; `/baslat`, `/kapat`, `/karar`, `/ayikla`, `/denetle`, `/bakim` becerilerini çalıştırır.
- Araştırmada `Explore`, salt okunur incelemede `inceleyici`, düzen onarımında `bakimci` alt ajanlarını kullanır; kütüphaneci alt ajanı (`--agent kutuphaneci`) yerel systemd timer ile tetiklenir.

## Kurulum ve giriş
- Kurulum betiği: `bash 20-sistem/kurulum/araclar/claude.sh` (`https://claude.ai/install.sh` ile `~/.local/bin/claude` altına kullanıcı-yerel kurar).
- Giriş yalnızca aracın kendi komutuyla yapılır: `claude auth login` (veya oturum içinde `/login`).
- Giriş durumu: `claude auth status` veya oturum içinde `/status`. Kimlik dosyası (`~/.claude/.credentials.json`) ve `claude setup-token` çıktısı asla okunmaz veya taşınmaz.

## Etkileşimsiz çağırma
`claude --help` ile bu makinede doğrulanan bayraklar:
```bash
claude -p "istem" --output-format json
claude -p "istem" --output-format stream-json --include-partial-messages
claude -p --agent kutuphaneci --permission-mode plan "istem"
claude -p --fallback-model sonnet --max-budget-usd 1.00 --no-session-persistence "istem"
```
- Seçenekler: `-p`/`--print`, `--output-format <text|json|stream-json>`, `--input-format <text|stream-json>`, `--json-schema <schema>`, `--agent <ad>`, `--permission-mode <acceptEdits|auto|bypassPermissions|manual|dontAsk|plan>`, `--permission-prompts <host|none>`, `--allowedTools`, `--disallowedTools`, `--tools`, `--add-dir <dizin...>`, `--mcp-config`, `--strict-mcp-config`, `--settings <dosya|json>`, `--setting-sources <user,project,local>`, `--bare`, `--restricted`, `--safe-mode`, `-w`/`--worktree`.

## Okuduğu dosyalar
- **Kurallar ve bellek:** Proje kökünde `CLAUDE.md` veya `.claude/CLAUDE.md`, `.claude/rules/*.md`, kullanıcı genelinde `~/.claude/CLAUDE.md` (`kur.sh --genel` ile `30-programlar/claude-code/genel/CLAUDE.md.sablon` dosyasından `__ATOLYE__` doldurularak kopyalanır).
- **Ayarlar (öncelik sırasıyla):** Kurumsal yönetilen ayarlar → CLI bayrakları → `.claude/settings.local.json` (git dışı) → `.claude/settings.json` (proje; izinler + `SessionStart`, `PreToolUse`, `Stop`, `SessionEnd` hook'ları) → `~/.claude/settings.json` (`30-programlar/claude-code/genel/settings.json` symlink'i).
- **Uzantılar ve MCP:** `.claude/skills/<ad>/SKILL.md` (`commands/` buraya birleşti; `~/.claude/skills/synced/` claude.ai'ye aittir, ellenmez), `.claude/agents/*.md`, `.claude/hooks/*`, kök `.mcp.json`.
- **Makine-yerel (depoya girmez):** `~/.claude/{.credentials.json,history.jsonl,projects/,sessions/,session-env/,shell-snapshots/,file-history/,cache/,backups/,plugins/,skills/synced/,settings.local.json}`.

## Dikkat
- **Kota:** Claude Max 5x aboneliği **geniştir**; ana geliştirme ve yazma yükünü taşır. Yine de ağır işten önce kota kontrol edilir.
- **ToS:** Abonelik yalnızca resmi `claude` CLI'da kendi girişiyle kullanılır; OAuth/oturum anahtarı hiçbir ağ geçidine veya proxy'ye verilmez. `CLAUDE_CONFIG_DIR` kimlik dosyasını da taşıdığı için USB'de kullanılmaz.
- **Ayar ve hook tuzakları:** `autoMemoryEnabled: false` ile otomatik hafıza kapalıdır (hafıza `60-hafiza/`'da tutulur). `attribution.commit` ve `attribution.pr` boş string (`""`) olmalıdır; boolean verilirse `settings.json` yüklenmez ve hook'lar sessizce devre dışı kalır.
- **Alt ajan sistem istemi:** Ana ajan dosyasının gövdesi doluysa varsayılan sistem isteminin yerine geçer; ajan dosyası ince tutulur ve `@dosya` yerine Read aracıyla okuma talimatı verilir. Yıkıcı komutlar `cc-safety-net` + `.claude/hooks/yikici-koruma.py` ile çift katmanlı engellenir (exit 2 engeller).

## Eksikler
- `claude auth status` komutunun kota harcamadan `denetle.sh --tam` içine eklenmesi doğrulanacak (şu an denetim betiği elle `/status` öneriyor).
- Başka CLI için proje klasöründe ilgili CLI açılır veya `/araclar <arac> <görev>` kullanılır; giriş o makinede aracın kendi komutuyla yapılır.
