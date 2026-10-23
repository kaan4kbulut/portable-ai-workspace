# 20-sistem/denetim — Düzen denetimi

`denetle.sh` atölyenin değişmezlerini kontrol eder; kurallar kod değil **veri** olarak `kurallar/` altındadır, böylece
bakımcı ajan yeni kural ekleyebilir.

| Dosya | Görev |
|---|---|
| `denetle.sh [--hizli\|--commit\|--tam]` | Çıkış 0 temiz · 1 uyarı · 2 hata. Satır biçimi `[HATA\|UYARI\|OK\|BILGI] kural · yol · öneri` |
| `kurallar/izinli-kokler.txt` | Kökte bulunabilecek girdiler (ANAYASA 4.3) |
| `kurallar/ad-regex.txt` | 1. satır dizin, 2. satır dosya adı deseni (ANAYASA 3) |
| `kurallar/sir-desenleri.txt` | İzlenen dosyalarda asla görünmeyecek desenler |
| `kurallar/istisnalar.txt` | Araçların dayattığı adlar/yollar (denetim dışı) |
| `git-hooks/pre-commit` | `kur.sh` bunu `core.hooksPath` ile bağlar; `--commit` kipinde hata = commit engellenir |

Kipler: `--hizli` SessionStart hook'u ve `/kapat`; `--commit` pre-commit; `--tam` `/baslat`, haftalık gözden geçirme, `/bakim`.
`--tam` giriş durumunu yalnızca aracın kendi komutuyla sorar (`gh auth status`, `codex login status`, `opencode auth list`); kimlik dosyası okumaz.

**Girer:** denetim betiği ve kural verileri. **Girmez:** onarım (→ `../bakim/`), kurulum (→ `../kurulum/`).
