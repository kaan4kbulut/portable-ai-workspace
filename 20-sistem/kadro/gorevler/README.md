# Ölçüm görevleri

## Girer

Beş sabit görev kendi kebab-case klasöründe bulunur. Her klasörde kapsam
README’si, `istem.md`, `degerlendir.py`, `girdi.json`, `cozum.json` ve varsa
`rubrik.md` yer alır; alt klasör bulunmaz.

Manifestolar UTF-8 JSON nesnesidir: göreli POSIX dosya yolu → metin içeriği.
Koşucunun `hazirla` komutu yalnız `girdi.json` dosyasını açar. Testler
`cozum.json` içeriğini geçici çalışma klasörüne açar. Böylece depoda en çok
dört klasör derinliği korunurken çalışma girdilerinde iç içe yollar kullanılabilir.
Değerlendirme sabitleri `../olcum/destek.py` içinde korunur.

## Girmez

Gerçek ölçüm çıktıları, model oturumları, giriş bilgileri ve alt klasörler.
Referans çözümler, rubrik ve değerlendirme kodu modele verilmez.

## Çalıştırma

Depo kökünden `python3 -I -B 20-sistem/kadro/gorevler/<gorev>/degerlendir.py calisma`
çalıştırılır. Koşucu ve test komutları [ölçüm belgesindedir](../olcum/README.md).
