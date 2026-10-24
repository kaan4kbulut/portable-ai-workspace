# Model–efor ölçümü

## Girer

Python 3 standart kütüphanesiyle çalışan koşucu, ortak değerlendirme desteği ve çevrimdışı testler.
Beş sabit görev ve referans çözümler kardeş [gorevler/](../gorevler/README.md)
klasöründedir. Dosya ve görev adları kebab-case kullanır.

## Girmez

Model/ağ çağrısı, giriş bilgileri, gerçek ev klasörüne bağımlılık, CLI kurulumları
ve kadro seçim politikası. Ölçüm günlüklerinin yeri kardeş `olcumler/` klasörüdür.
Referans çözümler ve değerlendirme dosyaları modele verilmez.

## Görevler

| Görev | Model çıktısı | Otomatik puan |
|---|---|---|
| `kod-duzeltme` | Düzeltilmiş `guard.py` | Test SHA-256 özeti aynı ve unittest başarılıysa 1 |
| `inceleme` | `bulgular.json` | Yeni satır numarası ve açıklama sözcükleri eşleşen hata sayısı / 3 |
| `turkce-belge` | Şemaya uyan `README.md` | Başlıklar ve boş olmayan bölümler sağlanırsa 1 |
| `arastirma` | `rapor.md` | Kaynak satırları, HTTP(S) URL biçimi ve özet atıfları uygunsa 1 |
| `mekanik-tasima` | Düzeltilmiş bağlar ve ayar | Sabit kontrol listesinde 0 hata varsa 1 |

Her `degerlendir.py calisma` çağrısı tek JSON nesnesi basar:
`{"basari": true, "puan": 1.0, "not": "..."}`. Kısmi inceleme puanında
`basari` false olur; diğer görevler 0 veya 1 verir. Eksik/bozuk çıktılar 0 puandır.
Değerlendiricinin normal tamamlanması çıkış kodu 0'dır; başarısız çözüm de JSON
sonucuyla bildirilir. Koşucu kullanım hatalarında 2 döndürür ve kayıt yazmaz.

Belge puanı yalnız yapısaldır; [rubrik](../gorevler/turkce-belge/rubrik.md) ile 0–5
içerik puanını farklı sağlayıcıdan model ayrıca verir. Bu puan otomatik puanın
yerine geçirilmez. Araştırmada URL'nin erişilebilirliği ve kaynakların iddiaları
desteklemesi otomatik doğrulanmaz. İncelemede yanlış pozitifler cezalandırılmaz;
eşleşme puanı anlamsal incelemenin yerine geçmez. Bu sınırlamalar sonuçların
`not` alanında da belirtilir.

## Kullanım

Komutlar depo kökünden çalıştırılır; hedef henüz mevcut olmamalıdır:

```sh
python3 -I -B 20-sistem/kadro/olcum/kosucu.py hazirla kod-duzeltme calisma/kod
python3 -I -B 20-sistem/kadro/olcum/kosucu.py komut kod-duzeltme --cli codex --model MODEL --efor medium calisma/kod
python3 -I -B 20-sistem/kadro/olcum/kosucu.py degerlendir kod-duzeltme calisma/kod --cli codex --model MODEL --efor medium --sure 12.5
```

`hazirla` yalnız `../gorevler/<gorev>/girdi.json` manifestosunu hedefe açar;
var olan hedefin üzerine yazmaz. Manifesto göreli POSIX dosya yolunu UTF-8
metin içeriğine eşler. Mutlak yollar, üst klasöre çıkış, ters eğik çizgi,
dosya/klasör çakışması ve metin olmayan içerik yazmadan önce reddedilir.
`istem.md` komutun son argümanına metin olarak eklenir. `komut` yalnız JSON
argüman listesi basar; süre tutmaz ve CLI çalıştırmaz. agy ve opencode için komutu
çalıştıran kişi/sistem önce hedef çalışma klasörünü cwd olarak seçmelidir.
Codex klasörü `-C` ile alır. Efor/model değerleri envanterden seçilir;
koşucu desteklenip desteklenmediğini kontrol etmez. Opencode efor bayrağı
almadığından `--efor` yalnız ölçüm etiketi olarak saklanır; tercihen `n/a` kullanılır.
Argüman listesi kabuk metnine dönüştürülmeden, liste kabul eden alt süreç arayüzüne
verilmelidir. Resmi CLI'lar kendi girişlerini kullanır.

Gerçek ölçümde kota anlık görüntüleri ölçümden önce ve sonra ayrı alınır:

```sh
python3 -I 20-sistem/nabiz/kota.py --json > calisma/kota-oncesi.json
python3 -I 20-sistem/nabiz/kota.py --json > calisma/kota-sonrasi.json
python3 -I -B 20-sistem/kadro/olcum/kosucu.py degerlendir kod-duzeltme calisma/kod --cli codex --model MODEL --efor medium --sure 12.5 --kota-oncesi calisma/kota-oncesi.json --kota-sonrasi calisma/kota-sonrasi.json
```

İki kota komutu arasında görev çalıştırılır. Koşucu kota okuyucusunu çağırmaz;
`kota.py --json` liste biçiminden seçilen CLI'ın tek kaydını okur.
`kota_farki`, `5s` ve `hafta` için son kullanılan pay eksi ilk kullanılan paydır
(0..1); yüzde puanına çevirmek için 100 ile çarpılır. Pencere sıfırlanması,
azalan kullanım, eksik ya da sayısal olmayan veri `null` olur. Kota verilmezse
alan bütünüyle `null`; yalnız bir görüntü verilirse kullanım hatasıdır.
Ortak kota havuzundaki eşzamanlı işler farkı etkileyebilir.

`degerlendir`, kendi dosya konumundan kardeş `olcumler/YYYY-MM-DD.jsonl` yolunu
bulur; geçerli yerel tarih ve saat dilimini kullanır. Her çağrı bir UUID ile
yeni satır ekler; başarısız çözüm de kaydedilir. Alanlar: `id`, `tarih` (ISO 8601),
`gorev`, `cli`, `model`, `efor`, `sure_sn`, `basari`, `puan`, `kota_farki`, `not`.
Süre kullanıcı tarafından verilen, sonlu ve negatif olmayan duvar süresidir.
Token sayımı bu sürümün kayıt sözleşmesinde yoktur.

Kod değerlendirmesi aday Python modülünü unittest ile alt süreçte çalıştırır;
bu bir güvenlik sandbox'ı değildir. Gerçek model görevleri yalıtılmış, sırsız,
ağsız çalışma ortamında değerlendirilmelidir. Symlink girdiler/hedefler kabul edilmez.

## Test ve devir

```sh
python3 -I -B 20-sistem/kadro/olcum/testler/olcum-testleri.py
bash 20-sistem/denetim/denetle.sh --hizli
```

Testler kendi geçici depo kopyasını ve boş ev klasörünü kullanır; soket açma
girişimleri test alt süreçlerinde engellenir. Gerçek ölçüm günlüğü oluşturmaz.
Her yeni klasörde kapsam README’si vardır. Görevler `../gorevler/<gorev>/`
altında yalnız dosyalardan oluşur; iç içe girdiler ve referans çözümler
`girdi.json` ve `cozum.json` içinde tutulur. Depo ağacı dört klasörü aşmaz.
Testler referans manifestolarını geçici klasöre açıp değerlendirir; girdilerin
birebir açılmasını, üzerine yazma yasağını, geçersiz manifesto yollarını ve
değerlendirme sabitlerinin korunmasını da kontrol eder.

2026-10-24 devir: Derinlik düzeltmesi tamamlandı; eski `olcum/gorevler/`
ağacı bu geçici klon için verilen açık izinle kaldırıldı. Değerlendirme
sabitleri ortak `destek.py` içine taşındı. Otomatik biçim/yapı puanları
içerik kalitesinden ayrı yorumlanır. Çekirdek ajan farklı sağlayıcıdan
incelemeyi ve ana depoya birleştirmeyi yürütür; ortak hafıza kaydını da
bu devirden aktarır. Korunan dosyalar, kadro kök README’si ve denetim
kuralları değiştirilmedi.

Yerel doğrulama: 15 test geçti (`Ran 15 tests`, `OK`). Hızlı denetim
`1 hata, 0 uyarı` verdi; 17 derinlik uyarısı giderildi. Kalan tek hata,
önceden mevcut `.aws` kök girdisidir. Bu girdinin içeriği okunmadı veya
değiştirilmedi; ortamın salt okunur alanıdır. `0 hata, 0 uyarı` hedefi için
çekirdek ajanın bu ortam girdisini depo dışında ele alması gerekir.
