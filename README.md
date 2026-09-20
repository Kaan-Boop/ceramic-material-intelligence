# Ceramic Glaze Lab

Ceramic Material Intelligence Platform — M1 tasarım teslimi

Durum: **M1 — bilimsel sözleşme ve mimari**. Bu depo henüz çalışan uygulama, kimya motoru veya kabul edilmiş malzeme dataset'i içermez.

Amaç: seramik reçetelerini kaynaklı kimyasal hesaplara ve gerçek deney sonuçlarına bağlayan responsive araştırma uygulaması geliştirmek.

## Buradan başlayın

1. [M1 teslim raporu](docs/M1_REPORT.md)
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

M1 yalnızca Markdown tasarım belgeleri ve JSON sözleşme örnekleridir; runtime veya paket kurulumu gerekmez. Git ile sürümlenir.

Planlanan stack: Next.js/React/TypeScript, FastAPI/Pydantic, bağımsız Python `ceramic_engine`, PostgreSQL/SQLAlchemy/Alembic. Sürümler implementasyon başlangıcında destek ve bağımlılık uyumuna göre sabitlenecek; henüz lockfile yok.

Çalıştırma, Docker, database setup, migration ve import komutları henüz yoktur. Uygulama oluşmadan çalışırmış gibi kurulum komutu sunulmuyor. PostgreSQL kalıcılığı M5; tekrarlanabilir dosya tabanlı referans seti M2; ilk web prototipi M4'tür.

## Testler

M1 kontrolü: belge bağlantıları, JSON örneklerinin okunabilirliği, bilimsel örnek aritmetiği ve sözleşme tutarlılığı. Bunlar motor unit testleri değildir. M3'te pytest/golden/property, M4'te E2E, M5'te PostgreSQL integration/replay testleri uygulanacak.

## Veri ve lisans

`contracts/examples/` altındaki kimlikler ve içerik **sentetik sözleşme örnekleridir**. Gerçek üretici analizi, gerçek deney veya yürütülmüş API cevabı değildir.

Bu depoya üçüncü taraf dataset'i, özel reçete, fotoğraf veya model ağırlığı eklenmemiştir. Projenin kod/belge lisansı henüz seçilmedi; açık kaynak lisansı verilmiş sayılmamalıdır. Üçüncü taraf içerik hakları kendi koşullarına tabidir; [LICENSES](docs/LICENSES.md) geçerlidir.

## Sonraki adım

M1 sonrası **M2'ye ayrı geçiş** gerekir. M1 onayı bütün yol haritasını geliştirme veya veri indirme yetkisi değildir. İlk prototip M4, deney MVP'si M6, pilot v1 M8 sonunda hedeflenir.
