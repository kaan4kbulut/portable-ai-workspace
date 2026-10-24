# Kadro testleri

**Girer:** seçimin kota ve sağlayıcı kapılarını, Bayes karışımını, öğrenmenin
tekrarsızlığını ve atomik yazmasını sınayan stdlib `unittest` dosyaları.
Adlar küçük harfli, aksansız ve kebab-case olur; giriş `kadro-testleri.py`dir.
**Girmez:** gerçek model çağrıları, ağ istekleri, gerçek ev klasörü, canlı kota
yenilemesi ve kalıcı ölçüm sonuçları.

Depo kökünden:

```bash
python3 -I -B 20-sistem/kadro/testler/kadro-testleri.py
```

Testler sahte kota listeleri ve geçici klasörler kullanır; süreç, ağ bağlantısı
ve gerçek ev klasörünü bulma girişimleri hata verir. Kota okuyucusunun bağlantı
testi de yalnız geçici kök, sahte Codex kayıt klasörü ve agy önbelleği kullanır.
Gerçek `kadro.json` yalnız okunur; öğrenme kopyada sınanır.
