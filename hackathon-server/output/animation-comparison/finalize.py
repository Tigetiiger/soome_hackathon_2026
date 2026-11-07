"""Fill measured render timings into COMPARISON.md / index.html and make poster frames.

Run after ./render_all.sh:   python3 finalize.py
Reads logs/timings.txt and media/*.mp4; uses bin/ffmpeg. Standard library only.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FFMPEG = str(ROOT / "bin" / "ffmpeg")
MEDIA = {
    "manimce": "manimce_compactor_diagram.mp4",
    "manimgl": "manimgl_calibration_surface.mp4",
    "pyvista": "pyvista_lift_scatter.mp4",
    "threejs": "threejs_fleet_timeseries.mp4",
    "blender": "blender_calibration_surface.mp4",
}


def fmt_seconds(s: float) -> str:
    return f"{s:.0f} s" if s < 90 else f"{int(s // 60)} min {s % 60:02.0f} s"


def duration_s(video: Path) -> float:
    out = subprocess.run([FFMPEG, "-i", str(video)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def read_timings() -> dict[str, tuple[str, float]]:
    rows = {}
    for line in (ROOT / "logs" / "timings.txt").read_text().splitlines():
        name, status, secs = line.split()
        rows[name] = (status, float(secs.rstrip("s")))
    return rows


def main() -> None:
    timings = read_timings()
    values: dict[str, str] = {}
    for name, file in MEDIA.items():
        video = ROOT / "media" / file
        status, secs = timings.get(name, ("missing", 0.0))
        if status not in ("ok", "partial") or not video.exists():
            values[f"T_{name}"] = values[f"F_{name}"] = "not rendered"
            continue
        dur = duration_s(video)
        frames = round(dur * 30)
        values[f"T_{name}"] = fmt_seconds(secs)
        values[f"F_{name}"] = f"{secs / frames:.2f} s"
        poster = ROOT / "media" / f"poster_{name}.jpg"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{dur * 0.62:.2f}",
                        "-i", str(video), "-frames:v", "1", "-q:v", "3", "-vf", "scale=960:-1",
                        str(poster)], check=True)
    for target in ("COMPARISON.md", "index.html"):
        path = ROOT / target
        text = path.read_text()
        for key, val in values.items():
            text = text.replace("{{" + key + "}}", val)
        path.write_text(text)
        left = re.findall(r"\{\{\w+\}\}", text)
        print(target, "unfilled:" if left else "filled", " ".join(left))
    for key in sorted(values):
        print(f"  {key:12s} {values[key]}")

    # Contact sheet of all posters for a quick visual check.
    posters = [str(ROOT / "media" / f"poster_{n}.jpg") for n in MEDIA
               if (ROOT / "media" / f"poster_{n}.jpg").exists()]
    if len(posters) >= 2:
        inputs = sum((["-i", p] for p in posters), [])
        n = len(posters)
        layout = "|".join(f"{(i % 2) * 960}_{(i // 2) * 540}" for i in range(n))
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", *inputs, "-filter_complex",
                        f"xstack=inputs={n}:layout={layout}:fill=black", "-q:v", "3",
                        str(ROOT / "media" / "contact_sheet.jpg")], check=True)


if __name__ == "__main__":
    main()
