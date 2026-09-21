# Sır–bünye fizik araştırması

Kontrol tarihi: 2026-09-21. Kullanıcının son yönlendirmesi: önce seramik ve sır; metal ve diğer yabancı malzemeler daha sonra. Bütün fizik alanları tasarımda korunacak, fakat eksik alanlar hesaplanmış gibi gösterilmeyecek.

## Karar ve teslim sınırı

Bu çalışma M2 yanında yürütülen **sınırlı bir araştırma prototipidir**. M2 gerçek kimya referans seti tamamlanmış, M3 kimya motoru kurulmuş veya M4 web arayüzü bitmiş sayılmaz. ADR-014'ün üretim kısıtı sürer. Yeni kod `research/thermal/` altında izole tutulur; doğrulama sonrası bağımsız `ceramic_engine` paketine taşınabilir. Ağ, veritabanı ve dosya erişimi `core.py` içinde yoktur.

FEM (sonlu elemanlar yöntemi), uzaydaki bir problemi küçük parçalara ayırarak çözme yöntemidir; FEA bu yöntemle yapılan analizdir. Çözücü; malzeme yasası, özellikler, geometri ve sınır koşulları gerektirir. Genel bir FEM yazılımı indirmek seramik için bu girdileri sağlamaz.

## Omniverse'den hangi fikri alıyoruz?

Öneri: ürünün kodunu veya arayüzünü birebir kopyalamak yerine, ayrı verileri ortak sahnede birleştiren ve farklı hesap araçlarını bağlayan yapıyı benimsemek. [OpenUSD](https://openusd.org/release/intro.html), sahne/veri alışverişi ve katmanlı bileşim sağlar; bizim kimya veritabanımızın veya reaksiyon çözücümüzün yerine geçmez.

Hedef veri akışı (bu katmanların tümü henüz uygulanmadı):

```text
Sürümlü Material / Recipe / Property / Experiment kayıtları
                          |
                SimulationCase snapshot
        geometri + katman + koşul + özellik kapsamı
                          |
                   Capability check
                          |
          Seçilen solver adapter'ları
     kimya | termal | mekanik | faz | kinetik
                          |
                 SimulationRun / alan sonuçları
                          |
          grafik / tablo / ileride OpenUSD görüntüleme
```

Bu bir bağlantı haritasıdır; bütün çözücüler her analizde sırayla çalışmaz. Bağlaşım gerektiğinde bağımlılıklar ve iterasyon/yakınsama açık tanımlanır. Isı, gerilme veya faz sonuçları tek bir evrensel "başarı yüzdesine" indirgenmez. Render malzemesi ile bilimsel malzeme özellikleri ayrı tutulur.

Gelecekte `SimulationCase` input hash, recipe/body revision, property snapshot, geometry hash, mesh, boundary conditions ve solver seçimlerini taşır. `SimulationRun` solver/model sürümü, toleranslar, convergence, mesh/time-step kontrolü, kaynaklar, varsayımlar ve kullanılamayan bölümleri saklar. Yakınsamama veya kapsam dışı özellik, yeşil başarı göstergesi oluşturmaz.

## Araç değerlendirmesi

| Araç | Bizim için rolü | Sınır / karar |
|---|---|---|
| OpenUSD / Omniverse | İleride sahne, katman, geometri ve sonuç görüntüleme | Başlangıç bağımlılığı değil; renderer görüntüsü deney sonucu değildir. OpenUSD kendi açık lisansına sahip; Omniverse bileşenlerini aynı lisans altında varsaymayız. |
| [MOOSE](https://mooseframework.inl.gov/source/materials/ComputeInstantaneousThermalExpansionFunctionEigenstrain.html) | Bağlaşık termal/mekanik model için aday | Depodaki [LICENSE](https://github.com/idaholab/moose/blob/master/LICENSE) LGPL-2.1 metni; seçilen sürüm/bağımlılıklar kurulum öncesi ayrıca incelenir. Bu teslimde kurulmadı. |
| [FEniCSx/DOLFINx](https://github.com/FEniCS/dolfinx) | Denklemleri açıkça tanımlanan küçük 2D FEM araştırmaları | LGPL-3.0-or-later. Windows için ek çalışma ortamı gerekebilir; ilk FEM karşılaştırma deneyi için aday, kesin ürün tercihi değil. Kurulmadı. |
| [pycalphad](https://pycalphad.org/docs/latest/examples/EquilibriumWithOrdering.html) | Seçilmiş bileşen/faz kümesinde termodinamik denge | Uygun termodinamik veritabanı gerekir; örnek metal TDB dosyası bir sır TDB'si değildir. Denge, gerçek pişirimdeki reaksiyon hızlarını vermez. |
| [PhysicsNeMo](https://github.com/NVIDIA/physicsnemo) | İleride doğrulanmış fizik modellerinin ML yaklaştırıcıları | Eksik malzeme ölçümlerini tamamlayan bir seramik veri kaynağı değil. Model/veri doğrulaması öncesi bağımlılık yapılmayacak. |

Bu kaynaklardan kod kopyalanmadı; yeni haricî paket, GPU servisi, hesap veya ticari lisans kurulmadı. Kaynak okumak, içerik/veri yeniden yayın izni değildir.

### NVIDIA beceri kontrolü

NVIDIA skill-finder kullanıldı. Yerel katalog CLI çağrısı bulunamadığından [resmî canlı katalog](https://raw.githubusercontent.com/NVIDIA/skills/main/skills.sh.json) kontrol edildi. İki ileri-aşama adayı:

- `omniverse-cad-to-simready`: geometri/varlıkların simülasyona hazırlanması. İncelenen kart Linux/macOS, bazı yollar için GPU/Docker/servis anahtarı gerektiriyor; mevcut Windows prototipine doğrudan gerekli değil. İlk uygun istem: "Bu test plakası geometrisini, bilimsel özellik uydurmadan yalnızca USD dönüşümü ve doğrulaması açısından değerlendir."
- `physicsnemo-discover`: fizik-ML örneklerini araştırma rehberi; motor veya hazır seramik model değil. İlk uygun istem: "Doğrulanmış 2D termal FEM sonuçlarını hızlandıracak surrogate seçeneklerini ve veri ihtiyaçlarını karşılaştır."

Yalnızca ileride ayrı açık onayla kurulabilecek komutlar (çalıştırılmadı):

```sh
npx skills add nvidia/skills --skill omniverse-cad-to-simready --agent codex --global --yes
npx skills add nvidia/skills --skill physicsnemo-discover --agent codex --global --yes
```

## Bütün modüller için kapsam haritası

| Alan | Gerekli temel girdiler | Üretebileceği çıktı | Bugünkü durum |
|---|---|---|---|
| Oksit/molar kimya | Ürün/lot analizi, baz, LOI, reçete | Oksit dengesi, mol, UMF | M3 planı; bu teslimde yok |
| Termal serbest şekil değişimi | Uyumlu α(T), sıcaklık referansı, uzunluk | Serbest strain ve iki malzemenin farkı | Sentetik doğrulamalı araştırma prototipi |
| Isı transferi | k(T), Cp(T), yoğunluk, geometri, ışınım/konveksiyon, gerçek program | Numune içi T(x,t), sıcaklık farkları | Planlandı; katsayı ve deney eksik |
| Sır–bünye mekaniği | E(T), ν(T), kalınlık, bağ/mesnet, α(T), gevşeme | Gerilme, eğilme, deformasyon | Planlandı; ilk ideal çift tabaka benchmark'ı sonra |
| Termodinamik | Lisanslı/izinli Gibbs verisi, fazlar, bileşim, gaz koşulları | Tanımlı sistem için denge fazları | Uygun seramik TDB doğrulanmadı |
| Reaksiyon kinetiği | Hız/aktivasyon parametreleri, t-T, tane boyutu, atmosfer | Reaksiyon ilerleme tahmini | Planlandı; denge hesabından otomatik türetilmez |
| Sinterleme / gözeneklilik | Dilatometri, yoğunlaşma ve gaz çıkışı ölçümleri | Kalıcı büzülme, yoğunlaşma | Planlandı; termal strain ile karıştırılmaz |
| Eriyik / akış / kristalleşme | Viskozite, yüzey gerilimi, kinetik veriler | Akış, kristal gelişimi için sınırlı tahminler | Planlandı; fotoğraf benzerliği bu ölçümlerin yerine geçmez |
| Belirsizlik / ihtimal | Girdi dağılımları, bağımlılıkları, model hatası | Koşullu sonuç dağılımı, sonra doğrulanmış kusur olasılığı | OAT duyarlılık var; Monte Carlo / ML yok |
| Metal / cam arayüzleri | İlave termokimya, oksidasyon, plastisite, bağ özellikleri | Ayrı araştırma alanları | Kullanıcının kararıyla sonraya bırakıldı |

Bu liste bir bilimsel araştırma gündemidir; parametrelerin etkisi her reçete için kanıtlanmış kabul edilmez.

## "Bütün kimyasal reaksiyonları görmek" hedefinin karşılığı

Tam evrensel reaksiyon çözümü vaadi vermiyoruz. Önce **reaksiyon kapsamı kayıtları** tasarlayacağız: bileşen/faz kümesi, denklem, atom/yük dengesi, kaynak, T/P/atmosfer alanı, Gibbs/hız parametresi olup olmadığı, gözlenen kanıt ve eksikler. Bunlar gelecekteki `ReactionDefinition`, `ReactionEvidence`, `ThermodynamicAssessment` ve `KineticModel` kayıtlarıdır; bu teslimde veri tabanı oluşturulmadı.

Üç ayrı görünüm önerilir: kaynakta bildirilen olası reaksiyon; seçilmiş modelin öngördüğü faz/reaksiyon; deneyde ölçülmüş dönüşüm. Bilgi grafiğinde denklem göstermek, pişirimde o reaksiyonun gerçekleştiğinin kanıtı değildir. LOI tek başına hangi gazın hangi hızda çıktığını tanımlamaz. CALPHAD girdisinde bulunmayan fazları sonuç listesinde yok diye imkânsız saymayacağız.

İlk kapsam kapısı "bütün reaksiyonlar tamam" değil: seçilen sır–bünye çiftinde sorulan çıktı için önemli süreçlerin hangilerinin kapsandığı, hangilerinin ölçülmediği ve sonucu nasıl sınırlandırdığı yazılı olmalı.

## Çalışan prototipin bilimsel sözleşmesi

Küçük şekil değişimi, izotropik ve tersinir termal model:

```text
epsilon_g = integral[Tref -> T] alpha_g(theta) dtheta
epsilon_b = integral[Tref -> T] alpha_b(theta) dtheta
mismatch  = epsilon_g - epsilon_b
delta_L   = Lref * epsilon
```

Sabit α için ε = α ΔT. Sıcaklık farkında °C ve K aynı artışa sahiptir. α birimi `1/K`; strain boyutsuz, uzunluk mm. Girdi `TANGENT_SMALL_STRAIN` yaklaşımıdır: gerçek anlık `(1/L)dL/dT` ile sonlu şekil değişimi çözümü değildir; küçük-strain doğruluğu dışında kullanılmaz. Mean/secant CTE veya doğrudan dilatasyon ayrı veri türleridir ve otomatik dönüştürülmez.

[MOOSE anlık genleşme modeli](https://mooseframework.inl.gov/source/materials/ComputeInstantaneousThermalExpansionFunctionEigenstrain.html) sıcaklığa bağlı katsayıyı trapez kuralıyla biriktirir. Biz doğrusal parçalarda bütün düğümlerden geçerek integrali alıyoruz; bu interpolant için integral tamdır, gerçek malzeme modeli için "kesin" demek değildir. Bağımsız karşılaştırma [Bleyer'in FEniCSx termoelastisite anlatımı](https://bleyerj.github.io/comet-fenicsx/tours/linear_problems/thermoelasticity_weak/thermoelasticity_weak.html): sabit α termal strain'i mekanik gerilme bağıntısından ayırır. İkinci FEM çözücüsü bu bilgisayarda çalıştırılmadı; karşılaştırma doküman/formül ve elle hesap düzeyindedir.

Sıcaklık noktaları artan sırada, en az iki adet olmalı; ekstrapolasyon yasak. Bilinen negatif α yasaklanmaz. Sonlu olmayan/bool sayılar, kaynaksız eğri, belirsiz katsayı türü, desteklenmeyen alan ve birim reddedilir. %1 mutlak birikimli strain yazılım kapsam sınırıdır; çatlama eşiği veya evrensel fizik kanunu değildir. Eksik belirsizlik `null` olur.

Referans sıcaklığı seçilen bir karşılaştırma başlangıcıdır; Tg veya gerçek gerilmesiz sıcaklık olarak yorumlanmaz. Bu modelde soğuma hızı yoktur; aynı sıcaklık uçları aynı sonucu verir. Soğuma hızının etkisini incelemek için kinetik/viskoelastik model gerekir. Kalınlık ve geometri etkisi hesaplanmadığından bu model bonded bilayer veya FEM değildir.

Sonuç sınıfı `PREDICTED / DETERMINISTIC / THEORETICAL`: fiziksel davranış için varsayımlı model çıktısıdır. Matematik deterministik olsa da gerçek numunenin ölçümü değildir. `contains_synthetic_inputs` ayrıca verilir. Kaynak kimliği saklanır, bu prototip kaynak doğruluğunu otomatik onaylamaz.

## Duyarlılık ve ihtimal politikası

OAT (one-at-a-time) her girdiyi tek tek verilen ±adımla değiştirir. α değişimi tüm eğriye sabit offset'tir; sıcaklık ve uzunluk ayrı değiştirilir. Bu adımlar ölçülmüş hata payı değildir. Farklı birim/adım büyüklüklerini kullanıp evrensel önem sırası çıkarılmaz; etkileşimli/global duyarlılık değildir.

[NIST Uncertainty Machine](https://uncertainty.nist.gov/about/about_English.md.html) açık fonksiyon, girdi dağılımları ve korelasyonlarla belirsizlik yayılımı yaklaşımını açıklıyor. İleride Monte Carlo için veri kökenli dağılım/bağımlılık, örnek sayısı, seed, yakınsama ve model hatası kaydedilecek. Bileşim yüzdeleri bağımsız rastgele oynatılmayacak; toplam/baz kısıtları korunacak.

Bir modelde `P(|strain farkı| > seçilmiş eşik)` hesaplanması **çatlama olasılığı değildir**. Çatlama için gerilme/fraktür modeli veya uygun bağımsız deneylerden kalibre edilmiş istatistik gerekir. Hatalı modelin çok sayıda kez çalıştırılması doğruluğunu artırmaz. Bugünkü raporda gerilme, kusur olasılığı, reaksiyon ve hız etkisi açıkça `UNAVAILABLE` karşılığı gerekçelerle listelenir.

## Çalıştırma

Proje kökünde, Python 3.12:

```sh
python -m research.thermal data/fixtures/thermal-synthetic.json
python -m research.thermal data/fixtures/thermal-synthetic.json --output storage/thermal/demo-v1.json
python -m unittest discover -s tests -v
```

Çıktı dosyası varsa üstüne yazmaz; yeni ad seçilir. JSON snapshot ve hash replay için saklanır. Bu CLI prototipidir; HTML/web, sahne editörü veya fırın kontrol yazılımı değildir. GPU ve yeni paket gerekmez.

## Sonraki kapılar

1. M2: izinli gerçek ürün analizleri; buna paralel sır ve pişmiş bünyenin kaynaklı dilatometri/α(T) ölçümlerini arama. Isıtma/soğutma dalı, ölçüm geçmişi ve referans uzunluğu ayrı kaydedilmeli.
2. M3–M4: doğrulanmış kimya çekirdeği ve ilk web akışı; fizik verisi bulunmayan reçeteye otomatik CTE atanmamalı.
3. Termal araştırma: ölçüm kapsamıyla replay, bağımsız hesap ve bir sır–bünye çiftinde fiziksel ölçüm karşılaştırması.
4. Mekanik araştırma: önce analitik çift tabaka benchmark'ı; sonra FEniCSx veya MOOSE adaylarından biriyle aynı durum. Kuvvet/moment dengesi, ağ ve zaman-adımı yakınsaması kontrol edilir. Sınır koşulu değişince yorum da değişir.
5. Denge ve kinetik için lisansı ve seramik bileşim kapsamı uygun veri bulunduğunda ayrı adapter. İlgisiz metal TDB'siyle sır sonucu üretilmez.
6. Yeterli bağımsız test sonrası belirsizlik/olasılık kalibrasyonu. Metal modülü bu temelin ardından ayrı kapsam onayıyla ele alınır.

Teknik borç: şimdilik JSON CLI, küçük-strain yaklaşımı, tek scalar sıcaklık ve elle verilen provenance. Gerçek ölçüm importer'ı, birim dönüştürücü, veri hak kapısına entegrasyon, FEM solver, model hata tahmini ve UI yok. Hiçbiri tamamlanmış gibi sunulmayacak.
