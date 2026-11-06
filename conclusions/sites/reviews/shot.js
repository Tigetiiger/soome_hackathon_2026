// usage: node shot.js <html file> <out.png> [width] [light|dark] [#hash]
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const [,, file, out, width, theme, hash] = process.argv;
  const exe = ['/usr/bin/chromium','/usr/bin/chromium-browser'].find(p => fs.existsSync(p));
  const b = await chromium.launch(exe ? { executablePath: exe } : {});
  const p = await b.newPage({ viewport: { width: +(width||1280), height: 900 }, colorScheme: theme||'light' });
  const errs=[]; p.on('pageerror', e=>errs.push(e.message)); p.on('console', m=>{ if(m.type()==='error') errs.push(m.text()) });
  await p.goto('file://'+file+(hash||'')); await p.waitForTimeout(1500);
  await p.screenshot({ path: out, fullPage: true });
  console.log(JSON.stringify({errors:errs}));
  await b.close();
})();
