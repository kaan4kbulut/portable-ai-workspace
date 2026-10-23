@00-cekirdek/AGENTS.md

# Atölye: bu depoya özel kurallar

Ortak kurallar `00-cekirdek/AGENTS.md` dosyasındadır; önce onu oku ve uy. (Claude üstteki `@` satırıyla
otomatik yükler; Codex, opencode ve agy için bu düz metin yönlendirmedir.)

Bu depo kullanıcının **atölyesi**: beyni, araçları, çalışma masası. Hangi makineye taşınırsa taşınsın aynı
şekilde çalışmalıdır. Harita `README.md`'de, düzen kuralları `00-cekirdek/ANAYASA.md`'de.

1. **ANAYASA'ya uy.** `00-cekirdek/ANAYASA.md` yalnızca insan tarafından düzenlenir; sen düzenlemezsin, değişiklik
   önerirsin. Adlandırma, derinlik ve "ne nereye gider" kuralları oradadır.
2. **Ne nereye gider tablosuna bak** (`README.md`). Yeri kesin olmayan her şey `70-gelen-kutusu/`'na gider; asla köke,
   asla rastgele bir bölüme.
3. **Karar → `/karar`** becerisi ile `40-hafiza/kararlar/KARARLAR.md`'ye. Kararı sohbette bırakma.
4. **Oturum biterken → `/kapat`** becerisi ile `40-hafiza/oturumlar/`'a devir notu. Başka makinede devam etmenin tek yolu budur.
5. **Depo içinde symlink yok, `./betik` çağrısı yok.** Betikler `bash yol/betik.sh` ile çağrılır (USB/exFAT uyumu).
   Mutlak yol yazma; `$CLAUDE_PROJECT_DIR` ya da betiğin kendi konumundan göreli çöz.
6. **Taşı, silme.** Kaldırılan her şey `60-arsiv/YYYY-MM-DD-<ad>/` + `NEDEN.md`.
7. **Yeni bölüm/araç açmadan önce ara:** `60-arsiv/`, `70-gelen-kutusu/`, `40-hafiza/`, `gh repo list`. Aynı işi yapan
   ikinci şey açılmaz.
8. **Düzen sorunu görürsen** `/bakim` ya da `bash 10-sistem/bakim/bakim.sh`; çözümü `10-sistem/bakim/bilinen-sorunlar.md`'ye yaz.
9. Kimlik dosyalarını (`~/.claude/.credentials.json`, `~/.codex/auth.json`, `~/.gemini/`) okuma; giriş durumunu
   yalnızca aracın kendi komutuyla sor.
