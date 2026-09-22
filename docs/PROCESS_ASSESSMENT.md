# Çamur–sır–pişirim değerlendirmesi — 22 Eylül 2026

## Çalışan kapsam

`research/process/assessment.py` ağ/UI/veritabanı bağımsızdır. API analiz raporuna
`process` alanı ekler. Kimya sonuçlarını değiştirmez. Sonuç ve girdiler sürüm/hash taşır.
Web'de bünye ve sır için ayrı, isteğe bağlı ürün/kaynak/koşul/pişirim aralığı girilir.
Manuel girilmiş referansın doğruluğu otomatik doğrulanmış sayılmaz.

- Tepe sıcaklığı ile **bildirilen** aralık karşılaştırılır: altında / içinde / üzerinde.
- Kaynak, ürün kimliği ve kaynak koşulları olmadan aralık kabul edilmez.
- API'de plan segmentlerinin süresi `abs(Tson−Tilk)/hız×60 + bekleme` ile dakika hesaplanır.
- Doğal soğumanın süresi null olur; bilinen süre toplam süre diye sunulmaz.
- Program tepe sıcaklığı ve ayrı girilmiş hedef çelişirse uyarılır, sessizce düzeltilmez.
- Uygulama, arayüz, soğuma uyumu, yüzey, renk ve bünye dayanımı ayrı bölümlerdir.
- Bu altı alanda henüz model yok: `UNAVAILABLE`, olasılık `null`. Yüzde uydurulmaz.

Program segment editörü henüz web formunda yoktur; süre hesabı API üzerinden kullanılabilir.
Mevcut web taslakları korunur; yeni isteğe bağlı aralık alanları olmayan eski taslaklar geçerlidir.
Bu sürüm ısı/kütle/gaz/gerilme modellerini birbirine bağlamaz. İşlem kontrolü, fizik simülasyonu değildir.
Raporun `CALCULATED` etiketi sadece karşılaştırma/aritmetik için geçerlidir.

## Bilimsel dayanak ve kaynakların aktarım durumu

İnceleme tarihi 2026-09-22. Aşağıdaki tablo bibliyografik araştırma indeksidir;
lisansı belirsiz içerikler ham veri setine veya eğitim verisine aktarılmadı.
Kaynaklar altı aşamalı ürün tasarımını doğrudan önermez; aşamaların ayrımı proje kararıdır.

| Kaynak | Ülke/dil; ilgisi | Lisans ve kullanım kararı |
|---|---|---|
| [AIST Ceramic Color Database, Sugiyama 2013](https://doi.org/10.5571/syntheng.6.84) | Japonya/İngilizce; 300.000'den fazla fiziksel sır test parçasının koleksiyon/veri tabanı çalışması | Serbest okunabilirlik açık veri lisansı değildir. İndirilmiş 300.000 kayıt **yok**. Export/API/haklar incelenecek. |
| [Kasama celadon, Ojima et al. 2022](https://doi.org/10.2109/jcersj2.21162) | Japonya/İngilizce; atmosfer geçmişi, Fe durumu ve renk | J-STAGE sayfasında CC-BY-4.0. PDF arşivleme; tam metin sayısal veri çıkarımı henüz yapılmadı. Belirli numunelerin bulguları evrensel renk kuralı değildir. |
| [Inada 1978](https://doi.org/10.2109/jcersj1950.86.990_76) | Japonca; bünye/sır genleşmesi ve sıcaklığa bağlı gerilme | Lisans doğrulanmadı; yalnızca referans. |
| [Low thermal expansion cookware glaze](https://doi.org/10.60136/bas.v10.2021.155) | Tayland; Chulalongkorn/Department of Science Service | CC-BY-NC-ND-4.0; ticari modele alınmadı. Kordiyerit/spodümen esaslı özel bünye, genel stoneware değil. |
| [Thai crazing study](https://ph02.tci-thaijo.org/index.php/eit-researchjournal/article/view/130008) | Tayca; sır çatlağı deneyi | Açık yeniden kullanım lisansı doğrulanmadı; yalnızca bibliyografik kayıt. |
| [Chinese Tianmu mechanisms](https://doi.org/10.1039/c9ra06870h) | Çin/İngilizce; faz ayrımı, demir oksit yapıları ve görünüm | Europe PMC XML izin alanında açık lisans bulunamadı; tam metin kalıcı arşiv/training'e alınmadı. Ayrı yayıncı lisansı kontrolü gerekli. |
| [NTUA tez adayı](https://lib.ntua.edu.tw/wSite/public/Data/f1717034009914.pdf) | Tayvan; kristal/mat sır çalışması adayı | Henüz tam metin ve lisans doğrulanmadı; bilimsel modele dayanak değil. |
| [Rusça sırlı tuğla çalışması adayı](https://cyberleninka.ru/article/n/mehanizm-formirovaniya-glazuri-v-protsesse-obzhiga-glazurovannogo-kirpicha.pdf) | Rusça; sır oluşumu | Henüz yayıncı/hak/metot doğrulanmadı; yalnızca keşif adayı. |
| [amorphouspy](https://github.com/glasagent/amorphouspy) | Atomistik cam hesap iş akışları | Apache-2.0; commit 2c7b65d2922066b01b668e392bfec06a0f1aa431. LICENSE/README/pyproject referans kopyaları. Kurulmadı, kodu çalıştırılmadı. Proje üretime hazır olmadığını bildiriyor. |
| [Orton](https://www.ortonceramic.com/pyrometric-cones) | Cone/heatwork üretici referansı | Referans bağlantısı; sayısal cone tablosu kopyalanmadı. |
| [Mayco SW-212 Peacock](https://www.maycocolors.com/product/sw-212-peacock/) | ABD; bünye, kat ve atmosferle birlikte bildirilen sır sonuçları | Üretici beyanı; açık dataset lisansı yok. Fotoğraf/kimya veri seti indirilmedi; kullanıcı çamuruyla eşleştirilmedi. |
| [Mayco combinations](https://www.maycocolors.com/glaze-combinations/) | Beyaz stoneware üzerinde cone 6 oksidasyon ve cone 10 redüksiyon örnekleri | Bu iki koşul farkı yalnız sıcaklığa atfedilemez. Formül ve bağımsız tekrar verisi değildir. Toplu aktarım izni bekleyen referans. |
| [SIO-2 PRAI 3D](https://www.sio-2.com/gb/3d-printing-ceramic-clays/1708-prai-3d-5kg-8422830133079.html) | İspanya; ürün bazlı şamot, küçülme, emme ve genleşme bilgisi | PRAI 3D ile normal PRAI aynı ürün kabul edilmez. Açık lisans doğrulanmadı; yalnızca referans. Kullanıcının bünyesi olduğu varsayılmadı. |

Arşiv manifest'i: `data/manifests/process-acquisition-2026-09-22.json`.
Ham dosyalar: `storage/process-pool/2026-09-22/`; Git'e konmaz, checksum/izin kaydı Git'te tutulur.
Üretici fotoğrafları, tezler ve topluluk veri tabanları lisans belli olmadan toplanmaz.

## Bir sonraki bilimsel teslim

1. Gerçek ürün için üretici TDS/CoA + analiz bazını edin; sır reçetesi veya ticari sır kimliğiyle bağla.
2. Specimen kaydı: bünye lotu, bisküvi, kalınlık ölçüm yöntemi, kuruma, fırın konumu,
   gerçek rampalar/bekleme/soğuma/atmosfer, witness cone ve değerlendirme zamanı.
3. Aynı koşul tekrarlarıyla gözlenen sonuçları kaydet; değerlendirilmemiş kusuru “yok” sayma.
4. Ölçülmüş genleşme eğrilerini mevcut termal araştırma modülüne bağlamak için koşul eşdeğerliğini doğrula.
5. Üretici aralığı, gözlenen numune sonucu ve model tahmini ayrı kalmalı.

Şamot kaba taneli önceden pişirilmiş malzeme olabilir; kullanıcının tarif ettiği parçaların
şamot olduğu doğrulanmadı. Şamot oranı tek başına daha yüksek dayanım veya iyi sır uyumu anlamına getirilmez.

## Doğrulama — bu teslim

- Araştırma ortamında unittest: **187 test geçti** (10 yeni süreç testi dahil).
- Ayrı prototip ortamında API: **10 test geçti** (2 yeni süreç entegrasyon testi dahil).
- OpenAPI TypeScript sözleşmesi yeniden üretildi; typecheck ve production build geçti.
- Playwright: **14/14 geçti**; masaüstü Chromium ve iPhone boyutunda Chromium emülasyonu.
  Gerçek iPhone/Safari testi değildir. Kaynaklı aralık, taslak geri yükleme, sonuç raporu,
  aralık üstü uyarı ve mevcut gecikmiş yanıt/kimya/export akışları test edildi.
- Mobil tam sayfa görüntüsü incelendi; yatay taşma testi geçti.
- React rehberi: form alt bileşenleri render içinde tanımlanmadı; eski taslaklar için yeni
  alanlar isteğe bağlı ve doğrulamalıdır. Bilimsel hesap Python'da tek yerde kalır.
- Starlette test istemcisinin httpx kullanımı için deprecation uyarısı var; testler başarısız değil.
  Bağımlılık yükseltmesi ayrı, sözleşme testli bakım işi olarak bırakıldı.
- Fiziksel fırın deneyi, yüzey tahmini doğrulaması ve olasılık kalibrasyonu **yapılmadı**.
