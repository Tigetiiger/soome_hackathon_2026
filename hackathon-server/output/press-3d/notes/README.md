# Europress Combi: exploded view with sensor positions

A 16-second clip for the demo video (1920 × 1080, 30 fps, 480 frames). The Combi 20 m³
press-container comes apart, the sensors light up one by one with honest position labels,
the ram strokes into the container mouth while an illustrative pressure curve rises, and the
machine goes back together.

- Video: `out/combi_exploded_sensors.mp4` (H.264, CRF 18, yuv420p, +faststart)
- Poster frame: `out/poster.jpg` (t = 10.95 s, ram 25 cm into the mouth). 6-frame contact sheet: `out/contact_sheet.jpg`
- QC: `qc/compare_side.png`, `qc/compare_top.png` (render vs brochure drawing),
  `qc/01_assembled.png`, `qc/02_exploded.png`, `qc/02b_sensors_hold.png`, `qc/03_sensor_closeup.png`,
  `qc/04_side_ortho_3d.png`, `qc/05_top_ortho_3d.png`
- Blender files: `combi.blend` (static model in named collections) and `combi_animated.blend`
  (the same model with the camera and every keyframe of the clip). Both open in Blender 5.2.
- Dimensions and their sources: `notes/dimensions.md`

## Re-rendering

```bash
cd /home/hackathon/output/press-3d
nohup setsid ./render.sh > logs/render.log 2>&1 &   # resumable; re-run to continue
FRESH=1 ./render.sh        # rebuild the model, delete all frames, start over
ENCODE_ONLY=1 ./render.sh  # composite + encode whatever 3D frames exist (partial clip)
OVERLAY=1 ENCODE_ONLY=1 ./render.sh   # after editing label copy/layout: re-composite only
SAMPLES=16 WORKERS=2 ./render.sh      # defaults (threads per worker = nproc / WORKERS)
```

Pipeline (each step skips finished work):

| step | script | output |
|---|---|---|
| 1. model | `build_combi.py` (bpy) | `combi.blend` |
| 2. animation + label anchors | `animate_combi.py --anchors --save-blend` | `out/anchors.json`, `combi_animated.blend` |
| 3. 3D pass | `animate_combi.py --render --worker k --workers n` | `out/frames3d/fNNNN.png` (frames 1–451) |
| 4. overlay | `compose_overlay.py --frames` (Pillow) | `out/frames/fNNNN.png` (1–480) |
| 5. encode | ffmpeg | `out/combi_exploded_sensors.mp4` |
| 6. poster + sheet | `compose_overlay.py --sheet` | `out/poster.jpg`, `out/contact_sheet.jpg` |
| QC | `animate_combi.py --qc`, `compose_overlay.py --qc`, `qc_compare.py` | `qc/*` |

`timeline.py` holds the storyboard timing and is shared by the Blender and Pillow scripts.
Frames 452–480 (the closing card) reuse 3D frame 451, because nothing moves after t = 15 s.

Interpreters: Blender scripts use `../animation-comparison/.venv-blender/bin/python` (bpy 5.2.3).
Overlay and QC use `../animation-comparison/.venv/bin/python` (Pillow 13 + numpy). Nothing
was installed on the VM.

## Labels: why a 2D overlay (option 2)

The 3D pass is rendered without text. Labels, leader lines, confidence tags, the "schematic"
caption, the pressure-curve inset and the closing card are composited afterwards with Pillow.
We chose this because:

- the copy and layout can change in seconds (`OVERLAY=1 ENCODE_ONLY=1 ./render.sh`) without
  re-running about an hour of Cycles;
- text stays pixel-crisp at the required ≥ 28 px sizes, and labels sit in fixed screen columns
  where they cannot intersect geometry;
- leader lines still track the 3D parts exactly. `animate_combi.py` exports the Blender
  camera projection of every sensor anchor for every frame, plus a ray-cast visibility flag, so
  after reassembly a hidden sensor is drawn as a ring ("inside the machine") and a visible one
  as a filled dot.

## What comes from the drawing, and what is schematic

**From the drawing (exterior).** Overall outline and every exterior part position come from the
side and top views on page 2 of the Combi brochure: 6,520 / 4,090 / 2,500 / 2,350 / 1,720 /
2,650 + wheels / 1,480 + wheels 30 / infeed 1,500 × 900, plus about 60 measured positions (posts,
lid line, ribs, door profile, rollers, roof ribs, hatch, bail, lock handles, lettering). The
full table with sources is in `notes/dimensions.md`.

**Schematic (interior), labelled on screen.** The ram block, two double-acting telescopic
cylinders, power unit (tank, motor, pump, valve block), control box, hoses and wiring.
Whenever internals are visible, the caption "Internal layout: schematic, not Europress CAD"
is on screen (3.1 s – 14.95 s).

**Sensor positions.**
- Confirmed by Europress material:
  - load cells, one at each corner of the SMART Scale platform (Scale brochure);
  - ram entry of 20–30 cm into the container (Europress product specialist).
- Schematic, tagged "position schematic": pressure transducer, GPS/5G module, tilt/movement
  sensor, door interlock switch, hopper lid switch.
- Our proposal, tagged "proposed": the ~€30 oil temperature probe.

**Not used.** No Europress CAD, no third-party models, no part numbers, no sensor model names,
no logo mark. The container carries only plain "EUROPRESS" type, set in IBM Plex.

The pressure curve in the inset is **illustrative and unitless**: friction until the ram face
reaches the container mouth, then a steep rise against the pack. It is not measured data.

## Storyboard as built

| time | content |
|---|---|
| 0 – 3 s | assembled Combi on the scale platform, slow three-quarter orbit from the front-left; title "Europress Combi · 20 m³" |
| 3 – 7 s | exploded view, eased (smootherstep): lid lifts 1.15 m, top service cover lifts 0.75 m, near side panel (with control panel and hopper cheek) slides out 2.4 m, container slides back 2.3 m, rear door swings 95° and moves back 0.6 m, machine lifts 0.6 m off the scale platform |
| 7 – 12 s | sensors light up teal one by one (every 0.33 s), each with a leader line, a one-line use note and a confidence tag. The ram strokes once (9.7 – 11.0 s out, 11.25 – 12.0 s back) past a ghost outline of the container mouth; the inset draws the pressure curve |
| 12 – 15 s | reassembly in reverse order; labels fade; every sensor stays as a small glowing dot (filled = visible, ring = inside the machine) |
| 15 – 16 s | closing card: "Exterior dimensions from the Europress Combi brochure (20 m³). Internal layout and most sensor positions are schematic." |

## Render settings and time

- Cycles on the CPU, 16 samples (adaptive, threshold 0.02) + OpenImageDenoise. Bounces: diffuse
  2, glossy 3, transmission 0. Standard view transform, so the background is exactly #0E1218.
- 2 worker processes × 18 threads on the 36-core VM. Each worker renders the frames that are
  still missing, interleaved between the two.
- **Time as delivered: ≈ 67 min of 3D rendering for 451 frames.** First pass: 3,528 s (58.8 min,
  ≈ 7.8 s/frame overall). Then 60 frames were re-rendered (476 s, ≈ 7.9 s/frame overall);
  see below. Overlay compositing of 480 frames takes about a minute on 16 processes, and the
  ffmpeg encode a few seconds.
- A clean run with the current settings needs about 59 min: 451 frames at ≈ 15.7 s per frame
  per worker.

**Render issue found in review, and the fix.** The first pass used Cycles' persistent data.
From frame 333 onwards, one of the two worker processes produced stale shading on every frame
it rendered: the chamber floor and liner came out pure black (48 frames, odd numbers
333–427). We found this by scanning every frame for pure-black pixels. A diff against fresh
single-frame renders confirmed it: the fresh renders were bit-identical everywhere else.
Persistent data is now switched off in `animate_combi.py`. The odd frames 333–451 were deleted
and re-rendered, and a rescan finds no outliers. The thin dark line on the container's front
wall at t ≈ 4.6 s is not a fault: it is the lifted lid's shadow (checked with a ray cast).

## QC against the drawing

`qc/compare_side.png` and `qc/compare_top.png` put the brochure drawing and our orthographic
render side by side. Below them is a 1:1 overlay: the ortho camera uses 3.927 mm per pixel, so
the drawing linework (coral) lands on the render with no fitting. Outline, posts, lid line,
ribs, door profile, rollers, roof ribs, infeed opening and hatch all register to within a few
pixels (≈ 10–20 mm).

Known differences:
- The "EUROPRESS" lettering is plain IBM Plex type stretched to the measured span. It is not
  the brand typeface, and the logo mark is deliberately left out.
- The rear centre lug is a simple block; the top view shows a wider curved handle.
- Door lock hardware (wedge locks, lever hooks) and the front roller housings are simplified.
- Hook-lift rail spacing, front cross-beam height and every platform section are not in the
  drawing. They are schematic.
- The drawing's rounded rectangle on the press side (a bolted cover) is used as the
  control-panel position. The brochure photo shows the panel in that band, but on a
  differently configured machine.

## Environment notes

- The VM has no PDF rasteriser. Page 2 was rasterised at 400 dpi with PyMuPDF on the
  presenter's laptop, and the crops were copied to `qc/ref_drawing_side_400dpi.png` and
  `qc/ref_drawing_top_400dpi.png`.
- `PROMPT_press_exploded_animation.md`: rule 5 is retitled "No official-looking logo", as
  requested. The text of the rule is unchanged.
