# 3B fizik–kimya araştırması — başlangıç teslimi

Kontrol tarihi: 21 Eylül 2026. Kullanıcının yerel fizik/simülasyon geliştirme isteği üzerine M2 yanında açılan araştırma hattı; M3 kimya motorunun veya M4 web MVP'sinin tamamlandığı anlamına gelmez.

## Ne çalışıyor?

- Gerçek üç boyutlu tetrahedral FEM ağı: iki katman, arayüzde ortak düğümler.
- Sabit özellikli ısı iletimi; ayrı backward-Euler geçici ısı benchmark'ı.
- Sıcaklık alanından küçük şekil değiştirmeli, doğrusal izotrop termoelastik gerilme ve yer değiştirme.
- Kaynak kodu/girdi hash'leri, paket sürümleri, sayısal denge ve analitik kontrol raporları.
- JSON + VTK + internet gerektirmeyen, döndürülebilir Plotly 3B HTML çıktısı.
- GPU uygunluk deneyi: NVIDIA Warp CPU/CUDA float64 termal şekil değiştirme çekirdeği.

**Bu bir sentetik sayısal araştırma prototipidir. Gerçek reçete, ham çamur pişirimi, kırılma olasılığı veya bütün reaksiyonların simülasyonu değildir.** Ağ yakınsaması ve fiziksel deney doğrulaması tamamlanmadı. Varsayımlar arayüzde de görünür.

## Dosyalama

```text
docs/simulation/                         İnsanların okuyacağı kararlar ve kontrol raporları
  00_INDEX.md                           Başlangıç, komutlar, klasör rehberi
  01_ENGINE_SELECTION.md                Motorlar, kaynaklar, lisans/kapsam ayrımı
  02_MODEL_SCOPE.md                     Denklemler, birimler, geçerlilik
  03_VALIDATION.md                      Testler, ölçülen hatalar, açık eksikler
  04_NEXT_EXPERIMENTS.md                Ham malzemeden pişmişe geçiş planı
research/simulation/                    Bizim araştırma kodumuz
  core.py                               Veri tipleri, FEM ve sayısal fizik
  __main__.py                           Snapshot ve deney çalıştırma
  verify.py                             Analitik, ağ ve duyarlılık kontrolü
  warp_probe.py                         Ayrı CPU/GPU altyapı kontrolü
  export.py                             JSON dışındaki VTK/HTML sunumu
data/fixtures/simulation-*.json          Açıkça sentetik deney girdisi
data/manifests/simulation-sources-*.json Lisans, kaynak, commit, SHA-256, dosya envanteri
pipelines/ingestion/simulation_sources.py Sınırlı izinli kaynak edinme
tests/test_simulation.py                 Otomatik doğrulama
storage/simulation/                     Git dışında, yerel çalışma alanı
  00_environment/                       İzole Python, kurulu paketler, Warp önbelleği
  01_sources/raw/sha256/                 Değiştirilmemiş, hash adresli kaynak dosyaları
  01_sources/by_source/                 Aynı dosyaların kaynak/commit/ad ile okunabilir kopyası
  03_runs/<input-hash>-<run-id>/          Her çalıştırmaya ayrı girdi/sonuç/3B çıktı
  03_runs/verification.json              Son sayısal doğrulama raporu
  03_runs/warp-probe.json                GPU uygunluk raporu
  dependency-plan.json                  Kurulum öncesi çözülmüş paket planı
  install-report.json                   Gerçek kurulum ve wheel hash kayıtları
```

Numaralar işlev gruplarıdır; kaynak dosyalar sonuç klasörüne taşınmaz. `02_packages` ancak çevrimdışı wheel arşivi gerektiğinde açılır; henüz yok. Büyük ortam ve çıktılar Git'e girmez. İndirilen üçüncü taraf dosyalar proje kodu diye yeniden lisanslanmaz. İlk başarısız dışa aktarma denemesinin kısmi dizini korunmuştur; yalnızca `receipt.json` bulunan run dizinleri tamamlanmış teslim sayılır.

## Yerelde tekrar çalıştırma

PowerShell, repository kökünde; buradaki Python ortamı kurulmuştur:

```powershell
& './storage/simulation/00_environment/Scripts/python.exe' -X utf8 -m unittest discover -s tests -v
& './storage/simulation/00_environment/Scripts/python.exe' -X utf8 -m research.simulation data/fixtures/simulation-bilayer-synthetic.json
& './storage/simulation/00_environment/Scripts/python.exe' -X utf8 -m research.simulation.verify data/fixtures/simulation-bilayer-synthetic.json --output storage/simulation/03_runs/verification.json
& './storage/simulation/00_environment/Scripts/python.exe' -X utf8 -m research.simulation.warp_probe --output storage/simulation/03_runs/warp-probe.json
```

İkinci komutun yazdığı dizindeki `index.html` tarayıcıda açılır. Dört görünüm: katman, sıcaklık, en büyük asal gerilme, yer değiştirme. Son ikisinde geometri 50 kat deforme gösterilir; sayısal renk değerleri büyütülmez. HTML yeni FEM hesabı yapmaz; çözücü Python'dadır. Sonraki web uygulaması bu motora API ile bağlanabilir; tarayıcı kısıtı motoru HTML'e taşımayı gerektirmez.

Başka bir Windows x64 / Python 3.12 ortamında, önce venv oluşturulduktan sonra:

```powershell
& './storage/simulation/00_environment/Scripts/python.exe' -m pip install --require-hashes --only-binary=:all: -r requirements-simulation-win-py312.lock
```

Lock bu platforma özeldir; Linux/macOS için aynı wheel hash'leri kullanılamaz. GPU sürücüsü/işletim sistemi değiştirilmedi; ücretli servis, harici hesap, buluta veri aktarımı yok. Kurulum yaklaşık 211 MB wheel indirmesi gerektirdi; açılmış ortam daha büyüktür.

## Donanım kontrolü

Windows; i7-11800H, 8 çekirdek/16 iş parçacığı; yaklaşık 32 GB RAM; RTX 3060 Laptop, 6 GiB VRAM, sürücü 610.62. Başlangıçta C: üzerinde yaklaşık 296 GiB boş alan. Bunlar yerel sorgu sonuçları; her sistem için gereksinim veya performans garantisi değil. CPU FEM bu küçük modeller için seçildi; GPU hız kazanımı ölçülmüş değildir.

## Sonraki güvenli adım

Önce iki katmanlı eğilme için yüksek mertebeli eleman ve bağımsız çözücü karşılaştırması; ardından gerçek malzeme özellikleriyle kalibrasyon. Ham malzemenin dönüşümü için [ayrı araştırma planı](04_NEXT_EXPERIMENTS.md) uygulanacak. Omniverse, ML ve metal modülü bu açıkları kapatmadan etkinleştirilmez.
