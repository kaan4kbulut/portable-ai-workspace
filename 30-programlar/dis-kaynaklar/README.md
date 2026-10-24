---
katman: programlar
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../README.md, DIZIN.md, ../opencode/README.md]
---

# 30-programlar/dis-kaynaklar — Dış kaynaklar (git dışı)

İşletim sisteminin **mount** noktası: başkalarının repolarının klonları, 50 MB üstü indirmeler. İçerik izlenmez; yalnızca
`DIZIN.md` (ad · kaynak URL · neden · tarih) izlenir. `DIZIN.md`'de satırı olmayan klasör denetimde uyarıdır.

**Girer:** dış klon, büyük dosya. **Girmez:** kendi projelerimiz (→ `40-projeler/`), kendi yazdığımız her şey.

## Ne işe yarar

Dış kaynak kodunu incelemek ve araç davranışlarını kaynaktan doğrulamak için yerel kopyaları barındırır.
[Dizinde](DIZIN.md) `opencode` kaynak klonu kayıtlıdır; ilgili araç sayfası: [opencode](../opencode/README.md).
Üst katman: [programlar](../README.md).

## Çalıştırma / bağlanma

Bu klasörün ortak bir çalıştırma komutu yoktur; her dış kaynağın kendi belgeleri esas alınır.
Kaynak adresi [DIZIN.md](DIZIN.md) üzerinden bulunur. Bu çalışma kopyasında yalnızca README ve dizin
dosyası vardır; kayıtlı `opencode` klonu mevcut değildir. Klona ait yerel çalıştırma doğrulaması: -.

## Açık eksikler

- Kayıtlı `opencode` klonu bu çalışma kopyasında bulunmadığından içeriği ve çalıştırılması doğrulanamadı.
- Klasörün bağımsız sürümü ve resmi kaynak adresi: - (`kaynaklar: []`); klonun kaynak URL'si dizinde tutulur.
- **Eskimiş ifade:** Yukarıdaki “yalnızca DIZIN.md izlenir” ifadesine README.md de dahildir;
  `.gitignore` iki dosyayı da izleme dışında bırakmaz.
- **Eskimiş kapsam:** Yukarıdaki “50 MB üstü indirmeler” ifadesi ANAYASA 5'e göre sınırlıdır:
  model ağırlıkları `../yerel-modeller/agirliklar/` altında, diğer büyük dosyalar amacına uygun git dışı yerde tutulur.
