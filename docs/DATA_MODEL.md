# İlişkisel veri modeli — taslak v0.1

PK birincil anahtar, FK dış anahtar. ID'ler API'de opaque string; production persistence'da UUID önerilir. Bu belge SQL migration değildir.

## Temel ilişkiler

```text
Material -> MaterialLot
    `----> MaterialAnalysis -> MaterialAnalysisOxide -> Oxide
                       |                              `-> OxideConstant
                       v
                  SourceRecord -> RightsPolicy -> License

Recipe -> RecipeRevision -> RecipeIngredient -> MaterialAnalysis
                 |               (taslakta nullable)
                 v
             AnalysisRun -> AnalysisRunMaterial -> MaterialAnalysis

ComparisonRun -> AnalysisRun / RecipeRevision
             `-> ExternalReferenceSnapshot -> Source / license manifest

Experiment -> TestSpecimen -> Observation
                   |        `-> ImageAsset
                   |-> RecipeRevision
                   |-> ClayBodyRevision
                   |-> ApplicationRecord
                   `-> FiringRun -> FiringSample
                            `-> FiringScheduleRevision -> FiringSegment
```

## Tablo taslağı

| Entity | PK / FK | Önemli alanlar ve kısıtlar | Aşama |
|---|---|---|---|
| User | PK id | identity_subject, durum; kimlik sağlayıcısı seçimi açık | M5/dış erişim öncesi |
| Material | PK id | canonical_name, manufacturer, product_code, type, theoretical, country | M2 veri/M5 SQL |
| MaterialAlias | PK id; FK material_id | alias, language; isim tek başına unique değil | M2/M5 |
| MaterialLot | PK id; FK material_id | lot_code, supplier, received_at; gerçek olmayan lot oluşturulmaz | M5 |
| MaterialAnalysis | PK id; FK material_id, lot_id?, source_record_id | version, basis, coverage, LOI/nem ve bazları, method, analysis_date, review_status, checksum | M2/M5 |
| MaterialAnalysisOxide | PK (analysis_id, oxide_id); iki FK | wt_pct?, qualifier, lower/upper?, uncertainty?, detection_limit?, reported_as | M2/M5 |
| MaterialProperty | PK id; FK material_id, lot_id?, source_record_id | property_key, value, unit, method, temperature_interval? | M5+ |
| Oxide | PK id; unique formula | formula, atom counts; fiziksel rol burada sabitlenmez | M2/M5 |
| ConstantSet | PK id; FK source_record_id | version, selection/rounding policy, checksum | M2/M5 |
| OxideConstant | PK (oxide_id, constant_set_id); iki FK | molar_mass_g_mol; >0 | M2/M5 |
| UMFConvention | PK id | version, flux member ilişkileri, report groups, definitions | M3/M5 |
| Recipe | PK id; FK owner_id, current_revision_id? | name, visibility; varsayılan PRIVATE | M5 |
| RecipeRevision | PK id; FK recipe_id, parent_revision_id? | revision, immutable content hash, original input; unique(recipe_id, revision) | M5 |
| RecipeIngredient | PK id; FK revision_id, analysis_id? | order, unresolved_label?, amount, unit, role, amount_basis | M5 |
| AnalysisRun | PK id; FK owner_id, recipe_revision_id?, dataset_snapshot_id? | input snapshot/hash, engine/constants/convention/policy versions, result schema, results JSONB | M5 |
| AnalysisRunMaterial | PK (run_id, analysis_id); iki FK | exact checksum; kaynak etkisi sorguları | M5 |
| ComparisonRun | PK id; FK owner_id?, internal_analysis_run_id?, recipe_revision_id? | internal/external engine versions, external source snapshot, input hash, comparison result JSONB, status (`COMPARED`/`PARTIAL`), limitations | M5 |
| ExternalReferenceSnapshot | PK id; FK comparison_run_id | source name, repository ref, archive checksum, recipe-name mapping, raw report JSONB, retrieved_at | M5 |
| ClayBody | PK id; FK owner_id? | manufacturer/product, name | M6 |
| ClayBodyRevision | PK id; FK clay_body_id, analysis_id? | version, lot/reference; fired properties Observation/Measurement üzerinden | M6 |
| Experiment | PK id; FK owner_id | question, plan, controls, replicate plan; ilk API köprüsü `experiment-record-v1` ile yerel immutable snapshot | M6 |
| ApplicationRecord | PK id | method, dry_thickness?, unit, measurement_method, coats?, suspension, drying | M6 |
| Kiln | PK id; FK owner_id | model, energy, sensor/calibration refs | M6 |
| FiringSchedule | PK id; FK owner_id | name | M6 |
| FiringScheduleRevision | PK id; FK schedule_id | revision, immutable plan | M6 |
| FiringSegment | PK id; FK schedule_revision_id | order, RAMP/HOLD/NATURAL_COOL, hedef, hız/süre | M6 |
| FiringRun | PK id; FK kiln_id, schedule_revision_id? | started_at, ended_at?, operator, actual context | M6 |
| FiringSample | PK id; FK firing_run_id | elapsed_seconds, temperature_C, sensor/location, provenance | M6 |
| ConeObservation | PK id; FK firing_run_id, specimen_id? | system, code string, cone_type, bend, location, image_id? | M6 |
| TestSpecimen | PK id; FK experiment_id?, recipe_revision_id, clay_revision_id?, application_id?, firing_run_id? | owner, kiln_position, replicate, demo flag | M6 |
| PropertyDefinition | PK id | version, quantity, allowed unit/method, observation domain | M6 |
| Observation | PK id; FK specimen_id, property_definition_id, observer_id?, source_record_id? | value, unit, method, assessed_at, assessment_status, uncertainty | M6 |
| ImageAsset | PK id; FK specimen_id, owner_id, rights_policy_id | storage_key, checksum, capture metadata, EXIF policy | M6 |
| Source | PK id | name, type, homepage, publisher | M2/M5 |
| SourceRecord | PK id; FK source_id, rights_policy_id, ingestion_run_id? | exact URL, authors, date, retrieved_at, raw checksum/location, parser version | M2/M5 |
| License | PK id | identifier, version, URL, text hash; unknown lisans ayrı durum | M2/M5 |
| RightsPolicy | PK id; FK license_id? | attribution/share-alike ve işlem bazlı ALLOWED/DENIED/UNKNOWN, evidence | M2/M5 |
| IngestionRun | PK id; FK source_id | manifest hash, pipeline version, terminal state, sayımlar | M2/M5 |
| RecordRelationship | PK id; iki FK SourceRecord | SAME_CONTENT / DERIVED_FROM / POSSIBLE_DUPLICATE, method, review | M2/M5 |
| DatasetSnapshot | PK id | immutable manifest, checksum, purpose, release status | M2/M5 |
| DatasetSnapshotMember | PK (snapshot_id, source_record_id); iki FK | content checksum, rights snapshot reference | M2/M5 |
| Consent | PK id; FK user_id | scope, granted_at, revoked_at?, policy version | Dış paylaşım/eğitim öncesi |

`Surface`, `Defect`, `Atmosphere` sürümlü kontrollü sözlüklerdir. Surface tek kategori değildir: gloss, opacity, texture, crystallinity ayrı property tanımlarıdır. Renk kullanıcı etiketi ve cihaz ölçümü olarak ayrılır; ölçülen renk varsa color space/illuminant/observer saklanır. `Measurement`, Observation'ın ölçüm yöntemi ve birim zorunlu uzmanlaşmış biçimidir; aynı ölçümü iki tabloda çelişkili saklamayız.

ModelVersion/PredictionRun/Interpretation ileri aşamada eklenir; şu anda migration veya placeholder servis yok.

## Zorunlu invariants

1. Analizin lot'u varsa aynı Material'a ait olmalı: composite FK veya eşdeğer DB constraint; yalnızca UI kontrolü değil.
2. Recipe.current_revision ve parent_revision aynı Recipe içinde olmalı; cross-recipe parent yerine açık derivative relationship kullanılır.
3. Yayınlanmış RecipeRevision, kabul edilmiş analiz ve AnalysisRun bilimsel içeriği update edilmez. Düzeltme yeni sürüm ve supersedes ilişkisi üretir.
4. Taslak ingredient: analysis_id veya unresolved_label bulunur. Hesap başlatılırken bütün aktif ingredient'ler çözülmüş olmalı.
5. Bir reçete birden çok numuneye bağlanır. Numune bir recipe revision'a bağlıdır; üst üste iki sır uygulaması MVP dışıdır, tek recipe olarak gizlenmez.
6. FiringRun, plan revision'ını referans eder; actual veri planla doldurulmaz. Natural cool duration bilinmiyorsa null.
7. Fiziksel ilişki girdisi bilinmiyorsa taslak numune kaydı engellenmez; sonuç kapsamı PARTIAL ve missing_reason ile görünür.
8. OBSERVED absence/presence ile NOT_ASSESSED/MISSING ayrıdır. Crazing zamanla değerlendirilebilir; observed_at/assessed_at korunur.
9. `LOI`, `moisture`, toplam element eşdeğerleri bağımsız oksit gibi çift sayılmaz.
10. Unique source identity + source content hash import idempotency sağlar; içerik değişmişse eski kayıt üzerine yazılmaz.
11. Recipe visibility, bağlı AnalysisRun ve fotoğraf erişimini otomatik genişletmez; erişim kapsamı birlikte kontrol edilir.
12. Kullanıcı silmesi veya lisans iptali: gerektiğinde içerik silinir, kişisel veri taşımayan tombstone/audit kalabilir. Silinen girdiler için replay UNAVAILABLE olur; sahte yeniden üretilebilirlik iddiası yok.

## Değer türleri

Orijinal ondalık girdiler decimal/text biçimiyle korunur; hesap float/tolerance politikasına göre çalışır. Timestamps UTC, UI yerel saat. Fiziksel miktarlar değer+birim+referans koşullarıyla. Missing value null ve neden; ölçüm belirsizliği bilinmiyorsa null.

Sık aranan kimya/kimlikler ilişkisel. Değişken capture metadata ve immutable rapor payload'ı JSONB olabilir; schema_version zorunlu. İlk uygulamada tüm bilgiyi genel EAV modeline taşımayız.

## Provenance zinciri

AnalysisRun -> RecipeRevision / inline input snapshot -> exact MaterialAnalysis -> SourceRecord -> raw checksum + RightsPolicy; ayrıca constants/convention/engine sürümleri.

ComparisonRun aynı snapshot için kendi `AnalysisRun` sonucunu ve harici hesaplayıcı raporunu ayrı tutar. Harici rapor üretim kimyasının üzerine yazılmaz; repository/ref/checksum ve isim eşlemesi saklanmadan sayısal fark yeniden üretilebilir kabul edilmez. Harici kaynağın erişimi veya lisansı kaybolursa eski ComparisonRun raporu korunabilir, ancak yeni replay durumu `UNAVAILABLE` olabilir.

Hash tek başına reproducibility sağlamaz: girdinin izinli kopyası ve eski motor/policy sürümünün çalıştırılabilir artifact'i saklanmalıdır. Replay iki modu ayırır: ORIGINAL_VERSION ve LATEST_ENGINE_REANALYSIS. İkincisi yeni AnalysisRun oluşturur.
