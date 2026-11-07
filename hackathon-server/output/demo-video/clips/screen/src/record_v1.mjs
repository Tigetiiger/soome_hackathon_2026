// Deterministic screen recording of the 55 s "demo" segment (D1–D6).
// Every video frame is one PNG screenshot of the live app (headless Chromium, 1600x900 CSS px at
// deviceScaleFactor 1.2 = 1920x1080 device px). Cursor, scrolling and click ripples are driven per frame
// by this script, so motion is perfectly even at 30 fps regardless of how long a screenshot takes.
// The app is only read: no code or data is changed. The one /api/ask call (D6 "brief") is answered
// from brief_cache.sse, a real answer captured from the live endpoint before the take.
//
//   node record.mjs                 -> ../demo.mp4
//   node record.mjs --stills D4     -> stills every 15 frames of shot D4 into ../explore/stills
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '..', 'demo.mp4');
const FFMPEG = '/home/hackathon/output/animation-comparison/bin/ffmpeg';
const APP = 'http://127.0.0.1:8080/';
const FPS = 30;
const W = 1600, H = 900, DSF = 1.2;
const BRIEF = readFileSync(join(HERE, process.env.BRIEF_FILE || 'brief_cache.sse'), 'utf8');

const args = process.argv.slice(2);
const stillsIdx = args.indexOf('--stills');
const STILLS = stillsIdx >= 0;
const ONLY = STILLS ? args.slice(stillsIdx + 1) : [];
const STILL_DIR = join(HERE, '..', 'explore', 'stills');

const SHOTS = [
  { id: 'D1', t: 0.0, d: 9.0 }, { id: 'D2', t: 9.0, d: 9.0 }, { id: 'D3', t: 18.0, d: 9.0 },
  { id: 'D4', t: 27.0, d: 9.0 }, { id: 'D5', t: 36.0, d: 10.0 }, { id: 'D6', t: 46.0, d: 9.0 },
];

const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2); // easeInOutCubic
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

// ------------------------------------------------------------------ page setup
const INIT = () => {
  try {
    localStorage.setItem('ep.lang', 'en');
    localStorage.setItem('ep.plan', 'smart');
    localStorage.setItem('ep.customer', 'ORG-0049');
  } catch { /* ignore */ }
  const install = () => {
    if (document.getElementById('__cur')) return;
    const st = document.createElement('style');
    st.textContent = `
      html, body, * { scroll-behavior: auto !important; }
      #aiPopup { display: none !important; }
      #__cur, #__rip { position: fixed; left: 0; top: 0; pointer-events: none; z-index: 2147483647; border-radius: 50%; }
      #__cur { width: 18px; height: 18px; margin: -9px 0 0 -9px; border: 3px solid #0a1a5c; background: rgba(255,255,255,.55);
               box-shadow: 0 0 0 1.5px rgba(255,255,255,.95), 0 2px 6px rgba(0,0,0,.35); box-sizing: border-box; }
      #__rip { width: 18px; height: 18px; margin: -9px 0 0 -9px; border: 2.5px solid #0a1a5c; opacity: 0; box-sizing: border-box; }`;
    document.head.appendChild(st);
    const rip = document.createElement('div'); rip.id = '__rip'; document.body.appendChild(rip);
    const cur = document.createElement('div'); cur.id = '__cur'; document.body.appendChild(cur);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install); else install();
};

// ------------------------------------------------------------------ recorder
class Rec {
  constructor(page, cdp, sink) {
    Object.assign(this, { page, cdp, sink });
    this.frame = 0; this.shotStart = 0; this.cx = 800; this.cy = 450; this.rippleAt = -999; this.shotId = '';
  }
  async apply() {
    const rp = (this.frame - this.rippleAt) / (0.45 * FPS);
    await this.page.evaluate(([x, y, rp]) => {
      const c = document.getElementById('__cur'), r = document.getElementById('__rip');
      if (!c) return;
      c.style.transform = `translate(${x}px, ${y}px)`;
      r.style.transform = `translate(${x}px, ${y}px) scale(${rp >= 0 && rp <= 1 ? 1 + rp * 2.6 : 1})`;
      r.style.opacity = rp >= 0 && rp <= 1 ? String(0.85 * (1 - rp)) : '0';
      c.style.scale = rp >= 0 && rp <= 0.35 ? String(0.8 + 0.2 * (rp / 0.35)) : '1';
    }, [this.cx, this.cy, rp]);
  }
  async snap() {
    await this.apply();
    const buf = await this.page.screenshot({ type: 'png', scale: 'device', animations: 'allow', caret: 'initial' });
    const local = this.frame - this.shotStart;
    if (this.sink) await this.sink(buf);
    else if (local % 15 === 0) writeFileSync(join(STILL_DIR, `${this.shotId}_${String(local).padStart(3, '0')}.png`), buf);
    this.frame += 1;
  }
  async frames(n, step) {
    for (let i = 1; i <= n; i += 1) { if (step) await step(i / n); await this.snap(); }
  }
  sec(s) { return Math.max(1, Math.round(s * FPS)); }
  async hold(s) { await this.frames(this.sec(s)); }
  async holdUntil(tLocal) { const n = Math.round(tLocal * FPS) - (this.frame - this.shotStart); if (n > 0) await this.frames(n); }
  async box(sel) {
    const loc = this.page.locator(sel).first();
    const b = await loc.boundingBox();
    if (!b) throw new Error(`no box for ${sel}`);
    return b;
  }
  /** Move the cursor to a selector (ax, ay = anchor within its box, 0..1) or to {x, y}. */
  async move(target, s, ax = 0.5, ay = 0.5) {
    let x, y;
    if (typeof target === 'string') { const b = await this.box(target); x = b.x + b.width * ax; y = b.y + b.height * ay; }
    else ({ x, y } = target);
    const x0 = this.cx, y0 = this.cy;
    await this.frames(this.sec(s), async (p) => {
      const e = ease(p); this.cx = x0 + (x - x0) * e; this.cy = y0 + (y - y0) * e;
      await this.page.mouse.move(this.cx, this.cy);
    });
  }
  async click(settleMs = 900) {
    this.rippleAt = this.frame;
    await this.page.mouse.click(this.cx, this.cy);
    await wait(settleMs); // let the app re-render (wall clock only; no video time passes)
  }
  /** Ease-scroll the window (scroller = null) or an element so that `sel` top lands at viewport y = topY. */
  async scrollTo(sel, topY, s, scroller = null) {
    const from = await this.page.evaluate((sc) => (sc ? document.querySelector(sc).scrollTop : window.scrollY), scroller);
    const b = await this.box(sel);
    const want = await this.page.evaluate(([sc, delta]) => {
      const el = sc ? document.querySelector(sc) : document.scrollingElement;
      const max = el.scrollHeight - el.clientHeight;
      return Math.max(0, Math.min(max, (sc ? el.scrollTop : window.scrollY) + delta));
    }, [scroller, b.y - topY]);
    await this.frames(this.sec(s), async (p) => {
      const v = from + (want - from) * ease(p);
      await this.page.evaluate(([sc, v]) => { if (sc) document.querySelector(sc).scrollTop = v; else window.scrollTo(0, v); }, [scroller, v]);
    });
  }
  async go(hash, settleMs = 2500) {
    await this.page.evaluate((h) => { location.hash = h; }, hash);
    await wait(settleMs);
    await this.page.evaluate(() => window.scrollTo(0, 0));
  }
}

// ------------------------------------------------------------------ shots (times are seconds within the shot)
const plan = {
  async D1(r) {
    await r.go('#overview');
    r.cx = 1180; r.cy = 300;
    await r.hold(1.0);
    await r.scrollTo('#view-overview h2[data-i18n="machines.title"]', 115, 1.4);          // 1.0 → 2.4  machine cards
    await r.move('#machinesNowOverview >> text=/kg inside now/', 1.0, 1.06, 0.55); // → 3.4
    await r.holdUntil(5.0);
    await r.scrollTo('.save-card', 105, 1.4);                     // 5.0 → 6.4  savings card
    await r.move('#saveTitle', 0.9, 0.62, 1.8);                  // → 7.3
    await r.holdUntil(9.0);
  },
  async D2(r) {
    await r.go('#weight');
    r.cx = 900; r.cy = 200;
    await r.hold(0.4);
    await r.move('#weightTable tr:has-text("Mixed waste 2") td >> nth=0', 1.0, 0.3, 0.3); // → 1.4
    await r.click(2500);                                           // machine page
    await r.page.evaluate(() => window.scrollTo(0, 0));
    await r.hold(0.3);
    await r.move('#machineWeight >> text=/Most likely/', 0.9, 0.5, 0.5); // → 2.6
    await r.holdUntil(3.6);
    await r.scrollTo('#machineWeight >> text=/Weight in the container, last 30 days/', 115, 1.1); // → 4.7
    await r.move('#machineWeight canvas >> nth=0', 0.8, 0.515, 0.2); // → 5.5  (weighbridge ticket marker on the band)
    await r.holdUntil(5.9);
    await r.scrollTo('#machineWeight >> text=/Last pickups/', 115, 1.1); // → 7.0
    await r.move('#machineWeight table tbody tr >> nth=0 >> td >> nth=2', 0.7, 0.6, 0.5); // → 7.7
    await r.holdUntil(9.0);
  },
  async D3(r) {
    await r.go('#contracts');
    r.cx = 700; r.cy = 420;
    await r.hold(0.4);
    await r.move('#operatorsTable tr:has-text("Hauler Delta") td >> nth=1', 1.0, 0.75, 0.5); // → 1.4 on time 57 %
    await r.holdUntil(2.6);
    await r.move('#operatorsTable tr:has-text("Hauler Delta") td >> nth=2', 0.8, 0.85, 0.5); // → 3.4 shared 0 %
    await r.holdUntil(4.6);
    await r.move('#operatorsTable tr:has-text("Hauler Epsilon") td >> nth=1', 0.8, 0.75, 0.5); // → 5.4
    await r.holdUntil(5.9);
    await r.move('#operatorsTable tr:has-text("Hauler Epsilon") td >> nth=2', 0.6, 0.85, 0.5); // → 6.5
    await r.holdUntil(7.1);
    await r.move('#operatorsAsOf', 0.8, 0.5, 1.6);                 // → 7.9 data as of
    await r.holdUntil(9.0);
  },
  async D4(r) {
    await r.go('#savings');
    r.cx = 700; r.cy = 500;
    await r.hold(0.3);
    await r.move('#leversTable tr:has-text("39,955") >> text=/39,955/', 1.1, 0.5, 0.55); // → 1.4
    await r.click(1200);                                           // trace drawer opens
    await r.holdUntil(2.6);
    await r.scrollTo('#drawerBody details.calc > summary', 140, 0.8, '#drawerBody'); // → 3.4
    await r.move('#drawerBody details.calc > summary', 0.6, 0.15, 0.5); // → 4.0
    await r.click(700);                                            // expand "How it is calculated"
    await r.hold(0.3);
    await r.scrollTo('#drawerBody details.calc > summary', 90, 0.9, '#drawerBody'); // → 5.2
    await r.move('#drawerBody .formula', 0.7, 0.6, 0.5);          // → 5.9
    await r.holdUntil(9.0);
  },
  async D5(r) {
    await r.go('#overview');
    r.cx = 1000; r.cy = 300;
    await r.hold(0.3);
    await r.move('#wsBtn', 0.9, 0.5, 0.55);                        // → 1.2
    await r.click(500);
    await r.hold(0.2);
    await r.move('#wsMenu button[data-ws="europress"]', 0.6, 0.4, 0.5); // → 2.0
    await r.click(2500);                                           // Europress → weight soft sensor (live fleet)
    await r.hold(0.4);
    await r.move('.ss-tabs a[href="#ep-sensor-check"]', 0.8, 0.5, 0.55); // → 3.2
    await r.click(3000);                                           // weighbridge check
    await r.page.evaluate(() => window.scrollTo(0, 0));
    await r.hold(0.5);
    await r.scrollTo('#view-ep-sensor-check >> text=/Emptyings checked/', 125, 1.2); // → 4.9
    await r.move('#view-ep-sensor-check >> text=/Emptyings checked/', 0.8, 0.4, 3.2); // → 5.7 (4,876)
    await r.holdUntil(7.0);
    await r.move('#view-ep-sensor-check canvas >> nth=0', 1.0, 0.55, 0.45); // → 8.0 scatter
    await r.holdUntil(10.0);
  },
  async D6(r) {
    await r.go('#ep-pipeline');
    r.cx = 1100; r.cy = 250;
    await r.hold(0.3);
    await r.move('#salesAlerts .lead:has-text("0049") .ans-row', 1.0, 0.5, 0.5); // → 1.3
    await r.click(1000);                                           // lead pop-up
    await r.hold(0.8);                                             // → 2.1
    await r.scrollTo('#drawerBody [data-lead="brief"]', 560, 0.9, '#drawerBody'); // → 3.0
    await r.move('#drawerBody [data-lead="brief"]', 0.7, 0.5, 0.5); // → 3.7
    r.releaseBrief = null;
    const released = new Promise((ok) => { r.releaseBrief = ok; });
    r.briefGate = released;
    await r.click(600);                                            // dock opens: question + "thinking"
    await r.holdUntil(5.0);
    r.releaseBrief();
    await wait(1200);
    await r.page.evaluate(() => { const l = document.getElementById('aiLog'); const b = l.querySelector('.msg.bot'); if (b) l.scrollTop = b.offsetTop - 8; });
    await r.hold(0.3);
    await r.move('#aiLog .msg.bot', 0.7, 0.015, 0.1);              // → ~6.0
    await r.holdUntil(6.4);
    await r.frames(r.sec(1.6), async (p) => {                     // → 8.0 scroll the brief to "Tell the customer"
      await r.page.evaluate((p) => {
        const l = document.getElementById('aiLog'); const b = l.querySelector('.msg.bot');
        const from = b.offsetTop - 8; const to = l.scrollHeight - l.clientHeight;
        l.scrollTop = from + (to - from) * p;
      }, ease(p));
    });
    await r.holdUntil(9.0);
  },
};

// ------------------------------------------------------------------ main
async function main() {
  if (STILLS) mkdirSync(STILL_DIR, { recursive: true });
  const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--hide-scrollbars', '--font-render-hinting=none'] });
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: DSF, colorScheme: 'light', reducedMotion: 'reduce', locale: 'en-GB', bypassCSP: true });
  await ctx.addInitScript(INIT);
  const page = await ctx.newPage();
  page.on('pageerror', (e) => process.stderr.write(`pageerror: ${e.message}\n`));
  let rec;
  await page.route('**/api/ask', async (route) => {
    if (rec?.briefGate) await rec.briefGate;
    await route.fulfill({ status: 200, headers: { 'content-type': 'text/event-stream; charset=utf-8' }, body: BRIEF });
  });
  await page.goto(`${APP}#overview`);
  await page.waitForFunction(() => document.getElementById('__cur') && document.querySelector('#machinesNowOverview .rt-weightlink, #machinesNowOverview *'), null, { timeout: 30000 });
  await wait(3000);
  const cdp = await ctx.newCDPSession(page);

  let ff = null, sink = null;
  if (!STILLS) {
    ff = spawn(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-movflags', '+faststart', '-an', OUT],
    { stdio: ['pipe', 'inherit', 'inherit'] });
    sink = (buf) => (ff.stdin.write(buf) ? Promise.resolve() : new Promise((ok) => ff.stdin.once('drain', ok)));
  }
  rec = new Rec(page, cdp, sink);
  const t0 = Date.now();
  const log = [];
  for (const shot of SHOTS) {
    const total = Math.round(shot.d * FPS);
    if (STILLS && ONLY.length && !ONLY.includes(shot.id)) continue;
    // close anything left open from the previous shot (drawer, dock, menus)
    await page.evaluate(() => {
      document.querySelectorAll('[data-close]').forEach((b) => { if (b.offsetParent) b.click(); });
      const d = document.getElementById('advisorDock'); if (d && !d.classList.contains('hidden')) document.getElementById('advisorClose').click();
    });
    rec.shotStart = rec.frame; rec.shotId = shot.id; rec.briefGate = null;
    await plan[shot.id](rec);
    const used = rec.frame - rec.shotStart;
    if (used > total) throw new Error(`${shot.id} overran: ${used} > ${total}`);
    if (used < total) await rec.frames(total - used);
    log.push(`${shot.id} frames ${rec.shotStart}-${rec.frame - 1} (${(rec.shotStart / FPS).toFixed(2)}s-${(rec.frame / FPS).toFixed(2)}s), script used ${used}`);
    process.stdout.write(`${log[log.length - 1]}  wall ${((Date.now() - t0) / 1000).toFixed(0)}s\n`);
  }
  if (ff) {
    ff.stdin.end();
    await new Promise((ok, fail) => ff.on('close', (c) => (c === 0 ? ok() : fail(new Error(`ffmpeg ${c}`)))));
  }
  writeFileSync(join(HERE, STILLS ? 'stills_log.txt' : 'record_log.txt'), log.join('\n') + '\n');
  await browser.close();
  process.stdout.write(`done, ${rec.frame} frames\n`);
}
main().catch((e) => { process.stderr.write(`${e.stack}\n`); process.exit(1); });
