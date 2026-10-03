# Fizik sözleşmesi — research-v1

## Malzeme durumu ve epistemik etiket

Kabul edilen tek malzeme durumu `FIRED_SOLID_IDEALIZED`, tek veri niteliği `SYNTHETIC`. `RAW_POWDER`, eriyik ve gerçek ölçüm etiketi bu ilk sürümde açık hata verir. Böylece bir hammadde analizini yanlışlıkla pişmiş katı mekaniğine bağlamak mümkün değildir.

Fizik alanı sonuçları: `PREDICTED / DETERMINISTIC / SYNTHETIC + IDEALIZED`. Bir PDE'nin deterministik çözülmesi fiziksel gerilmeyi gözlem veya kesin hesap haline getirmez. Analitik çözümle fark, düğüm sayısı ve artık hesabı ise `CALCULATED` sayısal doğrulama bilgileridir. Belirsizlik ölçülmedi; sıfır olarak sunulmaz.

## Birimler ve girdiler

- Geometri ve yer değiştirme m; sıcaklık girdisi °C, farklar K; E/gerilme Pa.
- Isıl iletkenlik W/(m K); yoğunluk kg/m³; özgül ısı J/(kg K); CTE K⁻¹.
- Her malzemede kimlik, source_ref, durum, nitelik ve sıcaklık geçerlilik aralığı zorunlu.
- k, rho, cp, E pozitif/sonlu; Poisson aralığı bu düşük mertebeli yer değiştirme formülasyonu için (-0.9, 0.45). Üst sınır kilitlenme riskini azaltan proje kısıtıdır; tüm fiziksel malzemeleri tanımlamaz.
- Sıcaklık geçerlilik aralığı dışına ekstrapolasyon yok. Referans sıcaklığı da kontrol edilir. Termal gerinim için %1 araştırma üst sınırı; evrensel doğruluk sertifikası değildir.
- Doğrudan çözücü prototipinde en fazla 20.000 düğüm. Bu bellek/performance garantisi değil; yanlışlıkla dev deney başlatmayı sınırlar.

## Isı

Steady: `div(k grad T) = 0`. Alt ve üst yüzeyde Dirichlet sıcaklık, yanlarda sıfır ısı akısı. Arayüz mükemmel termal temas; temas direnci yok. İki katman sınırına tam oturan P1 tetrahedral ağ.

Transient benchmark: `rho cp dT/dt - div(k grad T) = 0`.

`(M/dt + K) T_next = M T_previous / dt`; backward Euler. Bu benchmark'ta **tüm dış yüzeyler** sabit sıcaklıkta. Başlangıç sınırıyla uyumsuz giriş reddedilir. Bu denklem doğrulaması ana HTML'nin zamana bağlı fırın animasyonu olduğu anlamına gelmez.

Gerçek fırın için sonraki sınır koşulu konveksiyon ve radyasyondur: `q = h(T_gas - T_surface) + epsilon*sigma_SB*(T_surroundings^4 - T_surface^4)` işaret seçimi ve mutlak K ile uygulanmalı. Henüz uygulanmadı. Fırın programındaki setpoint, parça yüzey sıcaklığına eşit değildir.

## Mekanik

`epsilon = (grad u + grad u^T)/2`

`epsilon_thermal = alpha (T - T_ref) I`

`sigma = 2 mu (epsilon - epsilon_thermal) + lambda tr(epsilon - epsilon_thermal) I`

`mu = E/[2(1+nu)]`, `lambda = E nu/[(1+nu)(1-2nu)]`; mekanik denge `div sigma = 0`.

Zayıf forma termal yük pozitif sağ taraf olarak girer. Gerilme çıktısında termal gerinim çıkarılır; ısıtılan tamamen tutulmuş katıda basınç (negatif asal gerilme) oluşması test edilir.

Kaynaklar: [bağlaşık termoelastik formülasyon](https://bleyerj.github.io/comet-fenicsx/tours/linear_problems/thermoelasticity_weak/thermoelasticity_weak.html) ve [bağımsız scikit-fem elastisite uygulaması](https://github.com/kinnala/scikit-fem/blob/a9c43abbc3b17c36a059132c9f571447b755920e/docs/examples/ex11.py). Bizim sayısal sonuçlarımız ayrıca serbest genleşme ve tam kısıtlı hidrostatik analitik çözümleriyle sınanır. Bu iki yazılım kaynağı fiziksel malzeme deneyinin yerini tutmaz.

Sınır koşulu `RIGID_MODES_ONLY_321`: (0,0,0)'da xyz, (L,0,0)'da yz, (0,W,0)'da z yer değiştirmesi sabit. Altı rijit hareket kaldırılır; tüm alt yüzey yapıştırılmaz. Referans sıcaklığında gerilmesiz, mükemmel bağlı iki katı; dış kuvvet yok. Pin yakınları ve serbest kenar tepe gerilmeleri bağımsız yakınsama kontrolü gerektirir. `ALL_NODES_FIXED` yalnızca analitik test seçeneğidir.

P1 elemanda şekil değiştirme sabit; sıcaklık doğrusal olabilir. Gerilme Gauss noktalarında hesaplanır, hücre hacim ortalaması olarak dışa aktarılır. Arayüzdeki iki farklı malzemenin gerilmeleri düğüm ortalamasıyla yapay biçimde yumuşatılmaz. Gösterilen sigma_1 hücre-ortalama tensörün en büyük özdeğeridir; Gauss noktası maksimumu değildir. Pozitif çekme, negatif basınç. Von Mises bir seramik kırılma ölçütü gibi kullanılmaz.

## Çözülmeyenler

Sıcaklığa bağlı E/k/cp/CTE, faz dönüşümleri, kuvars dönüşümü, viskoelastik gevşeme, cam geçişi, sinterleme büzülmesi, gözenek değişimi, çatlak yayılması, arayüz ayrılması, gaz çıkışı, eriyik akışı, kristallenme, kimyasal reaksiyon kinetiği ve termokimyasal denge **uygulanmadı**.

Referans 80 °C, nihai 30 °C seçimi sentetik ve düşük sıcaklık aralığında doğrulama içindir; gerçek sırın gerilmesiz sıcaklığı olduğu iddia edilmez. 1200 °C gibi bir pişirim değeri bu fixture'da reddedilir. Ham çamurun pişirim büzülmesi `alpha * delta_T` ile taklit edilmez.

Bir malzemenin ham, kurumuş, bisküvi, eriyik ve pişmiş durumları ayrı özellik seti/evrim yasaları gerektirir. Reçete oksit analizi tek başına k(T), E(T), cam geçişi veya kırılma dayanımı sağlamaz.
