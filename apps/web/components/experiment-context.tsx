'use client';
import {useExperimentSession} from './experiment-session';
const fields = {specimen_id:'Numune kimliği',body_revision:'Bünye / analiz sürümü',glaze_revision:'Sır / reçete sürümü',application_revision:'Uygulama kaydı',firing_run_id:'Pişirim kaydı',sensor_location:'Sensör konumu'};
export default function ExperimentContext(){
 const {draft,setDraft,archive}=useExperimentSession();
 const count=Object.values(draft.context).filter(v=>v.trim()).length;
 return <section className="bench-panel" aria-label="Ortak deney bağlamı">
  <h2>Üzerinde çalıştığın numune</h2>
  <p>{draft.kind==='SYNTHETIC'?'Sentetik çalışma — gerçek deney değildir.':'Gerçek deney — kullanıcı beyanı.'} {count}/6 kimlik alanı dolu; bu bir doğruluk puanı değildir.</p>
  <p>Bu alanlar deney defteriyle ortaktır. Reçete hesaplayıcısına veya kataloğa otomatik bağlantı kurulmaz.</p>
  <details><summary>Deney kimliklerini düzenle</summary>
   {Object.entries(fields).map(([key,label])=><label className="field" key={key}>{label}<input maxLength={160} value={draft.context[key as keyof typeof fields]} onChange={e=>{const value=e.target.value;setDraft(d=>({...d,context:{...d.context,[key]:value}}));}} /></label>)}
  </details>
  <p>{archive.length} arşiv raporu · Kimlikleri değiştirmek eski raporların girdilerini değiştirmez. Deney defterinde yeniden karşılaştır.</p>
  <small>Yalnızca bu açık oturumda korunur. Yenilemeden veya kapatmadan deney dosyanı indir.</small>
 </section>;
}
