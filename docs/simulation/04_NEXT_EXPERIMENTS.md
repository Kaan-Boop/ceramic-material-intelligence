# Ham malzeme → sır/bünye: izlenecek araştırma yolu

Bu plan bütünüyle tamamlanmış özellik listesi değildir. İlk 3B düşük sıcaklık katı modelinin üstüne tek seferde bütün kimyayı eklemiyoruz. Her alt modelin veri ve deney kapısı var; eksik model UNAVAILABLE kalır.

## Birbirine bağlanacak katmanlar

```text
Ürün/lot + mineralojik analiz + nem + tane boyutu + kaynak/haklar
                 ↓
Reçete / element-oksit-kütle dengesi             Geometri / gözenek / başlangıç hali
                 ↓                                         ↓
Reaksiyon / gaz çıkışı / faz dengesi ← sıcaklık-zaman-atmosfer alanı
                 ↓                                         ↓
Faz oranı / eriyik / gözeneklilik → özellik modelleri → ısı iletimi / deformasyon
                                                            ↓
Gerçek numune ölçümü ← karşılaştırma / duyarlılık / belirsizlik
```

Bu döngüyü çözmek için iterasyon gerekir; sadece bir web sayfasındaki değerleri sırayla çarpmak yeterli değil. Denge sonucu reaksiyon hızı değildir; bir reaksiyonun mümkün olması verilen fırın süresinde tamamlandığını göstermez.

## Sıradaki sınırlı teslimler

| Sıra | İş | Gerekli veri / kabul kapısı | Henüz yapılmayan |
|---|---|---|---|
| S1 | 3B termoelastik doğrulama — bu teslim | Analitik patch testleri, replay, GPU smoke | İki katman için ağ yakınsaması açık; gerçek deney yok |
| S2 | İnce katman çözüm doğruluğu | P2/uygun eleman, en az üç ağ, bağımsız iki-katman eğilme çözümü; seçilen ortalama/eğrilik için önceden belirlenmiş tolerans | Üretim gerilme yorumu bu kapıdan önce açılmaz |
| S3 | Gerçek sıcaklık alanı | k(T), rho(T), cp(T), emissivity, h için yöntem/kapsam; parçada termokupl ölçümü, Kelvin radyasyon ve enerji bilançosu | Fırın setpoint'ini doğrudan tüm parça sıcaklığı yapmayız |
| S4 | Kaynaklı kimya ve termal özellik bağları | M2'den izinli/bazı belli ürün analizi; M3 kütle/mol/UMF; ayrı mineralojik veri | UMF'den otomatik E/CTE/viskozite üretmeyiz |
| S5 | Bir dönüşüm için reaksiyon pilotu | Önce bir malzeme ve bir dönüşüm; ör. kaolin dehidroksilasyonu için TGA/DSC, atmosfer, ısıtma hızı, tane boyutu | Evrensel reaksiyon listesi veya otomatik reaksiyon sıcaklığı yok |
| S6 | Sinterleme / cam geçişi / gevşeme | Dilatometre, porozite, yoğunluk, viskozite/gevşeme verileri; [stoneware model çalışması](https://arxiv.org/abs/1907.07754) ayrıntılı inceleme | Ham büzülme ile tersinir CTE integralini toplarken iki kez sayım yapılmaz |
| S7 | Belirsizlik / deneyle kalibrasyon | Girdilere ölçülmüş dağılım, bağımlılık/korelasyon, model hatası; ayrılmış doğrulama numuneleri | Çatlama yüzdesi ancak dayanaklı kırılma/arayüz modeliyle; şu an kapalı |
| S8 | Gerçek geometriler ve ölçekleme | STL/STEP mesh kalitesi, ince sır tabakası ve birim denetimi; GPU/CPU hata karşılaştırması | Omniverse/OpenUSD isteğe bağlı sahne adaptörü; motorun koşulu değil |

Her teslim sonunda ayrı kanıt/rapor. MOOSE/FEniCSx'e geçiş, ölçülen çözüm veya bağlaşım ihtiyacı ortaya çıkınca karşılaştırılır; mevcut kodun üstüne ikinci bağımsız bilim motoru gizlice eklenmez. Metal/cam malzemeler bu seramik/sır hattı doğrulanmadan açılmaz.

## Veri havuzunun kabul süreci

1. Resmi repo/API/export; hak kapsamı, kaynak ve sürümü belirle. Lisansı bilinmeyeni indirilmiş ve kullanılabilir veri gibi etiketleme.
2. Immutable raw dosya + SHA-256 + okunabilir kaynak dizini. Makale, kod, ölçüm, fixture ve model katsayısı ayrı türler.
3. Ham tablodan dönüşüm: orijinal değer, birim, sıcaklık aralığı, deney yöntemi, bileşim, atmosfer, geometrik bağlam korunur.
4. `rights_review` ve `scientific_review` ayrı kapılar. Açık lisans bilimsel uygunluk anlamına gelmez.
5. Solver'a yalnızca onaylı `PropertyCurve` / `ReactionModel` / `PhaseDatabase` snapshot'ı geçer. Eğitim için ayrı izin gerekir.
6. Parametreler başka çalışmadan aktarılmışsa aynı malzeme oldukları varsayılmaz; kapsam dışı deneyde sonuç vermekten kaçınılır.

Önerilen gelecek kayıtlar (henüz entity implementasyonu değil):

- `PropertyCurve`: property, material_revision, state, temperature grid, value/unit, method, uncertainty, temperature/atmosphere domain, source hash.
- `ReactionModel`: dengelenmiş türler, basis, extent, kinetik yasa, Arrhenius katsayıları ve birimleri, fit protocol, geçerli sıcaklık/hız/atmosfer.
- `PhaseDatabase`: element/pseudo-element ayrımı, fazlar, Gibbs fonksiyonları, TDB lisansı, compositional domain, değerlendirme yayını.
- `SimulationCase`: mesh hash, malzeme bölgeleri, sınır/başlangıç koşulları, solver settings, bağımlı modeller/sürümler.
- `ValidationExperiment`: numune kimliği, gerçek fırın kaydı, ölçüm cihazı, kalibrasyon, tekrar ve hangi hipotezi sınadığı.

Latent ısı cp(T)'ye dahil bir ölçümden geliyorsa ayrıca reaksiyon entalpisi eklenip çift sayılmamalı. Aynı şekilde sinterleme hacim değişimi, termal genleşme ve faz dönüşümü şekil değiştirmeleri açıkça ayrılmalı.

## Olasılık konusunda sınır

Monte Carlo, seçilen girdi dağılımlarını ileri taşır; bilinmeyen reaksiyonları keşfetmez ve kendi başına fiziksel doğruluk kazandırmaz. Başlangıçta aralık senaryosu/OAT; sonrasında ölçülmüş belirsizlik ve korelasyonla örnekleme, örnek sayısı/seed/yakınsama kaydı. Olasılık çıktısı bir varsayım koşullu sonuçtur. Malzeme dayanımı/çatlak boyutu/arayüz dayanımı verisi olmadan “%X çatlar” üretilmez. Bir modelin kendi denklemine uyması, gerçek deneyle sınanmasıyla aynı şey değildir.

## İlk fiziksel veri paketi

Henüz üretici/ürün seçilmediğinden ilk gerçek deney tasarımı tamamlanamaz. Yazılım işi ilerleyebilir; gerçek validasyon için daha sonra bir bünye ve bir sır, ürün/lot analizi, aynı pişirimden en az karşılaştırmalı numuneler ve uygun laboratuvar ölçümleri gerekir. Fırın kontrolüne komut gönderilmeyecek. Güvenli fiziksel deney protokolü ekipman/üretici sınırları ve ilgili uzmanlıkla ayrıca hazırlanacak.
