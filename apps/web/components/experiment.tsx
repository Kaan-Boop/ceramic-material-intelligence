'use client';
import { useEffect, useRef, useState } from 'react';
import {useExperimentSession} from './experiment-session';
import Link from 'next/link';
import { MAX_FILE_BYTES, parseExperimentFile, serializeExperiment, type ExperimentFile } from '../lib/experiment-file';

type Row = { time: string; predicted: string; observed: string };
type Report = { metrics: { bias_C: number; mae_C: number; rmse_C: number; max_absolute_error_C: number }; input_hash: string; point_count: number };
const labels = { body_revision: 'Bünye / analiz sürümü', glaze_revision: 'Sır / reçete sürümü', application_revision: 'Uygulama kaydı', firing_run_id: 'Pişirim kaydı', specimen_id: 'Numune kimliği', sensor_location: 'Sensör konumu' };
type Context = Record<keyof typeof labels, string>;
const emptyContext = Object.fromEntries(Object.keys(labels).map(k => [k, ''])) as Context;
const blank = (): Row => ({ time: '', predicted: '', observed: '' });
const fmt = (n: number) => n.toLocaleString('tr-TR', { maximumFractionDigits: 3 });

export default function Experiment() {
  const {draft,setDraft,archive,setArchive}=useExperimentSession();
  const {context,rows,source,model,kind}=draft;
  const setContext=(value:Context)=>setDraft(d=>({...d,context:value}));
  const setRows=(value:Row[])=>setDraft(d=>({...d,rows:value}));
  const setSource=(value:string)=>setDraft(d=>({...d,source:value}));
  const setModel=(value:string)=>setDraft(d=>({...d,model:value}));
  const setKind=(value:'REAL'|'SYNTHETIC')=>setDraft(d=>({...d,kind:value}));
  const [confirmed, setConfirmed] = useState(false);
  const [report, setReport] = useState<Report | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const revision = useRef(0);
  const rawReport = useRef<unknown>(null);
  useEffect(()=>()=>{revision.current++;fileRequest.current++;},[]);
  const [pendingFile, setPendingFile] = useState<ExperimentFile | null>(null);
  const [fileMessage, setFileMessage] = useState('');
  const fileRequest = useRef(0);
  function saveExperiment() {
    try {
      const raw = serializeExperiment({context,rows,source,model,kind}, archive);
      const url = URL.createObjectURL(new Blob([raw], {type:'application/json'}));
      const a = document.createElement('a'); a.href=url; a.download='ceramic-deney.json'; a.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
      setFileMessage('Dosya indirmesi başlatıldı. Eski dosyanızı silmeden yeni bir kopya saklayın.');
    } catch(e) { setFileMessage(e instanceof Error ? e.message : 'Dosya oluşturulamadı.'); }
  }
  async function openExperiment(file?: File) {
    const request = ++fileRequest.current;
    setPendingFile(null);
    if (!file) return;
    try {
      if (file.size > MAX_FILE_BYTES) throw new Error('Dosya 2 MiB sınırını aşıyor.');
      const parsed = parseExperimentFile(await file.text());
      if (request !== fileRequest.current) return;
      setPendingFile(parsed); setFileMessage('Dosya okunabildi. Mevcut girişler henüz değiştirilmedi.');
    } catch(e) { if (request === fileRequest.current) setFileMessage(e instanceof Error ? e.message : 'Dosya açılamadı.'); }
  }
  function applyFile() {
    if (!pendingFile) return;
    invalidate(); const d = pendingFile.draft;
    setContext(d.context); setRows(d.rows); setSource(d.source); setModel(d.model); setKind(d.kind);
    setArchive(pendingFile.archived_reports); setConfirmed(false); setPendingFile(null);
    setFileMessage('Girdiler açıldı. Arşiv raporları doğrulanmadı; güncel sonuç için yeniden karşılaştırın.');
  }
  function invalidate() { revision.current++; setReport(null); rawReport.current = null; setError(''); }
  function example() {
    invalidate(); setKind('SYNTHETIC'); setConfirmed(false);
    setContext(Object.fromEntries(Object.keys(labels).map(k => [k, 'demo-' + k])) as Context);
    setSource('Sentetik kontrol verisi · v1'); setModel('Sentetik model çıktısı · v1');
    setRows([{ time:'0', predicted:'22', observed:'20' }, { time:'60', predicted:'96', observed:'100' }, { time:'120', predicted:'155', observed:'150' }]);
  }
  async function compare(e: React.FormEvent) {
    e.preventDefault(); setError(''); setReport(null); rawReport.current = null;
    const requestRevision = revision.current;
    try {
      if (!confirmed) throw new Error('Aynı numune ve koşulları karşılaştırdığınızı doğrulayın.');
      const number = (s: string) => { const n = Number(s.trim().replace(',', '.')); if (!s.trim() || !Number.isFinite(n)) throw new Error('Tüm ölçüm hücrelerine geçerli sayı girin.'); return n; };
      const record = (predicted: boolean) => ({ context, source_ref: predicted ? model : source, method_version: predicted ? model : source,
        evidence_kind: predicted ? 'PREDICTED' : 'OBSERVED', data_kind: kind, temperature_basis:'SPECIMEN', unit:'degC',
        samples: rows.map(r => ({ time_s:number(r.time), temperature_c:number(predicted ? r.predicted : r.observed) })) });
      setBusy(true);
      const response = await fetch('/api/v1/validation/temperature', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({prediction:record(true), observation:record(false)}) });
      const result = await response.json();
      if (!response.ok) throw new Error((result.errors?.[0]?.message ?? 'İstek tamamlanamadı') + ' (' + (result.errors?.[0]?.code ?? response.status) + ')');
      if (revision.current === requestRevision) { setReport(result); rawReport.current = result; setArchive(old=>[...old,result]); }
    } catch (e) { if (revision.current === requestRevision) setError(e instanceof Error ? e.message : 'Karşılaştırma tamamlanamadı.'); }
    finally { setBusy(false); }
  }
  function download() {
    if (!rawReport.current) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(rawReport.current, null, 2)], {type:'application/json'}));
    const a = document.createElement('a'); a.href=url; a.download='deney-karsilastirma.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  const values = rows.flatMap(r => [Number(r.predicted.replace(',', '.')), Number(r.observed.replace(',', '.'))]);
  const low = Math.min(...values), range = Math.max(1, Math.max(...values)-low);
  const times = rows.map(r => Number(r.time.replace(',', '.')));
  const timeRange = Math.max(1, times[times.length-1]-times[0]);
  const points = (key:'predicted'|'observed') => rows.map((r,i) => `${40+520*(times[i]-times[0])/timeRange},${190-150*(Number(r[key].replace(',','.'))-low)/range}`).join(' ');
  return <main className="experiment-shell">
    <nav className="experiment-nav" aria-label="Çalışma alanları"><Link href="/">← Laboratuvar masam</Link><span>Deney ve ölçüm</span> · <Link href="/experiments/measurements">Numune kayıtları →</Link></nav>
    <header><p className="eyebrow">CERAMIC GLAZE LAB / DENEY DEFTERİ</p><h1>Deney ve <em>doğrulama</em></h1><p>Modelin söylediği ile numunenin gösterdiğini aynı yerde incele.</p></header>
    <div className="experiment-notice"><strong>Bu ekran simülasyon üretmez.</strong> Mevcut model çıktısı ve numune ölçümlerini karşılaştırır. Fırın programı, numune sıcaklığı değildir. Bu karşılaştırma taslağı sunucuda saklanmaz. Kalıcı ölçüm kayıtları için <Link href="/experiments/measurements">Numune kayıtları</Link> bölümünü kullan.</div>
    <section className="card" aria-label="Deney dosyası">
      <h2>Deney dosyası</h2>
      <p>Taslağı ve {archive.length} arşiv raporunu bilgisayarına kaydet. İndirilen dosya özel deney bilgilerini içerir; şifreli değildir. Taslak uygulama içi sayfa geçişlerinde korunur; sayfayı yenilemek veya kapatmak bellekteki çalışmayı siler. Kalıcı otomatik kayıt yoktur.</p>
      <button type="button" onClick={saveExperiment} disabled={busy}>Deney dosyasını kaydet</button>
      <label className="field">Deney dosyası aç · JSON, en fazla 2 MiB<input type="file" accept=".json,application/json" disabled={busy} onChange={e=>{void openExperiment(e.target.files?.[0]); e.target.value='';}} /></label>
      <p role="status">{fileMessage}</p>
      {pendingFile && <div className="experiment-notice"><p>{pendingFile.draft.rows.length} satır · {pendingFile.draft.kind==='SYNTHETIC' ? 'Sentetik' : 'Gerçek veri beyanı'} · {pendingFile.archived_reports.length} doğrulanmamış arşiv raporu.</p><p>Açmak mevcut taslağı ve rapor arşivini değiştirir. Önce mevcut dosyanı kaydedebilirsin.</p><button type="button" onClick={applyFile} disabled={busy}>Mevcut taslağın yerine aç</button> <button type="button" onClick={()=>setPendingFile(null)}>Vazgeç</button></div>}
    </section>
    <div className="experiment-grid"><form onSubmit={compare} className="card">
      <div className="experiment-heading"><h2>01 / Deney bağlamı</h2><button type="button" onClick={example} disabled={busy}>Sentetik örnek yükle</button></div>
      <label className="field">Veri türü<select value={kind} onChange={e => { invalidate(); setKind(e.target.value as 'REAL'|'SYNTHETIC'); setConfirmed(false); setRows([blank(),blank()]); setContext(emptyContext); setSource(''); setModel(''); }}><option value="REAL">Gerçek deney — kullanıcı beyanı</option><option value="SYNTHETIC">Sentetik — yalnızca yazılım kontrolü</option></select><small>Veri türünü değiştirmek mevcut girişleri temizler.</small></label>
      {kind==='SYNTHETIC' && <p className="experiment-notice">SENTETİK ÖRNEK · Gerçek pişirim veya fiziksel doğrulama değildir.</p>}
      <p>Kimlikler bu prototipte elle girilir; malzeme kataloğuna otomatik bağlanmaz.</p>
      <div className="experiment-fields">{Object.entries(labels).map(([key,label]) => <label className="field" key={key}>{label}<input required maxLength={160} value={context[key as keyof Context]} onChange={e => { invalidate(); setContext({...context,[key]:e.target.value}); }} /></label>)}</div>
      <label className="field">Model çıktısı kaynağı ve sürümü<input required maxLength={500} value={model} onChange={e => { invalidate(); setModel(e.target.value); }} /></label>
      <label className="field">Ölçüm kaynağı / cihaz ve yöntem kaydı<input required maxLength={500} value={source} onChange={e => { invalidate(); setSource(e.target.value); }} /></label>
      <h2>02 / Eşleşen sıcaklıklar</h2><p>Aynı numune ve sensör konumu, artan zaman sırası. Ondalık virgül kullanılabilir.</p>
      <div className="experiment-table"><table><thead><tr><th>Zaman (s)</th><th>Model (°C)</th><th>Ölçüm (°C)</th><th>İşlem</th></tr></thead><tbody>{rows.map((r,i) => <tr key={i}>{(['time','predicted','observed'] as const).map((k,j) => <td key={k}><input aria-label={`${i+1}. satır ${['zaman','model','ölçüm'][j]}`} inputMode="decimal" required value={r[k]} onChange={e => { invalidate(); setRows(rows.map((row,n) => n===i ? {...row,[k]:e.target.value} : row)); }} /></td>)}<td><button type="button" aria-label={`${i+1}. satırı sil`} disabled={rows.length<=1} onClick={() => { invalidate(); setRows(rows.filter((_,n) => n!==i)); }}>×</button></td></tr>)}</tbody></table></div>
      <button type="button" disabled={rows.length>=100} onClick={() => { invalidate(); setRows([...rows,blank()]); }}>+ Ölçüm satırı</button>
      <label className="experiment-check"><input type="checkbox" checked={confirmed} onChange={e => { invalidate(); setConfirmed(e.target.checked); }} />İki seri aynı bağlama aittir; model serisini bu ölçümleri kopyalayarak oluşturmadım. Sentetik örnekte bu yalnızca akış kontrolüdür.</label>
      {error && <p role="alert" className="experiment-error">{error}</p>}
      <button className="experiment-primary" disabled={busy || !confirmed}>{busy ? 'Karşılaştırılıyor…' : 'Model ve ölçümü karşılaştır'}</button>
    </form><aside className="card experiment-results" aria-live="polite">
      <p className="eyebrow">03 / KARŞILAŞTIRMA RAPORU</p><h2>{report ? 'Farkı görünür kıl' : 'Henüz karşılaştırma yok'}</h2>
      {!report ? <p>Deney bilgilerini ve eşleşen sıcaklıkları gir. İlk deneme için sentetik örneği kullanabilirsin.</p> : <>
        <p className="experiment-notice">{kind==='SYNTHETIC' ? 'SENTETİK KONTROL' : 'HESAPLANAN KARŞILAŞTIRMA'} · Başarı onayı değil.</p>
        <svg viewBox="0 0 600 230" role="img" aria-label="Numune sıcaklığı karşılaştırması: yatay eksen saniye, dikey eksen derece Celsius"><path d="M40 25 V190 H565" fill="none" stroke="#aab4aa"/><polyline points={points('predicted')} fill="none" stroke="#244f40" strokeWidth="3"/><polyline points={points('observed')} fill="none" stroke="#94622b" strokeWidth="3" strokeDasharray="7 4"/><text x="40" y="18">{fmt(low+range)} °C</text><text x="40" y="220">{times[0]} s</text><text x="500" y="220">{times[times.length-1]} s</text><text x="2" y="190">{fmt(low)}</text></svg>
        <p>Yeşil düz: model · Kahverengi kesikli: ölçüm. Çizgiler yalnızca noktaları bağlar; ara değer hesabı yok.</p>
        <dl className="experiment-metrics">{([['bias_C','Ortalama sapma'],['mae_C','Ortalama mutlak hata'],['rmse_C','RMSE'],['max_absolute_error_C','En büyük mutlak hata']] as const).map(([key,label]) => <div key={key}><dt>{label}</dt><dd>{fmt(report.metrics[key])} <small>°C</small></dd></div>)}</dl>
        <p>{report.point_count} zaman noktası · 1 numune. Noktalar bağımsız deney sayısı değildir. Pozitif sapma: model ölçümden sıcak.</p>
        <button type="button" onClick={download}>Kaynaklı raporu indir · JSON</button>
        <details><summary>İzlenebilirlik</summary><p className="experiment-hash">{report.input_hash}</p><p>İndirilen rapor girdileri ve motor sürümünü içerir. Belirsizlik ve kabul eşiği henüz değerlendirilmedi.</p></details>
      </>}
      <hr/><h3>Bu deneyin sınırı</h3><p>Henüz reçeteden matlık, renk, tutunma veya çatlama olasılığı hesaplanmıyor. Burada sıcaklık farkını ölçüyoruz; nedeni veya genel doğruluğu otomatik belirlemiyoruz.</p>
      <p>Sayfayı yenilemeden veya kapatmadan deney dosyasını kaydet. Araçlar arasında geçişte girdiler ve arşiv korunur; dönüşte sonuç için yeniden karşılaştırma gerekir.</p>
    </aside></div>
  </main>;
}
