# Sürekli ortam çözücüleri — indirme durumunun kapanışı

23 Eylül 2026 edinme partisi, 26 Eylül 2026'da yerel manifest ve dosyalar üzerinden
yeniden kontrol edildi. Bu rapor kurulum veya bilimsel entegrasyon raporu değildir.

Manifest: `data/manifests/continuum-solvers-2026-09-23.json`.
Yerel havuz: `storage/continuum-solvers/2026-09-23/`.

| Kaynak | Yereldeki kapsam | Dosya | Bayt | Kullanım durumu |
| --- | --- | ---: | ---: | --- |
| SfePy | Kaynak ZIP + lisans | 2 | 9.963.833 | Arşiv; kurulu değil |
| OpenFOAM-13 | Kaynak ZIP + lisans | 2 | 72.904.784 | Arşiv; kurulu değil |
| oomph-lib | Lisans, README, 3 örnek sürücü | 5 | 212.480 | Seçilmiş kaynak; çalışabilir paket değil |
| Elmer | LICENSE.md, README, 3 solver kaynağı | 5 | 362.149 | Seçilmiş kaynak; çalışabilir paket değil |
| Toplam | Manifest kayıtları; ZIP içi dosya sayısı değil | 14 | 83.443.246 | Kurulum/çalıştırma/entegrasyon yapılmadı |

Kontrol sonucu: 14 dosya mevcut; her dosyanın boyutu ve SHA-256 değeri manifestle
aynı. Bu yalnız bütünlük kontrolüdür; kod güvenliği, derleme veya fiziksel model
doğrulaması değildir. Bu turda yeni arşiv indirilmedi.

## Kaynak sürümleri ve lisans kapsamı

- [SfePy](https://github.com/sfepy/sfepy):
  `307e51ecf3b57fc364104630e62ae1fa8ed88c55`; kök lisans BSD-3-Clause.
- [OpenFOAM-13](https://github.com/OpenFOAM/OpenFOAM-13):
  `18870c24d21c6b982e2cdec27b2f59738cca5f90`; GPL-3 metni, dosya bildirimleri ayrıca.
- [oomph-lib](https://github.com/oomph-lib/oomph-lib):
  `02c3c99bba3411f00e621ff3ac6b3e92bfb240d5`; LGPL-2.1-or-later ve üçüncü taraf koşulları.
- [Elmer](https://github.com/ElmerCSC/elmerfem):
  `6418e1cf76ceb56202344e4d6004371d33f3a31e`; karma GPL/LGPL kapsamı.

Kök lisans dosyalarının varlığı tüm alt bileşenlerin lisans denetimi değildir.
Özellikle Elmer modüllerinin referans verdiği LGPL metinleri/bileşen bildirimleri ve
oomph-lib'in üçüncü taraf koşulları dağıtım/bağlama öncesi tamamlanmalı. Manifestte
ticari kullanım “uygulanabilir lisansa bağlı” olarak tutulmuştur; sınırsız izin değildir.

Edinme betiği o tarihte branch HEAD'ini çözümleyip commit hash'ini kaydetmiştir.
Manifest sürümü sabitler; betiği başka tarihte yeniden çalıştırmak aynı commit'i
garanti etmez. Aynı manifestteki URL/checksum'lar exact replay için kullanılmalıdır.
Betik mevcut/yarım parti üzerine yazmayı reddeder; tekrar çalıştırılmadı.

## Motorumuz açısından anlamı

Bu kaynaklar FEM/CFD ve arayüz problemlerine adaydır; hazır “reçete -> sır sonucu”
veritabanı veya kalibre seramik modeli değildir. Yeni çözücü indirmek tek başına
eksik viskozite(T), yüzey gerilimi, temas açısı, CTE(T), mekanik ve kinetik verileri
tamamlamaz. Kaynak kod arşivi ile çalışan fizik modülü ayrı envanterlerde tutulmalı.

Mevcut scikit-fem tabanlı araştırma hesapları korunuyor. Önce bu hattın kapsamlı
malzeme girdileri ve deney doğrulaması; ancak somut bir denklem/sınır koşulu ihtiyacı
doğduğunda alternatif çözücü seçimi öneriliyor. OpenFOAM için WSL/sistem kurulumu
yapılmadı. İşletim sistemi değişikliği veya dağıtım lisansı kararı ayrı değerlendirilir.
