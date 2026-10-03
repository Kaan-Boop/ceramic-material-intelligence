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

## Araştırma arşivi

82 MB'lık yerel SQLite arşivi deployment image'ına kopyalanmaz. Tam arşivli production için ayrı, izinleri ve yedekleme politikası tanımlı bir veri servisi veya volume gerekir. Küçük teorik katalog API image'ında çalışabilir; quarantine kayıtları otomatik olarak kimya motoruna açılmaz.
