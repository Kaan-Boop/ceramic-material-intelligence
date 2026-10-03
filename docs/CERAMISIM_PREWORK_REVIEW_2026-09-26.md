# CeramiSim ön çalışma incelemesi — 26 Eylül 2026

## Sonuç

Ön çalışma ürün hedefi açısından yararlı; mevcut haliyle bilimsel motorun yerine
alınamaz. 3D görünüm, numune etiketi ve deney hafızası fikirleri korunabilir.
Akma, matlık ve çatlama etiketleri doğrulanmış fizik/ML çıktıları değildir.
Sunulan belge bir inceleme girdisidir; içindeki mimari talimatlar otomatik kabul
edilmedi. Next.js/FastAPI/Python ayrımı değiştirilmedi.

İncelenen kullanıcı eki: `Yapıştırılan metin.txt`, 675 satır.
SHA-256: `de12538ce10b5aecc23ebf3918fbbab19c54dc67afdd186b984163c7c770529c`.
Satır numaraları bu ek içindir, proje kaynak dosyalarının satırları değildir.
Kod çalıştırılmadan okundu; tarayıcıda çalışır veya 60 FPS olduğu doğrulanmadı.

## Bu çalışma paketinin kapsamı

- Ne: Kod/bilim/lisans incelemesi ve mevcut veri kabul denetleyicisini kullanan
  dar kapsamlı ek inceleme adaptörü.
- Neden: Görselleştirme fikrini korurken doğrulanmamış kimyayı üretim verisine
  dönüştürmemek; eksik bilimsel girdileri görünür kılmak.
- Sistem etkisi: Üretim kataloğu, UI, API sözleşmesi ve fizik denklemleri değişmedi.
- Dosyalar: `research/prework_review.py`, `tests/test_prework_review.py`,
  `data/manifests/ceramisim-prework-review-2026-09-26.json`, bu rapor ve çözücü raporu.
- Bağımlılık: Yalnızca Python standart kütüphanesi ve mevcut yerel intake validator.
- Beklenen çıktı: Tekrarlanabilir inceleme, kaynak izleri, entegrasyon kabul kapıları.

## Lisans fikrinin düzeltilmesi

Belgenin 24. satırındaki, NC veriden öğrenilen ağırlıkların kendiliğinden tamamen
serbest ticari ürün olduğu iddiası kabul edilmedi. Eğitim de veri kullanımıdır;
ham verinin sonradan silinmesi, önceden yapılan işlemleri kendiliğinden izinli hale
getirmez. Modelin ezberlemesi de ayrı değerlendirme gerektirir. Bunun bütün model
ağırlıklarının her hukuk düzeninde türev eser olduğu anlamına geldiği de söylenemez.
İstisnalar, ülke ve kullanım şekli önemlidir; bu rapor hukuki görüş değildir.

[Creative Commons'ın resmi açıklaması](https://creativecommons.org/using-cc-licensed-works-for-ai-training-2/)
hem ihtiyatlı lisans uyumu yaklaşımını hem yasal istisnalarla ilgili ayrımı açıklar.
[Glazy'nin yayımladığı politika](https://help.glazy.org/about/data-use-policy)
ticari model eğitimi/testi için ayrı izin öngörür ve web arayüzünden izinsiz toplu
kazımayı yasaklar. Bu proje böyle bir izin edinmiş değildir.

Uygulanacak ayrım:

| Kullanım | Proje kararı |
| --- | --- |
| Erişimi izinli yayını okuyup yöntem ve sınırlılıklarını değerlendirmek | Kaynaklı araştırma notu; kod/metin kopyalama lisansı ayrıca incelenir |
| Bilimsel denklemi kendi kodumuzla uygulamak | Formülün bilimsel alanı, patent ve ilgili kullanım koşulları gerektiğinde incelenir; test yapılır |
| Kaynaktan kod/veri/şekil aktarmak | İlgili eserin lisansı; kod lisansı veri lisansı yerine geçmez |
| Eğitim, fine-tuning, distillation veya RAG | Kaynak ve amaç bazında izin; ham veri yayınlamamak tek başına yeterli değildir |
| Kullanıcının kendi fiziksel deneyleri | Kaynak/mahremiyet ve eğitim onayı ayrı; özel reçete otomatik eğitim verisi değildir |
| Belirsiz haklı kaynak | Araştırma adayı; production/training setine kabul edilmez |

Eğitim ileride eklendiğinde kaynak manifesti, izin kararı, dataset snapshot'ı ve
model sürümü birlikte tutulacak. Ham verisiz dağıtım boyut/mahremiyet açısından
yararlı olabilir; lisans kontrolünün alternatifi değildir. Kısıtlı model çıktısından
başka model eğitmek de otomatik bir hak temizleme yöntemi olarak kullanılmayacak.

## Kullanılacak fikirler ve kabul kapıları

| Fikir | Karar | Entegrasyon için gerekli değişiklik |
| --- | --- | --- |
| Döndürülebilir 3D form | Uygun, sonraki UI işi | “Görsel önizleme” etiketi; renderer motor değildir |
| Yerel eğim/yükseklik katmanı | Uygun geometrik hesap | Mesh birimi ve dünya koordinatları; termal risk diye adlandırılmaz |
| Reçete miktarı slider'ı | Uygun | Mevcut Python motoruna senaryo isteği; normalize/base/ilave ayrımı; eski cevap iptali |
| QR numune etiketi | Uygun | Aynı kalıcı specimen UUID, recipe revision, firing context; gizli veriyi QR'a dökmeme |
| Başarısız deneyleri saklama | Uygun | Otomatik silme yok; gözlenmedi/değerlendirilmedi ayrımı; kontrollü silme politikası |
| Matlık/akma/çatlama sayıları | Bu haliyle uygun değil | Kaynaklı yöntem, birim, geçerlilik alanı ve gerçek deney karşılaştırması |
| NC veriyle ticari ağırlık üretme güvencesi | Uygun değil | Kaynak/amaç özelinde hak incelemesi |
| Tamamen tarayıcı motoruna geçiş | Onaylanmadı | Büyük mimari değişiklik; Python hesabını JS'te yeniden yazmayacağız |

## Bilimsel sorunlar

1. **Stull tek oranlı bir mat/parlak sınıflandırıcı değildir.** Ek satır 63–67 ve
   372–383'teki 5/7,5 eşikleri bu kullanım için doğrulanmadı. Stull referansı iki
   UMF koordinatına dayanır; özgün deney kapsamı cone 11 ve belirli flux dengesidir.
   Cone 6'da genel sonuç garantisi değildir.
   [Glazy'nin Stull kapsam açıklaması](https://help.glazy.org/guide/recipes).
2. **CTE modelinin kaynağı, bileşim bazı ve birimi eksik.** Metinde `10^-7` var,
   uygulamadaki 346. satırda yok. Bünye verisi olmadan tek bir 7,5 eşiğiyle “uyumlu”
   veya “çatlama riski yüksek” denemez. Mevcut motorun aynı sıcaklık aralığındaki
   ölçülmüş/raporlanmış CTE karşılaştırması korunmalı; bu da çatlama olasılığı değildir.
3. **Akma formülü ince film çözücüsü değil.** Satır 351–353'te viskozite, yoğunluk,
   zaman, kapillarite ve kütle dengesi bulunmuyor; 2,2 çarpanı ve mm birimi
   doğrulanmadı. Mevcut ideal film hesabı bile sabit sıcaklık/viskozite varsayar ve
   ortalama sıvı hareketini verir; gerçek sır kenarının ilerlemesi değildir.
4. **Renk/roughness önizlemesi ölçüm değildir.** Satır 372–406'daki eşleme bir
   tasarım tercihi. Normal, eğim veya yüksekliğe verilen renk, FEM sıcaklık/gerilme
   sonucu olarak gösterilemez.
5. **Eksik kimya sıfır yapılamaz.** Yedi oksitli tablo B2O3, Li2O, SrO, BaO ve
   renklendiricileri kapsamaz. 337. satırdaki sıfır varsayımı genişletmede sessiz hata
   yaratır. 364. satırda MgO ile ZnO toplanıp MgO başlığı altında gösteriliyor.
6. **Cone tek bir sıcaklık değildir.** Cone hedefi ile tepe sıcaklığı ayrılmalı;
   QR'daki sabit cone 6 seçilen koşullarla eşleşmiyor.
   [Orton'un cone açıklaması](https://www.ortonceramic.com/pyrometric-cones).
7. **Toplam 100 olmayan oranlar:** Tüm bileşenlerin ortak ölçeklenmesi UMF'yi
   değiştirmez; dolayısıyla her >100 toplam yanlış UMF demek değildir. Ancak UI'ın
   yüzde etiketi, batch kütlesi ve base/ilave politikası açık olmalı.
8. **GRD viskozite kapsamı:** Kaynak doğal magmatik silikat eriyikleri için
   kalibre edilmiştir. B2O3/ZnO gibi bileşenleri kapsamayan modeli her sırda
   kullanamayız. İzinli katsayı/veri ve kapsam denetimi ayrıca gerekir.
   [Model yazarlarının UBC sayfası](https://www.eoas.ubc.ca/~krussell/VISCOSITY/grdViscosity.html).

Önceki mesajdaki sekiz satırlık regresyon/logistic model bu yeni HTML tarafından
çağrılmıyor. Sekiz örnek, yedi özellik ve intercept; ayrıca KNaO+CaO=1 bağımlılığı
ve iki pozitif sınıf örneğiyle güvenilir kusur olasılığı kanıtlanamaz. Veri kaynağı,
ölçüm birimleri, bağımsız test ve kalibrasyon yoktur. Eğitim akışı demosu olabilir;
fiziksel sonuç tahmin servisi değildir. Bu turda o eski eğitim kodu çalıştırılmadı.

## Yazılım incelemesi — entegrasyondan önce düzeltilmeli

| Öncelik | Ek satırları | Bulgular |
| --- | --- | --- |
| P1 | 98–102 | Script adresleri HTML URL yerine Markdown bağlantısı; bağımlılıklar yüklenmez |
| P1 | 343–403 | Boş reçete sıfır UMF, mat, 0,5 mm akma, güvenli ve uyumlu sonucuna düşüyor; UNAVAILABLE gerekir |
| P1 | 629–632 | On birinci kayıtta en eski deney `pop()` ile sessiz siliniyor |
| P1 | 585–594, 617–623 | QR ve kayıt ayrı ID üretir; dört haneli zaman kimliği çakışabilir |
| P1 | 620–627, 650–664 | Kalınlık saklanmaz; kaydedilen sıcaklık geri yüklenmez; deney replay mümkün değil |
| P1 | 562–578 | Çok parçalı OBJ importunda her mesh önceki mesh'i kaldırır; formun parçaları kaybolabilir |
| P2 | 499–504, 565–570 | Ham koordinatla renk hesabı, görüntü ölçeklendirmesiyle tutarsız; dosya birimine bağlı görünüm |
| P2 | 234–235, 360–407 | Sabit düşük risk uyarısı diğer değişken sonuçlarla çelişebilir |
| P2 | 147–150, 591 | QR seçilen cone yerine cone 6 yazar |

Yalnız URL biçimini düzeltmek sayfayı doğrulanmış ürün yapmaz. CDN bağımlılığı
çevrimdışı çift tıklama iddiasını da sınırlar. İleride localStorage/import içeriği
DOM'a taşınırken HTML birleştirme yerine güvenli metin aktarımı gerekir; bu inceleme
uzaktan sömürülebilir bir güvenlik açığını kanıtlamış değildir.

## Malzeme incelemesi: 6 aday, 0 katalog kabulü

`research.prework_review` eki çalıştırmadan dar bir literal ayrıştırıcıyla okur.
Desteklenmeyen ifade, çift anahtar veya sonsuz değer işlemi durdurur. Mevcut
`pipelines.ingestion.materials.validate_record` üzerinden kalite/izin sorunlarını
raporlar. Ham eki değiştirmez ve normalize ürün analizi üretmez.

| Malzeme anahtarı | Bildirilen oksit toplamı | Karar |
| --- | ---: | --- |
| potash_feldspar | 99,5 | İnceleme bekliyor |
| kaolin | 86,0 | İnceleme bekliyor |
| silica | 99,9 | İnceleme bekliyor |
| whiting | 56,1 | İnceleme bekliyor |
| talc | 93,5 | İnceleme bekliyor |
| zinc_oxide | 99,5 | İnceleme bekliyor |

Eksik kısım LOI değildir; LOI ve analiz bazı bilinmiyor. Yazılmış sıfırlar yalnızca
ekteki iddia olarak korunur. EPK gibi ürün çağrıştıran ad doğrulanmış üretici analizi
yerine geçmez. Tüm adaylarda kaynak, analiz sürümü/tarihi, kapsam ve kullanım izni
incelemesi gereklidir. “Leach 4321” adıyla sunulan 40/20/20/20 preset de adla
eşleşmiyor; sessiz düzeltme yerine kaynakla yeniden tanımlanmalı.

## Önerilen sonraki entegrasyon

Mevcut mimari korunarak tek çalışma ekranına ilerleyelim:

1. **Hesap paneli:** Gerçek API raporu, birim, kaynak, kapsam ve eksik girdiler.
2. **Form paneli:** 3D geometri/kalınlık yerleşimi. Örnek görünüm ile hesaplanan
   alanlar ayrı seçilir. Sayısal alan yalnız gerçek motorun eşleşen mesh çıktısıyla.
3. **Deney paneli:** Aynı specimen kimliğine bağlı recipe revision, analysis run,
   application/firing, fotoğraf ve ölçüm; QR yalnız bu kimliği taşır.

Önce numune kaydı/replay ve API çıktıları; sonra 3D görselleştirme. Akışkan sırın
form üzerinde göllenmesi için ayrı muhafazakâr model, mesh/kalınlık/birim kontrolleri,
viskozite(T), sınır koşulları ve gerçek akma testi gerekir. Aktif öğrenme ancak
izinli deney seti ve baseline sonrasında değerlendirilir. Tek başarısız deney
kimyasal bölgeyi kalıcı olarak yasaklamaz. “%50 daha az deney” henüz hipotezdir.

## Doğrulama ve kalan işler

- Başlangıç kontrolü: 230 çekirdek/araştırma testi ve 14 API testi geçti.
- Yeni review adaptörü: 8 test geçti; 6 aday karantinada, 0 kabul, 0 sayısal red.
- Son toplu tekrar: 238 çekirdek/araştırma testi geçti; API paketindeki 14 test de geçti.
- Bağımsız kod incelemesinde bulunan kayan nokta sınır yuvarlaması/taşması için
  tam ondalık sınır denetimi ve orijinal sayı metni saklama eklendi. Çok küçük
  temsil edilemeyen değerler kontrollü durur; reddedilen yüzdelerden toplam üretilmez.
- Ayrı raporda 14 arşiv dosyasının boyutu/SHA-256'sı yeniden doğrulandı.
- API ortamında Starlette/httpx kullanımdan kaldırma uyarısı var; testler geçti.
  Bağımlılık geçişi bu incelemede yapılmadı.
- Browser/E2E, gerçek cihaz, fiziksel fırın deneyi, model eğitimi ve 3D entegrasyonu
  bu turda yapılmadı. Yazılım testleri malzeme davranışını deneysel olarak doğrulamaz.
- Ekteki Kaggle dosya kapsamları/lisansları ve iddia edilen tam dataset sayıları
  bu turda doğrulanmadı. “Tüm kaynaklar doğrulanmıştır” ifadesi benimsenmedi.

Teknik borç: inceleme adaptörü yalnız bu biçimdeki düz material literalini destekler;
genel JS parser değildir. Ticari referans kimyası, model kalibrasyonu, kalıcı deney
kaydı ve üretim kalitesinde 3D rapor bağlama halen ayrı geliştirme işleridir.
