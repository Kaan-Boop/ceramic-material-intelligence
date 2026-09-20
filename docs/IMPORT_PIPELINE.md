# Veri edinme ve import sözleşmesi

M1 tasarımı; ağ erişimi yapan importer yazılmadı. M2 validator/import işleri bu kapılara uyar.

## İş akışı

1. **REGISTER**: kaynak, amaç, kayıt türü ve hak kanıtı. API -> public export -> lisanslı repo -> indirilebilir CSV/JSON/PDF -> ancak uygunluğu doğrulanırsa scraping.
2. **EXTRACT**: yalnızca izinli yöntem; domain'e uygun rate limit ve Retry-After; 403/429/robots/ToS kısıtlarını aşma yok. Hesap veya ödeme açılması ayrı yetki gerektirir.
3. **RAW**: orijinal artifact, UTC retrieval timestamp, exact URL, media type, SHA-256, response/license evidence; değişmez ve erişim kontrollü saklama.
4. **PARSE**: satır/değer konumu, original text, unit ve parser_version. OCR belirsizliği review flag; virgül ve trace tahmin edilmez.
5. **NORMALIZE**: isim alias önerisi, standard unit, explicit basis; original korunur. Genel isimden ticari ürün otomatik seçilmez.
6. **VALIDATE**: kimlik, ürün/lot, oxide sözlüğü, baz, LOI/nem, kapsam, toplam, haklar.
7. **REVIEW**: accepted / quarantined / rejected. Reason code zorunlu. QUARANTINED production dataset'e girmez.
8. **DEDUPLICATE**: içerik hash'i ve source id exact duplicate; benzer isim/kimya yalnızca aday. Farklı kaynak kökenleri silinmez; relationship oluşturulur.
9. **RELEASE**: amaç/hak filtresi, immutable dataset manifest, kabul raporu ve sürüm. Eksik/unknown analizi prod release'e alma yok.

## İdempotency

Kaynak, external record id, raw checksum ve pipeline sürümü kaydedilir. Aynı raw/policy ile tekrar import logical record çoğaltmaz. Yeni raw içerik eski analizi update etmez; yeni sürüm ve ilişki açar. Parser/policy değişikliği aynı raw'dan yeni normalization revision üretebilir; lineage korunur.

Raw artifact file path'i ve manifest kimliği ayrı. DB/storage transaction yarıda kalırsa IngestionRun FAILED/PARTIAL olarak kalır, accepted release oluşmaz; tekrar deneme güvenli olmalı.

## Rapor sayımları

`received = accepted + quarantined + rejected + duplicate_skipped` terminal partition'ıdır. `duplicates`, `unknown_materials`, `missing_chemistry`, `license_conflicts` tanı sayımlarıdır; birbirleriyle örtüşebilir ve received'a tekrar eklenmez. Parse edilemeyen dosya/satır sayısı ayrı raporlanır; tanınamayan kayıt sayısı uydurulmaz.

Her hata: code, source_record_ref/row, field, severity, message, suggested_resolution. Raw reçete içeriği genel log'a basılmaz.

## Kalite değerlendirmesi

Tek kaynak harfi yerine provenance_verified, basis_known, coverage, lot_specificity, analysis_age, measurement_method, uncertainty_known, duplicate_status ve review_status tutulur. Manufacturer ve academic `source_type` değerleridir; doğruluk derecesi değildir.

A–E özeti ileride kullanılacaksa kuralı açıklanmış, sürümlü ve görev özelinde olmalı; kaynak harfi model güveni veya ağırlığına doğrudan çevrilmez.

## M2 kabul kapısı

- Her kabul edilen malzeme analizi kaynak/baz/sürüm/kapsam/hak bilgisi taşıyor.
- Bilinmeyen alanlar karantinaya gidiyor; bilimsel değerler sessiz düzeltilmiyor.
- Duplicate kaynak kayıtları görünür ilişkiyle korunuyor.
- Tekrar import çoğaltmıyor; rapor sayımları tutarlı.
- Sentetik/theoretical fixture'lar gerçek üretici ve OBSERVED deney diye görünmüyor.
- 10–20 analiz başlangıç hedefi; hak/kalite kapıları sayı için gevşetilmiyor.
