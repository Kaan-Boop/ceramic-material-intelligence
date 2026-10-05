# Harici açık kaynak araştırma havuzu

Bu belge, uygulamanın çekirdek motoruna kopyalanmadan indirilen açık kaynak yazılım ve benchmark’ları tanımlar. Ham arşivler `storage/external/` altında tutulur ve Git’e alınmaz. Sürüm, SHA-256 ve lisans kararları `data/manifests/external-repositories-2026-10-05.json` dosyasındadır.

## Kullanım politikası

- Harici yazılımın çıktısı `CALCULATED` sonucu için otomatik doğruluk kanıtı değildir. Aynı fixture’ı iki motorla çalıştırıp farkları, UMF convention’ını ve varsayımları raporlarız.
- Harici kod şu anda `research/` veya `packages/` içine kopyalanmadı. Böylece GPL ve veri lisansı sınırları üretim uygulamasına taşınmaz.
- Glazy/GlazyBench gibi kullanıcı reçetesi, fotoğrafı veya metadata’sı içeren kaynaklar üretim verisi değildir. CC BY-NC-SA içerik ticari eğitim veya ürün veri paketi olarak kullanılmaz.
- Lisansı, kullanım amacını veya kimyasal analiz bazını doğrulayamadığımız kayıtlar karantinada kalır; eksik oksitler `0` varsayılmaz.

## Kurulan skill

OpenGlaze’in repository içinde sunduğu `skills/openglaze/SKILL.md` skill’i şu konuma kuruldu:

`C:\Users\MONSTER\.codex\skills\openglaze\SKILL.md`

Bu skill, OpenGlaze’in UMF, sır reçetesi analizi, parti ölçekleme, malzeme ikamesi ve yaklaşık CTE araçlarını nasıl çalıştıracağını anlatır. Skill’i uygulamanın otoritesi yapmıyoruz: fired test tile yerine geçmez, gıda güvenliği iddiası üretmez ve eksik analizleri tamamlamaz.

Bir sonraki güvenli entegrasyon adımı, aynı `RecipeRevision` snapshot’ını kendi `ceramic_engine` ve OpenGlaze’e verip `ComparisonRun` üretmektir. Karşılaştırma; motor sürümü, UMF convention’ı, molar-mass seti, input hash’i ve uyarılarla birlikte saklanmalıdır.

İndirilen OpenGlaze kaynağının CLI smoke testi başarıyla çalıştı: `brief` komutu proje yüzeylerini döndürdü; örnek feldspar/silica/whiting/EPK reçetesi için UMF, oranlar, yaklaşık termal genleşme, limit uyarıları ve `Firing test required` sınırlaması üretildi. Bu sonuç uygulamamızın ölçülmüş deney sonucu olarak saklanmadı.

## Kaynakların rolü

| Kaynak | Projedeki rol | Şu an etkin mi? |
|---|---|---|
| OpenGlaze | Bağımsız UMF/CTE karşılaştırma referansı | Hayır; skill kurulu, adapter sonraki adım |
| pycalphad | İleride Gibbs/phase-equilibrium araştırması | Hayır; seramik TDB yok |
| GlazyBench | Lisanslı olmayan ticari kullanım için benchmark denetimi | Hayır; karantina |
| LIPGLOSS-CALC / LIPGLOSS2 | Kısıtlı UMF optimizasyonu algoritma incelemesi | Hayır; GPL kodu kopyalanmadı |
| Cantera | Genel kinetik/termo-kimya API incelemesi | Hayır; seramik mekanizması yok |
| pymatgen | Faz/yapı veri adaptörü için gelecek referans | Hayır |
| matminer | Gelecek feature-engineering referansı | Hayır; ölçülmüş ve hakları temiz veri bekleniyor |

## Bilinçli olarak yapılmayanlar

Bu kaynakların hiçbirinden yüzey, parlaklık, akış, crazing veya renk olasılığı doğrudan kopyalanmadı. Böyle bir aktarım, lisans ve bilimsel geçerlilik açısından yanlış olurdu. Üretim motoru önce ölçülmüş bir bünye–sır–pişirim serisiyle kalibre edilecek; harici motorlar ancak bağımsız karşılaştırma olarak rapora girecek.
