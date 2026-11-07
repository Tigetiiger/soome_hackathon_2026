// three.js demo: 14 days of fill-mass for a fleet of 6 compactors.
// Interactive in a browser (play / scrub / free orbit camera); deterministic
// frame-by-frame rendering for MP4 capture via window.__render(t).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

const CAPTURE = new URLSearchParams(location.search).has('capture');
const DURATION = 12;          // seconds of animation
const SPAN = 30;              // world units for 14 days
const H_MAX = 6;              // world height for capacity
const ROW_GAP = 2.5;

const [style, data] = await Promise.all([
  fetch('../../shared/style.json').then((r) => r.json()),
  fetch('../../data/timeseries.json').then((r) => r.json()),
]);
const C = style.colors;
const HOURS = data.hours;
const ROWS = data.compactors.length;
const xOf = (h) => (h / (HOURS - 1)) * SPAN - SPAN / 2;
const yOf = (kg) => (kg / data.capacity_kg) * H_MAX;
const zOf = (i) => (i - (ROWS - 1) / 2) * ROW_GAP;
const easeInOut = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x < 0.5 ? 4 * x ** 3 : 1 - (-2 * x + 2) ** 3 / 2);
const sineInOut = (x) => -(Math.cos(Math.PI * Math.min(1, Math.max(0, x))) - 1) / 2;
const kg = (v) => Math.round(v).toLocaleString('en').replace(',', ' ');

if (CAPTURE) document.body.classList.add('capture');

// ------------------------------------------------------------ renderer ---
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(CAPTURE ? 1 : Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.95;
stage.appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer({ element: document.getElementById('labels') });

const scene = new THREE.Scene();
scene.background = new THREE.Color(C.bg);
scene.fog = new THREE.Fog(C.bg, 34, 78);

const camera = new THREE.PerspectiveCamera(34, 16 / 9, 0.1, 200);
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(1920, 1080), 0.42, 0.4, 0.32);
composer.addPass(bloom);
composer.addPass(new OutputPass());

scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x0b0e13, 0.9));
const sun = new THREE.DirectionalLight(0xffffff, 1.4);
sun.position.set(-10, 20, 14);
scene.add(sun);

// --------------------------------------------------------------- floor ---
const zFront = zOf(ROWS - 1) + 1.6;
const zBack = zOf(0) - 1.6;
const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(SPAN + 6, zFront - zBack + 4).rotateX(-Math.PI / 2),
  new THREE.MeshStandardMaterial({ color: C.panel, roughness: 1 }),
);
floor.position.set(0, -0.01, (zFront + zBack) / 2);
scene.add(floor);

const gridPts = [];
for (let d = 0; d <= data.days; d += 1) {
  const x = xOf(Math.min(d * 24, HOURS - 1));
  gridPts.push(x, 0, zBack, x, 0, zFront);
}
for (let i = 0; i < ROWS; i += 1) gridPts.push(-SPAN / 2, 0, zOf(i), SPAN / 2, 0, zOf(i));
const grid = new THREE.LineSegments(
  new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(gridPts, 3)),
  new THREE.LineBasicMaterial({ color: C.grid, transparent: true, opacity: 0.9 }),
);
scene.add(grid);

for (let d = 0; d < data.days; d += 1) {
  if (d % 7 < 5) continue;  // weekend bands
  const band = new THREE.Mesh(
    new THREE.PlaneGeometry(SPAN / data.days, zFront - zBack).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ color: C.bg_glow, transparent: true, opacity: 0.9, depthWrite: false }),
  );
  band.position.set(xOf(d * 24 + 12), 0.002, (zFront + zBack) / 2);
  scene.add(band);
}

function label(text, cls, pos, color) {
  const el = document.createElement('div');
  el.className = cls;
  el.textContent = text;
  if (color) el.style.setProperty('--c', color);
  const obj = new CSS2DObject(el);
  obj.position.copy(pos);
  scene.add(obj);
  return obj;
}
for (let d = 0; d < data.days; d += 1) {
  label(d % 7 >= 5 ? `D${d + 1} wknd` : `D${d + 1}`, 'day', new THREE.Vector3(xOf(d * 24 + 12), 0, zFront + 0.6));
}

// ---------------------------------------------------------------- rows ---
const resolution = new THREE.Vector2(1920, 1080);
const rows = data.compactors.map((c, i) => {
  const color = new THREE.Color(style.streams[c.stream].color);
  const z = zOf(i);
  const pos = [];
  const col = [];
  const idx = [];
  const top = [];
  c.mass_kg.forEach((m, h) => {
    const x = xOf(h);
    const y = yOf(m);
    pos.push(x, y, z, x, 0, z);
    col.push(color.r, color.g, color.b, 0.26, color.r * 0.3, color.g * 0.3, color.b * 0.3, 0.0);
    top.push(x, y + 0.005, z);
    if (h > 0) {
      const a = (h - 1) * 2;
      idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
    }
  });
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 4));
  g.setIndex(idx);
  const ribbon = new THREE.Mesh(g, new THREE.MeshBasicMaterial({
    vertexColors: true, transparent: true, side: THREE.DoubleSide, depthWrite: false,
  }));
  scene.add(ribbon);

  const lg = new LineGeometry();
  lg.setPositions(top);
  const line = new Line2(lg, new LineMaterial({ color, linewidth: 2.6, resolution }));
  scene.add(line);

  const markers = c.pickups.map((p) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(0.13, 20, 14),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(C.ink) }));
    m.position.set(xOf(p.hour), yOf(p.ticket_kg), z);
    m.visible = false;
    scene.add(m);
    return { ...p, mesh: m };
  });
  label(c.id, 'row-id', new THREE.Vector3(-SPAN / 2 - 1.5, 0.1, z), style.streams[c.stream].color);
  return { c, ribbon, line, markers };
});

// Time cursor: a faint vertical sheet plus a bright floor line.
const cursor = new THREE.Mesh(
  new THREE.PlaneGeometry(zFront - zBack, H_MAX + 0.6).rotateY(Math.PI / 2),
  new THREE.MeshBasicMaterial({ color: C.ink, transparent: true, opacity: 0.045, depthWrite: false, side: THREE.DoubleSide }),
);
scene.add(cursor);
const cursorLineGeo = new LineGeometry();
cursorLineGeo.setPositions([0, 0.01, zBack, 0, 0.01, zFront]);
const cursorLine = new Line2(cursorLineGeo, new LineMaterial({ color: new THREE.Color(C.teal), linewidth: 2, resolution }));
scene.add(cursorLine);

const ticketEl = document.createElement('div');
ticketEl.className = 'ticket';
const ticket = new CSS2DObject(ticketEl);
ticket.visible = false;
scene.add(ticket);

// --------------------------------------------------------------- HUD ----
const legend = document.getElementById('legend');
style.streams.forEach((s) => {
  const el = document.createElement('span');
  el.style.setProperty('--c', s.color);
  el.textContent = s.label;
  legend.appendChild(el);
});
const pickEl = document.createElement('span');
pickEl.style.setProperty('--c', C.ink);
pickEl.textContent = 'Pickup (weighbridge ticket)';
legend.appendChild(pickEl);
const $clock = document.getElementById('t-clock');
const $mass = document.getElementById('t-mass');
const $pick = document.getElementById('t-pick');

// -------------------------------------------------------- camera path ---
const camPath = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-30, 18, 38), new THREE.Vector3(-13, 13, 34),
  new THREE.Vector3(5, 12, 32), new THREE.Vector3(20, 15, 34),
]);
const lookPath = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-6, 1.0, -1), new THREE.Vector3(-2, 1.6, 0),
  new THREE.Vector3(3, 1.6, 0), new THREE.Vector3(4, 1.2, -1),
]);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enabled = false;
controls.enableDamping = true;

function hourAt(t) { return (HOURS - 1) * sineInOut((t - 0.5) / 9.6); }

function updateTicket(latest, hour) {
  if (!latest || hour - latest.hour >= 60) {
    ticket.visible = false;
    return;
  }
  const delta = ((latest.estimate_kg - latest.ticket_kg) / latest.ticket_kg) * 100;
  ticketEl.innerHTML = `${latest.row.id} pickup · ticket <b>${kg(latest.ticket_kg)} kg</b>`
    + ` · estimate ${kg(latest.estimate_kg)} kg <span class="d">${delta >= 0 ? '+' : '−'}${Math.abs(delta).toFixed(1)}%</span>`;
  ticket.position.copy(latest.mesh.position);
  ticket.visible = true;
  ticketEl.style.opacity = String(Math.min(1, (60 - (hour - latest.hour)) / 12));
}

function render(t, { moveCamera = true } = {}) {
  const hour = hourAt(t);
  const k = Math.max(1, Math.floor(hour) + 1);
  let inside = 0;
  let picks = 0;
  let latest = null;
  rows.forEach(({ c, ribbon, line, markers }) => {
    ribbon.geometry.setDrawRange(0, Math.max(0, (k - 1) * 6));
    line.geometry.instanceCount = Math.max(0, k - 1);
    inside += c.mass_kg[Math.min(HOURS - 1, Math.floor(hour))];
    markers.forEach((m) => {
      const age = hour - m.hour;
      m.mesh.visible = age >= 0;
      if (age < 0) return;
      picks += 1;
      m.mesh.scale.setScalar(1 + 2.2 * Math.exp(-age / 5));
      if (!latest || m.hour > latest.hour) latest = { ...m, row: c };
    });
  });
  const x = xOf(hour);
  cursor.position.set(x, (H_MAX + 0.6) / 2, (zFront + zBack) / 2);
  cursorLine.position.x = x;
  const fade = 1 - Math.min(1, Math.max(0, (t - 10.4) / 0.8));
  cursor.material.opacity = 0.022 * fade;
  cursorLine.visible = fade > 0.02;
  updateTicket(latest, hour);

  const day = Math.floor(hour / 24) + 1;
  const hh = Math.floor(hour % 24);
  $clock.textContent = `DAY ${String(day).padStart(2, '0')} · ${String(hh).padStart(2, '0')}:00`;
  $mass.textContent = `${(inside / 1000).toFixed(1)} t`;
  $pick.textContent = String(picks);

  if (moveCamera) {
    const u = easeInOut(t / DURATION);
    camera.position.copy(camPath.getPoint(u));
    const target = lookPath.getPoint(u);
    camera.lookAt(target);
    controls.target.copy(target);
  }
  composer.render();
  labelRenderer.render(scene, camera);
}

function resize(w, h) {
  renderer.setSize(w, h, false);
  renderer.domElement.style.width = '100%';
  renderer.domElement.style.height = '100%';
  composer.setSize(w, h);
  labelRenderer.setSize(w, h);
  resolution.set(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
resize(innerWidth, innerHeight);
addEventListener('resize', () => resize(innerWidth, innerHeight));

await document.fonts.ready;

if (CAPTURE) {
  window.__render = (t) => render(t);
  render(0);
  window.__ready = true;
} else {
  let t = 0;
  let playing = true;
  let last = performance.now();
  const $play = document.getElementById('play');
  const $scrub = document.getElementById('scrub');
  const $free = document.getElementById('free');
  $play.onclick = () => { playing = !playing; $play.textContent = playing ? 'Pause' : 'Play'; };
  $scrub.oninput = () => { t = ($scrub.value / 1000) * DURATION; };
  $free.onchange = () => { controls.enabled = $free.checked; };
  renderer.setAnimationLoop((now) => {
    const dt = (now - last) / 1000;
    last = now;
    if (playing) t = (t + dt) % (DURATION + 1.5);
    $scrub.value = String(Math.round((Math.min(t, DURATION) / DURATION) * 1000));
    if (controls.enabled) controls.update();
    render(Math.min(t, DURATION), { moveCamera: !controls.enabled });
  });
}
