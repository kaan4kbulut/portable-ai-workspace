---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../../00-cekirdek/ANAYASA.md, ../bakim/README.md, ../kurulum/README.md, testler/README.md]
---
# 20-sistem/denetim — Düzen denetimi

`denetle.sh` atölyenin değişmezlerini kontrol eder; kurallar kod değil **veri** olarak `kurallar/` altındadır, böylece
bakımcı ajan yeni kural ekleyebilir.

| Dosya | Görev |
|---|---|
| `denetle.sh [--hizli\|--commit\|--tam]` | Çıkış 0 temiz · 1 uyarı · 2 hata. Satır biçimi `[HATA\|UYARI\|OK\|BILGI] kural · yol · öneri` |
| `kurallar/izinli-kokler.txt` | Kökte bulunabilecek girdiler (ANAYASA 4.3) |
| `kurallar/ad-regex.txt` | 1. satır dizin, 2. satır dosya adı deseni (ANAYASA 3) |
| `kurallar/sir-desenleri.txt` | İzlenen dosyalarda asla görünmeyecek desenler |
| `kurallar/istisnalar.txt` | Araçların dayattığı adlar/yollar (denetim dışı) |
| `git-hooks/pre-commit` | `kur.sh` bunu `core.hooksPath` ile bağlar; `--commit` kipinde hata = commit engellenir |

Kipler: `--hizli` SessionStart hook'u ve `/kapat`; `--commit` pre-commit; `--tam` `/baslat`, haftalık gözden geçirme, `/bakim`.
`--tam` giriş durumunu yalnızca aracın kendi komutuyla sorar (`gh auth status`, `codex login status`, `opencode auth list`); kimlik dosyası okumaz.

**Girer:** denetim betiği ve kural verileri. **Girmez:** onarım (→ `../bakim/`), kurulum (→ `../kurulum/`).

## Kısa tanım

Atölyenin dosya düzenini ve temel sağlık durumunu denetleyen Bash betiği, kural verileri
ve Git commit kancasıdır.

## Ne işe yarar?

İzinsiz kök girdilerini, adlandırma ihlallerini, büyük/küçük harf çakışmalarını, symlink'leri,
50 MB üzerindeki dosyaları ve sır desenlerini raporlar. README, derinlik, dizin kaydı,
gelen kutusu yaşı ve major sürüm uyumunu da denetler. Bulguların onarımı
[bakım bileşeninin](../bakim/README.md) alanıdır; düzenin dayanağı
[ANAYASA](../../00-cekirdek/ANAYASA.md) belgesidir.

## Nasıl çalıştırılır / bağlanılır?

Depo kökünden, Bash, Git ve standart Unix araçlarıyla:

```bash
# Varsayılan kip; yerel düzen denetimi.
bash 20-sistem/denetim/denetle.sh --hizli
# Aday dosya listesini Git indeksinden alır; sır taramasında indeks içeriğini okur.
bash 20-sistem/denetim/denetle.sh --commit
# Araç sürümleri, girişler, genel bağlantılar ve Git durumunu da denetler.
bash 20-sistem/denetim/denetle.sh --tam
```

Betik [kurulumun](../kurulum/README.md) `lib/ortak.sh` yardımcılarını kullanır.
`--commit` kipinde de kök ve bazı genel düzen kontrolleri depo genelinde çalışır.
`--tam` ağ durumunu sorgular; çevrimiçiyse araçların kendi giriş durumu komutlarını ve
`git fetch -q origin` çalıştırabilir. Denetim onarım uygulamaz.
`git-hooks/pre-commit`, çıkış kodu 2 olduğunda commit'i engeller;
[kurulum](../kurulum/README.md) `core.hooksPath` ayarını bağlar.
Hook doğrulama komutu ve kapsamı [testler sayfasında](testler/README.md) bulunur.

## Açık eksikler

- Bağımsız bileşen sürümü ve resmi kaynak URL'leri: -. `70-kutuphane/` içinde ilgili kayıt bulunamadı.
- ANAYASA madde 7'de belirtilen bayat varlık sayfası, kırık göreli bağ ve
  HARITA'da olmayan varlık kontrolleri mevcut `denetle.sh` içinde uygulanmış görünmüyor.
- Bu incelemede tam denetim, CLI girişleri ve Git kancasının canlı bağlantısı sınanmadı;
  bu makinedeki sonuçları: -.
