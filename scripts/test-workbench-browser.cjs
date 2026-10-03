const fs=require('node:fs');
const assert=require('node:assert/strict');
const T=require(['C:/Users/MONSTER/.Codex/tarayici/lib/tarayici.js','C:/Users/MONSTER/.claude/tarayici/lib/tarayici.js'].find(p=>fs.existsSync(p)));
(async()=>{const {page,kapat}=await T.ac();const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});try{
 await T.git(page,'http://127.0.0.1:3000/');
 await page.getByText('Hesap motoru bağlı',{exact:true}).waitFor();
 console.log(await T.ekranGoruntusu(page,'lab-workbench-desktop'));
 for(const route of ['analyze','explore','experiments']){
  await T.tikla(page,`.lab-navigation nav a[href="/${route}"]`);
  await page.waitForURL(`**/${route}`);
  assert.equal(await page.locator(`.lab-navigation nav a[href="/${route}"]`).getAttribute('aria-current'),'page');
  await page.locator('main').waitFor();
 }
 await T.tikla(page,'.lab-navigation nav a[href="/"]');
 await page.getByText('Hesap motoru bağlı',{exact:true}).waitFor();
 await page.setViewportSize({width:390,height:844});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 console.log(await T.ekranGoruntusu(page,'lab-workbench-mobile'));
 assert.deepEqual(errors,[]);console.log('PASS: home, live health, three routes, active navigation, mobile overflow, browser errors');
}finally{await kapat();}})().catch(e=>{console.error(e);process.exitCode=1});
