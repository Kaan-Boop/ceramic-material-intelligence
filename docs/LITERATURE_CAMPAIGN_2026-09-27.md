# Seramik motoru literatur havuzu — ilk teslim, tamamlanmamis kampanya

Hedef: en az 1000 ilgili tez/arastirma yayininin bulunmasi, okunmasi ve izinli
verilerinin ayri ayri izlenmesi. Bu hedef henuz TAMAMLANMADI.

## Gercek durum

44 resmi Crossref API sorgusu, 3919 kayit gorunumu, 3078 benzersiz DOI.
841 tekrarlanan DOI gorunumu birlestirildi. 1910 baslikta alan terimi var.
Tur/ikincil ozet/konu elemesinden sonra 1529 aday: 660 dogrudan konu,
869 komsu malzeme bilimi. Bunlar 1487 farkli normalize baslik tasiyor.
Baslik benzerligi ne ayni calismanin kesin kaniti ne bagimsiz deney kanitidir.
Butun adaylar elle ilgi denetimi bekliyor. 1000 dogrulanmis ilgili calisma
bulundugu veya okundugu iddia edilmez. Crossref sorgularinda tez turu 0;
tez kaynaklari ayrica edinilmeli. Ingilizce agirligi ve DOI kapsam yanliligi var.

Crossref metadata: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
API limiti: https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/
Metadata lisansi makale/tam metin lisansi degildir. Bildirilen lisans baglantisi
olan 1528 kayit otomatik acik lisansli veya egitime uygun sayilmadi.
Abstract alanlari bu toplamada alinmadi; dil alani API select tarafindan
desteklenmedigi icin dil dagilimi hesaplanmadi.

## Tam metin pilottaki durum

3 CC BY 4.0 JATS makale mevcut: 1 onceki arsivden hash dogrulamasi ile
yeniden kullanildi, 2 yeni tam metin indirildi. Toplam 8 ham tablo metni
cikarildi; bunlar otomatik temiz/deney verisi degildir.
10.3390/ma13081814 makalesinin dort ana bolumu ve dort tablosunun metni
incelendi. Sekiller gorsel olarak incelenmedi; FULLY_REVIEWED sayilmadi.
Table 4'ten 6 tane-boyutu kaydi kaynak/birim ile staging'e aktarildi.
Motor veya ML egitimine kabul edilen yeni deney seti: 0.

Ham catalog'daki METADATA_ONLY durumu edinme anina aittir; okuma ilerlemesi
data/manifests/literature-pilot-reading-2026-09-27.json dosyasinda ayri tutulur.
Catalog'u yeniden olusturmak inceleme notlarini silmez.

## Kalite bulgulari

- Yuksek: tam metin olmayan kaydi okunmus sayma riski; asama alanlari ayrildi.
- Yuksek: benzer kelimeler dis seramigi, polimer veya karo yapistiricisi gibi
  farkli alanlari da getiriyor. Otomatik filtre yalniz aday uretir; katalog
  akademik literatur derlemesi veya sistematik tarama sonucu degildir.
- Yuksek: makale/preprint, ChemInform ozetleri ve yeniden yayinlar sayiyi
  sisirebilir. DOI tekilligi tek basina bagimsiz calisma sayisi degildir.
- Yuksek: tam metin izni/sekil istisnalari/deney birimleri ayri kontrol edilir.
- Orta: tezler ve Turkce/Asya dillerindeki DOI'siz yayinlar eksik.

## Sonraki okuma protokolu

Her yayin: DOI/tez kimligi, yazarlar, yayin turu, model modulu, haklar,
malzeme/lot, kimyasal baz, deney yontemi, sicaklik/atmosfer, sayisal tablo,
birim, tekrar/belirsizlik, model varsayimlari, bagimsiz dogrulama, uygulanabilirlik.
Asamalar: DISCOVERED -> TITLE_SCREENED -> ABSTRACT_REVIEWED ->
FULLTEXT_AVAILABLE -> BODY_REVIEWED -> FIGURES_TABLES_CHECKED ->
DATA_EXTRACTED -> SCIENTIFICALLY_VALIDATED. Hak onayi ayri eksen.

Once: viskozite/eriyik yogunlugu ve isil ozellikler; sonra TGA/sinterleme;
sonra sir-bunye arayuzu/gerilme; renk/kusur ML en son. Bir yayinda hesaplanmis
degerler olcum olarak etiketlenmez; kaynaklar arasi bagimlilik kaydedilir.

## Dosyalar ve tekrar uretim

storage/research/literature-2026-09-27/: raw API cevaplari ve SHA256 receipts,
catalog.json/csv, reading-queue.json/csv, screening-summary.json, fulltext-pilot/.
scripts/collect_literature.py --fetch: eksik sorgulari getirir; parametresiz offline replay.
scripts/screen_literature.py: offline aday elemesi.
scripts/acquire_literature_pilot.py: sinirli OA pilotu.
262 cekirdek test gecti; 4 yeni baslik eleme testi dahil.
Kaynak toplama testleri 1000 yayin okundugu anlamina gelmez.

Tarayici kullanilmadi; Crossref/Europe PMC resmi API'leri kullanildi.
agent-reach yerel calistiricisi erisim hatasi verdi; kurulum degistirilmedi.
Yeni simulasyon veya tahmin modeli egitilmedi.
