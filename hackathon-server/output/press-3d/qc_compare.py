"""qc_compare.py - put the orthographic renders next to the brochure drawing and overlay them.

Inputs (made by animate_combi.py --qc, and the drawing crops rasterised at 400 dpi from page 2
of the Combi brochure):
    qc/ref_drawing_side_400dpi.png   qc/04_side_ortho_3d.png    (1920 x 860, same pixel grid)
    qc/ref_drawing_top_400dpi.png    qc/05_top_ortho_3d.png     (1920 x 700, same pixel grid)
The ortho camera uses ortho_scale = 1920 px * 3.927 mm/px, so one render pixel is one drawing
pixel and the images register without any fitting.

Outputs: qc/compare_side.png, qc/compare_top.png
    row 1: drawing | render (half size, side by side)
    row 2: overlay at full size: render dimmed, drawing linework drawn on top in coral
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
QC = HERE / "qc"
AC = Path("/home/hackathon/output/animation-comparison")
C = json.loads((AC / "shared" / "style.json").read_text())["colors"]
F = ImageFont.truetype(str(AC / "assets/fonts/IBMPlexSans-SemiBold.ttf"), 30)
FM = ImageFont.truetype(str(AC / "assets/fonts/IBMPlexSans-Regular.ttf"), 24)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def compare(view: str, title: str):
    ref = Image.open(QC / f"ref_drawing_{view}_400dpi.png").convert("L")
    ren = Image.open(QC / f"0{'4' if view == 'side' else '5'}_{view}_ortho_3d.png").convert("RGB")
    assert ref.size == ren.size, (ref.size, ren.size)
    w, h = ref.size
    # overlay: dim render, coral where the drawing has ink
    ink = np.asarray(ref) < 140
    base = (np.asarray(ren).astype(np.float32) * 0.55).astype(np.uint8)
    base[ink] = hexrgb(C["coral"])
    over = Image.fromarray(base)
    half = (w // 2, h // 2)
    pad, head = 24, 56
    out = Image.new("RGB", (w + 2 * pad, head + half[1] + head + h + 48), hexrgb(C["bg"]))
    d = ImageDraw.Draw(out)
    d.text((pad, 12), f"{title}: brochure drawing (left) | our render (right)", font=F, fill=hexrgb(C["ink"]))
    out.paste(Image.open(QC / f"ref_drawing_{view}_400dpi.png").convert("RGB").resize(half, Image.LANCZOS),
              (pad, head))
    out.paste(ren.resize(half, Image.LANCZOS), (pad + half[0], head))
    y2 = head + half[1]
    d.text((pad, y2 + 12), "Overlay at 1:1 (3.927 mm per pixel): drawing linework in coral over the render",
           font=F, fill=hexrgb(C["ink"]))
    out.paste(over, (pad, y2 + head))
    d.text((pad, out.height - 38), "Europress Combi brochure p.2 (20 m³) vs build_combi.py; orthographic, no fitting",
           font=FM, fill=hexrgb(C["muted"]))
    out.save(QC / f"compare_{view}.png")
    print("wrote", QC / f"compare_{view}.png")


if __name__ == "__main__":
    compare("side", "Side view")
    compare("top", "Top view")
