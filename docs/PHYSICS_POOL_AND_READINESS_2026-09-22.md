# Kaynak havuzu ve motorun güncel durumu

## Sonuç

Bu teslim 6 kaynak, 13 özgün dosya, 477591 bayt ekler. 3 makale CC BY 4.0, 3 seçilmiş kod paketi MIT koşullarıyla arşivlendi. Ham dosyaların SHA256, URL, lisans, yazar, erişim tarihi ve kod commit'leri manifest'te. Tam depolar klonlanmadı; paket kurulmadı, ücretli servis açılmadı, veri dışarı yayınlanmadı.

Bir makalenin Table 2'sinden 5 kil grubuna ait 10 numune-koşul kaydı normalize edildi. Bunlar 10 bağımsız malzeme popülasyonu veya ham zaman serisi değildir. Her satır 2 termal olayın raporlanan sıcaklık ve kütle kaybını içerir. Bir olay sıcaklığı eksik, null olarak korundu. Aktivasyon enerjisi ayrı PREDICTED/EMPIRICAL alanında; kayıp özeti OBSERVED/REPORTED_STUDY_SUMMARY alanında tutuldu. Bunlar araştırma referansıdır, üretim motorunun otomatik kinetik katsayıları değil.

## Yeni kaynaklar ve kullanılabilirlik

| Kaynak | Eklenen | Ne için kullanılır? | Kullanım sınırı |
|---|---|---|---|
| [Thermogravimetric Analysis of Moisture in Natural and Thermally Treated Clay Materials](https://pmc.ncbi.nlm.nih.gov/articles/PMC11123035/) | Resmi Europe PMC JATS tam metin, yapısal tablolar, Table 2'den 10 koşul kaydı | Nem geçmişinin önemini ve raporlanan kayıpları karşılaştırma | 5 adet 2:1 kil grubu, 25–260 °C MTGA; sır veya kaolinitin tüm pişirim aralığı değil |
| [Data on the estimation of thermomechanical damage for fired clay bricks](https://pmc.ncbi.nlm.nih.gov/articles/PMC8063730/) | JATS tam metin ve yapısal tablolar | Pişmiş kil mekanik deney/model tasarımı için referans | Makale eki zaman aşımıyla indirilemedi; Excel ölçümleri elde var denmiyor |
| [Lightweight thermally insulating fired clay bricks enhanced with chitosan-based clay nanocomposites](https://pmc.ncbi.nlm.nih.gov/articles/PMC12280097/) | JATS tam metin ve yapısal tablolar | Büzülme, yoğunluk, porozite ve dayanım ilişkileri için çalışma örneği | Özel chitosan–kil reçeteleri; sır E/CTE verisi değil. Table 1 ile Table 3'te kuruma büzülmesi aralıkları uyuşmuyor, otomatik parametre aktarımı yapılmadı |
| [TA Instruments / tadatakit](https://github.com/TA-Instruments/tadatakit) | LICENSE, README, pyproject, __init__; commit b5efbc2e55fde67d492d49a3e396433ab71d4f17 | TRIOS JSON export işleme mimarisini inceleme | Eski Q600 .001 okuyucusu değildir; kurulmadı/çalıştırılmadı |
| [pycalphad](https://github.com/pycalphad/pycalphad) | LICENSE, README, model.py; commit 1606b43d9f39d897ffa66bb1a77c071fdcde5b59 | Faz dengesi/Gibbs enerjisi model altyapısı | Uygun bileşim sistemine ait doğrulanmış ve lisanslı TDB hâlâ gerekli |
| [CoolProp](https://github.com/CoolProp/CoolProp) | LICENSE, README, HumidAirProp.h; commit 013429639d385de51dd62182da600fd0d3488070 | Su–buhar/nemli hava özellikleri için aday adaptör arayüzü | Başlık ve doküman seçimi tam çözücü değildir; Cantera ile görev örtüşmesi var, ikisi birden kurulmadı |

Kaynakların tam metin arşivlenmesi her cümlenin veya formülün bağımsız bilimsel doğrulaması anlamına gelmez. Bu tur nem makalesinin yöntem ve seçilmiş tablosu, tuğla çalışmasının yöntem ve tabloları incelendi; bütün modellere ait denklem/katsayı doğrulaması yapılmadı. Dış kod dosyaları referanstır, uygulamaya kopyalanmadı. Açık makale lisansı üçüncü taraf veri/şekil haklarını otomatik kapsamaz.

## Erişimde kalan açıklar

- [DTU brick clay / sewage sludge ash TGA](https://doi.org/10.11583/dtu.30157066.v1): resmi Figshare API metadata'sı CC BY 4.0, 360242 bayt XLSX ve 3807 bayt README gösterdi. Dosya yönlendirmesi s3q.ait.dtu.dk üzerinde sertifika doğrulama hatası verdi; ayrı normal TLS istemcisi de bağlantı kuramadı. TLS kapatılmadı, dosyalar indirilmiş sayılmadı. Yayımlanan deney: kuru numuneler, 35–900 °C, 10 °C/min, 50 mL/min N2; veri satırları incelenmedi.
- Önceki LC3 arşivindeki 16 ikili TGA dosyası hâlâ karantinada. Yeni kaynaklar bunları çözmüş sayılmaz.
- Europe PMC termomekanik makale eki indirmesi zaman aşımına uğradı. Tam metin mevcut, ek ölçüm arşivi mevcut değil.

## Motorun durumu: hesap var mı, kanıt var mı?

| Katman | Şu anda çalışan | Doğrulama düzeyi / eksik |
|---|---|---|
| Atom/oksit muhasebesi | 118 kimlik, seçili tabloda 84 standart kütle, 35 oksit; mol ve atom dengesi | Yazılım ve el hesabı testleri; tüm elementlerin termofiziksel verisi yok |
| Reçete kimyası | Kuru baz, ilave, LOI, oksit/molar kompozisyon, UMF ve oranlar | Sıkı araştırma sözleşmesi; gerçek üretici/lot veri seti tamamlanmadı |
| Ölçüm işleme | Zaman–kütle farkı, imzalı TGA kaybı, kaynaklı snapshot | Sentetik testler; bu yeni özet tablo zaman serisi yerine geçmez |
| Buhar | Verilen salım ve havalandırmayla sabit sıcaklıklı ideal hacim bilançosu | Yoğuşma/enerji/porozite yok; doygunluk aşımında durur |
| Genleşme | Uygun CTE eğrilerinden serbest boyut farkı | Eğrilerin gerçek malzemeden ölçülmesi gerekir |
| FEM | İdeal iki katmanlı pişmiş katıda ısı ve lineer termoelastisite | Analitik benchmark'lar var; önceki ağ incelemesinde yaklaşık %9 değişim, tam yakınsama yok |
| Belirsizlik | Varsayılan CTE dağılımlarıyla Monte Carlo senaryosu | Kalibre çatlama olasılığı değil |
| Faz/reaksiyon/akış | Araştırma kaynakları var | Aktif doğrulanmış çok bileşenli faz, viskoz akış veya kinetik çözücü yok |
| Görsel sonuç/AI | Henüz yok | Renk, matlık, kristal veya kusur yüzdesi üretilmez |
| Ürün arayüzü | Araştırma CLI ve önceki simülasyon çıktıları | Birleşik, gerçek kullanıcı akışı doğrulanmış web laboratuvarı yok |

Mühendislik değerlendirmesi: kimyasal muhasebe ve bazı fizik bileşenlerinin temeli atıldı. Birleşik ve deneyle doğrulanmış sanal fırın kurulmuş değil. Test sayısı kapsam göstergesidir; gerçek pişirim doğruluğunun yüzdesi değildir. Bu kaynak teslimi hesap motorunun fizik yeteneklerini değiştirmedi.

## Bundan sonra büyük çalışma paketi

1. **Gerçek veri kabulü:** bir sayısal TGA serisini zaman/baz/numune/atmosfer ve gaz ayrımıyla kabul etmek. Tek sıcaklık rampasından evrensel kinetik çıkarma yok.
2. **Su özellikleri:** Cantera veya CoolProp'tan yalnız bir izole adaptör seçmek; basınç, doygunluk, entalpi ve geçerlilik sınırlarını bağımsız referans noktalarıyla sınamak.
3. **Enerji ve kütleyi birleştirmek:** önce 0D kontrollü deney, su kaybının enerji etkisi, konveksiyon/ışınım ve açık bilanço; ardından uzaysal modele geçmek.
4. **FEM güvenilirliği:** ağ/zaman yakınsaması, ince tabaka eğilme kontrolü, E(T)/CTE eğrileri ve viskoelastisiteye geçiş şartları.
5. **Malzeme ve ürün akışı:** üretici analizi sürümleri ile web raporunda hesap/gözlem/tahmin ayrımı. Fizik modülleri tek tek geçerlilik alanıyla görünür olmalı.

Bu sıra öneridir; ücretli veri, ticari TDB veya büyük mimari değişiklik bu teslimle onaylanmış sayılmaz.

## Kanıt dosyaları ve tekrar üretim

Son doğrulama: `python -X utf8 -m unittest discover -s tests` ile **177 test, 6.218 saniye, OK**. Bu tur altı yeni test eklendi. Offline arşiv denetimi 13 dosyanın toplam 477591 baytını ve hash'lerini doğruladı; 10 kaydın normalizasyon replay'i geçti. Fiziksel doğrulama yapılmadı; yeni solver paketi kurulmadı.

- `data/manifests/physics-pool-2026-09-22.json`: edinilen kaynaklar/dosyalar/erişim hataları.
- `data/reference/moisture-study-observations-v1.json`: satır/cell metni ve kaynakla 10 çalışma kaydı.
- `research/physics_pool_audit.py`: 13 dosyanın hash/boyutu, normalizasyon replay ve bağımsız tablo spot-check'leri.
- `research/notebooks/physics-pool-audit.ipynb`: denetlenebilir çağrı; notebook UI'da çalıştırılmadı, CLI denetimi çalıştırılır.
- `pipelines/ingestion/physics_pool.py`: lisans kapısı ve yapısal tablo çıkarımı. JATS içindeki alternatif tablo temsilleri korunmuştur; table-wrap sayısı bağımsız deney sayısı değildir. Normalize işleminde tek açık table ID kullanılır.

Veri kalitesi becerisi, eksik değeri sıfıra çevirmemeyi, ampirik aktivasyon enerjisini gözlemsel kayıptan ayırmayı ve çalışma kapsamını korumayı yönlendirdi. Yeni üretim malzeme analizi, ham zaman serisi veya eğitilmiş model eklenmedi. Mevcut kirli README/edinme/FEM dosyaları değiştirilmedi.
