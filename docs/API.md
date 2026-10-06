# API ve domain sözleşmesi — taslak v0.1

Bu belge uygulanmış servis veya tam OpenAPI şeması değildir. JSON dosyaları sentetik örneklerdir; contract testleri M3/M4'te oluşturulacak. Başlangıç: same-origin JSON REST `/api/v1`.

## Endpoints ve aşama

| Endpoint | Davranış | Milestone |
|---|---|---|
| GET /materials | İzinli ürün listesi; query/filter/cursor | M4 |
| GET /materials/{id} | Ürün kimliği ve analiz sürümleri | M4 |
| GET /library | Yerel araştırma kütüphanesi; teorik, ürün dizini ve karantina kayıtlarını durum/izin alanlarıyla döndürür | M4 |
| GET /material-analyses/{analysis_id} | Exact local analysis record, provenance and engine eligibility | M4 |
| GET /oxides | Desteklenen oksitler ve sabit/policy metadata | M4 |
| POST /analyses | Geçici hesap; `persist=false` varsayılanı | M4 |
| POST /simulations/capabilities | Genel senaryoyu doğrular; hedef çıktılar için AVAILABLE/PARTIAL/UNAVAILABLE kapısı döndürür, fiziksel sonuç üretmez | M4 |
| POST /simulations/chemistry | Senaryo katmanlarının açık reçetelerini ayrı ayrı kuru baz oksit/mol/UMF raporuna bağlar; firing veya yüzey sonucu üretmez | M4 |
| POST /simulations/thermal-1d | Açık termal özellikler + ayrı gaz/duvar tarihçesiyle inert katmanlı plakanın zaman/konum sıcaklığını ve enerji bilançosunu hesaplar | Yerel araştırma |
| POST /references/openglaze/umf | Yerel olarak etkinleştirilmiş OpenGlaze CLI çıktısını harici karşılaştırma olarak döndürür; çekirdek sonucu değiştirmez | Araştırma |
| POST /references/openglaze/compare | Exact yerel analiz snapshot’ı ile OpenGlaze UMF/SiO₂:Al₂O₃ çıktısını oksit bazında karşılaştırır; doğruluk sıralaması üretmez | Araştırma |
| POST /references/openglaze/replay | İndirilen `comparison-run-v1` snapshot’ının hash ve fark tablosunu yeniden kontrol eder; OpenGlaze’i tekrar çalıştırmaz | Araştırma |
| POST /references/openglaze/runs | Bir `comparison-run-v1` snapshot’ını yerel immutable arşive idempotent biçimde kaydeder | M5 köprüsü |
| GET /references/openglaze/runs/{comparison_id} | Yerel arşivden snapshot’ı checksum ve replay kontrolüyle döndürür | M5 köprüsü |
| POST /validation/outcomes | Ölçülmüş veya raporlanmış numune gözlemlerini hesaplanmış outcome bölümleriyle bağlar; kabul/başarı onayı vermez | M6 başlangıcı |
| POST /validation/runs | Bir `experiment-validation-v1` raporunu yerel immutable arşive idempotent biçimde kaydeder | M6 köprüsü |
| GET /validation/runs/{run_id} | Deney doğrulama raporunu checksum kontrolüyle döndürür | M6 köprüsü |
| POST /outcomes/assess | Ölçülmüş/reported tartım veya gloss okumalarından deterministik sonuç özeti üretir; yüzey tahmini yapmaz | M6 ölçüm köprüsü |
| POST /experiments | Deney–numune bağlamını immutable yerel kayda alır; eksik bağlamı doldurmaz, `missing_context` olarak bildirir | M6 kayıt köprüsü |
| GET /experiments/{record_id} | Deney–numune snapshot’ını checksum kontrolüyle döndürür | M6 kayıt köprüsü |
| POST /experiments/{record_id}/observations | Bir gloss/porozite/su emmesi gözlemini specimen kaydına immutable biçimde bağlar | M6 ölçüm kaydı |
| GET /experiments/{record_id}/observations | Deney kaydına bağlı checksum doğrulanmış gözlemleri listeler | M6 ölçüm kaydı |
| POST /analyses, persist=true | Yeni immutable AnalysisRun | M5 |
| GET /analyses/{id} | Yetkili kaydedilmiş sonuç | M5 |
| GET/POST /recipes | Kayıtlar / yeni Recipe+ilk revision | M5 |
| GET /recipes/{id} | Kimlik, güncel revision ve kaynak bağlantıları | M5 |
| POST /recipes/{id}/revisions | Yeni revision; base revision precondition | M5 |
| GET/POST /tests | Numune + temel context/gözlem akışı | M6 |
| GET /recipes/{id}/similar | Yetkili exact revision'a göre yakınlık | M8 |

Unsupported endpoint route açılmaz. `/simulate`, `/predictions`, `/ai-explanations` bu sürümde yok.

## Genel simülasyon kapasite isteği

`POST /api/v1/simulations/thermal-1d` ayrı ve uygulanmış bir araştırma
endpoint'idir. Gövde `{"case": ...}`; tam sözleşme ve çalıştırılabilir örnek
[1B termal model](KILN_THERMAL_1D.md) ve
[sentetik fixture](../data/fixtures/kiln-thermal-1d-synthetic.json) içindedir.
Malzeme adı/UMF üzerinden termal özellik tahmin etmez. Yanıt
`kiln-thermal-1d-report-v1`, `PREDICTED / DETERMINISTIC`, tam girdi snapshot'ı,
mesh, zaman serisi ve enerji bilançosu içerir. Fiziksel doğrulama yapılmadı;
belirsizlik `null`. Eksik özellik, geçerlilik aşımı ve çözücü yakınsamama
durumları ayrı hata kodlarıyla 422 döner. Faz, reaksiyon, sinterleşme ve kusur
olasılıkları bu endpoint'te de mevcut değildir. Web arayüzü henüz çağırmaz.

`POST /api/v1/simulations/capabilities` gövdeyi, engobe/sır/katkı katmanlarını,
bisque/final firing programını, geometriyi ve kullanıcının `requested_outputs`
hedefini alır. Malzeme özellikleri istemciden kabul edilmez; sunucu exact
`analysis_id` değerlerini yerel kütüphaneden çözerek `material_resolutions` ve
`property_inventory_source` alanlarını üretir. Yanıtta senaryo `input_hash`
değeri ve her hedef için durum bulunur. Bu endpoint henüz
`melt_fraction`, sıcaklığa bağlı `viscosity`, renk, yüzey veya kusur olasılığı
hesaplamaz; bu hedefleri `UNAVAILABLE` döndürür.

`/library` içindeki `RESEARCH_ONLY` ve `QUARANTINED` kayıtlar araştırma
kataloğunda görünür; ürün adı veya katalog pişirim aralığı tek başına oksit
analizi sayılmaz. Böyle bir kayıt senaryoda seçilirse çözülür, fakat motorun
sunucu tarafındaki özellik envanterine `oxide_analysis` eklenmediği için kimya
çıktısı `UNAVAILABLE` kalır. Kütüphane keşfi ile hesap motoru uygunluğu
bilinçli olarak birbirinden ayrılır.

`POST /api/v1/simulations/chemistry` aynı exact senaryoyu ve her hesaplanacak
katman için ayrı reçete girdisini alır. Bu istekte `BASE` miktarları parça,
`ADDITION` miktarları kuru baz yüzdesidir; fiziksel senaryo içindeki
`amount_g` alanıyla karıştırılmaz. Her katmanın sonucu ayrı kimya girdileri ve
provenance snapshot taşır. Araştırma dizini kaydı veya eksik analiz varsa
endpoint 422 döndürür; sessiz teorik eşleştirme yapmaz.

`POST /api/v1/references/openglaze/umf` yalnızca `OPENGLAZE_REPO_ROOT` ortam
değişkeni lisans incelemesinden geçmiş yerel checkout’a işaret ediyorsa çalışır.
Sonuç `DETERMINISTIC_EXTERNAL_REFERENCE` olarak etiketlenir; OpenGlaze raporu
ölçülmüş deney, yüzey garantisi veya gıda güvenliği kanıtı değildir. Kaynak
etkin değilse endpoint 503 ve `EXTERNAL_REFERENCE_NOT_CONFIGURED` döndürür.

`POST /api/v1/references/openglaze/compare` yalnızca `BASE` satırlarını kabul
eder. `ADDITION` satırlarının kuru baz yüzdesi ile harici reçete parser’ının
parça yüzdesi aynı semantik olmadığı için bu durum sessizce dönüştürülmez.
Yanıt `comparison-run-v1` içinde `internal`, `external`, oksit bazında `delta`
ve `delta_pct`, uyarılar ve sınırlamalar bulunur.

Web prototipi bu yanıtı `comparison-run-<hash>.json` adıyla snapshot olarak
indirebilir. Snapshot içinde karşılaştırmada kullanılan harici adlar, miktarlar
ve cone da bulunur. `POST /references/openglaze/replay` bu dosyanın aritmetik
bütünlüğünü ve input hash'ini kontrol eder; geçmişteki OpenGlaze checkout'unu
yeniden çalıştırmadığı için kaynağın bugün hâlâ erişilebilir olduğunu kanıtlamaz.
Dosya geçici/export niteliğindedir; M5 kalıcı `ComparisonRun` tablosu ve
yetkilendirilmiş erişim politikası gelene kadar sunucu kaydı sayılmaz.

M5 köprüsünde web istemcisi aynı snapshot’ı `POST /references/openglaze/runs`
ile yerel dosya arşivine kaydedebilir. Varsayılan kök
`storage/comparison-runs`'tır; `COMPARISON_ARCHIVE_ROOT` ile değiştirilebilir.
Arşiv kaydı `comparison_id=input_hash` ile adlandırılır, atomik yazılır ve aynı
kimlikte farklı payload sessizce üzerine yazılmaz. Bu dosya arşivi PostgreSQL
değildir; kullanıcı yetkilendirmesi, yedekleme ve paylaşım politikası içermez.

`POST /validation/outcomes` şu an yalnızca doğrudan eşleştirilebilen ölçümleri
kabul eder: gloss ortalaması (GU), su emmesi kütle yüzdesi ve görünür açık
porozite yüzdesi. Her kayıt `specimen_id`, yöntem, kaynak ve `MEASURED` veya
`REPORTED` durumunu taşır. Aynı numunenin tekrarları bağımsız deney sayılmaz.
Yanıt residual'ı `observed - calculated` olarak verir; `COMPARED` veya
`PARTIAL` durumu deneysel doğrulama sertifikası değildir.

Kimya analizinden deneye aktarılan `analysis_report_id` ve
`chemistry_input_hash`, bünye veya sır revision'ı yerine geçmez; yalnızca
hangi hesap snapshot'ının kullanıldığını gösteren provenance alanlarıdır.
Deney raporu `POST /validation/runs` ile `storage/experiment-runs` altında
checksum'lı yerel arşive alınabilir. Bu arşiv de henüz PostgreSQL, kullanıcı
yetkilendirmesi veya bulut yedeklemesi değildir.

## Web dağıtımı

Web uygulaması `/api/v1/*` isteklerini `API_ORIGIN` ortam değişkenine yönlendirir. Yerel geliştirmede varsayılan değer `http://127.0.0.1:8000`'dır. Vercel dağıtımında FastAPI servisinin kök adresi, sondaki `/` olmadan `API_ORIGIN` olarak tanımlanmalıdır. Backend dağıtılmadan production arşiv ve analiz istekleri çalışmaz; bu durum frontend build başarısı ile karıştırılmamalıdır.

## Analiz isteği

`input` discriminated union:

- `kind=INLINE_RECIPE`: base/additions, açık input_mode ve mass_basis.
- `kind=RECIPE_REVISION`: recipe_revision_id; M5'ten itibaren. Inline satırlarla aynı istekte verilmez.

Malzeme adı değil `material_analysis_id`. M4'in dosya tabanlı sürümlü referans resolver'ı aynı sözleşmeyi sağlar; M5 DB resolver geçişi motoru değiştirmez.

`analysis_options`: normalization_policy_id, umf_convention_id, constants_version (opsiyonel; belirtilmezse server seçtiğini yanıtta sabitler), include_additions. Mass basis unsupported/unknown ise hard error. `firing_context` opsiyoneldir; kimya hesabı için sıcaklık zorunlu değil.

Örnek: [analysis.request.example.json](../contracts/examples/analysis.request.example.json). Kimlikler gerçek materyallere referans değildir. [analysis.error.example.json](../contracts/examples/analysis.error.example.json) bazın çözülemediği varsayımsal bir 422 cevabıdır; gerçek endpoint çalıştırması değildir.

## Sonuç zarfı

```text
AnalysisResult
  schema_version
  analysis_id?                 # yalnızca persisted sonuçta
  persistence: TRANSIENT | PERSISTED
  engine_version
  constants_version
  policy_versions
  input_hash
  provenance: recipe_revision?, analysis_refs[], dataset_snapshot?, source_refs[]
  calculated
    normalized_recipe
    oxide_masses
    oxide_percentages          # bazları ayrı
    moles / mol_percent
    umf
    ratios
    flux_distribution
  observed_refs[]              # varsa gerçek numunelere link
  predictions[]                # MVP boş
  warnings[]
  unavailable_sections[]
```

Her bölüm/value envelope: evidence_kind, method_kind, status, qualifiers[], value, unit, basis, method_id/version, input_refs/source_refs, assumptions[], limitations[], uncertainty?, unavailable_reason?. Section metadata aynı olan değerler için ortak taşınabilir; serializer bu mirası belgeler.

EXAMPLE ONLY normalizasyon çıktısı: [normalization.result.excerpt.json](../contracts/examples/normalization.result.excerpt.json). Bu dosya tam AnalysisResult değildir; değer sözleşmesinin örneğidir.

M4 yanıtı hesaplama için gerçekten kullanılan sabitleri/sürümleri içerir. İstemcinin güncel bir malzeme listesinden yeniden kaynak ataması yapmasına izin verilmez. `recipe_revision_id` kullanılıyorsa başka kullanıcının revision'ına erişim yetkisi kontrol edilir.

## Hatalar

| HTTP / kod | Kullanım |
|---|---|
| 400 MALFORMED_REQUEST | JSON çözülemiyor |
| 422 NEGATIVE_AMOUNT / NON_FINITE_AMOUNT / ZERO_BASE_TOTAL | Geçersiz giriş |
| 422 ANALYSIS_BASIS_UNKNOWN / INCOMPLETE_ANALYSIS / UNSUPPORTED_OXIDE | Bilimsel girdi eksik veya kapsam dışı; strict tam hesap yapılamıyor |
| 404 MATERIAL_ANALYSIS_NOT_FOUND | Analiz yok veya istemciye açıklanmaması gereken erişim kapsamı |
| 401 AUTH_REQUIRED | Kimlik gerekiyor |
| 403 ACTION_NOT_ALLOWED | Kimliği bilinen kaynağa işlem yetkisi yok; existence leakage politikası uygulanır |
| 409 IDEMPOTENCY_KEY_REUSED | Aynı anahtar, farklı payload |
| 412 REVISION_PRECONDITION_FAILED | İstemcinin base revision'ı güncel değil |
| 429 RATE_LIMITED | Tekrar deneme bilgisiyle |

Hata alanları code, path, message, details, severity. Kullanıcı mesajı yerelleştirilebilir; kod sabit. Stack trace ve özel girdi sızmaz.

Geçerli kimyada sıfır flux, tüm isteği 422 yapmaz: HTTP 200; oxide/moles AVAILABLE, UMF UNAVAILABLE/ZERO_FLUX. Benzer biçimde tek ratio'da zero denominator bölüm düzeyindedir. Eksik analizde 422 cevabı isterse normalizasyon partial_results taşıyabilir; yanlış tam kimya üretmez.

## Mutasyonlar ve concurrency

Persisted POST için Idempotency-Key zorunlu; anahtar owner+route kapsamlı, body hash ile eşlenir. Aynı key/body aynı kaydı döndürür; farklı body 409. Transaction'da unique constraint ile çift kayıt engellenir. İlk sürüm saklama süresi API sözleşmesinde açıklanacak; süresi dolmuş key için sınırsız garantisi yok.

Yeni revision, If-Match/expected_revision ile eski revision'ı belirtir. Uyuşmazlık 412 ve çözüm akışı; sessiz overwrite yok. GET paging deterministic sıralama+cursor; ilk default 25, max 100 önerisi M4 ölçümünde doğrulanır. Cache key owner/access scope+input+engine/policies/constants; private yanıt shared public cache'e girmez.

## Geçersiz vs desteklenmeyen

Geçersiz JSON negatif amount ile, fiziksel modelin henüz uygulanmaması aynı sorun değildir. Optional prediction yoksa calculations başarısız olmaz. `unavailable_reason=MODEL_NOT_IMPLEMENTED` backend tarafından gerçek duruma göre üretilir; sahte % veya placeholder grafik yok.
