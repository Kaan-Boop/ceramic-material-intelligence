# Ceramic Glaze Lab

Ceramic Material Intelligence Platform — M2 veri altyapısı ve ilk araştırma koleksiyonu

Durum: M1 tamamlandı. **M2 veri altyapısı ve ilk açık veri edinimi çalışıyor; gerçek motor referans seti eksik olduğundan M2 bütünüyle tamamlanmış sayılmıyor.** Web uygulaması ve kimya motoru henüz yok.

Amaç: seramik reçetelerini kaynaklı kimyasal hesaplara ve gerçek deney sonuçlarına bağlayan responsive araştırma uygulaması geliştirmek.

## Buradan başlayın

1. [M2 teslim ve test raporu](docs/M2_REPORT.md), [indirilen kaynaklar](docs/DATA_ACQUISITION.md), [veri kalitesi](docs/DATA_QUALITY.md)
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

M2 intake/edinme altyapısı Python 3.12 standart kütüphanesini kullanır. XLSX kaynaklarını salt okunur profillemek için ayrıca `requirements-research.txt` içindeki openpyxl 3.1.5 gerekir. Bu ortamda Python 3.12.14 ve openpyxl 3.1.5 ile çalıştırıldı; yeni paket yüklenmedi.

```sh
python -m unittest discover -s tests -v
python -m pipelines.ingestion.materials validate data/fixtures/synthetic-materials.json --rights data/fixtures/synthetic-rights.json --purpose INTERNAL_VALIDATION
python -m pipelines.ingestion.materials import data/fixtures/synthetic-materials.json --rights data/fixtures/synthetic-rights.json --purpose INTERNAL_VALIDATION --storage storage/intake
```

Komutlar proje kökünde çalıştırılır. Sistemde `python` yoksa kurulu Python 3.12 executable'ının tam yolu kullanılmalıdır. Ağ üzerinden veri almak ayrı ve bilinçli bir işlemdir; [IMPORT_PIPELINE](docs/IMPORT_PIPELINE.md) komut ve sınırları açıklar.

Planlanan stack: Next.js/React/TypeScript, FastAPI/Pydantic, bağımsız Python `ceramic_engine`, PostgreSQL/SQLAlchemy/Alembic. Sürümler implementasyon başlangıcında destek ve bağımlılık uyumuna göre sabitlenecek; henüz lockfile yok.

Docker, API, database setup ve migration henüz yok. PostgreSQL kalıcılığı M5; ilk web prototipi M4'tür. Mevcut çalışır sistem dosya tabanlı intake ve araştırma koleksiyonu araçlarıdır.

## Testler

M2: 37 unit test; hak kapısı, baz/LOI kontrolleri, tekrar import, bozuk arşiv, atomik yayın, negatif değer, birim dönüşümü, aralık ve yönlendirme kontrolü. Bunlar UMF motoru veya fiziksel seramik doğrulaması değildir. M3'te kimya/golden/property, M4'te E2E, M5'te PostgreSQL integration/replay testleri uygulanacak.

## Veri ve lisans

`contracts/examples/` altındaki kimlikler ve içerik **sentetik sözleşme örnekleridir**. Gerçek üretici analizi, gerçek deney veya yürütülmüş API cevabı değildir.

Beş kaynaktan 24 kaynak/dosya/içerik kaydı yerel `storage/research/` altında saklandı. Raw veri Git'e alınmaz; yalnızca checksum/provenance [manifest'i](data/manifests/research-acquisition-2026-09-20.json) sürümlenir. Dört kaynak CC BY 4.0, GitHub program örnekleri GPL-3.0-or-later referansıdır; lisanslar birbirine veya proje lisansına dönüştürülmez. Dışarı yayın ve AI eğitimi yapılmadı.

`data/fixtures/` üç sentetik yazılım testidir; gerçek malzeme analizi sayılmaz. Gerçek motor-referans analizi sayısı 0. Projenin kod/belge lisansı henüz seçilmedi; açık kaynak lisansı verilmiş sayılmamalıdır. [LICENSES](docs/LICENSES.md) geçerlidir.

## Sonraki adım

M2 içinde kullanım izni ve analiz bazı açık gerçek ürün referansları tamamlanmalı. M3 kimya motoruna otomatik geçilmez. İlk prototip M4, deney MVP'si M6, pilot v1 M8 sonunda hedeflenir.
