# Dönüşüm atlası — ilk çalışan görsel modül

Yerel adres: http://127.0.0.1:3000/explore

Saf CaCO3 → CaO + CO2 dönüşümü için verilen başlangıç kütlesi ve kullanıcı
tarafından varsayılan dönüşüm oranı ile kütle hesabı. Reaksiyon dengesi ve
atomik kütleler mevcut Python foundation modülünden gelir. POST
/api/v1/reactions/calcite arayüze sonuç ve 21 dönüşüm noktası döndürür.

Grafiğin yatay ekseni sıcaklık/zaman değil dönüşüm oranıdır. Üç türün kalan
ve oluşan kütlesi gram cinsindedir. CO2 hacmi, tutulma miktarı, pinhole riski,
faz dengesi, sonraki reaksiyonlar veya herhangi iki malzemenin etkileşimi
hesaplanmaz. Saflık, tek reaksiyon ve verilen dönüşüm varsayımları görünürdür.

## Kaynak kontrolü

28 Eylül 2026 resmi NIST yayın kaydı ve birincil araştırma yayıncı özeti
incelendi. Tam metin kinetik katsayıları alınmadı. Yeni bağımlılık kurulmadı.

- https://www.nist.gov/publications/precision-calcination-mechanism-caco-3-high-porosity-nanoscale-cao-co-2-sorbent
- https://www.sciencedirect.com/science/article/pii/S0009250902001379

Bu kaynaklar dönüşüm ve koşul bağımlılığına dayanak; tüm seramikler için
evrensel eşik veya kalibre edilmiş kinetik model sayılmaz.

## Test ve kullanıcı deneyimi

Dört yeni çekirdek test: uç dönüşümler, bağımsız yaklaşık gaz oranı,
kütle dengesi/ölçekleme, geçersiz giriş ve tekrar üretim. TypeScript kontrolü
geçti; OpenAPI ve üretilmiş istemci türleri güncellendi.
Mevcut görünür/ekran dışı Playwright kitiyle API grafiği, bileşik açıklaması,
tam dönüşüm, negatif kütle hatası/iyileşme ve 390px yatay taşma kontrolü geçti.
Tarayıcı pageerror görülmedi. Gerçek mobil cihaz testi veya fiziksel
deney doğrulaması değildir. Ekran görüntüleri screenshots/ altında.

Yeni modül deney dosyasına henüz kaydedilmez. Reçete masası ve deney
karşılaştırması bağlantıları mevcut; bu, hesap zincirlerinin bilimsel olarak
birleştiği anlamına gelmez. Sonraki adım: ısı modelinin destekli girdilerini
ayrı görsel alana taşımak; dönüşüm-zaman bağlantısını gerçek kinetik veri
olmadan oluşturmamak.
