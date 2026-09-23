# Sır–çamur sonuç göstergeleri: ilk hesap paketi

Bu paket ürün amacına doğrudan bağlı beş ayrı sonuç üretir. Birleşik fırın
simülasyonu değildir. Reçeteden eksik fiziksel özellik türetmez. Gerekli özellik
veya ölçüm yoksa ilgili bölüm UNAVAILABLE döner; başarı olasılığı null kalır.

## Gerçekleşen geliştirme

- Bağımsız motor: `research/process/outcomes.py`.
- Yerel API: `POST /api/v1/outcomes/assess`.
- Tekrarlanabilir, açıkça sentetik örnek girdiler ve üç senaryo çıktısı.
- 14 yeni çekirdek testi ve 4 yeni API testi.
- Tam çekirdek test paketi: 230 test geçti. API: 14 test geçti.
- OpenAPI ve üretilmiş TypeScript sözleşmesi güncellendi; TypeScript kontrolü geçti.
- Kalıcı kayıt, ticari ürün analizi, tarayıcı formu veya fiziksel doğrulama eklenmedi.

## Hangi soruya ne cevap verir?

| Soru | Girdi | Çıktı | Sınır |
|---|---|---|---|
| Soğumada sır ile bünye farklı mı küçülmek istiyor? | Aynı soğuma aralığında ortalama doğrusal CTE çiftleri | Serbest büzülme farkı, mikrogerinim; nominal çekme/basma yönü | Gerilme, çatlama yüzdesi veya güvenli eşik değil |
| Tabaka kalınlaşınca akış nasıl değişebilir? | Ölçülmüş/raporlanmış viskozite ve yoğunluk, sıcaklık, kalınlık, eğim, süre | İdeal film ortalama hızı ve hareket mesafesi | Akıntı cephesinin gerçek ilerlemesi veya raf üzerine damlama tahmini değil |
| Eriyik yüzeyi ıslatmaya ne kadar yatkın? | Aynı koşulda denge temas açısı ve yüzey gerilimi | İdeal tersinir yapışma işi, J/m² | Pişmiş sırın kopma dayanımı veya tutunma yüzdesi değil |
| Numune su alıyor mu, açık gözenekliliği ne? | Kuru, doygun ve sıvıda askıda kütle | Kütlece su emme ve hacimce görünür açık porozite | Sır tabakasını, kapalı gözenekleri ve pinhole sayısını ayırmaz |
| Yüzey ne kadar parlak ölçülmüş? | Aynı ölçüm açısında cihaz okumaları | GU ortalaması ve örnek standart sapması | Reçeteden mat/parlak tahmini değil; GU yüzde değildir |

## Çalıştırılmış örnekler — tamamı SENTETİK

Bunlar gerçek bir stoneware veya sır ürününe ait değildir.

1. Aynı 20–500 °C aralığında bünye CTE=6e-6/K, sır CTE=8e-6/K:
   fark **960 mikrogerinim**. İdeal bağlı tabakada sırın çekme yönünde zorlanma
   eğilimi vardır. Bu, kesin crazing veya çatlama olasılığı değildir.
2. Varsayımsal 1200 °C sabit sıcaklıkta yoğunluk 2500 kg/m³, viskozite
   1000 Pa·s, dik yüzeyde 0,5 mm film ve 600 saniye:
   ortalama ideal sıvı hareketi **1,2258 mm**.
3. Yalnız kalınlık 1 mm olursa **4,9033 mm**; viskoziteyi iki katına çıkarmak
   ilk senaryoyu **0,6129 mm** yapar. Bu hesap, kalınlık etkisini karşılaştırmak
   içindir; gerçek sırın kenarının bu mesafe ilerleyeceği anlamına gelmez.
4. Temas açısı 60°, yüzey gerilimi 0,3 N/m: ideal yapışma işi **0,45 J/m²**.
5. Kuru/doygun/askıda kütle 100/102/60 g: **%2 su emme**, **%4,7619 açık porozite**.
6. 60° cihaz okumaları 28/30/32 GU: **30 GU ortalama**, **2 GU standart sapma**.

## Formüller ve varsayımlar

`mismatch = (alpha_glaze-alpha_body)*(T_high-T_low)`.
Sıcaklıklar aynı aralıkta, aynı soğuma durumu için olmalıdır. İşaret yorumunda
bağlı sır ve daha kalın kısıtlayıcı bünye varsayılır. Viskoelastik gevşeme,
faz dönüşümü, kalınlık, eğrilik ve sıcaklık gradyanı hesaba katılmaz. Isıtma
CTE'sini veya oda sıcaklığı katsayısını sessizce tüm soğumaya yayma.

`mean_velocity = rho*g*sin(theta)*h²/(3*eta)`; `mean_travel = mean_velocity*time`.
Sonsuz düzlem, Newtonyen ve tamamen erimiş film, sabit sıcaklık/kalınlık,
kaymayan taban ve gerilmesiz serbest yüzey varsayılır. Eğim yataydan ölçülür.
Muhafazakâr kapsam kapısı `Re=rho*u*h/eta <= 1`; bu deneysel geçerlilik
sertifikası değildir. Kristal, kabarcık, kapiler kenar ve bünye emmesi yoktur.

`W = gamma*(1+cos(theta))` (Young–Dupré). Aynı sıcaklık ve atmosfer,
denge temas açısı, ideal düz homojen ve reaksiyonsuz yüzey gerekir. Gerçek
pürüzlü/gözenekli/reaktif bünye bu koşulları ihlal edebilir. Oda sıcaklığındaki
su damlası ölçümünü yüksek sıcaklık sır eriyiği ölçümü sayma.

`absorption = 100*(saturated-dry)/dry`;
`open_porosity = 100*(saturated-dry)/(saturated-suspended)`.
Uyumlu doygunlaştırma ve sıvı koşulları gerekir. Tam ASTM prosedürü uygulanmış
olduğu iddia edilmez. Sırlı tüm numune ölçümü, sır porozitesini tek başına vermez.

## Bilgi türü ve sözleşme

Fit/flow/wetting: PREDICTED / DETERMINISTIC, kısıtlı model göstergesi.
Porosity/gloss: CALCULATED / DETERMINISTIC, sağlanan ölçümlerden türetilir.
Her bölüm ayrıca input_kind=MEASURED/REPORTED/SYNTHETIC taşır; kullanıcı beyanı
otomatik doğrulanmış kaynak sayılmaz. source_ref ve conditions zorunludur.
Belirsizlik bilinmiyorsa null; tüm sonuçlarda olasılık null.
Girdi snapshot'ı, motor sürümü, kaynak ve SHA-256 yeniden üretime bağlanır.

API girdisi için `data/fixtures/outcome-indicators-synthetic.json` örneğini
kullan. Bölümler isteğe bağlıdır; gönderilen bir bölümün alanları eksiksiz
olmalıdır. Yanlış birim/tür, eksik kaynak, reddedilmiş model varsayımı ve
bilinmeyen alan 422 döndürür. Eksik bölüm UNAVAILABLE döndürür.

```powershell
& .\storage\simulation\00_environment\Scripts\python.exe -X utf8 scripts/run_outcome_examples.py
& .\storage\simulation\00_environment\Scripts\python.exe -X utf8 -m unittest discover -s tests
& .\storage\prototype\environment\Scripts\python.exe -X utf8 -m unittest discover -s apps/api/tests
```

## Kaynaklar ve kalan doğrulama

Kaynaklar yöntem araştırması içindir; makale/dataset kopyalanmadı veya eğitim
havuzuna katılmadı. Erişim, yeniden dağıtım izni değildir.

- Seramik sır uyumu ve gerilme sınırları, birincil araştırma:
  https://www.sciencedirect.com/science/article/pii/S0921509307003656
- Genleşme/uyum için bağımsız teknik açıklama:
  https://digitalfire.com/glossary/glaze%2Bfit
- Akış formülünün ders kaynağı:
  https://eng.libretexts.org/Bookshelves/Chemical_Engineering/Chemical_Engineering_Separations%3A_A_Handbook_for_Students_%28Lamm_and_Jarboe%29/01%3A_Chapters/1.02%3A_Mass_Transfer_in_Gas-liquid_Systems
- Young–Dupré, ölçüm cihazı üreticisi:
  https://pceu.kruss-scientific.com/en/know-how/glossary/adhesion
- Su emme/porozite standardının resmî kapsamı:
  https://store.astm.org/standards/c373
- Tartım formüllerini içeren bağımsız kurumsal yayın:
  https://ntrs.nasa.gov/api/citations/20120013504/downloads/20120013504.pdf
- Parlaklık ölçüm geometrileri, cihaz üreticisi:
  https://www.byk-instruments.com/en-GB/appearance/micro-gloss
- Matlık mekanizmaları ve soğumanın rolü:
  https://digitalfire.com/glossary/130

Akış ve ıslanma modellerinin seramikler üzerinde bağımsız fiziksel doğrulaması
henüz yoktur. Testler formüllerin ve sınırların doğru uygulandığını denetler.
Bu nedenle modeller araştırma göstergesi olarak kalır. Mat/parlak olasılığı,
arayüz dayanımı ve kusur olasılığı için ürün/lot, gerçek pişirim, uygulama
kalınlığı, soğuma ve eşlenmiş deney sonuçları gereklidir. Bir sonraki ürün adımı
bu girdileri arayüzde açık birim ve kaynak alanlarıyla sunmak; gerçek ölçümleri
bulmadan örnek sabitleri ticari ürünlere bağlamamak olmalıdır.
