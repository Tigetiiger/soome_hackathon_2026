# Demo video (2:00)

The final video is `out/demo_video.mp4`, 1920×1080 at 30 fps with English captions burned in. A version without burned-in captions is `out/demo_video_clean.mp4`, with the subtitles in `out/demo_video.srt`.

## Structure

The structure follows the organiser's guide. The source of every number on screen is listed in `clips/manim/README.md` and in `../NUMBERS.md`.

| Time | Segment | Source |
|---|---|---|
| 0:00–0:15 | Problem: a year of pickups for the hotel group, only 48 of 395 with a weighing ticket | Manim, practice data |
| 0:15–0:27 | 3D exploded view with sensor positions | **Placeholder until the GPU render arrives** |
| 0:27–0:40 | Solution: ram pressure curves, then error falling from 32.1 % to 5.3 % | Manim, simulated |
| 0:40–1:35 | Live demo of the dashboard (Overview, Weight, Operators, Savings trace, Weighbridge check, Sales brief) | Screen recording of http://127.0.0.1:8080 |
| 1:35–2:00 | Impact: €60,471 of €140,574 saveable; 74 % → 97 % of pickups with an independent weight; +1 pp ≈ €21,600; €0 test first | Manim, practice data and estimate |

Captions and voice-over lines live in `timeline.json`. That file is the single source for every time and every line of text.

## Drop in the 3D clip

1. Copy the GPU render to `clips/3d/combi_exploded_sensors.mp4`. Any resolution works; it is fitted to 1080p.
2. Set `"in_point"` in `timeline.json`, in the `machine3d` segment, to the second where the 12 s excerpt should start. The default is 4.0, which skips the slow opening orbit and shows the disassembly and the sensors.
3. Rebuild (takes about 5 minutes):
   ```bash
   ../animation-comparison/.venv/bin/python build.py
   ```

## Add a voice-over

The organisers recommend narration. No speech engine could be installed here, so the video currently has a silent audio track.

- **Script:** `out/voiceover_script.md` lists every line with its time window and word count. Each line is about 2.6 words per second or slower.
- **Option 1, one take:** record the whole narration as one take, `voice/voiceover.wav`, starting at 0:00.
- **Option 2, one file per line:** save each line as `voice/<id>.wav`, using the ids in the script (`problem_1`, …). Each file is placed at its caption's start time.

Rerun `build.py` afterwards. The audio is normalised to −16 LUFS.

## Notes

- **Sales brief (D6):** the brief in the recording is a real Claude answer from the app, captured earlier and replayed from cache. A live answer takes about 13 s, so the clip shortens the wait to about 1.3 s.
- **Hidden pop-up:** the "SMART AI found a way to save you €39,955" pop-up is hidden in the recording browser only. The app itself was not changed.
- **Re-rendering the clips:**
  - Manim clips: `clips/manim/src/render.sh`.
  - Screen recording: `node clips/screen/src/record.mjs`. The app must be running.
