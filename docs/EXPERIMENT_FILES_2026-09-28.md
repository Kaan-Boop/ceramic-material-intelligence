# Adım 1 — Taşınabilir deney dosyası

Mevcut /experiments ekranına sürümlü JSON taslağı kaydetme/açma eklendi.

## Arşivlenen hesap ve sonuçlar

Deney ekranındaki ölçüm özeti `Doğrulama paneline aktar` ile bağlandığında, aynı
`ceramic-experiment` dosyasının `archived_reports` dizisine `OUTCOME_ASSESSMENT`
kaydı eklenir. Gözlenen numune ile hesaplanan ölçüm özeti karşılaştırması
`OUTCOME_VALIDATION` kaydı olarak eklenir. Bu kayıtlar mevcut dosya sürümünü
değiştirmeden yerel snapshot olarak tutulur; dosyayı açmak arşivi otomatik olarak
bilimsel olarak doğrulanmış hale getirmez. Aynı `input_hash` ikinci kez eklenmez.
Yeni bağımlılık, dış servis veya sunucu saklama alanı yoktur.

## Kapsam

Dosya mevcut deney ekranındaki bünye/sır/uygulama/pişirim kimliklerini,
sensör konumunu, kaynak/yöntem metinlerini, gerçek/sentetik beyanını ve sıcaklık
satırlarını taşır. Bunlar tam reçete, analiz veya pişirim eğrisi içerikleri
değil, henüz elle girilen referanslardır. Reçete masası otomatik bağlanmadı.

Başarılı karşılaştırmalar kendi girdilerini ve motor sürümünü taşıyan raporlar
olarak arşive eklenir. Girdi değişince güncel rapor kaldırılır, arşiv silinmez.
Bu, tüm düzenlemeleri kaydeden bir revision veritabanı değildir.

## İçe aktarma ve mahremiyet

- Dosya türü, sürümü, alanlar, metin uzunlukları, satır sayısı ve 2 MiB boyut sınırı kontrol edilir.
- Eksik taslaklar saklanabilir; hesap için bilimsel doğrulama yine API'dedir.
- Dosya önce önizlenir; mevcut taslağı/arşivi değiştirmek açık düğme eylemi gerektirir.
- Bozuk dosya mevcut girişleri değiştirmez.
- Arşiv raporları güvenilmeyen geçmiş içeriktir; güncel metrik olarak işlenmez.
- Açılışta onay sıfırlanır, güncel rapor boş kalır; yeniden hesap gerekir.
- Açılan dosya sunucuya yüklenmez. Karşılaştırma düğmesine basınca mevcut girdiler yerel API'ye gider.
- İndirilen dosya şifreli değildir. Otomatik kayıt/yedek veya tarayıcı kalıcılığı yoktur.

## Kontrol

TypeScript kontrolü geçti. Dosya roundtrip, arşiv koruma, altı şema reddi,
bozuk JSON ve boyut sınırı kontrolleri geçti. Mevcut görünür/ekran dışı Playwright
kitiyle indirme → yenileme → içe aktarma → yeniden hesap, bozuk dosyada mevcut
girdileri koruma, eski raporu kaldırma, hatalı zaman sırası ve 390px taşma
kontrolleri geçti. Masaüstü ekran görüntüsü incelendi. Gerçek cihaz testi değildir.

## Sonraki adım

Isı modelinin desteklediği malzeme özelliği ve sınır koşullarını inceleyip
ayrı, sürümlü bir senaryo girdisi tasarlamak; uygun olmayan sistemde hesap
üretmemek. Bu teslim yeni fizik modeli veya deneysel doğrulama içermez.
