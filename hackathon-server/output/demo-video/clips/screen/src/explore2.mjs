// Probe the current app for the v2 shot list: one viewport + one full-page screenshot per view,
// in the same 1600x900 CSS geometry the recorder uses.   node explore2.mjs
import { chromium } from 'playwright-core';
import { mkdirSync } from 'node:fs';
const OUT = '/home/hackathon/output/demo-video/clips/screen/explore/v2';
mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--hide-scrollbars'] });
const views = [
  ['smart', 'overview'], ['free', 'overview'], ['smart', 'weight'], ['smart', 'machines'], ['smart', 'savings'],
  ['smart', 'operators'], ['smart', 'ep-sensor'], ['smart', 'ep-sensor-check'], ['smart', 'ep-pipeline'], ['smart', 'ep-overview'],
];
for (const [plan, v] of views) {
  const ctx = await browser.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1, colorScheme: 'light', locale: 'en-GB' });
  await ctx.addInitScript((plan) => { try { localStorage.setItem('ep.lang', 'en'); localStorage.setItem('ep.plan', plan); localStorage.setItem('ep.customer', 'ORG-0049'); } catch {} }, plan);
  const page = await ctx.newPage();
  page.on('pageerror', (e) => console.error('pageerror', v, e.message));
  await page.goto('http://127.0.0.1:8080/#' + v);
  await page.waitForTimeout(3500);
  await page.addStyleTag({ content: '#aiPopup{display:none!important}' });
  await page.screenshot({ path: `${OUT}/${plan}_${v}.png` });
  await page.screenshot({ path: `${OUT}/${plan}_${v}_full.png`, fullPage: true });
  const heads = await page.evaluate(() => [...document.querySelectorAll('h1, h2, h3')]
    .filter((h) => h.offsetParent).map((h) => `${h.tagName}${h.id ? '#' + h.id : ''}: ${h.textContent.trim().slice(0, 70)}`).slice(0, 30));
  console.log(`== ${plan} ${v}\n  ` + heads.join('\n  '));
  await ctx.close();
}
await browser.close();
