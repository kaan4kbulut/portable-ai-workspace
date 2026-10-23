---
katman: programlar
surum: 1.4.6
son_kontrol: 2026-10-23
kaynaklar: [https://antigravity.google, https://github.com/google-antigravity/antigravity-cli]
baglar: [../README.md, ../../10-donanim/monster/README.md, ../claude-code/README.md, ../cc-safety-net/README.md, ../mcp/README.md]
---

# Google Antigravity CLI (`agy`)

## Nedir
Google Antigravity çoklu-ajan geliştirme platformunun terminal arayüzüdür (`agy 1.4.6`).
Aynı anda birden fazla alt ajan, geniş bağlamlı araştırma ve yerleşik terminal sandbox'ı ile çalışır.

## Atölyedeki rolü
- **Geniş kotalı araştırma, haritalama ve yardımcı üretim aracı:** Google AI Ultra aboneliğinin geniş kotası sayesinde büyük kod tabanı taramaları, salt okunur haritalama (`agy -p --mode plan --sandbox`) ve paralel belge/yapı işlerinde kullanılır (`00-cekirdek/AGENTS.md`, `60-hafiza/kararlar/KARARLAR.md`).
- Çekirdek ajan tarafından alt görevlerde hedef klasöre `cd` yapılarak çağrılır; masaüstü Antigravity / IDE uygulamaları kaldırılmıştır, yalnızca `agy` CLI kullanılır.

## Kurulum ve giriş
- Kurulum betiği: `bash 20-sistem/kurulum/araclar/agy.sh` (henüz doğrulanmış sabit genel kurucu URL'si olmadığından kurulu sürümü denetler; eksikse elle kurulup `agy install` çalıştırılır).
- Giriş yalnızca aracın kendi komutuyla (`agy` etkileşimli oturumunda Google hesabıyla) yapılır; güncelleme `agy update`, sürüm notları `agy changelog` ile görülür.
- `~/.gemini/` altındaki kimlik ve oturum dosyaları asla okunmaz, kopyalanmaz veya proxy/ağ geçidine bağlanmaz.

## Etkileşimsiz çağırma
`agy --help` ve `60-hafiza/ogrenilenler/agy.md` ile bu makinede doğrulanan bayraklar:
```bash
agy -p --mode plan --sandbox "Salt okunur analiz ve haritalama istemi"
agy -p --output-format stream-json --dangerously-skip-permissions --sandbox "istem"
agy -p --output-format json --json-schema schema.json --print-timeout 20m "istem"
```
- Seçenekler: `-p`/`--print`/`--prompt` (etkileşimsiz tek tur), `--output-format <text|json|stream-json>`, `--input-format <text|stream-json>`, `--json-schema <json|dosya>`, `--mode <accept-edits|auto|plan>`, `--sandbox` (terminal kısıtlamalı sandbox), `--dangerously-skip-permissions`, `--print-timeout <süre>` (Go süre biçimi zorunlu: `1400s`, `20m`; birimsiz sayı çıkış kodu 2 ile hata verir), `--model <ad>`, `--effort <low|medium|high|xhigh|max>`, `--agent <ad>`, `--add-dir <dizin>`, `--disable-slash-commands`.
- Çalışma dizini bayrağı yoktur; hedef dizine `cd` ile geçilerek veya `--add-dir` eklenerek çağrılır.

## Okuduğu dosyalar
- **Kurallar:** Proje kökünde ve üst dizinlerde `AGENTS.md`, `GEMINI.md`, `.agents/rules/*.md`; kullanıcı genelinde `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md` ve `~/.gemini/config/rules/*.md`.
- **Beceriler ve eklentiler:** Proje içinde `.agents/skills/<ad>/SKILL.md`, kullanıcı genelinde `~/.gemini/antigravity-cli/skills/` ve `~/.gemini/antigravity-cli/plugins/`.
- **Ayarlar ve MCP:** `~/.gemini/antigravity-cli/settings.json`, proje içi `.agents/mcp_config.json` ve global `~/.gemini/config/mcp_config.json` (`kur.sh --genel` ile `30-programlar/agy/genel/mcp_config.json`'a bağlanır).
- **Makine-yerel (depoya girmez):** `~/.gemini/{antigravity/,antigravity-cli/,config/{projects,node_modules,config.json}}` (`settings.json` deny listesinde korumalıdır).

## Dikkat
- **Kota:** Google AI Ultra aboneliği **geniştir** (Claude Max 5x ile birlikte ana kapasiteyi oluşturur).
- **ToS:** Google, proxy/havuz kullanan Gemini ve Antigravity hesaplarını toplu askıya almaktadır; yalnızca resmi `agy` CLI kendi girişiyle kullanılır.
- **TURBO / Sandbox kipi:** Etkileşimli kullanımda TURBO kipi (sandbox kapalı, onaysız komut) kullanıcı kararıyla açıktır; ancak otomasyon çağrılarında `--sandbox` (ve salt okunur işlerde `--mode plan`) kullanılır. Sunucuya (LENOVO) taşınırken izin kipi yeniden değerlendirilecektir.

## Eksikler
- `20-sistem/kurulum/araclar/agy.sh` için doğrulanmış, katılımsız çalışan resmi indirme/kurulum URL'si eklenecek.
- `kur.sh --genel` içinde `~/.gemini/config/rules/` veya `~/.gemini/AGENTS.md` bağlantısının eklenmesi (Plan Aşama C).
