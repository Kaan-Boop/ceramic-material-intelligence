# Kullanıcının 23 kaynaklık arşivi ve fizibilite PDF'si: kabul incelemesi

İnceleme tarihi: 2026-09-20. Aşama: M2. Bu belge kaynak keşfi ve teknik kabul kararıdır; hukuki görüş, bilimsel doğrulama veya veri indirme izni yerine geçmez.

## Sonuç

Liste projenin uzun vadeli kapsamıyla uyumlu; ancak aynı listede dört farklı şey var: veri seti, yazılım kütüphanesi, teknik bilgi sitesi ve veri toplama aracı. Bunları tek bir veri tabanına veya lisans sınıfına çevirmiyoruz. Bu turda README/lisanslar, bazı resmî API belgeleri ve OpenGlaze'in seçili veri dosyaları okundu. Yeni bulk dataset indirilmedi, uygulama bağımlılığı kurulmadı, dış kod çalıştırılmadı.

Mevcut raw koleksiyon sayımı **6 kaynak / 29 dosya-içerik** olarak değişmedi. Aşağıdaki 23 satır 23 edinilmiş veri seti değildir. Core engine için kabul edilmiş tam gerçek hammadde analizi hâlâ 0.

## Kullanıcının PDF'si

- Başlık: Ceramic Material Intelligence Platform: Veri Kaynağı, Bilimsel Altyapı ve Teknik Fizibilite Araştırması.
- Metadata yazarı: ChatGPT Deep Research; birincil bilimsel yayın veya veri lisansı değildir.
- 46 sayfanın metni okundu. Lisans tabloları ve mimari örnekler için 3, 4, 30, 32. sayfalar ayrıca render edilerek incelendi.
- Kaynak dosya SHA-256: `76d8e1e83487dd4ab3368c2fdd810b51eb542f210e135ea1bd04b78b5ff09a3c`.
- PDF değiştirilmedi. Geniş tabloların sağ sütunları sayfa sınırında kesiliyor; görselde okunmayan sütunlar metin katmanında bulunuyor. Kritik iddialar bu nedenle ayrıca birincil kaynaklarla kontrol edildi.
- Raporun tüm bilimsel iddiaları, atıfları ve tarihleri bağımsız doğrulanmış sayılmamalı. Özellikle ticari termodinamik veritabanı kapsamları bu turda denetlenmedi.

## Güncel kaynak matrisi

`BUGÜN` doğrudan sayfa/dosya incelemesini, `ÖNCEKİ` mevcut M1/M2 incelemesini, `ADAY` henüz paket düzeyinde incelenmeyeni belirtir. Hiçbiri tek başına üretim kabulü değildir. Boyut bilinmiyorsa sayı uydurulmadı. Yazılım için kayıt sayısı uygulanamaz.

| # / Kaynak | Tür ve büyüklük | Erişim / download / API | Hak ve kullanım kararı | Durum / sıra |
|---|---|---|---|---|
| 1 [Glazy](https://glazy.org/) | Topluluk reçete/gözlem/görsel; toplam sayılmadı | Resmî export tercih edilir; site scraping yok | NC-SA ve AI/veri koşulları; üretim/training bekletilir | ÖNCEKİ; hak çözümüne bağlı |
| 2 [Glazy Data](https://github.com/derekphilipau/glazy-data) | Reçete, malzeme, analiz; güncel toplam sayılmadı | GitHub YAML.gz + LATEST; legacy CSV; scraping gerekmez | README CC BY-NC-SA 4.0; ticari amaçlı kullanım için uygun izin gerekli | BUGÜN README; bulk alınmadı |
| 3 [GlazyBench GitHub](https://github.com/ziazhai/GlazyBench) | Yayıncı beyanı: property train 16.781/test 4.903; image metadata 4.490/443 | JSON split ve baseline kodu; GitHub sürümünde resimler yok | CC BY-NC-SA 4.0; commercial AI/deployment için ayrıca lisans | BUGÜN; benchmark ileride, veri alınmadı |
| 4 [GlazyBench HF](https://huggingface.co/datasets/AlpachinoNLP/GlazyBench) | Aynı benchmark'ın görsel/source dağıtımı; ikinci bağımsız deney seti değil | HF dosyaları; viewer bu incelemede JSON parse hatası gösterdi | Kart MIT, canonical repo NC-SA: LICENSE_CONFLICT; MIT kabul edilmez | BUGÜN; bulk alınmadı |
| 5 [OpenGlaze](https://github.com/KyaniteLabs/openglaze) | Yazılım + foundation verisi; incelenen materials.json içinde **36** kayıt | GitHub kaynak/JSON/YAML; scraping gerekmez | Yazılım MIT; karma upstream veri hakları kayıt bazında çözülmedi | BUGÜN dosya incelemesi; teknik karşılaştırma öncelikli |
| 6 [LIPGLOSS2](https://github.com/PieterMostert/LIPGLOSS2) | Kısıtlı reçete optimizasyon yazılımı; veri seti sayılmaz | Python/CVXOPT; GitHub download | Repo GPL-3.0; koşulları sağlanırsa ticari kullanım mümkün, NC değildir | BUGÜN README/lisans etiketi; koda gömülmedi |
| 7 [LIPGLOSS-CALC](https://github.com/PieterMostert/LIPGLOSS-CALC) | Eski hesaplama çekirdeği | Python; GitHub download | GPL-3.0; exact sürüm/lisans ve dağıtım mimarisi ayrıca incelenir | BUGÜN; yazar README'de eski sürüm diyor |
| 8 [glazy-data-analysis](https://github.com/PieterMostert/glazy-data-analysis) | Araştırma kodu; Glazy kaynaklı deney | GitHub; paket/model kurulmadı | Kod lisansı ile Glazy veri hakları ayrı; upstream NC kısıtı ortadan kalkmaz | BUGÜN depo; dosya düzeyi kabul tamamlanmadı |
| 9 [Materials Project](https://materialsproject.org/) | Hesaplamalı yapılar/enerjiler; ihtiyaç altkümesi seçilmedi | Resmî API, istemci API anahtarı ister | Genel lisans ifadesi yeterli değil: resmî belgede GNoME için BY-NC açıkça belirtiliyor | BUGÜN API/release docs; sınırlı altküme ileride |
| 10 [Materials Project API](https://github.com/materialsproject/api) | İstemci yazılımı; bağımsız malzeme dataset'i değil | Python mp-api; kullanıcı hesabı/API key | İstemci lisansı erişilen kayıtların haklarını değiştirmez; exact paket kabulü bekliyor | BUGÜN docs/repo; kurulmadı |
| 11 [pymatgen](https://github.com/materialsproject/pymatgen) | Composition/structure/phase analysis yazılımı | Python; GitHub/package | MIT; haricî veri kaynakları ayrı | BUGÜN README; M3 çekirdeğine zorunlu bağımlılık değil |
| 12 [pycalphad](https://github.com/pycalphad/pycalphad) | CALPHAD hesaplama yazılımı | Python; TDB okuma | MIT yazılım; TDB lisansı/model kapsamı ayrı | BUGÜN README; termal araştırma fazına ertelendi |
| 13 [NIST JANAF](https://janaf.nist.gov/) | Termokimyasal tablolar; SRD 13; site son veri güncellemesini 1998 gösteriyor | Web ve PDF tablo; bu tur bulk/API kullanılmadı | SRD kapsamı; non-SRD SRM kabulümüz buraya uygulanmaz; yeniden dağıtım UNKNOWN | BUGÜN resmî tanım/politika; içerik alınmadı |
| 14 [RRUFF](https://www.rruff.net/) | Mineral/spektrum/yapı; uygun altküme sayılmadı | Güncel adres RRUFF.net; dosya/indirme koşulları ayrıca incelenecek | Açık erişim yeniden dağıtım lisansı sayılmaz; UNKNOWN | BUGÜN ana sayfa/kurum kaydı; faz tanımlama ileride |
| 15 [Mindat](https://www.mindat.org/) | Mineral/lokalite bilgisi; uygun altküme seçilmedi | API varlığına ilişkin resmî yönetici açıklaması var; güncel erişim koşulları tamamlanmadı | 2024 açıklaması NC ve ayrı ticari lisans diyor; güncel sözleşme yerine geçmez | BUGÜN yönetici açıklaması; import bekletilir |
| 16 [USGS feldspar](https://www.usgs.gov/centers/national-minerals-information-center/feldspar-statistics-and-information) | Üretim/kaynak istatistiği; ürün lot analizi değil | Paket bazında dosya/API | USGS üretimi ve üçüncü taraflar ayrılır; somut paket seçilecek | ÖNCEKİ genel politika; yeni altküme ADAY |
| 17 [Digitalfire](https://digitalfire.com/) | Teknik bilgi ve malzemeler | Web; genel açık bulk lisansı doğrulanmadı | Yöntem referansı; toplu yeniden kullanım için anlaşma/izin incelemesi | ÖNCEKİ; bu tur bulk yok |
| 18 [Orton](https://www.ortonceramic.com/pyrometric-cones-resources) | Cone/heatwork referansı | Resmî PDF; seri/ramp hızı önemli | Chart yeniden dağıtımı UNKNOWN; kaynak olarak kullanılabilirlik import izni değildir | ÖNCEKİ; küçük izinli tablo hedefi |
| 19 [Ceramic Arts Network](https://ceramicartsnetwork.org/ceramic-recipes) | Editoryal reçeteler | Web/abonelik; açık bulk doğrulanmadı | Yeniden yayın UNKNOWN; kaynak keşfi | ÖNCEKİ; import yok |
| 20 [GlazeShare](https://www.glazeshare.com/) | Katmanlı glaze kombinasyonu/gözlem/fotoğraf; toplam sayılmadı | Web; API/export bu tur doğrulanmadı | Ana sayfa all-rights-reserved; ToS gövdesi araçta okunamadı; UNKNOWN | BUGÜN; resim/reçete kazınmadı |
| 21 [PubChem](https://pubchem.ncbi.nlm.nih.gov/) | Saf kimyasal kimliği, formül/MW | PUG-REST/PUG-View; sınırlı alan seçimi | Alanın depositor/source hakları izlenir; ticari kil karışımı tek CID değildir | ÖNCEKİ; kimlik/sabit için aday |
| 22 [matminer](https://github.com/hackingmaterials/matminer) | Özellik türetme/ML yazılımı | Python; dataset retrieval ayrıca var | BSD-tarzı izinli LBNL metni, ek Enhancements maddesi; dataset lisansları ayrı | BUGÜN LICENSE; ML aşamasına ertelendi |
| 23 [kiln-controller](https://github.com/jbruce12000/kiln-controller) | Kontrol yazılımı ve örnek programlar; evrensel gerçek pişirim arşivi değil | GitHub; kendi cihazında log üretimi | GPL-3.0-or-later; kontrol kodu çalıştırılmadı | ÖNCEKİ edinim: 5 örnek program; yeni indirme yok |

Hiçbir yeni site için scraping kararı alınmadı; robots/ToS toplu denetimi tamamlanmış sayılmaz. API key bulunmadığı için Materials Project hesabı açılmadı veya sırlar aranmadı. Kullanıcıdan anahtarı sohbet mesajına yapıştırması istenmeyecek.

## Kritik kabul bulguları

### 1. GlazyBench'in iki dağıtımı tek hak zinciridir

[Canonical README](https://raw.githubusercontent.com/ziazhai/GlazyBench/main/README.md) NC-SA koşullarını ve ticari AI kullanımı için ayrı lisans gereğini açıkça yazıyor. [HF kartındaki](https://huggingface.co/datasets/AlpachinoNLP/GlazyBench) MIT etiketi bu çelişkiyi çözmez. Sayılar README beyanıdır; dosyaları indirip bağımsız saymadık. Etiketi eksik örnekler bütün görevlerde etiketli sayılmayacak. GitHub ve HF kopyaları örnek sayısını ikiye katlamayacak.

Glazy Data'nın [README'si](https://raw.githubusercontent.com/derekphilipau/glazy-data/master/README.md) resmî export yolunu, duplicate sorununu ve fotoğraf kaynaklı RGB sınırlılığını açıklar. Hazır veri olması laboratuvar doğruluğu veya ticari izin değildir. Kaynak okuma yapılabilir; bu projeye yönelik veri/training edinimi için uygun kullanım kararı henüz yoktur.

### 2. OpenGlaze: MIT kod ile hammadde gerçeğini ayır

İncelenen Git ağacı: `ba43d84925bc83610fcf8be0b5fafee27e77210c`. [Lisans](https://github.com/KyaniteLabs/openglaze/blob/ba43d84925bc83610fcf8be0b5fafee27e77210c/LICENSE) MIT. Haricî kodu çalıştırmadık; motorun doğru/yanlış olduğuna dair çalıştırılmış test sonucu yok.

[materials.json](https://github.com/KyaniteLabs/openglaze/blob/ba43d84925bc83610fcf8be0b5fafee27e77210c/ceramics-foundation/data/materials.json) için doğrudan JSON alan sayımı:

| Kontrol | Sonuç |
|---|---:|
| Malzeme kaydı | 36 |
| Kayıt düzeyinde `analysis_basis` | 0 |
| Kayıt düzeyinde `analysis_date` | 0 |
| Kayıt düzeyinde `source_url` | 0 |

Dosyada toplu kaynak metni Digitalfire, Glazy ve Pacer Minerals'i anıyor; bu her satırın özgün kaynağını/iznini belirlemiyor. Dosya güncelleme tarihi, analiz tarihi sayılmayacak. EPK alias listesinde genel kaolin bulunuyor: bunu otomatik ürün eşleştirme kuralı olarak almayacağız. Manganese dioxide adlı kaydın MnO temsili de redoks/baz açıklaması olmadan motor girdisine alınmayacak. Bunlar tüm projenin kalitesine hüküm değil, bizim veri sözleşmemizle gözlenen uyumsuzluklardır.

[thermal-expansion.json](https://github.com/KyaniteLabs/openglaze/blob/ba43d84925bc83610fcf8be0b5fafee27e77210c/ceramics-foundation/data/thermal-expansion.json) göreli kullanım uyarıları içeriyor; UMF ile mol kesrini aynı anlamda yorumlamamalıyız. Aralık, seçilmiş katsayı ve ölçülmüş CTE ayrı şeylerdir. Katsayı seti bağımsız bilimsel inceleme olmadan kopyalanmayacak. [clay-bodies.json](https://github.com/KyaniteLabs/openglaze/blob/ba43d84925bc83610fcf8be0b5fafee27e77210c/ceramics-foundation/data/clay-bodies.json) ürün betimlemeleri içeriyor; tam çamur kimyası veya ölçülmüş dilatometri değildir.

Karar: OpenGlaze teknik/şema karşılaştırması için öncelikli; verisi **UNKNOWN_UPSTREAM_RIGHTS + INCOMPLETE_ANALYSIS_METADATA** nedeniyle production setine alınmadı. MIT kullanım olanağı korunuyor; “MIT kullanılamaz” demiyoruz. Mevcut mimariyi OpenGlaze fork'una dönüştürme kararı alınmadı.

### 3. Materials Project: açık veri içindeki istisnalar

[Resmî release notları](https://docs.materialsproject.org/changes/database-versions) GNoME kökenli yapıların BY-NC lisansını ve ayrı kabul gereğini bildiriyor. Bu nedenle tüm API cevaplarına tek bir CC BY etiketi yazmak uygun değil. Seçilen endpoint/kayıt kökeni ve hesap yöntemi doğrulanmalı. [API başlangıcı](https://docs.materialsproject.org/downloading-data/using-the-api/getting-started) kullanıcı anahtarı gerektiriyor.

Gelecekte sınırlı faz-adayı zenginleştirmesinde kullanabiliriz; DFT veya denge hesabı gerçek fırından çıkmış sırın ölçümü değildir. API istemcisi bir veri lisansı veya sır yüzeyi tahmin modeli sağlamaz.

### 4. JANAF: SRD ile SRM aynı hak kategorisi değil

[JANAF ana sayfası](https://janaf.nist.gov/) SRD 13 olduğunu açıklar. [NIST politikası](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications) SRD derlemelerini diğer NIST eserlerinden ayırır. Önceki dört SRM sertifikasının non-SRD incelemesi buraya taşınmadı. JANAF saf tür termokimyasıdır; çok bileşenli sır eriyiği için hazır CALPHAD solution database değildir. Paket/kullanım hakları ve bilimsel kapsam çözülmeden toplu import yok.

### 5. RRUFF ve Mindat bağlantılarında yeni inceleme gerekiyor

RRUFF.info ana adresi bu aracın erişiminde beklenmedik biçimde Gale Crater veritabanına yönlendi. Bu sonuçla RRUFF'un kapandığını söylemiyoruz. [RRUFF.net](https://www.rruff.net/) ve [PubChem'in RRUFF kaynak kaydı](https://pubchem.ncbi.nlm.nih.gov/source/25653) güncel adres için dayanak sağlıyor; kayıt linklerini körlemesine dönüştürmeyeceğiz.

[Mindat yönetici açıklaması](https://www.mindat.org/mesg-652986.html) API ve NC/ticari ayrımı hakkında 2024 tarihli kanıt sunuyor. Bu eski açıklamayı güncel sözleşme yerine koymadan API kullanım koşullarını yeniden incelemek gerekiyor. “API yok” veya “API kodu açık, verisi de açık” denmeyecek.

## PDF'den aynen devralmadığımız kararlar

1. **Bilgi sınıfları:** Sayfa 2'deki uzun enum mevcut sözleşmemizi değiştirmiyor. CALCULATED/OBSERVED/PREDICTED korunur; measurement, literature, simulation ve AI ayrımı yöntem/nitelik/kaynak alanlarında tutulur.
2. **Crazing örneği:** Sayfa 30'daki risk tahmininin CALCULATED etiketi bizim sistemimiz için uygun değil. Gözlenmemiş fiziksel risk PREDICTED olur; dayandığı aritmetik ayrı CALCULATED sonuç olabilir. Örnekteki confidence rakamları ölçülmüş kalibrasyon sonucu değildir, ürüne taşınmaz.
3. **P0 kapsamı:** Sayfa 32–34'te Materials Project, GlassNet, pycalphad, CTE ve substitution'ın erken entegrasyonu mevcut M4 sınırını genişletir. Araştırma adaylarıdır; otomatik MVP kapsamına alınmadı. İlk web prototipi hâlâ M4.
4. **Lisans yorumları:** GPL ticari kullanım yasağı değildir; dağıtım/uyarlama koşulları değerlendirilir. SaaS, kod kopyalama ve ayrı araç kullanımı aynı hükümle ele alınmaz. Projemizin lisansı seçilmeden GPL kodunu çekirdeğe kopyalamıyoruz.
5. **SciGlass genellemesi:** Rapordaki tek parça ticari/proprietary sınıflandırması bütün tarihsel paketlere ve SciGlass Next'e genellenemez. [Güncel üniversite dokümantasyonu](https://docs.sciglass.uni-jena.de/guide/) ayrı bir hizmeti gösteriyor; mevcut paket lisansı belirsizliğimiz çözülmüş değil.
6. **Faz/sonuç ayrımı:** PhaseObservation altında DFT/AI/CALPHAD yöntemlerini gözlemmiş gibi saklamayacağız. Ölçülmüş faz ile PredictionRun/SimulationRun bağlantısı ayrılır.
7. **Veri akışı:** Reçete girildikten sonra analizleri çözümleyip kimyayı hesaplarız. Termodinamik/ML/AI, zorunlu ardışık zincir değil, uygun girdiler bulunduğunda çalışan isteğe bağlı dallardır. Fiziksel deney, kimya raporu veya AI olmadan da kaydedilebilir.

## Somut devam sırası

| Sıra | İş | Çıktı / kabul kapısı |
|---|---|---|
| 1 — M2 | 36 OpenGlaze kaydını üretici/özgün analiz bağlantısına kadar izlemek | İzinli ve baz/LOI/tarih/ürün kimliği yeterli kayıtlar için yeni kaynak incelemesi; alias'lar sadece aday |
| 2 — M2 | Üretici TDS/CoA ve açık akademik ek veriler; PubChem/CIAAW sınırlı kimlik/sabit seçimi | 10–20 hedef analiz kalite kapısından geçer; sayı uğruna eksik kayıt kabul edilmez |
| 3 — M2 lisans hattı | Glazy/GlazyBench için kullanım kapsamı ve gerekirse izin talebi taslağı | Satın alma veya dışarı mesaj yok; NC araştırması ticari eğitim hattından ayrılır |
| 4 — M3 hazırlığı | OpenGlaze ve LIPGLOSS'un convention/normalizasyon yaklaşımlarını kaynaklı karşılaştırmak | Bağımsız elle hesap ve golden-case planı; dış motor otorite sayılmaz |
| 5 — M6+ | Kendi testleri/gerçek fırın logları; ileride faz/termal veri | Plan/ölçüm ayrımı, yöntem/cihaz kaydı; fırına uzaktan kontrol eklenmez |
| 6 — Sonraki bilimsel faz | MP/pymatgen, pycalphad+uygun TDB, GlassPy, matminer | Ayrı lisans, bağımlılık ve geçerlilik incelemeleri; M4'ü bloke etmez |

## Teslim / doğrulama sınırı

Kaynak envanteri ve karar belgesi güncellendi. Kod, API, DB migration, model, dış servis hesabı veya paket kurulumu yapılmadı. Yeni veri seti kabul edilmedi. Bu inceleme PDF'nin her bilimsel iddiasını veya listelenen tüm sitelerin tüm koşullarını doğruladığı iddiasında değildir. Açık kalan maddeler kayıt bazında takip edilecek.

Mevcut yerel regresyon testleri yeniden çalıştırıldı: 48/48 geçti. Bunlar haricî OpenGlaze/LIPGLOSS motorlarını, lisansların hukuki yeterliliğini veya PDF'deki modellerin bilimsel doğruluğunu test etmez. `git diff --check` temiz.
