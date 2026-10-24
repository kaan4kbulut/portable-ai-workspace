---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../durum/README.md, ../kutuphaneci/README.md, ../denetim/README.md, testler/README.md]
---
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
- Makineye özgü çıktı: `20-sistem/durum/<host>/` altına yazılır ve git dışıdır (kota-claude.json, kota-agy.json, kota-agy-deneme.txt, guncelleme-raporu.md).

## Kullanım

```
python3 20-sistem/nabiz/kota.py [--json]
python3 20-sistem/nabiz/takip.py          # rapor: 20-sistem/durum/<host>/guncelleme-raporu.md; çıkış 0 temiz, 1 bulgu
```

statusLine (kullanıcı ayarı, `~/.claude/settings.json` ya da proje `.claude/settings.json`):

```json
{ "statusLine": { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/20-sistem/nabiz/durum-satiri.py\"" } }
```

Çıktı: `<ad> · <makine> · git ±N · gelen N · denetim H/U · bağlam %B 46k/200k · claude 5s%X hf%Y · codex 5s%X hf%Y · agy 5s%X hf%Y`.
`bağlam` bu Claude oturumunun bağlam doluluğu ve token sayacıdır (statusLine `context_window`; ilk yanıttan önce `?`). Kota sayıları her pencerenin **kalan** yüzdesidir (`5s` = 5 saat, `hf` = hafta; veri yoksa ya da 6 saatten eskiyse `?`).
agy satırda yalnız önbellekten (`kota-agy.json`) okunur; önbellek 5 dakikadan eskiyse `kota.py --agy-yenile` arka planda başlatılır (en çok 2 dakikada bir, damga `kota-agy-deneme.txt`).
Ad `00-cekirdek/kimlik.json` içindeki `ad` alanından, yoksa klasör adından gelir. Denetim, `20-sistem/durum/<host>/son-denetim.txt` içindeki `[HATA]` / `[UYARI]` satırlarının sayısıdır; dosya yoksa `?/?`.

Claude kotası yalnızca Claude Code'un statusLine'a `rate_limits` verdiği durumlarda (Pro/Max, ilk yanıttan sonra) görünür.

## Kim nasıl kullanır

- **Çekirdek ajan:** ağır iş (çoklu ajan, uzun görev) öncesi `kota.py` çalıştırır; kip `idareli`/`dolu` olan araca iş vermez, `bol` olanı tercih eder. Codex kıt kaynaktır (AGENTS.md iş bölümü).
- **Kütüphaneci:** `guncelleme-raporu.md`'yi okuyup bulguları (yeni sürüm, destek bitişi) `60-hafiza/` ya da `bilinen-sorunlar.md` için aday olarak sunar; yükseltme kararı kullanıcıya aittir.
- **Sabitlenmiş araçlar** (`sabit=` kolonu, örn. cc-safety-net 2.6.12): rapor "aday" sürümü gösterir (en az 7 gün önce yayımlanmış en yeni kararlı sürüm); otomatik yükseltme önerilmez.

Kota metni bilinen iki pencereyi ayrı kalan yüzde ve yerel sıfırlanma saatiyle gösterir.
JSON'da `pencereler` korunur; `kalan_yuzde` pencerelerin en düşük kalan yüzdesidir,
`baglayici` bu pencerenin adıdır (`5s` / `hafta`; eşitlikte `5s`, eski/verisiz sonuçta `null`).
Bağlayıcı pencerede kalan <= %10 ise kip `dolu`, <= %25 ise `idareli` olur;
bu eşikler sıfırlanmaya az kalma kuralından da önce uygulanır. Daha fazla kalanda
mevcut tempo hesabı `bol` / `normal` / `idareli` seçer. Sıfırlanmış pencere %100 kalan sayılır.


## Açık eksikler

- Nabız için ayrı sürüm bilgisi: -
- Canlı kota verisi ve dış sürüm kaynaklarına erişim bu kontrolde doğrulanmadı; kullanım bilgileri yerel kod ve belgelere dayanır.
- Kota verisi eksik ya da altı saatten eskiyse kip `bilinmiyor` olur; opencode için kota verisi yoktur (`n/a`).
- **Eskimiş:** Yukarıdaki “Codex kıt kaynaktır” ifadesi güncel ortak ajan kurallarındaki iş bölümüyle uyuşmuyor. Güncel kuralda ağır iş Codex ve agy'ye verilir; kota dolarsa diğer CLI'a geçilir.

## İlgili sayfalar

- [Makineye özgü durum ve raporlar](../durum/README.md)
- [Kütüphaneci](../kutuphaneci/README.md)
- [Denetim](../denetim/README.md)
- [Nabız testleri](testler/README.md)
