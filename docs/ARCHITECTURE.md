# Sistem mimarisi

## Bileşen sorumlulukları

```text
Next.js / React / TypeScript
       | same-origin /api/v1
       v
FastAPI routes -> application services
                      |-- authorization / input resolution
                      |-- repositories -> PostgreSQL
                      |-- storage adapter -> local files / future object storage
                      |-- ceramic_engine -> pure scientific results
                      `-- snapshot / provenance / persistence
```

API route'ları HTTP doğrulaması yapar; uygulama servisi yetkiyi kontrol eder, exact analiz sürümlerini çözer, motoru çağırır. Motor ağ, ORM, FastAPI, dosya yolu veya LLM bilmez.

Motor domain nesneleri framework bağımsız typed Python nesneleridir. Pydantic API sınırında kalabilir; API modelinden domain modeline dönüşüm açık yapılır. OpenAPI web istemcisinin kaynak sözleşmesidir; Python domain tipiyle iki yönlü kod üretimi zorunlu değil.

## Stack

| Alan | Karar | Alternatif ve ödünleşim |
|---|---|---|
| Web | Next.js + React + TypeScript | Vite SPA daha hafif olabilir; mevcut yönelim ve gelecekteki public sayfalar için Next.js korunur |
| API | FastAPI + Pydantic | Next.js full-stack daha az runtime; bilimsel Python sınırı için FastAPI seçildi |
| DB | PostgreSQL | SQLite production parity yerine kullanılmayacak |
| ORM/migration | SQLAlchemy / Alembic | Prisma eklemek veri modelinin ikinci sahibini oluşturur |
| Çekirdek | Saf Python, başlangıçta hafif bağımlılıklar | NumPy/SciPy/Pandas yalnızca ihtiyaç çıktığında |
| Test | pytest, gerekli Hypothesis; Playwright | Bilimsel ve tarayıcı testleri ayrı |
| Yerel işletim | İhtiyaç oluştuğunda Docker Compose | M1 kurulum yok; Docker Desktop lisans/ortam uygunluğu kurulum öncesi kontrol edilir |

FastAPI OpenAPI/JSON Schema tabanlı istemci üretimini destekler: [resmî belge](https://fastapi.tiangolo.com/features/). PWA yaklaşımı: [Next.js rehberi](https://nextjs.org/docs/app/guides/progressive-web-apps). Bu kaynaklar projenin tüm mimarisini önermiş sayılmaz.

## Repo hedefi

```text
apps/web/
apps/api/app/{routes,services,repositories,adapters}/
apps/api/migrations/
packages/ceramic-engine/src/ceramic_engine/{domain,chemistry,validation}/
packages/api-client/
contracts/{examples,schemas}/
data/{fixtures,manifests}/
pipelines/{ingestion,validation}/
tests/{scientific,integration,contract,e2e}/
docs/
infra/
```

Klasörler ilgili iş başladığında oluşur. M1'de yalnızca docs ve contracts/examples vardır. Raw/staging/normalized/processed/exports, çalışma depolamasının mantıksal katmanlarıdır; büyük veya özel veri Git'e girmez.

## Ölçek ve performans

İlk kimya hesabı synchronous. Milyon kayıt hedefi başlangıç donanım garantisi değil, ilişkisel tasarımın büyüme yönüdür. İlk indeksler FK, owner/visibility, source identity ve recipe revision erişimleri için; ağır similarity/timeseries indeksleri gerçek sorgu planlarıyla eklenir.

M4 geçici performans kabul hedefi: kayıtlı referans makinede 20 satırlı geçerli reçete, 20 oksit, tek kullanıcı, warm backend; POST /analyses p95 <= 500 ms (ağ hariç), 100 çağrı. Bu ölçülmüş performans değil, doğrulanacak bütçedir. Makine, sürümler, veri ve cold-start ayrı raporlanır. Kullanıcı slider deneyimi yalnızca kimya API ölçümüyle tamamlanmış sayılmaz.

## Offline

M7: uygulama kabuğu, açıkça izinli cache, son kaydedilmiş raporlar, yerel taslak/not. Yeni kimya hesabı online API gerektirir. Taslak değiştiğinde önceki rapor stale olur. Reconnect'te base revision uyuşmazlığı kullanıcı çözümüne gider; sessiz last-write-wins yok.

Pyodide/WASM daha sonra ayrı spike: boyut, ilk açılış, bellek, cihaz ve fixture eşdeğerliği. İkinci TS kimya motoru kurulmaz.

## Güvenlik ve işletim sınırı

- Yerel auth'suz geliştirme yalnızca loopback erişimli; LAN/internet yayını sayılmaz.
- Dış erişimden önce kullanıcı ve object authorization, PRIVATE varsayılanı, rate/size limits, güvenli oturum tasarımı.
- UNLISTED aramada görünmezliktir; özel veri yetkilendirmesinin yerine geçmez.
- Özel API yanıtları public cache'e girmez. Cache anahtarı erişim kapsamı + kanonik input + bilimsel sürümleri içerir.
- Görseller MIME ve içerik doğrulaması, boyut sınırı ve EXIF konum yönetimiyle alınır. Görsel dosyasını URL bilmek erişim yetkisi sağlamaz.
- Log: correlation id, hata kodu, süre, sayımlar. Özel reçete içeriği ve anahtarlar loglanmaz.
- Pilot öncesi yedek, geri yükleme, export/silme ve kaynak geri çekme prosedürü denenir.
- M1 ücretli hizmet, hosting, auth sağlayıcısı veya dış AI servisi açmaz.
