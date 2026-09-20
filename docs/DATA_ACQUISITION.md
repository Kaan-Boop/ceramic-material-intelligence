# Açık veri edinimi — ilk koleksiyon

İnceleme ve indirme: 20 Eylül 2026. Kullanıcının henüz ürün envanteri yok; edinme alanı yasal hazır seramik, sır, bünye ve fırın verileri olarak genişletildi. Bu çalışma tüm interneti veya bütün üreticileri kapsayan tamamlanmış bir arşiv değildir.

## İndirilen kaynaklar

| Kaynak / URL | Veri türü / doğrulanmış büyüklük | Erişim / API / download | Scraping gerekli mi? | Lisans / ticari kullanım / araştırma | Kullanım ve kalite sınırı |
|---|---|---|---|---|---|
| [UCI Ceramic Samples](https://archive.ics.uci.edu/dataset/583/chemical+composition+of+ceramic+samples), DOI 10.24432/C54P5X | 88 pişmiş numune ölçüm satırı: 44 Body, 44 Glaze; 17 kimyasal sütun + 2 tanımlayıcı | Resmi ZIP içindeki CSV. Repository API seçeneği de belgeli; indirilebilir dosya kullanıldı | Hayır | CC BY 4.0; atıf/değişiklik bildirimi koşuluyla ticari ve araştırma kullanımı | EDXRF; modern üretim reçetesi değil. Bir negatif SrO değeri, tartışmalı PbO2 rapor etiketi var |
| [Mendeley Luomaqiao v2](https://data.mendeley.com/datasets/p49ncrb39k/2), DOI 10.17632/p49ncrb39k.2 | S1: 135 bünye satırı; S2: aynı 135 ID için sır; S3 katalog; S4 türetilmiş istatistik; S5 özet | Resmi public API; 5 CSV + README + metadata. Altı dosyanın yayıncı SHA-256 değeri doğrulandı | Hayır | CC BY 4.0; koşullu ticari ve araştırma kullanımı, belirtilmiş üçüncü taraf istisnaları ayrıca kontrol edilir | LA-ICP-MS element derişimleri; oksit yüzdesi değil. S1/S2/S3'ün ID kümeleri aynı; 270 bağımsız deney sayılmaz |
| [Zenodo Nicosia/Paphos Gate](https://zenodo.org/records/14742972), DOI 10.5281/zenodo.14742972 | 6 veri tablosu + 1 açıklama Excel dosyası; Table 1'de 80 katalog satırı; Table 2'de kaynak açıklamasına göre 39 XRF bünye örneği | Resmi Zenodo API, sürümlü dosya download. Metadata + 7 XLSX alındı | Hayır | CC BY 4.0; koşullu ticari ve araştırma kullanımı | Bünye, astar, sır, katman ve petrografi farklı granülerlikte. Satırları tek deney tablosuna birleştirmedik |
| [Fabris ve ark.](https://doi.org/10.3390/ma18010060), PMC11721402 | 7 makale tablosu; Table 2'de 11 frit/hammadde satırı; Table 1'de 4 reçete aralık seti | Europe PMC resmi açık erişim fullTextXML API; tek XML | Hayır | Makale CC BY 4.0; koşullu ticari ve araştırma kullanımı. Aktarılan üçüncü taraf standart/veri hakları ayrıca incelenir | Fritler anonim; reçeteler/aralıklar kesin formül değil. Analiz bazı/lot/belirsiz işaretler çözülmedi. Kimya çekirdeği için karantina |
| [kiln-controller](https://github.com/jbruce12000/kiln-controller) | 5 JSON program: 3 cone adlandırmalı, 2 test. 5 fırın modeli veya 5 ölçülmüş pişirim değil | Resmi GitHub API ile keşif; sabit commit'ten raw dosya indirme. README + config metni + 5 JSON | Hayır | README GPL-3.0-or-later; lisans yükümlülükleriyle ticari kullanım mümkün. Ayrı copyleft referans alanı | Programlar doğrulanmış pişirim önerileri değil; dosyalar birim metadata'sı taşımıyor. Kontrol kodu çalıştırılmadı |

Koleksiyonda **24 benzersiz kaynak/dosya/içerik kaydı, 425.581 byte** var. Sayı metadata/README/config metnini içerir; 24 dataset anlamına gelmez. Bunların 19'u CSV/XLSX/XML/JSON olarak profillendi. Orijinal XML/ZIP ve Excel dosyaları korunur.

GitHub commit: `a2b3071e4e55f47c20326563200da0b49d3c5bb8`.

## İndirilmemiş, izlenecek kaynaklar

| Kaynak | Bulunan içerik / erişim | İndirmeme veya kabul etmeme nedeni | Sonraki adım |
|---|---|---|---|
| [Glazy resmi export](https://github.com/derekphilipau/glazy-data) | YAML.gz, `LATEST`, eski CSV; README açık dağıtımı tarif ediyor | CC BY-NC-SA 4.0. Ticari ürüne yönelik araştırmayı otomatik noncommercial saymadık. Veri paketi indirilmedi | Ayrı ve gerçekten noncommercial kullanım kapsamı veya uygun izin; site scraping yok |
| [SciGlass](https://github.com/epam/SciGlass) | Cam bileşim/özellik arşivi | LICENSE başlığı/gövdesi belirsizliği ve veri/kod hak ayrımı | Kesin paket lisansı doğrulanmalı |
| [Digitalfire](https://digitalfire.com) | Malzeme/teknik bilgi; API hakkında açıklama | Genel açık dataset/yeniden yayın hakkı doğrulanmadı | Lisanslı export/API görüşmesi gerekir; otomatik toplama yok |
| [Ceramic Arts Network](https://ceramicartsnetwork.org/ceramic-recipes) | Editoryal reçeteler | Açık yeniden dağıtım lisansı doğrulanmadı | İzin veya açık lisanslı ayrı paket |
| [Sibelco seramik broşürleri](https://www.sibelco.com/en/ceramic-brochures) | Ball clay, feldspar, nefeline, bünye TDS/broşürleri; doğrudan PDF mevcut | Kamuya açık PDF olması uygulamada toplu yeniden kullanım hakkı sağlamaz; henüz izin/baz denetimi yok | Ürün bazında TDS/CoA ve hak teyidi. Motor için öncelikli takip |
| [Skutt teknik özellikler](https://skutt.com/skutt-resources/specifications/) ve [kılavuzlar](https://skutt.com/skutt-resources/manuals/) | Model özellikleri, indirilebilir kılavuzlar | Veri tabanı olarak kopyalama/yeniden yayın hakkı doğrulanmadı | Ürün metadata kataloğu için kapsamlı hak incelemesi; şimdilik bağlantı |
| [Nabertherm](https://nabertherm.com/en/products/arts-crafts/chamber-kilns) | Seramik fırın modelleri, teknik kataloglar | Açık toplu veri lisansı doğrulanmadı | Model/yıl/elektrik standardı ve izin birlikte doğrulanmalı |
| [Orton](https://www.ortonceramic.com/pyrometric-cones-resources) | Cone ve ısıtma hızı referansları | Yeniden dağıtım ve exact chart sürümü çözülmedi | Üretici referansına göre lisanslı küçük tablo; tek cone→°C değeri yok |
| [PubChem](https://pubchem.ncbi.nlm.nih.gov/docs/downloads) | Saf kimyasal kimlikleri/özellikleri, PUG API | Contributor hakları ve ihtiyaç duyulan sınırlı özellikler seçilmedi | Molar sabit setini ticari hammadde analiziyle karıştırmadan edinme |
| [USGS veri lisansları](https://www.usgs.gov/data-management/data-licensing) | Jeokimya/mineral veri paketleri | İlgili seramik altkümesi seçilmedi; üçüncü taraf istisnaları var | Belirli DOI/paket, kapsam ve hak kontrolü |

Bu tabloda “UNKNOWN” bir yasak hükmü değildir; yeterli kanıt olmadığı için henüz içeri aktarmama kararıdır. Lisans değerlendirmesi teknik kabul incelemesidir, hukuki garanti değildir.

## Erişim yöntemi ve sınırlar

- Kullanılan beş kaynakta resmi API veya özellikle yayımlanmış indirme dosyası kullanıldı; web sayfası toplu kazıması yapılmadı.
- Ağ okuyucu yalnızca listelenmiş HTTPS hostlarına erişir. Yönlendirmeyi takip etmeden host denetimi yapar; dosya başına 8 MiB sınırı ve en az 1 saniye istek aralığı vardır.
- 403/429 veya başka başarısızlıkta kaynak durur. Otomatik agresif retry, engel aşma veya farklı kaynaktan hak kısıtını dolaşma yok.
- Zenodo'nun yaklaşık 777 MB toplam paketindeki fotoğraf arşivleri alınmadı. Yalnızca küçük veri tabloları alındı.
- Mendeley API en son v2 döndürdü. Önce incelenen v1 sayfasını v2 verisinin lisans kanıtı saymadık; v2'nin `data_licence` alanı ayrıca doğrulandı.
- Mendeley resmi download, yayıncının S3 dosya sunucusuna yönlendi. İlk koşuda izin listesi bunu durdurdu; HTTP başlığı ve yayıncı checksum'u doğrulandıktan sonra tek host eklendi.
- robots.txt denetimi tüm sitelerde tamamlanmış değildir. Bu koleksiyondaki veri edinimi scraping'e dayanmaz; ileride scraping kararı için ayrı ToS/robots/izin denetimi zorunludur.
- Kaynak şartlarının tam hukuki denetimi, ürün içinde gösterim/export ve AI eğitimi onayı henüz yapılmadı. Açık lisanslı arşiv saklama, production release ile eşitlenmez.

## İkinci edinme dilimi — güncelleme

20 Eylül 2026: NIST/NBS'nin 70b, 97b, 98b, 99b sertifikaları ve kullanım politikası alındı. 4 referans materyalden 39 sertifikalı element değeri, ayrı araştırma katmanında sürümlendi. Güncel toplam 6 kaynak / 29 dosya-içerik kaydıdır. Bu belgenin önceki beş kaynak sayımları ilk edinme dilimine aittir. [İkinci dilim raporu ve hak tablosu](M2_BATCH2_REPORT.md) kapsamı, testleri ve sınırlamaları açıklar.

### Devam eden edinme öncelikleri

1. Önce pratik fayda: açıkça izinli, baz/ürün kimliği belli hammadde analizleri. Hedef 10–20; şu anda kabul edilmiş gerçek motor analizi **0**.
2. Modern stoneware/Cone 6 oksidasyon çalışmalarının CSV/JSON supplementary paketleri. Arkeolojik ölçüm sayısını artırmak pilot verisini kendiliğinden iyileştirmez.
3. Üreticiden izinli çamur bünyesi özellikleri: su emme, pişme küçülmesi, pişirim aralığı, ölçüm yöntemi. Bunlar tam oksit analizi yerine geçmez.
4. Fırın model kataloğu ile program arşivini ayır: model/enerji/hacim/güç/sensör bilgileri ve schedule farklı entity'lerdir.
5. Lisansı uygun yeni kaynaklar aynı raw/receipt/quality kapılarından geçer. Yeni kaynak sayısı kalite kabulünün yerine geçmez.

Hiçbir ücretli servis, ticari lisans satın alımı, hesap açılması, upstream kod çalıştırılması veya dışarı veri yayını yapılmadı.
