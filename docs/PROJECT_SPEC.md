# Proje kapsamı ve yürütme sözleşmesi

Tarih: 2026-09-20. Kaynak: kullanıcının bu görevde verdiği **Ceramic Material Intelligence Platform — Master Prompt v2**. Bu belge tam metnin birebir kopyası değildir; uygulanabilir kapsam özeti ve izlenebilirlik indeksidir. Önceki 69 maddelik brief, v2 ile çelişmediği ölçüde gereksinim kaynağıdır.

## Ürün

Reçete → seçilmiş hammadde analizleri → hesaplanan kimya → deney koşulları → fiziksel numune → gözlemler → karşılaştırma → yeterli kanıt varsa tahmin.

İlk değer: reçeteyi testten önce anlaşılır kılmak, testten sonra değişiklik ve sonuçları izlemek. Evrensel yüzey simülasyonu veya kesin uyumluluk iddiası yok.

## Başlangıç sınırları

- Responsive web öncelikli; native mobil ertelendi.
- Cone 6 civarı oksidasyon stoneware, **önerilen pilot alanı**. Kullanıcının gerçek malzemeleri ve fırını henüz bilinmiyor; kesinleşmiş deney protokolü değil.
- Kimya hesabı pilot cone ile kısıtlanmaz. Kapsam dışı fiziksel yorumlar/tahminler devre dışı kalır.
- İlk UI Türkçe; domain, API ve entity adları İngilizce.
- Hesap/gözlem/tahmin ve kaynak/lisans ayrımı temel gereksinim.
- Yerel tek kullanıcı prototipiyle başlanabilir; özel veriye dış erişim açılmadan auth ve nesne bazlı yetki zorunlu.

## Yetki ve çalışma sınırı

Kullanıcının 2026-09-20 tarihli “Tamamdır devam” mesajı, önceki teslimde tanımlanan **M1'e devam** olarak yorumlanmıştır. M2 dataset edinmesi veya M3+ uygulama geliştirmesi başlatılmaz.

M1: araştırma kararları, şema, sözleşme örnekleri, bilimsel doğrulama planı, Git ve teslim raporu. Çalışan yazılım iddiası yok.

Rutin teknik kararlar gerekçeyle alınır. Büyük mimari/kapsam değişikliği, ücretli hizmet, ticari lisans, yıkıcı migration ve yeni gizlilik riski kullanıcıya taşınır. Dış kişilere mesaj gönderilmez.

## Bilgi türleri

`evidence_kind`: CALCULATED / OBSERVED / PREDICTED.

`method_kind`: DETERMINISTIC / EMPIRICAL / STATISTICAL / ML / AI.

`status`: AVAILABLE / PARTIAL / UNAVAILABLE / NOT_APPLICABLE.

`qualifiers`: ESTIMATED / THEORETICAL / REPORTED / MEASURED / HYPOTHESIS gibi birden fazla değer taşıyabilir.

`OUT_OF_DOMAIN`, `INSUFFICIENT_SUPPORT`, `MISSING_ANALYSIS`, `ZERO_FLUX` durum enum'u değil, makine okunabilir neden kodlarıdır.

CALCULATED doğruluğu sertifikalandırmaz. OBSERVED yanılmaz değildir. Belirsizlik bilinmiyorsa null ve nedeni saklanır; sıfır yazılmaz.

## Ürün teslimleri

- M1: tasarım sözleşmesi.
- M2: izlenebilir sınırlı referans seti ve validator.
- M3: bağımsız motor.
- M4: ilk çalışan tarayıcı prototipi.
- M5: kalıcılık/replay.
- M6: deney MVP'si.
- M7: PWA/cihaz akışı.
- M8: kimyasal benzerlik ve pilot doğrulaması.

İlk brief'teki Phase 0–10 vizyon başlıkları uzun vadeli yetenek alanlarıdır. Komut dilindeki “PHASE 1” M1 başlangıcıdır; eski brief'teki “dataset fazı” anlamında kullanılmaz. Bundan sonra iş takibi M1–M8 kimlikleriyle yapılır.
