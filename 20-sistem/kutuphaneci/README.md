---
katman: sistem
surum: 0.1.0
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../../.claude/agents/kutuphaneci.md, ../../.claude/skills/kutuphane/SKILL.md]
---
# Kütüphaneci

Küre sayfalarını ve araştırma raporlarını denetler, bulguları kalıcı bir iş kuyruğuna alır, işleri resmi CLI işçilerine (agy, claude; codex yalnız açık istekle) yaptırır ve katmanlı haritayı üretir. Yalnızca Python 3 standart kütüphanesi.

## Komutlar

```
python3 20-sistem/kutuphaneci/kutuphaneci.py denetle
python3 20-sistem/kutuphaneci/kutuphaneci.py kuyruk [--ekle TUR KONU]
python3 20-sistem/kutuphaneci/kutuphaneci.py calistir [--kuru] [--sinir N] [--isci agy|claude|codex]
python3 20-sistem/kutuphaneci/kutuphaneci.py harita
python3 20-sistem/kutuphaneci/testler/kutuphaneci-testleri.py
```

- `denetle`: ön madde alanı eksik, `son_kontrol` 30 günden eski, kırık `baglar`, sayfasız varlık klasörü; araştırma raporlarında kırık bağlantı, `DIZIN.md`'de olmayan rapor, `Kaynak denetimi:` satırı yok.
- `kuyruk`: bulguları sha256 kimlikle tekilleştirir; kilitli, atomik JSON. `--ekle` ile `arastir`/`haber` gibi elle iş eklenir.
- `calistir`: sıradaki işleri sırayla agy, kota dolarsa claude ile çalıştırır. Kota ya da zaman aşımında iş "bekliyor" kalır. API anahtarı ortam değişkenleri işçiye geçmez.
- `harita`: `00-cekirdek/HARITA.md` ve `50-arayuz/harita.html` (çevrimdışı SVG, halkalar) dosyalarını yeniden üretir.

Çalışma durumu (kuyruk, kilit, günlük, denetim) `20-sistem/durum/<host>/kutuphaneci/` altındadır ve git dışıdır.

## Girer

- `kutuphaneci.py`, `istemler/*.md` (iş türü başına istem), `testler/`.

## Girmez

- Araştırma raporları (`70-kutuphane/arastirmalar/`), varlık sayfaları (kendi katmanlarında), kuyruk ve günlük (durum klasörü).
- Zamanlama, özet, toplama hattı: kapsam dışı.
