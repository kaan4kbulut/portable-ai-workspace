Kaynak denetimi: Bu rapor **2026-10-24** tarihinde yalnızca salt-okunur yerel belge incelemesi ([SKILL.md], [cli.md], [sdk.md]) ve canlı web/GitHub araştırması ile üretilmiştir; hiçbir kabuk komutu çalıştırılmamış ve hiçbir dosya yazılmamıştır. İddialar doğrudan GitHub depo/issue URL'leri ve resmi belgelerle eşleştirilmiş; genel indekslerde tam tarih/sürüm veya anlık açık/kapalı durumu kesinleştirilemeyen alanlar uydurulmayıp açıkça **`doğrulanamadı`** olarak işaretlenmiştir.
Yazan: agy (Gemini 4 Argon high, plan kipi) · doğrulayan: Claude (kısmi) · tarih: 2026-10-24

---

# KONU A — Açık Kaynak Kodlama CLI Orkestrasyon Örnekleri, Başsız (Headless) Çalışma Arızaları ve Tasarım Kalıpları

**Hedef Sistem Bağlamı:**
* **Donanım & İS:** Tek geliştirici makinesi — Ubuntu Linux, NVIDIA RTX 5070 Ti (12 GB VRAM).
* **Çekirdek Koordinatör:** Claude Code (`claude`, Max aboneliği).
* **İşçi (Worker) Havuzu:**
  1. **OpenAI Codex CLI** (`codex exec`, ChatGPT Plus aboneliği)
  2. **Google Antigravity CLI** (`agy -p` ve [Antigravity Python SDK](https://github.com/google-antigravity/antigravity-sdk-python), AI Ultra aboneliği: Gemini modelleri + ayrı kotalı Claude/GPT modelleri)
  3. **OpenCode CLI** (`opencode run`, ücretsiz/free-tier modeller)
  4. **Yerel Çıkarım** (`llama.cpp` sunucusu üzerinde Qwen3.5 4B/9B yoğun modeller ve Qwen3.6-35B-A3B MoE modeli)
* **Uyumluluk Sınırı (ToS):** Tüm abonelikler yalnızca kendi resmi CLI/SDK ikilileri üzerinden çağrılır. OAuth token çıkaran, ters vekil (reverse proxy) kuran veya istemci imzası (header/wire-format) taklit eden araçlar **kapsam dışıdır**.

---

## 1. Çoklu Kodlama CLI'ını Çalıştıran ve İş Dağıtan Projeler

Aşağıda, birden fazla kodlama CLI'ını (`claude`, `codex`, `gemini`/`agy`, `opencode`, `aider`) paralel veya başsız (headless) olarak çalıştıran **12 temel proje** ve araştırmada tespit edilen **7 ek açık kaynak proje** (toplam 19 proje) 8 teknik boyutta incelenmiştir.

### 1.1. İstenen 12 Temel Projenin Detaylı İncelemesi

#### 1) `claude-squad` (`smtg-ai/claude-squad`)
* **GitHub URL:** https://github.com/smtg-ai/claude-squad (Dil: Go, Lisans: AGPL-3.0)
* **Yıldız / Son Commit Tarihi:** ~7.8k–8.6k yıldız (Ekim 2026 itibarıyla); 2026 içinde aktif TUI ve kısa terminal penceresi düzeltmeleri mevcuttur, tam son commit günü `doğrulanamadı`.
* **Nasıl Çalıştırıyor:** Her ajan (`claude`, `codex`, `gemini`, `opencode`, `aider`) için ayrı bir `git worktree` + adanmış dal (branch) açar ve bunları arka planda ayrı `tmux` oturumları içinde çalıştırır.
* **İzin / Sandbox Modeli:** Kendi işletim sistemi sandbox'ı yoktur; alt CLI'ların kendi izin bayraklarını veya otomatik onay ("yolo" / auto-accept) modlarını `~/.claude-squad/config.json` üzerinden geçirir.
* **Zaman Aşımı / Takılma Tespiti:** `tmux` oturumu başlatılırken sabit başlangıç zaman aşımı (`failed to start new session: timed out waiting for tmux session`) vardır; ancak görev ortasında anlamsal takılma (hang) için otomatik öldürme/yeniden başlatma mekanizması `doğrulanamadı`.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** Yok (`doğrulanamadı`). Hata durumunda operatörün TUI üzerinden müdahalesini bekler.
* **Sonuç Doğrulama (Test / Diff):** TUI içinde yerleşik bir **Diff sekmesi** (`diff tab`) ile worktree'deki değişiklikleri canlı inceler; otomatik test koşumu orkestratör katmanında zorunlu değildir.
* **Kota / Ücret Takibi:** Yerleşik token/kota sayacı yoktur (`doğrulanamadı`).

#### 2) `vibe-kanban` (`BloopAI/vibe-kanban`)
* **GitHub URL:** https://github.com/BloopAI/vibe-kanban (Dil: Rust + TypeScript/React, Lisans: Apache-2.0)
* **Yıldız / Son Commit Tarihi:** ~27.5k yıldız (Ekim 2026 itibarıyla); 2026 boyunca aktif (PR `#3248`, `#3281`, Issue `#3417`).
* **Nasıl Çalıştırıyor:** Kanban kartındaki her görev için izole bir `git worktree`, ayrı dal, yerleşik terminal süreci ve geliştirme sunucusu (dev server) başlatır; `claude -p` / Agent SDK, `codex`, `gemini`, `opencode` ve `amp` işçilerini alt süreç olarak sürer.
* **İzin / Sandbox Modeli:** İşçileri başsız/programatik çalıştırdığı için ilgili CLI'ların otomatik onay parametrelerini kullanır; izole ortam olarak yerel worktree (veya uzak relay) kullanır.
* **Zaman Aşımı / Takılma Tespiti:** Uzak relay ve akış katmanında Yamux pencere boyutu ve yazma zaman aşımı (`write timeout`) kontrolleri bulunur; yerel alt süreçlerde akış kesilmesi ve bayat veri (stale-data) yakalama mantığı vardır.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** Görev planlamasında `ai/plans/...` dosyası bulunamazsa standart görev açıklamasına geri döner (plan fallback); ancak bir LLM sağlayıcısı 429 verdiğinde otomatik başka CLI'a geçiş yaptığı `doğrulanamadı`.
* **Sonuç Doğrulama (Test / Diff):** 300+ dosyalı PR'ları destekleyen yüksek performanslı yerleşik Diff görüntüleyici (Pierre Virtualizer, PR `#3248`), canlı diff akışı düzeltme (`#3281`) ve gömülü tarayıcı önizlemesi sunar.
* **Kota / Ücret Takibi:** Doğrudan kota yönlendiricisi yoktur; hatta `claude -p` / SDK kullanımının Anthropic tarafında abonelik havuzundan ayrılıp kredi tüketmesi nedeniyle toplulukta kota tartışmalarına (`BloopAI/vibe-kanban#3417`) konu olmuştur.

#### 3) `claude-flow` / `ruflo` (`ruvnet/claude-flow` $\rightarrow$ `ruvnet/ruflo`)
* **GitHub URL:** https://github.com/ruvnet/claude-flow ve https://github.com/ruvnet/ruflo (Dil: TypeScript/Node.js)
* **Yıldız / Son Commit Tarihi:** `ruvnet/ruflo` çatısı altında ~74k yıldız (v3/v4 serisi, 2026 içinde günlük commitlerle aktif).
* **Nasıl Çalıştırıyor:** MCP (Model Context Protocol) araçları, `npx claude-flow` / `npx ruflo` CLI sarmalayıcıları ve alt süreçlerle hiyerarşik/mesh/yıldız topolojisinde çoklu ajan sürüleri (swarm) başlatır; Claude Code ve Codex CLI arka uçlarını destekler.
* **İzin / Sandbox Modeli:** Alt ajanlara görev dağıtırken CLI bayraklarını (`--no-color`, `--no-browser` vb.) ve Claude Code hook/izin yapılandırmalarını geçirir.
* **Zaman Aşımı / Takılma Tespiti:** SQLite/vektör bellek (HNSW) durum kilitlerini ve işçi durumlarını izleyen kanca (hook) mekanizmaları vardır.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** Çoklu model yönlendirme ve özyinelemeli (recursive) hata düzeltme döngüleri mevcuttur.
* **Sonuç Doğrulama (Test / Diff):** Özyinelemeli kod-test döngüleri ve modüler GitHub PR/sürüm doğrulama yetenekleri (`github-release-management`) içerir.
* **Kota / Ücret Takibi:** Oturum durum çubuğu (statusline hooks) ve bellek katmanında token/maliyet izleme bileşenleri bulunur.

#### 4) `oh-my-opencode` (`code-yeongyu/oh-my-opencode`) ⚠️ **[ToS Riski Notu İçerir]**
* **GitHub URL:** https://github.com/code-yeongyu/oh-my-opencode (Dil: TypeScript, OpenCode eklentisi/koşum takımı)
* **Yıldız / Son Commit Tarihi:** ~35k–37k+ yıldız (2026 itibarıyla aktif).
* **Nasıl Çalıştırıyor:** OpenCode içinde *Sisyphus* (ana orkestratör), *Prometheus* (planlayıcı) ve *Oracle* (mimari/hata ayıklama) gibi uzmanlaşmış alt ajanları arka plan görevleri ve LSP/AST araçlarıyla çalıştırır.
* **İzin / Sandbox Modeli:** OpenCode'un kendi izin ve araç çalıştırma katmanını kullanır.
* **Zaman Aşımı / Takılma Tespiti:** Uzun süren isteklerde `AbortError` tabanlı zaman aşımı yakalama ve kesilen oturumları kurtarma mantığına sahiptir.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** **En güçlü olduğu alandır.** `User Override -> Provider Fallback -> System Default` öncelik zinciriyle bir model kota (`429`) veya zaman aşımı hatası verdiğinde otomatik olarak ikincil modele/sağlayıcıya (Claude, GPT, Gemini, Kimi, GLM) düşer.
* **Sonuç Doğrulama (Test / Diff):** Yerleşik LSP (Language Server Protocol) ve AST araçlarıyla üretilen kodun sözdizimsel/tip doğrulamasını anında yapar.
* **Kota / Ücret Takibi:** `429` hız sınırlarını ve sağlayıcı hatalarını yakalayıp yedek zincire devreder.
* **⚠️ ToS Durumu:** Projenin kendisi bir orkestrasyon eklentisidir; **ancak** ekosisteminde sıkça birlikte kullanılan `opencode-antigravity-auth` (`antigravity-accounts.json` ile çoklu OAuth hesap rotasyonu) ve üçüncü taraf Claude OAuth imza taklit eklentileri **Anthropic ve Google ToS'unu doğrudan ihlal etmektedir**. Bizim sistemimizde yalnızca model yedekleme (fallback) mimarisi örnek alınmalı, OAuth eklentileri kesinlikle kullanılmamalıdır.

#### 5) `just-every/code` (*Every Code*)
* **GitHub URL:** https://github.com/just-every/code (Dil: Rust/TypeScript — OpenAI Codex CLI çatalı, Lisans: Apache-2.0)
* **Yıldız / Son Commit Tarihi:** ~4.0k yıldız (2026 itibarıyla aktif).
* **Nasıl Çalıştırıyor:** OpenAI Codex CLI tabanlı olup arka planda otomatik inceleme ("Auto Review") ve çoklu ajan (OpenAI, Claude, Gemini) görevleri için izole `git worktree` ve alt süreçler başlatır.
* **İzin / Sandbox Modeli:** Codex CLI'ın sandbox mimarisini miras alır; arka plan doğrulama turlarında ana çalışma dizinini koruyan yama koşum takımı (patch harness) kullanır.
* **Zaman Aşımı / Takılma Tespiti:** Arka plan ajan turlarında ve model yanıtlarında katı yürütme zaman aşımı (strict execution timeout) uygular.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** Bir ajan turu veya doğrulama adımı zaman aşımına uğradığında daha güvenli bir model yapılandırmasına düşer (fallback), yama serisini yeniden temellendirir (rebase) veya ana dalı korumak için arka plan turunu iptal eder.
* **Sonuç Doğrulama (Test / Diff):** Değişiklikleri doğrudan ana dala yazmak yerine hayalet/arka plan commit'leri (ghost commits), doğrulama kontrolleri ve yerleşik tarayıcı entegrasyonu ile test eder.
* **Kota / Ücret Takibi:** Çoklu sağlayıcı yönlendirmesi vardır; ayrıntılı abonelik kota sayacı `doğrulanamadı`.

#### 6) `agent-of-empires` (`njbrake/agent-of-empires` / `agent-of-empires/agent-of-empires`)
* **GitHub URL:** https://github.com/njbrake/agent-of-empires (veya https://github.com/agent-of-empires/agent-of-empires, Dil: Rust)
* **Yıldız / Son Commit Tarihi:** ~2.4k+ yıldız (2026 itibarıyla aktif).
* **Nasıl Çalıştırıyor:** Claude Code, OpenCode, Codex CLI, Gemini CLI, Mistral Vibe ve Copilot CLI ajanlarını her biri kendi `git worktree` dizininde ve kalıcı `tmux` oturumu içinde olacak şekilde başlatır; TUI ve Web panosu sunar.
* **İzin / Sandbox Modeli:** Dosya sistemi izolasyonu için isteğe bağlı **Docker, Podman veya Apple Containers** sarmalayıcılarını destekler.
* **Zaman Aşımı / Takılma Tespiti:** Ajan durumlarını (`idle`, `running`, `waiting for input`) gerçek zamanlı izler; otomatik zaman aşımıyla süreç öldürme detayı `doğrulanamadı`.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** Yok (`doğrulanamadı`).
* **Sonuç Doğrulama (Test / Diff):** TUI ve web panosu üzerinden git diff incelemesi ve terminal çıktısı denetimi sağlar.
* **Kota / Ücret Takibi:** `doğrulanamadı`.

#### 7) `conductor` (Melty Labs — `conductor.build`)
* **GitHub URL:** Sürüm takipçisi: https://github.com/meltylabs/conductor-releases — **Not:** Uygulamanın kendisi (https://www.conductor.build) **kapalı kaynaklı (proprietary)** macOS uygulamasıdır.
* **Yıldız / Son Commit Tarihi:** Ana kaynak kodu kapalı olduğu için GitHub yıldızı uygulanamaz (`doğrulanamadı`).
* **Nasıl Çalıştırıyor:** Claude Code, Codex ve Cursor ajanlarını yerel makinede her görev için otomatik `git worktree add` çalıştırarak ayrı dal ve dizinlerde paralel alt süreçler halinde yönetir.
* **İzin / Sandbox Modeli:** Kullanıcının kendi yerel CLI aboneliklerini ("Bring Your Own Subscription") ve çalışma alanı izinlerini kullanır.
* **Zaman Aşımı / Takılma Tespiti, Yedek Model, Doğrulama, Kota:** Görsel diff inceleme ve PR açma arayüzü vardır; kapalı kaynak olduğu için iç zaman aşımı ve yedekleme algoritmaları `doğrulanamadı`.

#### 8) `terragon` (`terragon-labs/terragon-oss`)
* **GitHub URL:** https://github.com/terragon-labs/terragon-oss (Şubat 2026'da barındırılan bulut hizmeti kapatılıp açık kaynak yapıldı)
* **Yıldız / Son Commit Tarihi:** ~261 yıldız (Şubat 2026 sonrası açık kaynak sürümü).
* **Nasıl Çalıştırıyor:** Claude Code ve Codex gibi CLI araçlarını arka plan görevleri olarak izole konteyner/sandbox ortamlarında ve ayrı Git dallarında/worktree'lerinde çalıştırır.
* **İzin / Sandbox Modeli:** Tam **Docker / bulut sandbox** izolasyonu; ajan kabuk komutlarını, paket kurulumlarını ve testleri ana makineden izole yürütür.
* **Zaman Aşımı / Takılma Tespiti:** Arka plan ajanlarının sonsuz test döngülerinde veya yanıt vermeyen kabuk komutlarında asılı kalmasını önlemek için sandbox çalışma süresi zaman aşımı (runtime window timeout) uygular.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** `doğrulanamadı`.
* **Sonuç Doğrulama (Test / Diff):** Otomatik derleme/test çalıştırma, çalışma alanı kontrol noktası (checkpoint) alma ve otomatik PR/diff oluşturma.
* **Kota / Ücret Takibi:** Kullanıcının kendi abonelik/API kimlik bilgilerini sandbox içine bağlar; ayrıntılı kota sayacı `doğrulanamadı`.

#### 9) `sculptor` (`imbue-ai/sculptor`)
* **GitHub URL:** https://github.com/imbue-ai/sculptor (Geliştirici: Imbue)
* **Yıldız / Son Commit Tarihi:** ~240 yıldız (2026 itibarıyla aktif).
* **Nasıl Çalıştırıyor:** Başta Claude Code olmak üzere paralel kodlama ajanlarını yerel makinede doğrudan çalıştırmak yerine her birini ayrı bir **Docker konteyneri** içinde başlatır ve "Pairing Mode" ile yerel IDE'ye çift yönlü senkronize eder.
* **İzin / Sandbox Modeli:** Konteyner tabanlı tam izolasyon; yanlışlıkla dosya silme veya izin çakışması riskini ortadan kaldırır.
* **Zaman Aşımı / Takılma Tespiti:** `doğrulanamadı`.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** `doğrulanamadı`.
* **Sonuç Doğrulama (Test / Diff):** Yerleşik ajan iş akışları (ör. `/sculptor-workflow:fix-bug` ile önce başarısız testi yazıp sonra düzeltmeyi doğrulama), konteyner içi test koşumu ve otomatik birleştirme çakışması (merge conflict) çözümü sunar.
* **Kota / Ücret Takibi:** `doğrulanamadı`.

#### 10) `ccmanager` (`kbwo/ccmanager`)
* **GitHub URL:** https://github.com/kbwo/ccmanager (Dil: TypeScript)
* **Yıldız / Son Commit Tarihi:** ~1.3k yıldız (2026 itibarıyla `main` dalında aktif).
* **Nasıl Çalıştırıyor:** `tmux` bağımlılığı **olmadan** kendi iç süreç/PTY yönetimiyle Claude Code, Gemini CLI, Codex CLI, Cursor Agent, Copilot CLI, Cline ve OpenCode oturumlarını ayrı `git worktree` dizinlerinde çalıştırır.
* **İzin / Sandbox Modeli:** Proje bazlı `.ccmanager.json` önayarları ile alt CLI'lara komut satırı bayraklarını geçirir.
* **Zaman Aşımı / Takılma Tespiti:** Oturum durumunu (`Waiting`, `Busy`, `Idle`) canlı izler ve durum değiştiğinde kancalar (hooks) / masaüstü bildirimleri tetikler.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** Yok (`doğrulanamadı`).
* **Sonuç Doğrulama (Test / Diff) & Kota Takibi:** Worktree yaşam döngüsü yönetimi sunar; yerleşik test/kota motoru `doğrulanamadı`.

#### 11) `uzi` (`devflowinc/uzi`)
* **GitHub URL:** https://github.com/devflowinc/uzi (Dil: Go)
* **Yıldız / Son Commit Tarihi:** ~580+ yıldız; son commit tarihi `doğrulanamadı`.
* **Nasıl Çalıştırıyor:** `uzi prompt --agents claude:3,codex:2 "..."` sözdizimiyle aynı komutu birden fazla CLI'a ve kopyaya dağıtır; her ajan için otomatik `git worktree`, ayrı `tmux` oturumu ve dinamik port aralığı (`$PORT`) ile ayrı geliştirme sunucusu başlatır.
* **İzin / Sandbox Modeli:** `uzi auto` komutu ile ajanların etkileşimli onay istemlerini (confirmations) otomatik onaylar.
* **Zaman Aşımı / Takılma Tespiti:** `uzi ls -w` ile canlı izleme ve `uzi kill` ile toplu sonlandırma sunar; otomatik zaman aşımı `doğrulanamadı`.
* **Başarısızlıkta Yedek Modele Geçiş (Fallback):** Yok; ancak aynı görevi aynı anda hem Claude hem Codex'e koşturarak ("N-versiyon programlama" / rekabetçi yürütme) tek model başarısızlığını maskeler.
* **Sonuç Doğrulama (Test / Diff):** Her worktree'de ayrı portta çalışan canlı dev server ve `uzi checkpoint` ile commit/birleştirme doğrulaması sağlar.
* **Kota / Ücret Takibi:** Yok (`doğrulanamadı`).

#### 12) `crystal` (`stravu/crystal` $\rightarrow$ Nimbalyst)
* **GitHub URL:** https://github.com/stravu/crystal (Nimbalyst'e evrildiği için orijinal depo arşivlenmiştir/deprecated)
* **Yıldız / Son Commit Tarihi:** ~3.1k yıldız (Arşivlenmiş/deprecated; geliştirme `nimbalyst.com` altında devam etmektedir).
* **Nasıl Çalıştırıyor:** Claude Code ve Codex oturumlarını izole `git worktree` dizinlerinde paralel çalıştıran masaüstü GUI uygulaması.
* **İzin / Sandbox Modeli, Zaman Aşımı, Yedek Model, Doğrulama, Kota:** Farklı istem (prompt) stratejilerini paralel worktree'lerde koşturup yan yana diff karşılaştırması yaparak kazanan çözümü seçme kalıbını popülerleştirmiştir; otomatik kota/zaman aşımı detayları `doğrulanamadı`.

---

### 1.2. Araştırmada Bulunan Ek Açık Kaynak Orkestrasyon Projeleri

| Proje ve GitHub URL | Yıldız / Durum (2026) | Çalıştırma & İzolasyon Mimarisi | Öne Çıkan Doğrulama / Orkestrasyon Özelliği |
| :--- | :--- | :--- | :--- |
| **Gas Town** ([`gastownhall/gastown`](https://github.com/gastownhall/gastown) / `steveyegge/gastown`) | ~15.9k–17.8k yıldız, aktif | `tmux` + `git worktree` + **Beads** (Git destekli görev veri düzlemi). 20–30 ajanı paralel yönetir. | **Roller:** *Mayor* (koordinatör), *Polecats* (geçici işçiler), *Witness* (yaşam döngüsü/takılma izleyicisi), *Refinery* (birleştirme kuyruğu / merge queue). |
| **Superset** ([`superset-sh/superset`](https://github.com/superset-sh/superset)) | ~15.5k yıldız, aktif | Yerel-öncelikli masaüstü/CLI + her ajan için izole `git worktree` (10–100+ paralel ajan). | Claude ve Codex'in kendi çalışma alanlarını yönetmesi için yerleşik **MCP sunucusu**, TypeScript SDK, yama/test incelemesi. |
| **Workmux** ([`raine/workmux`](https://github.com/raine/workmux)) | ~2.9k yıldız, aktif | `git worktree` ile `tmux` (veya WezTerm/Zellij/Kitty) pencerelerini birebir eşler. | Sıfır sürtünmeli yaşam döngüsü: `workmux merge`, `--rebase`, `--squash` ile ajan işini doğrular, birleştirir ve worktree/tmux penceresini otomatik temizler. |
| **Agent Deck** ([`asheshgoplani/agent-deck`](https://github.com/asheshgoplani/agent-deck)) | v1.x aktif (Go / Bubble Tea) | Claude, Gemini, OpenCode ve Codex için `tmux` (`agentdeck_*`) + `git worktree` yöneticisi. | Worktree oluşturma/yıkma kancaları (setup/destruction hooks), alt ajan ve MCP bağlantısı yönetimi. |
| **Auto-Claude / Aperant** ([`AndyMik90/Auto-Claude`](https://github.com/AndyMik90/Auto-Claude)) | Aktif (Python + Electron) | İzole `git worktree` üzerinde çok oturumlu otonom boru hattı. | **4 Aşamalı Boru Hattı:** `Spec -> Planning -> Coding -> QA Validation` (kendi kendini düzelten QA doğrulama döngüsü ve Graphiti bellek katmanı). |
| **Parallel Code** ([`johannesjo/parallel-code`](https://github.com/johannesjo/parallel-code)) | Aktif (TypeScript / SolidJS) | Claude Code, Codex CLI, Gemini CLI ve Copilot CLI için ayrı `git worktree` + otomatik `node_modules` sembolik bağı (symlink). | Worktree başına bağımlılık yeniden kurma maliyetini symlink ile çözer; diff inceleme arayüzü sunar. |
| **Mux / Xum** ([`coder/mux`](https://github.com/coder/mux) $\rightarrow$ `coder/xum`) | Aktif (Coder tarafından) | Yerel worktree, uzak SSH ve Coder çalışma alanlarında çoklu ajan çoğullayıcı (multiplexer). | Yerleşik **maliyet/token takibi**, git sapma (divergence) görselleştirmesi, Claude/GPT/yerel model desteği. |

---

### 1.3. ⚠️ ToS Açısından Riskli ve Kapsam Dışı Bırakılması Gereken Projeler

Aşağıdaki projeler veya eklentiler açık kaynak ekosisteminde popüler olsa da **Anthropic ve Google Hizmet Şartları'nı (ToS) ihlal ettikleri** ve hesap kapatma (ban/suspension) dalgalarına yol açtıkları için sistemimizde **kesinlikle kullanılmamalıdır**:

1. **`router-for-me/CLIProxyAPI`** (https://github.com/router-for-me/CLIProxyAPI): Resmi CLI araçlarından (Claude Code, Gemini/Antigravity, OpenAI Codex) kullanıcı OAuth token'larını çıkarıp bunları yerel bir OpenAI/Anthropic uyumlu HTTP API uç noktası olarak yeniden yayınlar ve resmi istemci başlıklarını (`user-agent`, `anthropic-beta`, alan sıralaması) taklit eder.
2. **`musistudio/claude-code-router`** (https://github.com/musistudio/claude-code-router): Claude Code isteklerini araya girerek (proxy) başka uç noktalara yönlendiren veya OAuth kimlik bilgilerini üçüncü taraf istemcilere taşıyan yönlendirici.
3. **`opencode-antigravity-auth` ve Benzeri OAuth Rotasyon Eklentileri:** Google Antigravity veya Claude Max abonelik OAuth oturumlarını dışarı çıkarıp `opencode` gibi üçüncü taraf koşum takımlarında çoklu hesap rotasyonuyla (`antigravity-accounts.json`) kullanan eklentiler. Anthropic ve Google bu tür "OAuth passthrough / istemci taklidi" trafiğini aktif olarak engellemekte ve hesapları askıya almaktadır.

---

## 2. Başsız (Headless) Kullanımda Bilinen CLI Sorunları ve GitHub Issue Analizi

Koordinatörün (`claude`) alt işçileri (`codex exec`, `agy -p` / `gemini -p`, `opencode run`, `claude -p`) başsız modda alt süreç (subprocess) olarak çağırdığında karşılaşılan **5 kritik arıza sınıfı** ve GitHub issue kayıtları aşağıdadır:

### 2.1. `codex exec` Stdin Bekleme ve Sonsuz Asılı Kalma (Hang) Sorunu

* **Kök Neden:** `codex exec "<prompt>"` çağrıldığında, Codex CLI standart girdinin (`stdin`) bir TTY olup olmadığını kontrol eder. Eğer üst süreç (örneğin Claude Code'un Bash aracı, Node.js `child_process.spawn` veya Python `subprocess.Popen`) `stdin` için bir boru (pipe) açmış ancak içine hiçbir şey yazmayıp `EOF` da göndermemişse, `codex exec` ek girdi geleceğini varsayarak `"Reading additional input from stdin..."` mesajında **%0 CPU kullanımıyla sonsuza kadar kilitlenir (deadlock)**.
* **İlgili GitHub Issue'ları:**
  * **https://github.com/openai/codex/issues/20919** — *`codex exec '<prompt>'` hangs indefinitely when stdin is a non-TTY pipe with no writer* (Durum: Açık / bilinen davranış olarak takip ediliyor; `TERM=dumb` ve borulu alt süreç ortamlarında deterministik kilitlenme).
  * **https://github.com/openai/codex/issues/27019** — *Bug: hangs at 'Reading additional input from stdin...' in non-TTY environments (`TERM=dumb`)* (Durum: `#20919` ile ilişkili/kopya olarak raporlandı).
  * **https://github.com/openai/codex/issues/1045** — Otomasyon ve MCP sarmalayıcılarında `codex exec` stdin bloklanması.
* **Önerilen Geçici Çözüm (Workaround):**
  * **Kabuk (Shell) Çağrılarında:** Standart girdiyi açıkça `/dev/null`'a yönlendirerek anında `EOF` almasını sağlayın:
    ```bash
    codex exec --full-auto "Görev istemi" < /dev/null
    ```
  * **Programatik Alt Süreçlerde (Python / Node.js):** `stdin=subprocess.DEVNULL` (Python) veya `stdio: ['ignore', 'pipe', 'pipe']` (Node.js) kullanın ya da süreç başlar başlamaz `child.stdin.close()` çağırın.

### 2.2. `codex` Sandbox'ta `.git` Salt Okunur (Read-Only) ve Worktree `index.lock` Hatası

* **Kök Neden:**
  1. **Standart Depolarda:** Codex CLI `sandbox_mode = "workspace-write"` modunda çalışırken bile güvenlik politikası gereği `.git` meta veri dizinini Linux Landlock / bubblewrap veya macOS Seatbelt altında **salt okunur (`ro`)** bağlayabilmektedir. Bu durumda ajan `git add` veya `git commit` çalıştırdığında `fatal: Unable to create '.git/index.lock': Read-only file system` veya `Operation not permitted` hatası alır.
  2. **Git Worktree Kullanımında:** Bir `git worktree` dizininde `.git` bir klasör değil, ana depodaki `.git/worktrees/<id>` dizinine işaret eden bir metin dosyasıdır (`gitdir: /ana/depo/.git/worktrees/is-1`). Codex sandbox'ı çalışma alanı köküne yazma izni verse bile dışarıdaki ana `.git/worktrees/<id>` yolunu çözemediği veya bağlama sıralamasında (mount ordering) tekrar salt okunur yaptığı için worktree içinde hiçbir git yazma işlemi yapılamaz.
* **İlgili GitHub Issue'ları:**
  * **https://github.com/openai/codex/issues/19786** — *Linux sandbox mounts linked worktree gitdir read-only after writable ancestor bind* (Durum: Açık/aktif incelenen Linux sandbox bağlama sıralaması hatası).
  * **https://github.com/openai/codex/issues/27418** — *CLI sandbox remounts Git worktree gitdir read-only despite explicit .git write permission* (Durum: Açık/raporlanmış; açık izin verilse dahi worktree `gitdir` dizininin salt okunur kalması).
  * **https://github.com/openai/codex/issues/23661** ve **https://github.com/openai/codex/issues/38672** — Bağlı worktree yollarının sandbox tarafından reddedilmesi.
  * **https://github.com/openai/codex/issues/15505** ve **https://github.com/openai/codex/issues/7071** — `workspace-write` modunda `.git` dizininin salt okunur olması.
  * **https://github.com/openai/codex/issues/17482** ve **https://github.com/openai/codex/issues/41305** — İptal edilen veya paralel çalışan görevlerin arkasında sıfır baytlık bayat `.git/index.lock` bırakması.
* **Önerilen Geçici Çözüm (Workaround):**
  * **Tasarım Kalıbı (Ajan Commit Atmaz, Orkestratör Commit Atar):** `codex exec` işçisine **asla `git commit` veya `git add` görevi vermeyin**. İşçi yalnızca çalışma ağacındaki kaynak dosyaları düzenlesin; `codex exec` tamamlandığında sandbox dışındaki **orkestratör** `.git/index.lock` kontrolü yapıp `git status` / `git diff` / `git commit` işlemlerini kendisi yürütsün.
  * Eğer işçinin mutlaka git мета verisine erişmesi gerekiyorsa `--add-dir <ana-depo-.git-yolu>` eklenmeli, ancak `#27418` nedeniyle bunun bile her Linux çekirdeğinde yetmeyebileceği bilerek git yazma işlemleri orkestratöre bırakılmalıdır.

### 2.3. Gemini CLI ve Antigravity CLI (`agy`)'da Başsız Modda Komut İzni Reddi ve Allowlist Tuzakları

* **Kök Neden:**
  1. **Gemini CLI (`google-gemini/gemini-cli`):** Başsız modda (`gemini -p "..."`) güvenlik sertleştirmeleri (**CVE-2026-12537** sonrası çalışma alanı güveni / workspace trust zorunluluğu) ve politika motoru nedeniyle `run_shell_command` (`ShellTool`) varsayılan olarak engellenir veya onay bekler. Ayrıca `settings.json` içinde `"tools": {"core": ["run_shell_command"]}` tanımlamak, beyaz liste (whitelist) mantığı yüzünden `read_file` ve `write_file` dahil diğer tüm yerleşik araçları kazara devre dışı bırakır (`Tool not found in registry`).
  2. **Antigravity CLI (`agy`):** Resmi belgelere (`https://antigravity.google/docs/cli/reference`, `https://antigravity.google/docs/permissions`, `https://antigravity.google/docs/sandbox`) göre `agy -p "..."` (veya `--print` / `--prompt`) başsız modda çalışır. İzin motoru `Deny > Ask > Allow` öncelik sırasıyla `action(target)` (ör. `command(git)`, `write_file(src/)`) kurallarını değerlendirir ve varsayılan modda kabuk komutlarını Linux `nsjail` (ağ erişimi kapalı) sandbox'ında çalıştırır. Sandbox dışına çıkmak veya izin verilmeyen bir komutu çalıştırmak `Ask` katmanına düşerse başsız süreç onay bekleyerek durur veya reddedilir.
* **İlgili GitHub Issue'ları ve Resmi Belgeler:**
  * **https://github.com/google-gemini/gemini-cli/issues/18807** — *Setting `"tools": { "core": ["run_shell_command"]}` disables built-in tools unexpectedly* (Durum: Raporlanmış yapılandırma tuzağı; tam açık/kapalı durumu `doğrulanamadı`).
  * **https://github.com/google-gemini/gemini-cli/issues/20469** ve **https://github.com/google-gemini/gemini-cli/issues/19773** — Başsız (`-p`) modda `--approval-mode auto_edit` veya yerel `.gemini/policies/tools.toml` kurallarının `run_shell_command` için yok sayılması (Tam açık/kapalı durumu `doğrulanamadı`).
  * **Antigravity Resmi Belgeleri:** `https://antigravity.google/docs/cli/reference`, `https://antigravity.google/docs/permissions`, `https://antigravity.google/docs/sandbox` ve [sdk.md].
* **Önerilen Geçici Çözüm (Workaround):**
  * **Antigravity CLI (`agy`) İçin:** İzole bir `git worktree` içinde çalışırken `~/.gemini/antigravity-cli/settings.json` içinde `permissions.allow` listesine güvenli komut şablonlarını (`command(pytest*)`, `command(npm test*)`, `write_file(*)`) ekleyin veya tam izole worktree'de `--dangerously-skip-permissions` bayrağını `--output-format stream-json` ile birlikte kullanın. Alternatif olarak Python tabanlı orkestratörde doğrudan resmi [Antigravity Python SDK](https://github.com/google-antigravity/antigravity-sdk-python) (`pip install google-antigravity`) üzerinden `LocalAgentConfig(capabilities=CapabilitiesConfig())` ile programatik akış (`response.tool_calls`, `response.thoughts`) kullanın.
  * **Gemini CLI İçin:** `--yolo` ile `--approval-mode` bayraklarını aynı anda karıştırmayın; doğrudan `--approval-mode=yolo` veya `--allowed-tools "ShellTool(git status),ShellTool(pytest)"` kullanın ve `tools.core` dizisini elle daraltmayın.

### 2.4. `opencode run` İzin Kilitlenmesi, Boş Çıktı (`zero stdout`) ve Hatalı `exit code 0` Sorunları

* **Kök Neden:** `anomalyco/opencode` (eski adıyla `sst/opencode`) CLI'ında `opencode run` komutuyla ilgili dört kritik arıza bulunmaktadır:
  1. **Sıfır Çıktı (Zero Stdout):** Ajan diskte dosya oluşturma/düzenleme işlemlerini başarıyla yapsa bile `stdout`'a **0 bayt** yazıp `exit code 0` ile sessizce çıkar (v1.15.0 civarı regresyon).
  2. **Hatalarda Bile `exit code 0` Dönmesi:** Oturum bulunamadığında (`Error: Session not found`), kimlik bilgileri eksik olduğunda veya model adı geçersiz olduğunda bile süreç `exit code 0` döndürerek otomasyon betiklerini yanıltır.
  3. **Araç Çağrısı Sonrası Asılı Kalma:** Tüm araç çağrıları (tool calls) bittiği halde oturum işlemcisi "stop" durumunu yakalayamayıp süreci sonsuza kadar açık bırakır.
  4. **Yeni Dizinde/Worktree'de İzin Kilitlenmesi:** Yeni açılan bir worktree dizininde çalıştırıldığında `"Permission Required"` ekranında takılı kalır.
* **İlgili GitHub Issue'ları:**
  * **https://github.com/anomalyco/opencode/issues/27870** — *`[BUG] opencode run produces zero stdout, agent executes silently`* (v1.15.0 regresyonu; açık/kapalı durumu `doğrulanamadı`).
  * **https://github.com/anomalyco/opencode/issues/28407** — *`opencode run returns Session not found in headless mode (v1.15.5)`* (`exit code 0` ile hata dönmesi; açık/kapalı durumu `doğrulanamadı`).
  * **https://github.com/anomalyco/opencode/issues/17516** — *`opencode run hangs after completing tool calls — process never exits`* (Durum: `doğrulanamadı`).
  * **https://github.com/anomalyco/opencode/issues/30344** ve **https://github.com/anomalyco/opencode/issues/27436** — *`Stuck on "Permission Required" after opening in new directory`* (Durum: `doğrulanamadı`).
  * **https://github.com/anomalyco/opencode/issues/9954** — *`OpenCode GitHub Action hangs indefinitely at 'Sending message to opencode...'`*.
* **Önerilen Geçici Çözüm (Workaround):**
  * `opencode run` için **asla yalnız `exit code == 0` kontrolüne güvenmeyin**.
  * Başarı ölçütü olarak: **(a)** `stdout`/`stderr` içinde bilinen hata dizgilerinin (`Error: Session not found`, `ProviderError`, `Invalid model`) bulunmaması, **(b)** görev bir kod değişikliği ise `git status --porcelain` veya `git diff` çıktısının boş olmaması, **(c)** görev salt-okunur analiz ise `stdout` uzunluğunun `> 0` olması veya çıktının hedef bir dosyaya yazılıp dosya varlığının doğrulanması şart koşulmalıdır.
  * Worktree içinde izin takılmasını önlemek için çalışma dizininde `opencode.json` içinde `permission` kuralları önceden `"allow"` olarak yapılandırılmalı ve `--log-level DEBUG` / `~/.local/share/opencode/log/opencode.log` üzerinden kalp atışı (heartbeat) izlenmelidir.

### 2.5. `claude -p` Alt Ajan (`Task`) Kotası ve Paralel Çağrılarda Sahte Hız Sınırı (Rate Limit)

* **Kök Neden:**
  1. **Alt Ajan (`Task` Aracı) Kota/Hız Sınırı Çarpanı:** Claude Code içinden `Task` aracıyla paralel alt ajanlar başlatıldığında, istemci tarafındaki hız sınırlayıcı (rate limiter) büyük bağlam (context) penceresini aktif alt ajan sayısıyla çarparak daha token tüketilmeden (`total_tokens: 0`) `"API Error: Rate limit reached"` hatası fırlatabilmektedir.
  2. **Programatik (`claude -p` / SDK) Kota Havuzu Farkı:** `claude -p` ile aşırı paralel alt süreç başlatmak hem 5 saatlik / haftalık Max abonelik penceresini hızla eritir hem de eşzamanlılık (concurrency) duvarına çarpar.
* **İlgili GitHub Issue'ları:**
  * **https://github.com/anthropics/claude-code/issues/27053** — *`[BUG] Task tool subagents permanently return 'Rate limit reached' with 0 tokens consumed`* (Durum: `doğrulanamadı`).
  * **https://github.com/anthropics/claude-code/issues/40273** — *`[BUG] Rate limiter not functioning correctly "API Error: Rate limit reached" when spawning more that one agent`* (Durum: `doğrulanamadı`).
  * **https://github.com/anthropics/claude-code/issues/65942** — *`[BUG] This is frustating to get usage limit issue because of Anthropic capacity limitation`*.
  * **https://github.com/anthropics/claude-code/issues/14129** — Hız sınırına çarpıldığında `/rate-limit-options` döngüsünün fazladan token tüketmesi.
  * **https://github.com/BloopAI/vibe-kanban/issues/3417** — `claude -p` / SDK kullanımının kota havuzu üzerindeki etkisi.
* **Önerilen Geçici Çözüm (Workaround):**
  * **Claude Code Yalnızca Orkestratör ve Üst Düzey Hakem Olmalı:** Claude Code (Max aboneliği) kendi içinde 5–10 adet paralel `Task` alt ajanı (subagent fan-out) açmamalıdır. Bunun yerine alt görevleri tekil ve dar bağlamlı istemlerle **diğer CLI'lara** (`codex exec`, `agy -p`, `opencode run`) ve **yerel `llama.cpp` modellerine** (Qwen3.5 4B/9B, Qwen3.6-35B-A3B) dağıtmalıdır.
  * Zorunlu `claude -p` çağrılarında eşzamanlılık `max_concurrency = 1` (veya en fazla 2) ile sınırlandırılmalı ve `--max-turns` parametresiyle sonsuz döngüler engellenmelidir.

---

## 3. Sistemimize Alınacak 10 Somut Tasarım Kalıbı (Design Patterns)

Ubuntu + RTX 5070 Ti (12 GB VRAM) makinemizde Claude Code koordinatörlüğünde çalışacak otonom sistem için yukarıdaki projelerden ve GitHub issue'larından süzülen **10 somut mimari kalıp** şunlardır:

| # | Tasarım Kalıbı | Kaynak Proje / GitHub Issue | Sistemimizdeki Somut Uygulama Kuralı |
| :- | :--- | :--- | :--- |
| **1** | **Her Başsız Çağrıda `stdin=/dev/null` Zorunluluğu** | [`openai/codex#20919`](https://github.com/openai/codex/issues/20919), [`openai/codex#27019`](https://github.com/openai/codex/issues/27019), [`openai/codex#1045`](https://github.com/openai/codex/issues/1045) | Koordinatör (`claude`) veya görev dağıtıcı betik hiçbir CLI'ı (`codex exec`, `agy -p`, `opencode run`) açık stdin borusuyla çağırmaz. Tüm alt süreçler Python'da `stdin=subprocess.DEVNULL` veya kabukta `< /dev/null` ile başlatılır; istem (prompt) yalnızca argüman veya geçici görev dosyası olarak verilir. |
| **2** | **Worktree Başına Tek İşçi + Ortak Bağımlılık Symlink'i** | [`smtg-ai/claude-squad`](https://github.com/smtg-ai/claude-squad), [`BloopAI/vibe-kanban`](https://github.com/BloopAI/vibe-kanban), [`johannesjo/parallel-code`](https://github.com/johannesjo/parallel-code) | Aynı çalışma dizininde iki ajan asla çalışmaz. Her alt görev için `.worktrees/task-<id>` altında izole bir `git worktree` ve dal açılır. Disk/zaman maliyetini önlemek için `node_modules` veya `.venv` ana depodan sembolik bağ (symlink) ile bağlanır (`parallel-code` kalıbı). |
| **3** | **Git Meta Verisi Ayrımı: İşçi Kod Yazar, Orkestratör Commit Atar** | [`openai/codex#19786`](https://github.com/openai/codex/issues/19786), [`openai/codex#27418`](https://github.com/openai/codex/issues/27418), [`openai/codex#15505`](https://github.com/openai/codex/issues/15505), [`raine/workmux`](https://github.com/raine/workmux) | Codex sandbox'ının worktree `.git/worktrees/<id>/index.lock` dosyasını salt okunur kilitlemesi nedeniyle işçilere git komutu (`git add/commit`) yasaklanır. İşçi yalnızca dosyaları düzenler; süreç bittiğinde sandbox dışındaki orkestratör bayat `.git/index.lock` var mı bakar, testleri koşar ve commit/merge işlemini kendisi yapar. |
| **4** | **Çok Boyutlu Başarı Doğrulaması (`exit code 0` Yetersizdir)** | [`anomalyco/opencode#27870`](https://github.com/anomalyco/opencode/issues/27870), [`anomalyco/opencode#28407`](https://github.com/anomalyco/opencode/issues/28407), [`just-every/code`](https://github.com/just-every/code) | `opencode run`'ın hata aldığında veya 0 bayt çıktı ürettiğinde bile `exit code 0` dönmesi nedeniyle bir görevin başarılı sayılması için 3 koşul birlikte aranır: **(1)** `returncode == 0`, **(2)** `stderr`/`stdout` içinde bilinen hata imzalarının (`Session not found`, `Rate limit`, `429`) olmaması, **(3)** kod görevlerinde `git diff --stat` çıktısının boş olmaması + doğrulama testinin geçmesi. |
| **5** | **Çift Katmanlı Zaman Aşımı: Mutlak Süre + Akış Kalp Atışı (Heartbeat)** | [`anomalyco/opencode#17516`](https://github.com/anomalyco/opencode/issues/17516), [`terragon-labs/terragon-oss`](https://github.com/terragon-labs/terragon-oss), [`gastownhall/gastown`](https://github.com/gastownhall/gastown) (*Witness*) | Araç çağrıları bittiği halde kapanmayan süreçleri (`opencode#17516`) yakalamak için her alt sürece iki sayaç uygulanır: **(a)** Görev tipine göre mutlak üst süre (`hard_timeout`, ör. 600 sn), **(b)** `stdout`/`stderr`, NDJSON akışı (`agy -p --output-format stream-json`) veya worktree dosya değişim zamanı (`mtime`) üzerinde **hareketsizlik zaman aşımı** (`idle_timeout`, ör. 90 sn boyunca ne çıktı ne dosya değişikliği varsa `SIGTERM` $\rightarrow$ `SIGKILL`). |
| **6** | **ToS-Uyumlu Resmi CLI Kota ve Yedekleme Zinciri (Fallback Chain)** | [`code-yeongyu/oh-my-opencode`](https://github.com/code-yeongyu/oh-my-opencode) (mimari), [`anthropics/claude-code#40273`](https://github.com/anthropics/claude-code/issues/40273) | Hiçbir OAuth proxy kullanmadan, görevler resmi ikililer arasında öncelik ve kota durumuna göre devredilir:<br>• **Mimari / Koordinasyon / Son Hakem:** `claude` (Max)<br>• **Ağır Kod Üretimi / Refactoring:** `codex exec` (Plus) $\xrightarrow{\text{429/timeout}}$ `agy -p` (AI Ultra: ayrı Claude/GPT veya Gemini kotası)<br>• **Orta Ölçekli / Rutin Kod & Test:** `agy -p` (Gemini) $\xrightarrow{\text{fallback}}$ `opencode run` (ücretsiz modeller)<br>• **Özetleme / Sınıflandırma / Hızlı Linting / Diff Ön-İnceleme:** Yerel `llama.cpp` (RTX 5070 Ti 12GB VRAM üzerinde Qwen3.5 4B/9B veya Qwen3.6-35B-A3B). |
| **7** | **Claude `Task` Fan-Out Yasağı ve Yerel/Harici İşçi Delegasyonu** | [`anthropics/claude-code#27053`](https://github.com/anthropics/claude-code/issues/27053), [`anthropics/claude-code#40273`](https://github.com/anthropics/claude-code/issues/40273), [`BloopAI/vibe-kanban#3417`](https://github.com/BloopAI/vibe-kanban/issues/3417) | Claude Code'un kendi iç `Task` aracıyla paralel alt ajanlar açması, bağlam çarpanı ve `0 token` sahte rate-limit hatasına (`#27053`, `#40273`) yol açtığı için sınırlandırılır. Dosya arama, log özetleme ve ön analiz işleri **0 kota maliyetli yerel `llama.cpp` (Qwen3.5-9B / Qwen3.6-35B-A3B)** işçisine; paralel kodlama işleri ise `codex exec` ve `agy -p` işçilerine dağıtılır. |
| **8** | **Başsız İzin Ön-Onayı (Pre-Seeded Workspace Permissions)** | [`google-gemini/gemini-cli#18807`](https://github.com/google-gemini/gemini-cli/issues/18807), [`anomalyco/opencode#30344`](https://github.com/anomalyco/opencode/issues/30344), [`antigravity.google/docs/permissions`](https://antigravity.google/docs/permissions) | Yeni açılan her `git worktree` içine işçi başlatılmadan önce orkestratör tarafından güvenli izin şablonları enjekte edilir: `agy` için `permissions.allow` kuralları (veya izole worktree'de `--dangerously-skip-permissions`), `codex exec` için `--full-auto` (veya `-s workspace-write`), `opencode` için dizin bazlı otomatik izin yapılandırması. Böylece hiçbir başsız işçi etkileşimli onay isteminde (`Ask` / `Permission Required`) asılı kalmaz. |
| **9** | **Rekabetçi Çift-Koşum (Dual-Run) ve Hakemli Birleştirme Kuyruğu (Refinery)** | [`devflowinc/uzi`](https://github.com/devflowinc/uzi), [`stravu/crystal`](https://github.com/stravu/crystal), [`gastownhall/gastown`](https://github.com/gastownhall/gastown) (*Refinery*) | Kritik veya belirsizliği yüksek görevlerde orkestratör iki ayrı worktree açıp aynı görevi paralel olarak hem `codex exec` hem de `agy -p` işçisine verir (`uzi` / `crystal` kalıbı). Her iki worktree'de otomatik test paketi (`pytest` / `cargo test` / `npm test`) koşulur; testleri geçen ve en temiz diff'i üreten dal *Refinery* (hakem) adımıyla ana dala birleştirilir, diğeri silinir. |
| **10** | **VRAM-Farkında Yerel Model Kapısı ve Dinamik Kota Devre Kesicisi (Circuit Breaker)** | [`code-yeongyu/oh-my-opencode`](https://github.com/code-yeongyu/oh-my-opencode), [`coder/mux`](https://github.com/coder/mux) | RTX 5070 Ti (12 GB VRAM) üzerinde aynı anda tek bir ağır yerel model (`llama-server`) bellekte tutulur (hızlı görevlerde Qwen3.5 4B/9B Q8_0/Q6_K, derin yerel görevlerde Qwen3.6-35B-A3B Q4_K_M + MoE uzman offload). Bulut CLI'ları için yerel bir SQLite/JSON **Devre Kesici (Circuit Breaker)** tutulur: herhangi bir CLI `429` / kota uyarısı döndürdüğünde o CLI'ın ilgili model havuzu soğuma süresine (`cooldown_until`) alınır ve görevler kesintisiz olarak sıradaki sağlam CLI'a veya yerel `llama.cpp` sunucusuna yönlendirilir. |
