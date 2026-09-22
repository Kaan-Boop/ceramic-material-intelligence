import type { Report } from '../lib/api';
import { numberTR } from '../lib/api';

const labels: Record<string, string> = {
  NO_REPORTED_WINDOW: 'Ürüne ait kaynaklı pişirim aralığı girilmedi.',
  NO_PEAK_TEMPERATURE: 'Hedef tepe sıcaklığı girilmedi.',
  BELOW_REPORTED_WINDOW: 'Bildirilen aralığın altında.',
  ABOVE_REPORTED_WINDOW: 'Bildirilen aralığın üzerinde.',
  WITHIN_REPORTED_WINDOW: 'Bildirilen aralık içinde; uyumluluk garantisi değil.',
};

export default function ProcessReport({ report }: { report: Report['process'] }) {
  return <section className="card" aria-label="Çamur sır pişirim değerlendirmesi">
    <div className="card-heading"><h3>Çamur + sır + pişirim</h3><span className="tag amber">KISMİ DEĞERLENDİRME</span></div>
    <p className="helper">CALCULATED · Bildirilen girdilerin kontrolü; fiziksel sonuç tahmini değil.</p>
    <p><strong>Bünye:</strong> {labels[report.body_window.code] ?? report.body_window.code}</p>
    <p><strong>Sır:</strong> {labels[report.glaze_window.code] ?? report.glaze_window.code}</p>
    <p><strong>Program:</strong> {report.schedule.status === 'UNAVAILABLE' ? 'Program girilmedi; cone değerinden süre türetilmez.' : report.schedule.total_duration_minutes == null ? `Bilinen süre ${numberTR(report.schedule.known_duration_minutes)} dk; doğal soğuma süresi bilinmiyor.` : `Planlanan süre ${numberTR(report.schedule.total_duration_minutes)} dk; gerçekleşmiş süre değil.`}</p>
    {report.stages.map(stage => <details key={stage.id}>
      <summary>{stage.title} · Tahmin mevcut değil</summary>
      <p>{stage.reason}</p>
      <strong>Gerekli kanıtlar</strong>
      <ul>{stage.required_evidence.map(item => <li key={item}>{item}</li>)}</ul>
      <p>{stage.next_step}</p>
    </details>)}
    <details><summary>Kontrolün sınırları ve kaynak izi</summary>
      <ul>{report.warnings.map(w => <li key={w}>{w}</li>)}</ul>
      <p>Motor: {report.engine_version}</p><p className="hash">Girdi SHA-256: {report.input_hash}</p>
    </details>
  </section>;
}
