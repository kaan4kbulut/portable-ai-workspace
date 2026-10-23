# ANAYASA — Atölyenin düzen kuralları

Sürüm: 2.0 · Kabul: 2026-10-23 · **Yalnızca insan düzenler** (madde 13). Her değişiklik `SURUM.md`'ye major sürüm olarak işlenir.
Ajanlar bu dosyayı değiştiremez; değişiklik önerir, insan uygular.

## 1. Amaç ve tek ilke

Atölye; kullanıcının beyni, araçları ve çalışma masasıdır. Hangi makineye taşınırsa taşınsın aynı şekilde çalışır,
aynı disiplinle büyür. **Düzen koddan önce gelir; 7. yeniden yazım olmayacak.** Aynı fikir daha önce en az altı kez
sıfırdan yazıldı; sorun kod değil süreçti. Bu belge o süreci sabitler. Atölye dünya gibi içten dışa katmanlıdır
(madde 5); yeniden yerleşim yeniden yazım değil, `git mv` ile taşımadır.

## 2. Taşınabilirlik

1. Depo kendi kendine yeter: kök `CLAUDE.md`, `AGENTS.md`, `.claude/`, `opencode.json`, `.mcp.json` proje kapsamında
   okunur. Hiçbir dosyada mutlak yol yoktur; hook'lar `$CLAUDE_PROJECT_DIR`, betikler kendi konumundan göreli çözer.
2. Depo içinde **symlink yoktur**. Çalıştırma bitine güvenilmez; betikler `bash yol/betik.sh` ile çağrılır.
   Büyük/küçük harf farkıyla aynı ad kullanılmaz. (USB / exFAT uyumu.)
3. **Taşınan:** kurallar, beceriler, ajanlar, hook'lar, ayarlar, `kimlik.json`, kararlar, devir notları, varlık sayfaları,
   `HARITA.md`, kütüphane, şablonlar, betikler, model kaydı. **Git'e girmeyen** (çalışma ağacında yerel durabilir): oturum kayıtları,
   önbellekler, `node_modules`/venv, model ağırlıkları, dış klonlar, projeler, `20-sistem/durum/`, `20-sistem/gunluk/`.
   **Atölyede hiç tutulmayan:** araç giriş ve kimlik dosyaları (token, OAuth, `auth.json`). `kimlik.json` yalnızca çekirdek
   ajanın adını ve kurulum tarihini taşır; sır içermez.
4. Giriş her makinede ayrı yapılır; token taşınmaz (AGENTS.md Kesin kural 1).
5. Çevrimdışı çalışır: ağ yoksa `/baslat` pull ve giriş denetimini atlar, gerisi çalışır.

## 3. Adlandırma

1. Klasör ve dosya adları: küçük harf, Türkçe aksansız, `kebab-case`.
2. Üst düzey bölümler `NN-ad`; numara katmanın içten dışa sırasıdır (`00-cekirdek` … `90-gelen-kutusu`). Numara
   yalnızca kökte, onluk adımla. Alt klasörlerde numara yok; sıralama gerekirse tarih öneki.
3. Tarihli öğeler `YYYY-MM-DD-<ad>`; devir notları `YYYY-MM-DD-HHMM-<makine>-<konu>.md`.
4. Büyük harfli kanonik belgeler (bölümün kimliğini taşır; kök ve `00-cekirdek` dışında bir klasörde `README.md`'ye ek
   en fazla bir tane): `README.md ANAYASA.md AGENTS.md CLAUDE.md HARITA.md KARARLAR.md PLAN.md DURUM.md SURUM.md
   NEDEN.md DIZIN.md AYIKLAMA.md SKILL.md`.
5. **Saklanan bir sırrı ima eden adlar** depoda yasaktır: `*.token`, `token.json`, `secrets.*`, `*-secret.*`, `api-key*`,
   `auth.json`, `.credentials*`. Adında yalnızca "token" geçmesi yasak değildir (`token-hizi.md` serbest). İçerikteki
   sırlar ayrıca `sir-desenleri.txt` ile taranır.
6. Kesin biçim `20-sistem/denetim/kurallar/ad-regex.txt`; istisnalar `istisnalar.txt`.

## 4. Derinlik ve belgeleme

1. İnsan gezinmesi için kökten en fazla **4 klasör** derinlik. Araç biçimlerinin dayattığı derinlik
   (`skills/<ad>/SKILL.md`, `oturumlar/2026/`) sayılmaz.
2. İzlenen her klasörde bir `README.md` vardır: ne girer, ne girmez, nasıl adlandırılır. Varlık klasöründe bu
   README aynı zamanda varlık sayfasıdır (madde 12).
3. Kökte yalnızca `20-sistem/denetim/kurallar/izinli-kokler.txt` içindeki girdiler bulunur. Kökte kabuk giriş betiği olmaz.

## 5. Katmanlar ve ne nereye gider

| Katman | İçerik |
|---|---|
| `00-cekirdek/` | `kimlik.json` (çekirdek ajanın adı), ANAYASA, AGENTS, PLAN, `HARITA.md` (küre haritası), `sablonlar/` |
| `10-donanim/` | makine başına bir klasör: makine sayfası + o makinenin kurulum betikleri |
| `20-sistem/` | `kurulum/`, `denetim/`, `bakim/`, `ag/`, `servisler/`, `yedek/`, `yayin/`, `durum/`*, `gunluk/`* |
| `30-programlar/` | her CLI, uygulama ve araç kendi klasöründe (`claude-code/`, `codex/`, `mcp/`, `yerel-modeller/` …); `dis-kaynaklar/`* klonlar |
| `40-projeler/` | `DIZIN.md`, `aktif/`*, `deneme/`*; her proje kendi reposu |
| `50-arayuz/` | komut kataloğu, pano, durum satırı, `harita.html`, uzaktan erişim |
| `60-hafiza/` · `70-kutuphane/` · `80-arsiv/` | bağ dokusu: kararlar, oturumlar, dersler, tercihler · bilgi belgeleri · emekliler |
| `90-gelen-kutusu/` | dış kabuk: sınıflanmamış her şey |

\* git dışı içerik (README izlenir).

1. **Bağımlılık kuralı:** iç katmanın *içeriği* (kural, kayıt, sayfa) dış katmanın içeriğine bağımlı olmaz; dış katman
   içtekine başvurabilir. Ölçüt: dıştaki bir katman kaldırılsa da içtekinin anlamı bozulmaz. Çalıştırılabilir yardımcılar
   (`20-sistem/kurulum/lib/`, `20-sistem/denetim/`) istisnadır: her katmanın betiği onları çağırabilir. Bağ dokusuna (60–70) her katman yazar ve başvurur; hiçbir şey `80-arsiv/` ya da
   `90-gelen-kutusu/`'na bağımlı olmaz. Dizinler (`HARITA.md`, `DIZIN.md`) ve belge bağları bağımlılık sayılmaz.
2. Kökteki araç kapsamı (`.claude/`, `opencode.json`, `.mcp.json`) araç biçimi gereği kökte durur, ama katman olarak
   `50-arayuz` sayılır: her katmana başvurabilir.
3. Yeni üst katman açmak ya da katman sırasını değiştirmek bu belgeyi değiştirmek demektir (insan, major).

| Gelen şey | Yer |
|---|---|
| Ortak ajan kuralı · atölye düzeni kuralı | `00-cekirdek/AGENTS.md` · bu belge (insan) + `SURUM.md` |
| Çekirdek ajan adı · şablon | `00-cekirdek/kimlik.json` (ilk kurulumda) · `00-cekirdek/sablonlar/<tur>/` |
| Makine sayfası ve kurulum betiği | `10-donanim/<makine>/` |
| Makineye özgü geçici durum | `20-sistem/durum/<hostname>/` (git dışı) |
| Makinede çıkan sorun + çözümü | `20-sistem/bakim/bilinen-sorunlar.md` (+ `onarimlar/<ad>.sh`) |
| systemd user birimi · ağ · yedek · yayın | `20-sistem/servisler/` · `ag/` · `yedek/` · `yayin/` |
| Program sayfası · global ayar kopyası · MCP tanımı | `30-programlar/<ad>/` · `<ad>/genel/` · `mcp/<ad>/tanim.json` → kök `.mcp.json` |
| Model ağırlığı / llama.cpp ayarı | `30-programlar/yerel-modeller/agirliklar/` (git dışı) / `yapilandirma/` |
| Dış repo klonu | `30-programlar/dis-kaynaklar/<ad>/` (git dışı) + `DIZIN.md` |
| Yeni proje · atılabilir deneme | `40-projeler/aktif/<ad>/` + `DIZIN.md` · `40-projeler/deneme/YYYY-MM-DD-<ad>/` (30 gün) |
| Slash komutu · alt ajan · hook | `.claude/skills/` · `.claude/agents/` · `.claude/hooks/` (katalog `50-arayuz/`) |
| Pano · durum satırı · harita görünümü · uzaktan erişim | `50-arayuz/` |
| Karar · devir notu | `60-hafiza/kararlar/KARARLAR.md` (`/karar`) · `60-hafiza/oturumlar/YYYY/` (`/kapat`) |
| Öğrenilen ders · tercih | `60-hafiza/ogrenilenler/<konu>.md` · `60-hafiza/tercihler.md` |
| Bilgi belgesi · emekli olan her şey | `70-kutuphane/<kategori>/` · `80-arsiv/YYYY-MM-DD-<ad>/` + `NEDEN.md` |
| İndirilen dosya, fikir, belirsiz not | `90-gelen-kutusu/` (30 gün). >50 MB: klon → `30-programlar/dis-kaynaklar/`, model ağırlığı → `agirliklar/`, diğer büyük dosya → amacına uygun git dışı yer + izlenen kısa kayıt |
| **Bilmiyorsan** | `90-gelen-kutusu/`: asla köke, asla rastgele katmana |

## 6. Yaşam döngüsü

1. **Giriş:** Yeri kesin bilinmeyen her şey `90-gelen-kutusu/`'na `YYYY-MM-DD-<ad>` ile girer.
2. **Ayıklama (haftalık, `/ayikla`):** her öğe için taşı / arşivle / bekle (bekleme en fazla bir kez). Silme yalnızca
   yeniden üretilebilen geçici çıktılar için ve kullanıcı onayıyla (AGENTS.md Kesin kural 3). `AYIKLAMA.md` tarih ve bekleyenler. 30 günü geçen öğe denetimde uyarıdır.
3. **Yeni alt klasör:** gelen kutusunda aynı türde **3+ öğe** birikti **ve** mevcut hiçbir yere sığmıyorsa:
   `00-cekirdek/sablonlar/bolum/` iskeleti, README zorunlu, `KARARLAR.md` kaydı, `SURUM.md` minor.
4. **Arşiv:** "taşı, silme". `80-arsiv/YYYY-MM-DD-<ad>/NEDEN.md`: ne, neden, geri alma koşulu.

## 7. Denetim

`20-sistem/denetim/denetle.sh` düzen değişmezlerini kontrol eder. `--hizli` her oturum başında (`/baslat`) uyarır.
`--commit` her commit'te sırrı, izinsiz kök girdisini, ad ihlalini, sır ima eden adı, büyük/küçük harf çakışmasını,
symlink'i ve 50 MB'tan büyük dosyayı engeller. `--tam` haftalık ve `/denetle` ile koşar; bunlara ek olarak bayat varlık sayfası
(>30 gün), kırık göreli bağ, `HARITA.md`'de olmayan varlık ve sürüm uyuşmazlığı (madde 10.2) için uyarır. Bulgular
`/bakim` bakımcı ajanıyla onarılır; her onarım `bilinen-sorunlar.md`'ye ve gerekirse denetim kurallarına işlenir.

## 8. Haftalık gözden geçirme (30 dk)

`/baslat` → `/denetle` (tam) → `/ayikla` → `/kutuphane tara` (bayat sayfalar, sürüm nabzı) → `/projeler`
(`DIZIN.md`, `DURUM.md`'ler) → `PLAN.md` karar noktası → `/bakim` güncelleme raporu → gerekiyorsa `SURUM.md` ve yayın
(madde 10) → `/kapat`.

## 9. Yeniden yazma yasağı

Aynı işi yapan ikinci şey açılmaz. Önce `80-arsiv/`, `90-gelen-kutusu/`, `60-hafiza/` ve GitHub aranır;
bulunursa o değiştirilir. "Temiz başlangıç" yoktur: git geçmişi korunur, eski karar silinmez "geçersiz" işaretlenir,
kaldırılan şey arşivde `NEDEN.md` ile durur.

## 10. Sürümleme ve yayın

1. `SURUM.md` semver. Major: üst katman eklendi, kaldırıldı, yer değiştirdi ya da bu belge değişti. Minor: alt klasör,
   beceri, hook, betik eklendi. Patch: README, şablon, metin düzeltmesi.
2. Bu belgenin başlığındaki sürüm `N.0`'dır ve `SURUM.md`'deki son **major** (`N.0.0`) ile uyuşur. Minor ve patch
   sürümler başlığı değiştirmez.
3. Her `SURUM.md` sürümü iki repoda aynı `vX.Y.Z` etiketini ve GitHub release'ini alır: gizli `kaan4kbulut-ai-workspace`
   (tam atölye) ve açık `portable-ai-workspace` (kişisel içeriksiz iskelet). Release notu `SURUM.md` bölümünden gelir;
   açık repoya yalnız `20-sistem/yayin/yayinla.sh` çıktısı gider; o çıktı kişisel iz taramasından geçmeden yayımlanmaz.
   Açık repodaki release notları ve haritalar kişisel içerikten arındırılır. Push ve yayın kullanıcı onayıyla yapılır
   (AGENTS.md Kesin kural 3).

## 11. Çekirdek ajan

1. Atölye kökünde çalışan tek ajan çekirdek ajandır. Adı ilk kurulumda klasör adından önerilir, kullanıcı onaylar,
   `00-cekirdek/kimlik.json`'a yazılır. `/<ad>` komutu pano ve ana menüdür.
2. Claude Code'da settings `agent` anahtarıyla açılır. Ajan dosyası incedir (boş gövde); kurallar `CLAUDE.md`,
   `.claude/rules/` ve becerilerde durur.
3. Kullanıcı slash komutlarıyla çalışır: `/<ad>`, `/baslat`, `/kapat`, `/kur`, `/araclar`, `/programlar`, `/donanim`,
   `/projeler`, `/karar`, `/ayikla`, `/denetle`, `/bakim`, `/kutuphane`. Kabuk giriş betiği yoktur; `denetle.sh`, `kur.sh`
   gibi betikler komutların arkasındaki iç araçlardır.
4. Diğer CLI'lar (çekirdek ajan olmadan açılan claude, codex, opencode, agy) kökte başlatılmaz ve kökü, `00-cekirdek/`,
   `10-donanim/`, `20-sistem/`, `60-hafiza/`'yı düzenlemez. Ya kendi proje/program klasörlerinde başlatılır ya da çekirdek
   ajan onları kendi resmi girişleriyle çağırır (`codex exec -C <klasör>`; opencode ve agy için önce çalışma dizini hedef
   klasöre alınır, sonra `opencode run` / `agy -p`). Giriş, token ya da oturum anahtarı aktarılmaz (AGENTS.md Kesin kural 1).
   Bu sınır claude ve opencode'da ayar ve izinle sert, codex ve agy'de AGENTS.md ile yumuşaktır.

## 12. Varlık sayfaları (küre)

1. Her varlığın (makine, araç, program, proje, servis) kendi katmanında **tek** sayfası vardır: klasörünün `README.md`'si.
   Klasör git dışıysa (proje, dış klon) sayfa katmanın `sayfalar/<ad>.md` dosyasıdır ve git'te izlenir; ad çakışmasında
   önce `DIZIN.md`'deki ad esas alınır. Başka yerler sayfayı kopyalamaz, bağ verir.
2. Sayfa ön bilgisi (front-matter) şu alanları taşır: `katman` (numarasız katman adı, ör. `programlar`), `surum`, `son_kontrol` (`YYYY-MM-DD`),
   `kaynaklar` (resmi belge/repo adresleri), `baglar` (ilgili sayfalara göreli yollar).
3. Sayfalar arası bağlar göreli markdown bağıdır (`[monster](../../10-donanim/monster/README.md)`); mutlak yol ve wiki
   bağı (`[[...]]`) kullanılmaz. Atölye Obsidian kasası olarak da açılabilir.
4. `00-cekirdek/HARITA.md` tüm varlıkları katman sırasıyla dizinler; yeni sayfa ve HARITA satırı aynı commit'te girer.
   `50-arayuz/harita.html` (iç içe halkalar) HARITA'dan üretilir.
5. Kütüphaneci (çekirdek ajanın alt ajanı) sayfaları istek üzerine (`/kutuphane`) ve haftalık taramayla taze tutar.
   Zamanlama yereldir (systemd user timer + resmi `claude -p`); bulut görevleri yerel dosyaya erişemediği için kullanılmaz.
   `son_kontrol` değeri 30 günden eskiyse denetimde uyarıdır.
6. Vektör ya da çizge veritabanı kullanılmaz: dizin, bağlı sayfa ve hedefli okuma yeter. Kanıt
   `60-hafiza/kararlar/KARARLAR.md` (2026-10-23 gece): Türkçe BM25 isabeti %0, FTS5 okunan metni ~10 kat büyüttü.
   100+ sayfada yeniden ölçülür; karar değişirse bu belge de değişir.

## 13. Bu belgenin korunması

1. Bu belgeyi yalnızca insan düzenler (AGENTS.md Kesin kural 5). Üç koruma katmanı vardır: settings `deny`,
   `anayasa-koruma.py` hook'u ve dosya izni `444` (`kur.sh`). Hiçbiri tek başına yeterli sayılmaz.
3. Yıkıcı komut koruması kalıcı olarak iki katmanlıdır: genel kurallar için `cc-safety-net` (sürümü sabit; yükseltme
   yalnızca en az 7 günlük bir sürüme ve değişiklik notu okunduktan sonra), atölyeye özgü kurallar (taşı-silme, ANAYASA,
   symlink, proje dışı yazma) için `yikici-koruma.py`. İkisi de testlidir (`20-sistem/denetim/testler/`).
4. Ajanlara özel kalıcı hafıza (`memory` alanı, araçların otomatik hafızası) kullanılmaz; kalıcı bilgi `60-hafiza/`'dadır.
2. Ajan değişikliği önerir: madde numarası, eski metin, yeni metin, gerekçe. İnsan uygularsa aynı commit'te `SURUM.md`
   major satırı ve `KARARLAR.md` kaydı yazılır; sürüm iki repoda yayımlanır (madde 10.3).
