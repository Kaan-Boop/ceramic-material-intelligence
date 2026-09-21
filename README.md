# Ceramic Glaze Lab

Ceramic Material Intelligence Platform — M2 veri altyapısı ve ilk araştırma koleksiyonu

Durum: M1 tamamlandı. **M2 veri altyapısı ve ilk açık veri edinimi çalışıyor; gerçek motor referans seti eksik olduğundan M2 bütünüyle tamamlanmış sayılmıyor.** Web uygulaması ve kimya motoru henüz yok.

Amaç: seramik reçetelerini kaynaklı kimyasal hesaplara ve gerçek deney sonuçlarına bağlayan responsive araştırma uygulaması geliştirmek.

## Buradan başlayın

Yeni: [M2 üçüncü edinme raporu](docs/M2_BATCH3_REPORT.md): 4 yeni açık lisanslı çalışma, 15 araştırma-kapsamlı analiz adayı ve 12 aralık-ortalama genleşme değeri. Analiz adayları karantinada; fizik motoruna veya üretim hesabına aktarılmadı.

Yeni: [Sır–bünye fizik mimarisi ve çalışan termal araştırma prototipi](docs/PHYSICS_RESEARCH.md). Yerel Python CLI serbest büzülme farkı ve OAT duyarlılık üretir; örnekler sentetik, gerilme/çatlama olasılığı/kimyasal reaksiyon çözümü yoktur. M2 yanında izole araştırmadır; kimya motoru veya web MVP'si değildir.

Yeni: [23 kaynaklık arşiv ve fizibilite PDF'sinin kabul incelemesi](docs/SOURCE_REVIEW_2026-09-20.md). Bu inceleme yeni veri import'u veya M3 başlangıcı değildir.

1. [M2 ikinci edinme raporu](docs/M2_BATCH2_REPORT.md), [ilk teslim](docs/M2_REPORT.md), [indirilen kaynaklar](docs/DATA_ACQUISITION.md), [veri kalitesi](docs/DATA_QUALITY.md)
2. [Kararlar ve açık sorular](docs/DECISIONS.md)
3. [Mimari](docs/ARCHITECTURE.md)
4. [Bilimsel hesaplama sözleşmesi](docs/CHEMISTRY_ENGINE.md)
5. [Veri modeli](docs/DATA_MODEL.md)
6. [Yol haritası](docs/ROADMAP.md)

## Tasarım belgeleri

| Belge | Kapsam |
|---|---|
| [PROJECT_SPEC](docs/PROJECT_SPEC.md) | Master Prompt v2'den türetilen kapsam ve yürütme sözleşmesi |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | Stack, bileşen sınırları, dağıtım ve offline yaklaşımı |
| [DATA_MODEL](docs/DATA_MODEL.md) | PK/FK ilişkileri, sürümler, invariants |
| [CHEMISTRY_ENGINE](docs/CHEMISTRY_ENGINE.md) | Base, additions, baz, oksit, mol, UMF, oranlar |
| [FIRING_ENGINE](docs/FIRING_ENGINE.md) | Cone, plan ve gerçek pişirim ayrımı |
| [DATA_SOURCES](docs/DATA_SOURCES.md) | Kaynak envanteri, erişim ve açık araştırmalar |
| [LICENSES](docs/LICENSES.md) | Haklar, kaynak kökeni, yayın/training filtreleri |
| [IMPORT_PIPELINE](docs/IMPORT_PIPELINE.md) | ETL, karantina ve import sayımları |
| [API](docs/API.md) | Önerilen HTTP/domain sözleşmesi |
| [VALIDATION](docs/VALIDATION.md) | Bilimsel golden cases ve test kabul kapıları |
| [PRODUCT_UX](docs/PRODUCT_UX.md) | Kullanıcı akışı ve bilgi etiketleri |
| [SIMULATION](docs/SIMULATION.md) | Senaryo ve optimizasyon sınırları |
| [PREDICTION_ENGINE](docs/PREDICTION_ENGINE.md) | Gelecekteki ML/AI doğrulama kapıları |
| [ROADMAP](docs/ROADMAP.md) | M1–M8 teslimleri ve kapsam |
| [REQUIREMENTS](docs/REQUIREMENTS.md) | Gereksinim–belge–kabul kontrolü eşleştirmesi |

## Kurulum ve geliştirme

M2 intake altyapısı Python 3.12 standart kütüphanesini kullanır. XLSX profili için openpyxl 3.1.5, yeni makale PDF'lerinin kimlik/lisans kontrolü için pypdf 6.10.0 gerekir; `requirements-research.txt` içinde sabittir. Bu ortamda Python 3.12.14 ve mevcut paketler kullanıldı; yeni paket yüklenmedi.

```sh
python -m unittest discover -s tests -v
python -m research.thermal data/fixtures/thermal-synthetic.json
python -m pipelines.ingestion.materials validate data/fixtures/synthetic-materials.json --rights data/fixtures/synthetic-rights.json --purpose INTERNAL_VALIDATION
python -m pipelines.ingestion.materials import data/fixtures/synthetic-materials.json --rights data/fixtures/synthetic-rights.json --purpose INTERNAL_VALIDATION --storage storage/intake
```

Komutlar proje kökünde çalıştırılır. Sistemde `python` yoksa kurulu Python 3.12 executable'ının tam yolu kullanılmalıdır. Ağ üzerinden veri almak ayrı ve bilinçli bir işlemdir; [IMPORT_PIPELINE](docs/IMPORT_PIPELINE.md) komut ve sınırları açıklar.

Planlanan stack: Next.js/React/TypeScript, FastAPI/Pydantic, bağımsız Python `ceramic_engine`, PostgreSQL/SQLAlchemy/Alembic. Sürümler implementasyon başlangıcında destek ve bağımlılık uyumuna göre sabitlenecek; henüz lockfile yok.

Docker, API, database setup ve migration henüz yok. PostgreSQL kalıcılığı M5; ilk web prototipi M4'tür. Mevcut çalışır sistem dosya tabanlı intake, araştırma koleksiyonu araçları ve izole termal araştırma CLI'ıdır.

## Testler

Toplam 80 test: önceki M2 kontrolleri 48, yeni çalışma-adayı kontrolleri 11, termal araştırma 21. Haklar, baz/LOI, tekrar import, hash, tablo yapısı, metadata, eksik değerler, termal integral ve duyarlılık denetlenir. Bunlar UMF motoru veya fiziksel seramik doğrulaması değildir. M3'te kimya/golden/property, M4'te E2E, M5'te PostgreSQL integration/replay testleri uygulanacak.

## Veri ve lisans

`contracts/examples/` altındaki kimlikler ve içerik **sentetik sözleşme örnekleridir**. Gerçek üretici analizi, gerçek deney veya yürütülmüş API cevabı değildir.

On kaynaktan 34 tamamlanmış kaynak/dosya/içerik kaydı (4.608.097 byte) yerel `storage/research/` altında saklandı. Raw veri Git'e alınmaz; checksum/provenance [güncel manifest](data/manifests/research-acquisition-2026-09-21-batch3.json) sürümlenir. Sekiz kaynak CC BY 4.0, GitHub program örnekleri GPL-3.0-or-later, NIST sertifikaları ayrı non-SRD kullanım koşulları altındadır. Lisanslar birbirine veya proje lisansına dönüştürülmez. Dışarı yayın ve AI eğitimi yapılmadı.

`data/reference/study-material-candidates-v1.json`, 15 çalışma-kapsamlı hammadde analiz adayını ve iki S0 pişirim grubu için 12 ortalama TEC değerini içerir. Bu dosya motor girdisi değildir. Analiz bazı, eksik bileşenler ve ölçüm yöntemi sınırları korunur; tüm adaylar araştırma karantinasındadır. `pipelines.ingestion.study_materials` bunları yerel raw arşivden yeniden üretir.

`data/reference/nist-certified-elements-v1.json`, dört SRM'nin Table 1'inden seçilmiş 39 sertifikalı element değerinin küçük, kaynaklı transkripsiyonudur. Bu gerçek referans verisidir; sentetik fixture veya eksiksiz oksit analizi değildir. PDF becerisiyle tablolar görsel olarak incelendi; bağımsız ikinci kişi doğrulaması henüz yapılmadı.

`data/fixtures/` üç sentetik yazılım testidir; gerçek malzeme analizi sayılmaz. Gerçek motor-referans analizi sayısı 0. Projenin kod/belge lisansı henüz seçilmedi; açık kaynak lisansı verilmiş sayılmamalıdır. [LICENSES](docs/LICENSES.md) geçerlidir.

## Sonraki adım

M2 içinde kullanım izni ve analiz bazı açık gerçek ürün referansları tamamlanmalı. M3 kimya motoruna otomatik geçilmez. İlk prototip M4, deney MVP'si M6, pilot v1 M8 sonunda hedeflenir.
