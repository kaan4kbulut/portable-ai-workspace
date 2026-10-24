# Kadro ölçümleri

**Girer:** tekrarlanabilir görevlerden gelen, satır başına bir JSON nesnesi taşıyan
`YYYY-MM-DD.jsonl` ölçümleri. **Girmez:** giriş bilgileri, gizli metinler, ham
istemler, model çıktıları, ikili dosyalar ve geçici yazma/kilit dosyaları.
Bu iskelet gerçek deney sonucu içermez.

Alanlar:

| Alan | Biçim |
|---|---|
| `gorev` | `kod-duzeltme`, `inceleme`, `turkce-belge`, `arastirma`, `mekanik-tasima` veya `basit`; deney adı değil iş türü |
| `cli` | `kadro.json` sağlayıcı eşlemesindeki CLI adı |
| `model` | Boş olmayan model adı; envanter öncesinde `varsayilan` |
| `efor` | `low`, `medium` veya `high` |
| `sure_sn` | Sonlu, sıfır veya pozitif sayı |
| `basari` | true/false, 0–1 oranı veya null |
| `puan` | 0–5 puanı veya null; başarı ile aynı anda null olamaz |
| `kota_farki` | Yüzde puan cinsinden tüketim, bilinmiyorsa null; sıfırlanmada negatif olabilir |
| `not` | Gizli bilgi içermeyen kısa açıklama metni; boş olabilir |
| `id` | İsteğe bağlı, boş olmayan deney kimliği; bağımsız tekrarlar için farklı verilir |

Aşağıdaki satır yalnız biçim örneğidir, gerçek ölçüm değildir:

```json
{"id":"ornek-kod-001","gorev":"kod-duzeltme","cli":"codex","model":"varsayilan","efor":"high","sure_sn":12.5,"basari":true,"puan":null,"kota_farki":0.2,"not":"Yalnız biçim örneği"}
```

Dokuz temel alan zorunludur; bilinmeyen alanlar, yinelenen JSON anahtarları,
NaN/sonsuz sayılar ve bozuk satırlar reddedilir. Boş satırlar atlanır;
tamamen boş dosya hatadır. `ogren` kaynak dosyayı değiştirmez.

```bash
python3 -I -B 20-sistem/kadro/kadro.py ogren 20-sistem/kadro/olcumler/2026-10-23.jsonl
```

Kimlik ve sayaçlar üst klasördeki `kadro.json` içinde atomik güncellenir.
İş türü × CLI × model × efor dışındaki deney ayrımı `id` ile yapılır.
