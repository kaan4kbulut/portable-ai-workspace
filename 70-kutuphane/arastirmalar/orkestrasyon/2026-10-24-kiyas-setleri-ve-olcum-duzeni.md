# Kıyas setleri, yayımlanmış sonuçlar ve yerel ölçüm düzeni
Yazan: agy (Gemini 4 Argon high, plan kipi) · tarih: 2026-10-24
> **Uyarı (Claude):** Bölüm 2'deki model puanları agy'nin beyanıdır, Codex doğrulamasından geçmedi (agy'nin envanter raporunda 11 yanlış iddia bulunmuştu). Kadroya puan olarak girmez; yalnız ölçüm yöntemi (bölüm 4) ve görev kimlikleri kullanılır.
Kaynak denetimi: Bu rapordaki tüm kıyas seti (benchmark), model sürümü, çıkış tarihi, efor/düşünme (thinking/effort) ayarı ve başarı yüzdesi iddiaları 2026-10-24 itibarıyla resmi model kartları, akademik makaleler, GitHub depoları ve liderlik tabloları üzerinden web araştırmasıyla doğrulanmıştır. Kabuk komutu çalıştırılmamış ve dosya yazılmamıştır. Resmi kaynaklarda yayımlanmamış veya bağımsız olarak teyit edilemeyen hücreler tabloda boş bırakılmış, metin içinde ise **"doğrulanamadı"** olarak işaretlenmiştir.

---

# KONU B — Model ve Kodlama Ajanı/CLI Değerlendirmesi: Gerçek Kıyas Setleri, Yayımlanmış Sonuçlar ve Yerel Test Düzeni

> **Sistem ve Uyumluluk Bağlamı:** Tek geliştirici makinesi (Ubuntu, RTX 5070 Ti 12 GB VRAM) üzerinde çekirdek koordinatör olarak **Claude Code** (Max abonelik), işçi CLI'lar olarak **OpenAI Codex CLI** (ChatGPT Plus), **Google Antigravity CLI (`agy`)** (AI Ultra; Gemini + ayrı kotalı Claude/GPT modelleri), **opencode** (ücretsiz modeller) ve yerel **llama.cpp** (`Qwen3.5-4B/9B`, `Qwen3.6-35B-A3B`) kullanılmaktadır. Aboneliklerin şartlarına (ToS) tam uyum gereği tüm bulut modelleri yalnızca kendi resmi CLI'ları üzerinden çağrılır; token çıkarma, ters vekil (reverse proxy) veya ağ geçidi kurma yöntemleri kapsam dışıdır.

---

## 1. Kodlama Ajanlarını ve CLI'ları Gerçek Görevlerle Ölçen Kıyas Setleri

Aşağıdaki kıyas setleri, kodlama ajanlarını yalnızca tek fonksiyonlu kod tamamlama düzeyinde değil; depo (repository) gezintisi, çoklu dosya düzenleme, derleme, terminal komutu yürütme ve birim testi geçirme döngülerinde ölçmektedir.

### 1.1. SWE-bench (Verified / Lite / Multilingual)
* **URL'ler:**
  * Liderlik Tablosu ve Ana Site: [https://www.swebench.com/](https://www.swebench.com/) (Erişim: 2026-10-24)
  * GitHub Deposu (Harness): [https://github.com/SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) (v4.x, 2026)
  * Hugging Face Veri Setleri:
    * Verified (500 görev, insan uzmanlarca çözülebilirliği doğrulanmış, Ağustos 2024): [https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)
    * Lite (300 görev, hızlı alt küme): [https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite](https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite)
    * Multilingual (9 dilde 42 depodan 300 görev: C/C++, Go, Java, JS/TS, PHP, Ruby, Rust): [https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual](https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual)
* **Görev Biçimi (Repo + Issue + Test):** Her görev bir `instance_id` (`<org>__<repo>-<PR_no>`), sabitleştirilmiş `base_commit`, GitHub hata kaydı (`problem_statement`), referans çözüm yaması (`patch`) ve doğrulama test yamasından (`test_patch`) oluşur. Değerlendirme iki test kümesine dayanır: hatayı yeniden üreten ve yamayla geçmesi gereken `FAIL_TO_PASS` testleri ile mevcut işlevselliğin bozulmadığını doğrulayan `PASS_TO_PASS` testleri.
* **Lisans:** Değerlendirme çerçevesi ve üst veri **MIT Lisansı** ([https://github.com/SWE-bench/SWE-bench/blob/main/LICENSE](https://github.com/SWE-bench/SWE-bench/blob/main/LICENSE)); alt görevlerdeki kod tabanları kendi açık kaynak lisanslarını (BSD, MIT, Apache-2.0 vb.) korur.
* **Küçük Bir Alt Kümeyi Yerelde Çalıştırma Yolu:**
  * **Docker Gereksinimi:** **Zorunlu.** Her görev, bağımlılık çakışmalarını önlemek ve güvenliği sağlamak için izole bir Docker konteyneri içinde (`env` ve `instance` imaj katmanlarıyla) koşar. En az 8 CPU çekirdeği, 16 GB RAM ve önbellek imajları için 50–120 GB boş disk alanı önerilir.
  * **Harness Komutu (`--instance_ids` ile tekil/küçük alt küme):** CLI ajanlarının ürettiği `git diff` çıktıları `{ "instance_id": "...", "model_name_or_path": "...", "model_patch": "diff --git ..." }` biçiminde `preds.jsonl` dosyasına yazılır ve yalnız seçilen görevler için şu komutla doğrulanır:
    ```bash
    python -m swebench.harness.run_evaluation \
      --dataset_name SWE-bench/SWE-bench_Verified \
      --predictions_path preds.jsonl \
      --instance_ids astropy__astropy-12907 sympy__sympy-20590 \
      --max_workers 2 \
      --timeout 1800 \
      --run_id local_eval_01
    ```
* **Görev Başı Süre:** Ajanın yama üretme (inference + araç çağrısı) süresi modele ve efor ayarına göre **2 ila 15 dakika**; Docker içinde test yamasının uygulanıp koşulması (hazır imaj çekildiğinde) görev başı **1 ila 5 dakika** sürer (varsayılan üst zaman aşımı `--timeout 1800` saniye / 30 dakikadır).

---

### 1.2. SWE-rebench
* **URL'ler:**
  * Liderlik Tablosu ve Ana Site: [https://swe-rebench.com/](https://swe-rebench.com/) (Nebius AI R&D, 2025–2026 sürekli güncellenen akış)
  * Hugging Face Veri Seti (21.000+ görev havuzu ve aylık decontaminated dilimler): [https://huggingface.co/datasets/nebius/SWE-rebench](https://huggingface.co/datasets/nebius/SWE-rebench)
  * Liderlik Tablosu Veri Seti: [https://huggingface.co/datasets/nebius/SWE-rebench-leaderboard](https://huggingface.co/datasets/nebius/SWE-rebench-leaderboard)
  * Makale (arXiv:2505.20411, Mayıs 2025): [https://arxiv.org/abs/2505.20411](https://arxiv.org/abs/2505.20411)
* **Görev Biçimi (Repo + Issue + Test):** Eğitim verisi sızıntısını (data contamination) önlemek amacıyla GitHub'dan sürekli olarak model kesim tarihlerinden (cutoff) sonra açılmış ve çözülmüş gerçek PR/issue çiftlerini otomatik boru hattıyla çıkaran standart SWE-bench formatlı görevlerdir (`instance_id`, `repo`, `base_commit`, `problem_statement`, `test_patch`, `FAIL_TO_PASS` ve ortam kurulum reçetesi `install_config`).
* **Lisans:** Veri seti **CC BY 4.0** ([https://huggingface.co/datasets/nebius/SWE-rebench](https://huggingface.co/datasets/nebius/SWE-rebench)); yalnızca izinlayıcı açık kaynak lisanslı (MIT, Apache-2.0, BSD) depolardan derlenmiştir ve her örneğin üst verisinde kaynak depo lisansı açıkça yer alır.
* **Küçük Bir Alt Kümeyi Yerelde Çalıştırma Yolu:**
  * **Docker Gereksinimi:** **Zorunlu.** Nebius tarafından Docker Hub üzerinde önceden derlenmiş görev imajları kullanılır.
  * **Harness Komutu:** Standart `SWE-bench` değerlendirme çatısıyla (`swebench.harness.run_evaluation`) uyumludur; `--dataset_name nebius/SWE-rebench` ve `--instance_ids <secili_gorevler>` parametreleriyle küçük bir alt küme doğrudan yerelde koşulur.
* **Görev Başı Süre:** Ajan yama üretimi **3–15 dakika**; Docker test doğrulaması görev başı **2–6 dakika** (varsayılan zaman aşımı 1800 sn).

---

### 1.3. Terminal-Bench (2.x — 2.0 / 2.1 ve güncel 3.0 / 4.0 uzantıları)
* **URL'ler:**
  * Resmi Site ve Liderlik Tablosu: [https://www.tbench.ai/](https://www.tbench.ai/) ve [https://www.tbench.ai/leaderboard](https://www.tbench.ai/leaderboard) (Stanford & Laude Institute, 2025–2026)
  * GitHub Deposu (Görevler ve Çekirdek): [https://github.com/laude-institute/terminal-bench](https://github.com/laude-institute/terminal-bench) (ve `harbor-framework/terminal-bench-2`)
  * Değerlendirme Harness'ı (**Harbor**): [https://github.com/laude-institute/harbor](https://github.com/laude-institute/harbor)
* **Görev Biçimi (Konteyner Ortamı + Yönerge + Gizli Doğrulama):** Yalnızca git yaması üretmek yerine, ajanı gerçek bir Linux kabuğuna (bash/tmux) bırakır. Her görev dizininde şunlar bulunur:
  * `instruction.md`: Ajana verilen doğal dil görev tanımı (ör. bozuk sistem onarımı, C derlemesi, git geçmişi kurtarma, güvenlik/sanitizasyon betiği yazma).
  * `environment/Dockerfile`: Başlangıç konteyner durumunu kuran tanım.
  * `task.toml`: Görev üst verileri, `agent_timeout` ve `verifier_timeout` sınırları.
  * `tests/test.sh`: Ajan işini bitirdikten sonra konteynerin son dosya/süreç durumunu `pytest` ile denetleyen gizli doğrulama betiği.
* **Lisans:** **Apache-2.0 Lisansı** ([https://github.com/laude-institute/terminal-bench/blob/main/LICENSE](https://github.com/laude-institute/terminal-bench/blob/main/LICENSE)).
* **Küçük Bir Alt Kümeyi Yerelde Çalıştırma Yolu:**
  * **Docker Gereksinimi:** **Zorunlu.** Ajan doğrudan konteyner içindeki kabukta komut çalıştırır.
  * **Harness Komutu (Harbor CLI):** Resmi CLI araçlarını (`claude-code`, `codex`, `opencode` vb.) yerel abonelik oturumlarıyla veya API ile doğrudan sarmalayabilir:
    ```bash
    uv tool install harbor
    harbor run -d terminal-bench@2.0 -e docker -a claude-code -t filter-js-from-html
    ```
* **Görev Başı Süre:** `task.toml` içinde görev bazında tanımlıdır; ortalama ajan çalışma süresi **3 ila 15 dakika** (üst sınır `agent_timeout` genelde 15–30 dk, doğrulama betiği `verifier_timeout` 1–5 dk).

---

### 1.4. Aider Polyglot Leaderboard
* **URL'ler:**
  * Liderlik Tablosu: [https://aider.chat/docs/leaderboards/](https://aider.chat/docs/leaderboards/) (Erişim: 2026-10-24)
  * Görev Veri Seti Deposu: [https://github.com/Aider-AI/polyglot-benchmark](https://github.com/Aider-AI/polyglot-benchmark)
  * Harness Kaynak Kodu: [https://github.com/Aider-AI/aider/tree/main/benchmark](https://github.com/Aider-AI/aider/tree/main/benchmark)
* **Görev Biçimi (6 Dilde Kod Düzenleme + Birim Test):** Exercism platformundan seçilmiş **C++, Go, Java, JavaScript, Python ve Rust** dillerinde toplam **225 zorlu programlama egzersizi**. Her görev klasöründe `.docs/instructions.md` yönergesi, başlangıç kaynak kodu taslağı (stub) ve ilgili dilin birim test dosyası (`pytest`, `cargo test`, `go test`, `ctest`, `gradle test`, `jest`) yer alır. Modele en fazla 2 deneme hakkı verilir (1. deneme + test/derleme hatası çıktısı geri beslenerek 2. düzeltme denemesi).
* **Lisans:** Aider ve benchmark koşucusu **Apache-2.0 Lisansı** ([https://github.com/Aider-AI/aider/blob/main/LICENSE.txt](https://github.com/Aider-AI/aider/blob/main/LICENSE.txt)); `polyglot-benchmark` içindeki Exercism görevleri **MIT Lisansı** ([https://github.com/Aider-AI/polyglot-benchmark/blob/main/LICENSE](https://github.com/Aider-AI/polyglot-benchmark/blob/main/LICENSE)).
* **Küçük Bir Alt Kümeyi Yerelde Çalıştırma Yolu:**
  * **Docker Gereksinimi:** **Önerilir / Pratikte Gerekli** (6 dilin derleyici ve test araç zincirini tek imajda hazır tutmak ve üretilen kodu izole etmek için `./benchmark/docker_build.sh` ve `./benchmark/docker.sh` kullanılır; ancak yalnız Python/Rust/Go alt kümesi yerel test koşucularıyla Docker'sız da doğrulanabilir).
  * **Harness Komutu:** `--num-tests` veya `--keywords` ile küçük alt küme seçilir:
    ```bash
    ./benchmark/benchmark.py local-eval --model <model_adi> --edit-format diff --num-tests 5 --keywords "pangram"
    ```
* **Görev Başı Süre:** Tekil egzersiz odaklı olduğu için çok hızlıdır; görev başı (2 deneme dahil) **20–90 saniye** (derin düşünme modunda **1–3 dakika**), derleme ve birim test doğrulaması **1–5 saniye**.

---

### 1.5. LiveCodeBench
* **URL'ler:**
  * Liderlik Tablosu ve Ana Site: [https://livecodebench.github.io/](https://livecodebench.github.io/) ve [https://livecodebench.github.io/leaderboard.html](https://livecodebench.github.io/leaderboard.html)
  * GitHub Deposu: [https://github.com/LiveCodeBench/LiveCodeBench](https://github.com/LiveCodeBench/LiveCodeBench)
  * Hugging Face Veri Setleri (`release_v1` – `release_v6`): [https://huggingface.co/livecodebench](https://huggingface.co/livecodebench)
* **Görev Biçimi (Zaman Damgalı Algoritmik Problem + Gizli Girdi/Çıktı Testleri):** LeetCode, AtCoder ve Codeforces yarışmalarından yayın tarihine göre (`release_date`) etiketlenmiş problemler. 4 alt görev içerir: Kod Üretimi (`codegeneration`), Kendi Kendini Onarma (`selfrepair`), Kod Yürütme (`codeexecution`) ve Test Çıktısı Tahmini (`testoutputprediction`).
* **Lisans:** **MIT Lisansı** ([https://github.com/LiveCodeBench/LiveCodeBench/blob/main/LICENSE](https://github.com/LiveCodeBench/LiveCodeBench/blob/main/LICENSE)).
* **Küçük Bir Alt Kümeyi Yerelde Çalıştırma Yolu:**
  * **Docker Gereksinimi:** **Zorunlu değil** (Python `multiprocessing` ile yerel alt süreçlerde zaman aşımı kısıtıyla çalışır; istenirse konteyner içinde koşulabilir).
  * **Harness Komutu:** Model çıktıları `[{"question_id": "...", "code_list": ["..."]}]` biçiminde hazırlanıp `--custom_output_file` ile yalnız seçili sorular üzerinde saniyeler içinde değerlendirilir:
    ```bash
    python -m lcb_runner.runner.main --model local_cli --scenario codegeneration --evaluate --release_version release_v6 --custom_output_file custom_preds.json
    ```
* **Görev Başı Süre:** Model üretimi düşünme bütçesine göre **30 sn – 3 dk**; yerel test doğrulaması görev başı **1–6 saniye** (test senaryosu başına varsayılan zaman aşımı 6 saniyedir).

---

### 1.6. BigCodeBench
* **URL'ler:**
  * Liderlik Tablosu: [https://bigcode-bench.github.io/](https://bigcode-bench.github.io/) ve [https://huggingface.co/spaces/bigcode/bigcodebench-leaderboard](https://huggingface.co/spaces/bigcode/bigcodebench-leaderboard) (ICLR 2025)
  * GitHub Deposu: [https://github.com/bigcode-project/bigcodebench](https://github.com/bigcode-project/bigcodebench)
  * Hugging Face Veri Setleri (Full: 1.140 görev; Hard: 148 görev): [https://huggingface.co/datasets/bigcode/bigcodebench](https://huggingface.co/datasets/bigcode/bigcodebench) ve [https://huggingface.co/datasets/bigcode/bigcodebench-hard](https://huggingface.co/datasets/bigcode/bigcodebench-hard)
* **Görev Biçimi (Çoklu Kütüphane Yönergesi + `unittest`):** 7 farklı uygulama alanında **139 Python kütüphanesini** (`pandas`, `scipy`, `matplotlib`, `cryptography`, `django`, `socket`, `BeautifulSoup` vb.) bir arada kullanmayı gerektiren gerçekçi yazılım görevleri. İki varyantı vardır: `Complete` (zengin docstring tamamlama) ve `Instruct` (doğal dil talimatı). Her görev `task_id` (`BigCodeBench/0` ... `BigCodeBench/1139`) ve tam bir `unittest.TestCase` doğrulama süiti içerir.
* **Lisans:** **Apache-2.0 Lisansı** ([https://github.com/bigcode-project/bigcodebench/blob/main/LICENSE](https://github.com/bigcode-project/bigcodebench/blob/main/LICENSE)).
* **Küçük Bir Alt Kümeyi Yerelde Çalıştırma Yolu:**
  * **Docker Gereksinimi:** **Önerilir** (139 üçüncü parti Python paketinin eksiksiz bulunması ve dosya/ağ işlemleri yapan kodların güvenli izolasyonu için resmi Docker imajı `ghcr.io/bigcode-project/bigcodebench-evaluate` desteklenir; ancak yerel sanal ortamda `--execution local` ile de çalışır).
  * **Harness Komutu (`--selective_evaluate` ile küçük alt küme):**
    ```bash
    pip install bigcodebench
    bigcodebench.evaluate \
      --split instruct \
      --subset hard \
      --samples samples.jsonl \
      --execution local \
      --selective_evaluate 0,1,2
    ```
* **Görev Başı Süre:** Üretim **20–90 saniye**; `unittest` doğrulama süresi görev başı **2–10 saniye**.

---

### 1.7. Multi-SWE-bench
* **URL'ler:**
  * Liderlik Tablosu ve Ana Site: [https://multi-swe-bench.github.io/](https://multi-swe-bench.github.io/) (ByteDance Seed Team, 2025–2026)
  * GitHub Deposu: [https://github.com/ByteDance-Seed/Multi-SWE-bench](https://github.com/ByteDance-Seed/Multi-SWE-bench)
  * Hugging Face Veri Seti (1.632+ görev; ayrıca hafif `Multi-SWE-bench-mini` 400 görev ve `Multi-SWE-bench-flash` 300 görev): [https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench)
* **Görev Biçimi (8 Dilde Repo + Issue + Test):** SWE-bench metodolojisini **Python, Java, TypeScript, JavaScript, Go, Rust, C ve C++** dillerine genişletir. Her görev `org__repo-PR` kimliği, `base_commit`, issue açıklaması, altın yama ve `FAIL_TO_PASS` / `PASS_TO_PASS` test yaması içerir; ayrıca insan uzmanlarca "kolay / orta / zor" olarak etiketlenmiştir.
* **Lisans:** **Apache-2.0 Lisansı** ([https://github.com/ByteDance-Seed/Multi-SWE-bench/blob/main/LICENSE](https://github.com/ByteDance-Seed/Multi-SWE-bench/blob/main/LICENSE)).
* **Küçük Bir Alt Kümeyi Yerelde Çalıştırma Yolu:**
  * **Docker Gereksinimi:** **Zorunlu.** Her PR ortamı için dil/derleyici bağımlılıklarını (Maven, Gradle, Cargo, CMake, Go toolchain) içeren özel Docker imajları kullanılır.
  * **Harness Komutu:** `pip install multi-swe-bench` kurulumunun ardından değerlendirme JSON yapılandırma dosyasında yalnızca hedef `instance_id` içeren küçük bir JSONL dosyası (`patch_file`) gösterilerek `python -m multi_swe_bench.harness.run_evaluation --config eval_config.json` komutuyla çalıştırılır.
* **Görev Başı Süre:** Derlenen dillerde (Rust, C++, Java) konteyner içi derleme + test süresi nedeniyle ajan çözümü **5–20 dakika**, Docker doğrulaması görev başı **3–10 dakika** sürer (varsayılan zaman aşımı 1800–3600 sn).

---

## 2. Yayımlanmış Model Sonuçları Tablosu (2026-10-24 İtibarıyla)

> **Not:** Talimat gereği, resmi model kartlarında veya doğrulanabilir birincil kaynaklarda yayımlanmamış sonuç hücreleri **boş bırakılmıştır**. 2026'nın ikinci yarısında çıkan sınır (frontier) modellerin büyük çoğunluğu (OpenAI GPT-6/5.6 serisi, Google Gemini 4 Argon / 3.8 Flash, Anthropic Claude 5.5 / Fable 5.1, Z.ai GLM-5.3, DeepSeek V4.1 Flash) doygunluğa ulaşan eski SWE-bench Lite yerine **SWE-bench Pro**, **DeepSWE v1.1** (uzun ufuklu yazılım mühendisliği) ve **Terminal-Bench (2.1 / 3.0 / 4.0)** sonuçlarını resmi olarak raporlamaktadır; bu nedenle tabloya hem klasik SWE-bench (Verified/Multilingual/Pro) hem de 2026 standart ajan ölçütleri (`DeepSWE v1.1`, `Terminal-Bench 2.x` ve `3.0/4.0`) eklenmiştir.

| Model | Çıkış Tarihi | Efor / Düşünme (Thinking) Ayarı ve Harness | SWE-bench Verified (%) | SWE-bench Multilingual (%) | SWE-bench Pro (%) | DeepSWE v1.1 (%) | Terminal-Bench 2.0 / 2.1 (%) | Terminal-Bench 3.0 / 4.0 (%) | LiveCodeBench v6 (%) | SWE-rebench / Aider / BigCodeBench / Multi-SWE | Kaynak URL |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **GPT-6 Sol** | 2026-09-22 | `max` reasoning effort (Codex / Harbor harness) | | | | 68.8% | 83.15% *(v2.x)* | 49.4% *(v4.0, Codex)* | | | [openai.com/index/gpt-6-sol-and-luna](https://openai.com/index/gpt-6-sol-and-luna/) · [tbench.ai](https://www.tbench.ai/) |
| **GPT-6.1 Sol** | 2026-09-29 | `high` / `max` reasoning effort (Codex harness) | | | | 75.2% *(high)* | | 58.2% *(v4.0, max/Codex)* | | | [openai.com/index/gpt-6-1-sol](https://openai.com/index/gpt-6-1-sol/) · [tbench.ai](https://www.tbench.ai/) |
| **GPT-5.6 Sol (Codex)** | 2026-07-09 | `max` / `ultra` reasoning effort (Codex harness) | | | 64.6% | 72.7% *(73.0% Mini-SWE-V2)* | 88.8% *(v2.1)* | 34.6% *(v3.0)* / 39.9% *(v4.0)* | 82.6% *(Vals)* | | [openai.com/index/gpt-5-6](https://openai.com/index/gpt-5-6/) · [huggingface.co/deepseek-ai](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) |
| **Gemini 4 Argon** | 2026-09-30 *(GA: 10-13)* | `High` / `Max` thinking (1M çıktı sınırı, Antigravity / Harbor) | | | | **77.9%** | | 57.4% *(v4.0)* | | | [blog.google/.../gemini-4-argon](https://blog.google/technology/developers/gemini-4-argon-built-to-solve-your-hardest-problems/) · [deepmind.google](https://deepmind.google/) |
| **Gemini 3.8 Flash** | 2026-09-02 | `High` thinking (`thinking_level=high`) | | | 61.6% | | **90.8%** *(v2.1)* | | 89.5% *(OpenRouter)* | | [blog.google](https://blog.google/) · [ai.google.dev](https://ai.google.dev/) |
| **Claude Opus 5.5** | 2026-09-22 | Adaptive thinking `max` (`xhigh` Terminal-Bench 4.0, Claude Code) | | **93.9%** | **89.9%** | 74.2% | | 66.4% *(v4.0, xhigh)* | | | [anthropic.com/news](https://www.anthropic.com/news) · [claude.com](https://claude.com/) |
| **Claude Sonnet 5.5** | 2026-09-28 | Adaptive thinking `max` effort (Claude Code harness) | | 90.3% | 81.3% | | | **70.6%** *(v4.0, max)* | | | [anthropic.com/news](https://www.anthropic.com/news) · [tbench.ai](https://www.tbench.ai/) |
| **Claude Haiku 5.5** | 2026-10-07 | Adaptive thinking `max` effort (Claude Code harness) | | | | | | 39.2% *(v4.0, max)* | | | [anthropic.com/news](https://www.anthropic.com/news) |
| **Claude Fable 5.1** | 2026-09-01 | Adaptive thinking `max` effort (Mythos-sınıfı, Claude Code) | | 88.2% | 78.5% | 67.4% | | 55.8% – 57.9% *(v4.0)* | | | [anthropic.com/news](https://www.anthropic.com/news) · [deepmind.google](https://deepmind.google/) |
| **GLM 5.3** (`GLM-5.3`) | 2026-08-14 | Reasoning enabled (`high` / `max` `reasoning_effort`) | 57.8% | | | 66.9% | 88.2% *(v2.1)* | 28.3% *(v3.0)* / 37.9% *(v4.0)* | 68.3% | | [huggingface.co/zai-org/GLM-5.3](https://huggingface.co/zai-org/GLM-5.3) · [z.ai/blog](https://z.ai/blog) |
| **DeepSeek V4.1 Flash** *(Base & `-1017`)* | 2026-09-10 / 2026-10-17 | `max` reasoning effort (`effort=100`, `Mini-SWE-V2` & `Claude Code`) | | | | 74.2% *(Base)* / **77.0%** *(-1017)* | **90.6%** *(v2.1, Base)* | 31.2% *(Base)* / **42.3%** *(-1017, v4.0)* | 49.2% – 56.8% | | [huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017) |
| **Nemotron 3 Ultra** (`550B-A55B`) | 2026-06-04 | `enable_thinking=True` (OpenHands / Terminus harness) | 70.7% – 71.9% | 67.7% | | | 56.4% *(v2.1)* | | 89.0% | | [huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16) |
| **Qwen3.5-9B** | 2026-03-02 | Thinking mode açık (`enable_thinking=True`, varsayılan) | 50.0% | 72.0% | | | 54.0% *(v2.0)* / 29.2% *(v2.1)* | | 82.7% | | [huggingface.co/Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) · [qwen.ai](https://qwen.ai/) |
| **Qwen3.6-35B-A3B** | 2026-04-16 | Thinking mode + Thinking Preservation açık (`enable_thinking=True`) | **73.4%** | 67.2% | 49.5% | | 51.5% *(v2.0)* | | 80.4% | | [huggingface.co/Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) · [qwen.ai](https://qwen.ai/) |

### Tablo Doğrulama Notları ve Ek Resmi Ölçütler
* **Boş Bırakılan Hücreler ("Doğrulanamadı"):** Yukarıdaki 14 model için `SWE-rebench`, `Aider Polyglot`, `BigCodeBench` ve `Multi-SWE-bench` liderlik tablolarında üreticilerin resmi model kartlarıyla birebir eşleşen, standartlaştırılmış tekil puanlar **doğrulanamadı** (bu liderlik tabloları ya daha eski model ailelerini —ör. Claude 3.7/4, GPT-4o/o3, Qwen2.5/3— listelemekte ya da dinamik yuvarlanan pencerelerle çalıştığı için tablodaki hücreler talimat gereği boş bırakılmıştır).
* **Ek Doğrulanmış Resmi Kıyas Sonuçları:**
  * **Claude Opus 5.5 vs Sonnet 5.5 (`SWE-bench Multimodal`):** Opus 5.5 **%61,4**, Sonnet 5.5 **%54,3**, Fable 5.1 **%52,0** ([anthropic.com/news](https://www.anthropic.com/news), Eylül 2026).
  * **GLM-5.3 (`FrontierSWE` & `NL2Repo`):** FrontierSWE **%78,1**, NL2Repo **%58,0**, SWE-Marathon v1.1 **%42,5**, CyberGym **%84,5** ([huggingface.co/zai-org/GLM-5.3](https://huggingface.co/zai-org/GLM-5.3), Ağustos 2026).
  * **DeepSeek-V4.1-Flash-1017 (`NL2Repo-Bench` & `ProgramBench`):** NL2Repo-Bench **%68,2** (Opus 5: %75,3, GLM-5.3: %58,0, GPT-5.6 Sol: %56,8); ProgramBench **%29,1** ([huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017), 2026-10-17).
  * **Gemini 4 Argon (`FrontierSWE v2` & `Terminal-Bench Science 0.1`):** FrontierSWE v2 **%55,0** (GPT-6 Astra: %65,5, Opus 5.5: %62,3, Fable 5.1: %56,3); Terminal-Bench Science 0.1 **%57,6** ([deepmind.google](https://deepmind.google/), 2026-09-30).
  * **Yerel Donanım Notu (`RTX 5070 Ti 12 GB`):** `Qwen3.5-9B` (Q4_K_M ~5.8 GB VRAM) 12 GB VRAM'e KV önbelleğiyle tamamen sığar. `Qwen3.6-35B-A3B` (35B toplam / 3B aktif MoE; Q4_K_M ~20 GB boyut) 12 GB VRAM'e tamamen sığmaz; ancak `llama.cpp` içinde `--n-gpu-layers` / uzman (expert) katmanlarının sistem RAM'ine (CPU+GPU hibrit MoE offload) paylaştırılmasıyla saniyede yalnızca 3B parametre aktif olduğundan yüksek hızda yerel olarak çalıştırılabilir.

---

## 3. Türkçe Yazım, Dilbilgisi ve Belge Kalitesini Ölçen Kıyas Setleri ve Yöntemler

Türkçe teknik belge üretimi, özetleme, dilbilgisi/yazım denetimi ve kavram doğruluğunu ölçmek için doğrulanmış başlıca açık kaynak kıyas setleri ve değerlendirme yöntemleri şunlardır:

1. **Cetvel (`KUIS-AI/cetvel` — Koç Üniversitesi KUIS AI Lab, 2024):**
   * **URL:** [https://github.com/KUIS-AI/cetvel](https://github.com/KUIS-AI/cetvel) · Makale: [https://arxiv.org/abs/2405.19129](https://arxiv.org/abs/2405.19129)
   * **Kapsam ve Önem:** EleutherAI `lm-evaluation-harness` üzerine kurulu en kapsamlı birleşik Türkçe LLM kıyas çerçevesidir. 7 görev kategorisini kapsar: **Türkçe Dilbilgisi Hata Düzeltme (Grammatical Error Correction - GEC)**, **Özetleme (Summarization)**, Makine Çevirisi, Çıkarımsal Soru-Cevap (QA), Çoktan Seçmeli QA (`Belebele`, `EXAMS`), Doğal Dil Çıkarımı (`XNLI-tr`) ve Metin Sınıflandırma.
2. **Mukayese (`alisafaya/mukayese` — ACL 2022 Findings):**
   * **URL:** [https://github.com/alisafaya/mukayese](https://github.com/alisafaya/mukayese) · Hugging Face: [https://huggingface.co/mukayese](https://huggingface.co/mukayese) · Makale: [https://aclanthology.org/2022.findings-acl.115/](https://aclanthology.org/2022.findings-acl.115/)
   * **Kapsam ve Önem:** Türkçe yazım ve belge kalitesi için doğrudan kullanılabilir üç kritik alt veri seti içerir:
     * **`TRSPELL-10`:** Türkçe yazım denetimi ve hata düzeltme (spell checking & correction) kıyas seti.
     * **`TRSEG-41`:** Türkçe cümle sınırlarını ve noktalama/bölümleme kalitesini ölçen veri seti.
     * **`MLSUM-tr` (`mlsum/tu`) & `trwiki-67`:** Türkçe haber/ansiklopedik metin özetleme (ROUGE-1/2/L, METEOR) ve dil modelleme veri setleri ([https://huggingface.co/datasets/mlsum](https://huggingface.co/datasets/mlsum)).
3. **TurkishMMLU (`ArdaYueksel/TurkishMMLU`) ve TR-MMLU (`erdometo/TR-MMLU`):**
   * **URL'ler:** [https://github.com/ArdaYueksel/TurkishMMLU](https://github.com/ArdaYueksel/TurkishMMLU) (EMNLP 2024 Findings, [https://arxiv.org/abs/2407.12406](https://arxiv.org/abs/2407.12406)) ve [https://huggingface.co/datasets/erdometo/TR-MMLU](https://huggingface.co/datasets/erdometo/TR-MMLU) ([https://arxiv.org/abs/2405.10448](https://arxiv.org/abs/2405.10448))
   * **Kapsam ve Önem:** İngilizce MMLU'nun makine çevirisi değil; doğrudan Türkiye eğitim müfredatından (Türk Dili ve Edebiyatı, Matematik, Fen, Sosyal Bilimler dahil 9–60+ alt dal, 6.200–10.000+ soru) derlenmiş özgün Türkçe dil/kavram hâkimiyeti testleridir.
4. **TR-MTEB (Turkish Massive Text Embedding Benchmark, 2024):**
   * **URL:** [https://huggingface.co/spaces/trmteb/leaderboard](https://huggingface.co/spaces/trmteb/leaderboard) · Koleksiyon: [https://huggingface.co/trmteb](https://huggingface.co/trmteb)
   * **Kapsam ve Önem:** Türkçe belge/cümle gömme (embedding), anlamsal benzerlik (STS), bilgi geri getirme (RAG/Retrieval) ve özet tutarlılığı ölçümü için standart kıyas setidir. Üretilen Türkçe belgelerin kaynak kod/dokümanla anlamsal örtüşmesini ölçmekte kullanılır.
5. **TurkBench ve TARA (Türkçe Yönerge Takibi ve Akıl Yürütme):**
   * **URL'ler:** [https://huggingface.co/turkbench](https://huggingface.co/turkbench) ([https://arxiv.org/abs/2407.03407](https://arxiv.org/abs/2407.03407)) ve [https://huggingface.co/datasets/emre/TARA_Turkish_LLM_Benchmark](https://huggingface.co/datasets/emre/TARA_Turkish_LLM_Benchmark)
   * **Kapsam ve Önem:** Üretken Türkçe modellerin karmaşık biçimsel kısıtlara (Markdown tablosu, maddeleme, uzunluk kısıtı) ve çok adımlı Türkçe yönergelere uyumunu ölçer.
6. **LLM-as-a-Judge (Yargıç LLM) Rubrikleri ve Çok Dilli Değerlendirme Çatıları:**
   * **Prometheus 2 (`prometheus-eval/prometheus-eval`):** 1–5 puanlık açık rubrik tanımlarıyla hem referanslı (reference-guided) hem referanssız değerlendirme yapan açık kaynak yargıç çerçevesi ([https://github.com/prometheus-eval/prometheus-eval](https://github.com/prometheus-eval/prometheus-eval), NAACL/EMNLP 2024).
   * **LMSYS MT-Bench & Arena-Hard-Auto:** İkili karşılaştırma (pairwise judge) ve 1–10 puanlama şablonları ([https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge) ve [https://github.com/lm-sys/arena-hard-auto](https://github.com/lm-sys/arena-hard-auto)).
   * **Aya Evaluation Suite (`CohereForAI/aya_evaluation_suite`):** Türkçe (`tur`) alt kümesi içeren çok dilli açık uçlu üretim ve LLM-yargıç değerlendirme veri seti ([https://huggingface.co/datasets/CohereForAI/aya_evaluation_suite](https://huggingface.co/datasets/CohereForAI/aya_evaluation_suite)).

---

## 4. Bizim Sistemimiz İçin Öneri: 5 Görev Türünde Gerçek Örnek Görevler ve Yerel Değerlendirme Düzeni

Aşağıda, makinenizdeki CLI ajanlarını (`Claude Code`, `Codex CLI`, `agy`, `opencode`, `llama.cpp`) gerçekçi ve tekrarlanabilir biçimde kıyaslamak üzere yukarıdaki veri setlerinden seçilmiş **gerçek görev kimlikleri (`instance_id` / `task_id`)** ve **doğrulama komutları** yer almaktadır.

### 4.1. Beş Görev Türü İçin 2–3 Gerçek Örnek Görev

#### Tür 1: Kod-Düzeltme + Test (Bug Fixing & Unit Test Verification)
1. **Görev 1.1 (`SWE-bench Verified` & `Lite`):**
   * **Repo & Kimlik:** `astropy/astropy` — `astropy__astropy-12907` ([GitHub Issue/PR #12907](https://github.com/astropy/astropy/pull/12907))
   * **Görev Özeti:** `astropy.modeling.separable` içinde iç içe geçmiş `CompoundModel` nesnelerinde `separability_matrix` hesaplamasının yanlış boolean matris üretmesi hatasının düzeltilmesi ve regresyon testinin geçirilmesi.
   * **Doğrulama Komutu:**
     ```bash
     python -m swebench.harness.run_evaluation --dataset_name SWE-bench/SWE-bench_Verified --predictions_path preds.jsonl --instance_ids astropy__astropy-12907 --max_workers 1 --run_id fix_astropy
     ```
2. **Görev 1.2 (`SWE-bench Verified` & `Lite`):**
   * **Repo & Kimlik:** `django/django` — `django__django-11099` ([GitHub PR #11099](https://github.com/django/django/pull/11099))
   * **Görev Özeti:** `ASCIIUsernameValidator` ve `UnicodeUsernameValidator` içindeki düzenli ifadelerin (`\Z` yerine `$` kullanımı nedeniyle) sonu yeni satır (`\n`) karakteriyle biten kullanıcı adlarını hatalı biçimde kabul etmesinin düzeltilmesi.
   * **Doğrulama Komutu:**
     ```bash
     python -m swebench.harness.run_evaluation --dataset_name SWE-bench/SWE-bench_Verified --predictions_path preds.jsonl --instance_ids django__django-11099 --max_workers 1 --run_id fix_django
     ```
3. **Görev 1.3 (`Terminal-Bench 2.0`):**
   * **Repo & Kimlik:** `laude-institute/terminal-bench` — `filter-js-from-html` ([https://github.com/laude-institute/terminal-bench](https://github.com/laude-institute/terminal-bench))
   * **Görev Özeti:** Konteyner içindeki HTML belgelerinden XSS/JavaScript vektörlerini yapısal DOM bozulmasına yol açmadan temizleyen bir komut satırı filtresi/betiği geliştirmek ve gizli `pytest` doğrulama paketini geçmek.
   * **Doğrulama Komutu:**
     ```bash
     harbor run -d terminal-bench@2.0 -e docker -a <cli_agent> -t filter-js-from-html
     ```

---

#### Tür 2: İnceleme (Code Review, Hata Teşhisi ve Kök Neden Bulma)
> **Yöntem:** Bu görevlerde ajana dosya yazma izni verilmez (`--read-only` / `/plan`); SWE-bench veya Multi-SWE-bench görevlerinin `base_commit` aşamasındaki kod tabanı (veya kasıtlı olarak bozulmuş bir PR diff'i) verilerek **hatalı dosya + fonksiyon/satır aralığı + kök nedenin** tespit edilmesi istenir.

1. **Görev 2.1 (`SWE-bench Verified` üzerinden Kök Neden & Konumlandırma İncelemesi):**
   * **Repo & Kimlik:** `sympy/sympy` — `sympy__sympy-20590` ([GitHub Issue #20590](https://github.com/sympy/sympy/issues/20590))
   * **Görev Özeti:** `Symbol('s').__dict__` davranışının 1.6.2'den 1.7'ye geçişte değişerek `Basic` alt sınıflarında beklenmeyen bir `__dict__` oluşturmasının hangi sınıf/miras zincirinden (`sympy/core/_print_helpers.py` içindeki `Printable` sınıfında `__slots__ = ()` eksikliği) kaynaklandığını kodda değişiklik yapmadan teşhis etmek.
   * **Doğrulama Komutu (Altın Yamadaki Hedef Dosya/Sembol Eşleşmesi):**
     ```bash
     python3 -c 'import json; d=json.load(open("review_sympy_20590.json")); assert "sympy/core/_print_helpers.py" in d["flagged_files"] and "__slots__" in d["root_cause"]'
     ```
2. **Görev 2.2 (`SWE-bench Multilingual` — Java Kod İncelemesi):**
   * **Repo & Kimlik:** `apache/druid` — `apache__druid-13704` ([https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual](https://huggingface.co/datasets/SWE-bench/SWE-bench_Multilingual))
   * **Görev Özeti:** Çok modüllü Java deposunda ilgili issue semptomuna yol açan sınıf ve metodu bularak yan etkileriyle birlikte inceleme raporu (`JSON` + açıklama) üretmek.
   * **Doğrulama Komutu:** Veri setindeki `patch` alanından çıkarılan gerçek değişen dosya/fonksiyon listesine karşı `Recall@3` (hedef dosyanın ilk 3 bulgu içinde yer alması) kontrol komutu.
3. **Görev 2.3 (`Multi-SWE-bench` — Rust CLI İncelemesi):**
   * **Repo & Kimlik:** `clap-rs/clap` — `clap-rs__clap-5520` ([https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench))
   * **Görev Özeti:** Rust argüman ayrıştırıcısında (`clap`) bildirilen davranış hatasının hangi modülde gerçekleştiğini ve önerilen yamanın hangi kenar durumlarını (edge-case) kırma riski taşıdığını incelemek.
   * **Doğrulama Komutu:** Altın yama (`fix_patch`) dosya yolu ve `test_patch` içindeki senaryolarla otomatik JSON anahtar doğrulaması.

---

#### Tür 3: Türkçe Belge (Teknik Dokümantasyon, API Belgesi ve Yazım Kalitesi)
1. **Görev 3.1 (`BigCodeBench-Hard` Görevlerinden Türkçe Teknik API Dokümantasyonu Üretimi):**
   * **Repo & Kimlik:** `bigcode-project/bigcodebench` — `BigCodeBench/0` ve `BigCodeBench/1` ([https://huggingface.co/datasets/bigcode/bigcodebench-hard](https://huggingface.co/datasets/bigcode/bigcodebench-hard))
   * **Görev Özeti:** `BigCodeBench/0` ve `BigCodeBench/1` görevlerinin `canonical_solution` Python kodunu girdi olarak verip; parametre tipleri, dönüş değerleri, istisnalar (exceptions) ve çalışma zamanı karmaşıklığını içeren **eksiksiz Türkçe Markdown API referans belgesi** üretmek.
   * **Doğrulama Komutu (Deterministik Yapı + Yargıç Rubriği):**
     ```bash
     python3 eval_tr_doc.py --source-task BigCodeBench/0 --doc-file out_tr_0.md --check-signatures --check-trspell
     ```
2. **Görev 3.2 (`Mukayese / TRSPELL-10` & `Cetvel / GEC` — Türkçe Yazım ve Dilbilgisi Düzeltme):**
   * **Repo & Kimlik:** `alisafaya/mukayese` (`TRSPELL-10` test dilimi) ve `KUIS-AI/cetvel` (`GEC` alt görevi) ([https://github.com/alisafaya/mukayese](https://github.com/alisafaya/mukayese), [https://github.com/KUIS-AI/cetvel](https://github.com/KUIS-AI/cetvel))
   * **Görev Özeti:** İçinde kasıtlı Türkçe ek-kök, şapka/تركçe karakter ve teknik terim yazım hataları bulunan metin/README parçalarını anlamı ve kod bloklarını bozmadan düzeltmek.
   * **Doğrulama Komutu:**
     ```bash
     lm_eval --model local-completions --tasks cetvel_gec --limit 20
     ```
3. **Görev 3.3 (`SWE-bench Verified` — Türkçe Sürüm Notu ve Mimari Değişiklik Belgesi / ADR):**
   * **Repo & Kimlik:** `django__django-11099` ve `astropy__astropy-12907` altın yamaları üzerinden Türkçe `CHANGELOG.md` ve Mimari Karar Kaydı (ADR) yazımı.
   * **Doğrulama Komutu:** Kod içindeki sembol adlarının (`ASCIIUsernameValidator`, `separability_matrix` vb.) birebir korunumu (deterministik regex denetimi) + 5 puanlık Türkçe LLM-as-a-Judge rubrik betiği.

---

#### Tür 4: Araştırma / Özet (Kod Tabanı Keşfi, Teknik Sentez ve Özetleme)
1. **Görev 4.1 (`Mukayese / MLSUM-tr` & `Cetvel` — Türkçe Uzun Metin Özetleme):**
   * **Repo & Kimlik:** `mlsum` (`tu` test bölümü, ilk 10 örnek: `mlsum_tu_test_000` – `009`) ([https://huggingface.co/datasets/mlsum](https://huggingface.co/datasets/mlsum))
   * **Görev Özeti:** Uzun Türkçe kaynak metinleri olgusal kayıp olmadan ve kaynakta geçmeyen iddia üretmeden özetlemek.
   * **Doğrulama Komutu:** `ROUGE-L` ve `TR-MTEB` Türkçe gömme (embedding) kosinüs benzerliği doğrulaması:
     ```bash
     python3 -c 'import evaluate; r=evaluate.load("rouge"); print(r.compute(predictions=open("pred.txt").readlines(), references=open("ref.txt").readlines()))'
     ```
2. **Görev 4.2 (`Multi-SWE-bench` — Çok Dosyalı Mimari Keşif ve Çağrı Grafiği Özeti):**
   * **Repo & Kimlik:** `fasterxml/jackson-databind` (`java/fasterxml__jackson-databind_dataset.jsonl` ilk görev) ([https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench](https://huggingface.co/datasets/ByteDance-Seed/Multi-SWE-bench))
   * **Görev Özeti:** Depo içinde serileştirme/deserileştirme (deserialization) hattında ilgili hatanın geçtiği tüm sınıf zincirini (`file:line` bağlantılarıyla) araştırıp özetlemek.
   * **Doğrulama Komutu:** Rapordaki tüm `[dosya]` bağlantılarının repoda gerçekten var olduğunu ve belirtilen satır aralıklarının ilgili metot tanımını kapsadığını doğrulayan AST/satır denetim betiği.
3. **Görev 4.3 (`Terminal-Bench 2.0` — Sistem ve Git Geçmişi Araştırması):**
   * **Repo & Kimlik:** `laude-institute/terminal-bench` — `git-multibranch` ([https://github.com/laude-institute/terminal-bench](https://github.com/laude-institute/terminal-bench))
   * **Görev Özeti:** Karmaşık dallanma ve reflog geçmişine sahip bir git deposunu terminal araçlarıyla araştırarak kayıp değişiklikleri bulup birleştirmek.
   * **Doğrulama Komutu:**
     ```bash
     harbor run -d terminal-bench@2.0 -e docker -a <cli_agent> -t git-multibranch
     ```

---

#### Tür 5: Mekanik Taşıma (Dil/Sürüm Taşıma, Refactoring ve Çok Dilli Portlama)
1. **Görev 5.1 (`Aider Polyglot Benchmark` — Python'dan Rust'a Birebir Davranış Taşıma):**
   * **Repo & Kimlik:** `Aider-AI/polyglot-benchmark` — `python/exercises/practice/pangram` $\rightarrow$ `rust/exercises/practice/pangram` ([https://github.com/Aider-AI/polyglot-benchmark](https://github.com/Aider-AI/polyglot-benchmark))
   * **Görev Özeti:** Çalışan Python referans uygulamasını Rust tip sistemine ve Exercism birim testlerine (`tests/pangram.rs`) uyacak şekilde mekanik olarak taşımak.
   * **Doğrulama Komutu:**
     ```bash
     cargo test --manifest-path polyglot-benchmark/rust/exercises/practice/pangram/Cargo.toml -- --include-ignored
     ```
2. **Görev 5.2 (`Aider Polyglot Benchmark` — Go'dan C++'a Birebir Taşıma):**
   * **Repo & Kimlik:** `Aider-AI/polyglot-benchmark` — `go/exercises/practice/binary-search` $\rightarrow$ `cpp/exercises/practice/binary-search` ([https://github.com/Aider-AI/polyglot-benchmark](https://github.com/Aider-AI/polyglot-benchmark))
   * **Görev Özeti:** Go dilindeki ikili arama modülünü C++ başlık (`.h`) ve kaynak (`.cpp`) dosyalarına taşıyıp CMake/CTest birim testlerini geçirmek.
   * **Doğrulama Komutu:**
     ```bash
     ./benchmark/benchmark.py local-port --keywords "binary-search" --num-tests 1
     ```
3. **Görev 5.3 (`BigCodeBench-Hard` — Kütüphane / API Refactoring Taşıması):**
   * **Repo & Kimlik:** `bigcode-project/bigcodebench` — `BigCodeBench/2` ([https://huggingface.co/datasets/bigcode/bigcodebench-hard](https://huggingface.co/datasets/bigcode/bigcodebench-hard))
   * **Görev Özeti:** Mevcut fonksiyonel çözümü tip anotasyonlu (`typing`), PEP-8 uyumlu ve modüler yardımcı fonksiyonlara ayrılmış yapıya mekanik olarak dönüştürürken orijinal `unittest` süitini %100 geçirmek.
   * **Doğrulama Komutu:**
     ```bash
     bigcodebench.evaluate --split instruct --subset hard --samples migrated_samples.jsonl --execution local --selective_evaluate 2
     ```

---

### 4.2. Küçük, Tekrarlanabilir ve Kota-Farkında Yerel Değerlendirme Düzeni

RTX 5070 Ti (12 GB VRAM) bulunan Ubuntu makinenizde, abonelik kotalarını tüketmeden tüm CLI ajanlarını (`Claude Code`, `Codex CLI`, `agy`, `opencode`, `llama.cpp`) objektif biçimde kıyaslayacak yerel değerlendirme mimarisi:

| Parametre | Önerilen Değer / Ayar | Gerekçe |
| :--- | :--- | :--- |
| **Toplam Görev Sayısı** | **15 Görev** (5 kategori × 3 görev) | Tam SWE-bench (500 görev) abonelik kotalarını tek oturuşta bitirir; 15 seçilmiş temsilci görev (katmanlı mikro-paket) hem hızlıdır hem de 5 görev türünü dengeli ölçer. |
| **Tekrar Sayısı ($k$)** | **$k = 3$ tekrar** (toplam 45 görev koşumu / ajan) | Sıcaklık ($T > 0$) ve ajan araç çağrılarındaki stokastik sapmaları yakalamak için hem **`pass@1`** (ortalama başarı) hem de **`pass^3`** (3 denemenin 3'ünde de tutarlı başarı — üretim güvenilirliği) hesaplanır. |
| **Temel Metrikler** | 1. **Çözüm Oranı (`Resolved %` / `pass@1`)**<br>2. **Kararlılık (`pass^3 %`)**<br>3. **Görev Başı Duvar Saati Süresi (sn)**<br>4. **Kota / İstek Tüketimi (mesaj veya tur sayısı)**<br>5. **Türkçe Kalite Skoru (1–5 Rubrik + Deterministik Linter)** | Koordinatörün hangi işi hangi CLI'a yönlendireceğine karar vermesi için "kalite × kararlılık × süre × kota maliyeti" matrisini üretir. |
| **Türkçe Belge Yargıç Düzeni** | **Çift Yargıç (Dual-Judge) + Deterministik Ön-Filtre** | 1) Önce Python betiğiyle kod imzalarının ve Markdown yapısının bozulmadığı deterministik olarak denetlenir.<br>2) Ardından bulut kotası harcamadan yerel `Qwen3.6-35B-A3B` (`llama.cpp`) + ikinci bağımsız yargıç olarak `agy` (`Gemini 3.8 Flash`) üzerinden Prometheus-tarzı 1–5 puanlık rubrik (Dilbilgisi, Terim Tutarlılığı, Olgusal Sadakat, Biçim) koşulur. |
| **Yerel Donanım (`RTX 5070 Ti 12 GB`) Ayarı** | • `Qwen3.5-9B-GGUF` (`Q4_K_M`, ~5.8 GB): `%100 VRAM` (`-ngl 99`, `32K` bağlam)<br>• `Qwen3.6-35B-A3B-GGUF` (`Q4_K_M`, ~20 GB): **MoE Hibrit Offload** (`--n-gpu-layers 99 --override-tensor "\.ffn_.*_exps\.=CPU"`, dikkat/attention katmanları 12 GB VRAM'de, seyrek MoE uzmanları sistem RAM'inde) | 12 GB VRAM sınırında `Qwen3.6-35B-A3B` modelini OOM (bellek taşması) olmadan yüksek hızda (aktif parametre yalnızca 3B olduğu için) koşturmanın standart `llama.cpp` yoludur. |
| **Kota Bütçesi ve ToS Uyumlu Yürütme** | **2 Günlük / 4 Dilimli Kademeli Koşum (Staggered Run):**<br>• **Yerel (`llama.cpp`) & `opencode` (ücretsiz):** Kotasız; 45 koşum tek seferde (~1.5–2 saat) tamamlanır.<br>• **`Claude Code` (Max) & `agy` (AI Ultra):** 5 saatlik kayan pencere (rolling window) kotalarını %25'in üzerinde tüketmemek için her pencere diliminde en fazla **12–15 görev koşumu** yapılır.<br>• **`Codex CLI` (ChatGPT Plus):** Plus kotası en dar halka olduğundan yalnız **Kod-Düzeltme, İnceleme ve Mekanik Taşıma** alt kümelerinde (9 görev × 3 tekrar = 27 koşum, 2 pencereye bölünmüş) değerlendirilir. | Tüm çağrılar yalnızca resmi CLI'ların kendi etkileşimsiz (non-interactive / headless) bayraklarıyla (`claude -p "..."`, `codex exec "..."`, `agy ...`, `opencode run "..."`, `llama-cli / llama-server`) yapılır; hiçbir abonelik token'ı dışarı çıkarılmaz (ToS %100 uyumlu). |

### 4.3. Değerlendirme Sonuçlarına Göre Önerilen Görev Dağıtım (Yönlendirme) Eşikleri
Yerel 15 görevlik değerlendirme düzeni tamamlandığında koordinatör (`Claude Code`) şu karar kuralını uygular:
1. **`pass^3 == %100`** olan en düşük maliyetli (önce yerel `Qwen3.6-35B-A3B` / `Qwen3.5-9B`, sonra `opencode`, sonra `agy Gemini 3.8 Flash`) işçi ilgili görev türüne (ör. *Mekanik Taşıma* veya *Türkçe Belge*) birincil olarak atanır.
2. Yalnızca çok dosyalı **Kod-Düzeltme + Test** ve **Derin Mimari İnceleme** görevlerinde yerel model `pass^3 < %67` kalırsa görev kotalı sınır CLI'lara (`Claude Code Opus/Sonnet 5.5`, `agy Gemini 4 Argon` veya `Codex CLI GPT-6.1 Sol`) yükseltilir (escalation).
