# Diff incelemesi

`degisiklik.diff` içinde üç davranış/güvenlik hatası var. `orders.py` dosyasının `json` modülünü zaten içe aktardığını, `amount` değerlerinin ondalıklı ve tutarların negatif olmayan sayılar olduğunu varsay. Değişiklik sonrası satırlar: 1 `def load_settings`, 2 dönüş, 3 boş, 4 `def total_orders`, 5 toplam, 6 döngü, 7 koşul, 8 toplama, 9 koşul, 10 dönüş.

`bulgular.json` üret: `{"bulgular": [{"satir": 2, "aciklama": "somut hata ve etkisi"}]}`. Her bulgu hatalı yeni satır numarasını ve açıklamasını içermeli. Puan satır + anahtar sözcük eşleşmesiyle hesaplanır; aynı hata en fazla bir kez sayılır. Girdiyi değiştirme, kodu düzeltme, ağa çıkma.
