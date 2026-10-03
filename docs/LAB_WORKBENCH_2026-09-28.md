# Laboratuvar masası

Ana rota artık ortak çalışma masasıdır. Mevcut reçete aracı /analyze altında korunur; /explore ve /experiments ortak menüden erişilir. Ana masa canlı API bağlantısını gösterir; bağlantı bilimsel doğrulama anlamına gelmez.

Malzeme kimliği, deney koşulları ve ölçüm kaynağı için başlangıç kontrol listesi eklenmiştir. Deney JSON dosyasını açma/kaydetme akışı mevcut deney ekranındadır. Araçlar arasında otomatik veri aktarımı ve otomatik deney kaydı yoktur. Isı–zaman modülü henüz arayüze bağlanmadığından etkin araç olarak sunulmaz. Bilimsel motor değiştirilmemiştir.

Doğrulama: TypeScript noEmit geçti. Playwright ile ana masa, üç rota, aktif menü, canlı bağlantı, 390px taşma kontrolü; dönüşüm hesabı ve deney karşılaştırma/kaydetme/açma regresyonları geçti. Eksik favicon isteği saptanıp SVG uygulama ikonu ile düzeltildi. Masaüstü ve mobil emülasyon ekranları screenshots/ altında; gerçek telefon testi yapılmadı.

Sıradaki iş: kaydedilmemiş deney girdilerini sayfa geçişinde koruma ve sürümlü ortak deney bağlamı. Daha sonra ısı modeli yalnızca gerekli malzeme parametreleri, sınır koşulları ve doğrulama bilgisiyle arayüze bağlanmalı.
