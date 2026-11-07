# Demo video (2:00), v2

The final video is `out/demo_video.mp4`, 1920×1080 at 30 fps with English captions burned in. A version without burned-in captions is `out/demo_video_clean.mp4`, with the subtitles in `out/demo_video.srt`.

v2 (7 Nov 2026, late evening) follows the business model on `business.html`: operators are partners, SMART Free shows no weight, the fee is a share of the predicted savings (demo 25 %). Weight figures follow the technical page at http://100.87.158.27:8765/. v1 is kept as `timeline_v1.json`, `clips/manim/{problem,impact}_v1.mp4`, `clips/screen/demo_v1.mp4` and `clips/screen/src/record_v1.mjs`.

## Structure

Weight first, then money, then everything else.

| Time | Segment | Source |
|---|---|---|
| 0:00–0:15 | **Problem:** the operator weighs at the weighbridge after the truck has left; the hotel group has 395 pickups a year, only 48 with a weighing ticket | Manim `problem.mp4`, practice data |
| 0:15–0:40 | **Inside the machine → kilograms:** the ram, sensors already on board, the pressure graph, the hourly message with weather, the model (32.1 % → 5.3 %), no extra hardware, honesty card | **3D clip, delivered separately** → `clips/3d/press_weight.mp4` (placeholder card until then) |
| 0:40–1:35 | **Live demo**, three views: customer Free → SMART (weight), weight per machine and expected charge, savings trace (€39,955 lever); partner view (driver plan, 676 fewer trips, the partnership); Europress view (weighbridge check, sales brief) | Screen recording of http://127.0.0.1:8080, `clips/screen/demo.mp4` |
| 1:35–2:00 | **Impact:** €140,574 → €52,154 saveable (37 %), three levers, SMART fee 25 % = €13,038 vs €39,116 kept; demo fleet €1.25M saved, 3,945 fewer trips, ≈ €311k fees; next step: weigh a reference group, retrain, roll out as software; end card (never sells data) | Manim `impact.mp4`, practice data and estimate |

`solution.mp4` (pressure curves and the error ladder) is no longer in the timeline: the 3D clip covers the same story. It stays in `clips/manim/` as a fallback.

Captions and voice-over lines live in `timeline.json`. That file is the single source for every time and every line of text. The `machine3d` segment also lists the storyboard scenes, so the captions line up with the 3D clip.

## Drop in the 3D clip

1. Copy the render to `clips/3d/press_weight.mp4`. It should be 25 s long; any resolution works (it is fitted to 1080p on a dark background).
2. If the clip starts later, set `"in_point"` in the `machine3d` segment of `timeline.json`.
3. Rebuild (takes about 5 minutes):
   ```bash
   ../animation-comparison/.venv/bin/python build.py
   ```

## Add a voice-over

No speech engine is installed here, so the video has a silent audio track.

- **Script:** `out/voiceover_script.md` lists every line with its time window and word count (2.0–2.8 words per second).
- **Option 1, one take:** record the whole narration as one take, `voice/voiceover.wav`, starting at 0:00.
- **Option 2, one file per line:** save each line as `voice/<id>.wav`, using the ids in the script (`problem_1`, …). Each file is placed at its caption's start time.

Rerun `build.py` afterwards. The audio is normalised to −16 LUFS.

## Where the numbers come from

- Impact clip: `clips/manim/src/export_impact_v2.py` reads the dashboard data (`ORG-0049.json`, `customers/*.json`, `operators/*.json`) and writes `clips/manim/src/data/impact_v2.json`; the scene reads only that file.
- Problem clip: see `clips/manim/README.md`.
- Demo: whatever the live app shows at recording time. The weight values come from the soft-sensor service (`europress-dashboard/softsensor`, port 8093), which must be running.

## Notes

- **Sales brief (D6):** a real Claude answer from the app, captured at 23:40 on 7 Nov (`clips/screen/src/brief_cache_v2.sse`, written by `brief_v2.mjs`) and replayed during the take. It uses the v2 figures (€52,154, 25 % fee ≈ €13,038) and says the operator is a partner. A live answer takes about 15 s, so the clip shortens the wait to about 0.6 s.
- **Recording-browser only:** the "SMART AI found a way to save you…" pop-up is hidden, and the 🔒 emoji (no emoji font on this machine) is drawn as an inline SVG lock. The app itself is not changed.
- **Re-rendering:**
  - Manim clips: `clips/manim/src/render.sh` (all three) or `SCENES="problem impact" clips/manim/src/render.sh`.
  - Screen recording: `node clips/screen/src/record.mjs` (`--stills` for a QC pass). The app and the soft-sensor service must be running.
