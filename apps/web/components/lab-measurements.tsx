'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { api } from '../lib/api';
import { contextLabels, decimal, labels, measurementDefinitions, statusOptions,
  type ExperimentInput, type ExperimentRecord, type Measurement, type MeasurementEntry } from '../lib/lab-measurements';

const emptyExperiment: ExperimentInput = {
  experiment_id:'', specimen_id:'', source_ref:'', record_kind:'REAL', question:'', notes:'',
  context:{ body_revision:'', glaze_revision:'', application_revision:'', firing_run_id:'' },
};
const emptyReading = { value:'', status:'', source:'', method:'', conditions:'', replicate:'', uncertainty:'', uncertaintyKind:'' };
const uncertaintyOptions = ['STANDARD_UNCERTAINTY','EXPANDED_UNCERTAINTY','REPEAT_SD','INSTRUMENT_RESOLUTION','REPORTED_UNSPECIFIED'] as const;

export default function LabMeasurements() {
  const [draft, setDraft] = useState<ExperimentInput>(emptyExperiment);
  const [record, setRecord] = useState<ExperimentRecord | null>(null);
  const [entries, setEntries] = useState<MeasurementEntry[]>([]);
  const [openId, setOpenId] = useState('');
  const [observable, setObservable] = useState<Measurement['observable']>('firing_linear_shrinkage_pct');
  const [reading, setReading] = useState(emptyReading);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [saved, setSaved] = useState(false);
  const controller = useRef<AbortController | null>(null);
  const definition = measurementDefinitions[observable];

  async function perform(action: (signal: AbortSignal) => Promise<void>) {
    controller.current?.abort();
    const current = new AbortController(); controller.current = current;
    const timeout = setTimeout(() => current.abort(), 20000);
    setBusy(true); setError(''); setNotice('');
    try { await action(current.signal); }
    catch (cause) {
      if (controller.current === current) setError(current.signal.aborted
        ? 'İstek tamamlanamadı. Kayıt oluşmuş olabilir; aynı girdiyi yeniden göndermek kopya oluşturmaz.'
        : cause instanceof Error ? cause.message : 'İşlem tamamlanamadı.');
    } finally {
      clearTimeout(timeout);
      if (controller.current === current) { controller.current = null; setBusy(false); }
    }
  }

  async function load(id: string, signal: AbortSignal) {
    if (!/^[0-9a-f]{64}$/.test(id)) throw new Error('Kayıt kimliği 64 karakter olmalı. Kaydettiğin bağlantıyı veya kimliği kullan.');
    const [stored, measurements] = await Promise.all([
      api<{ record: ExperimentRecord }>(`experiments/${id}`, { signal }),
      api<MeasurementEntry[]>(`experiments/${id}/measurements`, { signal }),
    ]);
    if (signal.aborted) return;
    if (stored.record.record_kind !== 'REAL') throw new Error('Bu bölüm gerçek numune kayıtları içindir.');
    setRecord(stored.record); setEntries(measurements); setOpenId(id);
    setReading({ ...emptyReading, source:stored.record.source_ref }); setSaved(false);
    const url = new URL(window.location.href); url.searchParams.set('record', id);
    window.history.replaceState(null, '', url);
  }

  useEffect(() => {
    const id = new URLSearchParams(window.location.search).get('record');
    if (id) { setOpenId(id); void perform(signal => load(id, signal)); }
    return () => { controller.current?.abort(); controller.current = null; };
    // Initial bookmark restore only. Later loads are explicit user actions.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function editReading(key: keyof typeof emptyReading, value: string) {
    setReading(old => ({ ...old, [key]:value })); setSaved(false); setNotice(''); setError('');
  }

  async function create(event: React.FormEvent) {
    event.preventDefault();
    const payload: ExperimentInput = {
      ...draft, experiment_id:draft.experiment_id.trim(), specimen_id:draft.specimen_id.trim(),
      source_ref:draft.source_ref.trim(), question:draft.question?.trim(),
      context:{
        body_revision:draft.context.body_revision.trim(), glaze_revision:draft.context.glaze_revision.trim(),
        application_revision:draft.context.application_revision.trim(), firing_run_id:draft.context.firing_run_id.trim(),
      },
    };
    if (!payload.experiment_id || !payload.specimen_id || !payload.source_ref) { setError('Deney, numune ve kaynak alanlarını doldur.'); return; }
    await perform(async signal => {
      const result = await api<{ record_id:string }>('experiments', { method:'POST', body:JSON.stringify(payload), signal });
      await load(result.record_id, signal);
      if (!signal.aborted) setNotice('Numune kaydedildi. Şimdi ölçüm veya gözlem ekleyebilirsin.');
    });
  }

  async function save(event: React.FormEvent) {
    event.preventDefault(); if (!record) return;
    let payload: Measurement;
    try {
      if (!statusOptions(observable).includes(reading.status as Measurement['status'])) throw new Error('Gözlemin durumunu seç.');
      if (!reading.source.trim() || !reading.method.trim() || !reading.replicate.trim()) throw new Error('Kaynak, yöntem ve okuma kimliğini doldur.');
      const uncertainty = reading.uncertainty.trim() ? decimal(reading.uncertainty) : null;
      if (uncertainty !== null && !reading.uncertaintyKind) throw new Error('Belirsizlik / cihaz bilgisinin türünü seç.');
      payload = {
        observable, value:definition.unit ? decimal(reading.value) : reading.value,
        unit:definition.unit, status:reading.status as Measurement['status'], specimen_id:record.specimen_id,
        source_ref:reading.source.trim(), method:reading.method.trim(), replicate_id:reading.replicate.trim(),
        uncertainty, uncertainty_kind:uncertainty === null ? null : reading.uncertaintyKind as Measurement['uncertainty_kind'],
        conditions:reading.conditions.trim() ? { notes:reading.conditions.trim() } : {},
      };
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Girdileri kontrol et.'); return; }
    await perform(async signal => {
      const result = await api<MeasurementEntry>(`experiments/${record.record_id}/measurements`, {
        method:'POST', body:JSON.stringify(payload), signal,
      });
      if (signal.aborted) return;
      setEntries(old => old.some(entry => entry.measurement_id === result.measurement_id) ? old : [...old, result]);
      setSaved(true); setNotice(result.status === 'EXISTS' ? 'Bu ölçüm zaten kayıtlı; ikinci kopya oluşturulmadı.' : 'Ölçüm numuneye kaydedildi.');
    });
  }

  function startNew() {
    setRecord(null); setEntries([]); setDraft(emptyExperiment); setReading(emptyReading);
    setSaved(false); setOpenId(''); setError(''); setNotice('');
    const url = new URL(window.location.href); url.searchParams.delete('record'); window.history.replaceState(null, '', url);
  }

  function exportRecord() {
    if (!record) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify({ schema_version:'lab-notebook-export-v1', record, measurements:entries }, null, 2)], { type:'application/json' }));
    const anchor = document.createElement('a'); anchor.href=url; anchor.download=`numune-${record.record_id.slice(0,12)}.json`;
    anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    setNotice('Numune ve ölçümler için JSON indirmesi başlatıldı.');
  }

  return <main className="bench lab-notebook">
    <nav className="notebook-nav" aria-label="Deney bölümleri"><Link href="/experiments">← Deney ve doğrulama</Link><span>Numune kayıtları</span></nav>
    <header className="bench-heading"><div><p className="eyebrow">DENEY DEFTERİ / GÖZLENEN SONUÇLAR</p><h1>Numunenin <em>gösterdiği.</em></h1><p>Küçülmeyi ölç, yüzeyi incele, koşulları kaydet. Her gözlem ait olduğu numuneyle birlikte kalsın.</p></div></header>
    <p className="notebook-note">Kaydettiğin kayıtlar bu yerel sunucuda tutulur. Sayfa yenilemek kayıtları silmez; henüz kaydetmediğin girişler silinir. Yeniden açmak için kayıt bağlantısını sakla.</p>
    <form className="notebook-open" onSubmit={event => { event.preventDefault(); void perform(signal => load(openId.trim(), signal)); }}>
      <label htmlFor="open-record">Kayıt kimliğiyle aç</label><input id="open-record" value={openId} onChange={event => setOpenId(event.target.value)} required maxLength={64} placeholder="Kaydedilmiş numunenin 64 karakterli kimliği" disabled={busy} />
      <button disabled={busy} type="submit">Kaydı aç</button>
    </form>
    <div role="status" className="notebook-status">{busy ? 'İşlem sürüyor…' : notice}</div>
    {error && <p role="alert" className="notebook-error">{error}</p>}
    {!record ? <form className="bench-panel" onSubmit={create} aria-label="Yeni numune">
      <h2>01 / Numuneyi tanımla</h2><p>Gerçek deneyine ait kimlikleri gir. Eksik bünye veya pişirim bilgilerini sonuca bakarak tamamlamıyoruz.</p>
      <fieldset disabled={busy} className="notebook-fields">
        <label className="field">Deney kimliği<input required maxLength={160} value={draft.experiment_id} onChange={e => setDraft(old => ({ ...old, experiment_id:e.target.value }))} /></label>
        <label className="field">Numune kimliği<input required maxLength={200} value={draft.specimen_id} onChange={e => setDraft(old => ({ ...old, specimen_id:e.target.value }))} /></label>
        <label className="field">Deneyin kaynağı<input required maxLength={500} value={draft.source_ref} onChange={e => setDraft(old => ({ ...old, source_ref:e.target.value }))} placeholder="Laboratuvar defteri / belge referansı" /></label>
        <label className="field">Araştırma sorusu · isteğe bağlı<input maxLength={500} value={draft.question ?? ''} onChange={e => setDraft(old => ({ ...old, question:e.target.value }))} /></label>
        {Object.entries(contextLabels).map(([key,label]) => <label className="field" key={key}>{label} · isteğe bağlı<input maxLength={200} value={draft.context?.[key as keyof typeof contextLabels] ?? ''} onChange={e => setDraft(old => ({ ...old, context:{ ...old.context, [key]:e.target.value } }))} /></label>)}
      </fieldset>
      <button className="notebook-primary" disabled={busy}>Numuneyi kaydet</button>
    </form> : <>
      <section className="bench-panel notebook-specimen" aria-label="Kaydedilmiş numune">
        <div className="notebook-title"><div><p className="eyebrow">KAYITLI NUMUNE</p><h2>{record.specimen_id}</h2><p>{record.experiment_id} · {record.source_ref}</p></div><div className="notebook-actions"><button onClick={exportRecord} disabled={busy}>Numune dosyasını indir</button><button onClick={startNew} disabled={busy}>Yeni numune</button></div></div>
        <dl className="notebook-context">{Object.entries(contextLabels).map(([key,label]) => <div key={key}><dt>{label}</dt><dd>{record.context?.[key as keyof typeof contextLabels] || 'Belirtilmedi'}</dd></div>)}</dl>
        {record.missing_context.length > 0 && <p className="notebook-note">{record.missing_context.length} bağlam alanı eksik. Bu kayıt tek başına model karşılaştırması için yeterli sayılmaz.</p>}
        <label className="field">Yeniden açma bağlantısı<input readOnly value={`/experiments/measurements?record=${record.record_id}`} onFocus={e => e.target.select()} /></label>
      </section>
      <div className="notebook-grid">
        <form className="bench-panel" onSubmit={save} aria-label="Ölçüm ekle">
          <h2>02 / Ölçüm veya gözlem ekle</h2>
          <fieldset disabled={busy} className="notebook-fields">
            <label className="field notebook-full">İncelenen özellik<select aria-label="İncelenen özellik" value={observable} onChange={e => { setObservable(e.target.value as Measurement['observable']); setReading(old => ({ ...emptyReading, source:old.source })); setSaved(false); setNotice(''); setError(''); }}>{Object.entries(measurementDefinitions).map(([key,item]) => <option key={key} value={key}>{item.label}</option>)}</select><small id="measurement-hint">{definition.hint}</small></label>
            <label className="field">{definition.unit ? `Ölçüm değeri · ${definition.unit}` : 'Gözlenen özellik'}{definition.options ? <select aria-label="Gözlenen özellik" required value={reading.value} onChange={e => editReading('value', e.target.value)} aria-describedby="measurement-hint"><option value="">Seçin</option>{definition.options.map(option => <option key={option} value={option}>{labels[option]}</option>)}</select> : <input required inputMode="decimal" value={reading.value} onChange={e => editReading('value',e.target.value)} aria-describedby="measurement-hint" />}</label>
            <label className="field">Kayıt niteliği<select aria-label="Kayıt niteliği" required value={reading.status} onChange={e => editReading('status', e.target.value)}><option value="">Seçin</option>{statusOptions(observable).map(status => <option key={status} value={status}>{labels[status]}</option>)}</select></label>
            <label className="field">Okuma / tekrar kimliği<input aria-label="Okuma / tekrar kimliği" aria-describedby="replicate-hint" required maxLength={120} value={reading.replicate} onChange={e => editReading('replicate',e.target.value)} placeholder="Örn. okuma-01" /><small id="replicate-hint">Aynı numunede farklı okumalar için ayrı kimlik kullan.</small></label>
            <label className="field">Ölçümün kaynağı<input required maxLength={500} value={reading.source} onChange={e => editReading('source',e.target.value)} /></label>
            <label className="field notebook-full">Yöntem / cihaz<input required maxLength={500} value={reading.method} onChange={e => editReading('method',e.target.value)} placeholder="Nasıl ve hangi cihazla inceledin?" /></label>
            <label className="field notebook-full">Koşullar / ölçüm notu · isteğe bağlı<textarea maxLength={2000} rows={3} value={reading.conditions} onChange={e => editReading('conditions',e.target.value)} placeholder="Ölçüm tarihi, ham okumalar, eksen, açı, sıcaklık, numune hazırlığı…" /></label>
            {definition.unit && <details className="notebook-full"><summary>Belirsizlik / cihaz bilgisi · isteğe bağlı</summary><div className="notebook-fields">
              <label className="field">Bilgi değeri · {definition.unit}<input inputMode="decimal" value={reading.uncertainty} onChange={e => editReading('uncertainty',e.target.value)} /></label>
              <label className="field">Bilginin türü<select aria-label="Bilginin türü" value={reading.uncertaintyKind} onChange={e => editReading('uncertaintyKind',e.target.value)}><option value="">Seçin</option>{uncertaintyOptions.map(kind => <option key={kind} value={kind}>{labels[kind]}</option>)}</select></label>
            </div><small>Cihaz çözünürlüğü istatistiksel belirsizlik değildir. Genişletilmiş belirsizlik için kapsama katsayısını notlara ekle.</small></details>}
          </fieldset>
          <button className="notebook-primary" disabled={busy || saved}>{saved ? 'Ölçüm kaydedildi' : 'Ölçümü kaydet'}</button>
          <p className="notebook-caption">Girdiler değiştiğinde yeni kayıt oluşur; eski ölçümler korunur.</p>
        </form>
        <section className="bench-panel" aria-label="Kaydedilen ölçümler">
          <div className="notebook-title"><h2>03 / Numune geçmişi</h2><span>{entries.length} kayıt</span></div>
          {entries.length === 0 ? <div className="notebook-empty"><h3>İlk gözleminle başla.</h3><p>Ölçümlerin, kaynakları ve inceleme durumları burada görünecek.</p></div> : <ul className="notebook-readings">{entries.map(entry => {
            const item = entry.measurement.measurement;
            return <li key={entry.measurement_id}>
              <p className="eyebrow">{labels[item.status]} · {item.replicate_id || 'Tekrar kimliği yok'}</p>
              <h3>{measurementDefinitions[item.observable].label}</h3>
              <p className="notebook-value">{typeof item.value === 'number' ? item.value.toLocaleString('tr-TR') : labels[String(item.value)] ?? String(item.value)} {item.unit ?? ''}</p>
              {item.uncertainty != null && <p>{labels[item.uncertainty_kind ?? '']}: {item.uncertainty.toLocaleString('tr-TR')} {item.unit}</p>}
              <p>{item.method}</p><p className="notebook-caption">Kaynak: {item.source_ref}</p>
              <details><summary>Kayıt ayrıntıları</summary><pre>{JSON.stringify({ measurement_id:entry.measurement_id, ...item }, null, 2)}</pre></details>
            </li>;
          })}</ul>}
          <p className="notebook-caption">Bunlar kayıtlı ölçüm ve gözlemlerdir. Henüz tahmin doğruluğu veya fırın sonucu için başarı oranı hesaplanmıyor.</p>
        </section>
      </div>
    </>}
  </main>;
}
