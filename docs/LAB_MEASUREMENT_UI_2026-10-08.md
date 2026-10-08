# Numune defteri — 8 Ekim 2026

## Çalışan teslim

`/experiments/measurements`: gerçek deney–numune kaydı oluşturma; sayısal ölçüm,
yüzey/optik/tutunma değerlendirmesi ve kusur incelemesi ekleme; kimlikle veya
yer imiyle yeniden açma; kayıtları JSON olarak dışa aktarma.
Deney defterinden `Numune kayıtları` bağlantısıyla ulaşılır.

Ondalık virgül ve nokta desteklenir. Kayıt niteliği otomatik seçilmez.
`NOT_ASSESSED`, kusurun gözlenmediği anlamına gelmez. Okuma kimliği aynı
numunenin tekrar okumalarını ayırır; bağımsız numune sayısını artırmaz.
Kaynak, yöntem ve bağlam görünürdür. Belirsizlik bilinmiyorsa sıfır yapılmaz.

API yanıtları OpenAPI'de tiplidir. Girdiyle dönen arşiv snapshot'ı, checksum,
dosya adı ve içerik kimliği doğrulanır. Aynı ölçümü yeniden göndermek ikinci
kopya oluşturmaz. Checksum kimlik doğrulama veya dijital imza değildir.
Eski ölçüm düzenlenmez; değişen girdi yeni kayıt oluşturur. Düzeltme/geri çekme
ilişkisi henüz yoktur; yanlış kayıt analiz için otomatik seçilmemelidir.

## Saklama ve sınırlar

- Yerel Python API gerekir; salt frontend/Vercel dağıtımı bu dosyaları saklamaz.
- Varsayılan numune arşivi ve ölçüm arşivi uygulama sunucusunun `storage/`
  alanındadır. `EXPERIMENT_RECORD_ROOT` ve `EXPERIMENT_MEASUREMENT_ROOT`
  değişkenleriyle ayrı konum seçilebilir. Git'e veri dosyası eklenmez.
- JSON dışa aktarımı kayıtları taşır; arayüzde geri içe alma henüz yoktur.
- Kaydedilmemiş form girdileri yenilemede kaybolur. Kayıtları açmak için kimlik
  veya bağlantı gerekir; kayıt arama/listeme henüz yoktur.
- Kimya/bünye/pişirim referansları kullanıcı beyanıdır; yabancı anahtarlarla
  çözülmüş kayıtlar değildir. Eksik bağlam uyarılır, tahmin edilmez.
- Liste kronolojik kayıt defteri değildir; okuma kimliklerini ve tarih/koşul
  notunu kullan. Gelecek sürümde ayrı ölçüm zamanı ve kayıt sırası gerekli.
- Mevcut `/observations` arşivi korunur. `/measurements` genişletilmiş sözleşmedir;
  eski veriler otomatik taşınmaz ve iki arşiv birleştirilip çift sayılmaz.
- Bu teslim tahmin, kalibrasyon veya fiziksel doğruluk iddiası eklemez.
- Kimlik doğrulama, kullanıcı izolasyonu ve kalıcı üretim depolaması olmadan
  bu yerel servis internete açılmamalıdır.

## Doğrulama

Projenin mevcut `storage/prototype/environment/Scripts/python.exe` ortamında
FastAPI ve gerekli paketler mevcut. Genel Python ortamındaki eksiklik bu
proje ortamının çalışmadığı anlamına gelmiyor. Pydantic union üzerindeki
`strict=True` kısıtı API açılışını engelliyordu; kısıt her union üyesine taşındı.

- API testleri, ölçüm round-trip, idempotency ve sayı tiplerini kapsar.
- Birim testleri arşiv kimliğini, içerik bütünlüğünü ve bilimsel durum ayrımını kapsar.
- Next.js üretim derlemesi ve TypeScript denetimi çalıştırıldı.
- Playwright gerçek tarayıcıyla masaüstü ve 390 px mobil viewport kontrolü yapıldı.
  Gerçek telefon/iPhone cihaz testi değildir.
- Tarayıcı senaryosu: oluştur → virgüllü değer → üç ayrı gözlem → HTTP 503
  sonrası yeniden gönder → dışa aktar → yenile → kimlikle yeniden aç.
- QA kayıtları ayrı `storage/qa-notebook-*` kökünde tutuldu; gerçek deney yapılmadı.

Tarayıcı testi yalnızca ayrı QA arşivlerine yönlendirilmiş API ile çalıştırılmalı.
Bu ayarı yaptıktan sonra PowerShell'de:

```powershell
$env:CERAMIC_QA_ARCHIVE_CONFIRMED='1'
node scripts/test-lab-measurements-browser.cjs
```

Bu bayrak sunucu konumunu kendi doğrulamaz; operatörün izolasyonu doğruladığını
belirtir. Test verisi üretim/gerçek araştırma arşivine alınmamalıdır.

## İlişkili ısıl karşılaştırma

Önceden bekleyen `/api/v1/simulations/thermal-1d/compare` sözleşmesi de
OpenAPI'ye alındı. Hesaplanan numune sıcaklığı sensör konumu, ortak zaman
başlangıcı ve eşleşen bağlam ile karşılaştırılır. Zaman interpolasyonu açık
izin ve aralık sınırı ister; ekstrapolasyon yapılmaz. Sentetik ve gerçek veri
karıştırılmaz. Bias/MAE/RMSE raporlanır ama fiziksel doğrulama statüsü
`NOT_ESTABLISHED` kalır. Bu numune ölçüm ekranı henüz bu uca bağlı değildir.

## Sonraki bilimsel adım

Tek tanımlı numune için gerçek sensör eğrisi, ölçüm yöntemi/kalibrasyon bilgisi
ve bünye özellikleriyle ısıl karşılaştırma yap. Kabul sınırını ölçüm sonuçlarını
görmeden tanımla. Ardından uygun model–ölçüm çiftlerini deftere bağla.
Yüzey/tutunma gözlemlerini mevcut olmayan hesaplarla karşılaştırıp yüzde üretme.
