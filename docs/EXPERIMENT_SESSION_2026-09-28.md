# Oturum içi deney taslağı

ExperimentSession kök layout içinde deney girdilerini ve rapor arşivini bellekte tutar. Next.js uygulama içi navigasyonu bunları silmez. Kalıcı tarayıcı depolaması veya sunucu kaydı eklenmedi; tam sayfa yenileme ve kapatma oturumu siler. JSON export/import kalıcı kopya yöntemidir.

Güncel rapor ve bağlam onayı sayfa yerelinde kalır; geri dönüldüğünde yeniden karşılaştırma gerekir. Sayfadan ayrılırken istek revision numarası artırılır; geç dönen istek arşive rapor ekleyemez.

TypeScript kontrolü geçti. Playwright testi sentetik hesap, export, ana masaya geçip geri dönme, satır ve arşiv korunması, onay sıfırlanması, yenilemede temiz taslak, JSON açma, hatalı JSON, yeniden hesap, stale sonuç temizleme, geçersiz zaman ve mobil taşma kontrollerini geçti. Gerçek fiziksel doğrulama yapılmadı. Ortak reçete/ısı modeli bağlantısı henüz eklenmedi.
