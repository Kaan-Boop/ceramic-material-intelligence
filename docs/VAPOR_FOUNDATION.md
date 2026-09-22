# Su–buhar araştırma katmanı — 22 Eylül 2026

## Teslim

`research/thermal/vapor.py` sabit sıcaklıkta iyi karışmış bir kontrol hacminin su buharı kütle bilançosunu çözer:

`V dc/dt = s + Q(c_in - c)`

V: m³; Q: aynı koşullarda m³/s; c: kg/m³; s: kg/s. Kaynak hızı numuneden ölçülmüş veya açıkça senaryo olarak verilmiş olmalıdır. Bu, seramik içinden buharlaşmayı hesaplayan bir model değildir. Sabit segmentin analitik çözümü kullanılır; küçük Q için sayısal iptal önlenir. Birden fazla segmentin son konsantrasyonu sonraki segmente aktarılabilir; sıcaklık/hacim değişirken yalnızca konsantrasyonu aktarmak yeterli değildir ve bu sürüm bunu desteklemez.

Kütle bütçesi giriş/çıkış/kaynak/depolamayı ayrı tutar. Sonuç PREDICTED / DETERMINISTIC / IDEALIZED_SCENARIO'dur. Matematik doğrulaması fiziksel kalibrasyon değildir. Doygunluk konsantrasyonu aynı sıcaklıkta dışarıdan, kaynak kaydıyla sağlanır. Başlangıç/giriş aşırı doymuşsa hata; segment içinde doygunluk aşılırsa sonuç UNAVAILABLE olur. Yoğuşma miktarı veya kusur olasılığı uydurulmaz. Sabit katsayılı çözüm monotondur; bu yüzden iki uçta sınır denetimi bu segment için yeterlidir.

Önemli varsayımlar: seyreltik buhar, eşit hacimsel giriş/çıkış, tam karışım, sabit hacim/sıcaklık, ihmal edilebilir kaynak gaz hacmi. Buhar yoğun olduğunda bu yaklaşım geçerli değildir. Gözenek basıncı, kil içi difüzyon, su aktivitesi, latent ısı, gaz reaksiyonu ve fırın güvenliği hesaplanmaz. Modül henüz FEM, web veya reçete LOI hesabıyla otomatik bağlanmadı; LOI'yi buhar hızı olarak kullanmak yanlış olur.

## Çalıştırma ve örnek

`python -m unittest tests.test_vapor -v`

Sentetik senaryo: 1 m³ hacim; 0.01 m³/s hava değişimi; sıfır başlangıç/giriş nemi; 0.00001 kg/s buhar kaynağı; 100 s süre; 0.02 kg/m³ varsayımsal doygunluk sınırı. Son buhar yoğunluğu 0.00063212056 kg/m³, yani 0.63212056 g/m³. Havalandırma olmadan 1 g/m³ olur. Bu bir malzemeye veya sıcaklığa kalibre edilmiş fırın örneği değildir.

## Kullanılabilir kaynak havuzu

| Kaynak | İnceleme ve yerel durum | Hak/kullanım kararı |
|---|---|---|
| [Cantera 3.2 Vapor Dome](https://cantera.org/3.2/examples/python/thermo/vapordome.html) | Su–buhar özellikleri örneği; resmi GitHub'dan License.txt, README.rst, vapordome.py arşivlendi | BSD-3-Clause; bildiriler korunmalı; örnekler çalıştırılmadı, paket kurulmadı |
| [Cantera kaynak kodu](https://github.com/Cantera/cantera) | v3.2.0 etiketi commit 4a8358eb80cfeb50474386b5f9ec0b3a83519889 olarak çözüldü; dosya SHA256 ve tarihler manifest'te | Tam depo indirilmedi; mekanizma/veri dosyalarının hakları ayrıca incelenecek |
| [NIST Water Antoine](https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4&Type=ANTOINE) | Denklem, birimler ve geçerlilik aralıkları incelendi | SRD telif bildirimi var; veri tabanı açık lisanslı varsayılmadı, katsayı seti programa aktarılmadı |
| [Ceramic green bodies drying tezi](https://theses.hal.science/tel-02495750) | Başlık ve arama özeti bulundu; portal erişimi engelli | Tam metin okunmadı/indirilmedi; lisans UNKNOWN; yalnızca araştırma adayı |
| [RILEM kalsinasyon incelemesi](https://doi.org/10.1617/s11527-021-01807-6) | Önceki turda ilgili HTML bölümleri okundu; mineral yapı ve atmosfer bağımlılığı | CC BY 4.0; çimento için kalsine kil kapsamı sır fiziğine otomatik genellenmez |
| [OpenGlaze](https://github.com/KyaniteLabs/openglaze) | Önceki kaynak arşivinde seçilmiş MIT kod; reçete hesaplayıcı adayı | Buhar/kuruma/çok-fazlı fizik motoru değil; bütün uygulamayı bununla değiştirme kararı alınmadı |

Arşiv manifest'i: `data/manifests/vapor-cantera-2026-09-22.json`. Ham dosyalar `storage/vapor/sources/raw/sha256/` altında. Kaynak kod indirmek, bilimsel olarak doğrulandığını veya ürünümüze entegre edildiğini göstermez. Bu tur yeni hesap modülü proje içinde yazıldı; Cantera kaynakları referans arşividir.

## Birleşik motorun gerekli katmanları

1. Nem ve tür envanteri: serbest su, bağlı OH, karbonatlar ayrı; kuru/yaş baz ve kaynak/ölçüm belirsizliği.
2. Ölçümden kaynak terimi: TGA/DSC ile zaman–sıcaklık–kütle; buhar ve CO2 ayrımı için gaz analizi veya mineralojik kanıt. Tek LOI toplamı yeterli değil.
3. Gaz kontrol hacmi: bu teslimde idealize su buharı birikme/uzaklaşma benchmark'ı.
4. Enerji eşleştirmesi: buharlaşma entalpisi, reaksiyon ısısı, taşınım ve ışınım; önce enerji korunumu testleri.
5. Gözenekli katı: nem taşınımı, geçirgenlik, kapiler etki, büzülme; ölçümlü katsayılar ve ağ/zaman yakınsaması.
6. Yüksek sıcaklık: sinterleme, eriyik/katı faz, redoks, viskozite ve gerilme gevşemesi; ayrı malzeme veri modelleri.
7. Belirsizlik: ölçüm belirsizliği ve parametre dağılımlarıyla senaryo yayılımı; fiziksel kusur olasılığı için ayrıca deneysel kalibrasyon.

Sonraki somut teslim önerisi: TGA ölçüm serisi giriş sözleşmesi, baz/birim doğrulaması ve toplam kütle kaybı entegrasyon testi. Ardından izinli, koşulları bilinen bir deney serisini gaz kaynağına bağlamak. Cantera su özellikleri adaptörü ancak izole bağımlılık kurulumu, referans karşılaştırması ve kapsam testinden sonra aktifleşmeli. Yeni bir framework'e veya başka uygulamanın tam fork'una bu tur geçilmedi.
