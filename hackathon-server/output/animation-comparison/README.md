# Animation library comparison: 3Blue1Brown-style maths and 3D visuals

Five libraries, five rendered demos, one shared visual style. See **[COMPARISON.md](COMPARISON.md)** for the
results and recommendations. Open **[index.html](index.html)** for the side-by-side gallery.

| Demo | Library | What it shows | Output |
|---|---|---|---|
| Technical diagram | **Manim Community 0.22.1** (Cairo) | Compactor cross-section: ram force, pressure transducer, load cells, ultrasonic fill sensor → mass estimate | `media/manimce_compactor_diagram.mp4` |
| 3D maths surface | **ManimGL 1.7.2** (3b1b's library) | Calibration surface m̂(fill, pressure; ρ) morphing with ρ, orbiting camera, tracked point with live readout | `media/manimgl_calibration_surface.mp4` |
| 3D scatter | **PyVista 0.49 / VTK 9.7** | 554 lifts rise into place, colour by stream, anomalies pulse, 2σ covariance ellipsoids | `media/pyvista_lift_scatter.mp4` |
| Time-series data viz | **three.js r170** | 14 days × 6 compactors as glowing ribbons, sweeping time cursor, pickup tickets vs estimates | `media/threejs_fleet_timeseries.mp4` + interactive `demos/threejs/index.html` |
| Same surface, path-traced | **Blender 5.2 (bpy) Cycles** | The ManimGL surface with studio lighting and clear-coat material | `media/blender_calibration_surface.mp4` (partial: 142/240 frames, resumable) |

All data is synthetic and reproducible (`shared/mockdata.py`, seed 2026). It is loosely themed on the
Europress "virtual scale" idea from `input-files/`, but it is **not** measurement data.

## Layout

```
animation-comparison/
├── COMPARISON.md          research + experimental comparison + recommendations
├── index.html             gallery (side-by-side videos)
├── media/                 final MP4s + poster frames
├── shared/style.json      palette, fonts, resolution, fps (single source of truth)
├── shared/mockdata.py     reproducible mock data (seed 2026)
├── data/*.json            exported data for the JS demo
├── assets/fonts/          IBM Plex Sans/Mono TTF (SIL OFL), used by every demo
├── demos/<library>/       source + render.sh per demo
├── render_all.sh          renders everything sequentially and records timings
└── logs/timings.txt       measured wall-clock render times
```

## Install

### On a normal workstation (recommended)

```bash
# system packages (Debian/Ubuntu); macOS: brew install cairo pango pkg-config ffmpeg
sudo apt install build-essential python3-dev pkg-config libcairo2-dev libpango1.0-dev ffmpeg
# optional, for MathTex/Tex in Manim:  sudo apt install texlive-latex-extra dvisvgm

python3 -m venv .venv && .venv/bin/pip install manim pyvista imageio imageio-ffmpeg fonttools
python3 -m venv .venv-gl && .venv-gl/bin/pip install manimgl "setuptools<81" audioop-lts
python3 -m venv .venv-blender && .venv-blender/bin/pip install bpy==5.2.3 numpy  # needs Python 3.13
(cd demos/threejs && npm install)              # three, playwright-core, IBM Plex
npx playwright install chromium-headless-shell # only needed for MP4 capture of the three.js demo
mkdir -p bin && ln -sf "$(.venv/bin/python -c 'import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())')" bin/ffmpeg
```

Fonts: the demos use IBM Plex. `assets/fonts/*.ttf` are included. Manim/Pango find fonts through
fontconfig, so copy them once: `cp assets/fonts/*.ttf ~/.local/share/fonts/ && fc-cache -f`.

### What was needed in this sandbox (no sudo, no GPU, no LaTeX, no ffmpeg)

* **pycairo / manimpango** have no Linux wheels and need cairo/pango/Python headers. The headers were fetched
  without root via `apt-get download libcairo2-dev libpango1.0-dev libglib2.0-dev libgio-2.0-dev libharfbuzz-dev
  libfreetype-dev libfontconfig-dev libpixman-1-dev libpng-dev libfribidi-dev libpython3.13-dev`, unpacked with
  `dpkg -x` into `~/.local/devroot`, and exposed through a minimal `pkg-config` stand-in script. The XCB/Xlib
  surfaces were disabled in the local `cairo-features.h`, because the X11 headers were not installed.
* **ffmpeg**: the static binary shipped inside `imageio-ffmpeg`, symlinked to `bin/ffmpeg`. Manim CE itself
  uses PyAV, which bundles its own ffmpeg libraries.
* **OpenGL without a display**: Mesa's llvmpipe through EGL.
  * ManimGL: `demos/manimgl/render_headless.py` forces `moderngl.create_standalone_context(backend="egl")` and `PYGLET_HEADLESS=1`.
  * PyVista: `VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow`.
  * three.js: headless Chromium with SwiftShader.
  * Blender: Cycles on the CPU. EEVEE runs, but at about 100 s per frame on llvmpipe.
* **No LaTeX**, so every formula is set with Pango text (`Text`/`MarkupText`) instead of `MathTex`.

## Render

```bash
./render_all.sh                    # all demos, sequential, writes media/ and logs/timings.txt
python3 finalize.py                # fills timings into COMPARISON.md + index.html, makes posters
demos/manimce/render.sh            # or one at a time
demos/manimgl/render.sh            #   (-l for a quick 480p preview, -s for the last frame only)
demos/pyvista/render.sh
demos/threejs/render.sh            # node capture.mjs --still 7  → single PNG
demos/blender/render.sh           # 1080p Cycles on CPU, RESUMES: skips frames already in out/frames/
                                   #   (98 frames left, ~17 min on 16 cores). FRESH=1 restarts, ENCODE_ONLY=1 just encodes
```

## View

* Gallery: open `index.html` directly in a browser. It only plays local MP4s.
* Interactive three.js demo: ES modules need HTTP, so run `./serve.sh` and open
  <http://localhost:8000/demos/threejs/index.html>. It has play/pause, a timeline scrubber and a free orbit camera.
