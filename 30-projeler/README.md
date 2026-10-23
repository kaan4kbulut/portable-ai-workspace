# 30-projeler — Projeler

İşletim sisteminin **kullanıcı alanı**. Her proje **kendi git reposudur**; atölye yalnızca `DIZIN.md` (indeks) ve `sablon/`'u izler
(`aktif/*/` ve `deneme/*/` `.gitignore`'da).

| Klasör | İçerik |
|---|---|
| `DIZIN.md` | ad · repo · durum (aktif/duraklatıldı/bitti) · son dokunma · not |
| `sablon/` | yeni projeye kopyalanacak iskelet: `CLAUDE.md` (`@AGENTS.md`), `AGENTS.md`, `DURUM.md`, `README.md`, `.gitignore`, `.claude/settings.json` |
| `aktif/<ad>/` | çalışılan projeler (klon) |
| `deneme/YYYY-MM-DD-<ad>/` | atılabilir denemeler; 30 gün sonra arşiv ya da sil kararı |

Yeni proje: `gh repo clone <repo> 30-projeler/aktif/<ad>` → `sablon/` dosyalarını projeye kopyala (projenin kendi commit'i) →
`DIZIN.md`'ye satır → `10-sistem/durum/<host>/aktif-proje.txt`'e adını yaz (SessionStart bağlamına girer).
Proje içinde `claude` açıldığında projenin `.claude/`'ı geçerlidir; atölye kuralları `AGENTS.md`'deki yönlendirmeyle gelir.

**Girer:** proje klonları, indeks, şablon. **Girmez:** proje kodu atölye reposuna (asla), dış klonlar (→ `90-dis-kaynaklar/`).
