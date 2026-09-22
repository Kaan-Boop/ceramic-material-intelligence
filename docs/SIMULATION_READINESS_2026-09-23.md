# Simülasyon hazırlığı — 23 Eylül 2026

## Sonuç

Sınırlı araştırma simülasyonu çalışıyor. Birleşik ve fiziksel deneyle doğrulanmış
sır–çamur pişirim simülatörü henüz yok. Web/API prototipi mevcut; eski tarihli
ENGINE_CAPABILITIES_2026-09-22 belgesindeki 'web/API yok' ifadesi tarihsel durumdur.
Bu rapor güncel denetimdir; eski belgeyi geçmişin kaydı olarak değiştirmiyoruz.

## Bu tur yeniden çalıştırılan

- `python -m research.simulation data/fixtures/simulation-bilayer-synthetic.json`
- Çıktı: `storage/simulation/03_runs/24b48267d766-c1244196/`
- JSON, VTK alanları ve HTML görüntüleyici üretildi. HTML bu tur tarayıcıda görsel olarak test edilmedi.
- Girdi hash: `24b48267d766cfc806b3208b8f2d739acf024558c2eb4d7b48a6f1229dba3443`.
- 208 araştırma testi, 6.063 saniye, OK. Yazılım testidir; fiziksel doğrulama değildir.
- Kullanılan Python ortamında scikit-fem var; CoolProp, Cantera ve pycalphad yok.
  Bu tespit diğer ortamlar hakkında sonuç çıkarmaz. Önceden kaynak dosyası arşivlemek kurulum değildir.

Örnek, 20–100°C geçerlilik aralığı verilmiş sentetik malzemelerle 80°C referansından
30°C sınır koşullarına iki pişmiş katının lineer termoelastik davranışını inceler.
1200°C'de eriyen sırın simülasyonu değildir. Ağ yakınsaması ve fiziksel doğrulama
raporda sırasıyla NOT_ESTABLISHED ve NOT_PERFORMED durumunda.

| Katman | Durum | Kritik sınır |
|---|---|---|
| Reçete/oksit/mol/UMF | Çalışıyor | Kabul edilmiş analiz ve açık baz gerekiyor |
| Pişirim aralığı kontrolü | Çalışıyor | Üretici beyanı karşılaştırması; sonuç garantisi değil |
| Katı ısı ve termoelastisite | Araştırma örneği çalışıyor | İdeal arayüz, sabit özellik; erime/kuruma yok |
| Buhar taşınımı | Basitleştirilmiş modül | Dışarıdan verilmiş kaynak, izotermal yaklaşım; enerji bağlantısı yok |
| Gerçek TGA | Dosyalar edinilmiş, kabul edilmemiş | 16 ikili cihaz kaydının sayısal düzeni doğrulanmadı |
| Matlık/renk/aderans/çatlama olasılığı | Hazır değil | Eşlenmiş deneyler ve kalibre model yok |

## Yeni kaynak adayları ve yeniden incelenen referanslar

Bu tur üç referans inceleme kaydı eklendi; tam repo veya makale dosyası indirilmedi.
CoolProp, Cantera ve pycalphad yeniden incelendi; yeni kaynak sayısına eklenmedi.

1. [Hamopy](https://github.com/srouchier/hamopy): Python ile 1B bağlı ısı/hava/nem
   transferi; sıvı ve buhar depolama/akış yaklaşımı. README ve lisans sayfası incelendi,
   LGPL-3.0 olarak bildirilmiş. Başlangıç alanı bina malzemeleridir. Kuruma denklemleri
   ve benchmark karşılaştırması adayı; yüksek sıcaklık seramik modeli olarak kabul edilmedi.
   Entegrasyon öncesi sürüm sabitleme, lisans yükümlülükleri ve bağımlılık incelemesi gerekir.
2. [LBNL HygroThermFEM](https://github.com/LBNL-ETA/HygroThermFEM): 2B bağlı ısı/nem
   çözümü, test ve sayısal yöntem dokümanları olan karşılaştırma adayı. README incelendi;
   lisans metninin ayrıntılı incelemesi bekliyor. Mevcut motoru değiştirme kararı alınmadı.
3. [IAPWS-95 resmi kapsamı](https://iapws.org/technical-guidance/release/IAPWS-95):
   su/buhar termodinamiği için referans. Geçerli kararlı akışkan bölgesi erime eğrisinden
   1273 K'ye ve 1000 MPa'ya kadar belirtiliyor. 1273 K yaklaşık 999.85°C'dir;
   1200°C fırına bütün bölgede doğrulanmış model gibi taşınmayacak. Basınç/faz sınırları da gerekir.

[CoolProp Water](https://coolprop.org/fluid_properties/fluids/Water.html) ve
[arayüz dokümanı](https://coolprop.org/coolprop/HighLevelAPI.html) su özellikleri
adaptörü için incelendi. Kod [MIT lisanslı](https://github.com/CoolProp/CoolProp/blob/master/LICENSE);
kurulmadı. Saf su özellikleri, çamurdaki bağlı su veya nemli hava taşınımı modelinin yerine geçmez.
[Cantera termodinamik arayüzü](https://www.cantera.org/stable/python/thermo.html)
ve [pycalphad](https://pycalphad.org/docs/latest/faq.html) gelecekteki faz/gaz
çalışmaları için referanstır; kurulum tek başına doğru seramik faz veri tabanını sağlamaz.

## Sonraki uygulama paketi: doğrulanabilir kuruma modeli

Önce tek numune için düşük sıcaklık alanı tanımlanmalı. Sır erimesine kadar kapsam genişletilmemeli.

1. Su özellikleri adaptörü: T/p/faz sınırları, SI birimleri, doygunluk durumu ve açık hata sözleşmesi.
2. Bağımsız IAPWS kontrol noktalarında özellik doğrulaması; kütüphane sürümü ve tolerans kaydı.
3. Belgeli sayısal TGA export'u veya gerçek gravimetrik kuruma serisi; gaz türünü LOI'den çıkarmama.
4. Numune enerji dengesi + sıvı su/buhar kütle dengesi; buharlaşma enerjisini iki kez saymama.
5. Kütle/enerji residual, zaman adımı ve ağ yakınsaması; ardından tutulmuş deneyle karşılaştırma.
6. Ancak kabulden sonra web'de deneysel kuruma sekmesi. Sır rengi ve tutunma olasılığı ayrı projedir.

Bu tur yeni fizik algoritması, dış paket kurulumu veya kalibre olasılık eklenmedi.
Ticari ürün havuzu 166 kimlikte kaldı; yeni kaynak sayfaları ürün sayısını artırmaz.
