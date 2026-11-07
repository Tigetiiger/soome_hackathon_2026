# Comparison: tools for 3Blue1Brown-quality maths animations, 3D diagrams and 3D data viz

**Question:** Which tool produces the most impressive visuals with the least development effort, for
(a) high-quality presentation videos, (b) 3D mathematical explanations, (c) interactive 3D data visualisation?

**Method:** five libraries, one real rendered demo each. All demos use the same palette, the same typeface
(IBM Plex Sans/Mono), 16:9 framing at 1920×1080, 30 fps, and reproducible synthetic data (`shared/`). Every
video was rendered, inspected frame by frame (contact sheets), fixed, and re-rendered. The final renders ran
**one after another** on the same machine so the timings can be compared (`render_all.sh` → `logs/timings.txt`).

**Test machine:** 16 vCPU Intel Xeon E5-2680 v3, 16 GB RAM, **no GPU** (Mesa llvmpipe / SwiftShader software
OpenGL), no sudo, no LaTeX, no system ffmpeg. Development started on a 4-vCPU instance of the same VM; numbers
from that phase are labelled "4 cores". For the GPU-based tools this is a worst case. The workstation numbers
further down are marked as estimates and were not measured.

---

## 1. Results at a glance

| | Manim CE | ManimGL | PyVista | three.js | Blender (bpy) |
|---|---|---|---|---|---|
| Demo | Technical diagram (sensors, forces) | 3D surface, morphing parameter, orbit | 3D scatter, clusters, ellipsoids | Time-series ribbons, interactive | Same surface as ManimGL, path-traced |
| Output | MP4, 14.1 s | MP4, 12.7 s | MP4, 12.0 s | MP4, 12.0 s **+ live HTML** | MP4, 4.7 s (**partial**: 142 of 240 frames) |
| **Measured render time** | **80 s** | **3 min 16 s** | **65 s** | **2 min 49 s** (capture) | **24 min 44 s** for 142 frames |
| Per frame | 0.19 s | 0.52 s | 0.18 s | 0.47 s | 10.45 s |
| Code (non-blank, non-comment lines) | 199 | 144 (+11 headless shim) | 150 | 321 JS+HTML (+72 capture) | 273 |
| Visual quality, 2D diagrams | ★★★★★ | ★★★★☆ | ★★☆☆☆ | ★★★☆☆ | ★★★☆☆ |
| Visual quality, 3D | ★★☆☆☆ (Cairo) | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| Typography / formulas | ★★★★★ with LaTeX | ★★★★★ with LaTeX | ★★☆☆☆ | ★★★★★ (HTML/CSS) | ★★★☆☆ |
| Ease of impressive results | High | Medium | High for sci-vis | Medium | Low |
| Docs and API stability | Excellent | Poor (source is the doc) | Excellent | Good, but churn across revisions | Good, but churn across versions |
| Interactive output | No (video) | Interactive window only | Desktop window; HTML via trame | **Yes, native, in any browser** | No (viewport only) |
| Needs a GPU to be fast | No | Yes | Helps | Yes (any) | **Yes, strongly** |
| Fit for AI-assisted work (Claude Code) | Best | Risky | Very good | Very good | Moderate |

Star ratings are my judgement from these demos and are subjective. Times and line counts were measured.

## 2. Library by library

### Manim Community (CE) v0.22.1: `demos/manimce/diagram.py`

*What it is:* the community fork of 3b1b's library, forked in mid-2020. The official docs describe it as more
stable, better tested and documented, and recommend it for beginners. It renders with Cairo (CPU, vector,
antialiased); an OpenGL renderer can be selected with `--renderer=opengl`.
([docs FAQ](https://docs.manim.community/en/stable/faq/installation.html))

*Experience:*
* The fastest route to a polished explainer. `ValueTracker` and `always_redraw` drive live readouts, a gauge
  needle, a moving ram and force arrows in a few lines. `LaggedStart`, `Create`, `Write` and `GrowArrow` give
  the "3b1b feel" for free.
* It needs no GPU at all: 80 s for 423 frames (0.19 s per frame), the same speed per frame as PyVista and
  among the fastest here. It also took 80 s on 4 cores: the Cairo renderer is effectively single-threaded,
  so extra cores do not help.
* Tight feedback loop: `-s` renders only the last frame in about 7 s, which was enough to fix layout problems
  (gauge overlapping the result box, a label crossing the container wall) before a full render.
* Without LaTeX, `MathTex` and `DecimalNumber` (which uses LaTeX internally) are unavailable. Formulas were set
  with Pango `MarkupText` (`R<sub>1</sub>`), and numbers with `always_redraw(Text)`. With a TeX install you get
  real typeset maths, the biggest single quality gain for maths content.
* Weakness is 3D. The Cairo renderer has no depth buffer or lighting model: `ThreeDScene` surfaces are
  painter's-algorithm polygons and slow at high resolution. The OpenGL renderer is faster but has historically
  covered fewer features (see §6).

### ManimGL v1.7.2: `demos/manimgl/surface.py`

*What it is:* Grant Sanderson's own, OpenGL-based library (`pip install manimgl`, `import manimlib`). The
official Manim docs say it "has more experimental features and breaking changes between versions are not
documented". Its README lists FFmpeg, OpenGL and (optionally) LaTeX as requirements.
([3b1b/manim README](https://github.com/3b1b/manim))

*Experience:*
* The most "3Blue1Brown" 3D output: GPU-shaded parametric surfaces with gloss, `GlowDot`, `fix_in_frame` HUD
  text, and `frame.reorient()` / `add_ambient_rotation()` for a smooth orbiting camera.
* API knowledge had to come from the installed source: the `get_graph` signature, `set_rgba_array` for
  vectorised vertex colours, `frame.get_orientation()` for camera-facing labels, and CLI flags. CE examples
  and old `manimlib` code look similar but do not run. This is the main risk for AI-assisted work.
* Headless rendering needed an 11-line shim (`render_headless.py`): force
  `moderngl.create_standalone_context(backend="egl")` and set `PYGLET_HEADLESS=1`. It also needed
  `setuptools<81` (manimlib still imports `pkg_resources`) and `audioop-lts` (pydub on Python 3.13).
* Render: 3 min 16 s for 381 frames on **software** OpenGL. Most of the time goes to rebuilding a 72×72
  surface and its mesh every frame (`always_redraw`) and to llvmpipe. On a GPU, ManimGL previews
  interactively in real time; a final render of this clip should take well under a minute (estimate).
* QC fixes needed: axis labels mirrored or edge-on in 3D (fixed with camera-facing billboard labels), labels
  hidden under the semi-transparent surface (fixed by draw order), the z-axis occluded (moved to the back
  corner), and camera framing.

### PyVista 0.49 (VTK 9.7): `demos/pyvista/scatter.py`

*What it is:* a Pythonic wrapper around VTK, the scientific visualisation toolkit. It offers meshes, glyphs,
volumes, PBR materials, SSAA/FXAA, SSAO, movies via imageio-ffmpeg, and interactive HTML export via trame.
([docs](https://docs.pyvista.org))

*Experience:*
* For data-driven 3D it gives the most quality per line: `cloud.glyph(geom=sphere, scale=...)`, `pbr=True`,
  `enable_anti_aliasing("ssaa")` and a gradient background produce a clean, lit scene. Covariance ellipsoids
  are a transformed `pv.Sphere`.
* There is no animation framework. Timing, easing, staggering and camera paths are a hand-written frame loop
  (`write_frame()`): easy with NumPy, but all your own code.
* Typography is the weak point. VTK text actors accept a TTF file, but layout is manual pixel positions, and
  glyphs missing from the font (●) are silently dropped. It cannot match Manim or HTML for annotation-heavy
  scenes.
* Headless rendering worked first time with the stock VTK 9.7 wheel via
  `VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow`. Render: 65 s (SSAA plus about 550 glyph spheres
  rebuilt every frame on llvmpipe).
* QC fixes needed: ellipsoids too faint (raised opacity, enabled depth peeling), a clipped corner tag, and the
  missing legend glyph.

### three.js r170 (WebGL): `demos/threejs/`

*What it is:* the dominant WebGL scene-graph library. React Three Fiber (R3F) is a React renderer on top of
three.js with the same rendering capability, so this demo stands in for both.
([three.js docs](https://threejs.org/docs/), [R3F docs](https://r3f.docs.pmnd.rs))

*Experience:*
* It is the only tool where one artefact is both a video and an interactive page: play/pause, timeline scrub
  and a free orbit camera (`OrbitControls`). In a normal browser it runs in real time.
* Polish is cheap once set up: `UnrealBloomPass` glow, ACES tone mapping, fog for depth, `Line2` for thick
  lines, vertex-alpha gradient ribbons. HUD, labels and tooltips are plain HTML/CSS (`CSS2DRenderer`), so
  typography is as good as any website.
* MP4 export is not built in. `capture.mjs` (72 lines) serves the folder, drives headless Chromium frame by
  frame through a deterministic `window.__render(t)`, and pipes screenshots to ffmpeg. That makes frame timing
  exact regardless of machine speed. Capture: 2 min 49 s with SwiftShader (CPU WebGL).
* It needed the most code of the five, because there are no maths primitives: no axes, ticks, LaTeX, or
  `Create`-style stroke animations. Everything is geometry you build. API churn across revisions (addon import
  paths, colour management, `Line2` resolution handling) means version-pinned examples matter.
* QC fixes needed: overexposure from stacked translucent ribbons plus bloom (lowered alpha, bloom and exposure)
  and camera distance.

### Blender 5.2 (bpy, Cycles): `demos/blender/surface.py`

*What it is:* a full 3D content-creation suite. `pip install bpy` gives the whole of Blender as a Python module
(a 384 MB wheel for Python 3.13). Cycles is a path tracer; EEVEE is a rasteriser.
([bpy on PyPI](https://pypi.org/project/bpy/), [Python API](https://docs.blender.org/api/current/))

*Experience:*
* It produced the most photographic frames: soft area-light highlights, clear-coat reflections and real light
  falloff on the floor. The same surface as ManimGL becomes a product shot. Shape keys morph the surface, and
  text objects parented to the camera act as the HUD.
* Highest effort: building a shader node graph in Python is verbose (273 lines for one surface). Socket names
  change between versions (Principled BSDF "Coat Weight"), and the animation/action API changed in 4.4/5.x.
  I keyframed every frame explicitly to stay version-proof.
* Slowest by far without a GPU. 1080p at 16 samples with OIDN denoising took **44 s per frame on 4 cores** and
  10.45 s on 16 cores. The render was **stopped on request after 142 of 240 frames** (24 min 44 s),
  so the clip shows the first 4.7 s: the surface growing and morphing toward cardboard. The render is resumable:
  `demos/blender/render.sh` skips finished frames, so running it again renders only the remaining 98 frames
  (about 17 min here) and re-encodes the full 8 s clip. EEVEE on llvmpipe took about 100 s per frame on 4 cores,
  which is unusable. With a modern NVIDIA GPU (OptiX), frames like these typically take 1–3 s each
  (estimate, not measured).

## 3. Rendering speed and hardware

Measured on the 16-vCPU VM, sequential, wall-clock including start-up and encoding:

| Library | Frames | Resolution | Total | Per frame | Bottleneck here |
|---|---|---|---|---|---|
| Manim CE (Cairo) | 423 | 1920×1080 | 80 s | 0.19 s | CPU vector rasterising: no GPU needed |
| ManimGL | 381 | 1920×1080 | 3 min 16 s | 0.52 s | software OpenGL + per-frame mesh rebuild |
| PyVista | 360 | 1920×1080 | 65 s | 0.18 s | software OpenGL, SSAA (4× pixels) |
| three.js | 360 | 1920×1080 | 2 min 49 s | 0.47 s | SwiftShader WebGL + one PNG screenshot per frame |
| Blender Cycles | 142 of 240 (stopped) | 1920×1080 | 24 min 44 s | 10.45 s | CPU path tracing (16 spp + OIDN denoise) |

Manim CE and PyVista were the fastest (~0.2 s per frame) and both are usable without a GPU. They scale
differently: Manim CE took 80 s on both 4 and 16 cores (single-threaded Cairo), while PyVista went from
194 s on 4 cores to 65 s on 16 (Mesa llvmpipe spreads software OpenGL across cores). ManimGL and three.js
run in real time on any GPU but are 2–3× slower than those two in software. Blender needs a GPU for fast
1080p iteration: 10.5 s per frame on 16 CPU cores, 44 s on 4.

## 4. MP4/GIF vs interactive HTML

| | Video (MP4/GIF) | Interactive |
|---|---|---|
| Manim CE | Native (`-qh`, `--format=gif`) | No; Manim Slides adds click-through presentations |
| ManimGL | Native (`-w`) | A live window with an embedded IPython shell, not a shareable web page |
| PyVista | `open_movie` / `open_gif` | Desktop window; `export_html` / trame for the browser |
| three.js | Needs a capture harness (here Playwright + ffmpeg; in-browser: MediaRecorder/CCapture) | **Native in any browser, mobile included** |
| Blender | Native (frames → ffmpeg) | No; glTF export to three.js is the usual bridge |

Any of these can produce a GIF by running the MP4 through ffmpeg. GIF suits these scenes poorly, because
gradients and glow band badly in 256 colours, so MP4 or WebM is recommended.

## 5. Suitability for AI-assisted development (Claude Code)

What actually happened in this experiment:

* **Manim CE:** correct code on the first attempt, apart from layout tweaks. The API is stable and heavily
  represented in docs and examples, and the `-s` last-frame preview gives a 7-second visual feedback loop that
  suits an agent inspecting PNGs.
* **ManimGL:** required reading the installed source for signatures and behaviour. The main trap is mixing up
  CE, ManimGL and the old `manimlib` APIs, which look alike. Tell the agent which one, and have it grep the
  installed package rather than trust memory.
* **PyVista:** predictable and well documented. Off-screen rendering to PNG and MP4 makes visual QC easy.
* **three.js:** a huge corpus, but version-sensitive. Pin the version (r170 here) and use addons from the same
  package. A deterministic `__render(t)` plus headless capture made the browser demo as testable as the
  Python ones.
* **Blender:** works, but each iteration is slow (12–45 s per QC frame on CPU), and node and animation API
  names drift between 4.x and 5.x. Use it for a few hero shots, not for iterating on many scenes.

Universal lesson: give every demo a "render one frame at time t" mode. All five have one (`-s`, `--still`,
`DEMO_DURATION`), and that is what makes visual QC by an agent practical.

## 6. Other alternatives (researched, not built)

* **React Three Fiber + drei:** three.js in React. Same visuals with less boilerplate and better app
  integration; the pick if the visual lives inside a React dashboard.
* **Remotion:** renders React components to MP4 and can host R3F scenes (`@remotion/three`). It closes
  three.js's biggest gap, video export, with a proper timeline.
* **Motion Canvas:** TypeScript, generator-based animation with an editor and timeline. Excellent for 2D
  explainers and code animations; 2D only.
* **Manim Slides:** turns Manim CE/GL scenes into click-through presentations.
* **Plotly (Python/JS):** interactive 3D scatter and surfaces in minutes, exported as standalone HTML. It looks
  like a chart library and is hard to make cinematic, but is ideal for a quick interactive appendix.
* **Matplotlib 3D / Mayavi:** easy but default-looking; Matplotlib's 3D is a 2D painter's projection. Mayavi
  is VTK-based and largely superseded by PyVista.
* **VisPy / Datoviz:** GPU high-performance scientific plotting for millions of points. Low-level, less
  polished output.
* **Theatre.js:** a keyframe and timeline editor for three.js/R3F scenes. Worth adding when many hand-tuned
  camera moves are needed.

The Manim CE OpenGL renderer status could not be confirmed from current official docs. Community sources from
2024–2025 describe an "experimental" rewrite moving toward OpenGL, with no fixed timeline.

## 7. Recommendations

| Goal | Recommendation | Why (from these demos) | Runner-up |
|---|---|---|---|
| **High-quality presentation videos** | **Manim Community** (install LaTeX) | Best quality per hour of effort: crisp diagrams and typography, a stable API, a fast render with no GPU, and the best fit for AI-assisted iteration. | **Blender** for one or two cinematic hero shots, when a GPU is available |
| **3D mathematical explanations** | **ManimGL** | The genuine 3Blue1Brown 3D look (shaded surfaces, glow dots, smooth orbit), real-time preview on a GPU, and the same idioms as CE. Pin the version and read its source. | Manim CE with `--renderer=opengl`, if API stability matters more than the last 10% of the look |
| **Interactive 3D data visualisations** | **three.js** (via React Three Fiber in a React app) | The only option where the same scene is a shareable, real-time web page and, with a capture harness, also a video. HUD typography via HTML is the best of the five. | **PyVista** for Python-first scientific workflows (quick HTML export via trame) |

**Single pick for "most impressive with least effort":** Manim CE for anything explanatory, plus three.js
whenever interactivity matters. Use Blender only when photorealism is the point and a GPU is available.

## 8. Limitations of this comparison

* No GPU. ManimGL, PyVista, three.js and Blender are all slower here than on a workstation. GPU figures are
  estimates and were not measured.
* No LaTeX. The Manim formulas used Pango text, so neither Manim variant shows its best typesetting.
* One demo per library, on different scene types, as the brief asked. ManimGL vs Blender is the only
  like-for-like scene. The star ratings are subjective.
* The Blender clip is partial (4.7 s of the planned 8 s): the render was stopped on request after 142 of 240
  frames. Run `demos/blender/render.sh` to resume it.
* Data is synthetic (`shared/mockdata.py`). It illustrates the Europress virtual-scale idea and does not
  validate it.
