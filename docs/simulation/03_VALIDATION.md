# Sayısal doğrulama ve açık eksikler

21 Eylül 2026, Windows / Python 3.12, kilitlenmiş simülasyon ortamı. Bu dosya deneysel seramik doğrulaması değildir.

## Çalıştırılan kontroller

Repository testleri: **94/94 geçti**, atlanan test yok; bunların 14'ü yeni simülasyon testidir. Testler eksik bağımlılık bulunan başka bir ortamda atlanabilir; resmi tekrar komutu izole simülasyon Python'uyla çalıştırılmalıdır.

| Kontrol | Beklenen | Ölçülen |
|---|---|---|
| Serbest, homojen genleşme | `u=alpha*delta_T*x`, gerilme 0 | En büyük yer değiştirme hatası 1,90e-17 m; mutlak gerilme 3,41e-8 Pa |
| Tüm düğümleri kısıtlı homojen ısıtma | `sigma=-E*alpha*delta_T/(1-2nu)*I` | Gerilme hatası 2,33e-10 Pa |
| İki iletken tabaka, sabit sıcaklık sınırları | Seri ısıl direnç çözümü | Sıcaklık hatası 9,95e-14 °C; sınır gücü bağıl dengesizliği 9,06e-15 |
| Transient sine-mode, k/(rho cp)=1 | `exp(-3*pi²*t)` sönümü | n=3/6/9 ağlarında RMS hata 0,01938 / 0,00574 / 0,00256 °C; dt=0,00025 s |
| Aynı CTE, farklı E/nu | Serbest uniform sıcaklıkta gerilme yok | Test geçti |
| Yük iki kat | Yer değiştirme iki, enerji dört kat | Test geçti |
| Sıfır sıcaklık farkı | Sıfır enerji/yer değiştirme | Test geçti |
| Kaydet/tekrar çalıştır | Aynı bilimsel rapor, ayrı run dizinleri | Test geçti; JSON alan sayıları ve dosya SHA-256'ları doğrulandı |
| Geçersiz kapsam | Ham toz, gerçek ölçüm etiketi, aşırı sıcaklık, NaN/Inf, negatif özellikler | Kontrollü ret testleri geçti |

Toleranslar kaynak testlerde açık. İki iletken tabaka benchmark'ında alan 1 m², alt/üst 20/80 °C, katman kalınlıkları 0,5 m, k=2/4 W/(m K). Analitik toplam güç 160 W. Fixture fiziksel bir seramik parçası değildir.

## İki katmanlı parçanın ağ kontrolü

| Ağ | Düğüm | Eleman | Sır katmanında hücre sigma_1 hacim ortalaması |
|---|---:|---:|---:|
| 6×3×(2+1) | 112 | 324 | 7,052 MPa |
| 12×6×(4+2) | 637 | 2.592 | 6,433 MPa |
| 24×12×(8+4) | 4.225 | 20.736 | yaklaşık 5,860 MPa |

Son iki ağda elastik enerji %8,79; sır sigma_1 ortalaması %8,90 değişiyor. **Ağ bağımsızlığı sağlandı demiyoruz.** Bu yüzdeler hata üst sınırı veya güven aralığı değildir. P1 tetrahedronlar ince katman eğilmesinde yetersiz kalabilir; bir sonraki sayısal iş yüksek mertebeli eleman ve bağımsız eğilme kontrolüdür. Tepe gerilmeye göre çatlama kararı alınmaz.

En büyük yer değiştirme kaba/orta ağlarda yaklaşık 7 µm; rijit hareketleri kaldırmak için kullanılan referans sistemiyle ilişkilidir. Şekil uyumluluğu için sonraki karşılaştırmada eğrilik gibi referans sistemine daha az duyarlı nicelikler de kullanılmalı.

OAT duyarlılık: sır CTE'si ve E'si ayrı ayrı ±%10 değiştirilerek dört ek çözüm üretildi. Bu aralıklar **varsayımsal senaryolar**, gerçek ölçüm belirsizliği veya olasılık dağılımı değil. Sayısal rapor `storage/simulation/03_runs/verification.json` içinde.

## NVIDIA

Warp 1.17.0, yerel RTX 3060 Laptop'u gördü. 1.024 float64 `epsilon=alpha*delta_T` işleminde CPU ve CUDA için NumPy referansına karşı maksimum mutlak fark 0. GPU yoksa script bunu kayda geçirir; bu tur GPU vardı.

Bu test yalnızca çalışma zamanı, derleme ve basit çekirdek doğrulamasıdır. FEM montajı/çözümü GPU'ya taşınmadı; performans/hızlanma iddiası yok. GPU hafızası doluluk testi yapılmadı.

## Arayüz ve dosyalar

Offline HTML ve VTK üretildi. Otomatik test JSON yapısını, VTK alan başlıklarını, inline Plotly betiğini ve hash'leri kontrol etti. Bunlar görsel tarayıcı testi değildir. Yerel `file://` adresini tarayıcı aracı güvenlik politikası engelledi; başka kanal üzerinden aşılmadı. Döndürme, menü, gerçek mobil görüntü ve WebGL uyumluluğu kullanıcı tarayıcısında henüz doğrulanmış sayılmıyor. VTK, ParaView'de ayrıca açılıp test edilmedi.

## Bilinen teknik borç

- P2/mixed formulation ve bağımsız FEM karşılaştırması yok.
- Transient uzay yakınsaması var; ayrı zaman adımı yakınsaması ve enerji bilançosu sonraki doğrulama işi.
- Input JSON için temel doğrulama var; üretim Pydantic/API şeması ve bilinmeyen/tekrarlı anahtar sözleşmesi bu prototipte tam değil.
- Doğrusal çözücü için iptal, job kuyruğu, kaynak kotası, kalıcı yürütme günlüğü yok. Node sınırı tek başına bellek garantisi değil.
- Gerçek malzeme, değişken sıcaklık özelliği, fiziksel numune veya cihaz ölçümüyle validasyon yok.
- Radyasyon, konveksiyon, viskoelastisite, sinterleme ve kimya çözümü yok.

Yazılım testleri geçmesi bu teknik borçların kapandığı anlamına gelmez. Doğrulama receipt'i kod hash'lerini ve girişleri içerir; sonuçlar sürüm değişirse yeniden üretilmelidir.
