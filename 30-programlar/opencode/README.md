---
katman: programlar
surum: 2.1.3
son_kontrol: 2026-10-23
kaynaklar: [https://opencode.ai/docs, https://github.com/anomalyco/opencode]
baglar: [../README.md, ../../10-donanim/monster/README.md, ../claude-code/README.md, ../yerel-modeller/README.md, ../mcp/README.md]
---

# OpenCode (`opencode`)

## Nedir
Açık kaynaklı (`anomalyco/opencode`), çoklu model sağlayıcısını ve yerel modelleri destekleyen terminal kodlama ajanıdır (`opencode v2.1.3`).
İstemci/sunucu mimarisiyle hem etkileşimli TUI hem de tek komutluk (`opencode run`) çalışma sunar.

## Atölyedeki rolü
- **Ücretsiz, API veya yerel model işçisi:** Yalnızca ücretsiz modeller, açık API anahtarlı sağlayıcılar veya MONSTER üzerindeki yerel model sunucusu (`llama-server`) ile yardımcı görevlerde kullanılır (`00-cekirdek/AGENTS.md`, `60-hafiza/kararlar/KARARLAR.md`).
- Çekirdekte (atölye kökünde) doğrudan çalıştırılmaz; çekirdek ajan tarafından hedef proje dizininde ve izin kurallarıyla sınırlandırılmış olarak çağrılır.
- Kaynak kodu inceleme amacıyla `30-programlar/dis-kaynaklar/` altında klonlanmıştır.

## Kurulum ve giriş
- Kurulum betiği: `bash 20-sistem/kurulum/araclar/opencode.sh` (`https://opencode.ai/install` ile `~/.opencode/bin/opencode` altına kullanıcı-yerel kurar).
- Giriş yalnızca aracın kendi komutuyla yapılır: `opencode auth login` (durum kontrolü: `opencode auth list`).
- Kimlik ve servis dosyaları (`~/.config/opencode/service.json`, `~/.local/share/opencode/`) asla depoya alınmaz ve `opencode auth export` çıktısı paylaşılmaz.

## Etkileşimsiz çağırma
`opencode --help` ve `opencode run --help` ile bu makinede doğrulanan bayraklar:
```bash
opencode run -m provider/model "istem"
opencode run -m provider/model --format json --auto "istem"
opencode run --agent review -f dosya.py "Bu dosyayı incele"
```
- Seçenekler (`opencode run`): `-m`/`--model <provider/model#variant>`, `--agent <ad>`, `--format <default|json>`, `-f`/`--file <dosya>`, `--auto` (açıkça reddedilmeyen izinleri otomatik onayla), `--thinking`, `--title <başlık>`, `-c`/`--continue`, `-s`/`--session <id>`, `--fork`, `--standalone` (arka plan servisi yerine özel sunucuyla çalıştır), `--server <url>`, `--log-level`, `--print-logs`.
- Not: `opencode run` alt komutunda `--dir` bayrağı yoktur (ana `opencode [flags] [<directory>]` komutunda konum argümanı vardır); etkileşimsiz çağrıda hedef projeye `cd` ile geçilerek çalıştırılır.

## Okuduğu dosyalar
- **Ayarlar (`opencode.json` / `opencode.jsonc`):** Proje kökünde `opencode.json` (atölyede `"instructions": ["00-cekirdek/AGENTS.md", "AGENTS.md"]` içerir) ve kullanıcı düzeyinde `~/.config/opencode/opencode.json` (`kur.sh --genel` ile `30-programlar/opencode/genel/opencode.json` dosyasına bağlanır).
- **Kurallar (`AGENTS.md`):** Proje kökündeki `AGENTS.md`, `opencode.json` `instructions` dizisindeki dosyalar ve global `~/.config/opencode/AGENTS.md` (`kur.sh --genel` ile `00-cekirdek/AGENTS.md`'ye bağlanır).
- **Makine-yerel (depoya girmez):** `~/.config/opencode/service.json`, `~/.local/share/opencode/`, `~/.opencode/`.

## Dikkat
- **Kota ve ToS (Kesin kural 1):** Anthropic (Claude Pro/Max) ve Google abonelik girişleri üçüncü taraf araçlarda kullanılamaz; OpenCode içinde yalnızca resmi API anahtarları, ücretsiz modeller veya yerel `llama-server` uç noktası kullanılır.
- **OpenAI girişi uyarısı:** Mevcut OpenAI girişinin abonelik (ChatGPT Plus OAuth) mi yoksa API anahtarı mı olduğu kullanıcı tarafından doğrulanmalıdır; abonelikse Kesin kural 1 sınırındadır.
- **Eski global kural dosyası:** `~/.config/opencode/AGENTS.md` içindeki eski İngilizce dosya `80-arsiv/`'e taşınıp ortak Türkçe `00-cekirdek/AGENTS.md`'ye bağlanacaktır.

## Eksikler
- `30-programlar/opencode/genel/opencode.json` dosyasının (izin listesi + review ajanı) mevcut makine ayarından temizlenerek depoya alınması (Plan Aşama C).
- KARARLAR.md'de geçen `opencode run --dir` ifadesinin `opencode v2.1.3`'te desteklenmediği (`opencode run --help` ile) doğrulandı; çağrıcı betiklerde `cd <proje> && opencode run` kullanılmalı.
