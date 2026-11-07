import { chromium } from 'playwright-core';
const OUT = '/home/hackathon/output/demo-video/clips/screen/explore';
const zoom = Number(process.argv[2] || 1.15);
const browser = await chromium.launch({ executablePath: '/usr/bin/chromium' });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, colorScheme: 'light', locale: 'en-GB' });
await ctx.addInitScript(() => { try { localStorage.setItem('ep.lang', 'en'); localStorage.setItem('ep.plan','smart'); } catch {} });
const page = await ctx.newPage();
page.on('pageerror', (e) => console.error('pageerror', e.message));
for (const v of ['overview','weight','contracts','savings','ep-sensor','ep-sensor-check','ep-pipeline','ep-overview']) {
  await page.goto('http://127.0.0.1:8080/#' + v);
  await page.waitForTimeout(3500);
  await page.evaluate((z) => { document.documentElement.style.zoom = z; }, zoom);
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT}/${v}.png` });
  const h = await page.evaluate(() => [document.documentElement.scrollHeight, document.querySelector('.main')?.scrollHeight, getComputedStyle(document.querySelector('.main')).overflowY]);
  console.log(v, h);
  await page.screenshot({ path: `${OUT}/${v}_full.png`, fullPage: true });
}
await browser.close();
