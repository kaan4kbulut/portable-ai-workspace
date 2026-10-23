# ANAYASA — Atölyenin düzen kuralları

Sürüm: 1.1 · Kabul: 2026-10-23 · **Yalnızca insan düzenler.** Her değişiklik `SURUM.md`'ye major satırı olarak işlenir.
Ajanlar bu dosyayı değiştiremez (settings deny + hook); değişiklik önerir, insan uygular.

## 1. Amaç ve tek ilke

Atölye; kullanıcının beyni, araçları ve çalışma masasıdır. Hangi makineye taşınırsa taşınsın aynı şekilde çalışır,
aynı disiplinle büyür. **Düzen koddan önce gelir; 7. yeniden yazım olmayacak.** Aynı fikir daha önce en az altı kez
sıfırdan yazıldı; sorun kod değil süreçti. Bu belge o süreci sabitler.

## 2. Taşınabilirlik

1. Depo kendi kendine yeter: kök `CLAUDE.md`, `AGENTS.md`, `.claude/`, `opencode.json`, `.mcp.json` proje kapsamında
   okunur. Hiçbir dosyada mutlak yol yoktur; hook'lar `$CLAUDE_PROJECT_DIR`, betikler kendi konumundan göreli çözer.
2. Depo içinde **symlink yoktur**. Çalıştırma bitine güvenilmez; betikler `bash yol/betik.sh` ile çağrılır.
   Büyük/küçük harf farkıyla aynı ad kullanılmaz. (USB / exFAT uyumu.)
3. **Taşınan:** kurallar, beceriler, ajanlar, hook'lar, ayarlar, kararlar, devir notları, proje indeksi, kütüphane,
   şablonlar, betikler, model kaydı. **Taşınmayan (asla depoda):** araç girişleri ve kimlik dosyaları, oturum
   kayıtları, önbellekler, `node_modules`/venv, model ağırlıkları, `10-sistem/durum/`, `10-sistem/gunluk/`.
4. Giriş her makinede ayrı yapılır; token taşınmaz (AGENTS.md Kesin kural 1).
5. Çevrimdışı çalışır: ağ yoksa `basla.sh` pull ve giriş denetimini atlar, gerisi çalışır.

## 3. Adlandırma

1. Klasör ve dosya adları: küçük harf, Türkçe aksansız, `kebab-case`.
2. Üst düzey bölümler `NN-ad` (`00-cekirdek` … `90-dis-kaynaklar`); numara yalnızca kökte, onluk adımla.
   Alt klasörlerde numara yok; sıralama gerekirse tarih öneki.
3. Tarihli öğeler `YYYY-MM-DD-<ad>`; devir notları `YYYY-MM-DD-HHMM-<makine>-<konu>.md`.
4. Büyük harfli kanonik belgeler (bir klasörde en fazla bir tane; bölümün kimliğini taşır):
   `README.md ANAYASA.md AGENTS.md CLAUDE.md KARARLAR.md PLAN.md DURUM.md SURUM.md NEDEN.md DIZIN.md AYIKLAMA.md SKILL.md`.
5. Sır ima eden adlar (`*token*`, `*secret*`, `auth.json`, `.credentials*`) depoda yasaktır.
6. Kesin biçim `10-sistem/denetim/kurallar/ad-regex.txt`; istisnalar `istisnalar.txt`.

## 4. Derinlik ve belgeleme

1. İnsan gezinmesi için kökten en fazla **4 klasör** derinlik. Araç biçimlerinin dayattığı derinlik
   (`skills/<ad>/SKILL.md`, `oturumlar/2026/`) sayılmaz.
2. İzlenen her klasörde bir `README.md` vardır: ne girer, ne girmez, nasıl adlandırılır.
3. Kökte yalnızca `10-sistem/denetim/kurallar/izinli-kokler.txt` içindeki girdiler bulunur.

## 5. Ne nereye gider

| Gelen şey | Yer |
|---|---|
| Ortak ajan kuralı | `00-cekirdek/AGENTS.md` |
| Atölye düzeni kuralı | bu belge (insan) + `SURUM.md` |
| Karar | `40-hafiza/kararlar/KARARLAR.md` |
| Oturum devir notu | `40-hafiza/oturumlar/YYYY/` |
| Öğrenilen ders | `40-hafiza/ogrenilenler/<konu>.md` |
| Tercih | `40-hafiza/tercihler.md` |
| Cihaz bilgisi (kalıcı) / kurulum betiği | `40-hafiza/cihazlar/<makine>.md` / `10-sistem/cihazlar/<makine>/` |
| Makineye özgü geçici durum | `10-sistem/durum/<hostname>/` (git dışı) |
| Makinede çıkan sorun + çözümü | `10-sistem/bakim/bilinen-sorunlar.md` (+ `onarimlar/<ad>.sh`) |
| Beceri / alt ajan / hook | `.claude/skills/` · `.claude/agents/` · `.claude/hooks/` |
| MCP sunucu tanımı | `20-araclar/mcp/<ad>/tanim.json` → kök `.mcp.json` |
| Araç ayarı (global kopya) | `20-araclar/<arac>/genel/` |
| Yeni proje | `30-projeler/aktif/<ad>/` (kendi reposu) + `30-projeler/DIZIN.md` |
| Atılabilir deneme | `30-projeler/deneme/YYYY-MM-DD-<ad>/` (30 gün) |
| systemd user birimi | `10-sistem/servisler/` |
| Model ağırlığı / llama.cpp ayarı | `20-araclar/yerel-modeller/agirliklar/` (git dışı) / `yapilandirma/` |
| İndirilen dosya, fikir, belirsiz not | `70-gelen-kutusu/` (30 gün); >50 MB → `90-dis-kaynaklar/` |
| Dış repo klonu | `90-dis-kaynaklar/<ad>/` + `DIZIN.md` |
| Bilgi belgesi | `50-kutuphane/<kategori>/` |
| Emekli olan her şey | `60-arsiv/YYYY-MM-DD-<ad>/` + `NEDEN.md` |
| Şablon | `80-sablonlar/<tur>/` |
| **Bilmiyorsan** | `70-gelen-kutusu/` — asla köke, asla rastgele bölüme |

## 6. Yaşam döngüsü

1. **Giriş:** Yeri kesin bilinmeyen her şey `70-gelen-kutusu/`'na `YYYY-MM-DD-<ad>` ile girer.
2. **Ayıklama (haftalık, `/ayikla`):** her öğe için taşı / arşivle / sil (yalnızca kendi ürettiğimiz çöp) / bekle
   (en fazla bir kez). `AYIKLAMA.md` tarih ve bekleyenler. 30 günü geçen öğe denetimde uyarıdır.
3. **Yeni alt klasör:** gelen kutusunda aynı türde **3+ öğe** birikti **ve** mevcut hiçbir yere sığmıyorsa:
   `80-sablonlar/bolum/` iskeleti, README zorunlu, `KARARLAR.md` kaydı, `SURUM.md` minor.
   Üst düzey yeni bölüm bu belgenin değişmesidir (insan, major).
4. **Arşiv:** "taşı, silme". `60-arsiv/YYYY-MM-DD-<ad>/NEDEN.md`: ne, neden, geri alma koşulu.

## 7. Denetim

`10-sistem/denetim/denetle.sh` düzen değişmezlerini kontrol eder:
`--hizli` her oturum başında (uyarır), `--commit` her commit'te (sır, izinsiz kök, ad, büyük/küçük çakışması,
symlink, >50 MB dosya engeller), `--tam` haftalık ve `basla.sh`'ta. Bulgular `10-sistem/bakim/` bakımcı ajanıyla
onarılır; her onarım `bilinen-sorunlar.md`'ye ve gerekirse denetim kurallarına işlenir.

## 8. Haftalık gözden geçirme (30 dk)

`bash basla.sh` → denetim → gelen kutusu ayıklama → `30-projeler/DIZIN.md` ve `DURUM.md`'ler → `PLAN.md` karar
noktası → `10-sistem/bakim/guncelle.sh` raporu → gerekiyorsa `SURUM.md`.

## 9. Yeniden yazma yasağı

Aynı işi yapan ikinci şey açılmaz. Önce `60-arsiv/`, `70-gelen-kutusu/`, `40-hafiza/` ve GitHub aranır;
bulunursa o değiştirilir. "Temiz başlangıç" yoktur: git geçmişi korunur, eski karar silinmez "geçersiz" işaretlenir,
kaldırılan şey arşivde `NEDEN.md` ile durur.

## 10. Sürümleme

`SURUM.md` semver. Major: üst bölüm ya da bu belge değişti. Minor: alt klasör, beceri, hook, betik eklendi.
Patch: README, şablon, metin düzeltmesi. Bu belgenin başlığındaki sürüm `SURUM.md`'deki son major.minor ile uyuşur.
