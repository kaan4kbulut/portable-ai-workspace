# CLI'ları başsız çalıştırma ve izin ayarları (resmî belgeler)
Yazan: Codex (--search, high, salt okunur) · doğrulayan: Claude (opencode V2 ve agy kota bulguları canlı sınandı) · tarih: 2026-10-24
Kaynak denetimi: 2026-10-24 itibarıyla yalnız resmî belgeler ve resmî kaynak kod incelendi; kabuk komutu çalıştırılmadı, dosya yazılmadı. Aşağıdaki örnekler belge/kod üzerinden denetlendi; makinenizde çalıştırılarak doğrulanmadı. Tarih belirtilmeyen bağlantılar yaşayan belgelerdir; denetim tarihleri 2026-10-24’tür.

**En önemli sürüm farkları:** Codex **0.134.0+**, `[profiles.ad]` yerine ayrı profil dosyası kullanıyor. OpenCode 1 ve 2’nin yerel yapılandırma biçimleri farklı; V2 desteklenen V1 ayarlarını uyumluluk katmanıyla okuyabiliyor. Antigravity belgelerinde `--print-timeout` varsayılanı çelişkili. [Codex profil geçişi](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles), [OpenCode V1→V2](https://opencode.ai/v2/docs/migrate-v1/), [agy referansı](https://antigravity.google/docs/cli/reference), [agy headless](https://antigravity.google/docs/cli/headless/).

**1. Google Antigravity CLI — `agy`**

**Ayar dosyası ve izin anahtarları**

Doğrulanan kullanıcı dosyası `~/.gemini/antigravity-cli/settings.json`; biçimi JSON’dur. İzin kuralları `permissions.allow`, `permissions.ask`, `permissions.deny` dizilerindeki `action(target)` metinleridir. Ayrı `commandAllowlist`, `commandDenylist` veya `permissionGrants` JSON anahtarları **doğrulanamadı**; bu isimlerle ayar üretmeyin. Belgelenen karşılık aşağıdadır. [Resmî ayarlar](https://antigravity.google/docs/settings?tab=ide#object-settings), [izinler](https://antigravity.google/docs/permissions/).

| İstenen kavram | Doğrulanan karşılık |
|---|---|
| Tool Execution Policy | `toolPermission` |
| Command Allowlist | `permissions.allow` içinde `command(...)` |
| Command Denylist | `permissions.deny` içinde `command(...)` |
| Permission Grants | `read_file(...)`, `write_file(...)`, `read_url(...)`, `execute_url(...)`, `command(...)`, `mcp(...)` kuralları |
| Sandbox | `enableTerminalSandbox: true` veya `--sandbox` |
| Çalışma alanı dışı erişim | `allowNonWorkspaceAccess` |

Tablodaki anahtarlar ve eylemler resmî [ajan ayarları](https://antigravity.google/docs/agent-settings?authuser=6) ve [CLI izinleri](https://antigravity.google/docs/permissions/) üzerinden doğrulandı.

`toolPermission` seçenekleri:

| Değer | Belgelenen davranış |
|---|---|
| `request-review` | Yazma, komut ve web araçlarında onay ister. |
| `strict` | Okuma dışındaki araçlarda onay ister; `auto`yu geçersiz kılar. |
| `always-proceed` | Araçları onay sormadan çalıştırır; `--dangerously-skip-permissions` bunu etkinleştirir. |
| `proceed-in-sandbox` | Sandbox içindeki komutları otomatik çalıştırır; dışarı çıkacak komutlarda onay ister. |

Açık izin kuralları için öncelik **Deny > Ask > Allow**’dur. Dolayısıyla `ask: ["command(*)"]`, daha dar bir `allow` kuralını da bastırır. [Ajan ayarları](https://antigravity.google/docs/agent-settings?authuser=6), [öncelik kuralları](https://antigravity.google/docs/permissions/).

**Proje düzeyi dosya: kısmen doğrulandı.** Resmî değişiklik günlüğü proje izin yapılandırmalarını `~/.gemini/config/projects/` altında konumlandırıyor; kesin dosya adı ve elle yazılacak tam JSON zarfı **doğrulanamadı**. `/permissions` içinde **Project / Shared / Global** kapsamları belgelenmiş durumda; proje iznini buradan yönetmek doğrulanan yoldur. Ayrıca depodaki özelleştirme dosyasının `/.gemini/config.json` konumuna taşınması, onun CLI `settings.json` ile aynı şemayı kullandığını kanıtlamaz. [Değişiklik günlüğü](https://antigravity.google/docs/changelog), [kapsam seçici](https://antigravity.google/docs/cli/commands/permissions).

**Modlar ve bayraklar**

| Seçenek | Farkı |
|---|---|
| `--mode accept-edits` | Çalışma alanındaki dosya oluşturma/düzenlemeleri otomatik kabul eder; komut iznini ayrıca değerlendirmeye devam eder. |
| `--mode auto` | Düzenlemeleri kabul eder; komutları sandbox içinde çalıştırır, dışarı çıkacak komutları otomatik değerlendirmeye gönderir. Riskli işlemler yine onay isteyebilir. |
| `--mode plan` | Kod tabanını inceleme ve düzenleme öncesi planlama içindir. |
| `--sandbox` | Terminal komutlarına işletim sistemi sınırlandırması uygular. |
| `--effort` | Modele bağlı düşünme düzeyi; referans `low`–`max`, headless sayfası `low/medium/high` diyor. |
| `--print-timeout 10m` | Başsız çalışma için açık süre sınırı. |

`auto`, Linux/macOS için **v1.3.5+** olarak belgelenmiştir; değişiklik günlüğündeki çıkış tarihi **2026-10-14**. `--sandbox`ın desteklenmeyen makinede etkisiz olması gibi **v1.4.4+** açıklamaları belgede bulunuyor, ancak bu sürümün 2026-10-24’e kadar yayımlandığı **doğrulanamadı**; incelenen günlük CLI için v1.4.0’ı gösteriyor. [Modlar](https://antigravity.google/docs/cli/modes/), [bayraklar](https://antigravity.google/docs/cli/reference), [sürümler](https://antigravity.google/docs/changelog).

**Başsız komut izninin dar yolu**

Doğrulanan yöntem: genel politikayı `request-review` bırakıp yalnız gereken komut/altkomutu `permissions.allow` içine koymak. `command(git)` bütün Git altkomutlarını kapsar; `command(git status)` daha dardır. Bunlar önek kurallarıdır; tam `argv` eşitliği garantisi olarak yorumlanmamalıdır. [Eşleştirme kuralları](https://antigravity.google/docs/permissions/).

Örnek `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "toolPermission": "request-review",
  "enableTerminalSandbox": true,
  "allowNonWorkspaceAccess": false,
  "permissions": {
    "allow": [
      "command(git status)",
      "command(git diff)"
    ],
    "deny": [
      "write_file(*)",
      "read_url(*)",
      "execute_url(*)",
      "mcp(*)"
    ]
  }
}
```

Bu dosya üzerinden, bir Git deposunda çalıştırılacak örnek:

```bash
agy -p "git status --short ve git diff --stat çalıştır; sonuçları özetle." \
  --sandbox \
  --effort medium \
  --print-timeout 10m \
  --output-format stream-json
```

JSON ve çağrı, resmî [izin örnekleri](https://antigravity.google/docs/permissions/) ve [başsız çalışma](https://antigravity.google/docs/cli/headless/) biçiminden uyarlanmıştır. Dosya araçlarına konan `write_file` yasağını, izin verilmiş bir shell komutunun yan etkilerini engelleyen işletim sistemi kuralı saymayın; terminal sınırı sandbox tarafından uygulanır. [Terminal sandbox](https://antigravity.google/docs/sandbox/).

**Akış sözleşmesi**

`stream-json`, satır başına bir JSON nesnesidir. Belgelenen alan özeti:

| `event` | Yük ve önemli alanlar |
|---|---|
| `init` | Üstte `conversation_id`; `init` içinde `cwd`, `tools`, `permission_mode`; ayarlanmışsa `model`, `agent`. |
| `step_update` | `conversation_id`, `step_index`, `state`, `step_type`; isteğe bağlı `text_delta`, `tool_name`, `tool_info`, `subagent_info`, `usage`. |
| `result` | `conversation_id`, `status`, `response`, `duration_seconds`, `num_turns`, `usage`; hata durumunda `error`. |

Belgelenen adım türleri `user_input`, `agent_response`, `tool`, `checkpoint`; durumlar `ACTIVE` ve `DONE`. `tool_info`, `name`, `parameters`, `output` ve hatada `error.type/message` taşır. Çok turlu akışta sonuç metni tura, kullanım sayaçları oturum toplamına aittir. [Resmî akış açıklaması](https://antigravity.google/docs/cli/headless/).

**Güvenilirlik açısından kritik:** Onay gerektiren araç başsız modda reddedilse bile süreç `0` ile çıkabilir. Ayrıca **v1.2.0, 2026-09-10** günlüğü timeout halinde kısmi çıktı ve başarılı çıkış davranışı bildiriyor. Koordinatör yalnız çıkış koduna bakmamalı; araç çıktısını, terminal olayı ve `stderr`i de denetlemelidir. `--print-timeout` varsayılanı referansta `0s`, headless sayfasında `5m`; örnekte bu nedenle açık süre kullanıldı. [Headless davranışı](https://antigravity.google/docs/cli/headless/), [değişiklik günlüğü](https://antigravity.google/docs/changelog).

**2. OpenAI Codex CLI**

**`codex exec` seçenekleri**

| Seçenek | Doğrulanan anlam |
|---|---|
| `-s`, `--sandbox` | `read-only`, `workspace-write`, `danger-full-access`. |
| `-a`, `--ask-for-approval` | Güncel genel seçenekler: `on-request`, `never`. |
| `--json` | JSONL olay akışı. |
| `-o`, `--output-last-message` | Son ajan mesajını belirtilen dosyaya yazar. |
| `--skip-git-repo-check` | Git deposu dışındaki dizinde çalışmayı sağlar. |
| `--search` | Canlı web araması; `web_search = "live"` karşılığı. |
| `-c 'model_reasoning_effort="medium"'` | Tek çağrı için TOML ayar geçersiz kılması. |

Bayraklar [güncel komut referansında](https://learn.chatgpt.com/docs/developer-commands), düşünme düzeyleri [ayar referansında](https://learn.chatgpt.com/docs/config-file/config-reference) belgelenmiştir. Kabul edilen effort değerleri seçilen modele bağlıdır.

**Sürüm ayrımı:** `-a` ve `--search` için eski sürümlerde genel/altkomut ayrımı önemlidir. **rust-v0.77.0** `exec` ayrıştırıcısında bu iki bayrak yoktur; işçi çağrısında açık `-c` ayarları kullanmak bu belirsizliği azaltır. [v0.77.0 exec kaynağı](https://raw.githubusercontent.com/openai/codex/rust-v0.77.0/codex-rs/exec/src/cli.rs), [üst komut aktarımı](https://raw.githubusercontent.com/openai/codex/rust-v0.77.0/codex-rs/cli/src/main.rs).

**stdin ve olaylar**

Prompt verilmezse veya `-` verilirse stdin prompt olarak okunur. Güncel belgede prompt argümanı ile birlikte pipe kullanılırsa argüman talimat, stdin ek bağlamdır. `--json` olayları arasında `thread.started`, `turn.started`, `item.*`, `turn.completed`, `turn.failed`, `error` bulunur; tamamlanan turun `usage` alanı token kullanımını taşır. [Başsız çalışma](https://learn.chatgpt.com/docs/non-interactive-mode).

Aşağıdaki örnek mevcut dizinde çalışır; stdin tüm prompttur. `-o` yalnız son mesajı, yönlendirme tüm olay akışını kaydeder:

```bash
codex exec \
  -s workspace-write \
  -c 'approval_policy="never"' \
  -c 'sandbox_workspace_write.network_access=false' \
  -c 'web_search="disabled"' \
  -c 'model_reasoning_effort="medium"' \
  --skip-git-repo-check \
  --json \
  -o worker-result.md \
  - > worker-events.jsonl <<'PROMPT'
Mevcut projeyi incele. İstenen değişikliği uygula ve mevcut testleri çalıştır.
Commit oluşturma. Sonuçta değişen dosyaları ve test sonuçlarını bildir.
PROMPT
```

Çağrı biçimi [exec referansı](https://learn.chatgpt.com/docs/developer-commands), stdin/çıktı davranışı [başsız çalışma belgesi](https://learn.chatgpt.com/docs/non-interactive-mode), ağ anahtarı [ayar referansı](https://learn.chatgpt.com/docs/config-file/config-reference) üzerinden doğrulandı.

Canlı arama isteyen güncel bir çağrı örneği:

```bash
codex --search exec \
  -s read-only \
  -c 'approval_policy="never"' \
  "Projenin kullandığı bağımlılığın resmî geçiş belgesini araştır."
```

`--search`, komutların genel ağ erişimini açmakla aynı ayar değildir. [Arama bayrağı](https://learn.chatgpt.com/docs/developer-commands), [ağ erişimi ayrımı](https://learn.chatgpt.com/docs/agent-approvals-security#network-access).

**`workspace-write`: ağ, ek kökler ve `.git`**

`network_access` varsayılan olarak kapalıdır; `writable_roots` mevcut çalışma alanına **ek** yazılabilir dizinler ekler. `.git` ve Git worktree’nin işaret ettiği gerçek Git dizini korunmuş salt okunur yollardır. Bu nedenle kaynak dosyalarını değiştirebilen işçinin `git commit` yapabilmesi ayrıca garanti edilmez. `approval_policy="never"` sandboxı kaldırmaz. [Ayar alanları](https://learn.chatgpt.com/docs/config-file/config-reference), [korunan yollar](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots).

**Güncel işçi profili — Codex 0.134.0+**

Dosya: `~/.codex/worker.config.toml`

```toml
approval_policy = "never"
sandbox_mode = "workspace-write"
model_reasoning_effort = "medium"
web_search = "disabled"

[sandbox_workspace_write]
network_access = false
writable_roots = []
```

```bash
codex exec --profile worker --json \
  "İstenen düzeltmeyi uygula, mevcut testleri çalıştır ve raporla."
```

Profil, temel `~/.codex/config.toml` üstüne katman olarak yüklenir. Model belirtilmediği için hesabın mevcut model seçimi kullanılır. **0.134.0+** için `[profiles.worker]` içine gömmeyin. [Resmî profil belgesi ve sürüm sınırı](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles).

**İstenen eski `[profiles]` biçimi — v0.77.0 kaynak koduyla doğrulandı**

Dosya: `~/.codex/config.toml`

```toml
[sandbox_workspace_write]
network_access = false
writable_roots = []

[profiles.worker]
approval_policy = "never"
sandbox_mode = "workspace-write"
model_reasoning_effort = "medium"
```

```bash
codex exec --profile worker --json \
  "Projeyi incele ve mevcut testleri çalıştır."
```

Bu örnekte sandbox alt tablosu kök düzeydedir; v0.77.0 `ConfigProfile` yapısı yalnız profilin desteklediği alanları taşır. [Profil yapısı](https://raw.githubusercontent.com/openai/codex/rust-v0.77.0/codex-rs/core/src/config/profile.rs), [profil yükleme ve örnek testler](https://raw.githubusercontent.com/openai/codex/rust-v0.77.0/codex-rs/core/src/config/mod.rs).

**3. OpenCode**

`opencode run` başsız çağrıdır; `--agent` ajanı seçer, `--format json` olay akışı üretir. `--auto`, açıkça reddedilmemiş izin isteklerini otomatik onaylar; dar bir komut izin listesi yerine geçmez. Bu bayraklar hem [V1 CLI](https://opencode.ai/docs/cli/) hem [V2 komut belgesinde](https://opencode.ai/v2/docs/cli/commands/) bulunuyor.

**İstenen V1 izin biçimi**

`permission.edit`, `edit/write/patch` işlemlerini; `permission.bash`, ayrıştırılmış shell komutlarını yönetir. Kurallarda son eşleşen kazanır. Aşağıdaki JSON, okuma ve iki Git inceleme komutu için örnektir. [V1 izinleri; son güncelleme 2026-10-23](https://opencode.ai/docs/permissions/).

`worker-local.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "llama-local/qwen-local",
  "provider": {
    "llama-local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Yerel llama.cpp",
      "options": {
        "baseURL": "http://127.0.0.1:8080/v1"
      },
      "models": {
        "qwen-local": {
          "name": "Yerel Qwen"
        }
      }
    }
  },
  "permission": {
    "*": "deny",
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "edit": "deny",
    "bash": {
      "*": "deny",
      "git status --short": "allow",
      "git diff --stat": "allow"
    }
  }
}
```

Özel sağlayıcı biçimi ve yerel llama-server bağlantısı [resmî sağlayıcı belgesinden](https://opencode.ai/docs/providers/) uyarlanmıştır.

```bash
OPENCODE_CONFIG="$PWD/worker-local.json" \
opencode run \
  --agent build \
  --model llama-local/qwen-local \
  --format json \
  "git status --short ve git diff --stat çalıştır; değişiklikleri özetle."
```

`--auto` gereken daha geniş bir işte kullanılabilir:

```bash
opencode run --auto --agent build "Mevcut testleri çalıştır."
```

İkinci çağrı, etkin ayarlardaki `ask` işlemlerini de otomatik onaylayabilir; ilk örneğin dar izin kapsamını temsil etmez. [CLI](https://opencode.ai/docs/cli/), [auto izin davranışı](https://opencode.ai/docs/permissions/).

**`OPENCODE_CONFIG` birleştirmesi**

V1’de bu dosya global ayarlardan sonra, proje ayarlarından önce yüklenir; diğer ayarların yerine geçmez. Dolayısıyla proje ayarları çatışan değerleri değiştirebilir. V2’de paylaşılan arka plan sunucusu kullanıldığından, çağrıya özel ortam için `run --standalone` resmî otomasyon örneğindeki seçenektir. [V1 öncelik sırası](https://opencode.ai/docs/config/), [V2 otomasyon](https://opencode.ai/v2/docs/cli/commands/).

**V2’nin yerel biçimi**

Yeni V2 dosyasında `provider→providers`, `permission→permissions`, `bash→shell` değişir. V2, desteklenen V1 alanlarını bellekte dönüştürebilir; geçiş zorunlu değildir. [Resmî geçiş belgesi](https://opencode.ai/v2/docs/migrate-v1/).

V2 için aynı yerel işçinin örneği:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "llama-local/qwen-local",
  "providers": {
    "llama-local": {
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "http://127.0.0.1:8080/v1"
      },
      "models": {
        "qwen-local": {
          "modelID": "qwen-local"
        }
      }
    }
  },
  "permissions": [
    { "action": "*", "resource": "*", "effect": "deny" },
    { "action": "read", "resource": "*", "effect": "allow" },
    { "action": "glob", "resource": "*", "effect": "allow" },
    { "action": "grep", "resource": "*", "effect": "allow" },
    { "action": "shell", "resource": "git status --short", "effect": "allow" },
    { "action": "shell", "resource": "git diff --stat", "effect": "allow" }
  ]
}
```

```bash
OPENCODE_CONFIG="$PWD/worker-local-v2.json" \
opencode run --standalone \
  --agent build \
  --model llama-local/qwen-local \
  --format json \
  "git status --short ve git diff --stat çalıştır; sonuçları özetle."
```

V2 sağlayıcı paketi ve `modelID` biçimi [sağlayıcı belgesinde](https://opencode.ai/v2/docs/providers/), sıralı izin dizisi [izin belgesinde](https://opencode.ai/v2/docs/permissions/) doğrulandı.

**llama-server kimliği ve “Model unavailable”**

Örneklerin önkoşulu: yerel sunucunun `qwen-local` kimliğiyle model sunmasıdır. Mevcut GGUF dosyanızın yolunu değiştirerek kullanılacak sunucu örneği:

```bash
llama-server \
  -m ./model.gguf \
  --alias qwen-local \
  --host 127.0.0.1 \
  --port 8080
```

`--alias`, API’nin model kimliğini belirler; alias yoksa kimlik model dosyası yolu olabilir. [llama.cpp resmî server kaynağı, `master`](https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md).

Kimlik zinciri şöyledir:

| Yer | Örnekteki değer |
|---|---|
| OpenCode sağlayıcı anahtarı | `llama-local` |
| OpenCode model haritası anahtarı | `qwen-local` |
| CLI seçimi | `llama-local/qwen-local` |
| Sunucuya gönderilen model | V2’de `modelID`: `qwen-local` |

`name` görüntüleme adıdır. `--model qwen-local` sağlayıcı önekini içermez. Ancak **“Model unavailable” yalnız biçim hatası demek değildir**: sağlayıcı pasif, model eksik/devre dışı veya keşif sonucu kaybolmuş olabilir. V2 özel alias seçerken `modelID` yerine model haritasının anahtarını ister. [V1 model kimliği](https://opencode.ai/docs/models/), [V2 hata açıklamaları](https://opencode.ai/v2/docs/providers/#errors).

**4. Claude Code**

`claude -p` başsız oturum açar ve çıktı üretir. Yeni CLI süreci bağımsız oturumdur; oturum içi alt ajan için `--agents` tanımı ve Agent aracı kullanılır. `--agent ad` ise tanımlı ajanı oturumun ana ajanı olarak seçer. [Başsız kullanım](https://code.claude.com/docs/en/headless), [alt ajanlar](https://code.claude.com/docs/en/sub-agents).

| Seçenek | Doğrulanan davranış |
|---|---|
| `--model` | `sonnet`, `opus`, `haiku` gibi alias veya tam model adı. |
| `--effort` | Oturuma özel; modele göre `low/medium/high/xhigh/max`, ayrıca `ultracode` seçeneği. |
| `--allowedTools` | Eşleşen çağrıları önceden onaylar; mevcut araçları sınırlamak için `--tools` kullanılır. |
| `--permission-mode` | `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`; ayrıca `manual` aliası. |
| `--max-turns` | Print modunda ajan turu sınırı; kota rezervasyonu değildir. |

Bayraklar [CLI referansında](https://code.claude.com/docs/en/cli-reference), effort/model ilişkisi [model ayarlarında](https://code.claude.com/docs/en/model-config) doğrulandı.

`dontAsk`, normalde onay isteyecek işlemleri reddeder; önceden izin verilen işlemler çalışabilir. `acceptEdits`, çalışma dizinindeki dosya düzenlemelerini ve bazı dosya sistemi komutlarını kabul eder. `auto` otomatik değerlendirmedir; işletim sistemi sandboxının yerine geçmez. [İzin modları](https://code.claude.com/docs/en/permissions).

Dar kapsamlı ayrı işçi:

```bash
claude -p \
  "git status --short ve git diff --stat çalıştır; değişiklikleri özetle." \
  --model sonnet \
  --effort medium \
  --tools "Read,Grep,Glob,Bash" \
  --allowedTools "Read,Grep,Glob,Bash(git status --short),Bash(git diff --stat)" \
  --permission-mode dontAsk \
  --max-turns 6 \
  --output-format json
```

Araç ön onayı ve kullanılabilir araç ayrımı [CLI referansına](https://code.claude.com/docs/en/cli-reference), başsız çağrı [programatik kullanım belgesine](https://code.claude.com/docs/en/headless) dayanır.

Oturum içi gerçek alt ajan örneği:

```bash
claude -p \
  "audit alt ajanını kullanarak kodu incele; raporunu bekle ve özetle." \
  --model sonnet \
  --effort medium \
  --permission-mode dontAsk \
  --tools "Read,Grep,Glob,Agent" \
  --allowedTools "Read,Grep,Glob,Agent" \
  --agents '{
    "audit": {
      "description": "Salt okunur kod incelemesi yapar.",
      "prompt": "Kodu incele. Dosya değiştirme. Bulguları dosya konumlarıyla bildir.",
      "tools": ["Read", "Grep", "Glob"],
      "model": "sonnet"
    }
  }' \
  --output-format json
```

`--agents` JSON nesnesi ve `-p` içinde alt ajan sonucunu bekleme davranışı resmî [alt ajan belgesinde](https://code.claude.com/docs/en/sub-agents) açıklanmıştır.

**Arka plan işi ayrımı:** Güncel Claude Code, `--bg` ile bağımsız arka plan oturumu açabiliyor; **`-p --bg` birleşimi reddediliyor**. Önceden güvenilmiş çalışma dizininde:

```bash
claude --bg \
  --model sonnet \
  --effort medium \
  --permission-mode dontAsk \
  --allowedTools "Read,Grep,Glob" \
  "Kod tabanını incele; dosya değiştirmeden bulguları raporla."
```

`claude -p` ise kendi başlattığı arka plan alt ajanlarını bekleyebilir; varsayılan sürekli boşta bekleme tavanı 10 dakikadır. [Bağımsız arka plan oturumları](https://code.claude.com/docs/en/agent-view#dispatch-an-agent-from-your-shell), [print modunda bekleme](https://code.claude.com/docs/en/headless).

**Oturum ve kota etkisi**

Alt ajanlar kendi model isteklerini gönderir ve ana oturumla aynı kullanım sınırlarına sayılır. Max için yeni süreç/oturum açmak yeni abonelik kotası oluşturmaz: beş saatlik ve haftalık sınırlar Claude ile Claude Code arasında paylaşılır. `--max-budget-usd` API maliyeti tahminidir; Max’in kalan abonelik kotası için kesin bir tavan değildir. [Alt ajan kullanımı](https://code.claude.com/docs/en/sub-agents), [resmî Pro/Max açıklaması](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan), [maliyet ölçümü](https://code.claude.com/docs/en/costs).

**Koordinatör için bu denetimden çıkan uygulama kararı**

Aşağıdakiler belgelerden türetilmiş tasarım önerisidir:

- **İzin ve iş başarısını ayrı ölçün.** Özellikle agy’de `exit=0`, istenen komutun çalıştığını kanıtlamaz; araç sonucu ve reddetme bildirimini denetleyin. [agy headless](https://antigravity.google/docs/cli/headless/).
- **Sürümü iş kaydına ekleyin.** Codex profil geçişi ve OpenCode şema farkları nedeniyle tek yapılandırmayı bütün sürümlere göndermeyin. [Codex](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles), [OpenCode](https://opencode.ai/v2/docs/migrate-v1/).
- **Token kullanımını kalan kota saymayın.** agy `/usage` model kotasını backend’den yeniler; olay akışındaki `usage` tüketimi gösterir. Belgelenmiş, tüm CLI’ları kapsayan ortak kota API’si **doğrulanamadı**. [agy kota görünümü](https://antigravity.google/docs/cli/commands/usage), [akış sayaçları](https://antigravity.google/docs/cli/headless/).
- **Max işçilerini aynı havuzdan bütçeleyin.** Paralel Claude oturumlarını ayrı kota havuzları olarak planlamayın. [Resmî Max sınırları](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan).

Örnekler abonelik girişlerini resmî CLI içinde tutar; OpenCode özel uç noktası yalnız yerel llama.cpp içindir. Abonelik tokenı çıkarma veya başka uç noktaya aktarma yöntemi kullanılmamıştır.