import {chemicalNames} from '../lib/library';
const notes:Record<string,{text:string;url:string}>={
 SiO2:{text:'Silikat sırlarında temel cam ağı oluşturucudur. Kuvarstaki silika ile feldspat yapısındaki silikanın çözünme davranışı aynı değildir.',url:'https://digitalfire.com/oxide/sio2'},
 Al2O3:{text:'Sır eriyiğinin yapısını ve akış davranışını etkiler. Yüzde veya SiO₂/Al₂O₃ oranı tek başına matlık/parlaklık sonucu vermez.',url:'https://digitalfire.com/oxide/al2o3'},
};
export default function CompositionChart({oxides,basis}:{oxides:Record<string,number>;basis:string}){
 const entries=Object.entries(oxides).sort((a,b)=>b[1]-a[1]);
 if(!entries.length)return <p className="helper">Oksit yüzdeleri bulunmuyor. Grafik üretmek için değer uydurulmaz; bilinmeyen bileşen sıfır değildir.</p>;
 return <div className="composition-chart"><p className="helper">Ağırlıkça % · {basis==='UNKNOWN'?'Analiz bazı bilinmiyor; karşılaştırma sınırlı':basis==='DRY'?'Kuru baz':basis}. Değerler %100’e yeniden normalize edilmedi. LOI ayrı gösterilir.</p>
 {entries.map(([o,v])=><div className="composition-row" key={o}><details><summary aria-label={`${o} hakkında bilgi`}>{o} ⓘ</summary><p>{chemicalNames[o]??o}. Bu değer oksit cinsinden bileşim gösterimidir; numunede aynı oranda serbest oksit fazı bulunduğu anlamına gelmez. Tek başına renk, erime veya pişirim sıcaklığı belirlemez.</p>{notes[o]&&<p>{notes[o].text} <a href={notes[o].url} target="_blank" rel="noreferrer">Teknik kaynak ↗</a></p>}</details><meter min={0} max={100} value={v} aria-label={`${o} ağırlık yüzdesi`}/><span>{v.toLocaleString('tr-TR',{maximumFractionDigits:3})}%</span></div>)}
 </div>;
}
