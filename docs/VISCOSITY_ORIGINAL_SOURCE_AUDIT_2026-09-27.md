# Viskozite: özgün kaynak ve bağımsızlık incelemesi

Sonraki erişim kontrolü: [düzeltme yayını DOI'si doğrulandı](VISCOSITY_ERRATUM_ACCESS_2026-09-27.md); tam metin edinilemedi. Aşağıdaki tarihsel DOI-adayı belirsizliği yeni kayıtta kapandı; 44 satırın bilimsel beklemesi değişmedi.

27 Eylül 2026. Bu teslim bibliyografik/yöntem incelemesidir; özgün deneylerin tamamının satır satır doğrulandığı anlamına gelmez.

## Karar

S3/S4 sayısallaştırması izlenebilir bir araştırma kaydı olarak korunuyor. **Bağımsız model doğrulama seti olarak onaylanmadı.** Beş deney yayını ve iki model yayını eşleştirildi. Tarih ve ortak yazarlar tek başına eğitim/kalibrasyon örtüşmesinin kanıtı sayılmadı. Örtüşme için özgün model veri listesiyle numune-bileşim-sıcaklık-değer eşleşmesi gerekiyor.

[Makine tarafından okunabilir inceleme kaydı](../data/manifests/viscosity-original-source-audit-2026-09-27.json), [önceki sayısal teslim](VISCOSITY_TABLE_TRANSCRIPTION_2026-09-27.md).

## Deney kaynakları

Numune bağlantıları arşivlenmiş Conte 2018 kaynakçası ve S3/S4'ten gelir. Aşağıdaki koşullar yayının genel kapsamıdır; S4'teki her satıra otomatik atanmaz.

| Ref. | Yayın / numuneler | Doğrulanan yöntem bağlamı | Açık kalan |
|---|---|---|---|
| 32 | Giordano, Dingwell, Romano (2000), *Viscosity of a Teide phonolite in the welding interval*; G.2000, 22 satır | Doğal fonolit; kuru ve hidratlanmış örnekler, eşmerkezli silindir ve mikropenetrasyon. Viskozite ölçümü ile yüksek basınçlı örnek hazırlama ayrı işlemler. [Roma Tre](https://iris.uniroma3.it/handle/11590/157552) | Özgün tablo/satır ve kalibrasyon üyeliği |
| 33 | Giordano, Romano, Papale, Dingwell (2004), *The viscosity of trachytes, and comparison with basalts, phonolites, and rhyolites*; IGC/MNV, 36 satır | Doğal trakitlerin kuru ve su içeren viskozitesi; bileşime özel VFT ilişkileri. [Yayıncı](https://www.sciencedirect.com/science/article/abs/pii/S0009254104003304), [Torino kaydı](https://iris.unito.it/handle/2318/97373) | Tam tablo ve seçilen kuru alt kümenin eşleşmesi |
| 34 | Giordano ve diğerleri (2006), *An expanded non-Arrhenian model for silicate melt viscosity*; MST/CI_OF/MDV, 58 satır | Yeni anhidrat ölçümler ile eski verilerden model yeniden kalibrasyonu. [Torino kaydı](https://iris.unito.it/handle/2318/96450?mode=complete) | 2008 modelinin kalibrasyon listesiyle satır düzeyi eşleşme |
| 35 | Romano ve diğerleri (2003), *The dry and hydrous viscosities of alkaline melts from Vesuvius and Phlegrean Fields*; AMS-B1/AMS-D1, 25 satır | Kuru ve su içeren ergiyikler; mikropenetrasyon/silindir, yaklaşık 400-1500 °C genel çalışma kapsamı. Örnek hidratlama basıncı ölçüm basıncı sanılmamalı. [Roma Tre](https://iris.uniroma3.it/handle/11590/146434) | Her satırın özgün numune ve su içeriği bağlantısı |
| 36 | Whittington, Richet, Linard, Holtz (2001), *The viscosity of hydrous phonolites and trachytes*; Trachyte/Phonolite, 44 satır | Sentetik, demirsiz ergiyikler; kuru ve su içeren deneyler. Yayıncı ilişkili bir 2004 düzeltmesini listeliyor. [Yayıncı](https://www.sciencedirect.com/science/article/abs/pii/S000925410000317X) | Düzeltmenin içeriği/etkisi ve özgün sayılar |

**44 satır yanlış bulundu demiyoruz.** Bu iki numunenin bağlı olduğu yayın için düzeltme bulundu; düzeltmenin veriyi, denklemi veya başka bir alanı değiştirip değiştirmediği henüz okunamadı. Sayısal değerler silinmedi, düzeltilmedi veya sıfırlanmadı. Düzeltme adı: *Erratum to “The viscosity of hydrous phonolites and trachytes”*, Chemical Geology 211 (2004), 391. DOI adayı `10.1016/j.chemgeo.2004.01.002` ikincil indekslerde bulundu; DOI açılışı başarısız olduğundan birincil doğrulama tamamlanmış sayılmadı.

## Model kaynakları ve sınırlar

### Ref. 19: Giordano-Russell-Dingwell, 2008

[Yayıncı](https://www.sciencedirect.com/science/article/pii/S0012821X08002240), [yazarın UBC sayfası](https://www.eoas.ubc.ca/~krussell/VISCOSITY/grdViscosity.html), [UBC makale kopyası](https://www.eoas.ubc.ca/~krussell/VISCOSITY/grdViscosity_files/grdViscosityPaper.pdf).

Makalenin §2 bölümü 1774 kalibrasyon ölçümü; Ek A ise 257 ayrı kontrol ölçümü bildiriyor. Bu iki grubu birbirine veya bizim 185 satıra eşitlemiyoruz. Ek B'deki destek verisi bu turda edinilemedi; kalibrasyon üyeliği **UNKNOWN** kaldı. Formül doğal silikat ergiyiklerine yönelik ampirik modeldir. B2O3 ve ZnO gibi sır için önemli bazı bileşenler tanımlı bileşen kümesinde yoktur; bunları sessizce silip sonucu sır tahmini olarak sunamayız.

UBC arayüzü ağırlık yüzdesi giriş alır; modelin bileşim terimleri mol yüzdesi kullanır. Arayüzün giriş kabul sınırları ile makaledeki kalibrasyon alanı aynı değildir. Bunların hiçbiri S3'ün bütün birim/baz belirsizliğini kendiliğinden çözmez.

### Ref. 17: Fluegel, 2007

[Yazarın makalesi](https://glassproperties.com/viscosity/Viscosity_2006_AFluegel.pdf), *Glass viscosity calculation based on a global statistical modelling approach*, Glass Technology 48, 13-30.

Model SciGlass kaynaklı geniş bir derlemeye dayanır. İncelenen metin, kaynak veri ve referansların SciGlass'ta bulunduğunu belirtir (§2). Makalenin erişilebilir olması veri tabanının yeniden dağıtım/training izni değildir. S3/S4 ile tam örtüşme dışlanamadı; sonuç **UNKNOWN**, bağımsızlık onayı yok. Bu turda SciGlass verisi, hesaplayıcı kodu veya katsayılar sisteme alınmadı.

## Birim ve demir gösterimi: yeni kontrol adayı

[2006 yazar kopyasının](https://www.eoas.ubc.ca/~krussell/epapers/cg_getal06.pdf) Tablo 1 metni bileşimleri `wt.% oxides`, demiri `FeOtot` olarak tanımlar. MST ve CI_OF için S3'teki yuvarlatılmış değerlere benzeyen kayıtlar bulunuyor. Bu, kaynağa özel bir eşleştirme adayıdır; bütün S3'e toplu baz atamak için kullanılmadı. **FeOtot, yalnızca ölçülmüş Fe(II) demek değildir.** Görsel tablo ve bütün oksitler doğrulanmadan eski `FeO` alanı yeniden yorumlanmayacak. Ham transkripsiyon değişmedi.

## Erişim, lisans ve inceleme sınırı

Agent Reach arama aracı bulunmadığı için mevcut web araması kullanıldı. Araştırma kurumu, yayıncı ve yazar sayfaları esas alındı; sosyal platformlar bilimsel dayanak yapılmadı. Bazı yayıncı açılışları 403/erişim hatası verdi; erişim engeli aşılmadı. UBC/yazar PDF'lerinin metni taranabildi ancak istenen sayfa görüntülerinin bir kısmı alınamadı. Bu nedenle tam görsel PDF doğrulaması veya hücre kabulü ilan edilmedi.

Yeni tam metin dosyası, ek veri veya lisanslı veri tabanı indirilmedi. Bu kayıtta yalnızca bibliyografik bilgiler, kısa özgün araştırma notları ve kaynak bağlantıları saklandı. Okunabilir bir makale, açık lisanslı dataset olarak işaretlenmedi. Tüm yeni kaynakların veri yeniden kullanımı için lisansı/hakları ayrıca incelenecek; varsayılan ticari kullanım ve eğitim izni `UNKNOWN`.

Araştırma aracı sürüm kontrolü de yerel erişim hatasıyla çalışmadı; araç kurulumu/güncellemesi yapılmadı.

## Somut sonraki kapılar

1. Ref. 36 düzeltmesinin yasal tam metnini edin ve 44 satıra etkisini belirle. Birincil metin olmadan düzeltme uydurma.
2. GRD 2008 destek verisinde kalibrasyon/kontrol üyeliğini eşleştir. Bulunamazsa S4'ü yalnızca regresyon/uygulama karşılaştırması olarak tut; dış doğrulama diye sunma.
3. Özgün kimya tablolarını görsel doğrula; wt%, toplam demir gösterimi, analiz bazı, su ve yuvarlama farklarını sürümlü türev kayda geçir.

Fizik motoru, katsayılar ve sayısal staging verisi bu teslimde değişmedi. Yeni başarı yüzdesi veya hata metriği üretilmedi.
