---
katman: sistem
surum: 0.1.0
son_kontrol: 2026-10-23
kaynaklar: []
baglar:
  - ../nabiz/README.md
  - ../../70-kutuphane/arastirmalar/kadro/2026-10-23-eski-kadro-kazisi.md
---

# Model–efor kadrosu

Aşama 4 seçim ve öğrenme iskeleti. Yalnız Python 3 standart kütüphanesini kullanır;
iş çalıştırmaz. Model adlarının tamamı `varsayilan` yer tutucusudur. Sıra ve eforlar
ölçülmüş üstünlük iddiası değil, Aşama 2 envanteri ve Aşama 3 ölçümleri için başlangıçtır.

**Girer:** `kadro.json` veri kaydı, `kadro.py` seçicisi, [testler](testler/README.md),
[ölçüm satırları](olcumler/README.md). Adlar küçük harfli, aksansız ve kebab-case olur;
kanonik `README.md` istisnadır.
**Girmez:** CLI yürütücüleri, model/ağ çağrıları, giriş dosyaları, kimlik bilgileri,
makineye özel yollar, model keşfi ve ajan ayarları.

## Kullanım

Depo kökünden; betik başka çalışma dizininden çağrıldığında da veri ve kota
okuyucusunu kendi konumundan bulur. Ölçüm dosyasının yolu çağıranın dizinine göredir.

```bash
python3 -I -B 20-sistem/kadro/kadro.py secim kod-duzeltme --json
python3 -I -B 20-sistem/kadro/kadro.py secim inceleme --yazan-saglayici openai --json
python3 -I -B 20-sistem/kadro/kadro.py goster --yazan-saglayici openai
python3 -I -B 20-sistem/kadro/kadro.py goster --json
python3 -I -B 20-sistem/kadro/kadro.py ogren 20-sistem/kadro/olcumler/2026-10-23.jsonl
python3 -I -B 20-sistem/kadro/testler/kadro-testleri.py
bash 20-sistem/denetim/denetle.sh --hizli
```

`secim`: seçildiyse çıkış 0, uygun aday veya yazar sağlayıcısı yoksa 1, bozuk girdi
ya da dosya hatasında 2. `--json` başarısız seçimde de gerekçeli nesne verir.
`goster` altı iş türünü tek kota görüntüsüyle gösterir; aday bulunamaması bu bilgi
komutunun çıkışını değiştirmez. İncelemede `--yazan-saglayici` verilmezse
`yazan_saglayici_gerekli` yazar; farklı sağlayıcı garantisi varsayımla kurulmaz.
Sağlayıcı argümanı CLI adı değil `openai`, `anthropic`, `google` gibi sağlayıcı adıdır.

## Veri ve seçim

`is_turu`, altı iş türünü öncelik sıralı `{cli, model, efor}` listelerine eşler.
`yedek` aynı iş türleri için ayrı aday listeleri taşır. Bir ana aday uygunsa,
yedeğin puanı veya kota bolluğu daha yüksek olsa bile yedeğe geçilmez.
Claude yalnız yedektedir; basit işte Claude yedeği yoktur. Basit işin ilk adayı
yereldir; yerelin hazır olduğunu gösteren kota girdisi yoksa otomatik seçilmez.
Envanter ucuz seçenekleri doğrulayana kadar agy/Codex low sırası geçici tercihtir.

`saglayicilar` CLI → sağlayıcı eşlemesidir: Claude → Anthropic, Codex → OpenAI,
agy → Google. agy üzerinden `claude-*` modeli seçilirse sağlayıcı Anthropic olur;
kota yine agy satırından okunur. İncelemede yazanla aynı sağlayıcı tüm gruplarda
elenir. `inceleme_saglayici_farkli` kapatılamaz.

1. Kota satırı adaydaki `cli` ile satırdaki `arac` eşleştirilerek bulunur.
   `baglayici`, sağlayıcı değil `5s` veya `hafta` penceresidir; çıktıda korunur.
2. `dolu` her zaman elenir. `idareli` yalnız `zor_isler` listesindeki kod düzeltme,
   inceleme, araştırma işlerinde veya incelemede kullanılabilir. Belge, mekanik
   taşıma ve basit işlerde elenir. Zor iş ile çok dosyalı ağır iş aynı sınıf değildir.
3. Eksik satır, `bilinmiyor`, `n/a` veya tanınmayan kip otomatik seçilmez.
   Aday kalmazsa `uygun_aday_yok` ve bilinmeyen/elenen adaylar gerekçeyle döner.
4. Her grupta önce `bol`, sonra `normal`, sonra `idareli` değerlendirilir.
   Kota kapısından geçen aynı kipteki adaylar Bayes puanına göre sıralanır.
   Eşit puanda düşük efor, ardından JSON sırası seçilir.

Önsel, her grubun kendi sıfır tabanlı sırası için `max(0.5, 0.75 - 0.05*sıra)`dır.
Ölçüm yoksa aynı kota kipinde ilk aday seçilir. Her iş türü × CLI × model × efor
ayrı öğrenilir. Anahtar, bu dört öğenin kanonik JSON listesidir; ayraç içeren
model adları çakışmaz. Ölçülen kalite başarı (0–1) ve puan/5'in mevcut olanlarının
aritmetik ortalamasıdır. İkisi de verilirse eşit ağırlıktadır.

```text
a = n / (n + 5)
son_puan = (1 - a) * onsel + a * ortalama_olculen_kalite
```

Örneğin n=5, önsel=0.75 ve ölçülen ortalama=0 ise son puan 0.375 olur.
`goster` ve `secim`, önseli, örnek sayısını, ölçülen ortalamayı, karışım katsayısını,
son puanı, kota kipini, kalan yüzdeyi ve bağlayıcı pencereyi gösterir.
Süre ve kota farkı saklanır; henüz kalite puanına maliyet cezası eklenmez.

## Kota okuma sınırı

`kota.py` importlib ile yüklenir. `hepsi(kok, agy=False)` Claude durum önbelleğini
ve Codex'in mevcut kota kayıtlarını okur; ardından `agy_oku` yalnız önbellekle,
CLI yenileme işlevi etkisizleştirilerek çağrılır. Önceden üretilmiş ve okuyucuya
göre taze bir agy kaydı yoksa kota bilinmiyor kalır. Seçici hiçbir CLI/model/ağ
çağrısı yapmaz, önbellek yazmaz, giriş dosyası okumaz. Canlı kota yenilemesi
seçicinin dışındaki nabız işidir. Pencerelerin eskiliği/sıfırlanması mevcut
okuyucunun sorumluluğudur; sahte listede verilen kip otorite kabul edilir.

Programlama arayüzü: `select(task_type, config, quotas, writer_provider=None)`
sahte kota listesiyle tamamen çevrimdışı çalışır; `load_config(path)` ve
`learn(source, config_path)` ayrı veri dosyasıyla kullanılabilir.

## Öğrenme ve bütünlük

`ogren`, bütün JSONL girdisini doğrular; geçerli satırların sayaçlarını
`kadro.json` içindeki `olcumler` altında, kimliklerini `islenmis_sonuclar` altında
tutar. Ham `not` metni bu dosyaya kopyalanmaz. Girdi satır biçimi ve örnek
[ölçüm açıklamasındadır](olcumler/README.md).

İsteğe bağlı `id` varsa kimlik odur; yoksa normalize edilmiş dokuz alanın
kanonik SHA-256 özeti kullanılır. Alan sırası, sayıların 1/1.0 biçimi ve
başarının true/1 biçimi aynı sonucu değiştirmez. Aynı kimlik ve içerik tekrar
sayılmaz; aynı kimlikle farklı içerik bütün işlemi reddeder. İçeriği tamamen aynı
iki bağımsız deneyi ayırmak için farklı açık `id` verilmelidir.

Tek yazıcı kilidi ve aynı klasörde geçici dosya → fsync → atomik dosya değişimi
kullanılır. Hatalı satırda veya kimlik çakışmasında kayıt değişmez; yalnız tekrar
varsa dosya yeniden yazılmaz. Eşzamanlı ikinci yazıcı hata alır. Kesilen süreçten
`kadro-kilit.tmp` kalırsa çalışan yazıcı olmadığı doğrulandıktan sonra çekirdek
ajan temizler; seçici kilidi kendiliğinden kırmaz. Geçici dosyalar ölçüm değildir.

## Çekirdek ajana devir

Bu yalıtılmış değişiklik yalnız bu klasörü kapsar. Envanterin yer tutucu modelleri
doldurması, gerçek ölçümler, farklı sağlayıcı incelemesi, `/araclar` ve
kütüphaneci bağlantıları, ajan frontmatter alanları, HARITA/karar/oturum kayıtları,
sürüm ve yayın ana repoda çekirdek ajan tarafından tamamlanacaktır.
Bu görevde commit veya git ile değişiklik yapılmaz.

23 Ekim 2026 doğrulaması: yalıtılmış 25 test geçti (`Ran 25 tests`, `OK`).
Gerçek kayıtlarla `goster --yazan-saglayici openai` çalıştı; farklı sağlayıcının
kotası bilinmediği için inceleme ataması yapılmadı. Hızlı denetim hem çalışma
öncesinde hem sonrasında **1 hata, 1 uyarı** verdi: kökteki `.aws` izinli kökler
listesinde değil; `70-kutuphane/arastirmalar/kadro/` altında README yok.
Bu iki bulgu izin verilen yazma alanının dışında kaldığından değiştirilmedi;
depo genelinde 0/0 kabul ölçütü henüz sağlanmıyor.

## İş kaydı ve pano (`isler.py`, `pano.sh`)

Her işçi çağrısı (codex, agy, opencode, yerel, claude) **elle de olsa** `isler.py baslat` üzerinden yapılır; kayıt
`20-sistem/durum/<host>/isler/<id>.json` + `<id>.log` (git dışı). Bekçi: stdin `/dev/null`, ayrı süreç grubu, `--hareketsiz`
saniye boyunca günlük ve klasör değişmezse öldürür (`takildi`), `--sure` dolunca `zaman_asimi`. Çıkış 0 tek başına başarı değildir:
boş çıktı `basarisiz`, reddedilen araç eylemi `reddedildi`, 429/limit imzası `limit`.

```bash
python3 -I 20-sistem/kadro/isler.py baslat --gorev "yurut.py yaz" --arac codex --model gpt-6-sol --efor high \
  --klasor <klon> --hareketsiz 180 -- codex exec -C <klon> -s workspace-write -o <cikti> "<istem>"
bash 20-sistem/kadro/pano.sh          # canlı pano: araç · model · efor · görev · durum · süre · kota · GPU
python3 -I 20-sistem/kadro/isler.py ozet   # durum satırındaki "işler N▶ M⚠"
```
Testler: `python3 20-sistem/kadro/testler/isler-testleri.py`.
