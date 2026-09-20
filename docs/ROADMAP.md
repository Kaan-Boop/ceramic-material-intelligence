# Geliştirme yol haritası

M1 sonrası her milestone ayrı teslim/geçiştir. Süreler ekip, veri hakları ve cihaz ortamı belirlenmeden kesinleştirilmez. Fiziksel fırın beklemeleri yazılım süresinden ayrılır.

| Milestone | Goal | Inputs | Outputs | Dependencies | Definition of Done |
|---|---|---|---|---|---|
| M1 — Bilimsel sözleşme/mimari | Hesap anlamı ve kapsam | Master Prompt v2, kaynaklar, pilot varsayımı | ADR, PK/FK şema, API/domain örnekleri, validation planı | Araştırma | Kritik varsayımlar görünür; baz/LOI/UMF/oran kararları yazılı; belirsiz kritik veriler kullanılmıyor |
| M2 — Referans seti | Küçük izlenebilir analiz seti | M1, izinli analizler/sabitler, kullanıcı ürün envanteri | Versioned manifest/fixture, validator, import raporu | M1 | Kabul edilen her analizde baz/sürüm/kaynak/hak; karantina; import idempotency; teorik/gerçek ayrımı |
| M3 — Kimya çekirdeği | API/UI bağımsız doğru hesap | M1 sözleşmeleri, M2 seti | Pure Python engine, golden/property testler | M1–M2 | Normalizasyon, additions, baz, mol, UMF ve oran kontrolleri; bağımsız bilimsel referans; sınır durumları |
| M4 — İlk web prototipi | Tarayıcıdan gerçek analiz | M3, OpenAPI ve UI akışı | FastAPI, generated TS client, responsive analyzer | M3 | Gerçek motor; kaynaklı rapor/hatalar; E2E ve performans ölçümü; sahte tahmin yok |
| M5 — Kalıcılık/replay | Sürümlü güvenilir kayıt | M4, data model | PostgreSQL/migrations, recipe revisions, AnalysisRun, export | M4 | Save/open/original replay; yeni analiz eski raporu etkilemiyor; PostgreSQL tests; dış erişim varsa auth |
| M6 — Deney defteri/pişirim | Gerçek fiziksel veri toplama | M5, kullanıcı testleri/protokol | Specimen, uygulama, plan/actual firing, gözlem/fotoğraf | M5 | Tek recipe çok koşul/numune; unknown negatif değil; demo/real ayrımı; kaynak ve media hakları |
| M7 — PWA/cihaz | Atölyede telefon/tablet akışı | M6, cihaz matrisi | Offline taslak/rapor, reconnect conflict, installability | M6 | Offline yeni hesap iddiası yok; duplicate ve cache isolation kontrolleri; gerçek/emulated cihaz raporu |
| M8 — Benzerlik/pilot | Güvenilir karşılaştırma | İzinli reçeteler, M6 deneyleri | Sürümlü chemistry distance, erişim filtreleri, pilot raporu | M6–M7 | Yakınlık olasılık diye sunulmuyor; filtre/empty state; kullanıcı doğrulaması ve backup restore |

## Teslim seviyeleri

M4: ilk çalışan web prototipi. M6: kullanılabilir deney MVP'si. M8: pilot v1. Tek dosyalık HTML gerekiyorsa M5 export, snapshot raporu olabilir; standalone offline hesaplayıcı diye sunulmaz.

## M2 başlangıç taslağı — henüz başlatılmadı

- WHAT: izinli analizler ve sabitler için validator+manifest.
- WHY: motor için izlenebilir küçük referans seti.
- SYSTEM IMPACT: uygulama değil veri sözleşmesi çalışır hale gelir.
- FILES: data/manifests, data/fixtures, pipelines/validation, import raporu ve kaynak kayıtları.
- DEPENDENCIES: gerçek malzeme ürünleri, hak/baz belgeleri, Python ortamı seçimi.
- RISKS: kullanım hakkı ve analiz bazı eksikliği; gerçek veriyi sentetikle doldurma yok.
- EXPECTED OUTPUT: kabul/karantina kayıtları, idempotent validator ve dataset release; haklar netleşmezse sınırlılık raporu.

## Sonraki yetenekler

M8 sonrası: what-if ve deney tasarımı -> düzenli veri/etiket denetimi -> baseline ve bağımsız değerlendirme -> koşullu ML -> kaynaklı AI yorum -> görüntü analizi -> doğrulanmış termal modeller -> metal/cam arayüz araştırması. AI/ML aynı doğrusal zincire zorlanmaz; her modül kendi kanıt kapısına sahiptir.

## Çalışma protokolü

DEFINE -> RESEARCH -> CONTRACT/DATA DESIGN -> IMPLEMENT -> TEST -> SCIENTIFIC VALIDATION -> DOCUMENT -> REVIEW -> COMMIT.

Başlangıç raporu: WHAT WE ARE BUILDING, WHY, SYSTEM IMPACT, FILES, DEPENDENCIES, RISKS, EXPECTED OUTPUT.

Bitiş raporu: WHAT WAS BUILT, WHAT WORKS, TEST RESULTS, KNOWN LIMITATIONS, TECHNICAL DEBT, NEXT STEP.

Hata olursa sebep/log/kapsam incelenir; temiz çözüm gerekçelendirilir. NOT_RUN test PASS sayılmaz. Milestone'u gereksiz yeni özellikle uzatmayız; bağımlı sonraki milestone kendiliğinden başlamaz.
