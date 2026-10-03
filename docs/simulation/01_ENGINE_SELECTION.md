# Motor ve kaynak seçimi

İnceleme: 2026-09-21. GitHub bağlantısı ve NVIDIA Skills canlı kataloğu kullanıldı. Motor lisansı ile motorun yanında bulunan veri dosyasının lisansı ayrı değerlendirildi. Tablodaki “araştırıldı” ifadesi kurulduğunu veya deneysel olarak doğrulandığını ifade etmez.

## Bu turdaki karar

Kendi motorumuz, malzeme durumunu ve fizik sözleşmelerini yöneten proje katmanıdır. Matris montajı, lineer çözüm ve GPU derleyicisini yeniden yazmıyoruz. İlk adaptör scikit-fem + SciPy; NVIDIA Warp ayrı donanım testi. Modüler monolit/Python domain planı korunur. Bu araştırma henüz üretim `ceramic_engine` paketi değildir.

| Sistem / birincil kaynak | İşlev / seramikte kullanımı | Lisans ve erişim | Bu turdaki işlem / sınır |
|---|---|---|---|
| [scikit-fem](https://github.com/kinnala/scikit-fem), [3B örnekler](https://scikit-fem.readthedocs.io/en/stable/listofexamples.html) | FEM montajı; ısı ve elastisite | BSD-3-Clause; PyPI ve resmi GitHub | 12.0.2 kuruldu; lisans, README, iki örnek arşivlendi. Malzeme veri tabanı sağlamaz. |
| [NVIDIA Warp](https://github.com/NVIDIA/warp) | CPU/CUDA çekirdekleri ve `warp.fem` altyapısı | Apache-2.0; PyPI, resmi GitHub | 1.17.0 kuruldu; lisans, README, 3B/2B difüzyon örnekleri arşivlendi. Kendi basit çekirdeğimiz CPU/GPU'da sınandı; GPU FEM henüz entegre değil. |
| [MOOSE phase field](https://mooseframework.inl.gov/modules/phase_field/), [heat transfer](https://mooseframework.inl.gov/modules/heat_transfer/index.html) | Sonraki aşamada ısı, mekanik, faz alanı bağlaşımı | [Resmi repo](https://github.com/idaholab/moose); hedef sürümün tüm lisans/bağımlılık incelemesi kurulum öncesi yapılmalı | Araştırıldı; indirilmedi/kurulmadı. Ayrı Linux/build ortamı ve model kalibrasyonu gerektirir. |
| [FEniCSx / DOLFINx](https://github.com/FEniCS/dolfinx) | Bağımsız FEM karşılaştırma adayı | Resmi repo; hedef sürüm/bağımlılık hak incelemesi bekliyor | Kurulmadı; ikinci çözücü kullanımı şu an test edilmiş değil. |
| [pycalphad](https://github.com/pycalphad/pycalphad) | Gibbs enerjisi tabanlı faz dengesi; uygun TDB ile | Kod ve her TDB ayrı incelenmeli | Kurulmadı. Bir oksit TDB'si bulunması tüm sır bileşenlerinin kapsandığı anlamına gelmez. |
| [Cantera](https://www.cantera.org/stable/python/thermo.html) | Gaz/reaksiyon mekanizmaları ve termodinamik alt sistemler | Resmi belgeler; seçilecek mekanizmanın hakları ve geçerliliği ayrı | Kurulmadı; hazır evrensel sır eriyiği/kinetik veri tabanı varsayılmıyor. |
| [NVIDIA PhysicsNeMo](https://github.com/NVIDIA/physicsnemo) | Fizik verisinden öğrenen modeller, daha sonra surrogate | Resmi repo/katalog; model/veri hakları ayrıca incelenmeli | Yalnızca aday. Doğrulanmış FEM ve deney verisinin yerine geçmez; kurulmadı. |
| [PhysX](https://github.com/NVIDIA-Omniverse/PhysX) | Etkileşimli mekanik/dinamik altyapısı | Resmi repo; seçilecek modülün lisansı ayrıca incelenmeli | Sır pişirimi/reaksiyon motoru olarak seçilmedi. |
| [OpenUSD](https://github.com/PixarAnimationStudios/OpenUSD) / Omniverse | Geometri, sahne ve uygulamalar arası veri paylaşımı | Format ile NVIDIA ürün/servis koşulları farklı | İlk HTML/VTK çıktısı yeterli; bu tur kurulmadı. Sahne standardı termodinamik model değildir. |

## İndirilenler ve hak kapsamı

[Manifest](../../data/manifests/simulation-sources-2026-09-21.json): **2 kaynaktan 8 dosya, 89.122 byte**. Tam repository klonu değildir. Paket dağıtımlarındaki motor kodları ayrıca izole venv içinde kurulu.

- scikit-fem commit: `a9c43abbc3b17c36a059132c9f571447b755920e`.
- Warp commit: `f4c57f26f1e3936a89afd283e39fcabf6d548dc7`.
- Orijinal lisans ve telif bildirimleri korundu; yeniden dağıtımda bunlar ve bağımlılıkların bildirimleri ayrıca taşınmalı. Ticari kullanım izni patent/marka garantisi veya bütün üçüncü taraf veriler için toplu izin değildir.
- Erişim: sabit commit'e resmi raw dosya indirmesi, saniyede en fazla bir istek, dosya başına 8 MiB. Site kazıması yapılmadı; arşivlenen örnekler otomatik çalıştırılmadı.
- Önceki M2 makaleleri/katsayı adayları yerinde duruyor; hiçbir karantina kaydı yeni modele gerçek malzeme girdisi yapılmadı.

## Kritik TDB bulgusu

pycalphad test havuzundaki [C_A_S_Fe_O_M.tdb](https://github.com/pycalphad/pycalphad/blob/develop/pycalphad/tests/databases/C_A_S_Fe_O_M.tdb) Portland çimentosu klinkeri bağlamına ait bir CaO–Al2O3–SiO2–Fe–O–MgO modelidir. Bu **sürümü sabitlenmemiş araştırma bağlantısıdır**, üretim girdisi değil. Dosya, A/Q/L/M gibi oksit esaslı pseudo-elementler içeriyor. Bunları atomik Al/Si/Ca/Mg gibi yorumlamak yanlış kütle dengesi üretir. Na/K/B içeren sırlar için otomatik genişletilemez. Dosyanın bağımsız veri hakları ve faz/bileşim/sıcaklık kapsamı açıkça onaylanmadığından yerel veri havuzuna alınmadı.

[al2o3_nd2o3_zro2.tdb](https://github.com/pycalphad/pycalphad/blob/develop/pycalphad/tests/databases/al2o3_nd2o3_zro2.tdb) içinde üçüncü taraf telif bildirimi bulunması, repository kod lisansını verilere genellememek için ikinci somut örnek. Bu dosya da import edilmedi. Sonraki inceleme tam commit, orijinal değerlendirme yayını, lisans sahibi ve kapsanan fazları sabitlemeli.

## Birincil bilimsel okumalar

| Kaynak | Bize sağladığı yöntem | İnceleme / yeniden kullanım sınırı |
|---|---|---|
| [Gustafsson & McBain, scikit-fem, JOSS, DOI 10.21105/joss.02369](https://doi.org/10.21105/joss.02369) | Seçilen FEM yazılımının yöntem/uygulama kaynağı | Kaynakça; seramik katsayı kalibrasyonu değil |
| [J. Bleyer, Linear thermoelasticity](https://bleyerj.github.io/comet-fenicsx/tours/linear_problems/thermoelasticity_weak/thermoelasticity_weak.html) | Isıdan gerilmeye zayıf bağlaşım ve izotrop termal gerinim | Denklemler incelendi; ders kodu kopyalanmadı |
| [Papathanasiou, Dal Corso, Piccolroaz, 2015](https://arxiv.org/abs/1512.00326) | Sıcaklığa bağlı özellikler, radyasyon, refrakterde termal şok için FEM | Özet incelendi; Al2O3 refrakter çalışması sır/bünye kalibrasyonu değildir; tam metin/veri import edilmedi |
| [Kempen, Piccolroaz, Bigoni, 2019](https://arxiv.org/abs/1907.07754) | Ham seramik presleme ve sinterlemede elastik-viskoplastik model, dilatometreyle parametreleme | Özet incelendi. arXiv lisansı arXiv'e dağıtım hakkı veriyor; bize açık veri yeniden dağıtım/eğitim lisansı sayılmadı. Tam metin/veri import edilmedi. |
| [Oyedeji ve diğerleri, 2023, Phys. Rev. E 108, 025301](https://doi.org/10.1103/PhysRevE.108.025301) | İzotermal olmayan sinterlemede nicel faz alanı ve arayüz artefaktları | Özet incelendi; parametreleri körlemesine aktarılmadı. Tam metin/veri hak incelemesi bekliyor. |
| [Viscoelastic FEA of residual stresses in porcelain-veneered zirconia crowns, PMC5920712](https://pmc.ncbi.nlm.nih.gov/articles/PMC5920712/) | Cam geçişi/soğumada viskoelastik gevşemenin önemi için aday bağımsız çalışma | Arama özeti düzeyinde; tam metin erişimi CAPTCHA ile engellendi, aşılmadı. Dental malzemeyi stoneware verisi saymıyoruz. |

Bir makale sayfasını görmek veri lisansı değildir. Bu tabloda bizim yöntem değerlendirmemiz var; tablolar/fotoğraflar/tam metinler açık izin olmadan havuza kopyalanmadı. Yeni gerçek malzeme katsayısı sayısı: **0**.

## NVIDIA Skills kararı

İstenen keşif becerisi kullanıldı. CLI katalog sorgusu sonuç vermediği için resmi `NVIDIA/skills` canlı GitHub kataloğu incelendi. Katalogdaki `physicsnemo-discover` sonraki SciML aşamasına; `omniverse-cad-to-simready` farklı CAD/sahne iş akışına; `warp-eval` hazır bir GPU sıcak yolunu değerlendirmeye yönelik. Hiçbiri mevcut analitik FEM doğrulamasının yerine geçmez. Yeni agent skill kurulmadı; mevcut NVIDIA becerisi bu ayrımı yapmamızı sağladı. İleride bir skill kurulumu gerekirse ayrıca onay istenir. Warp Python paketi kurulumu bu beceri kurulumundan ayrı ve kullanıcının motor kurma yetkisi kapsamındadır.
