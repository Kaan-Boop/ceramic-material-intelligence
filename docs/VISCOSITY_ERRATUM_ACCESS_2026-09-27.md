# Düzeltme metni erişim kontrolü

27 Eylül 2026. Sonuç: **yayının kimliği doğrulandı; düzeltmenin içeriği edinilemedi.**

Önceki incelemede aday olan `10.1016/j.chemgeo.2004.01.002` DOI'si, [Crossref kaydı](https://api.crossref.org/works/10.1016%2Fj.chemgeo.2004.01.002) ve [yayıncının XML API'si](https://api.elsevier.com/content/article/PII:S0009254104000233?httpAccept=text/xml) ile doğrulandı. Yayıncı kimliği `S0009254104000233`; tarih 15 Kasım 2004. [Yayıncı sayfası](https://www.sciencedirect.com/science/article/pii/S0009254104000233).

API yanıtının `full-text-retrieval-response` adını taşıması tam metnin geldiği anlamına gelmiyor: alınan XML'de yalnızca `coredata` var, düzeltme gövdesi yok. Yayıncı `openaccess=0`, `openaccessArticle=false`, `openArchiveArticle=false` bildiriyor. Bu kontrol, yazarın başka yerde izinli bir kopyası bulunamayacağının kanıtı değildir; yapılan taramada böyle bir kopya bulunamadı.

Crossref'teki TDM lisans bağlantısı otomatik açık lisans, ticari veri kullanımı veya model eğitimi izni sayılmadı. Metin biçimli API isteği 400 biçim hatası verdi; ardından Crossref'teki XML biçimi denendi ve metadata alındı. Bu iki sonuç ayrı kaydedildi. Satın alma, hesap açma, yazara mesaj gönderme veya erişim engeli aşma yapılmadı.

## Sayısal veri kararı

- Trachyte: 24; Phonolite: 20 sıcaklık satırı. Toplam **44 satırın düzeltme kontrolü bekliyor** durumu korunur.
- Hangi değerin değiştiği bilinmiyor; 44 satırın yanlış olduğu iddia edilmiyor.
- 185 satırlık özgün transkripsiyonun SHA-256 değeri değişmedi: `220adb44c5609554d5e7d1c40ac06ffd9088aa48e81e39312e5f3bc2e22ab6ee`.
- Diğer 141 satır bu özel düzeltme beklemesinin dışında olsa da bağımsız doğrulama için otomatik onaylı değildir.
- Fizik motoruna veri/katsayı aktarılmadı. Kod değişmedi; bu teslimde yazılım test paketi yeniden çalıştırılmadı. JSON, satır sayısı ve kaynak hash'i kontrol edildi.

[Erişim inceleme kaydı](../data/manifests/viscosity-erratum-access-2026-09-27.json) ham API yanıtı arşivi değil, gözlemlenen alanların yapılandırılmış inceleme notudur. Önceki tarihsel kaydı değiştirmez; yalnızca DOI belirsizliğini kapatan yeni kanıt ekler.

## Nasıl ilerleyebiliriz?

Düzeltme kolu, yasal tam metin sağlanana kadar bekler. Kullanıcının temin ettiği PDF, kurum erişimi veya izinli yazar kopyası geldiğinde içerik ve satır etkisi incelenebilir. Ücretli erişim veya yazarla iletişim için ayrıca onay gerekir. Aynı aramaları tekrar etmek yerine diğer kaynakların birim/baz ve kalibrasyon örtüşmesi kontrolleri sürdürülebilir.
