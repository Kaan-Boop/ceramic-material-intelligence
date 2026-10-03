# Isıl doğrulama pilotu — aday elemesi

İnceleme tarihi: 2026-09-28. Karar: **eşleşmiş çamur–sır pilotu henüz seçilmedi**.
Bu teslim kaynak elemesidir; yeni çözücü, ölçüm seti veya fiziksel doğrulama değildir.

## İnceleme sınırı

Yayıncı kaynaklarının arama hizmetince erişilen metin bölümleri incelendi. Doğrudan sayfa açılışları MDPI, Nature ve SciELO için hata verdi; PMC tarayıcı kontrolü aşılamadı ve aşılmaya çalışılmadı. Tam metin, ekler ve şekillerin eksiksiz incelemesi tamamlanmadı. İndirilmiş ham deney dosyası yok. Yayına özel lisans teyit edilmedi; genel yayıncı politikası tekil makalenin/verinin izni sayılmadı.

## Adaylar

| Aday | Görülen kanıt | İlk pilot açısından karar |
|---|---|---|
| Santos vd., 2023, 3D baskılı stoneware | Yöntem §2.2 ve Şekil 3 açıklaması: pirometre numune yüzeyini, termokupl havayı ölçüyor. Tartışma §4: simülasyondaki bazı dielektrik girdiler varsayımsal; faz dönüşümleri ve büzülme kapsam dışı. | Ölçüm ayrımı için güçlü örnek. Mikrodalga enerji aktarımı mevcut sıradan ısıl modele doğrudan taşınamaz. Ham zaman serisi, eşleşmiş sır analizi ve özellik eğrileri teyit edilmeden kabul edilmez. |
| Jiang vd., 2026, Jingdezhen fırını | Numune yerleştirme bölümü ve Tablo 1 açıklaması çamur ve sır kimyalarını birlikte bildiriyor. Fırın konumlarına göre yüzey/mikroyapı inceleniyor. Tablo 2 pirometrik halkaların eşdeğer pişirim sıcaklıklarını veriyor. | Eşleşmiş sistem için öncelikli derin okuma adayı. Halkaların sonucu numunenin sıcaklık–zaman kaydı değildir. Gerçek numune eğrisi ve ham verisi henüz doğrulanmadı. |
| Cargnin vd., 2015, pişirim eğrisi ve doğrusal büzülme | Birincil SciELO arama kaydı başlık ve deneysel yüzey sıcaklığı karşılaştırması yönünde aday oluşturuyor. | Isıl yöntem adayı; birincil tam metin erişimi tamamlanmadı. Eşleşmiş sır katmanı, ölçüm kökeni ve veri hakları belirsiz. Henüz yöntem/parametre aktarımı yapılmaz. |

Kaynaklar:

1. [Santos vd. — A 3D-Printed Ceramics Innovative Firing Technique: A Numerical and Experimental Study](https://doi.org/10.3390/ma16186236), Materials 16, 6236 (2023). [Yayıncı](https://www.mdpi.com/1996-1944/16/18/6236).
2. [Jiang vd. — Interpreting the firing technology logic of the Jingdezhen egg-shaped kiln through experimental archaeology](https://www.nature.com/articles/s40494-026-02801-3), npj Heritage Science 14, 465 (2026).
3. [Cargnin vd. — Modeling and simulation of the effect of the firing curve on the linear shrinkage of ceramic materials: laboratory scale and industrial scale](https://doi.org/10.1590/0104-6632.20150322s00002876), Brazilian Journal of Chemical Engineering 32, 433–443 (2015). [Birincil erişim adayı](https://www.scielo.br/j/bjce/a/sZ78HhKHZMRsBn3NdbQ34Lr/?lang=en).

## Model girdileri için kabul kapısı

Herhangi bir adaydan çalıştırılabilir pilot üretmeden önce aynı deney kimliği altında:

- Çamur ve sır analizleri, analiz bazları, numune hazırlığı ve malzemenin ham/bisküvi/pişmiş durumu.
- Başlangıç geometrisi; bünye ve sır kalınlığı; destek/temas koşulları.
- İletkenlik, ısı kapasitesi ve yoğunluk: sıcaklık ve malzeme durumuyla ilişkili ölçüm veya gerekçelendirilmiş model. Sabit değer kullanılırsa geçerlilik aralığı ve duyarlılık deneyi.
- Işınım/taşınım sınır koşulları; çevre sıcaklığı ile numune sıcaklığının ayrılması.
- Numune sensörünün konumu, kalibrasyonu, belirsizliği; pirometrede emisivite yaklaşımı.
- Zaman damgalı ham ölçümler, birimler ve bağımsız pişirim/tekrar kimlikleri.
- Veri lisansı, edinme kaydı, checksum ve kaynak içindeki tam konum.
- Kalibrasyon ve değerlendirme ayrımı; kabul hatasının sonuç görülmeden belirlenmesi.

Bir alanın burada doğrulanamamış olması yayında kesinlikle bulunmadığı anlamına gelmez.
Grafikten ileride sayısallaştırılan seri, ham cihaz kaydı olarak etiketlenmez; sayısallaştırma belirsizliği ayrıca tutulur.

## Karar ve sonraki sınırlı iş

1. Jiang çalışmasının yöntem, Tablo 1, veri erişimi/lisans ve eklerini tam inceleme önceliğine al: aynı çamur–sır sistemini tanımlama olasılığı en yüksek adayımız bu. Bu bir öncelik kararı, veri yeterliliği sonucu değil.
2. Santos çalışmasını ayrı bir ölçüm/yöntem referansı olarak koru; mikrodalga modülü kurma veya elektrikli fırın için malzeme yasalarını kopyalama.
3. Cargnin çalışmasındaki sıcaklık karşılaştırmasının hangi deneyden geldiğini birincil tam metinden izlemeyi sürdür; doğrulanmadan bağımsız yeni deney sayma.
4. Tek çalışmada bütün veriler bulunamazsa farklı yayınların kimya ve sıcaklıklarını tek gerçek deney gibi birleştirme. Ayrı alt-model kıyaslamaları kullanılabilir; bütünleşik çamur–sır doğrulaması açık kalır.

Kabul edilen fiziksel pilot: **0**. Yeni indirilen deney veri seti: **0**. Aday inceleme kaydı: **3**.
Mevcut kimya/ısı motorunda değişiklik yok; bu araştırma turunda motor testleri yeniden çalıştırılmadı.
