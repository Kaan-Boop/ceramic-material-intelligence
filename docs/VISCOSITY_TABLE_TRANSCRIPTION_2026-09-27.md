# Viskozite tablolarının kaynaklı sayısallaştırılması

Sonraki inceleme: [özgün kaynak ve bağımsızlık kontrolü](VISCOSITY_ORIGINAL_SOURCE_AUDIT_2026-09-27.md). Ref. 36 için düzeltme kaydı bulundu; iki numuneye bağlı 44 satır düzeltme içeriği incelemesini bekliyor. Sayısal transkripsiyon değiştirilmedi; bu, 44 satırın yanlış bulunduğu anlamına gelmez.

Tarih: 27 Eylül 2026. Kapsam: daha önce edinilmiş Conte ve arkadaşları (2018) ek PDF'sindeki S3 ve S4. Yeni indirme, model çalıştırma veya katsayı uydurma yapılmadı.

## Teslim

[Sayısal veri](../data/reference/conte-2018-viscosity-staging.json), [yeniden üretme aracı](../pipelines/ingestion/viscosity_tables.py), [11 kontrol testi](../tests/test_viscosity_tables.py).

| Numune | S4 sıcaklık satırı |
|---|---:|
| IGC | 18 |
| MNV | 18 |
| MST | 21 |
| CI_OF | 20 |
| MDV | 17 |
| G.2000 | 22 |
| AMS-B1 | 11 |
| AMS-D1 | 14 |
| Trachyte | 24 |
| Phonolite | 20 |
| Toplam | 185 |

S3: 10 bileşim ve bileşim başına 10 oksit hücresi. S4: 185 raporlanmış deneysel viskozite değeri ve 370 raporlanmış model tahmini (Giordano ve Fluegel). Bunlar 555 bağımsız deney veya 10 ticari sır reçetesi değildir. Aynı numunenin farklı sıcaklıkları birlikte tutulur.

## Bilgi ayrımı

- `experimental`: `OBSERVED / EMPIRICAL / REPORTED`. Kaynak yazarların literatürden aktardığı değer; bizim ölçümümüz değil.
- `giordano`, `fluegel`: `PREDICTED / EMPIRICAL / REPORTED`. Makaledeki model çıktılarının transkripsiyonu; motorumuzun yeniden hesapladığı tahminler değil.
- Her viskozite değeri `log10(Pa.s)`, sıcaklık `degC`. Logaritma kaldırılmadı; 4.34 değeri 4.34 Pa.s gibi kullanılmamalı.
- Belirsizlik `null`; kaynak tabloda raporlanmama nedeni ayrıca kayıtlı. Sıfır belirsizlik veya olasılık üretilmedi.

## Kaynağa geri izleme

Kaynak: Sonia Conte, Chiara Zanelli, Matteo Ardit, Giuseppe Cruciani, Michele Dondi, *Predicting Viscosity and Surface Tension at High Temperature of Porcelain Stoneware Bodies: A Methodological Approach*, [DOI 10.3390/ma11122475](https://doi.org/10.3390/ma11122475), supplementary tables S3/S4.

Her kayıt numune kimliği, ana makaledeki referans numarası, tablo ve fiziksel PDF sayfasını taşır. S4'te sol/sağ panel ve satır numarası da vardır. Her sayısal hücrede özgün metin ve PDF üst-sol köşesine göre point biriminde hücre kutusu saklanır. Kaynağın tekrar eden basılı sayfa numaraları kimlik olarak kullanılmaz. Bölünmüş `Phono / lite` etiketi yalnızca bu sabit kaynak için `Phonolite` kimliğine bağlanır.

Kaynak PDF SHA-256: `43fb9ce2b12683b1563978a315f44da45a2e28e784f41b059be9f28e5308f0ce`.

CC BY 4.0 dayanağı, ana makalenin ek materyale bağlantısı ve görsel lisans incelemesi [önceki raporda](MELT_EVIDENCE_BATCH2_REVIEW_2026-09-27.md) kayıtlıdır. Sayısal dosya kaynak atfını korur. Orijinal deney kaynakları [32]-[36] ayrıca incelenmeden bağımsız benchmark veya ürün/training yayını onayı yoktur.

## Sessizce düzeltilmeyen noktalar

1. S3 başlığı/açıklaması bileşim birimini ve analiz bazını açıkça belirtmiyor. `unit: null`, `analysis_basis: UNKNOWN` korundu. Beklenen birimi varsayımla wt% veya mol% olarak atamadık.
2. Sayısal hücre toplamları 97.9-100.4 arasında. Bunlar `reported_numeric_sum` olarak yalnızca aritmetik toplamdır; otomatik %100 normalizasyonu yok.
3. S3'te altı tire hücresi `null / SOURCE_DASH_UNDEFINED` olarak saklandı. Açık yazılmış `0.0` değerleri sıfır olarak kaldı. Bu fark kaybolmadı.
4. FeO raporlandığı gibi kaldı; Fe2O3 dönüşümü veya atmosferden redoks kestirimi yapılmadı.
5. S4'ün sıcaklık sırası her yerde monoton değil. Örneğin MDV'de 818 ardından 955 gelir. Özgün sıra korunur.
6. Bu bileşimler NBS 710 değildir; mevcut NBS 710 bağıntısının başka bileşimlerde geçerliliği bu tabloyla varsayılmıyor.

## Doğrulama düzeyi

- Fiziksel PDF sayfaları 3-6 görsel olarak incelendi.
- Koordinat tabanlı çıkarımın bütün S3/S4 sayısal satırları ikinci metin okuyucusunun çıktısıyla eşleşti. Bu, aynı kaynağın iki yazılımla okunmasıdır; bağımsız deneysel doğrulama değildir.
- Her numuneden bir satır olmak üzere 10 görsel golden kontrol, panel/sayfa devamı, satır sayısı, eksik/sıfır ayrımı, birimler, sınıflandırma ve bozulmuş düzenin reddi için 11 test geçti.
- Kaynak yalnızca sabit PDF hash'iyle kabul edilir. Bilinmeyen dosya düzenine aynı koordinatlar uygulanmaz.
- `--check` ile yeniden üretim mevcut JSON ile birebir eşleşti.
- Yerel simülasyon ortamında mevcut çalışma ağacının tamamı için 282 yazılım testi geçti (27 Eylül); bunun 11'i bu teslimde eklendi. Bu sonuç fiziksel malzeme doğrulaması değildir.
- İkinci bağımsız araştırmacı kontrolü, orijinal ölçüm referanslarının doğrulanması ve model kalibrasyon örtüşmesi denetimi tamamlanmadı.

## Yeniden üretme

Proje kökünde mevcut Python ortamıyla:

```text
python -X utf8 -m pipelines.ingestion.viscosity_tables --check
python -X utf8 -m unittest discover -s tests -p test_viscosity_tables.py -v
```

Arşiv elde değilse araç indirme yapmaz; eksik dosya hatası verir. İlk üretim için `--check` kaldırılır. Var olan çıktıyı ezmez; değişen kaynak/çıkarım için yeni sürüm ve ayrı çıktı yolu gerekir. Gerekli mevcut paketler `requirements-transcription.txt` içinde; yeni paket kurulmadı. Çıkarıcı hash'i ve pdfplumber sürümü veri dosyasında yer alır.

## Motor için karar

`RESEARCH_QUARANTINE`, `core_engine_eligible: false`, `training_enabled: false`, `product_release_approved: false`.

Bu teslim bir fizik modeli veya yüzey tahmini eklemez. Motor geliştirilirken başvurulabilecek izlenebilir bir karşılaştırma adayı hazırlar. Sonraki bilimsel kapı, [32]-[36] özgün deneyler ile [17]/[19] model kaynaklarının incelenmesi; birim/baz ve kalibrasyon örtüşmesinin çözülmesidir.
