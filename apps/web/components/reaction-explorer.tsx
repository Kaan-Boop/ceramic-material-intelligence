'use client';
import {useEffect,useState} from 'react';
import Link from 'next/link';
type State={conversion:number;CaCO3_g:number;CaO_g:number;CO2_g:number};
type Result={current:State;series:State[];method_version:string;constants_version:string;input_hash:string;source_refs:string[];input_snapshot:{mass_g:number;conversion:number}};
const substances=[{key:'CaCO3_g',name:'Kalan kalsit',formula:'CaCO₃',color:'#244f40',text:'Başlangıçtaki saf kalsiyum karbonatın henüz dönüşmediğini varsaydığımız kısmı.'},{key:'CaO_g',name:'Oluşan kalsiyum oksit',formula:'CaO',color:'#94622b',text:'Bu tek reaksiyonun katı ürünü. Bir sır karışımında daha sonra başka bileşenlerle tepkimeye girebilir; burada bu sonraki adımlar hesaplanmıyor.'},{key:'CO2_g',name:'Üretilen karbondioksit',formula:'CO₂',color:'#65798b',text:'Teorik gaz kütlesi. Gazın hacmi, bünyede tutulması veya iğne deliği oluşturma olasılığı değildir.'}] as const;
const fmt=(v:number)=>v.toLocaleString('tr-TR',{maximumFractionDigits:3});
export default function Explorer(){
 const [mass,setMass]=useState('100'),[extent,setExtent]=useState(50),[data,setData]=useState<Result|null>(null),[error,setError]=useState(''),[selected,setSelected]=useState(0),[loading,setLoading]=useState(false);
 useEffect(()=>{
  const controller=new AbortController();setData(null);setError('');setLoading(true);
  const timer=setTimeout(async()=>{try{
   const m=Number(mass.replace(',','.'));if(!mass.trim()||!Number.isFinite(m)||m<=0)throw new Error('Başlangıç kütlesi pozitif bir sayı olmalı.');
   const r=await fetch('/api/v1/reactions/calcite',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mass_g:m,conversion:extent/100}),signal:controller.signal});
   if(!r.ok)throw new Error('Hesap yapılamadı. Kütle sınırı: 0,000001–1.000.000 g. API bağlantısını kontrol edin.');
   const result=await r.json();if(!controller.signal.aborted)setData(result);
  }catch(e){if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Bağlantı kurulamadı.');}finally{if(!controller.signal.aborted)setLoading(false);}},180);
  return()=>{clearTimeout(timer);controller.abort();};
 },[mass,extent]);
 return <main className="experiment-shell"><nav className="experiment-nav" aria-label="Laboratuvar alanları"><Link href="/">← Laboratuvar masam</Link><span>Kimyasal dönüşüm</span></nav>
 <header><p className="eyebrow">KİMYA / İLK MODEL · KALSİT</p><h1>Madde nereye <em>gidiyor?</em></h1><p>Bir dönüşümü, kütlesini ve bilmediğimiz kısmı birlikte gör.</p></header>
 <div className="experiment-notice"><strong>HESAPLANAN · Varsayımlı kütle dengesi.</strong> Bu bir sıcaklık veya reaksiyon hızı tahmini değil. Dönüşüm oranını sen belirliyorsun.</div>
 <div className="reaction-layout"><section className="card"><h2>01 / Senaryon</h2><label className="field">Saf CaCO₃ başlangıç kütlesi (g)<input aria-label="Başlangıç kütlesi" inputMode="decimal" value={mass} onChange={e=>setMass(e.target.value)}/></label>
 <label className="field">Varsayılan dönüşüm: %{extent}<input aria-label="Varsayılan dönüşüm" type="range" min="0" max="100" value={extent} onChange={e=>setExtent(Number(e.target.value))}/></label><p>Bu sürgü sıcaklık, süre veya olasılık değildir.</p>
 <h3>Neden sıcaklık sürgüsü yok?</h3><p>Dönüşümü sıcaklığa bağlamak için numune özellikleri, süre, CO₂ kısmi basıncı ve uygun kinetik model gerekir. Bunlar doğrulanmadan “şu derecede şu kadar dönüşür” diyemeyiz.</p>
 <details><summary>Gerçek karışımda ne değişir?</summary><p>Saf madde varsayımı; safsızlıkları, mineral yapısını, taşınımı ve başka bileşenlerle tepkimeleri dışarıda bırakır. Reçetenin oksit toplamı, gerçekleşen fazları tek başına belirlemez.</p></details>
 </section><section className="card" aria-live="polite"><p className="eyebrow">02 / REAKSİYON VE MADDE AKIŞI</p><h2 className="reaction-equation">CaCO₃ → CaO + CO₂</h2><p>Bir mol kalsiyum karbonat → bir mol kalsiyum oksit + bir mol karbondioksit.</p>
 {loading&&<p role="status">Kütle dengesi hesaplanıyor…</p>}{error&&<p role="alert">{error}</p>}
 {data&&<><div className="reaction-species">{substances.map((s,i)=><button type="button" key={s.key} aria-pressed={selected===i} onClick={()=>setSelected(i)}><strong>{s.formula}</strong><span>{s.name}</span><b>{fmt(data.current[s.key])} g</b><span>Bilgi ⓘ</span></button>)}</div>
 <div className="experiment-notice"><strong>{substances[selected].name}</strong><p>{substances[selected].text}</p></div>
 <h3>03 / Dönüşüm boyunca kütle</h3><svg viewBox="0 0 640 300" role="img" aria-label="Yatay eksen varsayılan dönüşüm yüzdesi, dikey eksen gram. Kalsit azalırken CaO ve CO2 artar."><path d="M65 30 V245 H610" fill="none" stroke="#b0b8ae"/>{[0,.5,1].map(t=><g key={t}><text x="5" y={249-210*t}>{fmt(data.input_snapshot.mass_g*t)}</text><path d={`M65 ${245-210*t} H610`} stroke="#e2e5da"/></g>)}<text x="10" y="18">Kütle (g)</text>{substances.map((s,i)=><polyline key={s.key} fill="none" stroke={s.color} strokeWidth="3" strokeDasharray={i===1?'8 4':i===2?'2 4':undefined} points={data.series.map(p=>`${65+540*p.conversion},${245-210*p[s.key]/data.input_snapshot.mass_g}`).join(' ')}/>)}<line x1={65+540*data.current.conversion} x2={65+540*data.current.conversion} y1="30" y2="245" stroke="#263c34" strokeDasharray="3 4"/><text x="65" y="267">0</text><text x="330" y="267">50</text><text x="585" y="267">100</text><text x="180" y="292">Varsayılan dönüşüm (%) — sıcaklık değil</text></svg>
 <p>Yeşil düz: CaCO₃ · Kahverengi kesikli: CaO · Mavi noktalı: CO₂. Düşey çizgi seçtiğin senaryoyu gösterir.</p><p><strong>Korunan toplam:</strong> {fmt(data.current.CaCO3_g+data.current.CaO_g+data.current.CO2_g)} g. Gaz kütlesi de toplamın içindedir.</p>
 <details><summary>Kaynaklar, yöntem ve sınırlar</summary><p>{data.method_version} · {data.constants_version}</p><ul>{data.source_refs.map((url,i)=><li key={url}><a href={url} target="_blank" rel="noreferrer">{['NIST: kalsit dönüşümü','Kinetik: sıcaklık, basınç ve tane boyutu','Sürümlü atomik kütle kaynağı'][i]??'Kaynak'}</a></li>)}</ul><p>Kaynak açıklamaları yöntem dayanağıdır; kinetik katsayı veya veri seti bu ekrana aktarılmadı. Deneysel doğrulama yapılmadı.</p><p className="experiment-hash">Girdi izi: {data.input_hash}</p></details></>}
 </section></div><section className="experiment-notice"><h3>Sıradaki katman: ısı ile bağlantı</h3><p>Bu madde hesabını gerçek pişirim eğrisine bağlamak için doğrulanmış sıcaklık–zaman ve dönüşüm verileri gerekiyor. Henüz bağlı değil; renk, tutunma ve kusur yüzdesi üretilmiyor.</p><Link href="/experiments">Ölçüm ve model karşılaştırmasına git →</Link></section></main>;
}
