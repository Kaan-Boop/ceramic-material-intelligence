# ML ve AI stratejisi — implementasyon ertelendi

M1'de paket, eğitim pipeline'ı, LLM bağlantısı veya model ağırlığı yok.

## Bilgi sınıflandırması

Normalizasyon/UMF: CALCULATED/DETERMINISTIC. Kullanıcı veya cihaz numune değerlendirmesi: OBSERVED/EMPIRICAL. Kayıtlı kusur sıklığı gibi gözlemlerden türetilen özet: CALCULATED/STATISTICAL. Tahmin modeli: PREDICTED/ML. Ampirik expansion: PREDICTED/EMPIRICAL + ESTIMATED; deterministik uygulama olması sonucu ölçüm yapmaz.

AI yorumu ayrı Interpretation kaydıdır: method_kind AI, claim_type EXPLANATION/HYPOTHESIS, evidence refs. Kaynaksız yeni sayı, test veya gerçek neden üretilmez. LLM çıktısı training ground-truth olmaz.

## ML hazır olma kapısı

Etiket protokolü -> bağımsız deney çeşitliliği -> baseline -> grouping/leakage denetimi -> ayrılmış değerlendirme -> kalibrasyon -> out-of-domain/abstention -> yayın kararı.

Sabit “N kayıt yeterli” eşiği yok. Yeni recipe ailesi, yeni kiln/run veya yeni atölye hedefi farklı generalization testidir. Recipe family, duplicate ilişkisi, aynı numune fotoğrafları ve aynı firing run split'te göz önüne alınır. Train/test bağlantı grafiği gerektiğinde birlikte gruplandırılır; tek GroupKFold alanı bütün sızıntıyı otomatik çözmez.

Gloss, opacity, texture, crystals ve defects ayrı hedeflerdir. Bilinmeyen label negatif değil. Kaynak kalite puanı model olasılığı veya confidence değildir. Veri sayısı kadar bağımsız firing/lab sayısı açıklanır.

Baseline: görevine uygun majority/rate/regression; sonra sınırlı adaylar (örneğin Random Forest/CatBoost). Hepsini baştan kurma. Ön işleme yalnızca train'de fit. Calibration ve test ayrı; Brier/log-loss ve göreve uygun hata raporu. [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html), [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html).

## Abstention

status UNAVAILABLE, reason MODEL_NOT_IMPLEMENTED / OUT_OF_DOMAIN / INSUFFICIENT_SUPPORT / MISSING_CRITICAL_FEATURE. 0.81 raw score otomatik %81 kalibre olasılık olarak gösterilmez. SHAP/korelasyon nedensel açıklama değildir.

## Model lineage

ModelVersion: code/runtime, immutable dataset manifest, hak filtresi, feature schema, split policy, baseline ve held-out metrics, calibration, domain sınırı, artifact hash. PredictionRun: exact model+input snapshots. Test sonrasında ölçülmüş bilgi test öncesi tahmine feature olarak sızmaz.

Kaynak geri çekilirse etkilenen model bulunur; satır silmenin modeldeki etkisini giderdiği varsayılmaz. Gerekirse retire/retrain.

## AI araştırma asistanı

AnalysisRun ve izinli kaynak parçalarını okur. Çıktıda açıklama, dayanak kayıtları, belirsizlik, alternatif hipotez ve test önerisi bulunur. Retrieval metinleri talimat değil veridir. Özel reçetenin dış sağlayıcıya aktarımı ayrıca onaylanır; API anahtarı server'da, maliyet sınırı ve AI'sız rapor yolu vardır. ML ve LLM birbirine zorunlu bağımlılık değildir.

Kimyasal similarity M8: önce tek ana chemistry temsili ve sürümlü mesafe; UMF/oxide/ratios aynı bilgiyi üç kez saymayacak. Firing ve atmosphere başlangıçta filtre/ayrı açıklanan bağlam olabilir. 0–100 skor yalnızca belgelenmiş monoton dönüşüm; başarı veya aynı sonuç verme olasılığı değil. Reçete yakınlığı fiziksel sonuç yakınlığıyla ayrı doğrulanır.
