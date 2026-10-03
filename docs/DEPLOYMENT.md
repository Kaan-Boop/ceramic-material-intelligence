# Dağıtım sınırları

## Bileşenler

- `apps/web`: Vercel üzerinde Next.js frontend.
- `Dockerfile.api`: FastAPI kimya ve analiz API'si.
- `storage/local-glazy`: büyük yerel araştırma arşivi; Git ve API image'ına dahil edilmez.

## API çalıştırma

```powershell
docker build -f Dockerfile.api -t ceramic-api .
docker run --rm -p 8000:8000 ceramic-api
```

Sonra `GET http://localhost:8000/api/v1/health` ile servis kontrol edilir.

## Vercel bağlantısı

Vercel projesinde `API_ORIGIN` değişkeni FastAPI servisinin kök adresini göstermelidir. Değişken tanımlı değilse yerel geliştirme varsayılanı `http://127.0.0.1:8000` kullanılır. API servisinin CORS/TrustedHost ve arşiv depolama politikası ayrıca yapılandırılmadan production yayını yapılmaz.

## Render prototip deploy'u

Kök dizindeki `render.yaml`, Docker tabanlı ücretsiz bir web service ve `/api/v1/health` kontrolünü tanımlar. Render Dashboard'da repository'yi bağlayıp Blueprint'i uyguladıktan sonra oluşan `onrender.com` adresi Vercel'de `API_ORIGIN` olarak kullanılır. Ücretsiz servisler 15 dakika boşta kaldığında uykuya geçebilir ve yerel dosya sistemi kalıcı değildir; bu nedenle bu ayar araştırma prototipi içindir, kalıcı arşiv için değildir.

## Araştırma arşivi

82 MB'lık yerel SQLite arşivi deployment image'ına kopyalanmaz. Tam arşivli production için ayrı, izinleri ve yedekleme politikası tanımlı bir veri servisi veya volume gerekir. Küçük teorik katalog API image'ında çalışabilir; quarantine kayıtları otomatik olarak kimya motoruna açılmaz.
