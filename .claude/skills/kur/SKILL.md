---
name: kur
description: >-
  Bir makinede ilk kurulumu yapar - ajan adını önerir, kimlik.json ve ana menü becerisini üretir, kur.sh'i çalıştırır.
  "kur", "ilk kurulum", "bu makineyi hazırla", "ajanın adı ne olsun" dendiğinde ya da 20-sistem/durum/HOST/ilk-kurulum.txt yoksa kullan.
---
# /kur — ilk kurulum

1. `hostname -s` al. `20-sistem/durum/<host>/ilk-kurulum.txt` varsa "bu makine kurulu" de; yalnızca kullanıcı isterse
   (yeniden kurulum) devam et. Yoksa ilk kurulumdur.
2. **Ad doğrulama** (hem kimlik.json'daki hem önerilen ad için): `^[a-z0-9][a-z0-9-]{1,40}$` ile eşleşmeli ve şu adlarla
   çakışmamalı: mevcut beceri/komutlar (`kur baslat kapat araclar programlar donanim projeler yayinla karar ayikla denetle bakim kutuphane`),
   `.claude/skills/` ve `.claude/agents/` altında başka amaçlı klasör/dosya, Claude Code yerleşik komutları
   (`help model config agents init review clear compact status memory mcp login logout doctor`). Geçersizse reddet, nedenini söyle.
   `00-cekirdek/kimlik.json` varsa `ad` değerini oku, doğrula ve **4. adıma geç** (idempotent: yeniden çalıştırmak zararsız).
   Yoksa ad öner: depo klasör adının (`basename "$CLAUDE_PROJECT_DIR"`) küçük harfli, aksansız, kebab-case hali
   (boşluk/alt çizgi `-` olur). Kullanıcıya göster, **onay al** ya da başka ad iste.
3. `00-cekirdek/kimlik.json` yaz: `{"ad": "<ad>", "kurulum": "<YYYY-MM-DD>", "makine_ilk": "<host>"}`.
4. `00-cekirdek/sablonlar/beceri/ana-menu.md` içindeki `{{ad}}` yerine adı koyarak
   `.claude/skills/<ad>/SKILL.md` üret. Aynı dosya zaten varsa ve içerik aynıysa atla; farklıysa üzerine yazmadan önce farkı göster.
5. `.claude/agents/<ad>.md` üret (varsa aynı kuralla); **yalnızca frontmatter, gövde BOŞ**:
   ```
   ---
   name: <ad>
   description: "<ad> çekirdek ajanı, atölyenin ana ajanı."
   model: inherit
   ---
   ```
   Gövde boş kalır, çünkü dolu gövde Claude Code'un varsayılan sistem istemini değiştirir; kurallar zaten
   `CLAUDE.md` → `AGENTS.md` zincirinden yüklenir.
6. Kullanıcıya söyle: `.claude/settings.json` içine `"agent": "<ad>"` satırını **kendisi** eklemeli (ajan kendi
   ayar/izin dosyasını düzenlemez). Sonra `claude`'u depo kökünde yeniden başlatınca çekirdek ajan açılır.
7. `bash 20-sistem/kurulum/kur.sh` çalıştır (`ilk-kurulum.txt`'i o yazar); çıktıyı özetle: kurulanlar, uyarılar, eksik araçlar.
8. Özet (5 satır): ad, üretilen dosyalar, kur.sh sonucu, kullanıcının yapacağı tek iş (settings satırı), sonraki komut `/<ad>`.
   Commit önerisi sun; kullanıcı istemeden commit/push yapma.
