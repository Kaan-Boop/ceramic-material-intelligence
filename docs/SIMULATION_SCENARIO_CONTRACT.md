# Genel simülasyon senaryosu

`research.simulation.scenario` tek bir taş çamur–sır örneğine bağlı değildir. Bir
senaryoda gövde ayrı, üzerine gelen engobe/sır/üst-sır/katkı katmanları ayrı
tanımlanır. Her malzeme `analysis_id` ile sürümlü analiz kaydına bağlanır; isim
üzerinden sessiz eşleştirme yapılmaz.

## Kapsam

- Malzeme rolleri: `BODY`, `ENGOBE`, `GLAZE`, `ADDITION`, `OVERGLAZE`
- Uygulama: daldırma, fırça, püskürtme, dökme, elek ve özel yöntem
- Her katmanda kat sayısı, ıslak/kuru kalınlık ve kuruma süresi
- Ayrı bisque ve final firing programları; her programda ramp, hold ve atmosfer
- Tile, plate, cylinder, sphere veya özel geometri
- Kullanıcının hedefi ve istediği çıktılar

Örneğin kullanıcı yalnızca “1200 °C stoneware” değil; porselen + engobe + iki
sır katmanı, bakır katkısı, kontrollü soğuma ve “fit-risk + firing timeline”
hedefini de aynı sözleşmede ifade edebilir.

## Kapasite geçidi

`assess_capabilities` çözülmüş analiz/properties envanterini senaryo hedefiyle
karşılaştırır. Sonuçlar fiziksel tahmin değildir:

- `AVAILABLE`: bu sürümün yöntemi ve gerekli girdileri var.
- `PARTIAL`: yalnızca sınırlı/ara gösterge var; örneğin CTE karşılaştırması.
- `UNAVAILABLE`: doğrulanmış model veya kritik veri yok.

Eksik özellikler malzeme adına bakılarak doldurulmaz. `melt_fraction`, sıcaklığa
bağlı viskozite, reaksiyon kinetiği, yüzey, renk ve kusur olasılığı bu geçitte
şimdilik `UNAVAILABLE` kalır. Bu, sonraki fizik/deney modülleri eklendiğinde
aynı senaryo sözleşmesini değiştirmeden bağlanabilmesini sağlar.

## Yeniden üretilebilirlik

Senaryonun canonical snapshot'ı SHA-256 ile parmak izi alır. Bir analiz çalışması
bu hash'i, çözülmüş material-analysis snapshot'ını, motor sürümünü ve sabit setini
saklamalıdır. Böylece kullanıcı hedefini değiştirdiğinde eski reçete veya analiz
sessizce üzerine yazılmaz; yeni bir senaryo/revizyon oluşur.
