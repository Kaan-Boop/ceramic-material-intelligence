# İlk gerçek veri koleksiyonunun kalite incelemesi

21 Eylül eki: [M2 üçüncü dilim](M2_BATCH3_REPORT.md) 15 yeni çalışma-kapsamlı aday içerir. 15'inin analiz bazı belirsiz, 7'sinde kullanılabilir wt% LOI yok; 4 sütunun raporlanan toplamı tanımlı inceleme bandının dışında. Hiçbiri normalize edilip kabul edilmiş gibi gösterilmedi. İki gerçek bünye TEC serisi aralık ortalamasıdır; anlık α(T) girdisi değildir. İlk koleksiyonun aşağıdaki bulguları korunur.

Tarih: 2026-09-20. Amaç: arşivlenmiş araştırma verisini kimya motoruna uygun hammadde analiziyle karıştırmamak. Kaynak kapsamı ve lisanslar [edinme raporunda](DATA_ACQUISITION.md).

## Bulgular

| Bulgu | Somut kanıt | Risk / önem | Uygulanan işlem |
|---|---|---|---|
| Negatif derişim | UCI CSV satır 3, `FLQ-2-b`, SrO = -10 ppm; 88 satırda 1 satır (%1,14), 1 hücre | Yüksek: fiziksel bileşim olarak doğrudan kullanılamaz; neden kaynakta net değil | Original -10 saklandı; normalize fiziksel değer null, inceleme bayrağı. Sıfıra çevrilmedi |
| Karışık birimler | UCI ilk 8 kimya sütunu wt%; sonraki 9 ppm | Yüksek: yanlış ölçek 10.000 kat hata doğurabilir | Metadata'ya göre açık ppm/10000 dönüşümü; orijinal metin/birim korunuyor; unit test var |
| Şüpheli oksit adı | UCI `PbO2` başlığı hem dosyada hem kaynak metadatasında var | Yüksek: PbO varsayımı bilimsel anlamı değiştirir | `reported_as=PbO2`; otomatik kimlik düzeltmesi yok |
| Ortak numuneler | Mendeley S1/S2/S3: her birinde 135 satır ve 135 unique SampleID; üç kümenin kesişimi 135 | Yüksek: 270 satırı bağımsız deney saymak veri sızıntısı/yanlış örneklem hesabı yaratır | Bünye-sır ölçüm bağlantısı kaydedildi; motor/ML eğitim setine alınmadı |
| Element ile oksit ayrımı | Mendeley S1/S2 sütunları Si, Al, Fe vb.; başlıklar birim taşımıyor | Yüksek: Si'yi SiO2 yüzdesi gibi kullanmak yanlış | Özgün hücreler saklandı; oksit dönüşümü yapılmadı. README/paper birim protokolü ve oksidasyon varsayımları ayrıca incelenecek |
| Ölçüm ve türetilmiş özet ayrımı | Mendeley S4 istatistik sonuçları, S5 mean/SD/%SD; S4'te 119 boş hücre, S5'te 7 başlık/boş hücre | Orta/yüksek: boşluğu negatif etiket veya türetilmiş skoru gözlem sanma | Dosya rolleri ayrı; genel boş hücre sayıları veri kaybı oranı diye yorumlanmadı |
| Reçete aralıkları | Fabris Table 1: dört G1–G4 formülasyonu aralıklarla; Table 2'de F1–F4 anonim fritler | Yüksek: orta noktalarla uydurma kesin reçete üretme | 4 REPORTED_RANGE reçete kümesi ve 11 araştırma malzemesi; hiçbirine çalışır UMF bağlanmadı |
| Sayısal toplam çelişkisi | Fabris Table 2 dolomite MgO21.6 + CaO31.8 + LOI47.6 = 101.0 | Yüksek: toplamı %100'e sessiz kapatmak hata saklar | Tablo metni korundu; analiz bazı ve kaynak doğrulaması bekliyor |
| Makale birim çelişkisi | Fabris Table 4 ΔWLS mg/cm²; Table 7 başlığı g/cm² | Yüksek: bin kat fark riski | Sonuçlar standartlaştırılmış ölçüm olarak kabul edilmedi; kaynak teyidi bekliyor |
| Birleştirilmiş hücreler | Zenodo çok satırlı başlıklar, notlar, boş alanlar; makalede rowspan/colspan | Orta: satır sayısı numune sayısı değildir; sütun kayması riski | Hücre matrisleri ve XML cell attributes korundu; tek düz tabloya zorlanmadı |
| Program birimleri | GitHub JSON'larında kendi temperature/time unit alanı yok; repository config display default F, profile display m | Yüksek: varsayılanı her dosyanın kesin birimi kabul etme | Birimler null+reason; 5 program incelenmemiş örnek, fırın kontrolüne gönderilemez |

UCI'de 0 birebir tekrar satırı bulundu. Mendeley CSV'lerinde ve Zenodo nonempty matris satırlarında 0 birebir tekrar bulundu; bu, farklı adlarla kopya kayıt veya bağımsız deney garantisi değildir. Tarihsel veri için güncellik trendi uygulanmadı; retrieval zamanı deney tarihi olarak yazılmadı.

## Kullanılabilirlik

- **Araştırma arşivi:** beş kaynak saklandı; 19 veri dosyası profillendi. Okunabilirlik, hash ve seçilmiş schema/birim kontrolleri yapıldı.
- **Motor referansı:** kabul edilmiş gerçek üretici/ürün analizi 0. Akademik kimya verileri araştırma için değerlidir; alanı/bazı belirsiz girdiler hesap girdisine dönüştürülmedi.
- **Fiziksel doğrulama:** yapılmadı. İstatistiksel model veya “başarılı sır” tahmini üretilmedi.
- **Pilot kapsamı:** arkeolojik pişmiş numune ağırlığı yüksek; Cone 6 oksidasyon modern hammadde/deney seti eksik.

## Tekrarlanabilir inceleme

İnceleme kodu `pipelines/ingestion/profile_research.py`; ham kayıt checksum'ları ve profiller `data/manifests/research-acquisition-2026-09-20.json` üzerinden bulunur. Raw dosyalar `storage/research/raw/sha256/`, işlem kayıtları `storage/research/receipts/` içindedir. Profil JSON'ları spreadsheet hücre konumlarını/matris sırasını korur; özgün workbook'lar değiştirilmedi.

Bu kalite denetimi veri-kalitesi becerisinin granülerlik, eksik değer, duplicate ve kaynak anlamı kontrolleriyle yürütüldü. Bir kalite puanı veya “% doğruluk” üretilmedi. Sonraki kabul için üretici/baz doğrulaması ve kayıt düzeyinde insan incelemesi gerekir.
