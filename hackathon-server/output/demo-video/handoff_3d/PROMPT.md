# Prompt: make the rest of the demo video 3D, in the style of your press clip

> Paste everything below into the Claude chat that made the 25 s press clip (`press_weight.mp4`). Copy this whole `handoff_3d/` folder to that computer first; the data files and frames it mentions are in it.

---

You made the 25 s 3D press clip for our Europress × Since AI 2026 demo video in this chat (Combi compactor → sensors → pressure graph → hourly message → model → kilograms). The judges' cut is 2:00. Right now the rest of the video is flat 2D (Manim) on a light background, and next to your clip it looks sloppy. **Make the other non-demo parts 3D, in exactly the visual language of your press clip**, so the whole video looks like one film.

## 1. Where your clips go

| Time | Segment | Made by |
|---|---|---|
| 0:00–0:15 | **Problem** → `problem_3d.mp4` | **you (new)** |
| 0:15–0:40 | Inside the machine → kilograms → `press_weight.mp4` | you (already in progress) |
| 0:40–1:35 | Live demo: screen recording of the dashboard (light UI) | done, do not touch |
| 1:35–2:00 | **Impact** → `impact_3d.mp4` | **you (new)** |

Optional, only if there is time: `demo_in.mp4` (fly-in to the demo, section 5).

**Priority if time runs short:** `press_weight.mp4` → `impact_3d.mp4` → `problem_3d.mp4` → `demo_in.mp4`. Our submission target is **09:30 today (Sun 8 Nov)**, so send each clip as soon as it is done; the 2D versions stay as a fallback.

## 2. Technical spec (all clips)

- 1920×1080, 30 fps, H.264 yuv420p (CRF ≤ 18) or a PNG sequence; no audio.
- **Exact length:** `problem_3d.mp4` = 15.000 s = 450 frames; `impact_3d.mp4` = 25.000 s = 750 frames; `press_weight.mp4` = 25.000 s = 750 frames; `demo_in.mp4` = 0.800 s = 24 frames.
- **The bottom 180 px (y > 900) is reserved for burned-in captions.** Keep all text and key action above it.
- **Draw the data tag yourself, top right**, in the same pill/tag style as your press clip: `practice data` (problem), `practice data · estimate` (impact). Our build will not add one.
- Fonts: IBM Plex Sans / IBM Plex Mono (SIL OFL), as in your clip.
- Keep a short dark lead-in and lead-out (the build crossfades between segments).

## 3. Visual language: same film as the press clip

- **Same Combi model** (`combi.blend`), same lighting, same dark background, same colour grade, same overlay label style (titles, honesty tags).
- Accent colours: your teal for structure and data flow; **SMART green `#54DEA9` for weight and money**; a warm red/coral only for "unknown" (`?`).
- **The camera never stops:** slow dollies, orbits and push-ins. No static cards, no slide-like fades. Prefer match cuts and camera moves over cuts.
- Data comes alive in 3D: columns that rise, blocks that split, light trails that flow, waves that ripple across a fleet.
- Inspiration: industrial 3D explainers that pair a realistic machine with abstract data visuals and show the data flow (ST Engineering, Altair, JUMO in the Advids roundups), and camera fly-throughs from one data point to the next (Pitch Interactive "Flying through data views", DataReels).

## 4. Storyboards

The captions below are also the voice-over. **Time each visual beat to its caption.** Times are seconds within the clip.

### 4.1 `problem_3d.mp4`: 15 s, tag `practice data`

| Caption (t, duration) | Text |
|---|---|
| 0.3, 5.0 | Waste is billed by weight, but only the operator weighs it, after pickup. |
| 5.5, 5.0 | Our demo hotel group: 395 pickups a year, only 48 with a weighing ticket. |
| 10.7, 4.2 | The machine knows how full it is. Nobody knows how heavy. |

- **0.0–5.2: the weight gap.** An abstract low-poly hotel (`Hospitality Customer 0049 · 3 sites · 9 machines`) with the Combi at its loading dock. A neutral, unbranded hook-lift truck picks up the press container and drives off along a road to a **weighbridge far away**. The camera follows and then pulls back so the distance reads. A weight display lights up **only at the weighbridge** (show the unit `kg` with dashes, not an invented number). Over the hotel, a coral `?`. Labels: `operator weighs · at the weighbridge, after the truck has left` and `customer: ?`.
  - Tone: **operators are our partners.** No villain truck, nothing like "paid per tonne", nothing that suggests the operator's figure is wrong. The point is only *where* and *when* the weight becomes known.
- **5.2–10.6: one year of pickups.** The camera lifts into the data. A 3D timeline lies on the floor, Oct 2025 → Sep 2026. **395 thin columns**, one per pickup at its date, height = fill % at emptying (`data/org0049_pickups.json`: `d` = date, `f` = fill %, `tk` = has a ticket). Columns rise in a quick wave as the camera dollies along the year, counter `395 pickups`. Then the **48 with `tk = true` light up blue** and the rest dim, with the title `48 of 395 with a weighing ticket`. A translucent plane at **49 %** (`avg fill at emptying 49 %`) slices through: most trucks come half full. One row has `f = null`; put that column at 49 %.
- **10.6–15.0: fill known, weight unknown.** Whip or match cut back to the Combi. An x-ray view shows the fill inside (green) with labels `fill: known ✓` and `weight: ?` (coral). **End on the framing of the first frame of `press_weight.mp4`**, so the cut into your press clip is invisible.

### 4.2 `impact_3d.mp4`: 25 s, tag `practice data · estimate`

All numbers are in `data/impact_v2.json` and `data/fleet_map.json`; read them from the files, don't retype them.

| Caption (t, duration) | Text |
|---|---|
| 0.3, 7.2 | SMART is paid with a share of what it saves: this hotel group pays about €13,000 and keeps €39,000. |
| 7.9, 7.6 | Across the demo fleet: €1.25 million saved for 52 customers, 3,945 fewer truck trips, and about €311,000 a year for Europress. |
| 15.8, 6.0 | Next: weigh a small reference group for real, retrain, and ship it to every machine as software. |
| 22.2, 2.7 | Europress sells trust and control, never data. |

- **0.2–7.7: one customer's money.** The hotel group's year as a 3D stack of slabs, `€140,574 waste cost`. A green block of **€52,154 (37 %)** slides out, `SMART can save`. It splits into three blocks: `empty when full €39,955`, `better sorting €6,318`, `avoidable fees €5,881`. Then the green total splits **25 / 75**: **€13,038** flows to a SMART emblem (`SMART fee · 25 % of the saving`) and **€39,116** flows back to the hotel (`the hotel group keeps`). The camera orbits slowly around the blocks.
- **7.8–15.6: the demo fleet, a fly-over of Finland.** A dark low-poly Finland. Outline from Natural Earth admin-0 (public domain); note its licence. The 150 sites of the 52 customers come from `fleet_map.json` (`customers[].sites[].lat/lon`, placed at their municipality centre). Pin each customer's sites as green columns, height ∝ `savings_eur` (split evenly over its sites).
  - **8.2:** `€1.25M · savings found · 52 demo customers`.
  - **10.5:** light trails between sites for the 5 partners (`partners[]`, names marked "fictional"), `3,945 · fewer truck trips · 5 demo partners`.
  - **12.7:** a Europress emblem rises (no real HQ location), `≈ €311k · SMART fees a year · at a 25 % share of savings`.
  - The camera flies from the Turku/Helsinki cluster north toward Oulu, DataReels-style.
- **15.6–22.0: next step, train on real weight.**
  - **1:** about 10 Combis on the SMART Scale platform (the load-cell platform you already modelled) glow as the reference group. `1 · Weigh a reference group`, small text `partner weighbridge weights first; load cells on 10 machines (≈ €34–63k) if needed`.
  - **2:** data lines flow from them into a model core, `2 · Retrain the model · on real weights, tested on machines outside the group`.
  - **3:** a wave ripples across a grid of hundreds of small Combis without platforms, `3 · Roll out as software · to every SMART machine, no new hardware`.
  - Small footnote: `all figures so far are simulated; this is how they become measured`.
- **22.1–25.0: end card.** The camera rises over the fleet. Text:
  - `SMART Insights · weight at source`
  - `Europress × Since AI 2026`
  - `Europress never sells data. Data is exchanged only when both parties agree.`
  - small: `All data synthetic: Europress practice data + our simulator. Prices hypothetical.`

The clip opens right after the demo's last frame (`frames/demo_end.png`, a light UI). Start from the dark stage; the build crossfades.

## 5. Optional: `demo_in.mp4`, 0.8 s, 24 frames

The bridge from your press clip into the screen recording. On the dark stage, a floating browser panel carries `frames/demo_start.png` as its texture. The camera flies in until the panel fills the frame. **The last frame must be `demo_start.png` exactly**, so the cut to the recording is invisible. Nothing else in the frame.

## 6. Rules (non-negotiable)

- **Numbers:** use only the numbers in this prompt and the data files. Invent none. Where no number exists, show a unit or `?`, not a made-up value.
- **Honesty tags** as in your press clip. Exterior per the Europress brochure; internals and sensor positions schematic. All data synthetic.
- **Business model (binding):**
  - operators are partners;
  - customers never upload invoices;
  - there is no oil-temperature probe;
  - load cells exist only on reference machines;
  - the SMART fee is a share of the predicted saving (demo 25 %);
  - Europress never sells data.
- **No third-party 3D models** of other brands' machines or trucks, no real logos except the brochure "EUROPRESS" lettering you already use, no real people.
- **Licences:** list every third-party asset (fonts, map outline, HDRIs, textures) with its licence in `LICENSES.md`.

## 7. Before you send each clip

1. Check the exact frame count and that nothing important sits in the bottom 180 px.
2. Make a contact sheet (6–8 frames, with timestamps), as you did for the press clip.
3. In `NOTES.md`, list where each on-screen number comes from (file + field) and which caption each beat lines up with.

Send back `problem_3d.mp4`, `impact_3d.mp4` (and `demo_in.mp4` if made), plus their contact sheets, `NOTES.md` and `LICENSES.md`. They go into `output/demo-video/clips/3d/` on the hackathon machine.

## 7a. Reminder for `press_weight.mp4`

- 25.000 s, 750 frames, saved as `press_weight.mp4`.
- Corrected storyboard:
  - load cells labelled `SMART Scale option · reference machines only`;
  - weather card `FMI in production · synthetic here`;
  - model just "LightGBM";
  - example BIN-0001, 16 Mar 2026 16:00: ≈ 1,490 kg, likely 1,370–1,530 kg, against 1,451 kg true (simulated); badge `≈ 1,490 kg inside`.
- **Heads-up:** another session retrained the model at 23:34 without oil temperature. The model files now say **5.2 %** on unseen machines (ladder 32.1 → 7.0 → 5.7 → 5.4 → 5.2 %), but the published technical page still says **5.3 %** (32.1 → 7.0 → 5.9 → 5.7 → 5.3). Keep 5.3 % unless told otherwise, and keep the ladder values in one place so they are easy to change.

## Files in this folder

| File | Contents |
|---|---|
| `data/org0049_pickups.json` | 395 pickups of the hotel group (`d`, `f`, `tk`, `s`, `id`); 48 with `tk = true`; mean `f` 49.2 |
| `data/impact_v2.json` | hotel group cost, savings, levers, fee, keeps; fleet totals; reference-group cost range |
| `data/fleet_map.json` | 52 customers (savings, 150 sites with municipality, region, lat/lon), 5 fictional partners (trips saved), totals |
| `frames/demo_start.png` | first still frame of the demo recording (end frame of `demo_in.mp4`) |
| `frames/demo_end.png` | last frame of the demo recording (comes right before `impact_3d.mp4`) |
