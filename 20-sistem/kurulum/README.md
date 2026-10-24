---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../denetim/README.md, ../servisler/README.md, ../../10-donanim/README.md]
---
# 20-sistem/kurulum — Kurulum

| Dosya | Görev |
|---|---|
| `kur.sh [--kuru] [--genel] [--yeniden-bagla h]` | İdempotent: makine durumu, apt (sudo varsa), eksik araçlar (kullanıcı-yerel), git kimliği/ayarı, `core.hooksPath`, git dışı dizinler, isteğe bağlı global bağlantılar, denetim |
| `lib/ortak.sh` | Tüm betiklerin ortak yardımcıları (`atolye_koku`, `makine_adi`, `fs_turu`, `cevrimici_mi`, `yedekle_ve_bagla`) |
| `araclar/<ad>.sh` | Araç başına kurucu; `komut_var || kur`; **giriş yapmaz** |

`--genel`: proje kapsamı dışında da aynı kurallar istenirse `~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.gemini`
içine bağlantı kurar (mevcut dosya `.yedek-<zaman>` olarak saklanır). USB/başka makine için gerekmez.
Kısıtlı dosya sisteminde (exFAT/NTFS) `core.filemode=false`, `core.symlinks=false`, `core.ignorecase=true` ayarlanır.

**Girer:** kurulum betikleri. **Girmez:** denetim (→ `../denetim/`), makine profilleri (→ `../../10-donanim/`).

## Kısa tanım

Atölyeyi yeni makinede hazırlayan kurulum betikleri ve ortak kabuk yardımcılarıdır.

## Ne işe yarar?

Makine durumunu kaydeder, eksik sistem paketleri ve araçları kurmayı dener, Git ayarlarını
ve çalışma dizinlerini hazırlar. İsteğe bağlı genel araç bağlantılarını kurar ve sonunda
[düzen denetimini](../denetim/README.md) çağırır.
[Makine profilleri](../../10-donanim/README.md) paket listesini,
[servisler](../servisler/README.md) genel kurulumda bağlanacak kullanıcı birimlerini sağlar.
Araç girişleri her makinede ayrı yapılır; kurucular giriş yapmaz.

## Nasıl çalıştırılır / bağlanılır?

Depo kökünden:

```bash
# Yapılacak işlemleri gösterir; kurulum uygulamaz.
bash 20-sistem/kurulum/kur.sh --kuru
# Makine kurulumunu uygular.
bash 20-sistem/kurulum/kur.sh
# İsteğe bağlı: genel araç ayarlarını da bağlar.
bash 20-sistem/kurulum/kur.sh --genel
```

`--yeniden-bagla <hedef>` yalnızca verilen genel hedefi yeniden bağlamak içindir;
`--kuru` ile birlikte kullanılabilir. `--genel`, mevcut hedefleri yedekleyerek ev dizinindeki
ayarları etkiler. Sistem paketi adımı uygun makine paket listesi, apt ve parolasız sudo
ister; araç kurulumu için ağ erişimi aranır. Çevrimdışı durumda araç kurulumu atlanır.

## Açık eksikler

- Bu kurulum bileşeninin bağımsız sürümü ve resmi kaynak URL'leri: -.
- `70-kutuphane/` taramasında ilgili kurulum belgesi bulunamadı.
- Bu sayfa kaynak kod okunarak doğrulandı; gerçek kurulum, genel bağlantılar ve
  makineye özgü sonuçlar bu incelemede çalıştırılarak sınanmadı.
