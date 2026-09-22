# Türkiye teknik özellik paketi — 23 Eylül 2026

## Teslim ve sınırlar

166 benzersiz ürün kimliği: 113 hazır bünye, 20 ham kil, 33 toz sır.
Önceki 162 kimliğe Refsan 856, 956, 159 ve 259 eklendi. Paket boyları sayılmadı.
Türkiye keşif pazarında 31 bünye ve 24 sır var; keşif pazarı menşe değildir.
Yedi hazır bünye markası / toplam dokuz marka: bölge başına 20 marka hedefi tamamlanmadı.
1.000+ doğrulanmış kayıt ve 100 toz sır hedefleri açık. Asya ticari ürün paketi henüz yok.

10 çamur için 15 sayısal özellik kaydı, 22 pişirim beyanı, kullanım alanları ve
eksiklikler saklandı. Bunlar 15 yeni ürün veya bağımsız laboratuvar deneyi değildir.
Kaynaklar üretici/marka ürün sayfaları; yeni ölçüm, lot doğrulaması veya toplu veri lisansı yok.
Veri-kalitesi rehberiyle ürün kimliği, koşullu özellik ve tam analiz ayrı sayıldı.

## Bulgular

| Ürün | Sırlı pişirim beyanı (°C) | Kritik durum |
|---|---|---|
| Akasya Stoneware Vakum | 1190–1220 | 1220°C'deki emme 0 diye bildirilmiş; belirsizlik ve yöntem yok |
| Akasya Porselen Vakum | 1190–1220 | Toplu küçülme %12–13; deney sıcaklığı açık değil |
| Akasya Şamotlu Gri 0,02 | 1190–1220 | Şamot %25; 0,02 mm yazımı aynen korundu, teyit gerekli |
| Akasya Serbest Şekillendirme | 1000–1200 | Şamot %25; 0,05–0,06 mm tanımı teyit gerekli |
| Refsan 656 | 1040–1060 | Sekiz oksit + LOI; toplam %99,8; baz/tarih/lot/yöntem eksik |
| Refsan 856 | 1040–1060 | Şamotsuz, kullanım beyanları var; oksit analizi yok |
| Refsan 956 | 1040–1060 | Şamotsuz; beyazlık ölçülmüş renk verisi değildir |
| Refsan 159 | 1180–1220 / 1180–1200 | Aynı sayfanın iki bölümü çelişkili |
| Refsan 259 | 1180–1220 / 1180–1200 | Aynı sayfanın iki bölümü çelişkili |
| Crafist Akçini 15362044 | Tek hedef: 1040 | Aralık değildir; Akçini başlığı/Stoneware sınıfı çelişkisi sürüyor |

Her satırın resmi URL'si ve sayfa bölümü `turkey-body-properties-2026-09-23.json` içinde.
Refsan 656 kimyası karantinada; toplamı 100'e kapatılmadı, LOI iki kez düşülmedi.
Kaynak hakları belirsiz olduğundan bu kayıtlar açık veri veya model eğitim verisi değildir.
Tam HTML/PDF/fotoğraf indirilmedi; yerel dosya sınırlı olgusal araştırma notlarıdır.

## Çalışan yeni kod

`research/process/reported_properties.py` katalogla bağlantıları, birimleri, sayısal
sınırları ve kimlik tekrarlarını doğrular. Saf karşılaştırma fonksiyonu girdiyi değiştirmez;
sürüm ve input hash üretir. Kaynak çelişkisini aralık kesişimiyle gizlemez.
Tek hedef sıcaklık için `SINGLE_TARGET_NO_OPERATING_RANGE`, çelişki için
`CONFLICTING_SOURCE_WINDOWS` üretir. İki durumda da sonuç `UNAVAILABLE` olur.
Bisküvi ve sır pişirimleri ayrı değerlendirilir. Olasılık her zaman null'dır.

Örnek 1210°C araştırma karşılaştırması: Akasya Stoneware bildirilen aralık içinde;
Refsan 656 bildirilen aralığın üzerinde; Refsan 159/259 için kaynak çelişkisi.
Hiçbiri gerçek sır tutunması, erime, gıda güvenliği veya başarılı sonuç hükmü değildir.

Bu modül araştırma/CLI katmanında çalışıyor. Web/API kataloğuna otomatik bağlanmadı;
lisans ve ürün incelemesi bitmeden üretim seçicisine ticari veriler eklenmeyecek.
Mevcut web kimya hesaplayıcısı değişmedi. Birleşik enerji/kütle/buhar/faz motoru,
kalibre matlık/renk/aderans tahmini ve gerçek deney doğrulaması halen eksik.

## Test ve tekrar üretim

Proje kökünde:

```text
python -m research.commercial_catalogue --audit-date 2026-09-23
python -m research.process.reported_properties
python -m unittest discover -s tests
```

208 araştırma testi geçti; 12 yeni test dahil. Bu tur API ve tarayıcı testleri
tekrar çalıştırılmadı. `research/notebooks/turkey-properties-audit.ipynb` aynı
raporu incelemek için yardımcı defterdir; arayüzde notebook çalıştırıldığı iddia edilmez.
Önceki tarihli audit dosyaları korunmuştur. Aynı ürünün eski kimlik inceleme tarihi
yeni teknik inceleme yapılınca topluca yenilenmemiştir.

## Sonraki paket

Türkiye'de ürün başına TDS/CoA, kuru/kızdırılmış baz ve lisans doğrulaması;
ardından Avrupa ve ABD. Ticari sırda tam formül yoksa içerik uydurulmayacak.
Üreticiye sorulacaklar: çelişkili sıcaklık aralığı, analiz bazı/LOI yöntemi,
şamot elek tanımı, küçülmenin başlangıç referansı, su emme test yöntemi,
belge sürümü/lot ve veri yeniden kullanım kapsamı. Henüz üreticilere mesaj gönderilmedi.
