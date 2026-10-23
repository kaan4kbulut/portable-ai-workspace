---
katman: programlar
surum: 2.103.0
son_kontrol: 2026-10-23
kaynaklar: [https://cli.github.com/manual, https://github.com/cli/cli]
baglar: [../README.md, ../../10-donanim/monster/README.md, ../claude-code/README.md]
---

# GitHub CLI (`gh`)

## Nedir
GitHub'ın resmi komut satırı aracıdır (`gh version 2.103.0 (2026-10-21)`).
Depo yönetimi, PR/issue işlemleri, sürüm yayınlama (`release`), API sorguları ve Git kimlik doğrulaması için kullanılır.

## Atölyedeki rolü
- **Tekrarı önleme ve depo envanteri:** Yeni bir araç veya proje açmadan önce `gh repo list kaan4kbulut` ile mevcut 22+ gizli/arşiv repo taranır (`00-cekirdek/AGENTS.md`).
- **İki sürümlü yayın akışı:** Gizli `kaan4kbulut-ai-workspace` ve açık `portable-ai-workspace` repolarında ortak `vX.Y.Z` etiketlerini ve GitHub release'lerini yönetir (`60-hafiza/kararlar/KARARLAR.md`).
- Emekli edilen repolar silinmez, `gh repo archive kaan4kbulut/<ad>` ile arşivlenir (geri alma: `gh repo unarchive`).

## Kurulum ve giriş
- Kurulum betiği: `bash 20-sistem/kurulum/araclar/gh.sh` (GitHub `cli/cli` son sürüm tarball'ını indirip `~/.local/bin/gh` altına sudo gerektirmeden kurar).
- Giriş yalnızca aracın kendi komutuyla (makine başına) yapılır: `gh auth login` ve HTTPS git işlemleri için `gh auth setup-git`.
- Giriş durumu (`denetle.sh --tam` tarafından da çağrılır): `gh auth status`.
- Takma adların yüklenmesi: `gh alias import 30-programlar/gh/takma-adlar.yml`.

## Etkileşimsiz çağırma
`gh --help` ve `gh auth --help` ile bu makinede doğrulanan komutlar:
```bash
gh auth status
gh repo list kaan4kbulut --limit 100 --json name,isPrivate,isArchived,pushedAt
gh repolar
gh release create v1.0.0 --repo kaan4kbulut/portable-ai-workspace --notes-file SURUM.md
gh api repos/kaan4kbulut/kaan4kbulut-ai-workspace
```
- Seçenekler: `--json <alanlar>`, `--jq <ifade>`, `--template <go-template>`, `-R`/`--repo <[HOST/]OWNER/REPO>`.
- `30-programlar/gh/takma-adlar.yml` içindeki `repolar` takma adı, oturum açmış kullanıcının repolarını ad, gizlilik (`gizli`/`acik`), arşiv durumu (`arsiv`/`aktif`) ve son push tarihiyle sekme ayrılmış olarak listeler.

## Okuduğu dosyalar
- **Kullanıcı ayarları:** `~/.config/gh/config.yml` (`git_protocol`, `editor`, `prompt`, `pager`, `aliases`).
- **Kimlik durumu (asla okunmaz/taşınmaz):** `~/.config/gh/hosts.yml` (veya sistem anahtarlığı). `.claude/settings.json` içinde `Read(~/.config/gh/**)` kuralıyla ajan erişimine kapatılmıştır.
- **Atölye şablonu:** `30-programlar/gh/takma-adlar.yml` (git'te izlenen takma ad tanımı).

## Dikkat
- **Yıkıcı işlem sınırı (`AGENTS.md` Kesin kural 3):** GitHub repo ayarı değiştirme, görünürlüğü açma (`--visibility public`), repo silme veya release/push işlemleri kullanıcıdan açık onay alınmadan yapılmaz.
- **Kimlik güvenliği:** `gh auth token` çıktısı veya `~/.config/gh/hosts.yml` içeriği sohbete, günlüğe ya da depoya asla yazılmaz (`sir-desenleri.txt` `ghp_`, `gho_`, `github_pat_` kalıplarını commit'te engeller).

## Eksikler
- `kur.sh` içinde `gh alias import 30-programlar/gh/takma-adlar.yml` adımının otomatikleştirilmesi (şu an elle içe aktarılıyor).
