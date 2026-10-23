# portable-ai-workspace

**Taşınabilir yapay zekâ çalışma alanı** — Claude Code, Codex, opencode ve benzeri CLI ajanları için işletim sistemi gibi
katmanlı, kendi kendine yeten, USB'ye koyup başka bilgisayarda aynı disiplinle devam edebileceğiniz bir klasör düzeni.
Kurallar + hafıza + araç ayarları + projeler + arşiv tek yerde; her makinede yalnızca giriş yapılır.

> A portable, self-contained workspace layout for AI coding agents (Claude Code, Codex, opencode).
> Rules, memory, tool config, projects and archive travel together; only logins stay per machine. Turkish docs; the
> structure is language-agnostic. See the table at the bottom for an English overview.

## Hızlı başlangıç

```bash
git clone https://github.com/kaan4kbulut/portable-ai-workspace.git ~/atolye
cd ~/atolye
claude                  # klasörde çekirdek ajanı açın
```
`claude` içinde `/kur` çalıştırın: ajan adını klasör adından (`atolye`) önerir, onayınızla kurar.
Pano ve menü `/<ad>` komutudur; ad `00-cekirdek/kimlik.json` içinde tutulur.
Sonra her CLI'a **o makinede** kendi girişinizle girin (`claude` → `/login`, `codex login`, `opencode auth login`).
Gün başı `/baslat`, gün sonu `/kapat`. Diğer komutlar: `/karar`, `/ayikla`, `/denetle`, `/bakim`.
Başka CLI için proje klasöründe ilgili CLI'ı açın veya `/araclar <arac> <görev>` kullanın.

## Yapı

| Katman | İçerik |
|---|---|
| `00-cekirdek/` | ANAYASA, AGENTS, PLAN, `sablonlar/` |
| `10-donanim/` | makine sayfaları, profiller ve makineye özgü kurulum |
| `20-sistem/` | kurulum, denetim, bakım, ağ, servisler, yayın; durum* ve günlük* |
| `30-programlar/` | CLI ve uygulamalar, ayarlar, yerel modeller; dış klonlar* |
| `40-projeler/` | DIZIN, şablon, aktif projeler* ve denemeler* |
| `50-arayuz/` | komut kataloğu, pano, durum satırı, harita ve uzaktan erişim |
| `60-hafiza/` | kararlar, devir notları, dersler, tercihler |
| `70-kutuphane/` | bilgi belgeleri |
| `80-arsiv/` | emekliler ve NEDEN.md |
| `90-gelen-kutusu/` | sınıflanmamış öğeler; haftalık `/ayikla` |

Kökteki `.claude/` araç kapsamı arayüz katmanına aittir.

## Neden böyle

- **Kendi kendine yeten:** mutlak yol yok, symlink yok, `./betik` yok; klasörü taşıyın, içinde `claude` açıp yeni makinede `/kur` çalıştırın.
- **Kurallar veri:** denetim kuralları `20-sistem/denetim/kurallar/*.txt`; bakım ajanı yeni kural ekleyebilir.
- **Gömülü bakım ajanı:** `bakim.sh` denetim bulgularını CLI'a verir; onarır, öğrendiğini `bilinen-sorunlar.md`,
  `ogrenilenler/` ve `onarimlar/` içine yazar. Aynı sorun iki kez elle çözülmez.
- **Hafıza araçta değil klasörde:** Claude auto-memory kapalı; süreklilik `60-hafiza/oturumlar/` devir notlarından.
- **Yeniden yazma yasağı:** git geçmişi korunur, karar silinmez "geçersiz" işaretlenir, kaldırılan şey arşivde `NEDEN.md` ile durur.
- **Güvenlik:** `yikici-koruma.py` (rm -r, reset --hard, force push, curl|sh, kimlik dosyası okuma engeli),
  ANAYASA yalnız insan, sır taraması pre-commit'te.

## Uyarlama

1. `00-cekirdek/ANAYASA.md` ve `AGENTS.md`'yi okuyun; dilinizi/kurallarınızı değiştirin (ANAYASA'yı elle).
2. `10-donanim/ornek/` klasörünü makinenizin adıyla kopyalayın, `profil.md` içine `hostname:` yazın.
3. Projelerinizi `40-projeler/aktif/<ad>/` altına klonlayın (`sablon/`'dan `CLAUDE.md`, `AGENTS.md`, `DURUM.md` alın), `DIZIN.md`'ye satır ekleyin.
4. Kendi kararlarınızı `/karar`, oturum sonlarını `/kapat` ile yazın.

## English overview

| Dir | Role |
|---|---|
| `00-cekirdek` | kernel: constitution (human-only), shared agent rules, plan |
| `20-sistem` | init/services: idempotent setup, structure checks (rules as data), embedded maintenance agent, device profiles |
| `30-programlar` | per-tool config kept in git, MCP definitions, local model registry |
| `40-projeler` | each project its own repo; index + template |
| `60-hafiza` | decisions, session handover notes, lessons, preferences |
| `70-kutuphane` · `80-arsiv` · `90-gelen-kutusu` · `00-cekirdek/sablonlar` · `30-programlar/dis-kaynaklar` | library · archive (move, never delete) · inbox · templates · external clones |

Entry: clone → open `claude` in the folder → `/kur` (agent name suggested from the folder name).
Daily: `/baslat`, `/kapat`; dashboard: `/<ad>`. Requirements: Claude Code, bash, git, python3, curl, rsync.
İç araçlar: `bash 20-sistem/kurulum/kur.sh`, `bash 20-sistem/denetim/denetle.sh`.

Lisans: MIT.
