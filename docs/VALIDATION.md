# Bilimsel doğrulama ve kabul vakaları

M1'de test kodu yok. Aşağıdakiler M3+ testlerinin önceden tanımlanmış beklenen davranışlarıdır. M1 aritmetik kontrolü motor testinin geçtiği anlamına gelmez.

## Referans katmanları

1. Bağımsız elle hesaplanabilir aritmetik vakalar.
2. Sabit seti kaynağına karşı molar mass doğrulaması (M2).
3. Fiziksel anlamı tanımlı teorik saf bileşik vakaları; mass balance (M3).
4. Aynı analiz/constants/convention/addition politikasıyla ikinci calculator karşılaştırması (M3).
5. Fiziksel deney protokolü ve measured comparison (M6+); yazılım testi yerine geçmez.

İlk sayısal tolerans hedefi abs=1e-10, rel=1e-9; bilimsel belirsizlik farklı alan. Tolerans değişirse neden ve etkilenen vakalar kaydedilir. UI rounding testleri ayrı.

## Golden cases

| ID | Girdi | Beklenen | Katman |
|---|---|---|---|
| N-01 | Base 40,25,20,15 part | Aynı yüzdeler; toplam 100 | Normalizasyon |
| N-02 | Base 40,25,20,10 = 95 | 42.1052631579,26.3157894737,21.0526315789,10.5263157895; original korunur | Normalizasyon |
| N-03 | N-02'nin bütün miktarları *10 | Aynı normalize değerler | Ölçek invariance |
| N-04 | Total 0; negatif; NaN/Infinity | Ayrı stable error; JSON'da sonlu olmayan değer yok | Validation |
| A-01 | 1000g BASE_MASS, %2 base-on-top | Base 1000g, ilave 20g, total 1020g | İlave |
| A-02 | 1000g TOTAL_DRY_MASS, %2 base-on-top | Base 980.3921568627g, ilave 19.6078431373g | İlave |
| A-03 | %2 addition analizinin katkısı | Hesaba dahil; base-only view ayrı policy | İlave chemistry |
| B-01 | 100g DRY, LOI %10 dry, ignited SiO2 %50 | 45g SiO2; retained 90g | LOI-free dönüşüm |
| B-02 | 100g DRY, dry analiz SiO2 %45, LOI %10 | 45g; 40.5g değil | Çift LOI engeli |
| B-03 | 100g as-received, %10 nem, dry SiO2 %50 | 45g SiO2 | Nem |
| B-04 | UNKNOWN baz veya nem referansı eksik | Tam kimya bloke; silent default yok | Validation |
| B-05 | AS_RECEIVED SiO2 %45, as-received nem %10 | Dry SiO2 %50; yalnızca oksidi koruyan nem dönüşümü varsayımıyla | Ters baz dönüşümü |
| B-06 | 100g as-received, nem %10, dry-referenced LOI %20 | Retained mass 72g; LOI nemi zaten içeriyorsa aynı yol kullanılmaz | Birleşik baz dönüşümü |
| O-01 | 40g A(%70 SiO2),60g B(%50 SiO2); kalan analizler tanımlı | SiO2 katkısı 28+30=58g | Oksit contribution |
| O-02 | Eksik/trace/aralık değeri | Sıfır veya midpoint icat edilmez; kapsam politikası | Validation |
| U-01 | Aşağıdaki SYNTHETIC_TEST_ONLY sabitleri ve kütleleri | Mol SiO2=2, Al2O3=1, CaO=1; UMF 2,1,1 | Mol/UMF |
| U-02 | Saf SiO2, pozitif miktar, uygun analiz | Oksit/moles var; UMF null/ZERO_FLUX | Bölüm durumu |
| R-01 | U-01 | SiO2/Al2O3=2; atomik Si/Al=1 | Oran adları |
| R-02 | B2O3=0 veya R2O=0 | İlgili ratio UNAVAILABLE; NaN/Infinity yok | Payda |
| R-03 | CaO=0.5mol, ZnO=0.5mol; diğer flux=0 | Flux CaO=.5/ZnO=.5; alkaline-earth share=.5, RO=1 | Grup ayrımı |
| F-01 | FIRING_ENGINE'deki 3 ramp + 20min hold | 693min, cooling hariç | Plan süresi |
| F-02 | Cone 06 ve 6 | İki farklı geçerli kod; otomatik sıcaklık yok | Firing context |

### U-01 — yalnızca algoritma doğrulama fixture'ı

Bu basitleştirilmiş değerler **ölçülmüş veya production bilimsel sabit değildir**. Testin elle kontrolünü kolaylaştıran `SYNTHETIC_TEST_ONLY` setidir. Gerçek malzeme kataloğuna alınmayacak.

| Oksit | Fixture molar mass g/mol | Fixture kütle g | Mol |
|---|---:|---:|---:|
| SiO2 | 60 | 120 | 2 |
| Al2O3 | 102 | 102 | 1 |
| CaO | 56 | 56 | 1 |

Toplam kütle 278g; mol toplamı 4. Mol% 50/25/25. Flux kümesinde yalnızca CaO var; denominator=1mol. UMF SiO2=2, Al2O3=1, CaO=1. Weight% yaklaşık 43.1654676259 / 36.6906474820 / 20.1438848921. Bu reçete fiziksel üretim önerisi değildir.

M3'ün bilimsel kabulü U-01 tek başına geçince tamamlanmaz. M2'nin kaynaklı sabitleriyle gerçek molar-mass hesapları, teorik CaCO3->CaO+CO2 dengesi ve bağımsız calculator karşılaştırması ayrıca zorunlu. Gerçek bir dataset veya üretici analizinden türetilmiş expected sayılar bu aşamada uydurulmadı.

## Property testler

- Pozitif global scale normalize ve UMF'yi değiştirmez; absolute oxide mass scale ile değişir.
- Ingredient sırası kimyayı değiştirmez; provenance satır kimliklerini korur.
- Geçerli base yüzdeleri 100; uygun UMF flux toplamı 1.
- Uyumlu ve tam raporlanmış bazda mass balance; gaz alışverişi veya partial analizde aynı assertion uygulanmaz.
- Base/addition eşdeğer nihai kütle temsilleri aynı full chemistry verir.
- Aynı canonical input ve bütün scientific sürümler aynı sonucu/toleransı sağlar.

## Entegrasyon ve ürün

M2: tekrar import, source duplicates, count partition, quarantine, hak filtresi.

M4: form -> API -> rapor, unknown material, 422 ve network failure, eski yanıtın yeni girdiyi ezmemesi, predictions boş olması. 360px/768px/1440px kontrol hedefleri. Keyboard/tab/focus ve yalnızca renge dayanmayan etiket.

M5: gerçek PostgreSQL migration, FK/cross-owner kontrolleri, optimistic concurrency, idempotent POST, original replay ve new-engine reanalysis ayrımı. Geri alınamaz migration yok; review gerekir.

M6: bir recipe'nin farklı kilns/body/application koşullarında ayrı numuneleri; MISSING/NOT_ASSESSED/ABSENT ayrımı; demo/real ayrımı; image hak/size/EXIF.

M7: offline taslak, stale report, reconnect conflict, cache isolation. Emülasyon gerçek Safari/iPhone testi diye raporlanmaz.

M8: lisans/mahremiyet filtresi, similarity leakage kontrolü, bağımsız comparison, pilot feedback ve backup restore.

## Rapor standardı

Her check: id, girdiler/sürümler, beklenen, gözlenen, PASS/FAIL/NOT_RUN, ortam ve sınır. Koşulamayan test NOT_RUN. Fiziksel sonuç henüz ölçülmediyse yazılım PASS bunu değiştirmez.
