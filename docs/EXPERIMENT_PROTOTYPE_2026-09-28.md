# Deney ve doğrulama prototipi

Yerel adres: http://127.0.0.1:3000/experiments

Mevcut Next.js/FastAPI uygulaması üzerinde geliştirildi; yeni bağımlılık yok.
Yeni API: POST /api/v1/validation/temperature. Python karşılaştırma motorunu
çağırır; arayüzde ikinci hesap motoru yok. OpenAPI ve TypeScript sözleşmesi yenilendi.

## Yapılanlar

- Boş başlangıç, açık sentetik örnek ve kullanıcı beyanlı gerçek veri modu.
- Ortak numune/sır/bünye/pişirim/sensör bağlamı; elle girilen kimlikler.
- Eşleşmiş zaman, model ve ölçüm sıcaklığı tablosu; satır ekleme/silme.
- Bias, MAE, RMSE, en büyük mutlak hata, karşılaştırma grafiği.
- Kaynakları ve input snapshot içeren JSON raporu indirme.
- Girdi değişince önceki raporu kaldırma; geç yanıtın yeni girdiyi ezmesini engelleme.
- Sentetik verinin tür değiştirilerek gerçek veri diye sunulmasını önlemek için tür değişiminde girişleri temizleme.

## Sınırlar

Yeni simülasyon veya fiziksel doğrulama değildir. Reçete kataloğuyla otomatik
bağlantı, kalıcı deney kaydı, rapor import, hesap yönetimi ve belirsizlik
değerlendirmesi yoktur. Sayfa kapanınca girişler kaybolur. Kimlikler kullanıcı
beyanıdır; kaynak ve sensör doğruluğu otomatik onaylanmaz. Tek ortak bağlam
formu ayrı deneylerin eşdeğer olduğunu ispatlamaz.

## Kontrol

282 çekirdek ve 17 API testi geçti. TypeScript kontrolü geçti.
Mevcut Playwright kiti ile görünür/ekran dışı tarayıcıda boş durum, sentetik
örnek, API hesabı, dosya indirme, stale temizleme, hatalı zaman ve 390px
taşma kontrolü geçti; pageerror görülmedi. Masaüstü/mobil ekran görüntüleri
incelendi. Gerçek telefon/Safari testi değildir. Kit .codex konumunda yoktu;
mevcut .claude kopyası kullanıldı. Starlette test istemcisi deprecation uyarısı sürüyor.

## Dağıtım kararı

Şimdilik loopback yerel kullanım. İnternete dağıtım yapılmadı. Vercel veya başka
barındırma öncesi Python backend dağıtımı, kimlik doğrulama, nesne erişim
kontrolü ve kalıcı saklama/yedekleme kararı gerekir. Mevcut host/origin sınırları
gelişigüzel kaldırılmamalıdır.
