# 20-araclar/codex

Codex proje içinde kök `AGENTS.md`'yi okur (oradan `00-cekirdek/AGENTS.md`'ye yönlendirilir). Global:
`kur.sh --genel` ile `~/.codex/AGENTS.md` → `00-cekirdek/AGENTS.md`, `~/.codex/config.toml` → `genel/config.toml`
(sır taraması geçerse), `~/.codex/skills/<ad>` → `.claude/skills/<ad>`.

Aşama 2'de doldurulacak: `genel/config.toml` (mevcut `~/.codex/config.toml`'dan, mutlak yollar `$CODEX_HOME` ile),
proje düzeyi `.codex/config.toml` desteği doğrulaması. Giriş: `codex login` / durum `codex login status`.
Makine-yerel: `~/.codex/{auth.json,*.sqlite*,sessions/,cache/,.tmp/,tmp/,logs*,installation_id,plugins/,packages/}`.
