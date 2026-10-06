# Fırın eğrisinden katman içi sıcaklığa — 1B ısı çekirdeği

Sürüm: `layered-kiln-heat/0.1.0` · 6 Ekim 2026.

**Çalışan araştırma modeli:** düz bir katı numunenin iki dış yüzeyden
taşınım/ışınımla ısı alışverişini ve kalınlık boyunca iletimini hesaplar.
Isıtma, bekletme ve soğuma aynı denklemle çözülür. Bu bir fırın kontrolörü,
ham çamurun tüm pişirim simülasyonu veya doğrulanmış ticari malzeme modeli değildir.

## Neyi ekledi?

Önceki `research/simulation/core.py` geçici 3B modeli dış yüzeylerde sabit
sıcaklık dayatır. Yeni `research/thermal/kiln_1d.py`, zamana bağlı **gaz ve
duvar sıcaklığı** ile yüzeydeki gerçek ısı alışverişini ayrı tanımlar.
Numune yüzeyinin fırın programıyla aynı sıcaklıkta olduğu varsayılmaz.
Mevcut FEM veya kimya motoru değiştirilmedi; bağımsız 1B çözüm yolu eklendi.

Kimyasal analizden `k`, `rho`, `cp`, `h` veya emissivity türetilmez.
Her parametre grubu kaynak ve `SYNTHETIC / REPORTED / MEASURED` beyanı ister.
Kaynak adresinin yazılması, analizin kabul edildiği veya doğrulandığı anlamına gelmez.

## Girdiler ve çıktı sınırı

| Girdi | Birim / anlam |
|---|---|
| Katman kalınlığı ve hücre sayısı | m; katman arayüzleri ağda korunur |
| `conductivity_w_m_k` | W/(m K), sabit iletkenlik |
| `density_kg_m3`, `specific_heat_j_kg_k` | kg/m³ ve J/(kg K), sabit |
| `valid_temperature_c` | Beyan edilen model geçerlilik aralığı; yüzeyler de denetlenir |
| `area_m2` | İki açık yüzeyin her birinin alanı, m² |
| Başlangıç sıcaklığı | °C, ilk anda tüm hacimde uniform |
| Her yüzeyde `h_w_m2_k`, `emissivity` | W/(m² K), 0–1; ikisi 0 ise yalıtılmış |
| Gaz/duvar tarihçesi | `time_s`, `gas_c`, `wall_c`; aynı çevre iki yüzeye uygulanır |
| `max_step_s` | s; her program kırılma noktasına tam varılır |

`MEASURED_ENVIRONMENT` bir kontrol cihazı hedefi değildir; ölçülmüş çevre
beyanıdır. Diğer durum `PRESCRIBED_ENVIRONMENT` olarak işaretlenir. Doğrusal
ara değer alınır; program sonundan sonrası hesaplanmaz. Bir termokupl kaydı
duvar sıcaklığı olarak otomatik kopyalanmaz. Kat sayısı kalınlığa çevrilmez.

Çıktı: her zaman adımında hücre ve iki gerçek yüzey sıcaklığı, katman orta
nokta sıcaklıkları, ısı kapasitesi ağırlıklı ortalama, anlık uzamsal sıcaklık
aralığı, net taşınım/ışınım enerjisi, duyulur enerji değişimi ve denge artığı.
Enerji işareti: numuneye giriş pozitif. Net enerji, fırının elektrik tüketimi
veya mutlak enerji geçişi toplamı değildir. Orta nokta değeri ölçüm değil,
o katmana ait merkez değerlerinden interpolasyonla elde edilen model çıktısıdır.

Sonuç `PREDICTED / DETERMINISTIC / IDEALIZED_INERT_SLAB` taşır.
`physical_validation=NOT_PERFORMED`, `uncertainty=null`. Bu null, sıfır hata
değildir. `AVAILABLE` yalnızca seçilen ideal modelin hesaplanabildiğini söyler.
Erime, sinterleşme, reaksiyon dönüşümü ve kusur olasılığı gerekçeli biçimde
`unavailable_sections` içinde kalır.

## Denklem ve sayısal yöntem

İçeride reaksiyon/latent ısı kaynağı olmadan:

```text
rho cp dT/dt = d/dx(k dT/dx)

q_in/A = h (T_gas - T_surface)
       + epsilon sigma (T_wall^4 - T_surface^4)

C_i = rho_i cp_i A dx_i
G_(i,i+1) = A / [dx_i/(2 k_i) + dx_(i+1)/(2 k_(i+1))]

C_i (T_i,new - T_i,old)/dt
  = sum_neighbors G_ij (T_j,new - T_i,new) + Q_face,new
```

Işınım denkleminde sıcaklıklar **Kelvin**. Sabit
`sigma=5.670374419e-8 W/(m² K⁴)` raporda sabitlenir; NIST/CODATA 2022
değerinin sonlu basamaklı temsilidir.

Hücre merkezli sonlu hacim, geri Euler ve sönümlü Newton kullanılır. Üç
diyagonalli Jacobian doğrudan çözülür. Bir arayüzde iletkenliği aritmetik
ortalama yapmak yerine seri ısıl direnç kullanılır. İki katman arasında
mükemmel temas varsayılır; temas direnci ve ara yüzey kimyası yoktur.

Fiziksel dış yüzey, ilk/son hücre merkezinden ayrıdır. Yarım hücre iletim
direnci ile taşınım ve T⁴ ışınım aynı anda çözülür. Yüzey sıcaklığını doğrudan
hücre sıcaklığı saymak özellikle kaba ağda hatalı ısı akısına yol açabilirdi.
Doğrusal olmayan yüzey denklemi monoton olduğu için aralıklı kök çözümü
kullanılır; Newton adımı pozitif mutlak sıcaklığı ve artık azalmasını korur.

Her kabul edilmiş adım için gelen net enerjinin integrali, çözücüde kullanılan
**aynı geri Euler akısıyla** alınır:

```text
residual_J = E_convection + E_radiation - sum_i C_i (T_i - T_initial)
```

Küçük artık, ayrık denklemin enerji tutarlılığıdır. Ağ/zaman adımı hatası veya
gerçek deney doğruluğu değildir. Kararlı örtük yöntem de büyük adımın doğru
olduğunu garanti etmez; adım ve ağ inceltmesi ayrıca kontrol edilir.

## Varsayımlar / uygulanamayacağı durumlar

- Düz plaka, kenarlar yalıtılmış; 2B/3B geometri, raf teması ve gölgeleme yok.
- Sabit kütle, geometri, yoğunluk, iletkenlik, ısı kapasitesi ve emissivity.
- Büyük izotermal çevre içinde gri/difüz yüzey, görüş faktörü 1; gazın kendi
  ışınımı ve katı içi radyatif aktarım yok.
- Ham kil kuruması, dehidroksilasyon, karbonat ayrışması, sinterleşme ve
  erime için gerekli kaynak terimleri henüz bu çözücüye bağlı değil.
- Mevcut ayrı `reaction_heat` çalışması verilen dönüşümden enerji hesabı
  yapar; sıcaklıktan reaksiyon hızını belirleyen doğrulanmış kinetik değildir.
  Bu nedenle iki modül sessizce birleştirilmedi.
- Bu özelliklerle 1200 °C'ye çıkarılan sentetik örnek **gerçek sır/bünye
  pişirim tahmini olarak kullanılamaz**. Matlık/akma/çatlama yüzdesi üretmez.
- Geçerlilik sınırı aşılırsa sonuç kesilir; ekstrapolasyon veya kırpma yok.

Kaynak sınırları: 1–8 katman, toplam en fazla 256 hücre, 20.000 zaman adımı,
2.000.000 hücre-zaman kaydı. API ayrıca mevcut 64 KiB istek sınırını korur.
Bunlar hesap/bellek sınırlarıdır; fiziksel doğruluk kriterleri değildir.
Yakınsamayan doğrusal olmayan çözüm `NONLINEAR_SOLVER_FAILED_REDUCE_STEP`
verir; kısmi sonuç başarılı diye dönmez, adım sessizce değiştirilmez.

## Doğrulama

`tests/test_kiln_thermal_1d.py`:

1. Uniform denge ve tümü yalıtılmış numune.
2. Sonlu plakanın analitik taşınımlı soğuma çözümüne karşı ağ inceltmesi.
3. Aynı analitik çözüme karşı bağımsız zaman adımı inceltmesi.
4. İki katmanın seri direnci + doğrusal olmayan ışınımlı kararlı çözüm.
5. Tek hücre için elle türetilmiş ayrık geri Euler sonucu.
6. Isıtma/bekletme/soğutmada enerji, sıcaklık gradyeni yönü ve tam program düğümleri.
7. Alanla enerjinin ölçeklenmesi, sıcaklığın değişmemesi.
8. Yeniden üretilebilirlik, girdi değişmezliği ve bilinmeyen belirsizlik.
9. Tür, aralık, kaynak, süre, hücre, NaN ve faz-modeli kapsam kontrolleri.
10. Hücre merkezleri sınırda olmasa da yüzeyin malzeme kapsamını aşması.

Analitik test: yarım kalınlık L=1 m, alpha=1 m²/s, Bi=1, başlangıç 100 °C,
çevre 0 °C. `mu tan(mu)=1` kökleri ve ayrık değişkenler çözümünün 40 terimi
bağımsız hesaplanır. Sayısal çözüm bu seriyle üretilmez. 32 hücre ve 0,0005 s
adımda t=0,2 s anındaki en büyük merkez sıcaklığı hatası <0,04 °C şarttır;
bu sadece bu **sentetik analitik problem** için kabul kriteridir.

API'nin 4 testi çekirdek/API eşitliği, kaynak/sınır etiketleri, anlamlı hata
kodları ve mevcut yerel erişim sınırlarını kontrol eder. CLI'nin 2 testi
JSON/CSV/checksum tutarlılığı, çakışmadan tekrar çıktı alma ve **site-packages
olmadan çekirdeğin import edilebilmesini** denetler.

### 6 Ekim sayısal çalıştırma sonuçları

| Kontrol | Sonuç |
|---|---|
| Analitik çözüm, 8 → 16 → 32 hücre, dt=0,0005 s | Maksimum hata 0,272680 → 0,080894 → 0,029226 °C |
| Analitik çözüm, dt=0,04 → 0,02 → 0,01 s, 128 hücre | Maksimum hata 0,943248 → 0,475529 → 0,239157 °C |
| Sentetik iki katman, 24 hücre, 1.500 adım | İlk yerel koşu yaklaşık 0,45 s; donanıma bağlı, servis performans garantisi değil |
| Aynı örnekte 30 s → 15 s adım | Ortak zamanlarda iki yüzey/kapasite ortalamasında en büyük fark 0,210238 °C |
| Aynı örnekte 24 → 48 hücre | Aynı üç ölçütte en büyük fark 0,016309 °C |
| İkisi birlikte inceltildiğinde | Başlangıç koşusuna göre en büyük fark 0,205617 °C |
| Başlangıç koşusu enerji bilançosu | Maksimum mutlak artık 0,000201 J'den küçük; tepe duyulur enerji değişimi yaklaşık 489.338 J |

İki ayrıklaştırma değişikliğinin etkileri toplanmak veya güven aralığı diye
yorumlanmak zorunda değildir. Bu farklar tam sıcaklık alanı için hata sınırı
da değildir; tablodaki belirli ölçütlerdir. Fiziksel katsayı belirsizliği
ve model eksikliği burada sayısallaştırılmış değildir.

Örnekte gaz 1200 °C, duvar 1220 °C iken bekletme sonunda numune yaklaşık
1219,36 °C olur: bu bir aşım hatası değil, daha sıcak duvardan gelen ışınımın
sonucudur. Çevre 20 °C'ye döndüğü son adımda numune orta noktası hâlâ yaklaşık
57,99 °C'dir. Programın bitmesi numunenin soğuduğu anlamına gelmez. Bunlar
**sentetik inert örnek** sonuçları; gerçek ürün için fırın programı önerisi değildir.

API sözleşmesi yeniden üretilirken eski şemada bulunmayan mevcut endpoint'ler
de güncellendi. İki kez tanımlanmış health route'un kullanılmayan kopyası
kaldırıldı; runtime yanıtı korunarak OpenAPI ile aynı tanıma bağlandı.

Yeni 16 test dahil, seçilen çekirdek/FEM/API regresyon paketlerinde toplam
129 farklı test geçti; `npm run typecheck` de geçti. Bunlar tüm repository'nin
tam test taraması değildir. API test ortamında mevcut Starlette/httpx
deprecation uyarısı sürüyor; bu teslimde paket yükseltilmedi.

## Çalıştırma

Proje kökünde PowerShell; yeni paket kurulumu gerekmez:

```powershell
& '.\storage\prototype\environment\Scripts\python.exe' -m unittest tests.test_kiln_thermal_1d tests.test_kiln_thermal_cli apps.api.tests.test_kiln_thermal_api -v
& '.\storage\prototype\environment\Scripts\python.exe' -m scripts.run_kiln_thermal_1d data/fixtures/kiln-thermal-1d-synthetic.json
```

`storage/simulation/kiln-thermal-1d/<hash>-<unique>/` altında:

- `report.json`: tüm sıcaklık alanı, girdi snapshot'ı, sürüm, sabit ve durumlar.
- `timeline.csv`: zaman, ortam/yüzey/katman sıcaklıkları, enerji bilançosu.
- `temperature-field.csv`: her zaman–konum için °C; katman indeksleri ayrı.
- `receipt.json`: dosya/çekirdek hash'leri, Python sürümü ve çalıştırma süresi.

CSV katman sütunlarının kimlik eşlemesi receipt'tedir; kullanıcı metni CSV
formülü olarak yazılmaz. Çıktılar her koşuda yeni dizine alınır. CSV'ler
grafik ve deney karşılaştırması için sayısal veridir; JSON'u ve receipt'i
yanlarında koruyun. Kalıcı veritabanı kaydı veya bulut yayını değildir.

Yerel API: `POST /api/v1/simulations/thermal-1d`, gövde `{"case": <fixture>}`.
Mevcut genel senaryo endpoint'lerinden otomatik çağrılmaz; kullanıcı termal
özellikleri açıkça vermelidir. Web ekranına ve Vercel'e henüz bağlanmadı.

## Yöntem kaynakları

6 Ekim 2026'da kontrol edilen birincil kaynaklar; kod kopyalanmadı,
değerler gerçek ürün analizi diye içeri alınmadı:

- [NIST FiPy — Discretization](https://pages.nist.gov/fipy/en/stable/numerical/discret.html):
  kontrol hacmi depolama/iletim ve örtük zaman ayrıklaştırma yaklaşımı.
- [MOOSE — Convective heat flux](https://mooseframework.inl.gov/source/bcs/ADConvectiveHeatFluxBC.html):
  h(T_çevre−T_yüzey) sınır koşulu; burada numuneye giriş pozitif seçildi.
- [MOOSE — Radiative boundary](https://mooseframework.inl.gov/source/bcs/ADFunctionRadiativeBC.html):
  emissivity ve Stefan–Boltzmann temelli T⁴ sınır koşulu.
- [NIST — CODATA 2022 constants](https://physics.nist.gov/cuu/Constants/Table/allascii.txt):
  sigma sabiti; kullanılan basamaklar yukarıda sabitlendi.
- [SN Applied Sciences, 2021, 3:71 — analitik plaka referansı](https://d-nb.info/1228401128/34):
  DOI `10.1007/s42452-020-04065-3`, denklemler 21–23. Analitik seri katsayıları
  ve taşınımlı sınırın özdeğer denklemi kontrol edildi; makaledeki sezgisel
  optimizasyon algoritmaları kullanılmadı, kökler aralıklı çözümle bulundu.

Bu belgeler çözücü yöntemine dayanak sağlar; seramik parametrelerini veya
ürün sonuçlarını doğrulamaz. Bir sonraki fiziksel doğrulama kapısı, belirli
bir inert/önceden pişmiş numunenin k/rho/cp ve yüzey katsayılarıyla, ayrı
gaz/duvar ve numune sıcaklık kayıtlarını eşleştirmektir. Ardından uygun
entalpi/kinetik verisi olan tek bir reaksiyon için enerji-kütle eşleşmesi
kurulabilir. Tüm malzemelere genel reçete→pişirim sonucu iddiası ertelenir.
