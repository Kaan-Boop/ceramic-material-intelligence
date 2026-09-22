# Ticari çamur ve sır havuzu — ilk envanter paketi

İnceleme: 22 Eylül 2026. **İş tamamlanmadı:** 60 marka, 100 ek çamur,
100 toz sır ve 1.000 üzeri doğrulanmış kayıt hedefleri halen açık.

## Bu teslim

Ürün kimliği, hammadde reçetesi, oksit analizi ve deney sonucu ayrı sayılır.
İlk paket: 162 benzersiz marka+ürün+tip kimliği; 109 hazır bünye, 20 ham kil,
33 toz sır. Dokuz marka etiketi var; hazır çamur bünyelerinde yedi marka var.
Bu 109 kayıt, talepteki 60 markanın üstüne ek 100 ürün hedefinin tamamlandığı anlamına gelmez.
Yeni kabul edilmiş motor analizi: **0**. Tam ticari hammadde reçetesi: **0**.

| Keşif pazarı | Hazır çamur | Ham kil | Toz sır |
|---|---:|---:|---:|
| Türkiye | 27 | 0 | 24 |
| Avrupa | 54 | 20 | 0 |
| ABD | 28 | 0 | 9 |

Keşif pazarı üretim ülkesi değildir. Türkiye'deki 16 Laguna sır kaydı ithal marka
olarak distribütör kataloğunda bulundu; Türk üretimi diye kaydedilmedi.
Ham kil ürünleri hazır torna/heykel bünyesi sayılmadı. Renk adından pigment bileşimi türetilmedi.
Şirketler, ürün markaları, distribütörler ve paket varyantları ayrı tutulmalı.
Kapsam Avrupa'dır; Birleşik Krallık ürünleri Avrupa Birliği ürünü diye etiketlenmez.

### Dosyalar ve tekrar üretim

- `data/research/commercial-products-seed.json`: incelenmiş sayfalardan ürün kimlikleri.
- `data/research/commercial-products-index.json`: kaynak ve hak alanları eklenmiş araştırma indeksi.
- `data/research/commercial-analysis-candidates.json`: üç sınırlı oksit tablosu transkripsiyonu; karantina.
- `data/manifests/commercial-catalogue-audit-2026-09-22.json`: sayımlar/kalite bayrakları.
- `research/commercial_catalogue.py`: deterministik derleme; hiçbir ağ çağrısı veya kazıma yapmaz.
- `tests/test_commercial_catalogue.py`: tekrar, kimlik, mükerrer, pazar/menşe, SDS ve hak ayrımı testleri.

Çalıştırma: `python -m research.commercial_catalogue` ardından
`python -m unittest discover -s tests`.
Bu tur toplam **196 araştırma testi geçti**; arayüz veya hesap algoritmaları değişmedi.
Veri-kalitesi rehberi, ürün kimliği ile motor girdisini ayrı saymayı ve belirsiz kayıtları
üretime taşımamayı yönlendirdi. Bu nedenle yeni indeks doğrudan kullanıcı malzeme seçicisine eklenmedi.

### Motorun mevcut seviyesi

Web/API prototipi mevcut. Normalizasyon, baz/ilave ayrımı, oksit kütlesi, mol,
UMF ve açıkça tanımlı oranlar hesaplanabiliyor. Ticari ürün analizi yerine teorik
fixture kullanıldığında sonuç da teoriktir. Pişirim bağlamı ve eksik sonuç alanları görünür.
Araştırma modüllerindeki iki katmanlı termoelastisite ve basitleştirilmiş buhar
taşınımı, birleşik ve deneyle doğrulanmış bir fırın simülatörü değildir.
Buhar modeli dışarıdan verilen kaynak terimini kullanır; LOI'den gaz türü üretmez.
Gerçek TGA serisi, su özellikleri, enerji/kütle dengesi ve deney karşılaştırması
henüz tamamlanmış kabul edilemez. Matlık, renk, aderans veya çatlama olasılığı
için kalibre edilmiş bir model yoktur. Bu envanter turu fiziksel yetenek eklemedi.

## Kritik bulgular

1. Crafist 15362044: ürün adı Akçini, kategori Stoneware; sessiz sınıflandırma yapılmadı.
   ESC1 özelliklerini sağladığı beyanı, aynı formül/üretici/lot olduğu anlamına gelmez.
2. G&S 245: sekiz oksit toplamı %100; bu durum analizin kuru mu kızdırılmış mı olduğunu
   kanıtlamaz. LOI, analiz tarihi ve lot belirsiz. PDF metni incelendi; görsel sayfa kontrolü
   web aracının cache hatası nedeniyle tamamlanmadı. Üretim hesabına kabul edilmedi.
3. Sibelco Opal DBX-2: raporlanan oksitler+LOI toplamı %99,45; eksik kısım normalize edilmedi.
4. Sibelco Electromix TA: erişilen tabloda Al2O3 ve Fe2O3 hücreleri ikisi de 25,4 görünüyor;
   oksitler+LOI toplamı %124. Kaynak hatası veya tablo temsil problemi olabilir; üreticiden
   teyit olmadan Fe2O3 değerini tahminle düzeltmedik. `AI2O3` başlık yazımı için yorum açık kaydedildi.
5. Mayco 2020 grup SDS'si dokuz toz ürünü kapsıyor. Tehlikeli bileşenler için üst sınır
   veriyor; geri kalan içerik açıklanmıyor. Bu değerler her ürünün tam oksit analizi değildir.
6. Laguna'nın eski Wix kataloğundan bulunan 28 kimlik güncel katalogla uzlaştırılmalı;
   bugün üretimde/satışta olduğu iddia edilmedi.
7. 162 kaydın kaynak bağlantısı var, fakat yeniden yayım/training/ticari toplu kullanım
   hakları doğrulanmadı. Hepsi araştırma indeksinde; açık veri seti olarak yayımlanmadı.

Tek inceleme tarihi vardır; popülerlik, satış sıralaması veya değişim trendi çıkarılmadı.

## Kaynak kuyruğu: Türkiye → Avrupa → ABD → Asya

İlk sıradaki kaynaklar ürün kimlikleriyle işlendi. Diğerleri keşif/izin incelemesi kuyruğudur;
adı listede bulunması veri tabanının indirildiği veya yirmi markanın doğrulandığı anlamına gelmez.

| Bölge | Kaynak | Durum ve rol |
|---|---|---|
| TR | [Akasya](https://www.akasyaseramik.com/urunler-kategori/camurlar) | 25 bünye kimliği; teknik belgeler ürün bazında açılmalı |
| TR | [Crafist](https://www.crafist.com.tr/toz-sirlar) | Kendi markası ve ithal ürünler ayrı |
| TR | [Refsan](https://www.refsan.com.tr/656-seramik-camuru-vakumlu) | İlk bünye kaydı; kalan katalog incelemesi bekliyor |
| TR | [Esan](https://esan.com.tr/) | Ham madde üreticisi; hazır çamur markası sayılmadı |
| TR | [Hanterra](https://hanterra.com/) | Tedarikçi; menşe/üretici ayrı kontrol edilmeli |
| TR | [Lodo](https://www.lodoseramik.com/urun-kategori/camurlar/) | Tedarikçi; marka olarak mükerrer sayılmayacak |
| TR | [Seramiksır](https://seramiksir.com/pages/icerik) | Marka/ürün ve hak incelemesi bekliyor |
| TR | [Clay.tr](https://www.clay.tr/camurlar/) | Tedarikçi; aynı markanın diğer mağaza kaydı yeni ürün değil |
| TR | [Güray](https://www.gurayceramic.com/) | Çamur üretim/ürün kodlarının ayrı teyidi gerekli |
| TR | [Kırmızı Çamur](https://www.kirmizicamur.com/urun-hakkinda/3/avanos-camuru) | Avanos kaynağı; jeolojik numune ile ticari lot karıştırılmayacak |
| TR | [Aşanlar](https://www.asanlarseramik.com/) | Tedarikçi kataloğu adayı |
| TR | [Erven](https://www.ervenmaden.com/tr) | Ham madde/teknik analiz adayı, hazır bünye markası değil |
| Avrupa | [SIO-2](https://www.sio-2.com/gb/content/18-high-fire-clays-sio-2) | 15 bünye kimliği |
| Avrupa | [Potclays](https://www.potclays.co.uk/clay-selection-chart/) | 38 bünye kimliği; analizler ayrı incelenecek |
| Avrupa | [G&S](https://www.goerg-schneider.de/de/downloads) | 245 TDS ilk aday; tüm toz/döküm/şamot sınıfları hazır bünye değildir |
| Avrupa | [Sibelco](https://www.sibelco.com/en/ceramic-brochures) | 2026 katalog ve analiz tabloları; hazır bünye/ham kil ayrı |
| Avrupa | [Scarva](https://www.scarva.com/en/Clays/cc-29.aspx) | Kendi ürünleri ve yeniden satılan markalar ayrılacak |
| Avrupa | [Potterycrafts](https://potterycrafts.co.uk/pages/about-us) | Üretici/tedarikçi kaynak adayı |
| Avrupa | [Solargil](https://solargil.com/content/entreprise) | Fransızca katalog adayı |
| Avrupa | [Ceradel](https://ceradel.fr/) | Fransızca katalog; SIO-2 tekrarları yeni marka sayılmayacak |
| ABD | [Laguna](https://www.lagunaclay.com/) | Güncel katalog, eski Wix kimliklerini uzlaştırma |
| ABD | [Standard Clay](https://www.standardclay.com/collections/all) | Kaynak adayı |
| ABD | [Aardvark](https://www.aardvarkclay.com/about.php) | Üretici kaynağı |
| ABD | [Sheffield](https://www.sheffield-pottery.com/collections/custom-clay-bodies-and-reclaim-service) | Özel müşteri reçetelerinin gizli tutulduğunu açıkça belirtiyor |
| ABD | [Kentucky Mudworks](https://kymudworks.com/) | Kendi bünyeleri ile Standard/Laguna ürünleri ayrılacak |
| ABD | [Armadillo](https://www.armadilloclay.com/) | Kendi ürünleri ve yeniden satış ayrılacak |
| ABD | [Mayco](https://www.maycocolors.com/documents/) | SDS tam kimya yerine kullanılamaz |
| Asya | Henüz ürün bazlı ticari katalog kaydı yok | Japonya/Çin/Tayland araştırma makaleleri ticari ürün kaydı yerine sayılmayacak |

## 1.000+ kayıt için kabul kapıları

Hedef sayısı onay/kalite eşiği değildir. Bir ürün için 10 oksit bulunması 10 ürün sayılmaz.
Bir markanın 25 kg/10 kg paketi ayrı bünye değildir. Islak/toz formül farkı varsa sürüm ilişkisi gerekir.

1. Kimlik: marka, üretici, ürün kodu, varyant, üretim/satış durumu, ülke/pazar.
2. Belge: tarih/sürüm, resmi TDS/CoA/SDS, açıklanan ve açıklanmayan alanlar.
3. Kimya: analitik yöntem, kuru/kızdırılmış baz, nem/LOI, oksit kapsamı, yuvarlama/tolerans.
4. Özellik: emme/küçülme/CTE için birim, ölçüm yöntemi, pişirim ve atmosfer koşulu.
5. Haklar: salt inceleme, yerel arşiv, görüntüleme, export ve model eğitimi ayrı izinler.
6. İnsan incelemesi + bağımsız karşılaştırma; yalnız bundan sonra motor kataloğuna kabul.

Toplu kazıma yapılmadı; raw site/PDF/fotoğraf paketleri indirilmedi. İzinli public export/API
bulunursa checksum'lı indirilecek. Özel ticari formüller için üretici paylaşımı veya yetkili
laboratuvar ölçümü gerekebilir; bunları kullanıcının adına talep eden mesaj gönderilmedi.
