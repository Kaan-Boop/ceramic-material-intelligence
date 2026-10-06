'use client';

import { useEffect, useState } from 'react';
import { api, type ValidationArchiveResponse } from '../lib/api';
import { OUTCOME_REFERENCE_EVENT, OUTCOME_REFERENCE_STORAGE } from './outcome-assessor';
import { useExperimentSession } from './experiment-session';

type Observable = 'gloss_mean_gu' | 'water_absorption_mass_pct' | 'apparent_open_porosity_volume_pct';
type Observation = {
  observable: Observable;
  value: string;
  unit: 'GU' | '%';
  specimen_id: string;
  source_ref: string;
  method: string;
  status: 'MEASURED' | 'REPORTED';
};
type ValidationReport = {
  status: 'COMPARED' | 'PARTIAL';
  input_hash: string;
  comparisons: Record<string, {
    status: 'AVAILABLE' | 'UNAVAILABLE';
    reason?: string;
    calculated: number | null;
    observed: number | null;
    residual_observed_minus_calculated?: number;
    absolute_error?: number;
    unit: string;
    observation_count: number;
    independent_specimen_count: number;
    observation_statuses?: string[];
  }>;
  warnings: string[];
  limitations: string[];
};

const observableLabels: Record<Observable, string> = {
  gloss_mean_gu: 'Gloss ortalaması',
  water_absorption_mass_pct: 'Su emmesi',
  apparent_open_porosity_volume_pct: 'Görünür açık porozite',
};
const units: Record<Observable, 'GU' | '%'> = {
  gloss_mean_gu: 'GU',
  water_absorption_mass_pct: '%',
  apparent_open_porosity_volume_pct: '%',
};
const emptyObservation = (): Observation => ({
  observable: 'gloss_mean_gu', value: '', unit: 'GU', specimen_id: '', source_ref: '', method: '', status: 'MEASURED',
});
const initialContext = { body_analysis_id: '', glaze_revision_id: '', firing_run_id: '', application_id: '' };
const ANALYSIS_REFERENCE_STORAGE = 'ceramic-lab-analysis-reference-v1';
type LinkedAnalysis = { report_id: string; recipe_name: string; input_hash: string; material_count: number };
type LinkedOutcome = { input_hash: string };
type ExperimentRecordResponse = { status: 'CREATED' | 'EXISTS'; record_id: string; record_sha256: string; record?: Record<string, unknown> };

export default function OutcomeValidation() {
  const { draft, setArchive: setExperimentArchive } = useExperimentSession();
  const [experimentId, setExperimentId] = useState('');
  const [context, setContext] = useState(initialContext);
  const [calculatedText, setCalculatedText] = useState('');
  const [observations, setObservations] = useState<Observation[]>([emptyObservation()]);
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [linkedAnalysis, setLinkedAnalysis] = useState<LinkedAnalysis | null>(null);
  const [archive, setArchive] = useState<ValidationArchiveResponse | null>(null);
  const [experimentRecord, setExperimentRecord] = useState<ExperimentRecordResponse | null>(null);
  const [linkedOutcome, setLinkedOutcome] = useState<LinkedOutcome | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(ANALYSIS_REFERENCE_STORAGE);
      if (!raw) return;
      const envelope = JSON.parse(raw) as { version?: number; report?: { report_id?: string; request?: { recipe_name?: string }; chemistry?: { input_hash?: string }; materials?: unknown[] } };
      const report = envelope.report;
      if (envelope.version !== 1 || !report?.report_id || !report.request?.recipe_name || !report.chemistry?.input_hash) return;
      setLinkedAnalysis({ report_id: report.report_id, recipe_name: report.request.recipe_name, input_hash: report.chemistry.input_hash, material_count: Array.isArray(report.materials) ? report.materials.length : 0 });
      setExperimentId(current => current || `${report.request?.recipe_name}-experiment`);
    } catch {
      localStorage.removeItem(ANALYSIS_REFERENCE_STORAGE);
    }
  }, []);

  useEffect(() => {
    const draftContext = draft.context;
    setContext(current => ({
      ...current,
      body_analysis_id: current.body_analysis_id || draftContext.body_revision,
      glaze_revision_id: current.glaze_revision_id || draftContext.glaze_revision,
      firing_run_id: current.firing_run_id || draftContext.firing_run_id,
      application_id: current.application_id || draftContext.application_revision,
    }));
  }, [draft.context]);

  useEffect(() => {
    function loadOutcomeReference() {
      try {
        const raw = localStorage.getItem(OUTCOME_REFERENCE_STORAGE);
        if (!raw) return;
        const envelope = JSON.parse(raw) as { version?: number; report?: { input_hash?: string; sections?: unknown } };
        if (envelope.version !== 1 || !envelope.report?.input_hash || !envelope.report.sections) return;
        setCalculatedText(JSON.stringify(envelope.report, null, 2));
        setLinkedOutcome({ input_hash: envelope.report.input_hash });
        setReport(null);
      } catch {
        localStorage.removeItem(OUTCOME_REFERENCE_STORAGE);
      }
    }
    loadOutcomeReference();
    window.addEventListener(OUTCOME_REFERENCE_EVENT, loadOutcomeReference);
    return () => window.removeEventListener(OUTCOME_REFERENCE_EVENT, loadOutcomeReference);
  }, []);

  function updateObservation(index: number, patch: Partial<Observation>) {
    setObservations(current => current.map((row, rowIndex) => rowIndex === index ? { ...row, ...patch } : row));
    setReport(null);
  }

  async function submit() {
    setError('');
    setReport(null);
    try {
      if (!experimentId.trim() || Object.values(context).some(value => !value.trim())) throw new Error('Deney kimliği ve dört bağlam alanı birlikte doldurulmalı.');
      const calculatedReport = JSON.parse(calculatedText) as unknown;
      if (!calculatedReport || typeof calculatedReport !== 'object') throw new Error('Hesaplanan rapor geçerli bir JSON nesnesi olmalı.');
      const payload = {
        experiment_id: experimentId.trim(),
        context: { ...context, analysis_report_id: linkedAnalysis?.report_id, chemistry_input_hash: linkedAnalysis?.input_hash },
        calculated_report: calculatedReport,
        observations: observations.map(row => ({ ...row, value: Number(row.value.replace(',', '.')), unit: units[row.observable] })),
      };
      if (payload.observations.some(row => !Number.isFinite(row.value))) throw new Error('Gözlem değerleri sayısal olmalı.');
      setBusy(true);
      const result = await api<ValidationReport>('validation/outcomes', { method: 'POST', body: JSON.stringify(payload) });
      setReport(result);
      setArchive(null);
    } catch (cause) {
      if (cause instanceof SyntaxError) setError('Hesaplanan rapor JSON olarak okunamadı.');
      else setError(cause instanceof Error ? cause.message : 'Gözlemler karşılaştırılamadı.');
    } finally {
      setBusy(false);
    }
  }

  async function archiveReport() {
    if (!report) return;
    setError('');
    try {
      const result = await api<ValidationArchiveResponse>('validation/runs', { method: 'POST', body: JSON.stringify({ report }) });
      setArchive(result);
      setExperimentArchive(current => current.some(entry => {
        if (!entry || typeof entry !== 'object') return false;
        const candidate = entry as { report?: { input_hash?: unknown } };
        return candidate.report?.input_hash === report.input_hash;
      }) ? current : [...current, { archive_kind: 'OUTCOME_VALIDATION', saved_at: new Date().toISOString(), report }]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Deney raporu arşivlenemedi.');
    }
  }

  async function createExperimentRecord() {
    if (!report) return;
    setError('');
    try {
      const specimen = observations.find(row => row.specimen_id.trim() && row.source_ref.trim());
      if (!specimen) throw new Error('API deney kaydı için en az bir numune kimliği ve kaynak/yöntem gerekir.');
      const result = await api<ExperimentRecordResponse>('experiments', {
        method: 'POST',
        body: JSON.stringify({
          experiment_id: experimentId.trim(),
          specimen_id: specimen.specimen_id.trim(),
          record_kind: draft.kind,
          source_ref: specimen.source_ref.trim(),
          context: {
            body_revision: context.body_analysis_id,
            glaze_revision: context.glaze_revision_id,
            application_revision: context.application_id,
            firing_run_id: context.firing_run_id,
          },
          analysis_report_id: linkedAnalysis?.report_id,
          chemistry_input_hash: linkedAnalysis?.input_hash,
          notes: 'OutcomeValidation panelinden oluşturuldu; gözlem ve hesap raporu ayrı tutulur.',
        }),
      });
      setExperimentRecord(result);
      if (result.record) setExperimentArchive(current => current.some(entry => {
        if (!entry || typeof entry !== 'object') return false;
        const candidate = entry as { record_id?: unknown };
        return candidate.record_id === result.record_id;
      }) ? current : [...current, result.record]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Deney kaydı API’ye yazılamadı.');
    }
  }

  return <section className="card outcome-panel" aria-label="Gözlenen sonuç doğrulaması">
    <div className="experiment-heading"><div><p className="eyebrow">04 / GÖZLENEN SONUÇLAR</p><h2>Hesap ile numuneyi bağla</h2></div><span className="tag">OBSERVED ↔ CALCULATED</span></div>
    <p className="experiment-notice"><strong>Bu panel tahmin üretmez.</strong> Daha önce üretilmiş hesap raporundaki ölçülebilir bölümleri fiziksel numune gözlemleriyle karşılaştırır. Sonuç kabul, güvenlik veya genelleme onayı değildir.</p>
    {linkedAnalysis && <div className="experiment-notice outcome-linked"><strong>CALCULATED kimya snapshot’ı bağlandı.</strong><p>{linkedAnalysis.recipe_name} · {linkedAnalysis.material_count} malzeme · {linkedAnalysis.input_hash.slice(0, 16)}…</p><p>Bu snapshot reçete kimyasını taşır; gloss, su emmesi veya porozite sonucu içermez. Outcome karşılaştırması için ayrıca hesaplanmış `sections` raporu gerekir.</p><button type="button" onClick={() => { localStorage.removeItem(ANALYSIS_REFERENCE_STORAGE); setLinkedAnalysis(null); }}>Bağlantıyı kaldır</button></div>}
    {linkedOutcome && <div className="experiment-notice outcome-linked"><strong>CALCULATED ölçüm özeti bağlandı.</strong><p>{linkedOutcome.input_hash.slice(0, 16)}… · JSON alanı dolduruldu.</p><p>Bu raporun hesaplanan tarafıdır. Aynı okumaları gözlenen tarafa kopyalamayın; bağımsız numune ölçümü girin.</p><button type="button" onClick={() => { localStorage.removeItem(OUTCOME_REFERENCE_STORAGE); setLinkedOutcome(null); setCalculatedText(''); setReport(null); }}>Bağlantıyı kaldır</button></div>}
    <div className="experiment-fields">
      <label className="field">Deney kimliği<input value={experimentId} maxLength={160} onChange={event => { setExperimentId(event.target.value); setReport(null); }} placeholder="Örn. cone6-white-stoneware-01" /></label>
      {Object.entries(context).map(([key, value]) => <label className="field" key={key}>{({ body_analysis_id: 'Bünye analiz sürümü', glaze_revision_id: 'Sır reçete sürümü', firing_run_id: 'Pişirim kaydı', application_id: 'Uygulama kaydı' } as Record<string, string>)[key]}<input value={value} maxLength={200} onChange={event => { setContext(current => ({ ...current, [key]: event.target.value })); setReport(null); }} /></label>)}
    </div>
    <label className="field">Hesaplanan rapor JSON'u<textarea className="outcome-json" value={calculatedText} onChange={event => { setCalculatedText(event.target.value); setLinkedOutcome(null); setReport(null); }} placeholder={'Ölçüm özetini üst panelden aktarın…'} rows={6} /></label>
    <p className="helper">Üst panelden aktarılan raporun `sections` alanı burada snapshot olarak kullanılır. Deney ekranındaki bünye, sır, pişirim ve uygulama kimlikleri boşsa elle tamamlayın.</p>
    <div className="outcome-observations"><div className="experiment-heading"><h3>Numune gözlemleri</h3><button type="button" onClick={() => setObservations(current => [...current, emptyObservation()])} disabled={observations.length >= 100 || busy}>+ Gözlem</button></div>
      {observations.map((row, index) => <div className="outcome-row" key={index}>
        <label className="field">Ölçüm<select value={row.observable} onChange={event => updateObservation(index, { observable: event.target.value as Observable, unit: units[event.target.value as Observable] })}>{Object.entries(observableLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></label>
        <label className="field">Değer · {units[row.observable]}<input inputMode="decimal" value={row.value} onChange={event => updateObservation(index, { value: event.target.value })} /></label>
        <label className="field">Numune kimliği<input value={row.specimen_id} onChange={event => updateObservation(index, { specimen_id: event.target.value })} /></label>
        <label className="field">Durum<select value={row.status} onChange={event => updateObservation(index, { status: event.target.value as Observation['status'] })}><option value="MEASURED">MEASURED · ölçüldü</option><option value="REPORTED">REPORTED · bildirildi</option></select></label>
        <label className="field">Kaynak / yöntem<input value={row.source_ref} placeholder="lab defteri veya cihaz" onChange={event => updateObservation(index, { source_ref: event.target.value })} /></label>
        <label className="field">Metot<input value={row.method} placeholder="Örn. ASTM C373 uyumlu prosedür" onChange={event => updateObservation(index, { method: event.target.value })} /></label>
        {observations.length > 1 && <button type="button" className="text-button outcome-remove" onClick={() => setObservations(current => current.filter((_, rowIndex) => rowIndex !== index))}>Satırı kaldır</button>}
      </div>)}
    </div>
    {error && <p className="experiment-error" role="alert">{error}</p>}
    <button className="experiment-primary" type="button" onClick={() => void submit()} disabled={busy}>{busy ? 'Karşılaştırılıyor…' : 'Gözlemleri karşılaştır'}</button>
    {report && <div className="outcome-results" role="status"><div className="experiment-heading"><h3>Karşılaştırma · {report.status}</h3><code>{report.input_hash.slice(0, 16)}…</code></div><div className="outcome-result-grid">{Object.entries(report.comparisons).map(([key, comparison]) => <article className={`outcome-result ${comparison.status.toLowerCase()}`} key={key}><span className="tag">{comparison.status === 'AVAILABLE' ? 'CALCULATED ↔ OBSERVED' : 'UNAVAILABLE'}</span><h4>{observableLabels[key as Observable] ?? key}</h4>{comparison.status === 'AVAILABLE' ? <><strong>{comparison.residual_observed_minus_calculated?.toLocaleString('tr-TR', { maximumFractionDigits: 3 })} {comparison.unit}</strong><p>Hesaplanan: {comparison.calculated?.toLocaleString('tr-TR', { maximumFractionDigits: 3 })} · Gözlenen: {comparison.observed?.toLocaleString('tr-TR', { maximumFractionDigits: 3 })}</p><small>{comparison.observation_count} kayıt · {comparison.independent_specimen_count} bağımsız numune</small></> : <p>{comparison.reason}</p>}</article>)}</div>{report.warnings.map(warning => <p className="helper" key={warning}>{warning}</p>)}<div className="simulation-actions"><button type="button" onClick={() => void archiveReport()}>Deney raporunu yerel arşive kaydet</button><button type="button" onClick={() => void createExperimentRecord()}>Deney kaydını API’ye yaz</button>{archive && <span className="helper">Arşiv: {archive.status} · {archive.run_id.slice(0, 16)}…</span>}{experimentRecord && <span className="helper">API: {experimentRecord.status} · {experimentRecord.record_id.slice(0, 16)}…</span>}</div><details><summary>Sınırlamalar</summary><ul>{report.limitations.map(limitation => <li key={limitation}>{limitation}</li>)}</ul></details></div>}
  </section>;
}
