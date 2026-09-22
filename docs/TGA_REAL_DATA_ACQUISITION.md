# Gerçek termal analiz verisi — kabul kapısı

22 Eylül 2026. Kaynak: Fernandez-Sanchez, Cuesta, De la Torre, Santacruz, Leon-Reina ve Aranda, [Mix and Measure III veri seti](https://zenodo.org/records/17659041), DOI 10.5281/zenodo.17659041; yayın 20 Kasım 2025. Zenodo resmi API metadata'sı CC-BY-4.0 ve açık erişim bildiriyor. Atıf ve değişiklik bildirimiyle ticari kullanım mümkün; bu, bilimsel uygunluk onayı değil.

## Sonuç

4,468,486 bayt Thermal analysis.zip indirildi; yayıncı MD5 ve yerel SHA256 kontrol edildi. 16 cihaz dosyası, içerik hash'ine göre 0 birebir kopya. Her dosya bir termal analiz kaydı adayı; LC3/kalsine kil-çimento çalışmasıdır, sır reçetesi veya saf kaolinit referansı değildir.

16/16 dosya karantinada, motor için kabul edilen 0. Yalnızca UTF-16 başlık alanları okundu. İkili gövdenin kayıt düzeni doğrulanmadı; bu nedenle satır sayısı, sayısal eksiklik, zaman monotonluğu ve kütle eğrisi değerlendirilmedi. Ham dosyalar değiştirilmedi, zip diske açılmadı. Başlık raporu operatör ve cihaz bilgisayar yollarını içermez.

Örnek LC3-CC1_7d.001 başlığı: SDT Q600; 37.060 mg başlangıç size bilgisi; Time (min), Temperature (°C), Weight (mg), Heat Flow (mW) sinyalleri; 10 °C/min ile 1000 °C hedefi; Gas2 Nitrogen 100 mL/min. Bunlar kayıtlı başlık değerleridir, gerçek ölçümün tamamında sabit koşul gerçekleştiğinin doğrulaması değil. Dosya adı ile cihaz sample adı farklı; numune eşlemesi ayrıca araştırılmalı.

## Riskler ve kararlar

| Bulgu | Kanıt / önem | Karar |
|---|---|---|
| Doğrulanmamış ikili kayıt düzeni | 16/16 dosya; yüksek risk, başlık sonrası metin decode başarısız | Sayıları tahmin ederek unpack etme; belgeli okuyucu veya resmi ASCII/CSV export gerekli |
| Gaz miktarı/türü ayrımı yok | Seçilmiş başlık kanalları TGA/DSC; su tahsisi doğrulanmadı | Buhar replay kapalı |
| Malzeme kapsamı farklı | Veri seti çimento/LC3 araştırması | Sır/kil kinetiğine doğrudan genelleme yok |
| Sayısal kalite bilinmiyor | Henüz doğrulanmış satır yok | Eksik veri oranını %0 gösterme; NOT_ASSESSED |

İndirme sırasında PowerShell TLS hatası verdi. Mevcut Python resmi-export istemcisi aynı API'ye standart sertifika doğrulamasıyla erişti; TLS kapatılmadı. Web aracı sayfa erişim hatası verdiği için yayıncının resmi API metadata'sı esas alındı.

## Yeniden üretim

`pipelines/ingestion/tga_sources.py`: lisans kontrollü, sınırlı API indirme ve checksum receipt. `pipelines/ingestion/tga_inspect.py`: hash kontrolü, izinli başlık alanları, dosya bazında karantina. Manifest'ler `data/manifests/tga-zenodo-17659041.json` ve `tga-17659041-quality.json`. Scriptler mevcut receipt'i ezmez. Ham veriler `storage/tga/17659041/raw/sha256/` altında.

İncelenebilir notebook: `research/notebooks/tga-source-inspection.ipynb` (kod korunmuştur; notebook arayüzünde çalıştırılmadı). Aynı başlık kontrolü CLI ile 16 dosyada çalıştırıldı. 171 test geçti; atlanan test yok. İki yeni test ikili veriyi ölçüm sanmamayı ve bilinmeyen formatı reddetmeyi doğrular.

Sonraki adım: bu cihaz formatı için belgeli/açık lisanslı okuyucu araştırması veya sayısal metin export'u bulunan başka termal veri seti. Doğrulanmış sayısal veri olmadan kinetik katsayı veya gerçek buhar salımı eklenmedi. Veri kalitesi becerisi özellikle bu kabul sınırını görünür kıldı.
