# 20-araclar/claude-code

Claude Code'un proje kapsamı kökteki `.claude/` ve `CLAUDE.md`'dir; burada yalnızca **global** kopya ve notlar durur.

| Dosya | Nereye | Nasıl |
|---|---|---|
| `genel/CLAUDE.md.sablon` | `~/.claude/CLAUDE.md` | `kur.sh --genel` `__ATOLYE__` yerine kökün mutlak yolunu yazıp **kopyalar** (symlink değil; tek mutlak yol makine tarafındadır) |
| `genel/settings.json` | `~/.claude/settings.json` | symlink; global izinler, hook yok (hook'lar proje kapsamında) |
| `.claude/skills/<ad>` | `~/.claude/skills/<ad>` | tek tek symlink; `~/.claude/skills/synced/` claude.ai'ye aittir, ellenmez |

Makine-yerel kalan (asla depoda): `~/.claude/{.credentials.json,history.jsonl,projects/,sessions/,session-env/,shell-snapshots/,file-history/,cache/,backups/,plugins/,skills/synced/,settings.local.json}`.

Giriş durumu: `claude` içinde `/status`. Otomatik hafıza atölyede kapalı (`autoMemoryEnabled: false`).
