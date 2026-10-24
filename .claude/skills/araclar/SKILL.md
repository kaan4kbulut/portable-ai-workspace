---
name: araclar
description: >-
  Kurulu CLI araçlarını (claude, codex, opencode, agy, gh, cc-safety-net) sürüm, giriş durumu ve rolleriyle listeler;
  "/araclar ARAC GOREV" ile ilgili CLI'ı etkileşimsiz çalıştırır. "araçlar", "codex'e sor", "agy ile çalıştır", "hangi araç kurulu" dendiğinde kullan.
argument-hint: "[<arac> <görev>]"
---
# /araclar — CLI'lar

## Argümansız: envanter
Her araç için sürüm (`<arac> --version`) ve giriş durumu. Giriş yalnızca aracın kendi komutuyla sorulur; kimlik dosyası asla okunmaz.

| Araç | Giriş sorgusu | Rol | Kota notu |
|---|---|---|---|
| claude | kullanıcıya `/status` denetlet | çekirdek ajan, yazım, planlama | Claude Max 5x: geniş |
| codex | `codex login status` | inceleme, zor hatalar | ChatGPT Plus: **kıt**, yalnızca inceleme/zor hata |
| opencode | `opencode auth list` | çok sağlayıcılı, yerel model (MONSTER llama-server) | sağlayıcıya bağlı |
| agy | yalnızca sürüm | Gemini tabanlı, uzun bağlam/araştırma | Google AI Ultra: geniş |
| gh | `gh auth status` | GitHub, yayın | — |
| cc-safety-net | sürüm; hook `.claude/settings.json`'da kayıtlı mı | yıkıcı komut koruması | — |

Kurulu olmayanı "yok" yaz; kurulum yeri `30-programlar/<arac>/` ya da `20-sistem/kurulum/araclar/<arac>.sh`.
Çıktı: araç · sürüm · giriş (var/yok/bilinmiyor) · rol, altında kota notu.

## `/araclar <arac> <görev>`: çalıştır
0. Abonelikler yalnızca her aracın resmi CLI'ında, kendi girişiyle kullanılır; anahtar/oturum hiçbir aracıya (ağ geçidi, proxy, başka CLI) verilmez.
1. Çalışma klasörünü seç: görev bir projeyse `40-projeler/aktif/<ad>/`. Yazma gerektiriyorsa **asla depo kökü**; kök yalnızca salt okunur sorulara.
   Belirsizse kullanıcıya sor. Komutlar her zaman o klasöre `cd` edilerek çalıştırılır.
2. **Yazan ve inceleyen farklı sağlayıcı olur; farklı CLI yeterli değildir** (opencode Anthropic modeli, agy Claude/GPT modeli çalıştırabilir).
   Hem yazanın hem inceleyenin gerçek model ve sağlayıcısını belirle (`-m`/`--model` değeri ya da aracın varsayılanı: `codex` = OpenAI,
   `claude` = Anthropic, `agy` varsayılanı = Google, `opencode` = `-m` önekindeki sağlayıcı). Aynı sağlayıcıysa **reddet**, farklısını öner.
3. Kota: codex kıt; basit işi (özet, sınıflandırma, commit mesajı, kod arama) ona verme, önce yerel model/opencode öner.
4. Komutlar (liste argümanlarıyla; kullanıcı girdisini kabuk dizgesine gömme):
   - codex: `codex exec -C <dir> -s read-only|workspace-write -o <cikti-dosyasi> "<istem>" < /dev/null`; inceleme için `read-only`.
     **`< /dev/null` zorunlu:** stdin açık kalırsa Codex ek girdi bekleyip asılı kalır. Başlattıktan birkaç dakika sonra günlüğün büyüdüğünü doğrula.
   - opencode: hedef klasöre `cd` edip `opencode run -m <saglayici/model> "<istem>"` (`--dir` bayrağı yok, klasör çalışma dizinidir).
   - agy: hedef klasörde `agy -p "<istem>" --model <m> --output-format stream-json --dangerously-skip-permissions --sandbox`;
     sonuç, `event:"result"` satırındaki `result.response` alanıdır.
   Çıktı dosyasını geçici klasöre yaz, depoya değil.
5. Sonucu özetle: hangi araç, hangi klasör, hangi kip, çıktının özü; değişiklik yapıldıysa `git -C <dir> status --short`.
   Başarısızlığı gizleme; aynı yöntemle en fazla 2 deneme.
