# Kaynakli referans viskozite ve ideal akis baglantisi

## Teslim

NBS Standard Sample 710 (soda-lime-silica glass), 29 Haziran 1962 sertifikasi
indirildi; iki sayfasi gorsel olarak incelendi. Kaynak ve SHA256 manifestte.
Referans: https://tsapps.nist.gov/srmext/certificates/archives/710.pdf
Hak politikasi: https://www.nist.gov/open/license

Bu tarihsel referans ticari sir analizi veya guncel sertifikasyon degildir.
Ikinci sayfadaki nominal kimya, sertifikali kimyasal analiz sayilmadi ve malzeme
veritabanina aktarilmadi. Dosya yerel arastirma havuzunda; ticari dagitim/training
onayi verilmedi. NIST'e atif ve kaynak kosullari korunmali.

## Yontem

Sayfa 1: log10(eta/poise) = -1.626 + 4236.118/(T_C - 266).
Pa.s donusumu: log10(eta/Pa.s) = log10(eta/poise) - 1.
Proje araligi 821.5--1434.3 C, Table 1 yuksek sicaklik bolumuyle sinirli.
Bu aralik proje tercihidir; yeni bir NIST gecerlilik iddiasi degildir.
Kaynakta yazan +/-0.020 notu korundu; acik kapsam olasiligi olmadigindan
otomatik %95 guven araligina veya olcum belirsizligine cevrilmedi.

research.process.reference_viscosity.viscosity(T, material_id) yalniz
NBS-710-1962 kimligini kabul eder. Baska receteye aktarim ve ekstrapolasyon yok.
Sonuc PREDICTED / EMPIRICAL: kaynak deneylerine uydurulmus denklem degeridir,
yeni bir olcum degildir.

reference_flow(...) viskoziteyi mevcut ideal, izotermal film hesabina baglar.
Yogunluk, kaynak, girdi turu, kalinlik, egim, sure ve varsayim onayi zorunlu.
Yogunluk kaynagi kullanicinin beyanidir; kaynak metni bulunmasi otomatik dogrulama
degildir. Varsayimsal yogunlukla sonuc SYNTHETIC_SCENARIO etiketlenir.
Gercek raf akmasi, eriyik orani, kusur olasiligi veya tutunma dayanimi uretilmez.

## Dogrulama

9 yeni test: sertifika tablosunun secilmis bes birlesik denklem noktasi,
birim donusumu, sicaklik yonu, malzeme kimligi, aralik ve gecersiz sayilar,
akis el hesabi, varsayim/kaynak zorunlulugu, sure olceklenmesi/replay,
belirsizlik notunun korunmasi. Tum cekirdek testler: 250 gecti.

Tablodaki son sutun ayni denklemden turetildigi icin bu karsilastirma bagimsiz
fiziksel validasyon DEGILDIR; aktarim/birim/uygulama kontroludur.
Yeni bagimsiz laboratuvar deneyi yapilmadi. API/UI baglantisi eklenmedi.

## Sonraki bilimsel kapilar

1. Ayni referans cam icin sicakliga bagli yogunluk ve bagimsiz viskozite
   olcumleri; kaynagin ayni calismayi tekrar etmediginin kontrolu.
2. Zaman-sicaklik serisine baglanti: numune sicakligi ile firin programini ayir;
   aralik disi bolumleri sifir akis diye doldurma.
3. Gercek sir/bunye sistemi icin farkli model veya olcum seti; NBS 710
   denklemini bilesim benzerligi gerekcesiyle otomatik tasima.
