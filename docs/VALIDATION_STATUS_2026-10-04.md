# Doğrulama durum raporu — 2026-10-04

## Kısa sonuç

Bu rapor yazılımın deterministik ve sözleşme düzeyindeki doğruluğunu ölçer; gerçek sır yüzeyi, yapışma, matlık veya kusur başarısını ölçmez.

| Katman | Durum | Yorum |
|---|---|---|
| Python test paketi | PASS | 294 test geçti, 17 test bilinçli olarak skip edildi |
| Oksit/mol/UMF aritmetiği | PASS | Golden ve invariance vakaları geçiyor; sentetik fixture ile |
| Kütle/LOI muhasebesi | PASS | Baz, ilave ve LOI politikaları test ediliyor |
| API sözleşmesi | PASS | Validation ve health endpoint testleri geçiyor |
| Veri import/replay | PASS | Yerel snapshot ve quarantine sayımları tekrar üretilebilir |
| Sayısal FEM/ısı benchmarkı | PASS | Analitik/nümerik regresyon kontrolü; fiziksel kiln doğrulaması değil |
| Gerçek malzeme analizi | PARTIAL | Kabul edilmiş kaynaklı analiz kümesi küçük; katalog kayıtlarının çoğu araştırma dizini |
| Sır–çamur fiziksel sonucu | NOT_VALIDATED | Eşleştirilmiş fiziksel deney serisi yok |
| Tahmin olasılıkları/ML | UNAVAILABLE | Kalibre edilmiş model yayınlanmıyor |

## Gerçekçilik değerlendirmesi

Mevcut sonuçların güvenilirlik sırası:

1. Birim, kütle, mol, oksit katkısı ve UMF aritmetiği: yüksek yazılım güveni; giriş analizinin doğruluğu ile sınırlı.
2. İdeal enerji, su ve sayısal mekanik benchmarkları: model denklemi ve kütle/enerji korunumu için geçerli; gerçek gözenekli kil veya fırın davranışı değildir.
3. Literatürden aktarılan viskozite/termal tablolar: transkripsiyon ve kapsam kontrolü yapılmış; proje numunesinde tahmin doğruluğu kanıtlanmış değildir.
4. Sırın yüzeyi, akması, yapışması, crazing/shivering ve renk sonucu: henüz fiziksel olarak doğrulanmış değildir; UI’da kesin olasılık gösterilmemelidir.

## Rakip sistem öz-denetimi

Benzer bir laboratuvar ürünü bizi şu konularda geçebilir: ürün/lot bazlı ölçülmüş analizleri daha geniş tutmak, aynı bünye–sır–fırın için tekrar deneylerini bağlamak, gerçek TGA/CTE/viskozite eğrilerini kullanmak ve tahminleri bağımsız test grubunda kalibre etmek. Bizim mevcut avantajımız ise eksik veriyi gizlememek, provenance ve `CALCULATED / OBSERVED / PREDICTED` ayrımını korumaktır.

## Sonraki doğrulama kapısı

Tek bir pilot sistem seçilmelidir:

```text
tek stoneware bünyesi
+ tek sır reçetesi
+ oksidasyon Cone 6 programı
+ aynı uygulama kalınlığı
+ en az üç tekrar numune
+ ölçülmüş kütle, küçülme, su emme, yüzey ve kusur gözlemi
```

Bu seri sisteme girilmeden sır–çamur uyumu veya kusur yüzdesi “doğrulanmış” olarak işaretlenmeyecektir.
