const T = require('C:/Users/MONSTER/.claude/tarayici/lib/tarayici.js');
;(async () => {
const { page, kapat } = await T.ac({ viewport: { width: 1440, height: 900 } });
const errors = [];
page.on('pageerror', error => errors.push(`pageerror: ${error.message}`));
page.on('console', message => { if (message.type() === 'error') errors.push(`console: ${message.text()}`); });
try {
  await T.git(page, 'http://127.0.0.1:3000/materials');
  await page.waitForSelector('.research-archive');
  await page.waitForTimeout(3000);
  const count = await page.locator('.research-archive').innerText();
  if (!count.includes('35.478')) { console.log('ARCHIVE_TEXT', count); throw new Error('Archive result count not rendered'); }
  await T.yaz(page, '.research-archive input', 'Tenmoku');
  await page.waitForFunction(() => document.querySelector('.research-archive')?.textContent?.includes('315'), null, { timeout: 15000 });
  const resultText = await page.locator('.archive-list').innerText();
  if (!resultText.includes('Tenmoku')) throw new Error('Search result not rendered');
  await T.tikla(page, '.archive-list button');
  await page.waitForSelector('.archive-detail');
  const detail = await page.locator('.archive-detail').innerText();
  if (!detail.includes('Reçete bileşenleri') || !detail.includes('Raporlanan oksit analizi')) throw new Error('Detail cards missing');
  const screenshot = await T.ekranGoruntusu(page, 'research-archive');
  console.log(JSON.stringify({ ok: true, screenshot, errors, hasDetailCards: true }));
} finally { await kapat(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
