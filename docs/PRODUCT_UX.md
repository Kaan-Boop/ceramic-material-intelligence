# Ürün akışı ve arayüz sözleşmesi

Tasarım hedefi: laboratuvar okunabilirliği, hızlı reçete girişi, bağlamın erişilebilir olması. Görsel mockup veya frontend bu milestone'da üretilmedi.

## M4 akışı

1. Reçete adı ve base satırları; miktar modu/bazı açık.
2. Malzeme seçimi: ürün + üretici + analiz sürümü/tarihi. Genel isim eşleştirme önerisi onaysız otomatik çözüm değildir.
3. Additions ayrı bölüm; “base üzerine %” ve nihai toplam açık.
4. İsteğe bağlı firing context; cone ve sıcaklık birbirini otomatik doldurmaz.
5. Analiz: normalize recipe, oxide mass/basis, mol%, UMF, açık oranlar, flux dağılımı, veri uyarıları.
6. Kaynak paneli: exact analiz, baz, tarih, kalite boyutları, assumptions. M5'te kaydet/export/replay.

Ana hesap akışı gereksiz bünye/fırın formuyla bloke edilmez. Fiziksel yorum için eksik alanlar ayrıca gösterilir. Kullanıcı yalnızca bir analizi bildiği için tüm deney bağlamı varsayılmaz.

## Etiketler

CALCULATED = Hesaplandı; OBSERVED = Gözlendi/ölçüldü; PREDICTED = Tahmin. Metin+ikon kullan; yalnızca renk değil. OBSERVED yanında kullanıcı raporu/cihaz ölçümü/insan fotoğraf etiketi ayrımı. LLM açıklaması “AI yorumu / hipotez” panelidir.

MVP'de model yoksa predicted sayısal bölüm gizli veya açık “Henüz model yok” durumu. Stull/limit referansı uygulanmadıysa dekoratif sınırlar çizilmez. Boş benzerlik listesi gerçek empty state; sahte kayıt yok.

## Kısmi ve hata durumları

- “Bilinmeyen malzeme”: taslak korunur; seçim/analiz ekleme yolu gösterilir.
- “Analiz bazı bilinmiyor”: tam kimya hesaplanamaz; normalize recipe gösterilebilir.
- “Flux toplamı sıfır”: mol tablosu açık, UMF yok.
- “Bağlantı yok”: yerel taslak düzenlenebilir; eski rapor snapshot tarihi ve stale etiketiyle.
- “Yeni analiz sürümü var”: önceki rapor değiştirilmez; yeniden analiz ayrı eylem.

Bilimsel uyarılar ile UI input hataları ayrı; “yüksek SiO2” gibi fiziksel başarı hükmü veren uyarılar kaynaklı model olmadan eklenmez. İlk warnings baz, eksik veri ve hesap kapsamıyla sınırlıdır.

## Form ve erişilebilirlik

Türkçe ondalık virgül ve nokta kabul politikası test edilir; API'ye canonical decimal sayı gider. Birimler başlıkta ve girdide görünür. °F->°C offset dönüşümü giriş sınırında; heating rate dönüşümü aynı offset'i kullanmaz. Dokunma hedefleri, mobilde yatay taşmayan editör, erişilebilir hata odağı ve keyboard navigation.

Reçete tablosu telefonda satır kartlarına dönüşebilir; ana değer/etiketler gizlenmez. Gelişmiş provenance ayrıntısı açılır panelde; uygulama kullanıcıya engine dosya yollarını göstermez.

## M6 deneyler

Tek firing/application bağlamı birden çok numuneye uygulanabilir; sonra numune özel farklar kaydedilir. Kat sayısı mm kalınlık değildir. Gloss/opacity/texture/crystal bağımsız seçeneklerdir. “Crawled” hem amaçlanan yüzey hem kusur olarak değerlendirilebilir; feature gözlemi ve istenen/istenmeyen sonucu ayrı tut.

MVP sayfaları M4: /analyze, /materials, /materials/[id]. M5: /recipes, /recipes/[id]. M6: /tests. Landing yalnızca gerçek yetenekleri anlatır. /simulate işlev gelmeden açılmaz.
