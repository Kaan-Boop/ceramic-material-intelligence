# M2 — Ürün ve çalışma bazlı referans adayları

Tarih: 21 Eylül 2026. **Bu edinme dilimi tamamlandı; M2'nin motor referans seti henüz tamamlanmadı.** Kimya motoru veya web uygulaması geliştirilmedi.

## WHAT WAS BUILT

Dört açık lisanslı çalışmanın iki XML, iki PDF ve bir lisans/ makale HTML belgesi yerel, içerik-adresli arşive alındı. API veya doğrudan resmi dosya adresleri kullanıldı; toplu site taraması, hesap açma, ödeme, dışarı yayın ve model eğitimi yok.

15 çalışma-kapsamlı hammadde analiz adayı ayrıştırıldı. Bu sayı 15 güncel üretici ürünü veya 15 doğrulanmış reçete değildir. İki XML tablosu yapısal olarak okunur; iki PDF tablosu hash ile sabitlenmiş, görsel kontrol yapılmış sınırlı transkripsiyondur. Kaynaklar, yazarlar, lisans, erişim tarihi, dosya SHA-256, tablo ve sayfa referansları korunur.

## WHAT WORKS

| Kaynak | Seçilen kayıtlar | Erişim ve lisans | Motor kabulünü engelleyen başlıca konu |
|---|---:|---|---|
| [Cui ve ark., metakaolin, 2024](https://doi.org/10.3390/ma17020367) | 5: Devolite, Shanxi, M501, 1200S, Opacilite | Europe PMC resmi fullTextXML; makale CC BY 4.0 | Analiz bazı belirsiz; Others bileşeni tanımlı değil; başka tablodaki LOI gram cinsinde |
| [Zhang ve ark., feldspat, 2023](https://doi.org/10.3390/ma17010144) | 1: Lingshou County Shengpeng kaynaklı potasyum feldspat | Europe PMC resmi fullTextXML; makale CC BY 4.0 | Elementler ve oksitler karışık; LOI yok; yüzde bazı açık değil |
| [Arastehnodeh ve Saghi, 2018](https://doi.org/10.1007/s40090-018-0137-4) | 3: Super Standard Porcelain, Quantum AP200F, Morvarid quartz | Derginin OICC Press açık PDF arşivi; PDF içinde CC BY 4.0 | Analiz bazı/tarih eksik; bazı hücreler çizgi; feldspat toplamı %98,47 |
| [Boulaiche ve ark., 2022](https://doi.org/10.18280/acsm.460306) | 6: Hycast VC, Parkaolin, Remblend/RMB, iki Çine feldspatı, Bir el-Ater quartz | Resmi IIETA PDF + lisans HTML; CC BY 4.0 | Analiz bazı açık değil; bazı sütun toplamları uyuşmuyor; lotlar yok |

İzin kararı seçilmiş makale tablolarının kaynaklı araştırma kopyası içindir. Üreticinin tüm kataloğu bu lisansa dahil sayılmaz. CC BY atfı/değişiklik bildirimi korunur; hukuki garanti verilmez. Üçüncü taraf resimleri eğitim setine alınmadı. Kaynak belgeleri değiştirilmedi.

### Sayımlar ve kalite

- Yeni: **4 kaynak, 5 tamamlanmış kaynak/dosya/içerik kaydı; 3.291.629 byte**.
- Birikimli: **10 kaynak, 34 tamamlanmış kaynak/dosya/içerik kaydı; 4.608.097 byte**. Başarısız girişimler receipt'lerde kalır; tamamlanmış arşiv sayısına eklenmez.
- Yeni aday: **15**; çekirdeğe kabul: **0**; araştırma karantinası: **15**; aynı aday kimliği tekrarı: **0**. Bu, kaynaklar arası tüm fiziksel numunelerin bağımsız olduğuna dair bir iddia değildir.
- 15 adayda analiz bazı, kesin analiz tarihi ve lot bilinmiyor. Yayın tarihi analiz tarihi olarak yazılmadı.
- 7 adayda kullanılabilir wt% LOI yok. 5 adayda `Others` var; LOI veya tek oksit olarak yorumlanmadı.
- 2 adayda belirsiz çizgi hücreleri var; sıfıra çevrilmedi.
- Dört sütunda raporlanan sayısal toplam %100 ±0,5 inceleme bandı dışında: Quantum AP200F **98,47**; Hycast VC **101,9**; Parkaolin **99,42**; Çine K-feldspar **100,56**. Bu eşik bir bilimsel kabul standardı değil, tanımlı inceleme alarmıdır. Toplamlar LOI/Others içerdiğinde bunu belirtir; eksik hücreleri dışarıda bırakır. Kimyasal kütle dengesi veya düzeltilmiş analiz değildir.

`study_materials` araştırma aday kaydı üretir; production intake biçimine dönüştürmez ve kabul kurallarını gevşetmez. Kaynak yazımı `Cibelco` sessizce `Sibelco` yapılmadı. `1200S`, `M1200S` ile eşleştirilmedi. Aynı üreticinin farklı çalışmalardaki analizleri birleştirilmedi.

### Fizik araştırmasına yarayan ek veri

2018 çalışmasının Table 3'ünden S0 bünyesi için **2 seri × 6 aralık = 12 ortalama doğrusal TEC değeri** ayrıldı. Bünyenin bildirilen reçetesi %50 kaolin, %25 kuvars, %25 K-feldspat; seriler 1250°C ve 1340°C pişirim gruplarına aittir. Ölçüm aralıkları 25–600°C içinde, birim 10⁻⁶/K'dir.

**Bunlar anlık α(T) eğrisi değildir.** Ölçümün ısıtma/soğuma kolu, referans uzunluk tanımı ve yöntem ayrıntıları yeterince belirlenmedi. `model_input_eligible=false`. Sır eşleşmesi yok; mevcut termal prototipe beslenmedi, gerilme veya çatlama ihtimali hesaplanmadı. Kaynakta ölçülmüş diye sunulan ve metinde ortalama hesabı olarak tarif edilen değerler `OBSERVED / EMPIRICAL / REPORTED / PARTIAL` altında tutuldu; bağımsız doğrulanmış ölçüm sayılmadı.

## TEST RESULTS

80 unit test geçti: önceki 69 + 11 yeni kontrol. Yeni kontroller: çizgi/sıfır ayrımı, sonlu olmayan değerler, Others/LOI ayrımı, sütun toplamını düzeltmeme, kimlik/baz koruması, tablo boyutu ve span değişimi, kaynak lisansı, raw hash bozulması, tekrar üretim, eksik kaynak, termal ortalama türü ve JATS yazar metadata'sı.

Gerçek arşivden yeniden üretim ayrıca çalıştırıldı. PDF becerisiyle IIETA sayfa 2 ve anortit makalesi sayfa 2/5 görsel incelendi. Bu tek asistan incelemesidir; bağımsız ikinci araştırmacı kontrolü veya fiziksel deney değildir. Genel profil aracı önceki 19 dosyayı kapsar; yeni analizler ayrı aday ayrıştırıcısında sayılır.

[Kontrol defteri](../research/notebooks/m2-study-quality.ipynb) aynı sayım, kaynak, toplam ve replay kontrollerini okunabilir hücrelerle içerir. Ortamda `nbformat` bulunmadığından **Jupyter yürütmesi ve notebook görünüm kontrolü yapılmadı**; defter çıktıları boş bırakıldı. Çalıştırılmış kanıt yukarıdaki CLI/unit testler ve gerçek arşiv replay'idir. Defteri çalıştırmak için nbformat/nbclient/ipykernel ve Jupyter ortamı kurulup `jupyter nbconvert --execute --to notebook --inplace research/notebooks/m2-study-quality.ipynb` kullanılmalı. Bu ek bağımlılıklar kurulmadı; çekirdeğin veya mevcut veri araçlarının gereksinimi değildir.

### Karşılaşılan sorunlar ve çözümler

- Europe PMC bağlantı kesintisi ve IIETA TLS zaman aşımı: sınırlı tekrar sonrasında tamamlandı; TLS doğrulaması kapatılmadı.
- Springer PDF isteği `idp.springer.com` yönlendirmesine gitti: kimlik akışı takip edilmedi. Aynı açık makalenin derginin resmi OICC Press arşivindeki nüshası incelendi.
- PDF lisans URL'si `creativecom-` satır sonu `mons` şeklinde bölünüyordu: yalnızca lisans kontrolünde bu belirli satır sonu birleştirildi; bilimsel sayılara dönüşüm uygulanmadı.
- XML yazar grubu `content-type=author` biçimindeydi: ilk receipt'teki boş yazar alanları silinmedi; hash ile doğrulanan XML'den türetilmiş atıflar aday dosyası ve yeni manifest'te düzeltme notuyla yayımlandı.
- Geliştirme sırasında bir sözdizimi hatası test yüklemesini durdurdu; fazla parantez giderildi ve tam test seti yeniden çalıştırıldı.

## KNOWN LIMITATIONS / TECHNICAL DEBT

Analizlerin güncel ticari ürün/lot karşılığı garanti değil. PDF ayrıştırma genel amaçlı OCR değil; kaynak hash'i değişirse yeniden inceleme gerekir. Analiz tarihi/lot eksikliğinin kullanıma etkisi veri kalite boyutları olarak ileride ayrı ele alınabilir; bu partide kritik baz/kimya belirsizliği zaten bağımsız engeldir. Hiçbiri sır yüzeyi veya gıda güvenliği kanıtı değildir.

2018 tablosundaki beyaz çimento ve 2022 tablosundaki SLGW bu sınırlı hammadde aday seçimine dahil edilmedi; özgün PDF'de korunur. Diğer pişirim/SEM/XRD tabloları ve TEC tablosunun S0 dışı kolonları henüz yapılandırılmadı. Tüm makale içeriğinin veri tabanına aktarıldığı iddia edilmez.

## NEXT STEP

M2 içinde rastgele daha çok dosya yerine bu 15 adayın eksik baz/LOI/kimlik bilgisini tamamlama önceliği. [Hazır bilgi talebi](REFERENCE_DATA_REQUEST.md) gönderilmedi; dış iletişim kullanıcı onayı gerektirir. Yeni açık CoA/TDS araması da bu alanlara hedeflenmeli. M3'e veya ücretli termodinamik/NVIDIA hizmetine otomatik geçiş yok.

## Yeniden üretim

Proje kökünde Python 3.12; PDF edinimi için pypdf 6.10.0, eski XLSX profili için openpyxl 3.1.5:

```sh
python -m pipelines.ingestion.acquire --storage storage/research --sources metakaolin-2024 feldspar-activation-2023 anorthite-2018 sanitary-body-2022
python -m pipelines.ingestion.study_materials --storage storage/research --output storage/research/new-candidate-review.json
python -m unittest discover -s tests -v
```

Çıktı dosyası varsa üzerine yazılmaz. İlk komut ağ erişimi gerektirir; ikinci komut yerel arşivle çalışır. Makale içeriği değiştiyse hash kapısı durur. Raw içerik Git'e girmez; küçük kaynaklı transkripsiyon ve manifest sürümlenir.

- [Aday analizler ve termal referanslar](../data/reference/study-material-candidates-v1.json)
- [Birikimli manifest ve kalite sayımları](../data/manifests/research-acquisition-2026-09-21-batch3.json)
- [Ayrıştırıcı](../pipelines/ingestion/study_materials.py)
