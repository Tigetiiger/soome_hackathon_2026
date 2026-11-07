"""Assemble the 2-minute demo video from timeline.json.

    ../animation-comparison/.venv/bin/python build.py            # full build
    ../animation-comparison/.venv/bin/python build.py --no-burn  # skip the captioned version

Inputs (paths relative to this folder, all listed in timeline.json):
    clips/manim/{problem,solution,impact}.mp4   Manim clips
    clips/screen/demo.mp4                       dashboard screen recording
    clips/3d/combi_exploded_sensors.mp4         3D render from the GPU machine (drop it in when ready;
                                                until then a placeholder card is used)
    voice/voiceover.wav   (optional) one take of the whole narration, 120 s, starting at 0:00
    voice/<segment>_<n>.wav (optional) one file per caption line, placed at its caption start

Outputs in out/:
    demo_video.mp4              captions burned in (+ voice if present, else a silent track)
    demo_video_clean.mp4        same without burned captions (upload together with the .srt)
    demo_video.srt              English subtitles
    voiceover_script.md         narration with timecodes, for recording the voice-over
"""

from __future__ import annotations

import argparse
import json
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FFMPEG = str(ROOT.parent / "animation-comparison" / "bin" / "ffmpeg")
FONTS = Path.home() / ".local" / "share" / "fonts"
TL = json.loads((ROOT / "timeline.json").read_text())
W, H, FPS = TL["width"], TL["height"], TL["fps"]
TMP = ROOT / "out" / "_build"

INK = (0, 13, 97)
GROUND = (246, 248, 251)
DARK = (14, 18, 24)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def duration_of(video: Path) -> float:
    err = subprocess.run([FFMPEG, "-i", str(video)], capture_output=True, text=True).stderr
    for line in err.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"no duration for {video}")


# ---------- overlays (Pillow) ----------

def pill(text: str, dark: bool, stacked: bool = False) -> Image.Image:
    """Small data-source tag. stacked=True puts each ' · ' part on its own line (narrow, for the app sidebar)."""
    f = font("IBMPlexMono-Medium.ttf", 22 if stacked else 24)
    lines = text.split(" · ") if stacked else [text]
    tw = max(int(f.getlength(line)) for line in lines)
    lh = 30
    img = Image.new("RGBA", (tw + 36, lh * len(lines) + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fill = (255, 255, 255, 30) if dark else (255, 255, 255, 240)
    edge = (255, 255, 255, 110) if dark else (195, 202, 217, 255)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=16, fill=fill, outline=edge, width=2)
    for i, line in enumerate(lines):
        d.text((18, 7 + i * lh), line, font=f, fill=(232, 237, 243) if dark else INK)
    return img


def caption_png(text: str, path: Path) -> None:
    f = font("IBMPlexSans-Medium.ttf", 38)
    lines = textwrap.wrap(text, width=62)
    lh = 50
    tw = max(int(f.getlength(line)) for line in lines)
    bw, bh = tw + 64, lh * len(lines) + 30
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0 = (W - bw) // 2, H - 44 - bh
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=14, fill=(0, 13, 97, 222))
    for i, line in enumerate(lines):
        lw = int(f.getlength(line))
        d.text(((W - lw) // 2, y0 + 13 + i * lh), line, font=f, fill=(255, 255, 255, 255))
    img.save(path)


def placeholder_3d(path: Path) -> None:
    """Card shown until the GPU render of the exploded 3D view is dropped into clips/3d/."""
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    d.text((160, 200), "Europress Combi · 20 m³", font=font("IBMPlexSans-SemiBold.ttf", 64), fill=(232, 237, 243))
    d.text((160, 290), "3D exploded view with sensor positions", font=font("IBMPlexSans-Light.ttf", 44), fill=(135, 147, 163))
    sensors = [
        "ram pressure transducer  →  fill & weight estimate",
        "4 load cells (optional scale platform)  →  reference weight",
        "oil temperature probe  →  cold-oil correction",
        "GPS · tilt · door & lid switches",
    ]
    for i, s in enumerate(sensors):
        y = 420 + i * 70
        d.ellipse([160, y + 12, 182, y + 34], fill=(63, 208, 201))
        d.text((206, y), s, font=font("IBMPlexSans-Regular.ttf", 38), fill=(232, 237, 243))
    d.text((160, 760), "PLACEHOLDER · final render comes from the GPU machine",
           font=font("IBMPlexMono-Medium.ttf", 28), fill=(242, 169, 59))
    img.save(path)


# ---------- segments ----------

def build_segment(seg: dict) -> Path:
    out = TMP / f"seg_{seg['id']}.mp4"
    dur = seg["duration"]
    src = ROOT / seg["file"]
    dark = seg["kind"] == "external"
    inputs: list[str] = []
    if src.exists():
        ss = seg.get("in_point", 0.0)
        avail = duration_of(src) - ss
        inputs = ["-ss", f"{ss}", "-i", str(src)]
        base = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x{'0E1218' if dark else 'F6F8FB'},"
                f"fps={FPS},setsar=1")
        if avail < dur:
            print(f"  ! {seg['id']}: source has {avail:.2f}s after in_point, need {dur}s -> holding last frame")
            base += f",tpad=stop_mode=clone:stop_duration={dur - avail + 0.5}"
    else:
        if seg["kind"] != "external":
            raise SystemExit(f"missing clip {src} (segment {seg['id']})")
        card = TMP / "placeholder_3d.png"
        placeholder_3d(card)
        inputs = ["-loop", "1", "-framerate", str(FPS), "-i", str(card)]
        base = "[0:v]fps=30,setsar=1"
        print(f"  ! {seg['id']}: {src.name} not found, using placeholder card")
    # Tag pill for clips that do not draw their own (screen recording, 3D).
    filt = base + "[b]"
    last = "[b]"
    if seg["kind"] in ("screen", "external"):
        tag = TMP / f"tag_{seg['id']}.png"
        # Screen recording: the app header owns the top-right, so tag goes in the sidebar, bottom-left,
        # above the caption band. 3D clip: top-right.
        stacked = seg["kind"] == "screen"
        pill(seg["tag"], dark, stacked).save(tag)
        inputs += ["-i", str(tag)]
        pos = "24:H-h-200" if stacked else "W-w-36:30"
        filt += f";[b][1:v]overlay={pos}[t]"
        last = "[t]"
    # Short fades in and out of the dark 3D clip so the cut from the light clips is soft.
    if dark:
        filt += f";{last}fade=in:st=0:d=0.3,fade=out:st={dur - 0.3}:d=0.3[f]"
        last = "[f]"
    run([FFMPEG, "-y", "-loglevel", "error", *inputs, "-filter_complex", filt, "-map", last,
         "-t", f"{dur}", "-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-preset", "medium",
         "-pix_fmt", "yuv420p", str(out)])
    return out


def all_captions() -> list[tuple[float, float, str, str]]:
    caps = []
    for seg in TL["segments"]:
        for i, c in enumerate(seg["captions"]):
            caps.append((seg["start"] + c["t"], seg["start"] + c["t"] + c["d"], c["text"], f"{seg['id']}_{i + 1}"))
    return caps


def ts(t: float, sep: str = ",") -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"


def write_srt_and_script(caps: list[tuple[float, float, str, str]]) -> None:
    srt = [f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n" for i, (a, b, text, _) in enumerate(caps, 1)]
    (ROOT / "out" / "demo_video.srt").write_text("\n".join(srt))
    md = ["# Voice-over script (read at a calm pace; each line must fit its window)\n",
          "Record one take as `voice/voiceover.wav` (starting at 0:00, ~120 s), or one file per line as "
          "`voice/<id>.wav`. Then rerun `build.py`.\n", "| Window | id | Words | Line |", "|---|---|---|---|"]
    for a, b, text, cid in caps:
        md.append(f"| {ts(a, '.')[3:8]}–{ts(b, '.')[3:8]} ({b - a:.1f} s) | `{cid}` | {len(text.split())} | {text} |")
    (ROOT / "out" / "voiceover_script.md").write_text("\n".join(md) + "\n")


def audio_args(total: float, caps: list[tuple[float, float, str, str]], first_input: int) -> tuple[list[str], str]:
    """Return extra ffmpeg inputs and the audio filter producing [aout]."""
    take = ROOT / "voice" / "voiceover.wav"
    if take.exists():
        return ["-i", str(take)], (f"[{first_input}:a]aresample=48000,apad,atrim=0:{total},"
                                   f"loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    files = [(a, ROOT / "voice" / f"{cid}.wav") for a, _, _, cid in caps]
    files = [(a, p) for a, p in files if p.exists()]
    if files:
        inputs: list[str] = []
        parts = []
        for k, (a, p) in enumerate(files):
            inputs += ["-i", str(p)]
            ms = int(a * 1000)
            parts.append(f"[{first_input + k}:a]aresample=48000,adelay={ms}|{ms}[v{k}]")
        mix = "".join(f"[v{k}]" for k in range(len(files)))
        return inputs, (";".join(parts) + f";{mix}amix=inputs={len(files)}:normalize=0,apad,"
                        f"atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    return ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"], f"[{first_input}:a]atrim=0:{total}[aout]"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-burn", action="store_true")
    args = ap.parse_args()
    TMP.mkdir(parents=True, exist_ok=True)
    segs = sorted(TL["segments"], key=lambda s: s["start"])
    t = 0.0
    for s in segs:  # timeline must be contiguous
        assert abs(s["start"] - t) < 1e-6, f"gap/overlap before {s['id']}"
        t += s["duration"]
    total = t
    print(f"timeline {total:.1f}s, {len(segs)} segments")

    parts = [build_segment(s) for s in segs]
    lst = TMP / "concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    joined = TMP / "joined.mp4"
    run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])

    caps = all_captions()
    write_srt_and_script(caps)

    # Clean version (no burned captions) + audio.
    a_in, a_f = audio_args(total, caps, 1)
    run([FFMPEG, "-y", "-loglevel", "error", "-i", str(joined), *a_in, "-filter_complex", a_f,
         "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{total}", "-movflags", "+faststart", str(ROOT / "out" / "demo_video_clean.mp4")])
    if args.no_burn:
        return

    # Burned captions: one transparent PNG per caption, faded in/out.
    inputs: list[str] = []
    chain, last = [], "[0:v]"
    for k, (a, b, text, _) in enumerate(caps):
        png = TMP / f"cap_{k:02d}.png"
        caption_png(text, png)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b + 0.5}", "-i", str(png)]
        chain.append(f"[{k + 1}:v]format=rgba,fade=in:st={a}:d=0.18:alpha=1,"
                     f"fade=out:st={b - 0.18}:d=0.18:alpha=1[c{k}]")
        chain.append(f"{last}[c{k}]overlay=0:0:enable='between(t,{a},{b})'[o{k}]")
        last = f"[o{k}]"
    a_in, a_f = audio_args(total, caps, len(caps) + 1)
    run([FFMPEG, "-y", "-loglevel", "error", "-i", str(joined), *inputs, *a_in,
         "-filter_complex", ";".join(chain) + ";" + a_f, "-map", last, "-map", "[aout]",
         "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-t", f"{total}", "-movflags", "+faststart",
         str(ROOT / "out" / "demo_video.mp4")])
    print("wrote out/demo_video.mp4, out/demo_video_clean.mp4, out/demo_video.srt, out/voiceover_script.md")


if __name__ == "__main__":
    main()
