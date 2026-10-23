# nabiz: kota ve sürüm nabzı

Atölyenin "ne kadar kotam kaldı, hangi araç eskidi" sorusuna cevap veren iki küçük araç. Yalnızca Python 3 standart kütüphanesi.

## Ne girer

- `kota.py`: claude / codex / agy için kalan kota tahmini + kip (bol, normal, idareli, dolu, bilinmiyor). opencode: n/a.
- `durum-satiri.py`: Claude Code statusLine betiği; kotayı önbelleğe yazar, tek satır basar. Ağ yok, model yok, hedef < 200 ms.
- `takip.py`: `izlenenler.txt` listesindeki araçların kurulu ve son sürümünü karşılaştırır. Ağ yalnızca burada (GET, 8 sn zaman aşımı).
- `izlenenler.txt`: veri. Biçim: `ad · tur(npm|pypi|github|eol) · kimlik · komut [· sabit=X.Y.Z]`.
- `testler/nabiz-testleri.py`: çevrimdışı testler (`python3 20-sistem/nabiz/testler/nabiz-testleri.py`).

## Ne girmez

- Giriş/anahtar dosyaları okuyan ya da token çıkaran kod (`~/.claude/.credentials.json`, `~/.codex/auth.json`, `~/.gemini/`). Kota yalnızca resmi çıktılardan: statusLine JSON'u, Codex rollout `rate_limits` kayıtları, `agy -p /quota`.
- Otomatik yükseltme / kurulum. Nabız yalnızca raporlar.
- Makineye özgü çıktı: `20-sistem/durum/<host>/` altına yazılır ve git dışıdır (kota-claude.json, kota-agy.json, guncelleme-raporu.md).

## Kullanım

```
python3 20-sistem/nabiz/kota.py [--json]
python3 20-sistem/nabiz/takip.py          # rapor: 20-sistem/durum/<host>/guncelleme-raporu.md; çıkış 0 temiz, 1 bulgu
```

statusLine (kullanıcı ayarı, `~/.claude/settings.json` ya da proje `.claude/settings.json`):

```json
{ "statusLine": { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/20-sistem/nabiz/durum-satiri.py\"" } }
```

Çıktı: `<ad> · <makine> · git ±N · gelen N · denetim H/U · kota claude X% codex Y%` (X, Y = kalan yüzde; veri yoksa `?`).
Ad `00-cekirdek/kimlik.json` içindeki `ad` alanından, yoksa klasör adından gelir. Denetim, `20-sistem/durum/<host>/son-denetim.txt` içindeki `[HATA]` / `[UYARI]` satırlarının sayısıdır; dosya yoksa `?/?`.

Claude kotası yalnızca Claude Code'un statusLine'a `rate_limits` verdiği durumlarda (Pro/Max, ilk yanıttan sonra) görünür.

## Kim nasıl kullanır

- **Çekirdek ajan:** ağır iş (çoklu ajan, uzun görev) öncesi `kota.py` çalıştırır; kip `idareli`/`dolu` olan araca iş vermez, `bol` olanı tercih eder. Codex kıt kaynaktır (AGENTS.md iş bölümü).
- **Kütüphaneci:** `guncelleme-raporu.md`'yi okuyup bulguları (yeni sürüm, destek bitişi) `60-hafiza/` ya da `bilinen-sorunlar.md` için aday olarak sunar; yükseltme kararı kullanıcıya aittir.
- **Sabitlenmiş araçlar** (`sabit=` kolonu, örn. cc-safety-net 2.6.12): rapor "aday" sürümü gösterir (en az 7 gün önce yayımlanmış en yeni kararlı sürüm); otomatik yükseltme önerilmez.
