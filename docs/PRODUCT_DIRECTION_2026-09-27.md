# Ürün yönü: seramik araştırma ve deney laboratuvarı

Tarih: 27 Eylül 2026. Durum: ürün/tasarım önerisi; uygulanmış özellik listesi değil.
Dayanak: kullanıcının tez araştırması amacı, bu turda verdiği Deney Masam görseli,
mevcut `apps/web/components/lab.tsx` ve `process-report.tsx` yapıları.

## Son kullanıcı düzeltmesi — önce bilimsel motor

Aşağıdaki eski tasarım sırası son kullanıcı önceliğiyle değiştirilmiştir:
doğru malzeme verisi → kapsamı ve doğruluğu sınanmış fizik/kimya modelleri →
tutarlı model bağlantıları → laboratuvar simülasyonu → tez/deney iş akışı.
Deney defteri ve 3D görünüm bu zinciri destekler; model geliştirmesinin yerine geçmez.
Güncel teknik sınırlar ve çalışma sırası `SCIENTIFIC_ENGINE_GAPS_2026-09-27.md`
belgesindedir. Belgenin aşağısındaki eski UI-öncelikli sıra uygulanmayacaktır.

## Karar önerisi

Ana ürün, malzeme odaklı bilimsel hesaplayıcı ile izlenebilir deney defterini
birleştiren bir seramik araştırma çalışma alanı olmalı. 3D görüntü bunun isteğe
bağlı bir görünümü olabilir; ürünün merkezi veya bilimsel doğruluğunun kanıtı değil.

Mevcut Ceramic Platform'ın ayrı Python motoru, açık eksik veri durumları ve
CALCULATED / OBSERVED / PREDICTED ayrımı ana temel olarak korunmalı. Antigravity
prototipinin görsel/numune fikirleri ayrı ayrı incelenmeli; bütün kodu ve dataset'i
tek seferde birleştirme, mevcut yapıyı değiştirme veya veritabanı taşıma yapılmamalı.

## Kullanıcı işleri

- Araştırmacı: soruyu ve değişkenleri tanımlar; yöntemi, kaynağı, eksikleri ve
  sonuçların tekrar üretilebilirliğini görebilir.
- Seramikçi: batch hazırlayabilir; bünye, sır, katman, uygulama ve gerçek pişirimi
  aynı numuneye bağlar; numune kimliğini atölyede takip eder.
- Sanatçı/tasarımcı: hedeflediği yüzeyi ve duyusal etkileri kendi diliyle kaydeder;
  teknik ölçümden ayrı estetik değerlendirmelerle denemeleri karşılaştırır.

Ana birim yalnız reçete değil: araştırma projesine bağlı deney ve onun fiziksel
numuneleri. Aynı reçetenin farklı bünyedeki veya farklı soğutmadaki testleri ayrı
sonuçlardır. Sanatsal olarak başarılı olan bir test, teknik olarak kusursuz olmak
zorunda değildir; kontrollü çatlak gibi amaçlanan özellikler otomatik başarısızlık
sayılmamalıdır. Güvenlik değerlendirmesi estetik tercih üzerinden değişmez.

## Referans ekranın sınırlı değerlendirmesi

Bu bir kullanıcı tarafından sağlanan tasarım görselidir. Canlı uygulama akışı,
klavye kullanımı, gerçek mobil ekran, ekran okuyucu veya ölçülmüş kontrast testi
bu incelemede yapılmadı. Görselde 'Tasarım konsepti · Tahmin değil' ifadesi var.

1. Malzeme seçimi: görünür yapı güçlü. Sır, çamur ve ek malzeme ayrı kartlar.
2. Malzeme inceleme: görünür yapı güçlü. Seçili satır ile sağ panel ilişkisi açık;
   analiz bazı, oksit yüzdesi ve teorik etiket aynı bağlamda görülebiliyor.
3. Pişirim/analiz/deney kaydı: yalnız giriş düğmeleri görünür; sonraki adımların
   çalışması veya kullanılabilirliği bu görselden değerlendirilemez.

Korunacaklar: sıcak beyaz zemin, koyu okunur metin, sınırlı yeşil vurgu, belirgin
satırlar, tek sağ inceleme paneli, az sayıda ana eylem, bilimsel sınırlılık metni.

Geliştirilecekler: büyük başlığın çalışma sırasında daha az yer kaplaması; deney
kimliği ve kayıt durumunun görünmesi; yinelenen 'Malzeme ekle' düğmelerinin kapsamının
netleşmesi; eksik analizin yalnız info ikonunda gizlenmemesi; pişirim özetinin görünür
kalması. Sabit alt araç çubuğunun küçük ekran/klavye üzerinde formu kapatmadığı
test edilmeli. Küçük info simgeleri klavye ile erişilebilir ve metinle adlandırılmış
olmalı; ayrıntı yalnız hover ile açılmamalı. Bunlar doğrulanmış erişilebilirlik
kusurları değil, uygulama sırasında kontrol edilecek risklerdir.

## Tek çalışma alanı, katmanlı ayrıntı

Üst satır: proje, deney adı/kimliği, revizyon, taslak/kaydedildi durumu.

Ana bölge: sır reçetesi, çamur bünyesi, ayrı katmanlar/ek malzeme ve pişirim özeti.
Birlikte kullanılan sır ve bünye tek bir toplama birleştirilmez. Sırın base/ilavesi,
bünye katkısı, ikinci sır katmanı ve gömülü metal farklı roller taşır.

Sağ inceleme paneli: seçilen malzeme, oksit, ölçüm veya uyarının ayrıntısı.
Ürün/üretici/lot, analiz sürümü, kaynak, baz, LOI/nem ve eksikler gerektiğinde açılır.
Mobilde aynı bilgi erişilebilir açılır panelde; sayısal tablo gövdesinde blur yok.

Aynı deney bağlamındaki çalışma görünümleri:
- Hazırla: malzeme, miktar, uygulama, pişirim.
- İncele: oksit katkıları, mol/UMF, karşılaştırma ve kapsamlı hesap çıktıları.
- Deney: numune, planlanan/gerçekleşen koşullar, fotoğraf ve ölçüm.
- Karşılaştır: kontrol, varyasyonlar ve tekrarlar.
- Rapor: kanıtlarıyla dışa aktarım.

Tek ekran, bütün alanların aynı anda açık olması demek değildir. Temel bilgiler
sürekli görünür, ayrıntı isteğe bağlı açılır. İlk aşamada kullanıcı ayarlarına
gömülmüş iki ayrı 'sanatçı modu / bilim insanı modu' yerine aynı kaydın katmanlı
okunması daha yalın bir yaklaşımdır.

## Malzemeyi açıklama modeli

Kimlik -> bildirilen kimyasal analiz -> reçetedeki oksit katkısı -> varsa mineral/faz
ölçümü -> kaynaklı bağlamsal açıklama ayrı tutulur. Oksit analizinden gerçek mineral
fazı veya yüksek sıcaklık eriyik türleşmesi kesin çıkarılmaz. Eksik oksit sıfır değildir.

Bir bilgi kartı şu soruları cevaplamalı: Ne? Bu reçeteye ne katıyor? Hangi koşullarda
etkili olabilir? Hangi bilgi eksik? Dayanak nedir? Genel oksit bilgisi ile belirli
ürünün önerilen pişirim aralığı aynı alan değildir. Fotoğraf ürün teşhisi yerine geçmez.

## En uygun motor yaklaşımı

Tek evrensel tahmin modeli yerine katmanlı ve bağımsız modeller:
1. Deterministik kimya: batch, base/ilave, kütle ve oksit katkısı, mol/UMF, açık oranlar.
2. Kaynaklı karşılaştırma: ürün aralıkları, analiz kapsamı, önceki testler; başarı garantisi yok.
3. Sınırlı fizik: gerekli malzeme özellikleri ve sınır koşulları mevcutsa uygun model;
   sonuçla birlikte yöntem, kapsam ve belirsizlik. Eksik girdide UNAVAILABLE.
4. Deneysel istatistik/ML: gerçek, izinli, yeterli çeşitlilikte veri ve bağımsız
   doğrulama sonrası; mevcut olmayan modelden yüzdeler üretilmez.
5. AI yorum: hesap ve kaynakların açıklaması; ölçüm veya nedensellik kanıtı değildir.

Hesaplanabilen kimya, eksik bir fizik modeli yüzünden engellenmemeli. Eksik fizik
çıktısı da sıfır veya düşük risk olarak gösterilmemeli. Motorun karşılaması gereken
temel soru 'Hangi deneyi neden yapmaya değer?' olmalı; yalnız 'sonuç bilinmiyor'
ekranında kalmamak için gerekli ölçüm ve karşılaştırma önerisi sunulmalı.

## Ana çıktı: deney dosyası ve karşılaştırma levhası

Her deney dosyası amaç/hipotez, malzeme/analiz snapshot'ları, uygulama, planlanan ve
gerçekleşen pişirim, hesap raporu, gözlemler/ölçümler, fotoğraflar, yorumlar, belirsizlik
ve kaynakları birleştirir. Reçete güncellenince eski deney sessizce değişmez.

Ana çıktı yalnız PDF veya 3D model değil:
- PDF: yöntemi ve kanıtı okunabilir deney raporu.
- CSV/JSON: birimli, sözlüklü, kaynak/revizyon bilgili analiz verisi.
- Karşılaştırma levhası: aynı çekim/ölçüm koşulları belirtilmiş numune görselleri.

Hesap, gözlem ve hipotez görsel olarak da ayrılır. Kullanıcı 'ipeksi', 'kuru',
'kenarda açılan', 'derinlikli' gibi estetik notları kaydedebilir; bunlar otomatik
gloss metre ölçümüne çevrilmez. Bir kusurun değerlendirilmemesi, görülmediği anlamına
gelmez. Üretilmiş görsel, gerçek test fotoğrafı ile aynı bölümde kanıtsız sunulmaz.

## İlk uçtan uca pilot

Örnek soru: 'Bu beyaz stoneware üzerinde uygulama kalınlığı yüzeyi nasıl değiştiriyor?'
Bu bir öneri; belirli ürün için sonuç iddiası değildir.

Kaynaklı bir sır/bünye seç, kontrol ve kalınlık varyasyonlarını tanımla, uygulama
yöntemini/belirsizliğini kaydet, numuneleri kimliklendir, pişirim ve konumu bağla,
gerçek sonuç/ölçümü kaydet, karşılaştır ve raporla. Kat sayısı kalınlığın kesin ölçüsü
değildir. Tek pişirimdeki çok sayıda numune bağımsız pişirim tekrarları sayılmaz.
Tam deney protokolü tez sorusu ve mevcut ölçüm araçlarıyla ayrıca belirlenir.

Kabul kapısı: bir numune için kaynaktan sonuca kadar iz kopmamalı; tekrar açılan kayıt
aynı hesabı vermeli; ölçülmeyen özellik ölçülmüş görünmemeli; rapor dışarı aktarılmalı.
Bu akış tamamlanmadan yeni 3D efekt veya geniş tahmin modeli öncelik olmayacak.

## Sıra ve durum

1. Önce yarım kalan güvenlik düzeltme paketinin test ve raporunu kapat.
2. Mevcut Ceramic Platform temelinde Deney Masam iş akışının etkileşimli tasarımını doğrula.
3. Kalıcı deney/numune ve revizyon bağlantısını tamamla.
4. Karşılaştırma ve tez çıktısını çalıştır.
5. Veri ihtiyacı somutlaşan bir fizik modelini deneyle doğrula; sonra daha geniş simülasyon.

Bu turda uygulama kodu, veritabanı veya arayüz değiştirilmedi. Önceki güvenlik paketi
kısmen uygulanmış, fakat son toplu yama başarısız olduğu için yeni test dosyası ve
rapor temizliği tamamlanmamıştı; paket bitmiş sayılmıyor. Bu belge o işi tamamlamaz.

## Kaynaklar ve sınırlar

[eLabFTW deney yapısı](https://doc.elabftw.net/docs/usage/user-guide/experiments/)
deney kaydı, ilişkili kaynaklar ve revizyon/export örüntülerine referans olarak incelendi.
[GO FAIR provenance ilkesi](https://www.go-fair.org/fair-principles/r1-2-metadata-associated-detailed-provenance/)
verinin kökeni ve işlenme geçmişinin korunmasına dayanak sağlar. Bunlar önerilen
seramik arayüzünün kullanıcı testi veya fizik motorunun doğrulaması değildir.
Bu turda başka ürün kurulmadı, dataset indirilmedi veya dış servise reçete gönderilmedi.
