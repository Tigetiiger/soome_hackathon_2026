# Task: an exploded-view animation of a Europress Combi waste compactor, showing where its sensors are

## Background (you have no other context)

This is for a hackathon, Europress × Since AI 2026 in Turku, Finland.

- **Europress** is a Finnish company that makes waste compactors. A compactor is a machine that presses waste into a container at a shop, hotel or factory. Its connected service, SMART, reports how full each machine is.
- **Our team's idea** is a "soft sensor". It estimates the **weight** of the waste inside from signals the machine already has, mainly the hydraulic ram pressure, so the customer no longer has to trust the waste hauler's weighbridge figure.
- **This animation** goes into a 2-minute demo video for the judges. It must show the machine being taken apart, where its sensors physically sit, and the machine being put back together.

**There is no CAD or 3D model from Europress, and none exists publicly.** You must build the model yourself from the published dimension drawing below. The outside must match the drawing. The inside is not public, so it must be shown honestly as a schematic (see "Honesty rules"). Do not search for or download third-party 3D models of other brands' machines.

## Reference material (read these first)

All in `/home/hackathon/output/press-3d/refs/`:

- `Europress-Combi-product-brochure_ENG.pdf`: **the main reference.** Page 2 has a side and top dimension drawing of a Combi with a 20 m³ container, plus a photo (look at it with your PDF/image reading tool).
- `Europress-Combimax-product-brochure_ENG-1.pdf`, `Europress_DuoMax_brochure_ENG.pdf`, `Europress-Retrofit-brochure-ENG.pdf`: these give extra exterior views.
- `Europress_Scale-Solutions_brochure_ENG.pdf`: a CAD wireframe of a compactor on a weighing platform. It has a photo of one corner load cell, and it says "four sensors… each corner of the scale platform has its own separate weighing sensor". It also shows a firmware screen with a "Front Turn Pressure (bar) 185" setting.

Quotes from a Europress product specialist (briefing transcript):
- "there is the horizontal ram … the block that moves, pushes the material into the container. And the ram moves only, let's say, 20 to 30 centimeters inside the container"
- back pressure "starting from the 5 to 10% of the fill level … then it packs, packs, packs until the whole container is totally full"
- "we will rely on the pressure only" (fill level is derived from hydraulic back pressure; there is no separate level sensor)

Other facts:
- Machines also have "a tilt sensor", "GPS location, the movement sensors, so we know when they have transported".
- The practice data logs **door interlock** faults.

## Known dimensions (Combi, 20 m³; from the brochure drawing and spec table)

**Overall:**

| Item | Value |
|---|---|
| Overall length | max 6,520 mm |
| Container body length | 4,090 mm (the drawing shows "4090" over the container) |
| Overall width | max 2,500 mm |
| Container width | 2,350 mm |
| Press-section width | 1,720 mm |
| Height | 2,650 mm + wheels |
| Infeed (loading) height | 1,480 mm + wheels (1,300 mm side infeed on the lowered version) |

**Infeed opening:**
- net 1,500 mm long × 900 mm wide (top view: 1500 × 900);
- gross 1,450 × 1,510 mm with hopper.

**Performance and equipment:**
- Compaction force 25 t, cycle time 42 s, motor 5.5 kW, 400 V.
- The press section and container are one unit, lifted together by the truck (hook-lift / roll-off style). It has lifting hooks at the front and rear and rollers or wheels underneath.
- The rear discharge door has locking handles.
- A sloping hopper lid with a gas strut sits over the infeed. The control panel (key switch and emergency stop) is on the side of the press section, below the lid.
- Colour is Europress blue (approximately `#1F4FA0`; match the photo).

**Measuring from the drawing:** where you measure a dimension yourself rather than reading it, write it down as "measured from drawing". The drawing is to scale, so you can measure proportions from the page image.

## Sensors to show, each with an honest position label

| # | Sensor | Where to place it | Confidence label (shown on screen) |
|---|---|---|---|
| 1 | Hydraulic pressure transducer | On the valve block of the hydraulic power unit inside the press section | "position schematic" |
| 2 | Ram and its 20–30 cm entry into the container | Ram face moving from the press chamber into the container mouth | "per Europress" |
| 3 | Load cells × 4 (optional SMART Scale platform) | One at each corner of a platform frame under the whole machine, same length as the machine | "per Europress brochure" |
| 4 | GPS / 5G SMART module | Behind the control panel | "position schematic" |
| 5 | Tilt and movement sensor | In the control box | "position schematic" |
| 6 | Door interlock switch | On the rear discharge door frame | "position schematic" |
| 7 | Hopper lid switch | At the hopper lid hinge | "position schematic" |
| 8 | Oil temperature probe (our proposed add-on, about €30) | In the hydraulic oil tank | "proposed" |

Each sensor gets a short label with a leader line, and a one-line note on what its signal is used for. Examples:
- Pressure transducer: "ram pressure → fill and weight estimate".
- Load cells: "reference weight (5 % of fleet)".
- Oil probe: "cold oil reads high → correction".

## Honesty rules (non-negotiable)

1. **The exterior follows the brochure drawing.** Report every dimension you used, with its source ("drawing" or "measured from drawing").
2. **The interior is schematic.** It shows the standard press-container layout:
   - a horizontal ram block in the press chamber;
   - two double-acting hydraulic cylinders behind the ram, along the machine's long axis;
   - a power unit with motor, pump, oil tank and valve block, beside or behind the chamber inside the press section;
   - a control box behind the panel.

   **Size the internals plausibly:**
   - the ram face fills the chamber cross-section (about 1,500 wide × 900 high);
   - each cylinder bore is around 100–125 mm;
   - the stroke is sized so the ram reaches 20–30 cm into the container.
3. **Label the internals on screen.** A small caption "Internal layout: schematic, not Europress CAD" must be visible whenever internals are shown. The video's closing card must say "Exterior dimensions from the Europress Combi brochure (20 m³). Internal layout and most sensor positions are schematic."
4. **Do not invent precision.** No part numbers, no real Europress sensor models, and no exact values apart from those listed above.
5. **Watch the units.** The data is synthetic and the model is ours. Never put the Europress logo on any surface where it would look like official CAD. Plain "EUROPRESS" lettering on the container side, as in the photo, is fine.

## Storyboard (about 16 s at 30 fps, 1920×1080, ~480 frames)

1. **0–3 s:** The assembled Combi in a dark studio. Slow three-quarter orbit from the front-left (infeed side). Title: "Europress Combi · 20 m³".
2. **3–7 s:** **Disassembly** (exploded view), with eased motion and parts moving apart along clear axes:
   - the hopper lid lifts up;
   - the press-section side panel slides out sideways;
   - the container body slides back along the long axis;
   - the rear door swings and offsets back;
   - the machine lifts off the scale platform.

   The internals appear (ram, cylinders, power unit, control box), with the "schematic" caption.
3. **7–12 s:** **Sensors.** The camera holds, or moves gently, while the sensors light up one by one in teal (`#3FD0C9`), each with its label, leader line and confidence tag. Then:
   - the ram strokes once into the container mouth;
   - a small 2D inset or overlay draws a pressure curve rising as the ram meets the pack;
   - the caption reads "Ram pressure → fill & weight".
4. **12–15 s:** **Reassembly**, the reverse of step 2. The sensors stay as small glowing dots.
5. **15–16 s:** The closing card with the honesty note from rule 3.

## Visual style

- **Background:** dark, `#0E1218`.
- **Text and colours:** `#E8EDF3` for text, `#8793A3` for muted text, teal `#3FD0C9` for sensors, amber `#F2A93B` for the pressure curve, coral `#EF6F6C` only for warnings.
- **Font:** IBM Plex Sans and Mono, from `/home/hackathon/output/animation-comparison/assets/fonts/`.
- **Full palette:** `/home/hackathon/output/animation-comparison/shared/style.json`.
- **Materials:** painted steel for the blue body, darker steel for the frame and platform, brushed metal for the cylinders, and a matte plastic for the control panel.
- **Lighting:** clean studio lighting with no clutter. It should read as engineering, not as a game.
- **Labels:** easy to read at 1080p, at least about 28 px tall, kept clear of the parts they label.

## Tools and environment (already set up; do not install system packages)

- **Machine:** Linux VM, **no GPU**, no sudo, many CPU cores (check `nproc`).
- **Blender (as a Python module):** `/home/hackathon/output/animation-comparison/.venv-blender/bin/python` has `bpy` 5.2.3. Run scripts headless with it.
  - **Cycles on CPU** has been measured at about 10 s per 1080p frame for a simple scene (16 samples + OpenImageDenoise) on 16 cores.
  - EEVEE works but is very slow here (about 100 s per frame on software OpenGL), so **use Cycles CPU**.
- **Example to read first:** `/home/hackathon/output/animation-comparison/demos/blender/surface.py` and its `render.sh`. They are a working headless Cycles setup, and their resumable frame loop does three things:
  - it skips frames that already exist;
  - it writes each frame to a temporary file, then renames it;
  - it lets `render.sh` encode whatever frames exist.

  Copy that pattern.
- **ffmpeg:** `/home/hackathon/output/animation-comparison/bin/ffmpeg`.
- **Text:** Blender text objects or a 2D overlay are both fine.
  - **Option 1:** render labels in Blender, parented to the camera, using the Plex TTF files.
  - **Option 2:** render the 3D pass alone, then composite labels and the pressure-curve inset afterwards with Pillow + ffmpeg, which is easier to iterate.

  Pick one and say why.
- **Running long jobs:** start them with `nohup setsid … &` and log to a file, so they survive the tool timeout. Don't kill processes with `pkill -f` or `pgrep` loops (that can kill your own shell); use explicit PIDs.

## Work plan

1. Read the PDFs (especially Combi page 2). Write `notes/dimensions.md`, listing every dimension and its source.
2. Build the model procedurally in Python (`build_combi.py`): named objects and collections (`exterior`, `internals_schematic`, `sensors`, `platform`), real-world units in metres.
3. **Check early, before rendering any frames.** Render 4 low-resolution stills (960×540, 8 samples), all with the "schematic" caption visible where it applies:
   - assembled;
   - exploded;
   - a sensor close-up;
   - a side view against the brochure drawing.
4. Compare the side and top stills with the brochure drawing. Put them side by side in one image, `qc/compare_side.png`, and fix proportions until they match.
5. Animate (`animate_combi.py`) with eased keyframes, following the storyboard.
6. Render the full sequence resumably at 1920×1080, 30 fps, Cycles CPU, with OIDN. Choose samples so the render takes under about 90 minutes, and say how many you used.
7. Encode H.264 (CRF 18, `yuv420p`, `+faststart`) to `out/combi_exploded_sensors.mp4`. Also save a poster frame and a 6-frame contact sheet.
8. Watch the result frame by frame from the contact sheet and the posters. Fix any of these:
   - clipping or overlapping parts;
   - labels covering the parts they point to;
   - unreadable text;
   - a missing "schematic" caption.

## Output

Everything goes under `/home/hackathon/output/press-3d/`:

- **Scripts:** `build_combi.py`, `animate_combi.py`, `render.sh` (resumable; `FRESH=1` restarts, `ENCODE_ONLY=1` encodes what exists).
- **Notes:** `notes/dimensions.md`, plus `notes/README.md` covering:
  - how to re-render;
  - what is from the drawing and what is schematic;
  - render time and samples.
- **Video and images:** `out/combi_exploded_sensors.mp4`, `out/poster.jpg`, `out/contact_sheet.jpg`, `qc/*.png`.
- **Model file:** the `.blend` file, so a person can open it in Blender later.

## Report back with

1. The video path, its length, and the render time.
2. A table of every dimension used and its source.
3. Which sensors are at confirmed positions and which are schematic.
4. The QC comparison with the drawing, and what still differs.
5. Anything you could not do.

Do not edit files outside `/home/hackathon/output/press-3d/`. Do not publish anything online.
