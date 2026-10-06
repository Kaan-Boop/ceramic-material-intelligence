'use client';

import { useState } from 'react';
import { api } from '../lib/api';
import { useExperimentSession } from './experiment-session';

type Mode = 'porosity' | 'gloss';
type AssessReport = {
  engine_version: string;
  input_hash: string;
  sections: Record<string, { status: string; evidence_kind: string; method_kind: string; values?: Record<string, number | string | null>; limitations?: string[] }>;
  notice: string;
};

export const OUTCOME_REFERENCE_STORAGE = 'ceramic-lab-outcome-reference-v1';
export const OUTCOME_REFERENCE_EVENT = 'ceramic-lab-outcome-reference-updated';

const initial = { source_ref: '', conditions: '', input_kind: 'MEASURED' as 'MEASURED' | 'REPORTED' | 'SYNTHETIC' };

export default function OutcomeAssessor() {
  const { setArchive } = useExperimentSession();
  const [mode, setMode] = useState<Mode>('porosity');
  const [common, setCommon] = useState(initial);
  const [porosity, setPorosity] = useState({ dry_mass_g: '', saturated_mass_g: '', suspended_mass_g: '', specimen_scope: 'UNGLAZED_BODY' });
  const [gloss, setGloss] = useState({ angle_deg: '60', readings_gu: '', instrument_id: '' });
  const [report, setReport] = useState<AssessReport | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function assess() {
    setError('');
    setReport(null);
    try {
      if (!common.source_ref.trim() || !common.conditions.trim()) throw new Error('Kaynak ve koşul açıklaması gerekli.');
      const number = (value: string) => {
        const parsed = Number(value.replace(',', '.'));
        if (!value.trim() || !Number.isFinite(parsed)) throw new Error('Tüm sayısal alanlar geçerli olmalı.');
        return parsed;
      };
      const section = mode === 'porosity'
        ? { ...porosity, dry_mass_g: number(porosity.dry_mass_g), saturated_mass_g: number(porosity.saturated_mass_g), suspended_mass_g: number(porosity.suspended_mass_g), source_ref: common.source_ref.trim(), conditions: common.conditions.trim(), input_kind: common.input_kind }
        : { ...gloss, angle_deg: number(gloss.angle_deg), readings_gu: gloss.readings_gu.split(/[,;\s]+/).filter(Boolean).map(number), source_ref: common.source_ref.trim(), conditions: common.conditions.trim(), input_kind: common.input_kind };
      setBusy(true);
      const result = await api<AssessReport>('outcomes/assess', { method: 'POST', body: JSON.stringify({ [mode]: section }) });
      setReport(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Ölçüm özeti hesaplanamadı.');
    } finally {
      setBusy(false);
    }
  }

  function linkForValidation() {
    if (!report) return;
    localStorage.setItem(OUTCOME_REFERENCE_STORAGE, JSON.stringify({ version: 1, report }));
    setArchive(current => current.some(entry => {
      if (!entry || typeof entry !== 'object') return false;
      const candidate = entry as { report?: { input_hash?: unknown } };
      return candidate.report?.input_hash === report.input_hash;
    }) ? current : [...current, { archive_kind: 'OUTCOME_ASSESSMENT', saved_at: new Date().toISOString(), report }]);
    window.dispatchEvent(new Event(OUTCOME_REFERENCE_EVENT));
  }

  return <section className="card outcome-assessor" aria-label="Ölçüm özeti hesaplayıcı">
    <div className="experiment-heading"><div><p className="eyebrow">03 / ÖLÇÜM ÖZETİ</p><h2>Numune ölçümünü hesapla</h2></div><span className="tag">CALCULATED</span></div>
    <p className="experiment-notice"><strong>Bu bir ölçüm özeti motorudur.</strong> Verilen tartım veya cihaz okumalarından türetilmiş değer çıkarır; reçeteden gloss/porozite tahmini yapmaz.</p>
    <div className="assessor-tabs"><button type="button" className={mode === 'porosity' ? 'active' : ''} onClick={() => { setMode('porosity'); setReport(null); }}>Porozite / su emmesi</button><button type="button" className={mode === 'gloss' ? 'active' : ''} onClick={() => { setMode('gloss'); setReport(null); }}>Gloss okumaları</button></div>
    <div className="experiment-fields"><label className="field">Kaynak / cihaz kaydı<input value={common.source_ref} onChange={event => setCommon(current => ({ ...current, source_ref: event.target.value }))} placeholder="lab defteri, cihaz ID veya belge" /></label><label className="field">Koşullar<input value={common.conditions} onChange={event => setCommon(current => ({ ...current, conditions: event.target.value }))} placeholder="saturasyon, açı, sıcaklık vb." /></label><label className="field">Veri niteliği<select value={common.input_kind} onChange={event => setCommon(current => ({ ...current, input_kind: event.target.value as typeof common.input_kind }))}><option value="MEASURED">MEASURED</option><option value="REPORTED">REPORTED</option><option value="SYNTHETIC">SYNTHETIC</option></select></label></div>
    {mode === 'porosity' ? <div className="experiment-fields"><label className="field">Kuru kütle · g<input inputMode="decimal" value={porosity.dry_mass_g} onChange={event => setPorosity(current => ({ ...current, dry_mass_g: event.target.value }))} /></label><label className="field">Doymuş kütle · g<input inputMode="decimal" value={porosity.saturated_mass_g} onChange={event => setPorosity(current => ({ ...current, saturated_mass_g: event.target.value }))} /></label><label className="field">Askıda kütle · g<input inputMode="decimal" value={porosity.suspended_mass_g} onChange={event => setPorosity(current => ({ ...current, suspended_mass_g: event.target.value }))} /></label><label className="field">Numune kapsamı<select value={porosity.specimen_scope} onChange={event => setPorosity(current => ({ ...current, specimen_scope: event.target.value }))}><option value="UNGLAZED_BODY">UNGLAZED_BODY</option><option value="WHOLE_GLAZED_SPECIMEN">WHOLE_GLAZED_SPECIMEN</option></select></label></div> : <div className="experiment-fields"><label className="field">Geometri · derece<input inputMode="numeric" value={gloss.angle_deg} onChange={event => setGloss(current => ({ ...current, angle_deg: event.target.value }))} /></label><label className="field">Cihaz kimliği<input value={gloss.instrument_id} onChange={event => setGloss(current => ({ ...current, instrument_id: event.target.value }))} /></label><label className="field">Gloss okumaları · GU<input value={gloss.readings_gu} onChange={event => setGloss(current => ({ ...current, readings_gu: event.target.value }))} placeholder="Örn. 42, 45, 43" /></label></div>}
    {error && <p className="experiment-error" role="alert">{error}</p>}
    <button className="experiment-primary" type="button" onClick={() => void assess()} disabled={busy}>{busy ? 'Hesaplanıyor…' : 'Ölçüm özetini hesapla'}</button>
    {report && <div className="assessor-result" role="status"><div className="experiment-heading"><h3>{mode === 'porosity' ? 'Porozite sonucu' : 'Gloss sonucu'}</h3><code>{report.input_hash.slice(0, 16)}…</code></div>{Object.entries(report.sections).map(([key, section]) => <div className="assessor-section" key={key}><span className="tag">{section.evidence_kind} · {section.method_kind}</span><h4>{key}</h4>{section.values && Object.entries(section.values).map(([valueKey, value]) => <p key={valueKey}><strong>{valueKey}</strong>: {typeof value === 'number' ? value.toLocaleString('tr-TR', { maximumFractionDigits: 3 }) : value ?? '—'}</p>)}{section.limitations?.slice(0, 2).map(limitation => <small key={limitation}>{limitation}</small>)}</div>)}<p className="helper">{report.notice}</p><div className="simulation-actions"><button type="button" onClick={linkForValidation}>Doğrulama paneline aktar</button><span className="helper">Bu yalnızca hesap snapshot’ını taşır; bağımsız numune ölçümünü ayrıca girin.</span></div></div>}
  </section>;
}
