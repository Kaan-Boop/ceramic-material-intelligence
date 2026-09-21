# Termal araştırma prototipi — teslim

Tarih: 2026-09-21. Durum: yerel CLI çalışıyor; üretim fizik modeli veya web uygulaması değildir.

## Yapılan

- Saf Python serbest termal strain integrali: sabit veya parçalı doğrusal α(T).
- Sır eksi bünye farkı; referans uzunluğa göre serbest uzunluk değişimi.
- Beş parametre için toplam 10 tek-girdi duyarlılık senaryosu.
- Sıkı JSON sözleşmesi, kaynaksız eğri/birim/kapsam denetimi, tekrar üretilebilir snapshot/hash ve model sürümü.
- Çıktı dosyası üzerine yazmayı reddeden CLI.
- [Kaynaklı fizik mimarisi, araç değerlendirmesi ve geçiş planı](PHYSICS_RESEARCH.md).

## Gerçekten çalıştırılan örnek

Girdi: `data/fixtures/thermal-synthetic.json`. Çıktı: `storage/thermal/demo-2026-09-21-v1.json` (yerel, Git dışında).

Input hash: `c403e3e2a7a80c765166215e02cf76e2b510996dd6be4ac51f6d015dadcaf95f`.

**SENTETİK:** İki katsayı da varsayımdır; ticari ürün veya ölçüm değildir. 520°C referansı gerçek Tg/gerilmesiz sıcaklık iddiası taşımaz. Lref = 100 mm, Tref = 520°C, T = 20°C.

| Çıktı | Model sonucu |
|---|---:|
| Sır α | 8 × 10⁻⁶ /K |
| Bünye α | 6 × 10⁻⁶ /K |
| Sır serbest strain | −0,004 = −%0,4 |
| Bünye serbest strain | −0,003 = −%0,3 |
| İşaretli fark: sır − bünye | −0,001 |
| Sır serbest uzunluk değişimi | −0,40 mm |
| Bünye serbest uzunluk değişimi | −0,30 mm |
| Serbest uzunluk farkı | −0,10 mm |

Sır katsayısına +0,5 × 10⁻⁶ /K eklenen senaryoda fark −0,125 mm; −0,5 × 10⁻⁶ /K senaryosunda −0,075 mm. Bunlar güven aralığı değil, seçilmiş iki senaryodur. Uzunluğu değiştirmek bu modelde strain farkını değiştirmez; mm cinsinden farkı ölçekler.

## Test sonuçları

`python -m unittest discover -s tests -v`: **69 test geçti**; 48 mevcut veri testi ve 21 yeni termal test. Sabit katsayı elle hesabı, değişken katsayı integrali, ters yol, sıfır fark, uzunluk ölçeklemesi, duyarlılık, hatalı girdi, ekstrapolasyon reddi, snapshot ve CLI dosya koruması test edildi. Floating-point karşılaştırmaları uygun testte 12–14 ondalık basamak toleransıyla yapıldı; fiziksel doğruluk iddiası değildir.

## Yapılmayan / sınırlamalar

Gerçek ürün dilatometri verisi, bonded-layer mekanik çözümü, FEM, gerilme/çatlama olasılığı, kimyasal reaksiyon, faz dengesi, sinterleme ve hız etkisi yok. Bağımsız FEM programı çalıştırılmadı; fırın/numune deneyi yapılmadı. NVIDIA/FEM paketleri indirilmedi veya kurulmadı; bu hesap için gerekmediler. Gerçek veri koleksiyonu aynı kaldı.

## Sonraki adım

M2 referans kimyasını tamamlamak ve sır–pişmiş bünye için kullanım hakkı, sıcaklık kapsamı ve ölçüm yöntemi belli genleşme verilerini aramak. Sonra kimya motoru/M4 web akışı; termal araştırma için ölçüm karşılaştırması ve analitik çift tabaka benchmark'ı. Mevcut sentetik fixture üretim girdisi olarak seçilmeyecek. Metal bu doğrulamalardan sonra ayrı modül olarak ele alınacak.
