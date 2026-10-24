# Belge içerik rubriği

Değerlendirici, yazan modelden farklı sağlayıcıya ait olmalıdır. Yazan CLI/model ve inceleyen CLI/model kaydedilir. Her madde 0 veya 1 puan; toplam 0–5.

- Verilen davranış doğru aktarılır; dosya değiştirdiği iddia edilmez.
- Kullanım komutu ve Python 3 gereksinimi doğru verilir.
- Girer/Girmez kapsamları şemaya uygundur.
- Adlandırma kuralı doğru ve somut örnekle açıklanır.
- Türkçe açık, kısa ve tutarlıdır; sağlanmayan özellik uydurulmaz.

Çıktı: `yazan`, `inceleyen`, beş madde puanı, toplam ve gerekçe. İstenirse toplam/5 ile normalize edilir. Bu puan koşucunun yapısal `puan` alanının yerine otomatik yazılmaz; ayrı inceleme kaydı olarak çekirdek ajana verilir.
