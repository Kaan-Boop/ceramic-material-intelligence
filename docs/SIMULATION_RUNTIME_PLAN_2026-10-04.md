# Esnek seramik simülasyon çalışma zamanı planı

## Karar

Motor, ChatGPT veya başka bir LLM olmadan çalışabilmelidir. LLM yalnızca daha sonra kaynaklı açıklama ve deney önerisi katmanı olur. Güncel veri ihtiyacı ayrı bir updater job ile çözülür; frontend internete doğrudan bağlanıp ham veri çekmez.

## İki çalışma modu

### OFFLINE / REPLAY

- Sürüm sabitlenmiş malzeme, reçete, oksit sabitleri ve deney verisi yerelden okunur.
- Aynı input snapshot + engine/policy sürümü aynı sonucu üretir.
- İnternet yokken yeni bilimsel iddia üretilmez; rapor snapshot tarihini gösterir.

### ONLINE / UPDATE

```text
source manifest
  → permission check
  → fetch with ETag/checksum/rate limit
  → raw immutable snapshot
  → parse/normalize/validate
  → quarantine
  → human/license review
  → versioned release
  → engine resolver
```

Updater Python job olarak Windows Task Scheduler, GitHub Actions veya hosting cron üzerinde çalışabilir. Çalışma zamanı bir modele/token'a bağlı değildir. Lisans belirsizliği olan kayıtlar arşivlenebilir ancak hesap ve eğitim setine otomatik açılmaz.

## Simülasyon girdisi

```text
body revision + analysis snapshot
glaze/engobe/addition layer revisions
dry mass and wet/dry application thickness
coat count and application method
geometry/thickness
bisque schedule and actual run
glaze firing schedule and actual run
kiln calibration/location
atmosphere timeline
material event properties
```

“Üç kat sır” tek başına yeterli değildir. Kuru film kalınlığı, süspansiyon katı oranı, katlar arasındaki kuruma, yüzey emiciliği ve parçanın geometrisi bilinmiyorsa model yalnızca senaryo aralığı raporlar.

## Katmanlı runtime

1. `chemistry`: reçete → oksit kütlesi → mol → UMF; deterministik.
2. `schedule`: ramp, hold, cooling ve toplam süre; planlanan program, gerçekleşmiş fırın kaydı değildir.
3. `mass_energy`: LOI, karbonat/bağlı su gibi yalnızca açıkça tanımlı olayların kütle muhasebesi.
4. `event_ledger`: her malzeme ve sıcaklık olayı için `AVAILABLE/PARTIAL/UNAVAILABLE`, kaynak ve varsayım.
5. `thermal_1d`: geometri ve termal özellikleri bilinen basitleştirilmiş sıcaklık gecikmesi; gerçek fırın haritası değildir.
6. `sintering`: yalnızca kaynaklı/kalibre edilmiş shrinkage veya porozite eğrisi varsa model.
7. `glaze_state`: solid/softening/partial-melt/melt sınıfları; bileşime ve sıcaklık eğrisine bağlı, veri yoksa sınıflandırma yok.
8. `interface`: glaze-body CTE ve ölçüm varsa fit göstergesi; tek başına çatlama olasılığı üretmez.
9. `outcome`: akma, tutunma, parlaklık, matlık ve renk için kanıt kapsamı; kalibre edilmiş deney yoksa `EXPERIMENT_REQUIRED`.

## Kullanıcının örnek senaryosu

```text
stoneware body
→ bisque schedule, yalnızca 600 °C değil
→ üç glaze coat + ölçülmüş kuru kalınlık
→ glaze recipe ve material analyses
→ 1200 °C firing schedule + hold + atmosphere
→ kiln calibration
```

Çıktı önce bir “sonuç” değil, zaman çizelgeli kanıt raporu olur:

- planlanan ve ölçülen sıcaklık ayrımı,
- beklenen kütle kaybı ve bilinmeyen gaz türleri,
- sinterleşme/vitrifikasyon göstergesinin geçerlilik alanı,
- erime durumu ve varsa viskozite kanıtı,
- üç katın kalınlık kaynaklı akma/defect etkileri,
- glaze-body fit göstergesi,
- tutunma, akış, matlık, parlaklık ve renk için `CALCULATED / OBSERVED / PREDICTED / UNAVAILABLE`,
- sonucu değiştirecek en önemli eksik ölçümler,
- kullanıcıya önerilen en küçük deney planı.

## Neyi henüz fiziksel olarak söyleyemeyiz?

UMF veya sıcaklık tek başına sır yüzeyini, yapışmayı ya da kusur yüzdesini belirlemez. OpenGlaze, UMF/Seger ve reçete yönetimi için uygun bir açık kaynak referanstır; fakat kendi sonuçları da laboratuvar doğrulamasının yerine geçmez. CALPHAD/pycalphad faz dengesi için altyapı sağlar, fakat uygun seramik `.tdb` veri tabanı olmadan sonuç üretmek bilimsel olarak savunulamaz. Cantera genel termokimya/transport aracıdır; doğrudan sır yüzeyi simülatörü değildir.

## Sonraki geliştirme kapıları

1. Scenario schema: body–bisque–application–glaze–cooling tek immutable input.
2. Event ledger ve kütle/enerji bilançosu.
3. Üç kat ve kuru film kalınlığı için what-if senaryosu.
4. Tek pilot body–glaze sistemi üzerinde ölçülmüş shrinkage, absorption, thickness ve surface gözlemleri.
5. Ölçülen CTE/TGA/viskozite geldikten sonra sınırlı termal ve melt modelleri.
6. Ancak bağımsız test grubu oluştuktan sonra kalibre edilmiş istatistik/ML.

## Rakip ürün kontrolü

Rakip bir ürünün daha gerçekçi olması için gereken veri avantajı; daha fazla slider değil, ürün/lot bazlı analiz, gerçek firing curve, kuru film kalınlığı, tekrarlı numune ve ölçülmüş sonuç geçmişidir. Bu nedenle geliştirme önceliği görsel simülasyon sayısını artırmak değil, her simülasyon çıktısını ölçülebilir bir deney kaydına bağlamaktır.
