# Haklar, mahremiyet ve provenance

## Ayrı eksenler

Etiketler OPEN_DATA, NON_COMMERCIAL_DATA, UNKNOWN_LICENSE, USER_GENERATED, PRIVATE_RESEARCH, COMMERCIAL_LICENSE olabilir. Tek enum karar vermez. Mahremiyet PRIVATE/UNLISTED/PUBLIC ayrı; erişim hakkı, yeniden dağıtım ve model eğitimi farklı işlemlerdir.

`RightsPolicy`: store, display, export, derive, research_training, commercial_training, commercial_product_use alanları ALLOWED/DENIED/UNKNOWN. Attribution/share-alike gerekliliği REQUIRED/NOT_REQUIRED/UNKNOWN. Kanıt, tarih, sürüm ve reviewer tutulur.

Kullanıcı dosya yükledi diye internette yayınlama, ticari eğitim veya üçüncü taraf LLM'e gönderme izni verilmiş olmaz. Metin/fotoğraf/dataset/kod hakları ayrı kontrol edilir. Lisans değerlendirmesi ve güvenlik yetkilendirmesi aynı şey değildir.

## Yayın kapısı

Bir release veya export amacındaki **bütün ilgili haklar** ALLOWED olmalı; DENIED veya UNKNOWN kayıt hariç bırakılır. Atıf gereklilikleri export manifest'ine taşınır. NC/SA kayıtlar ticari core'a görünmez birleştirilmez. İlgili release'in lisans uyumu ayrıca değerlendirilir; satır etiketlemek bütün birleşik dataset sorunlarını otomatik çözmez.

Kaynak açıklamasını okuyup yöntem araştırmakla içeriği üründe yeniden dağıtmak farklıdır. Link göstermek bütün belgeyi kopyalamak değildir. API varlığı veya robots allow bir kullanım lisansı değildir.

## Raw ve silme

Raw normal akışta immutable, checksum'lı ve erişim kontrollü. Değişiklik yeni artifact üretir. Kullanıcı silmesi, izin geri çekme veya zorunlu saklama süresi sonunda içerik silinebilir. Tutulması uygun audit bilgisi ve tombstone içerikten ayrılır; hash bile bağlamına göre hassas olabilir.

Kaynak -> DatasetSnapshotMember -> ModelVersion lineage gelecekte kaynağın hangi modelde kullanıldığını bulur. Veriyi silmek modeli temizlemez; gerektiğinde model emekliye ayrılır/yeni izinli veriyle yeniden eğitilir. Silinen kaynak yüzünden replay yapılamıyorsa sonuç açıkça UNAVAILABLE olur.

## Bu deponun durumu

Üçüncü taraf dataset/medya yok. Örnek JSON'lar proje için oluşturulmuş sentetik sözleşmelerdir. Yazılım ve özgün belgeler için açık kaynak lisansı seçilmedi. Kullanıcı adına lisans taahhüdü, ücretli kullanım anlaşması veya public yayın yapılmaz.

Kaynak ayrıntıları: [DATA_SOURCES](DATA_SOURCES.md). Somut ihtilaf veya ticari lisans için yayın öncesi uygun hak değerlendirmesi gerekir; bu belge otomatik hukuki kesinlik üretmez.
