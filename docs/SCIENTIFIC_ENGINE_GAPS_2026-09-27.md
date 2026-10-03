# Bilimsel motor: mevcut yeterlilik ve eksik bağlantılar

27 Eylül 2026. Kod incelemesi ve yazılım testleri; deneysel validasyon raporu değildir.

## Öncelik

Doğru malzeme → geçerli model → tutarlı bağlantı → simülasyon → araştırma çıktısı.
UI ve deney defteri bu amacı destekler. Yeni bir çözücü kurmak malzeme özelliği
eksikliğini kapatmaz. Bu turda yeni çözücü veya üçüncü taraf dataset kurulmadı.

## İncelenen mevcut hesaplar

| Modül | Gerçekte ürettiği | Henüz üretmediği / eksik bağlantı |
|---|---|---|
| Kimya temeli | Sürümlü atomik kütlelerle formül/oksit temsili | Element tablosundan faz, kinetik, viskozite veya yüzey sonucu |
| outcomes.fit | Aynı aralıktaki ortalama CTE'lerden serbest büzülme farkı | Artık gerilme, çatlama yüzdesi; sıcaklığa bağlı ölçüm ve gevşeme verisi eksik |
| outcomes.flow | Verilmiş viskozite/yoğunlukla ideal sabit film hareketi | Reçeteden viskozite; gerçek sır kenarı ve değişken pişirim altında akma |
| outcomes.wetting | Verilmiş temas açısı/yüzey gerilimiyle ideal arayüz işi | Pişmiş bağ dayanımı; reaksiyonlu/gözenekli bünye arayüzü |
| outcomes.porosity | Tartımlardan su emme ve görünür açık gözeneklilik | Pişirim öncesi gözenek/kabarcık tahmini; kapalı gözenekler |
| outcomes.gloss | Cihaz okumalarının ortalama ve yayılımı | Reçeteden mat/parlak tahmini |
| thermal.drying | İdeal homojen ısınma/kaynama, enerji ve serbest su dengesi | Gözenek içi nem taşınımı, kaynama öncesi kuruma, bağlı su/reaksiyonlar |
| simulation | Analitik referanslarla test edilen ısı ve doğrusal termoelastisite örnekleri | Gerçek sır/bünyenin yüksek sıcaklık davranışının fiziksel doğrulaması |

Bu göstergeler tek başına veya birlikte gerçek bir pişirim sonucunu doğrulamış
sayılmaz. Bir hesap çıktısının diğerine bağlanması için numune/lot, durum, birim,
sıcaklık aralığı, atmosfer ve zaman temelinin uyumlu olması gerekir.
Sır ile bünye oksitlerinin tek bir homojen reçete gibi toplanması arayüz modeli değildir.

## Önceliklendirilmiş eksikler

1. **Reçete → fiziksel özellik bağlantısı:** Kimyasal analizden otomatik viskozite,
   CTE veya temas açısı üreten, bizim bileşimlerimizde doğrulanmış bir model yok.
   Herhangi bir genel katsayıyı tüm sırlara uygulamak yerine model kapsamı ve
   bağımsız ölçüm çiftleri edinilmeli.
2. **Ortak malzeme durumu:** Kuru toz, eriyik ve pişmiş katının özellikleri ayrı.
   Kaynak metni tek başına yeterli değil; özellik kayıtları birim, yöntem,
   sıcaklık/atmosfer, belirsizlik, numune ve lisans kökeni taşımalı.
3. **Zaman bağımlılığı:** Isıtma, erime/çözünme, gaz çıkışı, soğuma ve kristalleşme
   henüz birlikte kalibre edilmiş bir model değil. Denge hesabı reaksiyonun
   ne kadar sürede gerçekleşeceğini kendiliğinden söylemez.
4. **Fiziksel validasyon:** Sayısal testler mevcut; gerçek karşılaştırma için
   aynı koşullu, kullanılmasına izin verilen ölçüm serileri gerekli.
5. **Araştırma çıktısı:** Modelin çalışmadığı alanın, hata ölçütünün ve kullanılan
   girdilerin raporlanması zorunlu; tek genel başarı yüzdesi kullanılmayacak.

## İlk bağlantı için öneri: viskozite ve ideal akış

Bu bir sonraki çalışma paketi önerisidir, tamamlanmış özellik değildir.
Amaç: 'Aynı eriyik için sıcaklık ve kalınlık değişince ideal akış göstergesi nasıl
değişir?' sorusuna ölçüme bağlı yanıt. Gerçek kenar hareketi veya raf akması değildir.

Gerekli kaynak: aynı tanımlı bileşimin birden fazla sıcaklıkta viskozitesi,
birim ve ölçüm yöntemi, uygun yoğunluk verisi, kaynak kullanım izni.
Tercihen seramik sırına uygun borosilikat/alkali-aluminosilikat bileşim;
volkanik eriyik modelini kapsam kontrolü olmadan borlu/çinkolu sırda kullanma.

Teslim sırası:

1. Ölçüm tablosunu ve haklarını doğrula; erişilen makaleyi kullanılabilir veri sayma.
2. Aralık içi özellik interpolasyonunu bağımsız doğrula; aralık dışına sessiz uzatma yok.
3. Özellik kaydını mevcut flow hesabına kaynak kimliğiyle bağla.
4. Sentetik kontrol ve bağımsız ölçüm karşılaştırmasını ayrı raporla.
5. Isıl geçmişe entegrasyonu ancak quasi-steady ve sabit kalınlık varsayımlarını
   açıkça değerlendirdikten sonra ekle; bunu tam akış simülasyonu diye adlandırma.

Kabul ölçütü: kaynak/numune/birim izi korunur; kapsam dışı hesap reddedilir;
analitik sınır durumları geçer; deneysel hata kendi biriminde raporlanır.
Sayısal hata toleransı ve fiziksel kabul eşiği veri/ölçüm yöntemi seçilince
belirlenecek; şu an keyfi yüzde atanmayacak.

## Araç araştırması: doğrudan resmi belgeler

- [Cantera termodinamik modelleri](https://cantera.org/stable/reference/thermo/index.html):
  tür ve faz modeliyle uyumlu katsayı/girdi gerektirir. Mevcut gaz/reaksiyon
  araştırmasına aday; hazır bir evrensel sır modeli değildir.
- [NIST FiPy](https://pages.nist.gov/fipy/en/stable/): sonlu hacim tabanlı
  difüzyon/taşınım ve bağlı PDE çözümü. İleride nem/ısı taşınımı için teknik
  deneme adayı; mevcut FEM'in yanına hemen yeni bağımlılık eklenmedi.
- [pycalphad](https://pycalphad.org/docs/latest/): faz dengesi ve faz özellikleri
  çalışmaları için aday. Uygun oksit sistemi ve veri tabanı kapsamı/lisansı
  seçilmeden sır fazları için sonuç üretmeyecek.

Bu kaynaklar 27 Eylül 2026'da çevrimiçi incelendi. Araçların varlığı, projenin
malzemelerinde deneysel doğruluk veya veri yeniden kullanım izni kanıtı değildir.

## Bu turda yapılan somut değişiklik

- outcomes sürümü 0.2.0: tüm bölümler artık gerekli özellikleri, koşul uyumunu,
  edinilmesi gereken ölçümleri ve hesaplamadığı çıktıyı taşır.
- Eksik bölüm UNAVAILABLE kalır; gereksinim açıklaması sahte sayı üretmez.
- Çok büyük tamsayılar için kontrollü OutcomeInputError; NaN/Infinity sınır testleri.
- Üç yeni test: gereksinim çıktısı, global verinin değişmemesi, uç sayı kontrolü.
- Yerel bilimsel/çekirdek test paketi: 241 test geçti, atlanan test raporlanmadı.
  Bu sayı fiziksel deney doğrulaması değildir.

Sınırlamalar: yeni requirements alanları API çıktısındadır; UI sunumu eklenmedi.
Diğer modüllerdeki sayısal giriş kontrolleri için aynı uç-değer taraması henüz
tamamlanmadı. Alternatif Antigravity projesindeki yarım güvenlik paketi bu turda
değiştirilmedi veya tamamlanmış sayılmadı. Ticari ürün analizlerinin tamamına
yönelik veri kabul denetimi bu kod incelemesinin kapsamı dışında kaldı.
