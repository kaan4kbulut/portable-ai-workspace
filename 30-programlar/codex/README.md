---
katman: programlar
surum: 0.164.0
son_kontrol: 2026-10-23
kaynaklar: [https://developers.openai.com/codex, https://github.com/openai/codex]
baglar: [../README.md, ../../10-donanim/monster/README.md, ../claude-code/README.md, ../cc-safety-net/README.md, ../mcp/README.md]
---

# OpenAI Codex CLI (`codex`)

## Nedir
OpenAI'ın yerel terminal kodlama ajanı ve komut satırı aracıdır (`codex-cli 0.164.0`).
Kodu inceleme, hata ayıklama ve yalıtılmış sandbox kiplerinde etkileşimsiz görev çalıştırma yeteneği sunar.

## Atölyedeki rolü
- **Çapraz inceleyici ve zor hata uzmanı:** "Yazan ile inceleyen farklı sağlayıcıdan olur" ilkesi gereği Claude Code'un yazdığı değişiklikleri ve güvenlik duvarlarını (`codex exec -s read-only`) inceler (`00-cekirdek/AGENTS.md`, `60-hafiza/kararlar/KARARLAR.md`).
- Çekirdekte (atölye kökünde) doğrudan etkileşimli çalıştırılmaz; çekirdek ajan tarafından proje dizini hedeflenerek (`codex exec -C <proje>`) kendi girişiyle çağrılır.
- Kota kıt olduğu için araştırma işçisi veya genel kod yazıcı olarak kullanılmaz.

## Kurulum ve giriş
- Kurulum betiği: `bash 20-sistem/kurulum/araclar/codex.sh` (Node/npm üzerinden `npm install -g @openai/codex`; önce `araclar/node.sh` gerekir).
- Giriş yalnızca aracın kendi komutuyla yapılır: `codex login` (durum kontrolü: `codex login status`).
- Kimlik dosyası (`~/.codex/auth.json`) asla okunmaz, kopyalanmaz ve HTTP uç noktasına açılmaz (`my-work/accounts.py` deseni kesinlikle yasaktır).

## Etkileşimsiz çağırma
`codex --help` ve `codex exec --help` ile bu makinede doğrulanan bayraklar:
```bash
codex exec -C <proje-dizini> -s read-only -o son-mesaj.txt "Değişiklikleri güvenlik açısından incele"
codex exec -C <proje-dizini> -s workspace-write --json --ephemeral "Testleri çalıştır ve hatayı bul"
codex review
```
- Seçenekler (`codex exec`): `-C`/`--cd <DIR>` (çalışma kökü), `-s`/`--sandbox <read-only|workspace-write|danger-full-access>`, `-o`/`--output-last-message <FILE>`, `--json` (stdout'a JSONL), `--output-schema <FILE>`, `-m`/`--model <MODEL>`, `-c`/`--config <key=value>`, `-p`/`--profile <ad>`, `--worktree`, `--add-dir <DIR>`, `--ephemeral` (oturumu diske yazmaz), `--skip-git-repo-check`, `--ignore-user-config`, `--ignore-rules`, `--oss`, `--local-provider <lmstudio|ollama>`.

## Okuduğu dosyalar
- **Kurallar (`AGENTS.md`):** Proje kökünden yukarı doğru `AGENTS.md` dosyalarını ve kullanıcı düzeyinde `~/.codex/AGENTS.md` (veya `~/.agents/AGENTS.md`) dosyasını okur. Atölyede kök `AGENTS.md` onu `00-cekirdek/AGENTS.md`'ye yönlendirir; `kur.sh --genel` ise `~/.codex/AGENTS.md` → `00-cekirdek/AGENTS.md` bağını kurar.
- **Ayarlar (`config.toml`):** Kullanıcı düzeyinde `~/.codex/config.toml` (`$CODEX_HOME/config.toml`), proje düzeyinde `codex.toml` / `.codex/config.toml`. `kur.sh --genel` sır taramasından (`api_key|token|secret`) geçirerek `30-programlar/codex/genel/config.toml` dosyasını bağlar.
- **Beceriler ve kurallar:** `~/.codex/skills/<ad>` (`kur.sh --genel` ile `.claude/skills/<ad>`'a bağlanır) ve `.rules` execpolicy dosyaları.
- **Makine-yerel (depoya girmez):** `~/.codex/{auth.json,*.sqlite*,sessions/,cache/,.tmp/,tmp/,logs*,installation_id,plugins/,packages/}`.

## Dikkat
- **Kota:** ChatGPT Plus aboneliği **kıttır**; yalnızca çapraz kod/güvenlik incelemesi ve zor hatalar için harcanır.
- **ToS:** Abonelik girişi yalnızca resmi `codex` CLI'da kendi girişiyle kullanılır; otomasyon/API ağ geçitlerine anahtar çıkarılmaz.
- **Salt okunur sandbox (`-s read-only`):** İnceleme görevlerinde her zaman `-s read-only` tercih edilir. Bu kipte dosya sistemi yazma denemeleri (`tempfile.gettempdir()` gibi) başarısız olacağından yardımcı betikler ortam değişkenini (`TMPDIR` veya `/tmp`) doğrudan kullanmalıdır.

## Eksikler
- `30-programlar/codex/genel/config.toml` şablonunun mevcut `~/.codex/config.toml` içinden mutlak yollardan arındırılarak (`$CODEX_HOME` ile) oluşturulması (Plan Aşama C).
- Proje düzeyi `.codex/config.toml` / `codex.toml` öncelik davranışının bu sürümde canlı doğrulanması.
