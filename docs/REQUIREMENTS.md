# Gereksinim izlenebilirliği

Kaynak: kullanıcı Master Prompt v2. M1 kanıtı tasarım belgesidir; uygulama gereksiniminin yazılması uygulanması anlamına gelmez.

| Gereksinim | M1 karşılığı | Uygulama kabul kapısı |
|---|---|---|
| Koddan önce research/architecture | PROJECT_SPEC, M1_REPORT | M1'de uygulama dosyası yok |
| Hesap/gözlem/tahmin ayrımı | PROJECT_SPEC, PRODUCT_UX, PREDICTION_ENGINE | M4 etiketler; M6 observed; model aşamasında predicted |
| Source/licence provenance | DATA_SOURCES, LICENSES, DATA_MODEL | M2 kabul, M5 replay/export |
| Raw ve normalized ayrı; orijinal kaybolmasın | IMPORT_PIPELINE | M2 manifest/checksum ve dönüşüm lineage |
| API -> export -> file -> ancak izinli scraping | DATA_SOURCES, IMPORT_PIPELINE | Kaynak edinme kapısı |
| Malzeme ürün/lot/analysis version | DATA_MODEL | M2 kayıt, M5 constraints |
| Normalize, base/additions | CHEMISTRY_ENGINE | N-01..04, A-01..03 |
| LOI, nem, baz dönüşümü | CHEMISTRY_ENGINE | B-01..04; mass balance |
| Mol, UMF, ratios | CHEMISTRY_ENGINE | U-01..02, R-01..03; ikinci referans |
| Stull ve limit formula | CHEMISTRY_ENGINE, DECISIONS | Koordinat ayrı; overlay/limits kaynak ve hak doğrulamasına bağlı |
| Cone != tek sıcaklık | FIRING_ENGINE | F-02; conversion henüz kapalı |
| Plan ve actual firing ayrı | DATA_MODEL, FIRING_ENGINE | F-01, M6 integration |
| Unknown material / input validation | API, PRODUCT_UX | 422/partial/E2E |
| Tek kaynak harfi confidence değildir | IMPORT_PIPELINE, DECISIONS | M2 quality vector; ML hazır olma kapısı |
| Framework bağımsız Python | ARCHITECTURE | M3 engine import purity |
| Versioning/reproducibility | DATA_MODEL, API | M5 original replay |
| Recipe comparison/similarity | PREDICTION_ENGINE, ROADMAP | M8 distance/rights/empty state |
| Test sonucu/numune/fotoğraf | DATA_MODEL, PRODUCT_UX | M6 workflow |
| ML'den önce chemistry/data | PREDICTION_ENGINE | Model release bağımsız kapısı |
| Offline model parity | ARCHITECTURE | M7 taslak/rapor; WASM ayrı spike |
| Responsive/erişilebilirlik | PRODUCT_UX, VALIDATION | M4 E2E, M7 device |
| Privacy/auth/cache isolation | ARCHITECTURE, LICENSES | Dış erişim öncesi, M7 tests |
| Safety kaynaklı olsun | PROJECT_SPEC, CHEMISTRY_ENGINE | SDS yönlendirmesi; uygunluk/food-safe sonucu yok |
| Metal/cam/fizik modelleri | SIMULATION | MVP dışı; ayrı bilimsel doğrulama |
| Logical commits / documentation | README, ROADMAP, M1_REPORT | Her milestone teslimi |

## Risk kaydı

| ID | Risk | Kontrol | Sahibi / kapı |
|---|---|---|---|
| RISK-01 | Yanlış hammadde analiziyle doğru aritmetik | Baz/lot/kapsam/provenance | Veri kabulü M2 |
| RISK-02 | Aynı UMF -> aynı yüzey çıkarımı | Malzeme ve fiziksel bağlam | M4 UX, M6 deney |
| RISK-03 | LOI/nem çift düşümü | Açık baz geçişleri/golden cases | M3 |
| RISK-04 | NC/unknown verinin ticari sete karışması | İşlem bazlı hak ve manifest | Her release |
| RISK-05 | Duplicate/run leakage | İlişki grafiği ve grup ayrımı | M8/ML |
| RISK-06 | Fotoğrafta yanıltıcı renk/parlaklık | Çekim yöntemi ve farklı hedefler | M6/CV |
| RISK-07 | Offline stale/conflict | Snapshot ve revision çözümü | M7 |
| RISK-08 | Özel reçete/media sızıntısı | Yetki/cache/EXIF/ayrı AI onayı | Yayın öncesi |
| RISK-09 | Hak iptaliyle replay/model etkisi | Tombstone ve dataset/model lineage | M5/ML |
| RISK-10 | Kullanıcının aşırı veri girişi yükü | Kademeli form, bağlam paylaşımı | M4/M6 pilot |
| RISK-11 | Teorik fixture'ın gerçek veri sanılması | SYNTHETIC_TEST_ONLY, ayrı release | M2/M3 |
| RISK-12 | Gereksiz kapsam/servis büyümesi | Milestone kabul kapıları | Her teslim |

## İlk ürün kararları neden farklı?

İlk brief'teki A–E kaynak harfi yerine kalite boyutları seçildi; üretici adı tek başına doğruluk sağlamaz. Similarity'de UMF/oxide/ratio aynı bilgiyi mükerrer ağırlıklandırmayacak. UNKNOWN material taslakta saklanır; motor exact analysis ister. M1 doküman teslimidir; her milestone'da çalışan web beklentisi M4'ten önce geçerli değildir. Üç değişiklik ve faz adlandırması DECISIONS/PROJECT_SPEC'te açık kaydedildi.
