---
katman: sistem
surum: "-"
son_kontrol: 2026-10-23
kaynaklar: []
baglar: [../README.md, ../../.claude/skills/kapat/SKILL.md, ../../00-cekirdek/PLAN.md]
---
# 20-sistem/yedek — Yedekleme

Atölyenin yedeği = GitHub (gizli repo) + her projenin kendi reposu. Burada yalnızca "commit/push edilmemiş ne var"
raporu ve ileride (Aşama 4) `yedekle.sh` durur: atölye + `40-projeler/aktif/*` için commit'lenmemiş/push'lanmamış özet;
**otomatik push yapmaz** (AGENTS.md: kullanıcı istemeden push yok). Şimdilik bu özet ve onaylı commit/push akışı `/kapat` ile yürütülür.

**Girer:** yedek raporu/betiği. **Girmez:** yedeğin kendisi (git'tedir), kimlik dosyaları.

## Kısa tanım

Atölye ve aktif proje repolarının Git üzerinden yedeklenmesine ilişkin kapsam ve
bekleyen rapor betiği kaydıdır. Klasörde şu anda yalnızca bu README bulunur.

## Ne işe yarar?

Commit edilmemiş değişiklikleri ve push edilmemiş commit'leri görünür kılacak raporun
yerini tanımlar. [Sistem dizini](../README.md) içindeki yedekleme bölümüdür;
yedek verisinin kendisini veya kimlik dosyalarını barındırmaz.

## Nasıl çalıştırılır / bağlanılır?

Mevcut kayıtlı akış Claude Code içinde `/kapat` komutudur.
[Komut tanımı](../../.claude/skills/kapat/SKILL.md), atölye ile
`40-projeler/aktif/*/` altındaki repoların değişiklik ve push edilmemiş commit
özetini kapsar; commit ve push ayrı kullanıcı onaylarıyla yapılır.
Bu klasörden çalıştırılabilecek bir betik henüz yoktur.

Uzak depo adresi: -. Bu incelemede `/kapat`, commit, push veya uzak depo erişim
kontrolü çalıştırılmadı; yedeklerin güncelliği ve geri yüklenebilirliği doğrulanmadı.

## Açık eksikler

- Bağımsız sürüm ve resmi kaynak URL'leri: -. `70-kutuphane/` taramasında ilgili kaynak bulunamadı.
- `yedekle.sh` mevcut değildir; [planda](../../00-cekirdek/PLAN.md) bekleyen iş olarak kayıtlıdır.
  İlk metindeki “Aşama 4” ifadesi planda “eski Atölye Aşama 4” adıyla anılır.
- Son başarılı push/yedek zamanı ve geri yükleme testi sonucu: -.
- Git dışında kalan içerikler için yedekleme yöntemi ve kapsamı: -.
