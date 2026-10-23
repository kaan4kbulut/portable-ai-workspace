---
katman: programlar
surum: 2.6.12
son_kontrol: 2026-10-23
kaynaklar: [https://ccsafetynet.com/docs, https://github.com/kenryu42/cc-safety-net]
baglar: [../README.md, ../../10-donanim/monster/README.md, ../claude-code/README.md, ../codex/README.md, ../agy/README.md]
---

# CC Safety Net (`cc-safety-net`)

## Nedir
Kodlama ajanlarının çalıştırmak istediği kabuk komutlarını ve dosya erişimlerini yürütme öncesinde ayrıştırarak (command parsing) yıkıcı işlemleri ve sır erişimini engelleyen güvenlik kapısıdır (`cc-safety-net v2.6.12`, MIT lisanslı).

## Atölyedeki rolü
- **Çift katmanlı yıkıcı komut korumasının birinci katmanı:** Regex tabanlı hook'ların kaçırdığı kabuk sarmalamalarını (`bash -c`, `/bin/rm`, `r''m`, argüman sırası değiştirme), yıkıcı `git`/`rm`/`sudo` komutlarını ve `.env`/SSH özel anahtar erişimlerini ayrıştırıcı tabanlı olarak engeller (`60-hafiza/kararlar/KARARLAR.md`, `60-hafiza/ogrenilenler/claude-code.md`).
- İkinci katman olan atölye hook'u (`.claude/hooks/yikici-koruma.py` ve `anayasa-koruma.py`) ise "taşı-silme", `ANAYASA.md` koruma, symlink yasağı ve proje dışı yazma gibi atölyeye özgü kuralları uygular; ikisi birbirini tamamlar.

## Kurulum ve giriş
- Kurulum betiği: `bash 20-sistem/kurulum/araclar/cc-safety-net.sh` (Node/npm üzerinden `npm install -g cc-safety-net@2.6.12`).
- **Tedarik zinciri politikası:** Sürüm sabittir (`2.6.12`); yalnızca en az 7 günlük yayınlanmış sürümler, changelog incelendikten sonra yükseltilir (`dcg` aracı lisans kısıtı nedeniyle tercih edilmemiştir).
- Giriş veya ağ bağlantısı gerektirmez; tamamen yerel çalışır.

## Etkileşimsiz çağırma
`cc-safety-net --help` ve `cc-safety-net hook --help` ile bu makinede doğrulanan komutlar:
```bash
cc-safety-net status
cc-safety-net doctor
cc-safety-net explain "git reset --hard HEAD~1"
cc-safety-net logs
cc-safety-net hook --coding-cli
```
- Desteklenen hook entegrasyon bayrakları (`cc-safety-net hook`): `-cc`/`--coding-cli` (Claude Code `.claude/settings.json` içinde kullanılan), `-cx`/`--codex`, `-ac`/`--agy-cli`, `-gc`/`--gemini-cli`, `-cu`/`--cursor`, `-cp`/`--copilot-cli`.
- Ortam değişkenleri: `CC_SAFETY_NET_LEVEL=standard|strict|paranoid`, `CC_SAFETY_NET_WORKTREE=1`, `CC_SAFETY_NET_AUDIT_SCOPE=all|blocked`, `CC_SAFETY_NET_PROJECT_TIGHTEN_ONLY=1`, `CC_SAFETY_NET_HOME`.

## Okuduğu dosyalar
`cc-safety-net status` ve `cc-safety-net rule doc` ile doğrulanan yapılandırma yolları:
- **Politika dosyaları:** Kullanıcı genelinde `~/.cc-safety-net/policy.json`, proje kapsamında `.cc-safety-net/policy.json` (`cc-safety-net policy check/apply`).
- **Özel kural kitapları (canlı okunur):**
  1. Kullanıcı kapsamı (öncelikli): `~/.cc-safety-net/rules/rule.json` ve `~/.cc-safety-net/rules/<kural-kitabi>/rulebook.json`.
  2. Proje kapsamı: `.cc-safety-net/rules/rule.json` ve `.cc-safety-net/rules/<kural-kitabi>/rulebook.json`.
- **Atölye bağlantısı:** `.claude/settings.json` içindeki `PreToolUse` (`Bash|Read|Grep|Glob|Edit|Write|MultiEdit|NotebookEdit`) kancasında `cc-safety-net hook --coding-cli` olarak tanımlıdır.

## Dikkat
- **Sandbox değildir:** İşletim sistemi düzeyinde süreç yalıtımı veya ağ filtrelemesi yapmaz; yalnızca ajan araç çağrısını (`PreToolUse`) denetler. Kritik dosyalar için dosya sistemi izni (`chmod 444 00-cekirdek/ANAYASA.md`) üçüncü katman olarak korunur.
- **Kural daraltma ilkesi:** Özel kurallar yalnızca ek kısıtlama getirebilir, yerleşik çekirdek korumaları gevşetemez; proje kuralları kullanıcı kapsamındaki kuralları ezemez.

## Eksikler
- `cc-safety-net status` çıktısında görülen "plugin cc-safety-net@cc-marketplace is disabled in Claude Code" uyarısının `.claude/settings.json` doğrudan hook çağrısıyla ilişkisi `20-sistem/denetim/testler/hook-testleri.py` ile doğrulanacak.
- Gerekirse Codex (`--codex`) ve agy (`--agy-cli`) için de aynı PreToolUse hook bağlantısının `kur.sh --genel`'e eklenmesi değerlendirilecek.
