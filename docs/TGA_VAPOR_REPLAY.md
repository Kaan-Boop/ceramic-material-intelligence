# TGA ölçüm hesabı → buhar senaryosu

Tarih: 22 Eylül 2026. Araştırma teslimi; üretim veya fiziksel validasyon değildir.

## Çalışan kapsam

`research/thermal/tga.py` iki saf fonksiyon sunar:

- `analyze_trace(trace)`: mutlak numune kütlesi mg, geçen süre s ve numune sıcaklığı °C kayıtlarından işaretli net kütle kaybı ve aralık ortalaması kg/s hesaplar. Düzensiz zaman adımlarını destekler. Kaynak, numune, atmosfer, kütle bazı ve MEASURED/SYNTHETIC kökeni zorunludur.
- `replay_water(trace, allocations, chamber)`: her aralıktaki net kaybın su payı açıkça verilmişse mevcut buhar kontrol hacmine aktarır. SCENARIO_ASSUMPTION veya kaynağı belirtilmiş QUANTITATIVE_ALLOCATION gerektirir. İkinci etiket kalibrasyonun kod tarafından doğrulandığı anlamına gelmez.

Çıktılar orijinal girdi snapshot'ı, hash, motor sürümleri, aralık sonuçları ve durum taşır. Hesaplanan ölçüm türevi CALCULATED; hazne senaryosu PREDICTED'dır. Eksik belirsizlik sıfır sayılmaz. TGA net kayıp hızı gerçek bir tür salım hızı değildir; eşzamanlı oksidasyon/kütle kazanımı gibi süreçler ek kanıt gerektirir.

## Koruma kuralları

- Kütle yüzdesi girişinde referans baz tahmin edilmez; bu sürüm mutlak mg ister.
- Kayıtlar sessizce sıralanmaz; aynı veya geriye giden zaman reddedilir.
- Kütle artışı korunur; smoothing veya sıfıra kırpma yoktur. Böyle bir iz gaz replay için bloke edilir.
- Su payı bilinmiyorsa toplam kayıp otomatik H2O yapılmaz. Nitel MS/FTIR tür tespiti miktar kalibrasyonu yerine geçmez.
- Numune kütlesi gerçek fırın yüküne ölçeklenmez; bu dönüşüm ısı/kütle transferi benzerliği gerektirir.
- Hazne sıcaklığı, numunenin sıcaklık programından ayrı ve sabittir. Numune sıcaklıkları buhar modeline fırın sıcaklığı olarak gönderilmez.
- Doygunluk aşılınca o aralık UNAVAILABLE olur, sonraki aralıklar çalıştırılmaz. Önceki geçerli yoğunluk son sonuç gibi gösterilmez.

## Kanıt ve kaynak havuzu

1. [METTLER TOLEDO — Evolved Gas Analysis Guide](https://www.mt.com/us/en/home/library/guides/lab-analytical-instruments/ta-ega.html): üreticinin web açıklaması incelendi. TGA kütle değişimini, bağlı gaz analiz yöntemleri çıkan gazların tanımlanmasını sağlar. Kullanım: yöntem sınırı referansı; tam rehber veya sayısal veri kopyalanmadı, dataset yeniden dağıtım hakkı varsayılmadı.
2. [Quantitative Analysis by Thermogravimetry-Mass Spectrum Analysis for Reactions with Evolved Gases](https://pmc.ncbi.nlm.nih.gov/articles/PMC6235619/): arama özetinde kalibrasyon ve gaz kütle debisi karşılaştırması görüldü. Tam metin erişiminde CAPTCHA çıktı; aşılmadı, tam metin okunmuş sayılmadı. Lisans doğrulanmadığından veri aktarılmadı. Araştırma adayı olarak tutuluyor.

Bu teslimin denklemi sonlu aralıktaki kütle farkının süreye bölünmesidir; sayısal bir kinetik katsayı makaleden alınmadı. Gaz tanımlama ve nicel tahsis konusunda ikinci kaynağın tam metin doğrulaması açık iş olarak kalıyor.

## Sentetik kabul örneği

Numune: 10 mg → 9 mg → 8 mg; süre: 0 → 10 → 30 s. İlk aralık 1e-7 kg/s, ikinci aralık 5e-8 kg/s net kayıp verir. Her aralığın %50'si varsayımsal su olarak seçildiğinde toplam 1e-6 kg H2O olur. 1 m³, havalandırmasız, sıfır başlangıç nemli ve doygunluğun aşılmadığı sentetik haznede son yoğunluk 1e-6 kg/m³'tür. Bu veri gözlem olarak etiketlenmez.

```powershell
.\storage\simulation\00_environment\Scripts\python.exe -X utf8 -m unittest tests.test_tga -v
.\storage\simulation\00_environment\Scripts\python.exe -X utf8 -m unittest discover -s tests
```

Son doğrulama: 169 test geçti, 9.305 saniye, atlanan test yok. Yeni 10 test: birimler/zaman adımları, kütle korunumu, kütle artışı, bilinmeyen gaz, entegre su bütçesi, doygunlukta durma, replay/snapshot, geçersiz girdiler, metadata ve nitel gaz bilgisini miktar sanmama.

## Eksikler / sonraki teslim

Gerçek izinli ölçüm serisi henüz içeri alınmadı. Cihaz CSV format adaptörü, blank/buoyancy düzeltmesi, ölçüm belirsizliği, TGA–MS zaman gecikmesi, kalibrasyon incelemesi ve enerji eşleştirmesi yok. Çekirdek aralık hesabı test edildi; fiziksel numuneye karşı validasyon yapılmadı. Sonraki adım, koşulları ve hakları açık tek bir ölçüm serisini edinip bu sözleşmeyle doğrulamak. Sonra ölçümlü su salımını sabit hazne deneyine karşı kıyaslamak; bundan önce yeni fırın programı için kinetik tahmin iddiası yok.
