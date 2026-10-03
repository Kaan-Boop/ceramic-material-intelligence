# Termal belirsizlik araştırması — 22 Eylül 2026

## Teslim ve kapsam

`research/thermal/uncertainty.py` mevcut serbest termal gerinim motorunu kullanır. Yeni bağımlılık yok. Mevcut 3B FEM, veri edinme ve arayüz dosyaları değiştirilmedi. Bu teslim M2/M3/M4 tamamlandı anlamına gelmez.

Her malzemenin tüm α(T) eğrisine tek bir sabit sapma eklenir. Sapmalar ayrı ayrı uniform(-h, h) dağılımından çekilir; iki malzeme arasında bağımsızlık **varsayılır**. Eğri içindeki noktalar aynı sapmayı paylaşır. Sıcaklıklar ve uzunluk sabittir. Sadece SYNTHETIC girdiler kabul edilir; ölçümden dağılım tahmini yapılmaz. h=0 sabit parametredir.

Fonksiyon: `propagate(scenario, glaze_half_width_per_k=..., body_half_width_per_k=..., samples=..., seed=...)`. 100–100.000 örnek; yerel RNG, giriş snapshot/hash ve iki model sürümü. Aynı Python/model sürümü ve girdilerle yeniden üretilebilir; farklı çalışma zamanlarında bit düzeyinde eşitlik taahhüdü yok.

Destek aralığının köşeleri hesaplanmadan örneklemeye başlanmaz. Model kapsamı dışına çıkan dağılım reddedilir; kırpma, yeniden çekme veya başarısız örnekleri sessiz silme yok. Bu doğrulama yalnızca bu doğrusal, sabit sapmalı model içindir.

## Denklemler ve bağımsız kontrol

`D = integral(alpha_glaze - alpha_body, Tref, Ttarget)`.

Sapma nedeniyle `D = D0 + deltaT * (offset_glaze - offset_body)`.

Bağımsız simetrik uniform girdiler için `E[D]=D0`; `Var(D)=deltaT²*(h_glaze²+h_body²)/3`. Bu analitik sonuç, Monte Carlo ortalaması ve varyansına bağımsız aritmetik kontrol sağlar. Korelasyon varsa bu varyans formülü geçerli değildir; bu sürüm korelasyon kabul etmez.

Yüzdelikler sıralı örneklerde `(n-1)*p` konumunda doğrusal interpolasyonla alınır. p2.5–p97.5 bir örnek çıktı dağılım aralığıdır; ortalama için güven aralığı, fiziksel kapsama garantisi veya çatlama olasılığı değildir. Sayısal örnekleme hatası, model-form hatası ve fiziksel doğrulama ayrı konulardır.

Yöntem dayanakları: [NIST Uncertainty Machine](https://uncertainty.nist.gov/about/about_English.md.html) girdi dağılımları ve bağımlılıkları üzerinden belirsizlik yayılımını açıklar. [MOOSE instantaneous thermal expansion](https://mooseframework.inl.gov/source/materials/ComputeInstantaneousThermalExpansionFunctionEigenstrain.html) sıcaklığa bağlı anlık katsayıdan termal gerinim integralini açıklar. Bunlar sentetik dağılımlarımızı veya seramik çatlama modelini doğrulamaz.

## Çalıştırılan sentetik örnek

α_glaze=8e-6/K, α_body=6e-6/K; her ikisinin h değeri 0,5e-6/K. Eğri kapsamı 0–600°C, referans 520°C, son sıcaklık 20°C, uzunluk 100 mm. Referans sıcaklık fiziksel Tg iddiası değildir. 20.000 örnek, seed=20260922.

| Nicelik | Sonuç |
|---|---:|
| Analitik ortalama gerinim farkı | −0,001 |
| Monte Carlo ortalaması | −0,0009992865992 |
| Analitik varyans | 4,166666667e-8 |
| Örnek standart sapması | 0,000206001923 |
| p2.5 / p97.5 gerinim farkı | −0,001390890380 / −0,000608613502 |
| Aynı aralık, 100 mm için serbest uzunluk farkı | −0,139089038 / −0,060861350 mm |
| Teorik destek, gerinim | −0,0015 / −0,0005 |

İşaret sır eksi bünyedir; negatif değer sırın serbest halde daha çok kısaldığını gösterir. Yapışık katman yer değiştirmesi veya gerilmesi değildir. Bu çalışma doğrudan fonksiyon çağrısıyla çalıştırıldı; yeni CLI veya HTML entegrasyonu yapılmadı.

Etiket: PREDICTED / STATISTICAL / SYNTHETIC + ASSUMPTION_CONDITIONAL. `fracture_probability.value=null`, status UNAVAILABLE; ölçülmemiş ihtimal 0 yapılmaz.

## Test ve sonraki kapı

İzole simülasyon ortamında `python -X utf8 -m unittest discover -s tests -v`: **119 test geçti**, atlanan yok; 9 yeni test. Analitik momentler, destek, sıfır genişlik/sıcaklık farkı, tekrar üretim, RNG izolasyonu, hatalı girdi, kapsam reddi ve dürüst olasılık etiketi kontrol edildi.

Bilinen sınırlar: bağımsız uniform varsayımı, sadece CTE sapmaları, korelasyon/deneysel dağılım/kalibre arıza modeli yok. Web arayüzü ve FEM bağlantısı yok. Gerçek fiziksel deney yapılmadı.

Sonraki adım: mevcut 3B FEM'in ağ/eğilme doğrulamasını tamamlamak; gerçek ölçüm aralıkları ve bağımlılıkları edinmek. Bunlar olmadan FEM üzerine Monte Carlo ekleyerek çatlama yüzdesi yayınlanmayacak. Gerçek kırılma olasılığı ayrıca dayanım/kusur/geometri ve bağımsız deneylerle doğrulanmış bir arıza modeli gerektirir.
