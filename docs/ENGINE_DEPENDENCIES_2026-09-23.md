# Motor bağımlılıkları — gerçek edinme ve kurulum

## Yapılanlar

Resmi GitHub/PyPI kaynaklarından 8 dosya, 26.606.990 bayt indirildi.
Arşiv: `storage/engine-dependencies/2026-09-23/`.
Manifest kaynak URL, lisans, yazar, commit/sürüm, zaman, boyut ve SHA-256 içerir.
GitHub arşivleri açılmadı veya çalıştırılmadı. Manifestteki 8 dosyanın hash'i
indirme sonrasında tekrar kontrol edildi. Mevcut web ve FEM ortamı değiştirilmedi.

| Bileşen | Sabit sürüm | Teslim durumu |
|---|---|---|
| CoolProp | 8.0.0 | Resmi Windows wheel indirildi, ayrı Python ortamında kuruldu |
| NumPy | 2.2.6 | CoolProp bağımlılığı; aynı ayrı ortamda kuruldu |
| Hamopy | 5ed90e804a38b557871d2042203c38e4e78c017e | Tam repository ZIP + LGPL lisansı arşivlendi; kurulmadı |
| HygroThermFEM | 975ad27674e104794485aa53b1529719e7b94af2 | Tam repository ZIP + LBNL lisansı arşivlendi; derlenmedi |

CoolProp MIT; NumPy BSD ve wheel içindeki üçüncü taraf bildirimleri korunmalı.
Hamopy LGPL-3.0; dağıtım/bağlama yükümlülükleri üretim entegrasyonundan önce ayrıca değerlendirilmeli.
HygroThermFEM lisansı BSD-benzeri izinlere ek LBNL hükümleri içeriyor; basitçe MIT diye etiketlenmedi.
Lisansların izin vermesi modellerin seramik pişirimine bilimsel uygunluğunu kanıtlamaz.
Upstream bağımlılıklar, alt modüller ve derleme ortamı ZIP arşivlerinin içinde bütünüyle sağlanmış sayılmaz.

## Kullanılabilir yeni arayüz

`research.thermal.water.pure_water(temperature_k, pressure_pa)`:
saf su için yoğunluk (kg/m³), entalpi/iç enerji (J/kg), cp (J/kg/K) ve faz döndürür.
CoolProp isteğe bağlı ve gecikmeli yüklenir; çekirdek kimya bunu gerektirmez.
Bu sürüm yalnız 273.16–473.15 K ve 10.000–1.000.000 Pa araştırma alanında
sıvı/gaz tek faz durumlarını kabul eder. Bu sınırlar proje kapsamıdır, CoolProp'un
tüm fiziksel geçerlilik alanı değildir. Doygunlukta belirsiz T/p girdisi hata verir.
NaN, Infinity, bool ve kapsam dışı değerler reddedilir. Sürüm 8.0.0 dışında
yeniden inceleme gerekir. Bilinmeyen belirsizlik null, sıfır değil.

Bu arayüz gözenek basıncı, nemli hava, bağlı su, kinetik kuruma, sır erimesi veya
fırın programı çözmez. Mevcut buhar modülüyle enerji/kütle bağlantısı henüz kurulmadı.
Web/API'ye eklenmedi. Yeni bir kullanıcı eklentisi/ücretli servis gerekli olmadı;
yerel bilimsel kütüphane ve resmi kaynak indirme araçları yeterliydi.

## Doğrulama

- 5 ayrı kurulum/tutarlılık testi: sıvı/gaz, h=u+p/rho, geçersiz giriş, tekrar üretim.
- `pip check`: uyumsuz bağımlılık yok.
- Mevcut 208 araştırma testi tekrar geçti.
- Testler bağımsız IAPWS kontrol noktası doğrulaması veya fiziksel deney değildir.
- Hamopy/HygroThermFEM için derleme ya da örnek çalışma testi yapılmadı.

```text
storage/engine-dependencies/2026-09-23/environment/Scripts/python.exe scripts/verify_water_dependency.py
```

`scripts/acquire_engine_dependencies.py` önceden var olan/yarım indirmeyi ezmez.
PyPI hash doğrulaması ve boyut sınırı uygular; indirme ile kod çalıştırma ayrıdır.
İndirilen dosyalar Git'e alınmadı; küçük manifest ve kilit dosyası alındı.

## Sıradaki iş

Bağımsız su özelliği referans testleri → sentetik tek numunede enerji/kütle
dengesi ve korunum hatası → zaman adımı yakınsaması → gerçek kuruma serisiyle
karşılaştırma. Hamopy denklemleri bu aşamada referans/benchmark adayı;
HygroThermFEM ise 2B ihtiyaç ortaya çıktığında değerlendirilir.
Cantera/pycalphad bu tur kurulmadı: uygun faz ve kinetik veri olmadan yeni
çözücüler eklemek mevcut bilimsel eksikliği çözmez.

Kaynaklar:
- https://github.com/CoolProp/CoolProp
- https://pypi.org/project/CoolProp/8.0.0/
- https://pypi.org/project/numpy/2.2.6/
- https://github.com/srouchier/hamopy
- https://github.com/LBNL-ETA/HygroThermFEM
