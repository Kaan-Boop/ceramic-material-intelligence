# Karar kayıtları ve açık sorular

Durumlar: ACCEPTED_FOR_M1 = bu tasarım tesliminin başlangıç kararı; PROVISIONAL = gerçek veri/ortamla doğrulanacak; DEFERRED = sonraki aşama. ACCEPTED_FOR_M1 kullanıcı adına ticari veya hukuki onay anlamına gelmez.

| ID | Durum | Karar | Gerekçe / etkisi |
|---|---|---|---|
| ADR-001 | ACCEPTED_FOR_M1 | Next.js + FastAPI + bağımsız Python paketi | UI ve bilimsel hesap sınırlarını korur; iki runtime işletim maliyeti kabul edilir |
| ADR-002 | ACCEPTED_FOR_M1 | PostgreSQL, SQLAlchemy, Alembic | Backend tek veri/migration otoritesi; Prisma eklenmez |
| ADR-003 | ACCEPTED_FOR_M1 | Snapshot ve sürümlü recipe/material analysis | Güncel hammadde analizi eski raporu değiştirmez |
| ADR-004 | ACCEPTED_FOR_M1 | Bilgi türü, yöntem, durum ve nitelik ayrı | Hesap ve tahmin birbirine karışmaz |
| ADR-005 | ACCEPTED_FOR_M1 | Haklar işlem bazlı üç durumlu | UNKNOWN, ALLOWED sayılmaz; kullanıcı verisi kendiliğinden açık değildir |
| ADR-006 | ACCEPTED_FOR_M1 | Tek kimya implementasyonu Python | Offline için ayrı TS motoru yazılmaz |
| ADR-007 | ACCEPTED_FOR_M1 | M4 geçici analiz, M5 kalıcı AnalysisRun | Database kurulmadan gerçek hesap akışı denenebilir |
| ADR-008 | ACCEPTED_FOR_M1 | M1'de uygulama kurulmaması | Teslim bilimsel ve mimari sözleşmedir |
| ADR-009 | ACCEPTED_FOR_M1 | Kalıcılık başladığında gerçek PostgreSQL | SQLite davranışını production gibi test etme riski azaltılır |
| ADR-010 | ACCEPTED_FOR_M1 | İlk motor strict chemistry politikası | Çözülmemiş baz veya eksik analizde güvenilir olmayan tam UMF üretilmez |
| ADR-011 | ACCEPTED_FOR_M1 | Klasik flux kümesi sürümlü | B/Fe/Zn sınıflandırması sessiz değişmez; bkz. CHEMISTRY_ENGINE |
| ADR-012 | ACCEPTED_FOR_M1 | Kaynak türünden tek A–E kalite sonucu türetilmez | Lot, baz, ölçüm ve kapsam ayrı değerlendirilir |
| ADR-013 | PROVISIONAL | Cone 6 oksidasyon pilotu | Fırın/bünye/ürün uygunluğu kullanıcı bilgisiyle sabitlenecek |
| ADR-014 | DEFERRED | Sayısal fiziksel özellik ve ML | İkinci bağımsız kaynak ve fiziksel doğrulama olmadan yayın yok |
| ADR-015 | ACCEPTED_FOR_M1 | HTML export, snapshot raporudur | Sunucusuz yeni hesap ile karıştırılmaz |

## Alternatifler

Next.js full-stack daha az kurulum gerektirir ve yalnızca reçete CRUD/aritmetik için uygundur. Bu projenin bilimsel Python ve optimizasyon hedefleri nedeniyle ayrı backend seçildi. İleride UI değişse de motor korunur. Python servis sınırı aynı kalır; native istemci aynı API'yi kullanabilir.

Mikroservis, Redis, ayrı arama motoru, vektör veritabanı, Kubernetes ve job queue başlangıçta yok. Ölçülmüş gecikme/iş yükü gerektirirse ilgili ADR yeniden açılır.

## Kullanıcı bilgisi bekleyen konular

| ID | Bilinmeyen | Geçici yaklaşım | Hangi işi etkiler? |
|---|---|---|---|
| Q-01 | Kullanıcı henüz ürün envanteri olmadığını bildirdi | İzinli hazır kaynaklar araştırılıyor; genel adları ticari analize eşleme yok | M2 gerçek referans seti seçimi; kullanıcı listesi beklenerek durulmaz |
| Q-02 | Bünye, fırın, maksimum koşullar, witness cone kullanımı | Pilot varsayımı görünür | M6 fiziksel protokol |
| Q-03 | Mevcut reçete/deney dosyaları ve sahiplik | Hiçbir veri alınmış kabul edilmez | M2/M6 import kapsamı |
| Q-04 | Yerel tek kullanıcı mı, dış erişimli pilot mu? | M4 yerel tek kullanıcı hedefi | Yayından önce auth/deployment |
| Q-05 | Kod ve özgün dataset lisansı | Lisans verilmemiş; yayın yok | Dış dağıtım |
| Q-06 | Gerçek telefon/tablet test cihazları | Emülasyon gerçek cihaz sayılmaz | M7 kabul matrisi |

Bu sorular tasarımın tamamlanmasını engellemez. Belirli ticari malzeme kabulü veya dış erişim gibi bağımlı işlemler yanıt gelmeden varsayımla yapılmaz.

## Bilimsel/araştırma açıkları

- Production sabit seti: M2'de CIAAW sürümü, seçilen değerler ve yeniden kullanım kapsamı doğrulanacak. M1 test sabitleri production kaynağı değildir.
- Orton tablolarının uygulamada yeniden dağıtımı ve seçilecek seri/sürüm doğrulanmadı; otomatik dönüşüm yok.
- Stull orijinal deney kapsamının birincil yayından incelemesi tamamlanmadı; bölge overlay'i kapalı.
- Limit formula seti ve yeniden kullanım hakları seçilmedi; başarı yorumu üretilemez.
- Genleşme için ikinci bağımsız model ve katsayı seti seçilmedi; termal çıktı yok.
- Kaynakların tamamında ToS/API/robots/paket lisansı incelemesi bitmiş değil; DATA_SOURCES kabul listesi değildir.
