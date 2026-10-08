# Laboratuvar gözlem kaydı v1

## Amaç ve sınır

Bu sözleşme gerçek numuneden elde edilen gözlem/ölçümleri kaynak, yöntem, birim,
belirsizlik ve koşullarıyla saklar. Kayıt oluşturmak fizik-kimya tahmini değildir;
arşiv de bu değerleri henüz herhangi bir simülasyonla karşılaştırmaz. Mevcut
`/api/v1/validation/outcomes` karşılaştırması yalnızca kendi izinli nicelikleri
ve eşleşen hesaplanmış karşılığı için kullanılmaya devam eder.

Sadece `record_kind=REAL` deney kayıtlarına ölçüm eklenebilir. Sentetik örnekler
ölçülmüş deney verisi gibi etiketlenemez. Kayıtlar immutable ve checksum'ludur;
aynı giriş yeniden gönderilirse yeni kopya yerine aynı kayıt kimliği döner.

## Desteklenen alanlar

| `observable` | `value` / `unit` | İzinli durum | Açıklama |
|---|---|---|---|
| `drying_linear_shrinkage_pct` | Sayı / `%` | `MEASURED`, `REPORTED` | Islak başlangıç boyundan kuru boyuta; eksen ve başlangıç/kuru şartları kaydedilmeli. |
| `firing_linear_shrinkage_pct` | Sayı / `%` | `MEASURED`, `REPORTED` | Kuru boydan pişmiş boyuta; pişirim ve ölçüm koşulları kaydedilmeli. Negatif değer boyutsal büyümeyi gösterebilir. |
| `glaze_runout_distance_mm` | Sayı / `mm` | `MEASURED`, `REPORTED` | Numunedeki işaretli referansa göre ölçülen mesafe; motorun ideal-film çıktısı ile eşdeğer sayılmaz. |
| `water_absorption_mass_pct` | Sayı / `%` | `MEASURED`, `REPORTED` | Yöntem ve numune hazırlığı kaydedilmeli. |
| `gloss_mean_gu` | Sayı / `GU` | `MEASURED`, `REPORTED` | Cihaz/ölçüm geometrisi `method` veya `conditions` içinde tutulmalı. |
| `glaze_surface_class` | Kontrollü kategori / birimsiz | `OBSERVED`, `REPORTED` | Glossy, satin, matte, crystalline, textured vb. |
| `optical_transmission_class` | Kontrollü kategori / birimsiz | `OBSERVED`, `REPORTED` | Transparent, translucent veya opaque. Surface finish ile aynı sınıflandırmaya karıştırılmaz. |
| `glaze_adhesion_assessment` | `ADHERED`, `PARTIAL_PEELING`, `PEELED`, `OTHER` / birimsiz | `OBSERVED`, `REPORTED` | Nitel değerlendirme; sayısal bağ dayanımı değildir. |
| `defect_observation` | Kontrollü kusur adı / birimsiz | `OBSERVED_PRESENT`, `OBSERVED_ABSENT`, `NOT_ASSESSED`, `REPORTED_PRESENT`, `REPORTED_ABSENT` | Yokluk yalnızca adı verilen kusur için değerlendirilmiştir. `NOT_ASSESSED` yokluk anlamına gelmez. |

Kusur sözlüğü: crazing, shivering, crawling, pinholing, blistering, bloating,
dunting, cratering, running, clouding, devitrification, settling, warping,
black core, cracking, peeling ve other. Yüzey sınıfları ve optik geçirgenlik
ayrı kontrollü enum'lar olarak saklanır; serbest etiket taksonomiyi sessizce
genişletmez. Tek numunede birden fazla yüzey/görünüm gözlemi ayrı kayıt olabilir.

## API örneği

```json
{
"observable": "firing_linear_shrinkage_pct",
  "value": 7.4,
  "unit": "%",
  "specimen_id": "tile-01",
  "source_ref": "lab:session-01",
  "method": "dry and fired dimensions; same marked axis",
  "status": "MEASURED",
  "uncertainty": 0.2,
  "uncertainty_kind": "REPEAT_SD",
  "replicate_id": "replicate-01",
  "conditions": {
    "dimension_axis": "length",
    "firing_run_id": "kiln-run-01"
  }
}
```

`uncertainty` verilirse `uncertainty_kind` de verilmelidir (`STANDARD_UNCERTAINTY`,
`EXPANDED_UNCERTAINTY`, `REPEAT_SD`, `INSTRUMENT_RESOLUTION` veya
`REPORTED_UNSPECIFIED`). Bu tek alan hangi hesap yönteminin kullanıldığını
belirtmez; gerekli ayrıntı `method` ve `conditions` içinde açıklanmalıdır.

İstek: `POST /api/v1/experiments/{record_id}/measurements`
Liste: `GET /api/v1/experiments/{record_id}/measurements`

## Bilimsel kullanım kapıları

1. Ölçümü uygun, tanımlı test yöntemiyle al; yöntem ve bağlamı kaydet.
2. Aynı reçete için farklı numuneleri ayrı `specimen_id` olarak sakla; aynı
   numunenin tekrar okumalarını bağımsız numune gibi sayma.
3. Ölçümün hesap karşılığı yoksa raporda yalnızca `OBSERVED` göster.
4. Karşılaştırma eklenecekse ölçüm ve hesap tanımı, birim, geometri, koşul ve
   geçerlilik alanını eşleştiren ayrı bir doğrulama protokolü ve test seti kur.
5. Bu kayıt şeması tek başına tekrar edilebilirlik, kalibrasyon, doğruluk,
   yapışma dayanımı veya tahmin başarısı kanıtı değildir.

Bu sürüm kalıcı uygulama veri tabanı değildir: yerel, içerik adresli JSON arşiv
kullanır. Üretim paylaşımı, kullanıcı yetkisi, yedek ve silme politikası ayrıca
tasarlanmalıdır.
