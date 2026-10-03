# Viskozite zaman serisi ve kaynak takibi

## Yeni islev

research.process.viscosity_timeline.evaluate: NBS 710 icin verilen numune
sicakliklarini zaman sirasi ile degerlendirir. Isi transferi cozmez.
PROGRAMMED_KILN verisi numune sicakligi olarak kabul edilmez. Kapsam disi
sicakliklarda null + neden uretilir; sifir viskozite/akis varsayilmaz.
Sonuc AVAILABLE/PARTIAL/UNAVAILABLE, girdi snapshot'i ve surumlu hash tasir.
Ornek sayisi kapsami, sure kapsami veya guven yuzdesi degildir.

## Kaynak arastirmasi — 27 Eylul 2026

- Napolitano ve Hawkins (1964), DOI 10.6028/jres.068A.042:
  https://pubmed.ncbi.nlm.nih.gov/31834755/
  Sertifikayi olusturan NBS ve yedi laboratuvar calismasi. Sertifikadan bagimsiz
  test seti diye sayilmayacak. Bibliyografik kayit/ozet incelendi; bu turda tum
  makale ve sayisal tablolar incelenmedi.
- Watanabe, Ohsaka ve Hasegawa (1973):
  https://doi.org/10.2109/jcersj1950.81.939_467
  Yayinci ozeti NBS 710 icin farkli bir basincli deformasyon yontemi ve
  10^10--10^13 poise bolgesini bildiriyor. Bizim 2--6 log-poise bolgemizle
  dogrudan ortusmuyor. Bagimsiz deney adayi; sayisal dogrulamada kullanilmadi.
  Free access yeniden dagitim/training lisansi kabul edilmedi.
- NBS SP 408 katalog arama sonucu yaklasik cam yogunlugu veriyor:
  https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nbsspecialpublication408.pdf
  Bu bir incelenmis yuksek sicaklik yogunluk egrisi degildir. Motora alinmadi.

PMC tam metin sayfalari bu turda bot kontrolu dondurdu; kontrol asilmayip resmi
yayin/bibliyografik sayfalar kullanildi. Yeni kaynak dosyasi indirilmedi.

## Kalan eksikler

NBS 710 icin ayni sicakliklarda izlenebilir eriyik yogunlugu ve modelden bagimsiz,
kapsamla uyumlu viskozite olcumleri henuz dogrulanmadi. Onceki sentetik yogunluk
gercek veriyle degistirilmedi. Birikimli akis, sicaklik gecikmesi ve UI entegrasyonu
bu teslimde yok. Yeni 8 test dahil toplam 258 cekirdek test gecti.
Bu sayisal/yazilim dogrulamasidir; bagimsiz fiziksel validasyon degildir.
