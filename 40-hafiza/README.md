# 40-hafiza — Hafıza

İşletim sisteminin **durum ve kayıt** katmanı. Kalıcı bilgi araçların kendi hafızasında değil burada durur; böylece her CLI
ve her makine aynı şeyi bilir. Claude otomatik hafızası atölyede kapalıdır.

| Klasör / dosya | İçerik | Nasıl yazılır |
|---|---|---|
| `kararlar/KARARLAR.md` | karar günlüğü (tarih · karar · gerekçe); eski karar "geçersiz" işaretlenir | `/karar` |
| `oturumlar/YYYY/` | devir notları `YYYY-MM-DD-HHMM-<makine>-<konu>.md`; makineler arası sürekliliğin tek kaynağı | `/kapat`, `kapat.sh` taslağı |
| `ogrenilenler/<konu>.md` | "bunu bir daha yapma" dersleri, konu başına tek dosya | bakımcı, `/kapat` |
| `tercihler.md` | kullanıcı tercihleri (tercih ≠ izin) | insan |
| `cihazlar/<makine>.md` | kalıcı cihaz bilgisi: rol, donanım, tarihçe (kimlik yok) | insan, bakımcı |
| `kisiler/` | ileride; kişisel veri kuralı README'de | insan |

Biçim kuralları: `.claude/rules/hafiza.md`. SessionStart hook'u en yeni 2 devir notunu ve KARARLAR başını bağlama basar.

**Girer:** karar, devir, ders, tercih, cihaz. **Girmez:** kural (→ `00-cekirdek/`), makine sorunu tablosu (→ `10-sistem/bakim/`), geçici durum (→ `10-sistem/durum/`).
