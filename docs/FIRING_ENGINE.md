# Pişirim sözleşmesi

M4 bağlam girişi; M6 plan ve gerçek run/numune kaydı. Fırına komut veren kontrol sistemi değildir.

## Cone

`cone_system`, `cone_code`, `cone_type`, `reference_version`, son aralıktaki `heating_rate`, varsa witness cone gözlemi ayrı tutulur. `06` ve `6` farklıdır; cone_code string ve kontrollü listedir. Unknown code sessiz integer dönüşümüyle kabul edilmez.

Hedef cone, program tepe sıcaklığı, termokuplta ölçülen tepe ve witness cone bükülmesi ayrı olgulardır. Birini diğerinden kesin türetmeyiz. Kaynak: [Orton Pyrometric Cones](https://www.ortonceramic.com/pyrometric-cones), [Orton kaynakları](https://www.ortonceramic.com/pyrometric-cones-resources).

Orton'un tablolarını ürün içinde yeniden dağıtma hakkı ve chart sürümü henüz doğrulanmadı. M4'te kullanıcı cone ve sıcaklığı ayrı girebilir; conversion lookup etkin değildir. Ara değer interpolasyonu, soak düzeltmesi ve heatwork modeli ayrı doğrulama gerektirir.

## Plan

`FiringSegment`: başlangıç/target temperature, °C/h magnitude, direction, HOLD duration minutes veya NATURAL_COOL.

RAMP duration hours = |T_end-T_start| / positive_rate. HOLD doğrudan süre. Isı artışı/azalışı hedefler üzerinden doğrulanır. Rate 0 geçersizdir; negatif oran sessiz abs() ile düzeltilmez. Başlangıçta oda sıcaklığı verilmemişse 20°C gözlenmiş gibi eklenmez.

Doğal soğuma süresi bilinmiyorsa toplam gerçek program süresi AVAILABLE değildir; planın hesaplanabilir kısmı PARTIAL gösterilir. Programın hesaplanan süresi fırının gerçekten ulaşacağı süre değildir.

Doğrulama vakası F-01: 20 -> 600°C, 100°C/h = 5.8h; 600 -> 1000°C, 150°C/h = 2.666666...h; 1000 -> 1220°C, 80°C/h = 2.75h; hold 20 min = 0.333333...h. Planlı ısıtma+hold toplamı 11.55h = 693min = 11h33min. Natural cooling eklenirse bu, toplam çevrim süresi değildir.

## Gerçek pişirim

FiringSample: elapsed_seconds, sensor_id, location, temperature_C, optional atmosphere measurement, kaynak ve kalibrasyon. Eksik zaman bölümleri gizlenmez. Original log korunur; sensör spike temizliği varsa dönüşüm kaydı ve ham görünüme erişim vardır.

Atmosfer etiketi `OXIDATION/REDUCTION/...` kullanıcı raporu olabilir; oksijen ölçümü farklı Observation'dır. Atmosfer tüm run boyunca sabit varsayılmaz. Atmosferden kesin FeO/Fe2O3 oranı üretilmez.

Sıcaklık-zaman eğrisi alanını evrensel heatwork ölçüsü saymayız. Grafik için plan ve actual farklı çizgiler/etiketlerdir. Tepe sıcaklığı doğrulaması cihaz/pilot kapsamına bağlıdır; negatif °C genel olarak fiziksel imkânsız diye reddedilmez. Mutlak sıfır altı, sonlu olmayan veya birimi belirsiz değer hard error; fırın rating'ini aşan plan ayrı context warning/validation konusudur.

## M6 numune bağlamı

Bünye ve lot, biscuit firing, kuruma, kuru uygulama kalınlığı veya kat sayısı, kiln position, soğuma ve değerlendirme tarihi. Kalınlık ölçülmemişse kat sayısından kesin mm türetilmez. Bir firing run çok numune içerebilir; bu numuneler istatistiksel açıdan otomatik bağımsız sayılmaz.
