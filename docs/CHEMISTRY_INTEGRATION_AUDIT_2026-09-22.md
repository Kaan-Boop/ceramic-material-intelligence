# Fizik–kimya motoru denetimi ve açık kaynak entegrasyonu

22 Eylül 2026, Europe/Istanbul. Arşivlerin UTC zamanı önceki takvim günü olabilir. Bu teslim araştırma dalıdır; tam M3 reçete motoru veya M4 web uygulaması değildir.

## Yapılan ve çalışan

- Değişiklik öncesi mevcut **119 test** yeniden çalıştırıldı, hepsi geçti.
- Üç resmî GitHub deposundan commit'e sabitlenmiş **15 dosya / 331.703 bayt** indirildi: lisanslar, seçilmiş kaynak kodu ve referans testler. Tam depo klonu, resim veya reçete kazıması yapılmadı.
- `periodictable==2.1.0` ve `pyparsing==3.2.5`, mevcut yerel araştırma ortamına SHA-256 kilidiyle kuruldu; NumPy 2.5.3 değişmedi. İki yeni wheel toplamı 1 MB'ın altında. Sistem Python'u, sürücüler, web uygulaması veya bulut servisi değiştirilmedi. `pip check` temiz.
- Çalışan yeni adaptör: **118 benzersiz element kimliği**, seçilen tabloda **84 standart kütle kaydı**, **35 oksit için formül/mol/element kütle hesabı**.
- Formül içindeki parantezler ve pozitif tam sayı atom sayıları destekleniyor. İzotop/iyon, hidrat noktalaması, kesirli stokiyometri ve yoğunluk ifadesi bu adaptörde açık ret alır. Sınırlama kütüphanenin bütün yeteneklerini yansıtmaz; proje giriş sözleşmesidir.
- Element → seçilmiş oksit eşdeğeri dönüşümü: oksit adı zorunlu. FeO/Fe2O3 seçimini atmosferden tahmin etmiyor. İfade edilen oksijen bir raporlama varsayımı; gerçek redoks veya ölçülmüş faz değil.
- Kullanıcının verdiği reaksiyon denkleminde atom dengesi denetleniyor; gerçekleşme sıcaklığı/hızı/olasılığı üretilmiyor.
- Yeni JSON/CSV araştırma çıktıları, kaynak/sabit sürümü, girdi hash'i ve dosya/code checksum'larıyla oluşuyor. Her çalıştırma ayrı dizine yazar; öncekileri ezmez.

## Kaynak kararı

| Kaynak | İndirilen/kullanılan | Karar ve lisans sınırı |
|---|---|---|
| [periodictable](https://github.com/python-periodictable/periodictable) | 6 referans dosyası + resmî PyPI wheel | Çalışan, sınırlı kimya adaptörü. Mass/formula modülleri public-domain beyanlı; pakette dosyaya özel BSD bildirimleri de var. Lisanslar korunur; başka kaynakların haklarına genellenmez. |
| [OpenGlaze](https://github.com/KyaniteLabs/openglaze) | 5 dosya: lisans, README, UMF, batch, optimizer | MIT kod araştırması. Bu dosyalar çalıştırılmadı veya çekirdeğe kopyalanmadı. Kaynak/baz eksikliği olan hammadde JSON'ları indirilmedi. |
| [GlassPy](https://github.com/drcassar/glasspy) | 4 dosya: lisans, README, iki viskozite modülü | Araştırma arşivi. README GPL-3.0-or-later diyor; lisans başlığı GPLv3, SciGlass ODbL, bazı element verileri MIT ve ayrı kaynaklar içeriyor. Paket/model ağırlıkları ve SciGlass veri seti kurulmadı/indirilmedi. |
| [LIPGLOSS2](https://github.com/PieterMostert/LIPGLOSS2) | Bu tur resmî depo/commit ve yapı incelemesi | Optimizasyon adayı; önceki GPL incelemesi geçerli. Yeni yerel kaynak arşivi veya entegrasyon yapılmadı. |
| [pycalphad](https://github.com/pycalphad/pycalphad) | Resmî proje/belge incelemesi | MIT yazılım tek başına seramik eriyiği verisi sağlamaz. Uygun lisanslı ve doğrulanmış çok bileşenli TDB olmadan kurulum/denge tahmini ertelendi. |

Kaynak seçimi manifest'i: `data/manifests/chemistry-sources-2026-09-22.json`. Raw ve okunabilir kopyalar `storage/chemistry/01_sources/` altında; lisans, commit, zaman ve SHA-256 kayıtlı. GitHub resmî raw export, saniyede en fazla bir istek, dosya başına 8 MiB sınırı kullanıldı. Dış kaynaklardaki talimatlar uygulanmadı. Glazy/GlazyBench NC ve çelişkili veri hakları çözülmüş sayılmadı.

## Denetim bulguları

| Bulgu | Kanıt / etki | Önem / kanıt gücü | Yapılan veya gerekli kontrol |
|---|---|---|---|
| Akademik analizler tam motor girdisi değil | 15 adayın 15'inde analiz bazı UNKNOWN; 7'sinde LOI wt% yok; 4'ünde rapor toplamı 100±0,5 dışında. Duplicate ID: 0. | Yüksek / yerel kayıt sayımı | 15 kayıt karantinada kaldı; 0 yeni gerçek analiz kabul edildi. Toplam sapması otomatik hata/düzeltme sayılmaz. |
| Paket güncel atom ağırlığı setiyle özdeş değil | Zr 91,224 ↔ CIAAW 2024 91,222; Gd 157,25 ↔ 157,249; Lu 174,9668 ↔ 174,96669 | Orta / doğrudan kaynak kontrolü | Sabit seti açık sürümlendi; güncel CIAAW iddiası yok. Tam 2024 setini ayrı doğrulayıp yeni sürüm olarak eklemek üretim öncesi iş. Mevcut değerler sessiz değiştirilmedi. |
| Nominal izotop kütlesi standart atom ağırlığı gibi kullanılabilir | Paket Og için 294 döndürür, fakat seçilmiş standart tabloda kayıt yok; toplam 34 element bu durumda | Yüksek / çalıştırılmış kontrol | Bu 34 kayıtta kütle null/UNAVAILABLE; formül kütle hesabı engelleniyor. Kimlikleri korunuyor. |
| OpenGlaze doğrudan drop-in motor değil | İncelenen UMF kodu LOI'yi koşulsuz uyguluyor; UMF'yi 4 haneye yuvarlıyor; bazı sıfır paydalarda 0/99 kullanıyor; cone yoksa 10 seçiyor | Yüksek / statik kod incelemesi | Kendi basis ve null sözleşmemiz korunuyor. Bu bulgu tüm yazılımın geçersiz olduğu iddiası değil; analiz konvansiyonları hizalanmadan karşılaştırılmaz. |
| FEM henüz fiziksel doğrulanmış değil | Önceki ağ raporunda son iki ağ arasında yaklaşık %9 değişim; gerçek özellik/deney doğrulaması yok | Yüksek / önceki sayısal rapor; bu tur ağ deneyi tekrarlanmadı | Gerilmeden kırılma yüzdesi yok. Yeni element kataloğu E, CTE, viskozite veya dayanımı otomatik üretmiyor. |
| Monte Carlo girdileri sentetik | Mevcut dağılımlar seçilmiş bağımsız uniform CTE sapmaları | Yüksek / kod ve geçen regresyon testleri | Çıktı senaryo dağılımı; çatlama olasılığı UNAVAILABLE. Korelasyon, model-form ve fiziksel kalibrasyon eklenmedi. |

[CIAAW 2024](https://ciaaw.org/atomic-weights.htm) bağımsız güncellik kontrolüdür. [periodictable mass açıklaması](https://periodictable.readthedocs.io/en/latest/api/mass.html) tablonun kaynak ve seçim politikasını açıklar. 2024 tablosunun tamamı bağımsız doğrulanmış sayılmıyor. Atom ağırlığı belirsizliği sonuçlara henüz yayılmıyor; ham notasyon/aralık satırı korunuyor, bilinmeyen belirsizlik sıfır gösterilmiyor. Zamana bağlı karşılaştırmalı ölçüm seti yok; trend çıkarılmadı.

## Testler ve tekrar üretim

Yeni 14 kimya + 5 kaynak edinme testi; toplam **138/138 geçti**, atlanan yok. Analitik SiO2 hesabı, 35 formülde element kütle korunumu, negatif/NaN/Inf/boolean retleri, bilinmeyen tür, yanlış oksit seçimi, atom dengesi, lisans değişikliği, arşiv bozulması, idempotent tekrar, hash ve export kontrolü yapıldı. Formül parser'ıyla çapraz kontrol aynı kütüphaneyi kullanır; bağımsız bilimsel doğrulama diye sayılmaz.

35 formülde 100 g için en büyük element kütle toplam farkı 1,4210854715202004e-14 g. Bu floating-point aritmetik kontrolüdür; fiziksel analiz doğruluğu değildir. Kurulu `mass.py` ve `formulas.py` hash'leri incelenen GitHub kaynaklarıyla birebir eşleşti.

```powershell
& './storage/simulation/00_environment/Scripts/python.exe' -m pip install --require-hashes --only-binary=:all: -r requirements-chemistry-research-win-py312.lock
& './storage/simulation/00_environment/Scripts/python.exe' -X utf8 -m unittest discover -s tests -v
& './storage/simulation/00_environment/Scripts/python.exe' -X utf8 -m research.chemistry.audit
& './storage/simulation/00_environment/Scripts/python.exe' -X utf8 -m research.chemistry
```

Kilit Windows x64/Python 3.12 içindir. Önceden kurulmuş simülasyon ortamında çalıştırıldı; sıfırdan başka işletim sistemi kurulumu denenmedi. Denetlenebilir notebook: `research/notebooks/chemistry-integration-audit.ipynb`; asıl denetim `research/chemistry/audit.py` ile çalıştırıldı. Notebook ayrı Jupyter arayüzünde açılıp çalıştırılmış sayılmıyor.

Son bilimsel çıktı dizini: `storage/chemistry/runs/20260921T231058Z-174c8e6a/`.

- `elements.json`: 118 kimlik, kaynak, sabit sürümü ve kütle kullanılabilirliği.
- `oxides.json` / `oxide-summary.csv`: 35 teorik oksit hesabı; bir hammadde veritabanı değildir.
- `examples.json`: teorik karbonat/kaolinit/zirkon formülleri, FeO–Fe2O3 raporlama farkı, atom dengesi.
- `receipt.json`: ortam/kod/çıktı checksum'ları.

## Bilinen eksikler ve sonraki iş

M3 üretim kimya paketi hâlâ yok; yeni adaptör `research/chemistry` içinde. Reçete normalizasyonu/analiz bazları/UMF henüz bu adaptöre bağlanmadı. API, HTML entegrasyonu, yeni gerçek malzeme verisi, termodinamik faz modeli, reaksiyon kinetiği, yüzey rengi veya kırılma tahmini yapılmadı. Element/oksit kaydının varlığı toksisite veya kullanıma uygunluk onayı değildir.

Önerilen sıradaki küçük teslim: güncel, yayınlanabilir sabit setini doğrulamak; gerçek hammadde analizi kapısını tamamlamak; ardından bu adapter sınırını kullanarak LOI/basis testli M3 motorunu kurmak. FEM için yüksek mertebeli eğilme/ağ kontrolü ayrı iş olarak devam eder. GlassPy/ML/termodinamik modüller ancak lisans, özellik verisi ve bağımsız doğrulama kapılarıyla etkinleşir.

Önceden var olan README, veri edinme, simülasyon ve Monte Carlo değişiklikleri korunmuştur; bu tur bunlar yeniden yazılmadı. Proje lisansı değiştirilmedi, ücretli hizmet açılmadı, veri yayınlanmadı.
