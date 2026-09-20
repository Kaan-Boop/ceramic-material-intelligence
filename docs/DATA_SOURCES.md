# Veri kaynakları ve araştırma kaydı

Kontrol tarihi: 2026-09-20. Bu tablo, aynı görevde yapılan önceki web incelemesinin kaynaklarını ve bulgularını kaydeder. Kaynak metadatası okundu; dataset import edilmedi. Hiçbir satır otomatik production kabulü değildir.

`NOT_VERIFIED` = bulunmadığı veya izin verilmediği iddiası değil; henüz doğrulanmadı. SourceRecord ve hak incelemesi **paket/kayıt düzeyinde** M2'de yapılır.

## Kaynak envanteri

| ID / kaynak | Veri / büyüklük | Erişim / API / download | Scraping | Hak durumu: ticari / araştırma | Kalite / kullanım kararı |
|---|---|---|---|---|---|
| S01 [Glazy](https://help.glazy.org/about/data-use-policy) | Reçete, test, fotoğraf; güncel toplam doğrulanmadı | Web, kullanıcı export; genel public API doğrulanmadı | İzinsiz bulk yasak; kullanmayacağız | CC BY-NC-SA 4.0 + ek politika; commercial AI ayrı lisans / noncommercial koşullu | Topluluk bağlamı değişken; çekirdek bağımlılığı değil |
| S02 [glazy-data](https://github.com/derekphilipau/glazy-data) | Reçete/malzeme arşivi; sayı sayılmadı | YAML.gz, eski CSV, LATEST işaretçisi; download var | Gerekmez | README NC-SA; commercial açık değil / koşullu | Duplicate ve eksik veriler; ayrı hak alanı |
| S03 [Digitalfire API açıklaması](https://digitalfire.com/glossary/digitalfire%2Bapi) | Malzeme, reçete, teknik açıklama; toplam bilinmiyor | API çalışması belgeli; public erişim sözleşmesi doğrulanmadı | Plan yok | Site hakları saklı; dataset hakları UNKNOWN / UNKNOWN | Yöntem referansı; yeniden dağıtım kabulü yok |
| S04 [Ceramic Arts Network](https://ceramicartsnetwork.org/ceramic-recipes/how-to-use-ceramic-recipes) | Editoryal reçeteler; sayı doğrulanmadı | Web/abonelik; bulk/API doğrulanmadı | Plan yok | Açık veri lisansı doğrulanmadı / yeniden yayın ayrıca inceleme | Kaynak keşfi; veri setine alınmadı |
| S05 [GlazyBench](https://arxiv.org/abs/2605.06641) | Yazar beyanı 23,148 formülasyon | Ön yayın; veri paketi/API doğrulanmadı | Plan yok | Dataset hak zinciri UNKNOWN / UNKNOWN | Benchmark adayı; bağımsız deney sayısı değil |
| S06 [SciGlass Next](https://docs.sciglass.uni-jena.de/guide/) | Birincil çalışmada 422,000+ cam/eriyik | Web, belgelenmiş API, tarihsel arşiv | Gerekmez | Tarihsel ODbL atfı; paket lisansı belirsiz / doğrulanacak | Cam araştırması; sır yüzeyi datası değil |
| S07 [Sibelco](https://ceramics.sibelcotools.com/) | Ürün/mineral PDF bilgileri; uygun analiz sayısı bilinmiyor | Web/PDF; public API doğrulanmadı | Gerekmez | Yeniden dağıtım UNKNOWN / UNKNOWN | TDS/CoA ve gerçek lot aranacak |
| S08 [Orton](https://www.ortonceramic.com/pyrometric-cones-resources) | Küçük cone/hız/seri referans tabloları; satır sayılmadı | Resmî chart PDF/web; API doğrulanmadı | Gerekmez | Yeniden dağıtım UNKNOWN / UNKNOWN | Birincil üretici; conversion üretime alınmadı |
| S09 [CIAAW](https://ciaaw.org/abridged-atomic-weights.htm) | Atom ağırlıkları; M2 için sınırlı element altkümesi | Web/yayın; API doğrulanmadı | Gerekmez | Sayısal sabit seçimi ve tablo hak kapsamı incelenecek | Production sabit seti henüz yok |
| S10 [PubChem](https://pubchem.ncbi.nlm.nih.gov/docs/downloads) | Kimlik/özellik; ilgili altküme sayılmadı | PUG-REST/PUG-View, CSV/JSON ve başka indirmeler | Gerekmez | Contributor-specific; blanket izin yok | Saf bileşik kimliği, ticari hammadde analizi değil |
| S11 [USGS](https://www.usgs.gov/data-management/data-licensing) | Mineral/jeokimya; ilgili altküme seçilmedi | Dataset'e göre API/dosya | Öncelikle gerekmez | USGS üretimi genel olarak public domain; üçüncü taraf ayrı | Jeolojik bağlam; lot analizi yerine geçmez |
| S12 [Crossref](https://www.crossref.org/documentation/retrieve-metadata/) | DOI metadata; seramik altkümesi sayılmadı | REST API/metadata download | Gerekmez | Metadata çoğunlukla serbest, abstract hakları ayrı | Kaynak zenginleştirme; deney verisi değil |
| S13 [Zenodo](https://zenodo.org/) / üniversiteler | Supplementary datasets; henüz seçilmiş sır dataset'i yok | Kayıt bazlı API/dosya | Öncelikle gerekmez | Record-specific UNKNOWN | Önce lisans/baz/deney kapsamı incelemesi |
| S14 [Reddit](https://redditinc.com/policies/data-api-terms) / forum | Gözlem/fotoğraf; sayı bilinmiyor | Reddit API onay/koşul; diğer forumlar ayrı | Kullanılmayacak | Ticari kullanım ve AI hakları koşullu; araştırma otomatik izin değil | Keşif; onaysız training/import yok |
| S15 [EPO OPS](https://www.epo.org/en/searching-for-patents/data/web-services/ops) | Patent metadata/metin; ilgili altküme bilinmiyor | Kayıtlı REST/XML, kota | Gerekmez | Sözleşme kapsamında ürün kullanımı; raw aynen dağıtım kısıtlı | Patent örneği bağımsız doğrulanmış deney sayılmaz |
| S16 [Kanthal A-1](https://www.kanthal.com/en/products/datasheets/material-datasheets/wire/resistance-heating-wire-and-resistance-wire/kanthal-a-1/) | Ürün termal/fiziksel özellikleri; tek datasheet incelendi | Web/PDF; public data API doğrulanmadı | Gerekmez | Yeniden dağıtım UNKNOWN / UNKNOWN | İleri metal modülü; ürün/sıcaklık aralığı önemli |
| S17 [SCHOTT](https://www.schott.com/en-gb/products/sealing-and-solder-glass-p1000291/technical-details) | Cam CTE/Tg/sealing bilgisi; altküme sayılmadı | Web ve download belgeleri | Gerekmez | Yeniden dağıtım UNKNOWN / UNKNOWN | İleri cam/arayüz modülü |

## Lisans/erişim bulguları ve sınırlamalar

- Glazy [ToS](https://help.glazy.org/about/terms-of-service) ve [AI/data policy](https://help.glazy.org/about/data-use-policy) beraber incelendi. Politika noncommercial araştırmaya koşullar getiriyor; commercial AI ayrı lisans; izinsiz bulk harvesting yasak. Export deposunun [README](https://raw.githubusercontent.com/derekphilipau/glazy-data/master/README.md) dosyası da NC-SA bildiriyor. Export'un belirli kullanımını değerlendirirken sürüm ve erişim yolu ayrıca sabitlenecek.
- Digitalfire'da API açıklaması bulunması, herkese açık entegrasyon hakkı veya kullanılabilir endpoint sözleşmesi olduğu anlamına gelmez. [Ana sayfa](https://digitalfire.com) all-rights-reserved bildirir.
- Ceramic Arts Network'te [yayıncı copyright açıklaması](https://ceramicartsnetwork.org/docs/default-source/magazine-archives/workshop-handbook-2022.pdf?sfvrsn=ec5ccd2_3) yeniden yayın izninin ayrı olduğunu gösterir. Bu tek yayın, bütün sitenin güncel ToS denetimi yerine geçmez.
- SciGlass [LICENSE](https://github.com/epam/SciGlass/blob/master/LICENSE) içinde ODbL başlığı ile MIT tarzı gövde metni birlikte görüldü. [Üniversitedeki birincil çalışma](https://www.db-thueringen.de/servlets/MCRFileNodeServlet/dbt_derivate_00068598/ADEM_ADEM202401560.pdf) ODbL ve dataset kapsamını tarif ediyor. Bu tutarsızlık üretim kabulünden önce paket bazında çözülmeli; ticari izin varsayılmaz.
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/docs/downloads) contributor lisansına gitmeyi söylüyor. [Crossref](https://www.crossref.org/documentation/retrieve-metadata/) abstract haklarını metadata'dan ayırıyor.
- [USGS copyright](https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits): USGS üretimi ile üçüncü taraf içerik ayrılır.
- [EPO OPS koşulları](https://www.epo.org/en/service-support/ordering/terms-and-conditions/ops-terms-and-conditions): API erişim sözleşmesi, fair use ve aynen raw yayın kısıtları var. Ücretsiz kota olması sınırsız hak değildir.

robots.txt: Glazy, Digitalfire, Ceramic Arts Network adreslerine önceki araştırmada erişim denendi; araç hata verdi. Durum **NOT_VERIFIED**. Diğer adaylarda kapsamlı robots kontrolü henüz yapılmadı. robots izin verse bile veri lisansı sağlamaz. Erişim reddi/ToS yasakları scraping alternatifiyle aşılmaz.

ResearchGate ve Google Patents için veri edinme kabulü yok. ResearchGate yerine yayıncı/yazarın yasal depo sürümü ve dosyanın kendi lisansı aranır. Patent araştırmasında başlangıç adayı belgelenmiş EPO erişimidir; patent tekniğini kullanma hakkı, metne erişimden ayrı konudur.

## İlk edinme sırası

1. Kullanıcının gerçek ürün envanteri ve kendisine ait kayıtları (Q-01/Q-03).
2. İzni açık TDS/CoA veya kullanıcıya ait ölçüm; başlangıç hedefi 10–20 kabul edilmiş analiz, kota değil.
3. Sınırlı kaynaklı atom/oksit sabit seti; teorik fixture'lar ayrı.
4. Cone 6 oksidasyon bağlamı yeterli, lisansı açık akademik/kurumsal deney dosyaları.
5. Topluluk export'ları yalnızca açıkça uygun kullanım amacı ve hak kararıyla ayrı release.

M2'de üretici analizi bulunamazsa genel feldspar seçip boşluğu doldurmayız. Sentetik fixture ile validator doğrulanabilir; gerçek ürün setinin eksikliği ayrıca raporlanır.

## Kaynak kayıt şablonu

Her kabul edilen kayıt: source_name, source_url, source_type, source_author (bilinmiyorsa null+reason), source_license (UNKNOWN olabilir fakat üretim kabulünü kısıtlar), commercial_use_allowed, attribution_required, share_alike_required, retrieval_date. Ayrıca lisans kanıt URL'si/hash'i, policy check tarihi, exact kayıt kimliği/sürümü, parser sürümü ve raw checksum. Hak alanları boolean yerine ALLOWED/DENIED/UNKNOWN veya gereklilik için REQUIRED/NOT_REQUIRED/UNKNOWN olarak tutulur.

## Bilimsel referanslar

| İddia/yöntem | Dayanak | Kapsam / açık nokta |
|---|---|---|
| Oksit kütlesi, mol, unity | [Digitalfire](https://digitalfire.com/article/189), [Glazy](https://help.glazy.org/concepts/analyses) | Teknik yöntem; test verisi değil |
| UMF eşitliği fiziksel sonuç eşitliği değil | [Unity Formula](https://digitalfire.com/glossary/unity%2Bformula), [Glazy malzemeler](https://help.glazy.org/guide/materials) | Malzeme analizi/kimliği korunacak |
| Cone heatwork/ısıtma koşulları | [Orton](https://www.ortonceramic.com/pyrometric-cones) | Chart aktarımı hakkı/sürümü açık |
| Stull eksenleri | [Glazy](https://help.glazy.org/guide/recipes), [Digitalfire sistem tanımı](https://digitalfire.com/picture/696) | Orijinal deney kapsamı incelenmedi; bölge modeli yok |
| Hesaplanmış expansion sınırı | [Digitalfire](https://digitalfire.com/glossary/calculated%2Bthermal%2Bexpansion) | İkinci bağımsız katsayı/model doğrulaması eksik; üretim dışı |
| CV grouping / calibration | [scikit-learn CV](https://scikit-learn.org/stable/modules/cross_validation.html), [calibration](https://scikit-learn.org/stable/modules/calibration.html) | Seramik grup seçimi proje kararı |

Bu dosya hukuki görüş veya veri kullanım izni değildir; teknik kabul politikası ve kanıt envanteridir.
