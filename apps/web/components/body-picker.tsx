'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
import {api} from '../lib/api';
import {type LibraryRecord,firingLabel,uses} from '../lib/library';
import CompositionChart from './composition-chart';
type WindowValue={product:string;min:string;max:string;source:string;conditions:string};
export default function BodyPicker({value,onChange}:{value:string;onChange:(name:string,window?:WindowValue)=>void}){
 const [records,setRecords]=useState<LibraryRecord[]>([]),[error,setError]=useState('');
 useEffect(()=>{const c=new AbortController();api<{records:LibraryRecord[]}>('library',{signal:c.signal}).then(r=>setRecords(r.records.filter(r=>r.kind==='CLAY_BODY'&&r.windows.length>0))).catch(e=>{if(!c.signal.aborted)setError(e.message)});return()=>c.abort()},[]);
 const name=(r:LibraryRecord)=>`${r.brand} · ${r.name}`;
 const selected=records.find(r=>name(r)===value);
 return <div className="body-picker"><label className="field">Hazır çamur bünyesi<select value={selected?.id??''} onChange={e=>{const r=records.find(r=>r.id===e.target.value);if(!r){onChange('');return}const w=r.windows.filter(w=>w.stage==='GLAZE');const valid=w.length===1&&w[0].kind!=='POINT_TARGET';onChange(name(r),valid?{product:r.id,min:String(w[0].min_c),max:String(w[0].max_c),source:r.source_url,conditions:'Kaynakta bildirilen sır pişirimi aralığı; atmosfer, ısıtma hızı ve bekleme doğrulanmadı.'}:undefined)}}><option value="">Özel / henüz seçilmedi</option>{records.map(r=><option key={r.id} value={r.id}>{name(r)} · {firingLabel(r)}</option>)}</select></label>
 <label className="field">Çamur bünyesi<input maxLength={160} value={value} placeholder="Ürün / özel numune adı" onChange={e=>onChange(e.target.value)}/></label>
 {error&&<p role="alert">Hazır bünyeler yüklenemedi. Adı elle girebilirsin. {error}</p>}
 {selected&&<div className="body-summary"><strong>{firingLabel(selected)}</strong><p>{selected.note}</p><p>{selected.uses.map(u=>uses[u]??u).join(' · ')}</p>{selected.windows.filter(w=>w.stage==='GLAZE').length>1&&<p>Kaynakta çelişkili aralıklar var; otomatik aralık atanmadı.</p>}<details><summary>Bileşenler ve oksit bilgisi ⓘ</summary><CompositionChart oxides={selected.oxides} basis={selected.basis}/></details><Link href={`/materials/${selected.id}`} target="_blank">Ürün ve analiz kaynağı ↗</Link><p className="helper">Seçim sır kimyasını değiştirmez; uyum tahmini üretmez.</p></div>}
 </div>;
}
