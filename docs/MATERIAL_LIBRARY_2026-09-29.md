# Kaynaklı malzeme kütüphanesi

## Ön inceleme ve teyit edilmiş iş akışı
Mevcut Next/React/CSS korunur. Yeni kütüphane bağımlılığı gerekmedi. Sıra: yerel veri/hak incelemesi → salt okunur katalog projeksiyonu → arama/filtre/sayfalama → kayıt sayfası/grafik → kaynaklı bünye seçimi → veri/API/TypeScript/tarayıcı testleri. Kullanılan beceriler: redesign-existing-projects, tarayici; agent-reach yönlendirmesi incelendi, mcporter bulunamadığından resmî sayfalar web aracıyla kontrol edildi.

## Kapsam
185 kayıt: 4 teorik hesap girdisi, 166 ticari kimlik kaydı, 15 CC-BY-4.0 çalışma numunesi. Bu sayı onaylı analiz sayısı değildir. Sadece mevcut dört teorik analiz motor girdisidir. Ticari kayıtlar özgün sayfa/fotoğraf kopyası değil mevcut sınırlı yerel bibliyografik dizinin gösterimidir. UNKNOWN_REUSE_RIGHTS kayıtları yayın/eğitim izni kazanmaz. Açık lisanslı akademik analizlerin bilinmeyen baz ve diğer kalite engelleri korunur.

Yerel /api/v1/library endpoint'i; /materials ve /materials/[id] sayfaları. Mevcut analiz sayfasındaki kütüphane sekmesi aynı bileşeni kullanır. Filtre: tür, ad/marka, aramalı oksit listesi; seçili oksitlerin tümü pozitif raporlanmış olmalıdır. Eksik analiz yokluk sayılmaz. Sayfa boyutu 12. Alfabetik ve seçili oksit yüzdesine göre sıralama; farklı bazların bilimsel eşdeğerliğini iddia etmez.

Bileşim grafiği: raporlanan/teorik wt%, normalize edilmez; LOI ayrı. Oksit dışı S/Cl grafiğe alınmaz, özgün kayıtlarda korunur. Pişmiş faz dağılımı değildir. SiO2 ve Al2O3 kısa açıklamaları kaynak bağlantılı özgün özetlerdir; evrensel pişirim sıcaklığı verilmez.

10 kaynaklı bünye seçeneği: kayıt adı ve bildirilen aralık. Aynı marka + tam katalog anahtarı veya tam URL ile birleştirme; fuzzy eşleştirme yok. Birden fazla sır pişirim aralığı varsa otomatik atama yok; nokta hedefi çalışma aralığı yapılmaz. Özel isim girilince eski otomatik bünye aralığı temizlenir. Seçim sırın oksit hesabını değiştirmez.

## Kaynak kontrolü
- https://www.akasyaseramik.com/urunler/stoneware-vakum-camuru — 29 Eylül 2026 kontrolü: 1190–1220 °C sır pişirimi; tam kimya yok.
- https://www.refsan.com.tr/656-seramik-camuru-vakumlu — ürün kimliği ve 1040–1060 °C aralığı kontrolü.
- https://digitalfire.com/oxide/sio2 ve https://digitalfire.com/oxide/al2o3 — kısa teknik açıklama dayanakları, veri seti aktarımı değil.

## Ertelenen
Tüm araştırma havuzunu üretim verisi olarak yayınlama, kabul edilmemiş analizle hesap, kapalı ticari sır formülleri, doğrulanmamış tarihçe, tam oksit etki ansiklopedisi, yeni fizik modeli. Tarihçe yalnızca kanıt bulunduğunda eklenecek. Kütüphane filtre durumu navigasyon sonrası kalıcı değildir.
