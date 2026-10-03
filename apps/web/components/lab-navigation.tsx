'use client';
import Link from 'next/link';
import {usePathname} from 'next/navigation';
export default function LabNavigation(){
 const path=usePathname();
 return <div className="lab-navigation"><Link className="lab-brand" href="/">C / L <span>Ceramic Glaze Lab</span></Link><nav aria-label="Laboratuvar araçları">{[['/','Masam'],['/analyze','Reçete'],['/materials','Kütüphane'],['/explore','Dönüşüm'],['/experiments','Deney defteri']].map(([href,label])=><Link key={href} href={href} aria-current={path===href||(href==='/materials'&&path.startsWith('/materials/'))?'page':undefined}>{label}</Link>)}</nav><span className="lab-local">Yerel · Araştırma prototipi</span></div>;
}
