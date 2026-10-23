# 10-sistem/durum — Makineye özgü geçici durum (git dışı)

`kur.sh`, `basla.sh` ve hook'lar hostname başına bir klasör yazar: `<hostname>/`
- `profil-otomatik.md` — OS, mimari, dosya sistemi, araç sürümleri (her kurulumda tazelenir)
- `yollar.env` — bulunan araç yolları
- `ilk-kurulum.txt` — tarih, makine, atölye sürümü, `genel=1` (global bağlantılar kurulduysa)
- `son-denetim.txt`, `guncelleme-raporu.md` — son çıktılar
- `son-oturum.json` — SessionEnd hook'u; `/kapat` ve `kapat.sh` ham maddesi
- `aktif-proje.txt` — bu makinede üzerinde çalışılan proje adı
- `oturum-<id>.isaret` — Stop hook'unun "bir kez hatırlat" işaretleri
- `notlar.md` — bakımcının yalnızca bu makineyi ilgilendiren notları

**Girmez:** kimlik dosyaları (asla), depoya girecek hiçbir şey (bu klasör `.gitignore`'dadır).
