// Deterministic MP4 capture of the three.js demo.
// Serves the repo root over HTTP, drives headless Chromium frame by frame
// (window.__render(t)), and pipes PNG screenshots into ffmpeg.
//
//   node capture.mjs [--frames N] [--still t]
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { existsSync, mkdirSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { extname, join, normalize, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { homedir } from 'node:os';
import { chromium } from 'playwright-core';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '../..');
const OUT_DIR = join(HERE, 'out');
const FPS = 30;
const DURATION = 12;
const args = process.argv.slice(2);
const argVal = (k, d) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const FRAMES = Number(argVal('--frames', DURATION * FPS));
const STILL = argVal('--still', null);

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.json': 'application/json', '.ttf': 'font/ttf', '.css': 'text/css' };

function serve() {
  const server = createServer(async (req, res) => {
    const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname));
    const file = join(ROOT, path);
    if (!file.startsWith(ROOT)) { res.writeHead(403).end(); return; }
    try {
      const body = await readFile(file);
      res.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream' }).end(body);
    } catch {
      res.writeHead(404).end();
    }
  });
  return new Promise((ok) => server.listen(0, '127.0.0.1', () => ok(server)));
}

function chromiumPath() {
  const shell = join(homedir(), '.cache/ms-playwright/chromium_headless_shell-1148/chrome-linux/headless_shell');
  return process.env.CHROMIUM_PATH ?? (existsSync(shell) ? shell : '/usr/bin/chromium');
}

async function main() {
  mkdirSync(OUT_DIR, { recursive: true });
  const server = await serve();
  const url = `http://127.0.0.1:${server.address().port}/demos/threejs/index.html?capture`;
  const browser = await chromium.launch({
    executablePath: chromiumPath(),
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => process.stderr.write(`pageerror: ${e.message}\n`));
  await page.goto(url);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 120000 });

  if (STILL !== null) {
    await page.evaluate((t) => window.__render(t), Number(STILL));
    await page.screenshot({ path: join(OUT_DIR, `still_${STILL}.png`) });
  } else {
    const t0 = Date.now();
    const ff = spawn(join(ROOT, 'bin/ffmpeg'), ['-y', '-loglevel', 'error', '-f', 'image2pipe',
      '-framerate', String(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18',
      '-preset', 'slow', '-movflags', '+faststart', join(OUT_DIR, 'fleet_timeseries.mp4')],
    { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < FRAMES; f += 1) {
      await page.evaluate((t) => window.__render(t), f / FPS);
      const png = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(png)) await new Promise((ok) => ff.stdin.once('drain', ok));
      if (f % 60 === 0) process.stdout.write(`frame ${f}/${FRAMES}  ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);
    }
    ff.stdin.end();
    await new Promise((ok, fail) => ff.on('close', (code) => (code === 0 ? ok() : fail(new Error(`ffmpeg ${code}`)))));
    process.stdout.write(`wrote fleet_timeseries.mp4 in ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);
  }
  await browser.close();
  server.close();
}

main().catch((e) => { process.stderr.write(`${e.stack}\n`); process.exit(1); });
