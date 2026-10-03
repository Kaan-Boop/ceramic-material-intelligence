# Akış, yüzey ve bünye etkileşimi — araştırma paketi 1

Kontrol: 21 Eylül 2026. Bu paket araştırma havuzunu genişletir; simülasyon motorunu değiştirmez. Yeni paket kurulmadı, dışarı veri yayınlanmadı, model eğitilmedi. Kayıtlar doğrulanmış üretim girdisi değildir.

## Teslim ve kaynaklar

3 tamamlanmış kaynak, 10 kaynak dosyası, toplam 357.115 byte; iki makaleden 4 yapısal tablo dökümü. Boyut yalnız özgün kaynak dosyalarının toplamıdır; okunabilir kopyalar ve türetilmiş JSON'lar dahil değildir. İki edinme çalışması aynı kaynakları iki veri seti yapmaz. Önceki envanter değiştirilmedi; [yeni manifest](../data/manifests/flow-acquisition-2026-09-21-batch1.json) ayrı tutuldu.

| Kaynak | İçerik ve haklar | Bilimsel kullanım sınırı |
|---|---|---|
| [Conte ve diğerleri, 2018](https://doi.org/10.3390/ma11122475) | Resmi Europe PMC API'den JATS tam metin, 2 tablo; CC BY 4.0 | Vitröz faz bileşimi ve yüksek sıcaklık özellikleri; model sonuçlarını ölçüm sayma |
| [Öztorun ve Demirkol, 2026](https://doi.org/10.3390/ma19163405) | Resmi Europe PMC API'den JATS tam metin, 2 reçete tablosu; CC BY 4.0 | İki bünye ve tek indirgeme pişirim programı; Cone 6 oksidasyona genellenemez |
| [GlassPy, sabit commit](https://github.com/drcassar/glasspy/tree/ddc06240152749d14d01e0c4f7cec9e4e79c706d) | LICENSE, README, CITATION, pyproject, 3 viskozite modülü, 1 veri yükleyicisi; GPL v3 bildirimleri | Yalnız yöntem kodu. Kurulmadı/çalıştırılmadı; SciGlass veri tabanı ve model ağırlıkları indirilmedi |

Makale lisansı ticari kullanıma koşullarıyla izin verir; atıf gerekir. Bu, bilimsel uygunluk veya tüm üçüncü taraf içerikler için sınırsız hak anlamına gelmez. Ürün export/gösterimi ayrıca kontrol edilecek. GPL kaynak kodunu uygulamaya aktarmak ayrı dağıtım/lisans kararı gerektirir; proje lisansı değiştirilmedi.

GlassPy LICENSE dosyasındaki SciGlass bölümü ODbL başlığı altında MIT benzeri metin içeriyor. Bu tutarsızlık nedeniyle veri tabanı indirilmedi. Özgün SciGlass sürümünün hakları ayrıca doğrulanacak; kod lisansı veri lisansı olarak kullanılmayacak. CITATION.cff kod için GPL-3.0-or-later bildiriyor; özgün dosya bildirimleri saklandı.

## Veri kalitesi incelemesi

Veri kalitesi becerisi yardımcı denetim olarak kullanıldı: tablo düzeyi, birim, yöntem, eksik değer ve haklar ayrıldı. Sayısal fizik parametreleri henüz normalize edilmedi.

### 2018 makalesi

- Table 1 toplam hammadde reçetesi değil, bünyedeki vitröz faz miktarı ve hesaplanmış bileşimidir. Bünye, sıvı faz ve kristal yükü ayrı tutulmalı.
- Table 2 maksimum pişirim sıcaklığındaki özellikleri içeriyor: sıcaklık °C, viskozite **log10(Pa·s)**, yüzey gerilimi **mN/m**, Tg °C. Logaritmik sayıyı doğrudan Pa·s olarak kullanma.
- Giordano viskozite modeli ve Dietzel/Appen yüzey gerilimi modelleri kullanılıyor. İlgili sonuçlar `PREDICTED / EMPIRICAL / ESTIMATED` adaylarıdır; makalede bulunmaları onları `OBSERVED` yapmaz.
- Sıvı fazın viskozitesi, kristal içeren bütün bünyenin etkin viskozitesine eşit değildir.
- Yan yana paneller ve birleşik hücreler var. Tablo satırı bağımsız deney değildir; satır sayısını malzeme/deney sayısı olarak raporlamadık.
- Eksik tireler, dipnotlar ve matematik işaretleri korundu. Tmax noktasından sürekli sıcaklık eğrisi türetilmedi.
- S1–S4 ek tabloları indirilmedi. Bağımsız model kontrolü için ek veriler ve özgün model kaynakları ayrıca gerekli.

### 2026 makalesi

- Baz sır ve A–D katkı formülasyonları var. Baz üstüne ilaveler sessizce toplam %100 reçeteye çevrilmemeli.
- Beyaz bünye ve şamotlu bünye ayrımı korunmalı; reçete ve fiziksel numune tek kayıt değildir.
- SEM–EDS, XRD ve görsel bulgular farklı kanıtlardır. Elementel EDS otomatik tam oksit analizi veya oksidasyon basamağı ölçümü değildir.
- Yazarların mekanizma yorumları ölçülmüş kinetik katsayı değildir. Çalışmaya özgü indirgeme/sonradan indirgeme programı korunmalı.
- Makale iki bünye ve tek pişirim programı sınırını belirtiyor. Fotoğraflar, bağımsız tekrar sayısı ve nicel belirsizlik ayrı kayıt olarak aktarılmadı.
- Bu kaynak temas açısı–zaman veya viskozite–sıcaklık ölçüm seti değildir. Metal katkılı lüster sır referansıdır; metal parçayla seramiği birlikte pişirme modülü değildir.

### GlassPy yöntem referansları

VFT/MYEGA denklem arayüzlerinde sıcaklık Kelvin olarak tanımlı. `equilibrium.py` doğrudan viskozite, `equilibrium_log.py` log10 viskozite döndürür; bunlar aynı birimli çıktı değildir. Kodun çalışması veya denklemin varlığı, katsayılarının belirli bir sır için uygun olduğunu doğrulamaz. Dış kod motorumuza kopyalanmadı.

## Havuz dışında tutulan adaylar

| Kaynak | Karar / neden |
|---|---|
| [Low-gloss, silky matte glaze for porcelain tiles](https://doi.org/10.1590/0366-69132023693913482) | Yalnız künye ve değerlendirme. SciELO lisans bağlantısı CC BY-NC 4.0'a gidiyor; tam veri indirilmedi, ticari açık havuza alınmadı |
| [Hot-stage microscopy, 2015](https://doi.org/10.1016/j.mspro.2015.05.031) | Yalnız aday künye. Yazar kopyasında CC BY-NC-ND 4.0 bildirimi görüldü; yayıncı hak incelemesi tamamlanmadı. Alümina üzerindeki tek sır, bütün çamurları temsil etmez |

NC, her türlü araştırmanın otomatik izinli olduğu anlamına gelmez. Ticari amaçla ilişkili kullanım açıklığa kavuşmadan veri dönüştürme/eğitim yapılmayacak. [Aday listesi](../data/manifests/flow-source-candidates-2026-09-21.json) indirilen kaynaklardan ayrıdır.

## Dosyalama ve yeniden üretim

```text
storage/research/flow/
  raw/sha256/<tam-hash>                 # özgün içerik
  by_source/<source-id>/<hash>/...      # okunabilir adla aynı içerik
  staging/<source-id>/<hash>/table-index.json
  receipts/<run-id>.json                # başarılı/kısmi/başarısız edinimler
data/manifests/flow-acquisition-2026-09-21-batch1.json
pipelines/ingestion/flow_sources.py
tests/test_flow_sources.py
```

Raw ve dış kaynak kodu Git'e alınmaz. Manifest kaynak/yazar/lisans/tarih, commit veya DOI, SHA-256, boyut, hak bölümü ve arşiv yollarını tutar. Tümü araştırma karantinasında: `core_engine_eligible=false`, `training=NOT_ENABLED`.

```sh
python -m pipelines.ingestion.flow_sources --root storage/research/flow --manifest data/manifests/flow-acquisition-NEW-RUN.json
python -m unittest discover -s tests -v
```

Manifest adı yeni olmalı; mevcut kayıt sessizce ezilmez. Resmi API/sabit dosya yolları, 1 saniye istek aralığı, 30 saniye timeout, dosya başına 8 MiB sınırı kullanılır. Toplu site kazıması yok. Başarısız kaynak tamamlanmış sayılmaz. Aynı içerik hash ile yeniden kullanılır; değişen içerik yeni sürüm olur.

102 test geçti: önceki 94 + 8 yeni test. Kimlik/lisans, NC/ND reddi, sahte lisans alan adı, birleşik/eksik hücreler, tekrar edinim, bozulmuş kopya ve kısmi indirme kontrol edildi. Yazılım testleri fiziksel seramik doğrulaması değildir. Manifestte 10 dosyanın raw ve okunabilir kopyaları ile iki tablo indeksinin hash kontrolü kayıtlıdır.

## Sonraki araştırma kapısı

Eksik olan: aynı sır–bünye çifti için sıcaklıkla viskozite, eriyik temas açısı/zaman, yüzey gerilimi, tabaka kalınlığı ve atmosfer. **Su damlasının pişmiş yüzeydeki temas açısı, erimiş sırın bünyeyi ıslatma açısı değildir.**

Önce 2018 ek verileri ve özgün modellerin geçerlilik alanı doğrulanacak; ardından uygun tablolar birim/baz/yöntem düzeyinde denetlenmiş property-curve adaylarına dönüştürülebilir. Gerçek ölçüm olmadan sentetik 3B gösterimi gerçek akma, tutunma veya çatlama olasılığı gibi sunmayacağız. Bu pakette yeni doğrulanmış motor girdisi **0**.
