import MaterialLibrary from '../../../components/material-library';
export default async function Page({params}:{params:Promise<{id:string}>}){const {id}=await params;return <main className="library-page"><MaterialLibrary id={id}/></main>}
