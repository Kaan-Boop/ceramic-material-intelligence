# Yerel Glazy arşivi — 3 Ekim 2026

Antigravity altındaki kullanıcı arşivinin altı dosyası `storage/local-glazy/raw/`
altına özgün byte içerikleri korunarak alındı. Kaynak dosyalar değiştirilmedi.
Manifest: `storage/local-glazy/manifest.json`; dosya SHA-256, boyut, yerel aktarım
zamanı, köken ve çalıştırılmış kalite SQL sorgularını içerir. Yerel aktarım tarihi,
GitHub indirme veya analiz tarihi değildir. Upstream commit bilinmiyor.

## Kullanım ve sınırlar

- `python -m scripts.import_local_glazy --source "C:\antigravity p\deneme"`
  tekrar çalıştırılabilir. Aynı dosya tekrar kopyalanmaz; farklı içerik üzerine
  yazılmaz. Harici Python dosyası yalnız köken incelemesi için saklanır, çalıştırılmaz.
- `research.local_recipe_archive.search_recipes` salt okunur, parametreli,
  sayfalanmış yerel araştırma erişimidir. Varsayılan sayfa 20, üst sınır 100.
- API/frontend ve chemistry resolver'a otomatik bağlanmadı. Genel dağıtım,
  eğitim ve motor kabulü kapalı; kayıt bazında kaynak/izin/analiz incelemesi bekliyor.
- Büyük arşiv mevcut storage ignore kuralıyla Git ve frontend paketinden ayrıdır.
  Bu kopya tek başına harici yedek değildir.

## İlk profil

35.478 reçete, 7.319 malzeme kimliği, 236.396 bileşen satırı.
SQLite integrity_check: ok. Reçetesi olmayan bileşen satırı: 0.
Malzeme kimliği çözülemeyen bileşen satırı: 403. Bileşensiz reçete: 20.
Null/negatif miktar: 0; bu test eski aktarıcının sıfıra çevirdiği eksikleri bulamaz.
Sıfır/null SiO2 bulunan reçete: 121; bunların tümü kesin hata değildir.

Eski aktarıcı eksik kimyayı sıfırla doldurur, parse hatalarını sessiz atlar ve
SiO2/Al2O3 kütle oranını kaydeder. Bu alan mol oranı/UMF gibi kullanılamaz.
JSON seçkileri tüm verinin yerine geçmez. Scriptteki seçki limiti ile mevcut JSON
sayısı da farklıdır; mevcut scriptin kesin üretim sürümü olduğu varsayılamaz.

## Sonraki kabul kapısı

Ham YAML'ı güvenli ve hataları görünür parser ile yeniden işle; orijinal alanları,
ID, yazar, lisans ve analiz bazını koru. SQLite ile ID bazında karşılaştır.
403 çözülemeyen bağlantıyı incele; ad benzerliğiyle otomatik birleştirme yapma.
Ardından izin kapsamına uygun yerel arşiv ekranı ve motor için ayrı analiz kabul
listesi oluştur. Teorik dört motor girdisini bu arşivle sessizce değiştirme.

## Ham dosyadan yeniden aktarım — tamamlanan ikinci adım

`pipelines/ingestion/local_glazy.py` ve PyYAML 6.0.3 ile ayrı
`storage/local-glazy/staging/v1.sqlite` üretildi. Eski dosyalar değişmedi.
Tam rapor: `storage/local-glazy/staging/v1.report.json`.

| Tür | Ayrıştırılan kayıt | Boş olmayan Percent Analysis alanı |
|---|---:|---:|
| Recipe | 35.478 | 35.475 |
| Material | 7.319 | 7.308 |
| Analysis | 286 | 286 |

Toplam 43.083 blok alındı, 43.083 ayrıştırıldı, 0 reddedildi; duplicate ID: 0.
Bu kabul yalnız yapısal ayrıştırma kabulüdür, bilimsel veya lisans kabulü değildir.
Reçetelerin 1.390'ının alt türü `Clay Body` ile başlıyor. Dolayısıyla reçete
toplamının tamamını sır olarak adlandırmak yanlış olur.

236.396 bileşen satırı korunuyor. Karşılığı olmayan 403 satır, 46 ayrı hedef
kimliğine karşılık geliyor. Ham arşivde bu hedefler de yok; ad benzerliğiyle
doldurulmadı. Başka reçeteye bağlanan bileşen bulunmadı. Eski SQLite ile Recipe ve
Material ID kümelerinde iki yönde fark yok. Eski aktarıcının atladığı Analysis
türü artık saklanıyor. Percent Analysis alanının varlığı tamlık/doğruluk kanıtı
değildir; baz, ölçüm yöntemi ve haklar hâlâ inceleme bekler.

Her kaydın tam ayrıştırılmış payload'ı, kaynak satırı, kaynak ID'si korunur.
Özgün YAML gzip dosyası byte düzeyinde korunur; YAML tarih tipleri JSON'a ISO
olarak taşınır. Eksik alan eklenmez, eksik oksit sıfır olmaz. `get_staged_record`
kayıtla birlikte arşiv SHA-256 ve parser sürümünü döndürür. Analiz bazı UNKNOWN,
motor uygunluğu false kalır. Ağ/public API erişimi eklenmedi.

Testler: 5 geçti. Sıfır/eksik ayrımı, duplicate YAML anahtarı reddi, çözülemeyen
referans, örnek reçete referansı, mevcut snapshot üzerine yazmama, salt okunur
erişim ve sayfalı parametreli arama kontrol edildi. Tam arşiv çalıştırması ayrıca
tamamlandı; ID 3 için bünye alt türü ve atmosfer alanları okunarak kontrol edildi.

Sıradaki iş: kayıt bazında kaynak/hak ve analiz bazı taraması; ardından yerel
araştırma ekranı. Henüz tarayıcı arayüzüne entegrasyon yapılmadı.
