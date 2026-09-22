# Ceramic Glaze Lab — yerel araştırma prototipi

## Teslim, 22 Eylül 2026

Next.js/React/TypeScript arayüz, aynı origin `/api/v1` yönlendirmesi ile FastAPI'ye bağlanır. Python API, mevcut `research/chemistry/recipe.py` motorunu çağırır. Tarayıcıda ikinci bir kimya motoru yoktur. Motorun bilimsel formülleri bu teslimde değiştirilmedi.

Çalışan akış: teorik malzeme seçimi → baz/ilave girişi → kuru kütle → analiz → oksit/molar oran/UMF → sabitlenen raporla UMF karşılaştırması → snapshot içeren JSON export. Malzeme analiz kartları, sürümlü yerel taslak kaydı/açma ve model sınırları bölümü vardır.

Bu M4 yönündeki ilk çalışan araştırma prototipidir; tüm M2/M3/M4 bilimsel ve ürün kabul kapılarının tamamlandığı iddiası değildir. Ticari ürün/lot analiz seti hâlâ eksiktir.

## Bilimsel kapsam

- Dört ideal formül: potasyum feldspat, silika, kaolinit, kalsit. Üretici/lot analizi veya denenmiş sır önerisi değildir.
- Motor teorik analizleri mevcut `recipe_demo.demo()` snapshot'ından çözer. Arayüz alanları bu hesapları taklit etmez.
- Baz miktarları parçadır. İlave miktarı kuru bazın yüzdesidir. UI virgül ve noktayı girişte sayıya çevirir; API yalnızca sonlu JSON sayısı kabul eder.
- API prototip miktar sınırı: sıfır veya 1e-6–1e6; baz gramı 1e-6–1e6; en çok 100 satır. Bu yazılım giriş sınırıdır, fiziksel kullanım önerisi değildir.
- Oksit wt% paydası LOI hariç teorik oksit toplamıdır. Mol% ve UMF ayrı gösterilir. Atomik Si/Al ile SiO2/Al2O3 mol oranı ayrı alanlardır.
- Pişirim sıcaklığı, cone, atmosfer ve bünye yalnızca bağlamdır. Kimyaya sıcaklık/redoks düzeltmesi uygulanmaz. Sıcaklık giriş sınırı 0–1800 °C bir fırın güvenlik sınırı değildir.
- Flux sıfırsa UMF/akı dağılımı UNAVAILABLE, sıfır paydalı oranlar null'dır; UI sıfır göstermez.
- Girdi değişince rapor stale olur. Geç dönen istek yeni girdiyi ezemez. Eski raporun export/sabitleme düğmeleri devre dışıdır.
- Katalog analizlerinde dışarıda kalan oksitlerin sıfır olduğu açık teorik varsayımdır; bu karar ticari ürün analizlerine taşınmaz.
- Kaynak kodu ve sabit seti bağlantıları rapordan görülebilir. Export'ta orijinal analiz snapshot'ları, engine/convention/constants sürümleri ve hash bulunur.

## Kurulum

Proje kökünde PowerShell; Python 3.12 ve Node.js 22 kullanıldı. [Next.js kurulum koşulları](https://nextjs.org/docs/app/getting-started/installation).

```powershell
python -m venv storage/prototype/environment
.\storage\prototype\environment\Scripts\python.exe -m pip install -r requirements-prototype.lock
cd apps/web
npm ci --ignore-scripts
$env:NEXT_TELEMETRY_DISABLED = '1'
npm run build
cd ../..
```

Araştırma ortamı değiştirilmez. Python doğrudan/dolaylı sürümleri `requirements-prototype.lock`, npm bağımlılıkları `apps/web/package-lock.json` ile kilitlidir. Python lock hash tabanlı supply-chain doğrulaması sağlamaz; bu ileride güçlendirilecek teknik borçtur. npm `--ignore-scripts` ile kuruldu, gerekli Next yerel SWC paketi ve üretim derlemesi çalıştı.

## Başlatma / durdurma

```powershell
.\scripts\serve-prototype.ps1
```

`http://127.0.0.1:3000` adresini açın. Script terminalini açık bırakın; Enter iki çocuğu kapatır. Başka süreçlerin kullandığı 3000/8000 portlarını sonlandırmaz. Hata logları `storage/prototype/logs/` altındadır. Kurumun PowerShell çalıştırma politikası script'i engellerse politikayı otomatik değiştirmeyin; aşağıdaki iki ayrı terminal komutunu kullanın.

Terminal 1, proje kökünde:

```powershell
.\storage\prototype\environment\Scripts\python.exe -m uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Terminal 2:

```powershell
cd apps/web
npm run start
```

Terminallerde Ctrl+C ile durdurun. Geliştirme için `npm run dev` kullanılabilir; sunucu yine loopback'e bağlıdır. API dokümantasyonu `http://127.0.0.1:8000/docs` adresindedir (Swagger UI harici CDN varlıkları gerektirebilir); OpenAPI JSON ayrıca repoda tutulur.

## API sözleşmesi

| Endpoint | İşlev |
|---|---|
| GET /api/v1/health | Yerel API durumu |
| GET /api/v1/materials | Sürümü sabit teorik katalog ve örnek reçete |
| POST /api/v1/analyses | Stateless hesap; sunucuda kayıt oluşturmaz |

POST gövdesi:

```json
{
  "recipe_name": "Teorik araştırma",
  "ingredients": [
    {"analysis_id": "ideal_k_feldspar", "amount": 40, "role": "BASE"},
    {"analysis_id": "pure_silica", "amount": 25, "role": "BASE"},
    {"analysis_id": "ideal_kaolinite", "amount": 20, "role": "BASE"},
    {"analysis_id": "pure_calcite", "amount": 15, "role": "BASE"}
  ],
  "base_mass_g": 100,
  "context": {"cone": "6", "atmosphere": "OXIDATION", "temperature_c": null, "clay_body": ""}
}
```

Yanıt `request`, `chemistry`, `materials`, `notices`, `report_id`, `persistence=NOT_STORED_EXPORT_TO_KEEP` taşır. Çözülmüş Pydantic girdisi motor hash'inin kaynağıdır; JSON'daki 40 ile 40.0 API'de aynı float'a çözülür. Rapor kimliği bağlamı da kapsar; yalnızca pişirim kaydı değişince kimya aynı kalabilirken rapor kimliği değişir.

Sözleşmeyi yeniden üretmek:

```powershell
.\storage\prototype\environment\Scripts\python.exe -m scripts.export_prototype_contract
cd apps/web
npm run generate:api
npm run typecheck
```

`contracts/prototype-openapi.json` ve üretilmiş `lib/api-schema.d.ts` birlikte sürümlenir. Hatalar code/path/message/severity içerir; kullanıcı girdisi hata yanıtına aynen kopyalanmaz.

## Testler

```powershell
# API'nin bağımsız ortamı
.\storage\prototype\environment\Scripts\python.exe -m unittest discover -s apps/api/tests
# Mevcut bilimsel/research ortamı
.\storage\simulation\00_environment\Scripts\python.exe -m unittest discover -s tests
# Sunucular açıkken tarayıcı testleri
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) 'storage/prototype/browsers'
cd apps/web
npx playwright install chromium
npm run test:e2e
```

Teslim kontrolü:

- Mevcut 177 test geçti (4.938 s); yeni 8 API testi geçti (0.555 s).
- 12 Playwright testi geçti (8.7 s): Chromium masaüstü ve iPhone boyutunda Chromium emülasyonu. Gerçek iPhone veya Safari/WebKit testi **yapılmadı**.
- Gerçek API yanıtı, virgüllü girdi, stale koruması, UMF karşılaştırması, export içeriği, sıfır baz, sıfır flux, yerel taslak, ilave, bağlantı hatası, geç yanıt ve bölüm geçişleri test edildi.
- `npm run typecheck` ve `npm run build` başarılı. Sayfa runtime hatası ve Next hata overlay'i kontrol edildi. Masaüstü/mobil raporda yatay sayfa taşması yok.
- Masaüstü ve dar ekran rapor görüntüleri incelendi (`apps/web/test-results/`, Git dışı).
- `npm audit --omit=dev`: bu çalıştırmada 0 bildirilen açık; tam güvenlik denetimi değildir.
- agent-browser hem sistem Edge hem izole Chromium bağlantısında `CDP response channel closed` verdi. Bu araçla doğrulama yapılamadı; aynı uygulama Playwright ile yukarıdaki kapsamda doğrulandı. Bu sınırlama gizlenmedi.
- Starlette TestClient/httpx entegrasyonu deprecation uyarısı veriyor; testler geçiyor. Test istemcisi uyumluluğu sonraki bağımlılık bakımında ele alınmalı.

## Güvenlik, saklama ve ertelenenler

Yalnızca loopback, auth yok; LAN/internet yayınına uygun değil. Host/origin kontrolleri, 64 KiB POST sınırı, no-store yanıtları, access-log kapatma vardır; bunlar auth yerine geçmez. Kalıcı sunucu kaydı, PostgreSQL, hesap yönetimi, yedekleme, fotoğraf/test kaydı, custom üretici analizi girişi, fizik modeli çalıştırma, ML, AI, PWA/offline hesap bu teslimde yoktur.

Taslak yalnızca açık kullanıcı eylemiyle localStorage'a yazılır; otomatik kurtarma/versiyon arşivi değildir. Tarayıcı verisi temizlenebilir. JSON raporu yeniden üretim için dosya çıktısıdır; bu sürümde rapor import ekranı yoktur. Sabitlenen karşılaştırma sayfa yenilenince kaybolur.

Next.js becerisi sunucu/istemci sınırlarının korunmasını; React incelemesi sürümlü, hataya dayanıklı yerel taslak saklamayı ve eski yanıt korumasını yönlendirdi. Mevcut kirli README, edinme ve fizik araştırma dosyalarına dokunulmadı.

Sonraki teslim önerisi: önce bu prototipte kullanıcı akışı değerlendirmesi; ardından izinli gerçek malzeme analizleri ve kalıcı reçete/deney defteri. Enerji-kütle modeli ayrı bilimsel doğrulama hattında gelişmelidir.
