# M2 ikinci edinme dilimi: NIST kil ve feldspat referansları

Kontrol tarihi: 20 Eylül 2026. M2 sürüyor; M3/M4 başlatılmadı.

## WHAT WAS BUILT

NIST/NBS'nin dört resmî Standard Reference Material sertifikası ve NIST kullanım politikası indirildi. İstekler doğrudan resmî dosya adreslerine, hız/sunum boyutu sınırlarıyla yapıldı; site taraması veya ücretli materyal satın alma yok.

39 sertifikalı element değeri, orijinal birim ve belirsizlikleri korunarak küçük bir JSON referans setine aktarıldı. Ortak kaynak/hak alanları dosyanın başında; kayıtlar kaynak URL, PDF SHA-256, sertifika sürümü, sayfa ve tabloyla bağlanır. Belirsizlik ve birim farklılıklarını kontrol eden bağımsız bir referans doğrulayıcı eklendi. Kimya motoru değildir.

## WHAT WORKS

| Referans / resmî URL | Veri | Boyut: seçili değer | Baz | Sertifika tarihi |
|---|---|---:|---|---|
| [SRM 70b](https://tsapps.nist.gov/srmext/certificates/70b.pdf) | Potassium Feldspar, Table 1 elementleri | 7 | AS_RECEIVED açıkça yazılı | 2024-03-26 |
| [SRM 97b](https://tsapps.nist.gov/srmext/certificates/97b.pdf) | Flint Clay, Table 1 elementleri | 12 | DRY: 140°C, 2 saat; en az 250 mg | 1988-04-21 |
| [SRM 98b](https://tsapps.nist.gov/srmext/certificates/98b.pdf) | Plastic Clay, Table 1 elementleri | 12 | DRY: 140°C, 2 saat; en az 250 mg | 1988-04-21 |
| [SRM 99b](https://tsapps.nist.gov/srmext/certificates/99b.pdf) | Soda Feldspar, Table 1 elementleri | 8 | UNKNOWN: bu tabloda açık baz etiketi yok | 2024-08-07 |

Sertifika tarihi analiz tarihi değildir; `analysis_date=null`. 70b için 2033-09-01, 99b için 2032-12-31 kaynakta belirtilen geçerlilik sonudur, uygun saklama/kullanım koşullarına bağlıdır. Arşivlemek herhangi bir fiziksel numunenin güncel geçerliliğini doğrulamaz. Eski kil sertifikalarına keyfî son kullanma tarihi eklenmedi.

### Erişim ve hak incelemesi

| Alan | Karar |
|---|---|
| Source name / author | NIST / National Bureau of Standards |
| Data type | Referans materyal sertifikası; element kütle kesirleri |
| API | Kullanılmadı; doğrudan resmî PDF indirmesi |
| Download / scraping | 4 PDF + 1 politika HTML; scraping gerekmedi |
| License | LicenseRef-NIST-NonSRD-Data-Use; CC BY olarak yeniden etiketlenmedi |
| Commercial / research use | İncelenen non-SRD kullanım koşulları kapsamında ALLOWED; atıf/bildirim/değişiklik belirtme koşulları saklandı |
| Data quality | Table 1 değerleri kaynak tarafından sertifikalı; bizim transkripsiyonumuz tek asistan görsel kontrolünden geçti, bağımsız ikinci inceleme yok |
| Product / AI training | NOT_APPROVED / NOT_ENABLED |

[NIST politikası](https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications), SRD derlemelerini diğer NIST verilerinden ayırır. Bu kabul kararı tüm NIST içeriğinin veya üçüncü taraf içeriklerin serbest olduğu anlamına gelmez; hukuki garanti değildir. NIST platformumuzu onaylamış veya sertifikalandırmış değildir.

### Sayımlar

- Bu dilimde 5 dosya, 890.887 byte; 4 materyal referansı, 39 element değeri.
- Birikimli: **6 kaynak, 29 benzersiz kaynak/dosya/içerik, 1.316.468 byte**.
- Önceki CSV/XLSX/XML/JSON profillemesi 19 dosyayı kapsar. PDF'ler bu sayıya dahil değildir; ayrı transkripsiyon/doğrulama raporundadır.
- Eksiksiz, motor için onaylı gerçek oksit analizi: **0**. 39 element değeri 39 reçete veya 39 malzeme değildir.

## TEST RESULTS

`python -m unittest discover -s tests -v`: **48 test geçti**. Sentetik raw dosyalarla checksum bozulması, eksik receipt, yanlış birim, mükerrer element, hatalı kapsam ve belirsizlik türü denetlendi. Gerçek arşiv doğrulayıcısı ayrıca dört PDF'nin SHA-256 değerlerini kontrol etti ve 4/39 sayımını doğruladı.

PDF becerisi kullanıldı: dört Table 1 sayfası Poppler ile görsele dönüştürülüp başlıklar, birimler ve dipnotlar incelendi. Bu sayede 70b Ca için k=2.5 korunurken, diğer bazı elementlerdeki k=2 kil sertifikalarına otomatik uygulanmadı. Kil belgelerinin tolerans aralığı tanımı ayrı tutuldu. PDF'ler değiştirilmedi.

Testler transkripsiyonun bilimsel doğruluğunun bağımsız ikinci kontrolü veya fiziksel deney değildir. Table 2 / Appendix A/B değerleri bu sürümde seçilmedi; orijinal belgelerde korunur. Eksik elementler sıfıra çevrilmedi; LOI veya oksidasyon durumu türetilmedi.

## KNOWN LIMITATIONS / TECHNICAL DEBT

Referans materyal gerçek bir seramik hammaddesi markasının yerine geçirilmez. 70b, adından veya coğrafi kökeninden hareketle ticari Custer Feldspar'a eşlenmedi. Element→oksit hesabı varsayım, sabit ve redoks politikası gerektirir; bu veri edinme diliminde yapılmadı.

Doğrulayıcı dört incelenmiş PDF hash'ini destekler; genel amaçlı PDF parser/OCR değildir. Sertifika değişirse yeni sürüm ve yeniden görsel inceleme gerekir. Küçük JSON Git'te, raw belgeler ve receipt'ler yerel arşivdedir. Taşınabilir raw yedekleme hâlâ pilot öncesi iş kalemidir.

## Bu turda alınmayan adaylar

- Sibelco'nun [kullanım bildirimi](https://www.sibelco.com/en/disclaimer) açık bir toplu veri yeniden yayın lisansı olarak yorumlanmadı. Üretici CoA/TDS verisi için hak ve baz teyidi gerekli.
- [DOI 10.1016/j.ceramint.2025.06.231](https://doi.org/10.1016/j.ceramint.2025.06.231): adlı ticari ürün analizleri içeriyor; üniversite arşivinde erişilebilirlik yeniden kullanım izni sayılmadı. Lisans doğrulanmadan veri setine alınmadı.
- İncelenen iki MDPI aday sayfası 429 döndürdü; isteklere devam edilmedi veya erişim engeli dolaşılmadı.
- Glazy, Digitalfire, ticari fırın katalogları için önceki hak bekletmeleri geçerli. Fırın model verisi edinildiği iddia edilmiyor.

## NEXT STEP

M2'de hedef artık yalnızca dosya sayısını artırmak değil: açık izinli, baz/LOI/ürün kimliği belirli modern hammadde analizlerini tamamlamak. Buna paralel üretici çamur/fırın bilgileri için bağlantı-kaynak kataloğu tutulabilir; içerik yeniden kullanımı ayrı onay kapısından geçer. İzin talebi metni hazırlanabilir ama kullanıcı onayı olmadan dışarı gönderilmez. M3'e otomatik geçilmez.

## Yeniden çalıştırma ve teslimler

Proje kökünde Python 3.12 ile:

```sh
python -m pipelines.ingestion.acquire --storage storage/research --sources nist-srm-ceramics
python -m pipelines.ingestion.reference_certificates data/reference/nist-certified-elements-v1.json --storage storage/research --receipt storage/research/receipts/d75950363aa34eff968c21d30cf38881.json --output storage/research/nist-validation-recheck.json
```

İlk komut yeni receipt kimliği üretir; yeni ortamda ikinci komuta o yolu verin. Output zaten varsa üzerine yazılmaz; yeni dosya adı kullanın. Yeni indirilen sertifikanın hash'i farklıysa validator bilinçli durur.

- [Seçilmiş element verisi](../data/reference/nist-certified-elements-v1.json)
- [Gerçek arşiv doğrulama sonucu](../data/manifests/nist-reference-validation-2026-09-20.json)
- [Birikimli kaynak manifest'i](../data/manifests/research-acquisition-2026-09-20-batch2.json)
- [İlk dilim raporu](M2_REPORT.md)
