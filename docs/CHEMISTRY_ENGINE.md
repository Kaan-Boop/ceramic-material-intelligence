# Kimya motoru — bilimsel sözleşme v0.1

Durum: M1 tasarımı; implementasyon ve bilimsel unit testler henüz yok.

## Kanıt ve kapsam

Kütle -> mol -> unity yaklaşımı iki ayrı teknik kaynaktan incelendi: [Digitalfire — Glaze Chemistry Basics](https://digitalfire.com/article/189), [Glazy — Chemical Analyses and Formulas](https://help.glazy.org/concepts/analyses). Bunlar iki teknik açıklamadır; belirli üretici analizini veya gerçek fırın sonucunu doğrulamaz.

Molar kütle için referans: [CIAAW abridged atomic weights](https://ciaaw.org/abridged-atomic-weights.htm). M2 production sabit setini sürüm, kaynak, seçilmiş atom ağırlığı ve yuvarlama politikasıyla yayınlar. M1 sentetik örnekleri bu setin yerine geçmez.

Her bilimsel metodun `method_id`, `version`, `source_refs`, `assumptions`, `limitations`, `validation_case_ids` alanları bulunacak. Kaynaksız bir fiziksel model yayına alınmaz.

## Girdi

Motor yalnızca çözülmüş immutable analiz snapshot'ları, miktarlar, birimler ve politikaları alır. Malzeme adı resolver'a aittir. “Feldspar” ifadesi sessizce belirli bir ticari ürüne çevrilmez.

MVP girdi politikaları:

| Mod | Anlam |
|---|---|
| `PARTS` | Base satırları bağıl miktarlar; toplam 100'e normalize edilir |
| `MASS` | Aynı batch'in g/kg miktarları; g'ye çevrilir, original korunur |
| `TOTAL_BATCH_PERCENT` | Bütün kuru malzeme payları toplamı 100; ayrı base-on-top ilave ile aynı istekte karıştırılmaz |

Base-on-top ilave: `amount_basis = PERCENT_OF_BASE`. Örneğin %2 ilave 100 g base'e 2 g; sonuç 102 g'dır. Nihai batch içinde ilave payı 2/102 olur. İlaveli reçeteyi son toplam 100'e çevirmek base reçetesini değiştirmez; ayrı bir sonuç görünümüdür.

TOTAL_BATCH_PERCENT modunda toplam 100 olmalıdır (sadece belgelenmiş numeric tolerans uygulanır); 95 toplamı sessizce düzeltilmez. Kullanıcı bilinçli olarak PARTS moduna geçerse normalizasyon yapılır. Ingredient role ile amount_basis ayrı alanlardır: bir pigment toplam batch yüzdesi olarak da girilebilir.

Su miktarı `suspension` bağlamıdır; kuru sır yüzdesinin paydasına girmez. Islak hammadde miktarı verildiyse nem/baz dönüşümü ayrıca gerekir. Kullanıcıdan alınmayan nem 0 sayılmaz.

`batch_target_basis`: BASE_MASS veya TOTAL_DRY_MASS. 1000 g base + %2 ilave = 1020 g. Hedef toplam 1000 g ise base = 1000/1.02, ilave = base*0.02. UI iki hedefi açık adlandırır.

## Normalizasyon

`base_total = sum(a_i)`; `p_i = 100*a_i/base_total`.

Negatif veya sonlu olmayan miktar geçersizdir. Sıfır satır taslakta kalabilir; katkısı sıfırdır. Base toplamı 0 ise normalizasyon UNAVAILABLE. Miktar/birim dönüşümünde original string/değer korunur. Ondalık virgül/nokta API öncesi yerel format kuralıyla çözülür; belirsiz binlik ayracı tahmin edilmez.

MVP karışık base birimleri (part ile gram) reddedilir. g ve kg aynı MASS isteğinde dönüştürülebilir. Volume -> mass dönüşümü yoğunluk varsayarak sessiz yapılmaz.

## Analiz bazları ve LOI

Zorunlu alanlar: `analysis_basis`, `oxide_wt_pct`, kapsam bilgisi; gerekiyorsa `loi_pct`, `loi_reference_basis`, `moisture_pct`, `moisture_reference_basis`, test yöntemi.

| Analiz | Girdi kütlesi | Dönüşüm |
|---|---|---|
| AS_RECEIVED | Alındığı halde kütle | Raporlanan oksit wt%'lerini doğrudan uygula; LOI'yi tekrar düşme |
| DRY | Kuru kütle | Raporlanan dry wt%'leri doğrudan uygula |
| DRY | Islak/as-received kütle | Bilinen as-received nem oranıyla kuru kütleye geç; sonra dry yüzdeler |
| IGNITED/LOI_FREE | Uyumlu LOI referansındaki başlangıç kütlesi | Retained mass = başlangıç*(1-LOI/100); oxide = retained*LOI-free wt%/100 |
| UNKNOWN | Herhangi | Tam oksit hesabı bloke; kullanıcı analiz bazını çözmeli |

Örnek: 100 g kuru malzeme, dry bazda LOI %10, ignited analizde SiO2 %50 -> 45 g SiO2. Dry/as-received analiz zaten %45 SiO2 raporluyorsa aynı 100 g bazda sonuç 45 g; tekrar %10 azaltılmaz.

Örnek nem: 100 g as-received, nem %10, dry analiz SiO2 %50 -> 45 g SiO2. Hem nem hem dry-referenced LOI gerekli dönüşümde varsa sırayla ve doğru referans bazlarıyla uygulanır.

`h` as-received nem kesri, `l_dry` dry-referenced LOI kesriyse: m_dry=m_as_received*(1-h); m_ignited=m_dry*(1-l_dry). Bir AS_RECEIVED oksit yüzdesini DRY baza geçirmek için, yalnızca nem gideriminin ilgili oksitleri koruduğu ve h'nin bilindiği durumda w_dry=w_as_received/(1-h). Tersi w_as_received=w_dry*(1-h). Toplam as-received LOI zaten nemi içeriyorsa retained mass=m_as_received*(1-l_as_received); nem ayrıca tekrar düşülmez. 1-h veya retained mass sıfırsa ilgili ters dönüşüm kullanılamaz. Çelişkili referans bazları `INCONSISTENT_BASIS_METADATA` verir.

LOI bir oksit değildir; UMF flux toplamına girmez. Oksidasyon nedeniyle kütle kazancı/negatif LOI olasılığı bilimsel olarak geçersiz sayılmaz; ilk motorun standart kayıp modeli kapsamı dışındaysa `UNSUPPORTED_MASS_CHANGE_MODEL` ile incelemeye alınır. Uçuculuk, gaz alışverişi ve redoks ayrıca modellenmedikçe sonuç gerçek pişmiş numunenin ölçülmüş bileşimi değildir.

## Oksit katkısı

Uyumlu bazda `m_j = sum(m_i * w_ij / 100)`.

Her satır katkısı saklanır; kullanıcı toplam oksidin hangi malzemeden geldiğini izler. Hesaba dahil edilen ilaveler varsayılan olarak analize dahildir. “Yalnızca base” karşılaştırması ayrı ve etiketli AnalysisRun/policy üretir; pigment veya opaklaştırıcı sessizce yok sayılmaz.

Sonuçlar ayrı adlandırılır:

- `oxide_mass_g`: raporlanan oksitlerin hesaplanan kütlesi.
- `oxide_wt_pct_of_input`: tanımlanmış giriş kütlesine göre yüzde.
- `oxide_wt_pct_of_reported_total`: yalnızca bilinen oksit toplamına göre normalize görünüm; eksiksiz fired chemistry iddiası değil.
- `reported_analysis_total`, `unreported_fraction`, `retained_mass_estimate`: bazları ve hesaplanabilirlik koşullarıyla.

Raporlanan toplam otomatik 100'e kapatılmaz. 100'den sapma; LOI, baz, rapor kapsamı ve yuvarlama üzerinden değerlendirilir. Varsayılan tarama eşiği |toplam-100| > 0.5 yüzde puanı ise review flag; bu **ölçüm doğruluğu limiti veya otomatik düzeltme yetkisi değildir**. Kaynak uncertainty ve kapsamı daha sıkı inceleme gerektirebilir. Eşik import policy'de sürümlenir.

`coverage`: COMPLETE_REPORTED / PARTIAL / UNKNOWN. Bir oksit satırının bulunmaması ancak kaynak açıkça kapsam ve sıfır semantiğini sağlıyorsa sıfır olarak çözülebilir. `<LOD`, aralık ve `trace` numeric zero değildir. İlk motor interval propagation yapmaz; desteklenmeyen sınır/aralık kritikse tam hesap kullanılamaz.

Strict v1: missing analysis/basis veya PARTIAL/UNKNOWN coverage varsa normalize reçete ve tanımlı bilinen katkılar PARTIAL gösterilebilir; **tam mol%, UMF, bütün reçete oranı ve fiziksel yorum yayımlanmaz**. Bilinen katkıları tam reçete yerine geçiren normalizasyon yok.

## Mol ve UMF

`n_j = m_j / M_j`; `mol_pct_j = 100*n_j/sum(n)`.

`standard-flux-v1` flux kümesi: Li2O, Na2O, K2O, MgO, CaO, SrO, BaO, ZnO.

`flux_total = sum(n_f)`; `u_j = n_j/flux_total`.

Gösterim grupları: flux kümesi; Al2O3 (intermediate); SiO2/B2O3 (glass-former gösterimi); kalanlar OTHER. Bu, oksidin her koşulda tek fiziksel rolü olduğu anlamına gelmez. B2O3 denominator'a alınmaz; Fe2O3/TiO2/ZrO2/CoO/CuO/MnO2/SnO2/P2O5 bu v1 denominator'ına alınmaz. Bunlar kaynak analizi uygunsa toplam kimyada korunur. Yeni flux veya redoks konvansiyonu yeni policy sürümüdür.

İlk kayıt sözlüğü hedefi: SiO2, Al2O3, Na2O, K2O, CaO, MgO, ZnO, BaO, SrO, Li2O, B2O3, TiO2, ZrO2, Fe2O3, CoO, CuO, MnO2, SnO2, P2O5. Desteklenmeyen oksit katkısı sessiz atılmaz; `UNSUPPORTED_OXIDE` döner. FeO veya Cr2O3 ileride ancak sabit/kural/test eklenerek desteklenir.

Flux toplamı 0 ise UMF UNAVAILABLE / ZERO_FLUX. Pozitif çok küçük flux'a keyfî epsilon ile sıfır muamelesi yapılmaz; extreme magnification uyarısı ve sayısal sonluluk kontrolü uygulanır. Görüntüleme yuvarlaması sonucu toplamın 0.999 görünmesi hesap değeri değiştirilerek düzeltilmez.

## Oran tanımları

| Ad | Tanım |
|---|---|
| oxide_molar_SiO2_to_Al2O3 | n(SiO2) / n(Al2O3) |
| atomic_Si_to_Al | n(SiO2) / [2*n(Al2O3)] |
| oxide_molar_SiO2_to_B2O3 | n(SiO2) / n(B2O3) |
| R2O | n(Li2O)+n(Na2O)+n(K2O) |
| RO | n(MgO)+n(CaO)+n(SrO)+n(BaO)+n(ZnO), bu konvansiyonda |
| alkaline_earth | n(MgO)+n(CaO)+n(SrO)+n(BaO); ZnO dahil değil |
| RO_to_R2O | RO/R2O |
| flux_share_j | n_j/flux_total, flux üyeleri için |

Alkali/alkaline-earth paylarının paydası seçilen flux_total olarak açık yazılır. ZnO nedeniyle alkaline-earth + alkali payı her zaman 1 değildir; other flux payı gösterilir. KNaO türetilmiş toplamdır; bağımsız oksit gibi çift sayılmaz. “Silica/alumina/boron percentage” etiketi tek başına kullanılmaz: wt% mi mol% mi, B mi B2O3 mü belirtilir.

Sıfır payda: ilgili oran null, status UNAVAILABLE, reason ZERO_DENOMINATOR. Diğer çıktılar etkilenmez. NaN/Infinity JSON'a çıkmaz.

## Arayüz ve determinism

```text
normalize_recipe(recipe, normalization_policy) -> NormalizedRecipe
convert_analysis_basis(analysis, target_basis, basis_policy) -> BasisResult
calculate_oxides(recipe, resolved_analysis_snapshots, basis_policy) -> OxideResult
calculate_moles(oxide_result, constant_set) -> MoleResult
calculate_umf(mole_result, umf_convention) -> UMFResult
calculate_ratios(mole_result, ratio_definitions) -> RatioResult
```

Motor sayısal çıktıya zaman, request id veya rastgele ID eklemez; wrapper ekler. Input hash canonical serializasyondan üretilir; normalize birimler, exact analiz checksum'ları ve bütün policy/constant sürümleri kapsanır. Orijinal kullanıcı yazımı audit'te korunur. Sıra bağımsız hesap için kararlı sıralama/toplama yöntemi uygulanır.

Aynı snapshot ve aynı motor/runtime sürümünde aynı sonuç hedeflenir. Platformlar arası karşılaştırma belgelenmiş toleransla; `abs_tol=1e-10`, `rel_tol=1e-9` ilk aritmetik test hedefidir. Bunlar fiziksel ölçüm belirsizliği değildir. Yuvarlama yalnızca UI/export görünümünde.

## Yasak çıkarımlar

UMF tek başına renk, parlaklık, erime sıcaklığı, food-safe, glaze fit veya metal/cam uyumu üretmez. Limit formula karşılaştırması yalnızca kaynaklı aralık karşılaştırmasıdır. Stull koordinat hesabı mümkün; tarihsel bölge kapsamı incelenmeden yüzey etiketi atanmaz. Genleşme modeli MVP dışında; [Digitalfire sınır açıklaması](https://digitalfire.com/glossary/calculated%2Bthermal%2Bexpansion).
