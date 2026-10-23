# testler/

Atölye hook'larının ve denetim kurallarının testleri. Yalnızca standart kütüphane (`unittest`); ağa ve ev klasörüne dokunmaz,
dosya yazmaz.

```bash
python3 10-sistem/denetim/testler/hook-testleri.py -v
```

| Dosya | Ne sınar |
|---|---|
| `hook-testleri.py` | `.claude/hooks/yikici-koruma.py` (reddet / sor / izin vakaları, bilinen yanlış pozitifler) ve `anayasa-koruma.py` |

Hook değiştiren her commit bu testleri geçmelidir. Yeni bir kaçak ya da yanlış engel bulunduğunda önce buraya vaka eklenir,
sonra hook düzeltilir.

**Girer:** atölye betik/hook testleri. **Girmez:** proje testleri (projenin kendi reposunda).
