// Run against localhost with EXPERIMENT_* roots pointing at an isolated QA archive.
const fs = require('node:fs');
const assert = require('node:assert/strict');
if (process.env.CERAMIC_QA_ARCHIVE_CONFIRMED !== '1') {
  throw new Error('Start the API with isolated EXPERIMENT_RECORD_ROOT and EXPERIMENT_MEASUREMENT_ROOT, then set CERAMIC_QA_ARCHIVE_CONFIRMED=1. Never run against real specimen storage.');
}
const kits = ['C:/Users/MONSTER/.Codex/tarayici/lib/tarayici.js','C:/Users/MONSTER/.claude/tarayici/lib/tarayici.js'];
const T = require(kits.find(path => fs.existsSync(path)) || kits[0]);

(async () => {
  const { page, kapat } = await T.ac();
  const errors = []; page.on('pageerror', error => errors.push(error.message));
  async function fill(label, value) { const item=page.getByLabel(label,{exact:true}); await item.waitFor({state:'visible'}); await item.fill(value); }
  async function select(label, value) { const item=page.getByLabel(label,{exact:true}); await item.waitFor({state:'visible'}); await item.selectOption(value); }
  async function count(value) { await page.locator('.notebook-readings li').nth(value-1).waitFor(); assert.equal(await page.locator('.notebook-readings li').count(),value); }
  try {
    await T.git(page,'http://127.0.0.1:3000/experiments/measurements');
    await page.getByRole('heading',{name:'01 / Numuneyi tanımla'}).waitFor();
    const run = Date.now().toString();
    await fill('Deney kimliği',`qa-${run}`);
    await fill('Numune kimliği','QA — yazılım testi');
    await fill('Deneyin kaynağı','Yazılım testi; fiziksel deney yapılmadı');
    await fill('Araştırma sorusu · isteğe bağlı','Kaydetme ve yeniden açma akışı kontrolü');
    await T.tikla(page,'button:has-text("Numuneyi kaydet")');
    await page.getByRole('heading',{name:'QA — yazılım testi'}).waitFor();
    const recordId=new URL(page.url()).searchParams.get('record');
    assert.match(recordId,/^[0-9a-f]{64}$/);
    await fill('Ölçüm değeri · %','7,4');
    await select('Kayıt niteliği','MEASURED');
    await fill('Okuma / tekrar kimliği','qa-okuma-01');
    await fill('Yöntem / cihaz','Yazılım test girdisi — gerçek ölçüm değil');
    await T.tikla(page,'button:has-text("Ölçümü kaydet")');
    await count(1);
    assert.match(await page.locator('.notebook-readings').innerText(),/7,4/);
    assert.equal(await page.getByRole('button',{name:'Ölçüm kaydedildi',exact:true}).isDisabled(),true);

    await select('İncelenen özellik','defect_observation');
    await select('Gözlenen özellik','CRAZING');
    await select('Kayıt niteliği','NOT_ASSESSED');
    await fill('Okuma / tekrar kimliği','qa-inceleme-01');
    await fill('Yöntem / cihaz','Yazılım test durumu');
    await T.tikla(page,'button:has-text("Ölçümü kaydet")');
    await count(2);
    await select('Kayıt niteliği','OBSERVED_ABSENT');
    await fill('Okuma / tekrar kimliği','qa-inceleme-02');
    await T.tikla(page,'button:has-text("Ölçümü kaydet")');
    await count(3);
    const history=await page.locator('.notebook-readings').innerText();
    assert.match(history,/Değerlendirilmedi/); assert.match(history,/İncelendi, görülmedi/);

    await select('İncelenen özellik','optical_transmission_class');
    await select('Gözlenen özellik','OPAQUE');
    await select('Kayıt niteliği','OBSERVED');
    await fill('Okuma / tekrar kimliği','qa-optik-01');
    await fill('Yöntem / cihaz','Yazılım test sınıflandırması');
    await page.route('**/api/v1/experiments/*/measurements', route => {
      if(route.request().method()==='POST') return route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({errors:[{message:'Test bağlantı kesintisi',path:[]}]})});
      return route.continue();
    },{times:1});
    await T.tikla(page,'button:has-text("Ölçümü kaydet")');
    await page.locator('.notebook-error[role="alert"]').waitFor();
    assert.match(await page.locator('.notebook-error[role="alert"]').innerText(),/Test bağlantı kesintisi/);
    assert.equal(await page.locator('.notebook-readings li').count(),3);
    await T.tikla(page,'button:has-text("Ölçümü kaydet")');
    await count(4);

    const downloaded=page.waitForEvent('download');
    await T.tikla(page,'button:has-text("Numune dosyasını indir")');
    const file=await downloaded;
    const exported=JSON.parse(fs.readFileSync(await file.path(),'utf8'));
    assert.equal(exported.schema_version,'lab-notebook-export-v1');
    assert.equal(exported.measurements.length,4);
    assert.equal(exported.measurements[0].measurement.measurement.value,7.4);
    assert.equal(exported.record.record_id,recordId);
    await page.reload(); await count(4);
    assert.equal(new URL(page.url()).searchParams.get('record'),recordId);
    const desktop=await T.ekranGoruntusu(page,'lab-measurements-desktop');
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1),'Mobile page overflows');
    const mobile=await T.ekranGoruntusu(page,'lab-measurements-mobile');
    await T.tikla(page,'button:has-text("Yeni numune")');
    await page.getByRole('heading',{name:'01 / Numuneyi tanımla'}).waitFor();
    await fill('Kayıt kimliğiyle aç',recordId);
    await T.tikla(page,'button:has-text("Kaydı aç")');
    await count(4);
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({status:'PASS',recordId,desktop,mobile,checks:['create','decimal-comma','distinct-defect-states','retry-after-503','export','reload','reopen','mobile-width','no-page-errors']}));
  } finally { await kapat(); }
})().catch(error => { console.error(error); process.exitCode=1; });
