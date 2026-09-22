# Fizik–kimya motoru: denetim ve yeni teslim

## Bu turda yapılan

Mevcut 138 test başlangıçta geçti. Yeni `research/chemistry/recipe.py` bağımsız araştırma hesaplayıcısı, `recipe_demo.py` çalıştırılabilir örneği ve 12 test eklendi. Yeni paket kurulmadı; eski sabit seti değiştirilmedi. Üretim web uygulaması veya tamamlanmış M3 teslimi değildir.

Reçete girdisi: analiz ID, miktar, BASE veya ADDITION; analiz snapshot'ı: sürüm, kaynak, kuru/kızdırılmış baz, kuru baza göre LOI, oksit yüzdeleri, açık tamlık ve raporlanmayan oksitlerin sıfır olduğu beyanı. Motor bu beyanın laboratuvar doğruluğunu veya kaynağın kullanım hakkını doğrulayamaz; kabul/lisans kontrolü uygulama katmanının görevidir.

BASE miktarları parça olarak 100'e normalize edilir. ADDITION kuru baz üzerine yüzdedir. DRY analizde LOI ikinci kez düşülmez; IGNITED analizde kuru başlangıç kütlesi tutunmuş fraksiyona çevrilir. Nemli/as-received giriş, eksik analiz, negatif LOI ve bilinmeyen baz desteklenmez. Toplam için 1e-6 yüzde puan toleransı araştırma sınırıdır; yuvarlanmış ticari analizleri sessizce düzeltmez. Böyle kayıtlar ayrı kabul politikasına ihtiyaç duyar.

Çıktı: orijinal/normalize miktar, kuru gram, oksit gramı, mol, mol%, teorik tutunmuş oksit wt%, LOI kütlesi, standard-flux-v1 UMF, flux payları, oksit SiO2/Al2O3 ve atomik Si/Al oranları, RO/R2O. Sıfır flux veya oran paydası sayı uydurmak yerine UNAVAILABLE verir. Snapshot, motor/sabit/convention sürümü ve hash tekrar üretimi destekler. Kaynak verisi sonradan değişse bile dönen snapshot değişmez.

## Çalıştırma

Proje kökünden PowerShell:

```powershell
.\storage\simulation\00_environment\Scripts\python.exe -X utf8 -m research.chemistry.recipe_demo
.\storage\simulation\00_environment\Scripts\python.exe -X utf8 -m unittest discover -s tests
```

## Gerçek çalıştırılan örnek

40 ideal K-feldspat + 25 saf SiO2 + 20 ideal kaolinit + 15 saf kalsit, 100 g kuru baz. Bunlar ticari ürün analizi değil, formülden türetilmiş teorik fixture'lardır. Oksit ayrıştırması serbest kristal faz oluşumu anlamına gelmez.

| Çıktı | Sonuç |
|---|---:|
| Teorik oksit kütlesi | 90.61298764 g |
| Teorik LOI bütçesi | 9.38701236 g |
| K2O UMF | 0.32408003 |
| CaO UMF | 0.67591997 |
| Al2O3 UMF | 0.67348171 |
| SiO2 UMF | 4.51985778 |
| SiO2/Al2O3 mol oranı | 6.71118116 |
| Atomik Si/Al | 3.35559058 |

Bu sayılar Cone 6'da erime, matlık, renk veya güvenli kullanım onayı değildir.

## Mevcut seviye

| Bileşen | Çalışan işlev | Sınır |
|---|---|---|
| Element/formül | 118 element kimliği, seçili tabloda 84 kullanılabilir standart kütle, 35 oksit; atom ve kütle hesabı | İzotop seçimi ve tüm elementlerin termofiziksel özellikleri yok |
| Reçete kimyası — yeni | Yukarıdaki kuru baz + ilave + LOI + UMF zinciri | Sınırlı araştırma girişi, gerçek ürün seti henüz kabul edilmedi |
| Termal eğriler | Verilen uygun CTE eğrilerinden serbest genleşme farkı | Çatlama/uyumluluk sertifikası değil |
| Belirsizlik | Sentetik CTE dağılımlarının Monte Carlo yayılımı | Sonuç aralığı fiziksel kusur olasılığı değil |
| 3B araştırma | İdeal iki katmanlı katıda ısı ve lineer termoelastik FEM; ayrı geçici ısı benchmark'ı | Sabit özellikler, ideal arayüz; eriyen sır veya ham bünyenin pişirimi değil |
| GPU | Ayrı basit hesap probu | FEM'in GPU ile hızlandığı gösterilmedi |
| Ürün | Komut satırı araştırma modülleri ve mevcut araştırma görselleri | Birleşik responsive reçete uygulaması/API akışı henüz yok |

Önceki FEM ağ inceltme raporundaki yaklaşık %8.9 değişim yakınsamanın tamamlandığı anlamına gelmez. Bu tur fiziksel deney, gerçek cihaz/browser testi veya FEM yakınsama kampanyası yapılmadı.

## Kaynak incelemesi ve bilimsel kararlar

Erişim: 22 Eylül 2026. Makale metinleri topluca dataset'e alınmadı; aşağıdaki bağlantılar yöntem referansıdır.

1. [Glazy — Chemical Analyses and Formulas](https://help.glazy.org/concepts/analyses) ve [Digitalfire — Glaze Chemistry Basics](https://digitalfire.com/article/189): oksit ağırlığı, mol ve unity temsili için iki teknik referans. Yeni uygulama proje kodudur; bu sitelerin veri tabanı kopyalanmadı. Referans erişimi toplu kullanım izni sayılmaz.
2. [Hanein ve ark., RILEM incelemesi, Materials and Structures 55, 3 (2022)](https://doi.org/10.1617/s11527-021-01807-6): HTML'deki kalsinasyon/dehidroksilasyon bölümleri ve hak bildirimi incelendi; CC BY 4.0, üçüncü taraf materyal istisnaları olabilir. Çalışmanın ana kapsamı çimento için kalsine killerdir, sır yüzeyi değildir. Buradan aldığımız tasarım sonucu: mineral yapı, tane boyutu ve su buharı kısmi basıncı gibi bağlamlar olmadan evrensel dönüşüm sıcaklığı/hızı koymamak. Kinetik katsayı veya yüzey tahmini aktarılmadı.
3. [CIAAW standart atom ağırlıkları](https://ciaaw.org/atomic-weights.htm): paket setindeki Zr/Gd/Lu değerleri ile 2024 güncellemeleri farkı önceki denetimde kayıtlı. Bu tur geçmiş hesapları değiştirmemek için sabit set korunuyor. Ayrı, açıkça seçilen güncel set ve regresyon testleri hâlâ yapılacak; mevcut sete 'en güncel CIAAW' denmiyor.

Bu tur bir tezin tam metni veya sunu doğrulanıp sayısal modele aktarılmadı. Makalenin incelenmesi fiziksel model validasyonu değildir.

## Henüz düşünülmesi gereken süreçler / sonraki kapılar

| Süreç | Gereken kanıt/veri | Uygulama kararı |
|---|---|---|
| Serbest su ve yapısal OH kaybı | Nem bazı, mineralojik analiz, farklı hızlarda TGA/DSC | LOI'den zaman/sıcaklık uydurma; ölçümlü olay verisini önce modelle |
| Karbonat gaz çıkışı ve kabarcık | Mineral miktarı, gaz atmosferi, kinetik, geçirgenlik/viskozite | LOI'yi doğrudan pinhole yüzdesine çevirme |
| Sinterleme ve gözenek kapanması | Dilatometri, porozite, tane boyutu, zaman/sıcaklık | Mevcut pişmiş-katı FEM'e ham bünye gibi davranma |
| Eriyik akışı ve kristalleşme | Bileşime/sıcaklığa bağlı viskozite, faz verisi, soğuma testleri | UMF'den tek erime noktası veya renk üretme |
| Redoks ve uçuculuk | Oksijen potansiyeli, zaman, ilgili faz modelleri | Fe2O3→FeO otomatik dönüşümü yapma |
| Gerilme gevşemesi ve arayüz | Tg, viskoelastisite, E(T), CTE eğrileri, aderans, geometri | CTE farkından çatlama olasılığı üretme |
| Fırından parçaya ısı geçişi | Işınım, emissivite, konveksiyon, yerleşim ve sensörler | Mevcut sınır sıcaklığını gerçek fırın programıyla eşitleme |

Önerilen bir sonraki küçük teslim: sürümlü deneysel TGA/DSC/dilatometri kayıt sözleşmesi ve kaynaklı tek bir ölçüm serisiyle karşılaştırma. Kinetik çözüm bundan sonra, numune/atmosfer/ısıtma hızı sınırlarıyla gelir. Eşzamanlı veri önceliği: 15 karantinadaki adayın baz/LOI/kaynak eksiklerini çözmek; teorik fixture'ları üretici malzemesi diye yayınlamamak.

## Doğrulama ve teknik borç

Son tam çalıştırma: 150 test, 5.820 saniye, OK; atlanan test yok. Başlangıç 138 testti, bu teslim 12 test ekledi.

Yeni testler: bağımsız el hesabı UMF/oran, parça ölçekleme ve sıra değişmezliği, batch ölçekleme, ilave, kuru/kızdırılmış eşdeğerlik, snapshot replay/izolasyon, eksik ve geçersiz girdiler, sıfır payda, teorik demo kütle dengesi ve sayısal underflow. Bunlar yazılım/matematik testidir, fırın sonucu doğrulaması değil.

Motor saf hesap fonksiyonudur; kalıcı AnalysisRun deposu, lisans kabul kapısı, nem dönüşümü, partial sonuç sözleşmesi, yuvarlanmış analiz tolerans politikası ve web entegrasyonu sonraki teslimlerdir. M2/M3 tamamlandı veya tahmin modeli hazır denmemelidir.
