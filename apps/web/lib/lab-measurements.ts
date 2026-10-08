import type { components } from './api-schema';

export type Measurement = components['schemas']['LabMeasurementRequest'];
export type MeasurementEntry = components['schemas']['LabMeasurementArchiveResponse'];
export type ExperimentInput = components['schemas']['ExperimentRecordRequest'] & {
  context: components['schemas']['ExperimentRecordContext'];
};
export type ExperimentRecord = ExperimentInput & { record_id: string; missing_context: string[] };

type Definition = { label: string; unit: string | null; hint: string; options?: string[] };
export const measurementDefinitions: Record<Measurement['observable'], Definition> = {
  drying_linear_shrinkage_pct: { label: 'Kuruma küçülmesi', unit: '%', hint: 'Islak başlangıç boyuna göre kuru boydaki değişim. Ölçüm eksenini ve kurutma koşullarını kaydet.' },
  firing_linear_shrinkage_pct: { label: 'Pişme küçülmesi', unit: '%', hint: 'Kuru başlangıç boyuna göre pişmiş boydaki değişim. Negatif değer büyümeyi ifade eder.' },
  glaze_runout_distance_mm: { label: 'Sır akma mesafesi', unit: 'mm', hint: 'Başlangıç çizgisinden pişmiş sır sınırına ölçülen mesafe. Numunenin eğimini ve referans çizgisini belirt.' },
  water_absorption_mass_pct: { label: 'Su emme', unit: '%', hint: 'Kütlece yüzde. Numunenin sırlı/sırsız oluşunu ve doyurma yöntemini belirt.' },
  gloss_mean_gu: { label: 'Parlaklık ölçümü', unit: 'GU', hint: 'Cihaz okumalarının ortalaması. Ölçüm açısını, cihazı ve tekrar sayısını belirt.' },
  glaze_surface_class: { label: 'Yüzey görünümü', unit: null, hint: 'Görsel değerlendirme. Parlaklık ve kristal gibi birlikte bulunan özellikler ayrı kaydedilebilir.', options: ['GLOSSY','SEMI_GLOSS','SATIN','MATTE','DRY_MATTE','CRYSTALLINE','TEXTURED','CRAWLED','METALLIC','LUSTER','OTHER'] },
  optical_transmission_class: { label: 'Optik geçirgenlik', unit: null, hint: 'Gözlenen saydamlık; ölçüm cihazıyla belirlenmiş geçirgenlik yüzdesi değildir.', options: ['TRANSPARENT','TRANSLUCENT','OPAQUE','OTHER'] },
  glaze_adhesion_assessment: { label: 'Tutunma gözlemi', unit: null, hint: 'Uygulanan inceleme veya testi belirt. Bu gözlem sayısal bağ dayanımı vermez.', options: ['ADHERED','PARTIAL_PEELING','PEELED','OTHER'] },
  defect_observation: { label: 'Kusur incelemesi', unit: null, hint: 'Yalnızca seçtiğin kusur için değerlendirme kaydet. İncelenmeyen kusuru yok olarak işaretleme.', options: ['CRAZING','SHIVERING','CRAWLING','PINHOLING','BLISTERING','BLOATING','DUNTING','CRATERING','RUNNING','CLOUDING','DEVITRIFICATION','SETTLING','WARPING','BLACK_CORE','CRACKING','PEELING','OTHER'] },
};

export const labels: Record<string, string> = {
  GLOSSY:'Parlak', SEMI_GLOSS:'Yarı parlak', SATIN:'Saten', MATTE:'Mat', DRY_MATTE:'Kuru mat',
  CRYSTALLINE:'Kristalli', TEXTURED:'Dokulu', CRAWLED:'Toplanmış yüzey', METALLIC:'Metalik', LUSTER:'Lüster',
  TRANSPARENT:'Saydam', TRANSLUCENT:'Yarı saydam', OPAQUE:'Opak', OTHER:'Diğer',
  ADHERED:'Tutunmuş görünüyor', PARTIAL_PEELING:'Kısmen soyulmuş', PEELED:'Soyulmuş',
  CRAZING:'Sır çatlağı (crazing)', SHIVERING:'Sır atması (shivering)', CRAWLING:'Sır toplanması',
  PINHOLING:'İğne deliği', BLISTERING:'Kabarcıklanma', BLOATING:'Bünye şişmesi', DUNTING:'Isıl çatlama',
  CRATERING:'Krater', RUNNING:'Sır akması', CLOUDING:'Bulanıklık', DEVITRIFICATION:'Devitrifikasyon',
  SETTLING:'Çökelme', WARPING:'Eğilme / çarpılma', BLACK_CORE:'Siyah çekirdek', CRACKING:'Çatlama', PEELING:'Soyulma',
  MEASURED:'Ölçtüm', REPORTED:'Kaynakta raporlanmış', OBSERVED:'Gözlemledim',
  OBSERVED_PRESENT:'Gözlendi', OBSERVED_ABSENT:'İncelendi, görülmedi', NOT_ASSESSED:'Değerlendirilmedi',
  REPORTED_PRESENT:'Kaynakta var', REPORTED_ABSENT:'Kaynakta yok',
  STANDARD_UNCERTAINTY:'Standart belirsizlik', EXPANDED_UNCERTAINTY:'Genişletilmiş belirsizlik',
  REPEAT_SD:'Tekrarların standart sapması', INSTRUMENT_RESOLUTION:'Cihaz çözünürlüğü', REPORTED_UNSPECIFIED:'Kaynakta türü belirtilmemiş',
};

export const contextLabels = {
  body_revision:'Bünye / analiz sürümü', glaze_revision:'Sır / reçete sürümü',
  application_revision:'Uygulama kaydı', firing_run_id:'Pişirim kaydı',
};

export function statusOptions(observable: Measurement['observable']): Measurement['status'][] {
  if (observable === 'defect_observation') return ['OBSERVED_PRESENT','OBSERVED_ABSENT','NOT_ASSESSED','REPORTED_PRESENT','REPORTED_ABSENT'];
  return measurementDefinitions[observable].unit ? ['MEASURED','REPORTED'] : ['OBSERVED','REPORTED'];
}

export function decimal(value: string): number {
  const text = value.trim().replace(',', '.');
  if (!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(text) || !Number.isFinite(Number(text))) {
    throw new Error('Değer için geçerli bir sayı gir. Ondalık ayırıcı olarak virgül veya nokta kullanabilirsin.');
  }
  return Number(text);
}
