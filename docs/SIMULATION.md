# Senaryo ve simülasyon sınırları

M1'de tanımlanır; M8 sonrası ayrı iş. İlk what-if yalnızca malzeme miktarının normalize reçete ve kimyaya etkisini hesaplar. Yüzey render'ı veya fırın sonucu iddiası yok.

1. Ingredient slider -> yeni geçici senaryo -> aynı Python motoru.
2. Line/biaxial blend -> kontrol/tekrar planı -> gerçek numune sonuçları.
3. İzinli ve doğrulanmış veriyle surrogate model.
4. Bağımsız termal/kinetik araştırma.
5. Metal–ceramic / glass–ceramic arayüz araştırması.

Slider kaydedilmiş recipe revision'ını değiştirmez. API çağrıları debounce/cancel/request generation ile yönetilir; eski yanıt yeni senaryoyu ezmez. Save yeni revision'dır.

Oksit slider'ı reçete sabitken mümkün bir reçete varmış gibi davranmaz. Target oxide chemistry inverse problem'dir. İlk aday nonnegative/constrained least squares; min/max malzeme, mevcut envanter ve hedef basis kısıtlarıyla. UMF normalization nedeniyle objective tanımı ayrıca doğrulanır. Hedef gerçekleşemiyorsa residual ve feasibility raporlanır; optimizer başarılı diye fiziksel sır başarılı sayılmaz.

Substitution yalnızca yüzde eşleştirmesi değil; oxide matrix ile kimyasal yaklaşım. Mineralojik geçmiş, çözünme, particle size, süspansiyon ve firing farkları ayrıca test gerektirir. Optimizer pure deterministic olsa da önerilen reçetenin fiziksel sonucu PREDICTED/UNAVAILABLE olabilir.

Termal: empirical index'i measured CTE ile çıkarmak yok. Uyumlu yöntem, birim, sıcaklık aralığı, bünye dilatometry ve fiziksel deney olmadan çatlama olasılığı üretilmez. Glass viscosity/softening/devitrification ve metal oxidation/interface ayrı veri alanlarıdır. MVP motoru bu özellikleri üretmez.
