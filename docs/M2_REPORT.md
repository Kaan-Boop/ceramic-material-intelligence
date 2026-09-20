# M2 ara teslimi — veri altyapısı ve açık araştırma koleksiyonu

Tarih: 20 Eylül 2026.

## WHAT WAS BUILT

- Kaynak/hak preflight, kimlik/baz/LOI doğrulayıcı, accepted/quarantined/rejected ayrımı.
- Birebir raw saklama, SHA-256 kontrolü, receipt/manifest, idempotent yerel import ve atomik publish.
- Beş resmi kaynaktan sınırlı dosya edinimi; kaynak başına başarısızlık kaydı, indirilen harici kodu çalıştırmama.
- CSV/XML ve salt okunur XLSX profil araçları; aralık, eşik ve eksik değeri koruyan araştırma temsil biçimleri.
- Üç sentetik fixture, 37 test, kaynak edinme/kalite raporları.

## WHAT WORKS

| Teslim | Gerçek sonuç |
|---|---|
| Kaynak koleksiyonu | 5 kaynak; 24 benzersiz kaynak/dosya/içerik kaydı; 425.581 byte |
| Dosya incelemesi | 19 veri dosyası profillendi; diğerleri metadata/README/config metni |
| UCI | 88 ölçüm satırı; 44 Body + 44 Glaze; 1 negatif hücre bayraklandı |
| Mendeley | 135 bünye + 135 sır satırı; aynı 135 SampleID. Katalog ve türetilmiş özetler ayrıca saklandı |
| Zenodo | 6 tablo + 1 açıklama workbook'u; fotoğraf arşivleri alınmadı |
| Fabris | 7 tablo, 11 araştırma malzemesi satırı, 4 reçete aralık seti; tamamı kimya girdisi bakımından karantinada |
| GitHub | 3 cone adlandırmalı + 2 test programı; 5 fırın modeli değildir |
| Yerel intake | İlk koşu received3/accepted3; tekrar koşu received3/duplicate_skipped3/accepted0 |

Bu sayılar farklı veri birimleridir; toplanıp “toplam güvenilir reçete” diye sunulmaz.

## TEST RESULTS

Python 3.12.14, openpyxl 3.1.5. `python -m unittest discover -s tests -v`: **37 test geçti**.

Kontroller: negatif/nonfinite/boolean/sıfır olmayan toplam, bilinmeyen oksit, LOI ve nem bazı, orijinali değiştirmeme, kaynak kimliği, dışarıdan hak kararı, exact hash review, duplicate ve hak revizyonu, tekrar import, checksum bozulması, lock, başarısız atomik yayın, HTTPS host/redirect, CSV quoting/boş değer, ppm dönüşümü, eşiği/aralığı kesin sayıya çevirmeme.

Gerçek UCI verisi ile bir negatif değer saptandı. Mendeley'in indirilen 6 CSV/README dosyası yayıncının SHA-256 alanıyla eşleştirildi. Diğer dosyalara lokal SHA-256 üretildi; bunlar yayıncı checksum doğrulaması yapıldı demek değildir. Final inventory, 24 başarılı kaynak/dosya içeriğini yerel raw ile yeniden eşleştirdi.

Web E2E, kimya motoru golden/property testleri, PostgreSQL veya fiziksel fırın testi yapılmadı; bu bileşenler henüz yok.

## KNOWN LIMITATIONS

**Gerçek, üretime hazır hammadde analizi sayısı 0.** Kaynaklı araştırma verisi edinildi; baz/ürün kimliği tam, motor için kabul edilmiş küçük set tamamlanmadı. Bu nedenle M2'nin veri edinme altyapısı çalışsa da bilimsel referans-seti kabul kapısı kapanmadı.

- Akademik arşiv ağırlığı arkeolojik pişmiş numunelerde; modern Cone 6 pilotunun yerine geçmez.
- Makaledeki fritler anonim, reçeteler aralıklı; genel feldspar/kaolin adı ticari ürüne eşlenmedi.
- Fırın örneklerinde per-profile birimler doğrulanmadı; çalıştırılamaz öneri olarak tutulur.
- Glazy NC-SA, SciGlass belirsiz lisans, üretici kataloglarında doğrulanmamış yeniden kullanım nedeniyle içerik indirilmedi.
- AI eğitim seti, tahmin, kimya motoru, HTML/Next.js arayüzü yapılmadı. İlk gerçek web prototipi hâlâ M4 hedefidir.
- “Tüm seramik verileri toplandı” iddiası yok; bu ilk edinme dilimidir.

## TECHNICAL DEBT

Erişim/izin kararlarının kayıt bazında UI ile gözden geçirilmesi, schema JSON/Pydantic contract'ı, geniş kaynak adaptörleri ve zengin hata sözlüğü henüz yok. Dosya araçları yerel tek kullanıcı içindir. Raw dosyalar Git dışındadır; taşınabilir yedekleme/saklama politikası pilot öncesi tamamlanmalı.

## NEXT STEP

M2 kapsamında gerçek üretici ürünü veya açık akademik numunesi için **tam ve açık bazlı analizleri** edinmek, kayıt düzeyinde onaylamak ve sabit setini tamamlamak. Ticari lisans satın alımı veya NC kapsamı seçimi gerektiğinde ayrıca kullanıcı kararı alınır. M3'e otomatik geçilmedi.

## Dosyalar

- [Kaynak koleksiyonu ve sonraki edinme planı](DATA_ACQUISITION.md)
- [Kalite bulguları](DATA_QUALITY.md)
- [Provenance ve checksum manifest'i](../data/manifests/research-acquisition-2026-09-20.json)
- [Çalıştırma ve import kuralları](IMPORT_PIPELINE.md)
- [README](../README.md)

Skill etkisi: veri-kalitesi kontrolleri satır/deney ayrımını, negatif değerin korunmasını ve birimlerin açık tutulmasını belirledi. Spreadsheet okuması salt okunur yapıldı; kaynak workbook'lar değiştirilmedi.
