// Deterministic screen recording of the 55 s "demo" segment (D1–D6), v2 shot list.
// v1 (old business model, Hauler Delta comparison) is kept as record_v1.mjs → ../demo_v1.mp4.
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
// brief_cache_v2.sse: captured 7 Nov 23:40 from the live endpoint (business model v2: €52,154, 25 % fee, operator = partner).
const BRIEF = readFileSync(join(HERE, process.env.BRIEF_FILE || 'brief_cache_v2.sse'), 'utf8');

const args = process.argv.slice(2);
const stillsIdx = args.indexOf('--stills');
const STILLS = stillsIdx >= 0;
const ONLY = STILLS ? args.slice(stillsIdx + 1) : [];
const STILL_DIR = join(HERE, '..', 'explore', 'stills');

// v2 shot list (business model of 7 Nov): weight first, then money, then partner and Europress.
// D1 Free → SMART · D2 weight per machine · D3 savings trace · D4 partner view · D5 model check · D6 sales brief
const SHOTS = [
  { id: 'D1', t: 0.0, d: 9.0 }, { id: 'D2', t: 9.0, d: 9.0 }, { id: 'D3', t: 18.0, d: 10.0 },
  { id: 'D4', t: 28.0, d: 13.0 }, { id: 'D5', t: 41.0, d: 8.0 }, { id: 'D6', t: 49.0, d: 6.0 },
];

const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2); // easeInOutCubic
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

// ------------------------------------------------------------------ page setup
const INIT = () => {
  try {
    localStorage.setItem('ep.lang', 'en');
    // The take starts on SMART Free; D1 clicks the SMART switch, which stores 'smart' for the rest.
    if (!sessionStorage.getItem('__rec')) { localStorage.setItem('ep.plan', 'free'); sessionStorage.setItem('__rec', '1'); }
    localStorage.setItem('ep.customer', 'ORG-0049');
  } catch { /* ignore */ }
  // This machine has no emoji font, so the app's 🔒 renders as a box. Swap it for an inline SVG lock
  // in the recording browser only (the app itself is not changed).
  const LOCK = '<svg viewBox="0 0 24 24" width="0.95em" height="0.95em" style="vertical-align:-0.13em;margin-right:.15em" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>';
  const fixLocks = (root) => {
    if (!root) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const hits = [];
    while (w.nextNode()) if (w.currentNode.nodeValue.includes('🔒')) hits.push(w.currentNode);
    for (const n of hits) {
      const frag = document.createDocumentFragment();
      n.nodeValue.split('🔒').forEach((part, i) => {
        if (i) { const s = document.createElement('span'); s.innerHTML = LOCK; frag.appendChild(s.firstChild); }
        frag.appendChild(document.createTextNode(part.replace(/^ /, i ? '' : ' ')));
      });
      n.replaceWith(frag);
    }
  };
  new MutationObserver((ms) => {
    for (const m of ms) {
      if (m.type === 'characterData') fixLocks(m.target.parentNode);
      for (const a of m.addedNodes) fixLocks(a.nodeType === 1 ? a : a.parentNode);
    }
  }).observe(document, { childList: true, subtree: true, characterData: true });
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
  // D1 · Customer, SMART Free → SMART: the weight is what SMART sells.
  async D1(r) {
    await r.go('#overview');
    r.cx = 1180; r.cy = 330;
    await r.hold(0.8);
    await r.move('.plan-lock p', 0.9, 0.5, 0.5);                       // → 1.7  "With SMART you see the weight…"
    await r.holdUntil(3.3);
    await r.move('#planToggle button[data-plan="smart"]', 0.9, 0.5, 0.55); // → 4.2
    await r.click(1800);                                               // Free → SMART
    await r.holdUntil(4.8);
    await r.move('text=/In your containers now/', 0.8, 0.12, 2.6);     // → 5.6  5.8 t
    await r.holdUntil(6.6);
    await r.move('#machinesNowOverview >> text=/kg inside now/', 0.8, 1.04, 0.55); // → 7.4  ≈ 2,849 kg
    await r.holdUntil(9.0);
  },
  // D2 · Weight per machine: now, at the next pickup, and the expected charge.
  async D2(r) {
    await r.go('#weight');
    r.cx = 900; r.cy = 250;
    await r.hold(0.4);
    await r.move('#weightTable tr:has-text("Mixed waste 2") td >> nth=2', 1.0, 0.8, 0.5); // → 1.4 weight now
    await r.holdUntil(2.3);
    await r.move('#weightTable tr:has-text("Mixed waste 2") td >> nth=5', 0.9, 0.8, 0.5); // → 3.2 expected charge
    await r.holdUntil(4.0);
    await r.move('#weightTable tr:has-text("Mixed waste 2") td >> nth=0', 0.6, 0.2, 0.3); // → 4.6
    await r.click(2500);                                               // machine page
    await r.page.evaluate(() => window.scrollTo(0, 0));
    await r.hold(0.2);
    await r.move('#machineWeight >> text=/Most likely/', 0.7, 0.5, 0.5); // → 5.5
    await r.holdUntil(6.4);
    await r.move('#machineWeight >> text=/Next pickup at your price/', 0.8, 0.5, 0.5); // → 7.2
    await r.holdUntil(9.0);
  },
  // D3 · Savings: every euro opens to its formula and data rows.
  async D3(r) {
    await r.go('#savings');
    r.cx = 700; r.cy = 500;
    await r.hold(0.4);
    await r.move('#leversTable tr:has-text("Total") >> text=/52,154/', 0.9, 0.5, 0.55); // → 1.3  total €52,154
    await r.holdUntil(2.2);
    await r.move('#leversTable tr:has-text("39,955") >> text=/39,955/', 0.8, 0.5, 0.55); // → 3.0
    await r.click(1200);                                           // trace drawer opens
    await r.holdUntil(4.2);
    await r.scrollTo('#drawerBody details.calc > summary', 140, 0.8, '#drawerBody'); // → 5.0
    await r.move('#drawerBody details.calc > summary', 0.6, 0.15, 0.5); // → 5.6
    await r.click(700);                                            // expand "How it is calculated"
    await r.hold(0.3);
    await r.scrollTo('#drawerBody details.calc > summary', 90, 0.9, '#drawerBody'); // → 6.8
    await r.move('#drawerBody .formula', 0.7, 0.6, 0.5);          // → 7.5
    await r.holdUntil(10.0);
  },
  // D4 · Partner view: driver plan 14 days ahead, value of SMART, the data partnership.
  async D4(r) {
    await r.go('#overview', 1200);
    r.cx = 1000; r.cy = 300;
    await r.hold(0.3);
    await r.move('#wsBtn', 0.8, 0.5, 0.55);                        // → 1.1
    await r.click(500);
    await r.hold(0.2);
    await r.move('#wsMenu button[data-ws="partners"]', 0.5, 0.4, 0.5); // → 1.8
    await r.click(2500);                                           // Partner view → Operator insight
    await r.page.evaluate(() => window.scrollTo(0, 0));
    await r.hold(0.3);
    await r.scrollTo('#view-operators >> text=/Driver plan/', 150, 0.8); // → 2.9
    await r.move('#view-operators >> text=/Call in more drivers/', 0.9, 0.5, 0.5); // → 3.8
    await r.holdUntil(5.4);
    await r.scrollTo('#view-operators >> text=/How SMART creates value for you/', 120, 1.3); // → 6.7
    await r.move('#view-operators >> text=/Fewer trips a year/', 0.8, 0.3, -0.9); // → 7.5  676
    await r.holdUntil(9.2);
    await r.move('#view-operators >> text=/You share through SMART/', 0.9, 0.4, 0.5); // → 10.1
    await r.holdUntil(11.4);
    await r.move('#view-operators >> text=/^You get$/', 0.7, 0.4, 0.5); // → 12.1
    await r.holdUntil(13.0);
  },
  // D5 · Europress view: the model checked against weighbridge weights, new installations.
  async D5(r) {
    await r.go('#operators', 800);
    r.cx = 1000; r.cy = 300;
    await r.hold(0.2);
    await r.move('#wsBtn', 0.7, 0.5, 0.55);                        // → 0.9
    await r.click(500);
    await r.hold(0.15);
    await r.move('#wsMenu button[data-ws="europress"]', 0.5, 0.4, 0.5); // → 1.55
    await r.click(2500);                                           // Europress → weight soft sensor
    await r.hold(0.2);
    await r.move('.ss-tabs a[href="#ep-sensor-check"]', 0.6, 0.5, 0.55); // → 2.35
    await r.click(3000);                                           // weighbridge check
    await r.page.evaluate(() => window.scrollTo(0, 0));
    await r.hold(0.2);
    await r.move('#view-ep-sensor-check button:has-text("New installations")', 0.6, 0.5, 0.5); // → 3.15
    await r.click(1500);                                           // machines the model never saw
    await r.hold(0.2);
    await r.scrollTo('#view-ep-sensor-check >> text=/Emptyings checked/', 150, 0.9); // → 4.25
    await r.move('#view-ep-sensor-check >> text=/Mean difference/', 0.6, 0.3, 3.4); // → 4.85
    await r.holdUntil(6.0);
    await r.move('#view-ep-sensor-check canvas >> nth=0', 0.8, 0.55, 0.3); // → 6.8 scatter
    await r.holdUntil(8.0);
  },
  // D6 · Sales: biggest savers first, a brief written by Claude from cited data.
  async D6(r) {
    await r.go('#ep-pipeline');
    r.cx = 1100; r.cy = 250;
    await r.hold(0.2);
    await r.move('#salesAlerts .lead:has-text("0049") .ans-row', 0.8, 0.5, 0.5); // → 1.0
    await r.click(1000);                                           // lead pop-up
    await r.hold(0.3);                                             // → 1.3
    await r.scrollTo('#drawerBody [data-lead="brief"]', 560, 0.6, '#drawerBody'); // → 1.9
    await r.move('#drawerBody [data-lead="brief"]', 0.5, 0.5, 0.5); // → 2.4
    r.releaseBrief = null;
    const released = new Promise((ok) => { r.releaseBrief = ok; });
    r.briefGate = released;
    await r.click(600);                                            // dock opens: question + "thinking"
    await r.holdUntil(3.0);
    r.releaseBrief();
    await wait(1200);
    await r.page.evaluate(() => { const l = document.getElementById('aiLog'); const b = l.querySelector('.msg.bot'); if (b) l.scrollTop = b.offsetTop - 8; });
    await r.hold(0.2);
    await r.move('#aiLog .msg.bot', 0.5, 0.015, 0.1);              // → ~3.7
    await r.holdUntil(4.0);
    const target = await r.page.evaluate(() => {                  // scroll position that puts "Tell the customer" on top
      const l = document.getElementById('aiLog'); const b = l.querySelector('.msg.bot');
      const tell = [...b.querySelectorAll('p, li, div')].find((e) => e.textContent.trim().startsWith('Tell the customer'));
      const max = l.scrollHeight - l.clientHeight;
      if (!tell) return max;
      return Math.min(max, tell.getBoundingClientRect().top - l.getBoundingClientRect().top + l.scrollTop - 12);
    });
    await r.frames(r.sec(1.4), async (p) => {                     // → 5.4 scroll the brief to "Tell the customer"
      await r.page.evaluate(([p, to]) => {
        const l = document.getElementById('aiLog'); const b = l.querySelector('.msg.bot');
        const from = b.offsetTop - 8;
        l.scrollTop = from + (to - from) * p;
      }, [ease(p), target]);
    });
    await r.holdUntil(6.0);
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
