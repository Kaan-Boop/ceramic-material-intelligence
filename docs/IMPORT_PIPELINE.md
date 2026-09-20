# Veri edinme ve import sözleşmesi

M1 sözleşmesi + M2 uygulaması. `materials.py` yerel kontrollü intake; `acquire.py` sınırlı resmi kaynak indirme; `profile_research.py` araştırma dosyası inceleme; `inventory.py` provenance manifest export sağlar. Araştırma arşivi ve kabul edilmiş motor dataset'i ayrı tutulur.

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

## M2 çalıştırma

Python 3.12+ ile proje kökünden:

```sh
python -m pipelines.ingestion.materials validate data/fixtures/synthetic-materials.json --rights data/fixtures/synthetic-rights.json --purpose INTERNAL_VALIDATION
python -m pipelines.ingestion.materials import data/fixtures/synthetic-materials.json --rights data/fixtures/synthetic-rights.json --purpose INTERNAL_VALIDATION --storage storage/intake
python -m unittest discover -s tests -v
```

`validate` storage'a yazmaz. `import` kaynak dosyasını birebir, hak kararını snapshot olarak, disposition ve accepted kayıtları ayrı katmanlarda saklar. CLI exit code: 0 temiz, 2 quarantined/rejected kayıt, 1 dosya/hak/import başarısızlığı. Bozuk JSON veya storage izni olmayan kaynak varsa raw saklamadan durur. İşletmecinin verdiği hak kararının hukuki doğruluğunu yazılım garanti etmez.

```sh
python -m pipelines.ingestion.acquire --storage storage/research --sources uci-583 zenodo-14742972 mendeley-p49ncrb39k fabris-2024 kiln-controller
python -m pipelines.ingestion.profile_research --storage storage/research
```

İlk komut ağ erişimi kullanır; ikinci komut yerel raw dosyalar üzerinde çalışır ve Excel için openpyxl gerekir. Program, R scripti veya upstream Python çalıştırılmaz. Her profil yeni dizine yazılır; konsolda dönen gerçek profil yolu inventory komutuna verilir:

```sh
python -m pipelines.ingestion.inventory --storage storage/research --profile storage/research/profiles/PROFILE_ID --output data/manifests/NEW_INVENTORY.json
```

`PROFILE_ID` ve `NEW_INVENTORY` yer tutucudur; mevcut dosyayı ezmek yerine yeni isim kullanılmalı. İndiricinin kaynağı tamamlanamazsa receipt hata ve alınmış parçaları kaydeder, profiler o koşunun başarısız kaynağını kabul etmez. Sonraki başarılı retry bağımsız receipt ile eklenir. SHA-256 içerik saklaması aynı byte'ları çoğaltmaz; değişen API metadata'sı yeni artifact olabilir.

Yerel intake aynı anda yalnızca tek import çalıştırır; atomik publish öncesi geçici klasör yayımlanmış release değildir. Çökme sonrası stale lock otomatik silinmez; doğrulanıp ele alınmalıdır. Önceki raw/artifact checksum bozuksa devam edilmez. Manifestler imzalı değildir; hash kontrolü güvenilir imza veya kötü niyetli değişikliğe karşı mutlak koruma sayılmaz.

## Bilinen teknik borç

- M2 tek kullanıcı yerel dosya araçlarıdır; uzak istemcilerin yüklemelerine açık API değildir. Yetkilendirme/çok kullanıcılı erişim yok.
- Araştırma kaynakları için genele açık configurable crawler yok; beş kaynak açıkça seçilmiş, boyut/host sınırları sabit.
- İlk acquisition receipt'leri `v1` metadata alanları taşır; inventory exporter eski boolean/koşullu hak etiketlerini açık migration kaydıyla üç durumlu alanlara çevirir. Orijinal receipt'ler değiştirilmez.
- Zengin hata mesajı ve çözüm önerilerinin bütün kodlara sözlük olarak bağlanması henüz yok; mevcut CLI code/path/severity döndürür.
- Veri kabulü için exact record hash inceleme listesi var; inceleme UI'ı yok. Üretici malzemesi kimliği/bazı/sürümü doğrulanmadan `approved_analysis_hashes` listesine eklenmez.
- Baz dönüşümü, molar sabit seti ve UMF bu modülün işi değildir; M3 motoru henüz yok.
