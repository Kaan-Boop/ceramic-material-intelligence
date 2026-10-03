# Ergiyik araştırma paketi 2: kaynak ve uygunluk incelemesi

İndirme: 21 Eylül 2026. Görsel inceleme ve yerel bütünlük kontrolü: 27 Eylül 2026.

## Sonuç

İki kaynak koleksiyonu, 10 kaynak dosyası ve iki PDF metin çıkarımı arşivde doğrulandı. Kaynak dosyalarının toplamı 19.485.238 byte. Bu toplam benzersiz deney verisi hacmi değildir: ZIP içindeki PDF ayrıca saklanır ve 2018 ana makalesi önceki koleksiyonda da vardır. İki koleksiyon, iki yeni bağımsız çalışma demek değildir.

Yeni fizik katsayısı, model eğitimi veya ürün yayını bu teslimde etkinleştirilmedi. Kaynaklar `RESEARCH_QUARANTINE` durumunda. Açık lisans ile bilimsel uygunluk ayrı değerlendirilir.

## 1. Stoneware viskozite ek tabloları

- Çalışma: Conte, Zanelli, Ardit, Cruciani ve Dondi (2018), *Predicting Viscosity and Surface Tension at High Temperature of Porcelain Stoneware Bodies: A Methodological Approach*.
- [Makale ve DOI](https://doi.org/10.3390/ma11122475); [resmi ek dosya API'si](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6317026/supplementaryFiles?inlineImages=false).
- Ana makalenin arşivlenmiş JATS lisansı CC BY 4.0; ek PDF ana makalede açıkça bağlı. Ek PDF'nin altı sayfasında ayrı bir kısıtlayıcı bildirim görülmedi. Bu gözlem bütün üçüncü taraf haklarının ayrıca temizlendiği anlamına gelmez.
- Altı fiziksel PDF sayfasının tamamı görsel olarak incelendi. Kaynağın basılı sayfa numarası son kısımda yeniden başladığı için aşağıdaki konumlar fiziksel PDF sayfalarıdır.

| İçerik | Fiziksel sayfa | Kullanım kararı |
|---|---|---|
| S1: bünyelerin toplam kimyası | 1-2 | Ana makaledeki sıvı faz kimyasıyla karıştırılmamalı |
| S2: kuvars, mullit, camsı faz dahil faz dağılımları | 2-3 | Numune adı tek başına benzersiz kimlik değil; koşullar korunmalı |
| S3: 10 silikat ergiyiği bileşimi | 3 | Viskozite karşılaştırması için aday bileşim seti |
| S4: deneysel ve iki modelin viskozite değerleri | 4-6 | `log10(Pa·s)`; deneysel/model sütunları ayrı tutulmalı |

S3 kodları: IGC, MNV, MST, CI_OF, MDV, G.2000, AMS-B1, AMS-D1, Trachyte, Phonolite. S4'te deneysel değerler literatür referansları [32]-[36]'dan aktarılıyor; bunlar bu projenin gerçekleştirdiği deneyler veya on bağımsız fırın testi değildir. Giordano ve Fluegel sütunları tahmindir. Orijinal kaynaklar ve modellerin kalibrasyon verileri kontrol edilmeden bağımsız test seti ilan edilmeyecek.

Sayısallaştırmada dikkat: iki paralel sütun paneli, sayfalar arasında devam eden numuneler, bölünmüş numune adları ve düzensiz sıcaklık sırası. S1'deki Fe2O3 ile S3'teki FeO otomatik birbirine dönüştürülmeyecek. Boş hücre ve tire sıfır kabul edilmeyecek. PDF'den metin çıkarılması, doğrulanmış sayısal tablo elde edildiği anlamına gelmez.

Bu ergiyikler NBS 710 değildir. Projedeki malzemeye özgü NBS 710 viskozite bağıntısı bunlara uygulanarak doğrulanamaz; başka bileşime yapılan aktarım kapsam dışıdır.

## 2. Borosilikat ergiyiklerinin ıslanması

- Novák, Řeháčková, Novák, Matýsek ve Peikertová (2025), *Influence of B2O3 on Reactive and Non-Reactive Wetting Behavior of CaO-SiO2-MgO-Al2O3-B2O3 System*.
- [Sabit veri sürümü](https://zenodo.org/records/15837287), DOI `10.5281/zenodo.15837287`; [makale](https://doi.org/10.3390/coatings15080967).
- Arşivlenmiş veri kaydı ve makalenin ilk sayfası CC BY 4.0 gösteriyor. Atıf zorunluluğu korunur. Veri sürümü ile kavramsal DOI `15837286` ayrıdır.
- Makalenin 1 ve 3-7. fiziksel sayfaları görsel olarak incelendi; 20 sayfanın tamamı görsel olarak kontrol edilmiş sayılmıyor.

| Bulgu | Proje açısından anlamı |
|---|---|
| Dört nominal oksit bileşimi; B2O3 aralığı %0-30 | Genel ticari sır kataloğu değil |
| Altlıklar platin ve grafit | Çamur üzerine sır yapışması verisi değil |
| Yüksek saflıkta argon, 5 °C/dakika, 1550 °C'ye kadar | Oksidasyon stoneware pilotuna doğrudan aktarılamaz |
| Tablo 3: reometre ve ısıtma mikroskobu sonuçları | Farklı operasyonel ölçüm yöntemleri; tek kesin liquidus değerinde birleştirilmez |
| Şekil 1: sıcaklığa karşı ortalama ıslanma açısı | Hata çubukları standart sapma; güven aralığı veya kusur olasılığı değil |
| Dört indirilen CSV: FTIR spektrumları | Sayısal temas açısı eğrileri değil |

Seçilen dosyalar: kayıt metadata'sı, README, dört FTIR CSV ve makale PDF'si. Sekiz TIFF şekil dosyası bu sınırlı pakette indirilmedi; adları ve boyutları edinme manifestinde kayıtlı. CSV başlık/birimleri tahminle doldurulmadı. Makale FTIR için 400-4000 cm^-1 ölçüm aralığı, 4 cm^-1 çözünürlük ve 32 tarama bildirir; şekillerde 400-1800 cm^-1 gösterilir. Makalede anlatılan işleme adımları her `RAW` CSV'ye varsayımla atanmayacak.

Temas açısı grafikleri sayısallaştırılmadı. İleride yapılırsa sonuçlar ham ölçüm değil, şekilden türetilmiş değerler olarak çözünürlük/digitizasyon belirsizliğiyle saklanmalı. Bağımsız tekrar sayısı bu incelemede doğrulanmadı.

## 3. Arşiv ve doğrulama

- [Edinme manifesti](../data/manifests/melt-evidence-2026-09-21-batch2.json): 21 Eylül kaydı değiştirilmedi.
- [İnceleme kaydı](../data/manifests/melt-evidence-review-2026-09-27.json): kapsam ve kararlar ayrı tarihli kayıt.
- Raw kopyalar: `storage/research/melt-evidence/raw/sha256/`.
- İnsan tarafından okunabilir kopyalar: `storage/research/melt-evidence/by_source/`.
- PDF metni: `storage/research/melt-evidence/staging/`.
- Görsel inceleme çıktıları: `storage/research/melt-evidence/review/`.

27 Eylül çevrimdışı kontrolü: 10 kaynak dosyasının raw/okunabilir kopyaları ve iki transkripsiyonun hash/lineage kontrolleri geçti. Üç edinme modülünün mevcut SHA-256 değerleri indirme zamanında sabitlenenlerle aynı. Zenodo dosyalarında indirme sırasında kaynak MD5 ve boyut da kontrol edilmişti.

Poppler ile oluşturulan bazı önceki görsellerde font uyarıları alınmıştı; incelenen sayfalar okunabilir bulundu. Kaynak PDF'ler değiştirilmedi. Bu, bağımsız ikinci araştırmacı incelemesi değildir.

Yerel simülasyon ortamında `python -X utf8 -m unittest discover -s tests -q`: **271 test geçti** (27 Eylül çalışma ağacı). Bu test sayısı bütün mevcut yazılım testlerini kapsar; hepsi bu pakette eklenmedi. Paketin sekiz yeni edinme testi arşiv güvenliği, dosya seçimi, sürüm/lisans doğrulaması ve checksum sınırlarını kapsar. Yazılım testlerinin geçmesi malzeme davranışının fiziksel doğrulandığı anlamına gelmez.

## 4. Sonraki kontrollü adım

1. S3/S4 tablolarını hücre konumu ve kaynak hash'i korunarak sayısallaştır; deneysel aktarımları `OBSERVED / REPORTED`, model değerlerini `PREDICTED` olarak ayır. İkinci kontrol olmadan motor girdisine yükseltme.
2. [32]-[36] orijinal kaynaklarını ve model eğitim/kalibrasyon örtüşmesini incele. Birbirinden türemiş yayınları bağımsız doğrulama sayma.
3. Çamur altlığı, gözeneklilik, yüzey hazırlığı, atmosfer, sır bileşimi ve pişirim eğrisi birlikte raporlanan gerçek sır-bünye ıslanma deneylerini ara.

Bu teslim 3B motoru veya NBS 710 modülünü değiştirmez. Araştırma havuzunu genişletir ve yanlış veri aktarımını önleyecek sınırları kaydeder.
