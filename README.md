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
bash basla.sh            # ilk açılış: kurulum (eksik araçlar, git ayarı), denetim, pano, sonra claude
```
Sonra her CLI'a **o makinede** kendi girişinizle girin (`claude` → `/login`, `codex login`, `opencode auth login`).
Gün sonu: `bash kapat.sh`. Claude içinde: `/baslat`, `/kapat`, `/karar`, `/ayikla`, `/denetle`, `/bakim`.

## Yapı

| Bölüm | Benzetme | İçerik |
|---|---|---|
| `00-cekirdek/` | kernel | `ANAYASA.md` (düzen kuralları, yalnız insan), `AGENTS.md` (ajan kuralları), `PLAN.md` |
| `10-sistem/` | init + servisler | `kurulum/kur.sh`, `denetim/denetle.sh` (kurallar veri olarak), `bakim/` (gömülü bakım ajanı), `cihazlar/`, `ag/`, `servisler/`, `durum/` |
| `20-araclar/` | programlar | her CLI'ın git'te duran ayarı, MCP tanımları, yerel modeller kaydı |
| `30-projeler/` | kullanıcı alanı | her proje ayrı repo; `DIZIN.md` indeks; `sablon/` |
| `40-hafiza/` | durum/kayıt | kararlar, oturum devir notları, öğrenilenler, tercihler, cihazlar |
| `50-kutuphane/` | belgeler | araçlar, modeller, sağlayıcılar, teknoloji, bilgi |
| `60-arsiv/` | — | emekliler, tarih önekli, `NEDEN.md` ile ("taşı, silme") |
| `70-gelen-kutusu/` | kuyruk | sınıflanmamış her şey; haftalık ayıklama |
| `80-sablonlar/` | — | belge, bölüm, beceri şablonları |
| `90-dis-kaynaklar/` | mount | dış klonlar (git dışı) |
| `.claude/` | — | kendi kendine yeten Claude Code kapsamı: ayarlar, kurallar, beceriler, ajanlar, hook'lar |

## Neden böyle

- **Kendi kendine yeten:** mutlak yol yok, symlink yok, `./betik` yok; klasörü taşıyın, `bash basla.sh` deyin.
- **Kurallar veri:** denetim kuralları `10-sistem/denetim/kurallar/*.txt`; bakım ajanı yeni kural ekleyebilir.
- **Gömülü bakım ajanı:** `bakim.sh` denetim bulgularını CLI'a verir; onarır, öğrendiğini `bilinen-sorunlar.md`,
  `ogrenilenler/` ve `onarimlar/` içine yazar. Aynı sorun iki kez elle çözülmez.
- **Hafıza araçta değil klasörde:** Claude auto-memory kapalı; süreklilik `40-hafiza/oturumlar/` devir notlarından.
- **Yeniden yazma yasağı:** git geçmişi korunur, karar silinmez "geçersiz" işaretlenir, kaldırılan şey arşivde `NEDEN.md` ile durur.
- **Güvenlik:** `yikici-koruma.py` (rm -r, reset --hard, force push, curl|sh, kimlik dosyası okuma engeli),
  ANAYASA yalnız insan, sır taraması pre-commit'te.

## Uyarlama

1. `00-cekirdek/ANAYASA.md` ve `AGENTS.md`'yi okuyun; dilinizi/kurallarınızı değiştirin (ANAYASA'yı elle).
2. `10-sistem/cihazlar/ornek/` klasörünü makinenizin adıyla kopyalayın, `profil.md` içine `hostname:` yazın.
3. Projelerinizi `30-projeler/aktif/<ad>/` altına klonlayın (`sablon/`'dan `CLAUDE.md`, `AGENTS.md`, `DURUM.md` alın), `DIZIN.md`'ye satır ekleyin.
4. Kendi kararlarınızı `/karar`, oturum sonlarını `/kapat` ile yazın.

## English overview

| Dir | Role |
|---|---|
| `00-cekirdek` | kernel: constitution (human-only), shared agent rules, plan |
| `10-sistem` | init/services: idempotent setup, structure checks (rules as data), embedded maintenance agent, device profiles |
| `20-araclar` | per-tool config kept in git, MCP definitions, local model registry |
| `30-projeler` | each project its own repo; index + template |
| `40-hafiza` | decisions, session handover notes, lessons, preferences |
| `50-kutuphane` · `60-arsiv` · `70-gelen-kutusu` · `80-sablonlar` · `90-dis-kaynaklar` | library · archive (move, never delete) · inbox · templates · external clones |

Entry: `bash basla.sh` (first run installs missing user-local tools, never logs in). Requirements: bash, git, python3, curl, rsync.

Lisans: MIT.
