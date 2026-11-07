"""compose_overlay.py - draw titles, sensor labels with leader lines, confidence tags, the
"schematic" caption, the pressure-curve inset and the closing card on top of the Cycles
frames.  Pure Pillow + numpy (run with animation-comparison/.venv/bin/python).

Why a 2D overlay instead of Blender text: crisp text at any size, labels that never
intersect geometry, and copy/layout changes in seconds without re-rendering the 3D pass.
Anchor positions come from out/anchors.json, written by animate_combi.py --anchors (the
exact Blender camera projection of each sensor, with a ray-cast visibility flag).

    python compose_overlay.py --frames [--overwrite] [--jobs 16]   # out/frames3d -> out/frames
    python compose_overlay.py --qc                                  # qc/*_3d.png -> qc/*.png
    python compose_overlay.py --stills                              # qc/still_*.png -> qc/ann_*.png
    python compose_overlay.py --sheet                               # out/poster.jpg + contact sheet
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import timeline as TL  # noqa: E402

AC = Path("/home/hackathon/output/animation-comparison")
STYLE = json.loads((AC / "shared" / "style.json").read_text())
C = STYLE["colors"]
FONT_DIR = AC / "assets" / "fonts"
W, H = STYLE["width"], STYLE["height"]
SS = 2                                  # supersampling for antialiased vector drawing
OUT, QC = HERE / "out", HERE / "qc"

# ---------------------------------------------------------------------------------
# copy
# ---------------------------------------------------------------------------------
TAG_STYLE = {   # confidence tag -> (text colour, fill, outline)
    "confirmed": (C["bg"], C["teal"], C["teal"]),
    "schematic": (C["muted"], None, C["muted"]),
    "proposed": (C["violet"], None, C["violet"]),
}
# x, y = top-left of the label box in 1920x1080; leaders run from the nearest box edge
LABELS = [
    {"key": "oiltemp", "anchors": ["oiltemp"], "title": "Oil temperature probe (~€30)",
     "note": "cold oil reads high → correction", "tag": "proposed", "kind": "proposed",
     "pos": (48, 172), "col": "left"},
    {"key": "pressure", "anchors": ["pressure"], "title": "Hydraulic pressure transducer",
     "note": "ram pressure → fill & weight estimate", "tag": "position schematic",
     "kind": "schematic", "pos": (48, 314), "col": "left"},
    {"key": "gps", "anchors": ["gps"], "title": "GPS / 5G SMART module",
     "note": "location, also while being transported", "tag": "position schematic",
     "kind": "schematic", "pos": (48, 456), "col": "left"},
    {"key": "tilt", "anchors": ["tilt"], "title": "Tilt & movement sensor",
     "note": "lifted & moved → container emptied", "tag": "position schematic",
     "kind": "schematic", "pos": (48, 598), "col": "left"},
    {"key": "loadcell", "anchors": ["loadcell_0", "loadcell_1"], "title": "Load cells ×4 (SMART Scale option)",
     "note": "reference weight (5 % of fleet)", "tag": "per Europress brochure",
     "kind": "confirmed", "pos": (48, 780), "col": "left"},
    {"key": "ram", "anchors": ["ram"], "title": "Ram: 20–30 cm into the container",
     "note": "pushes each load into the pack", "tag": "per Europress", "kind": "confirmed",
     "pos": (900, 52)},
    {"key": "lid", "anchors": ["lid"], "title": "Hopper lid switch",
     "note": "lid open → press stops", "tag": "position schematic", "kind": "schematic",
     "pos": (1190, 560)},
    {"key": "door", "anchors": ["door"], "title": "Door interlock switch",
     "note": "door open → no cycle", "tag": "position schematic",
     "kind": "schematic", "pos": (1540, 590)},
]
SENSOR_DOTS = ["pressure", "ram", "gps", "tilt", "door", "lid", "oiltemp",
               "loadcell_0", "loadcell_1", "loadcell_2", "loadcell_3"]
DOT_GROUP = {k: ("loadcell" if k.startswith("loadcell") else k) for k in SENSOR_DOTS}

PHASES = [  # (t0, t1, heading, sub)
    (3.25, 7.0, "Exploded view", "parts move apart along their own axes"),
    (7.0, 12.35, "Where the sensors sit", "tag = how sure we are of each position"),
    (12.35, 15.0, "Reassembly", "sensors stay marked · ring = inside the machine"),
]
CAPTION = "Internal layout: schematic, not Europress CAD"
CARD = [
    ("Exterior dimensions from the Europress Combi brochure (20 m³).", "card", "ink"),
    ("Internal layout and most sensor positions are schematic.", "card", "ink"),
    ("", "gap", "ink"),
    ("Load-cell corners: Europress Scale brochure  ·  ram entry 20–30 cm: Europress", "small", "muted"),
    ("Oil temperature probe: our proposal  ·  pressure curve illustrative, not measured", "small", "muted"),
    ("Model built by our team from the published drawing, not Europress CAD", "small", "muted"),
]


# ---------------------------------------------------------------------------------
# drawing helpers (all coordinates in 1920x1080 units; multiplied by SS when drawn)
# ---------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def font(name: str, px: int):
    files = {"semi": "IBMPlexSans-SemiBold.ttf", "reg": "IBMPlexSans-Regular.ttf",
             "med": "IBMPlexSans-Medium.ttf", "light": "IBMPlexSans-Light.ttf",
             "mono": "IBMPlexMono-Regular.ttf", "monomed": "IBMPlexMono-Medium.ttf"}
    return ImageFont.truetype(str(FONT_DIR / files[name]), px * SS)


def hexa(h: str, a: float = 1.0):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), max(0, min(255, int(round(255 * a)))))


def col(name_or_hex: str, a: float = 1.0):
    return hexa(C.get(name_or_hex, name_or_hex), a)


def text_size(txt, f):
    l, t, r, b = f.getbbox(txt)
    return (r - l) / SS, (b - t) / SS


def fade(t, t0, t1, ramp=0.3):
    return TL.clamp01((t - t0) / ramp) * (1.0 - TL.clamp01((t - (t1 - ramp)) / ramp))


def layer_alpha(img: Image.Image, a: float) -> Image.Image:
    if a >= 0.999:
        return img
    r, g, b, al = img.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))


@lru_cache(maxsize=None)
def glow_sprite(radius: int, color: str, strength: float):
    size = radius * 6 * SS
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size // 2
    d.ellipse((c - radius * 1.6 * SS, c - radius * 1.6 * SS, c + radius * 1.6 * SS,
               c + radius * 1.6 * SS), fill=col(color, strength))
    return im.filter(ImageFilter.GaussianBlur(radius * 0.9 * SS))


def paste_center(canvas, sprite, x, y):
    canvas.alpha_composite(sprite, (int(x * SS - sprite.width / 2), int(y * SS - sprite.height / 2)))


def rounded_panel(w, h, a=0.86, border=C["grid"], fill=C["panel"], accent=None, radius=10):
    im = Image.new("RGBA", (int(w * SS), int(h * SS)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), radius=radius * SS, fill=hexa(fill, a),
                        outline=hexa(border, 1.0), width=SS)
    if accent:
        d.rounded_rectangle((0, 0, 5 * SS, h * SS - 1), radius=3 * SS, fill=col(accent))
    return im


def dashed(d, p0, p1, color, width=2, dash=10, gap=8):
    x0, y0 = p0
    x1, y1 = p1
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    s = 0.0
    while s < L:
        e = min(L, s + dash)
        d.line(((x0 + ux * s) * SS, (y0 + uy * s) * SS, (x0 + ux * e) * SS, (y0 + uy * e) * SS),
               fill=color, width=int(width * SS))
        s = e + gap


# ---------------------------------------------------------------------------------
# elements
# ---------------------------------------------------------------------------------
def label_width(lab):
    ft, fn, fg = font("semi", 30), font("reg", 28), font("mono", 24)
    return max(text_size(lab["title"], ft)[0], text_size(lab["note"], fn)[0],
               text_size(lab["tag"], fg)[0] + 22) + 2 * 16 + 6


LEFT_W = None


def label_box(lab, lit: float):
    global LEFT_W
    ft, fn, fg = font("semi", 30), font("reg", 28), font("mono", 24)
    if LEFT_W is None:   # one tidy column: every left label gets the widest left width
        LEFT_W = max(label_width(lb) for lb in LABELS if lb.get("col") == "left")
    w = LEFT_W if lab.get("col") == "left" else label_width(lab)
    h = 128
    im = rounded_panel(w, h, accent=C["teal"] if lit > 0 else None)
    d = ImageDraw.Draw(im)
    x = 22
    d.text((x * SS, 22 * SS), lab["title"], font=ft, fill=col("ink"), anchor="lm")
    d.text((x * SS, 58 * SS), lab["note"], font=fn, fill=col("muted"), anchor="lm")
    tc, tf, to = TAG_STYLE[lab["kind"]]
    gw, _ = text_size(lab["tag"], fg)
    ty0, ty1 = 80, 114
    d.rounded_rectangle((x * SS, ty0 * SS, (x + gw + 20) * SS, ty1 * SS), radius=7 * SS,
                        fill=hexa(tf) if tf else None, outline=hexa(to), width=int(1.5 * SS))
    d.text(((x + 10) * SS, (ty0 + ty1) / 2 * SS), lab["tag"], font=fg, fill=hexa(tc), anchor="lm")
    return im, w, h


def draw_leader(ov, d, box, anchor, a, grow=1.0, gutter=None):
    """Leader from the nearest vertical box edge to the anchor, with a short horizontal run
    (left-column labels all turn at the same gutter x so their leaders never cross a box)."""
    bx, by, bw, bh = box
    ax, ay = anchor
    if ax >= bx + bw:
        sx = bx + bw
        ex = gutter if gutter else sx + 26
    elif ax <= bx:
        sx = bx
        ex = sx - 26
    else:   # anchor below/above the box: leave from the bottom/top centre
        sx = min(max(ax, bx + 30), bx + bw - 30)
        sy = by + bh if ay > by + bh else by
        pts = [(sx, sy), (ax, ay)]
        _poly(d, pts, a, grow)
        return
    sy = min(max(ay, by + 22), by + bh - 22)
    pts = [(sx, sy), (ex, sy), (ax, ay)]
    _poly(d, pts, a, grow)


def _poly(d, pts, a, grow):
    segs = list(zip(pts[:-1], pts[1:]))
    total = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in segs)
    left = total * grow
    for p, q in segs:
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        if left <= 0:
            break
        f = min(1.0, left / L) if L else 1.0
        e = (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f)
        d.line((p[0] * SS, p[1] * SS, e[0] * SS, e[1] * SS), fill=col("teal", 0.9 * a), width=int(2.5 * SS))
        left -= L


def draw_dot(ov, d, x, y, a, visible=True, flash=0.0, r=7):
    paste_center(ov, glow_sprite(r, C["teal"], 0.55 * a), x, y)
    if visible:
        d.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS), fill=col("teal", a),
                  outline=col("ink", 0.8 * a), width=int(1.5 * SS))
    else:   # x-ray marker: the sensor is inside the closed machine
        d.ellipse(((x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS),
                  outline=col("teal", a), width=int(2.5 * SS))
    if flash > 0:
        rr = r + 22 * flash
        d.ellipse(((x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS),
                  outline=col("teal", (1 - flash) * a), width=int(2 * SS))


def draw_heading(ov, t):
    for t0, t1, head, sub in PHASES:
        a = fade(t, t0, t1, 0.35)
        if a <= 0:
            continue
        lay = Image.new("RGBA", (900 * SS, 110 * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.text((0, 0), head, font=font("semi", 40), fill=col("ink"))
        d.text((0, 54 * SS), sub, font=font("reg", 28), fill=col("muted"))
        ov.alpha_composite(layer_alpha(lay, a), (48 * SS, 40 * SS))


def draw_title(ov, t):
    a = fade(t, *TL.TITLE, 0.45)
    if a <= 0:
        return
    lay = Image.new("RGBA", (1400 * SS, 170 * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((0, 0), "Europress Combi · 20 m³", font=font("semi", 64), fill=col("ink"))
    d.text((2 * SS, 84 * SS), "Press-container waste compactor · built from the brochure dimension drawing",
           font=font("reg", 30), fill=col("muted"))
    d.line((2 * SS, 140 * SS, 120 * SS, 140 * SS), fill=col("teal"), width=3 * SS)
    ov.alpha_composite(layer_alpha(lay, a), (64 * SS, 56 * SS))


def draw_caption(ov, t):
    a = fade(t, *TL.INTERNALS_CAPTION, 0.3)
    if a <= 0:
        return
    f = font("med", 28)
    tw, th = text_size(CAPTION, f)
    w, h = tw + 64, 54
    im = rounded_panel(w, h, a=0.9, border=C["muted"])
    d = ImageDraw.Draw(im)
    # small "schematic" glyph: dashed square
    gx, gy = 16, 15
    for i in range(0, 24, 6):
        d.line(((gx + i) * SS, gy * SS, (gx + i + 3) * SS, gy * SS), fill=col("muted"), width=2 * SS)
        d.line(((gx + i) * SS, (gy + 24) * SS, (gx + i + 3) * SS, (gy + 24) * SS), fill=col("muted"), width=2 * SS)
        d.line((gx * SS, (gy + i) * SS, gx * SS, (gy + i + 3) * SS), fill=col("muted"), width=2 * SS)
        d.line(((gx + 24) * SS, (gy + i) * SS, (gx + 24) * SS, (gy + i + 3) * SS), fill=col("muted"), width=2 * SS)
    d.text((52 * SS, 9 * SS), CAPTION, font=f, fill=col("ink"))
    ov.alpha_composite(layer_alpha(im, a), (48 * SS, int((H - 48 - h) * SS)))


def pressure(x: float) -> float:
    """Illustrative ram pressure vs travel: friction only until the face meets the pack at the
    container mouth, then a steep rise.  Unitless; no measured values."""
    xm = MOUTH_FRAC
    if x <= xm:
        return 0.08 + 0.05 * x / xm
    s = (x - xm) / (1 - xm)
    return 0.13 + 0.87 * s ** 1.7


MOUTH_FRAC = 0.900 / 1.150   # infeed length / ram stroke (build_combi.py)


def draw_inset(ov, t):
    a = fade(t, 9.45, 12.55, 0.3)
    if a <= 0:
        return
    w, h = 460, 300
    x0, y0 = W - 48 - w, H - 48 - h
    im = rounded_panel(w, h, a=0.92)
    d = ImageDraw.Draw(im)
    d.text((20 * SS, 12 * SS), "Ram pressure → fill & weight", font=font("semi", 30), fill=col("ink"))
    d.text((20 * SS, 50 * SS), "illustrative curve", font=font("reg", 26), fill=col("muted"))
    # plot area
    px0, py0, px1, py1 = 64, 96, w - 24, h - 52
    d.line((px0 * SS, py0 * SS, px0 * SS, py1 * SS), fill=col("muted"), width=2 * SS)
    d.line((px0 * SS, py1 * SS, px1 * SS, py1 * SS), fill=col("muted"), width=2 * SS)
    d.text((22 * SS, (py0 - 4) * SS), "p", font=font("mono", 28), fill=col("muted"))
    d.text(((px0 + 8) * SS, (py1 + 8) * SS), "ram travel →", font=font("reg", 26), fill=col("muted"))
    xm = px0 + (px1 - px0) * MOUTH_FRAC
    zone = Image.new("RGBA", im.size, (0, 0, 0, 0))   # blend, don't overwrite the panel
    ImageDraw.Draw(zone).rectangle((xm * SS, py0 * SS, px1 * SS, py1 * SS), fill=col("amber", 0.16))
    im.alpha_composite(zone)
    d = ImageDraw.Draw(im)
    dashed(d, (xm, py0), (xm, py1), col("muted"), 2, 7, 6)
    fm = font("reg", 24)
    for i, word in enumerate(("container", "mouth")):
        tw, _ = text_size(word, fm)
        d.text(((xm - 10 - tw) * SS, (py0 + 2 + 28 * i) * SS), word, font=fm, fill=col("muted"))
    fz = font("mono", 24)
    tw, _ = text_size("20–30 cm", fz)
    d.text(((px1 - tw) * SS, (py1 + 10) * SS), "20–30 cm", font=fz, fill=col("amber"))
    # curve drawn up to the current ram position during the extension, kept afterwards
    prog = TL.ram_progress(t)
    extending = t <= TL.RAM_EXT[1] + 0.01
    upto = prog if extending else 1.0
    n = 80
    pts = []
    for i in range(n + 1):
        x = upto * i / n
        pts.append((px0 + (px1 - px0) * x, py1 - (py1 - py0) * pressure(x)))
    if len(pts) > 1 and upto > 0.002:
        d.line([(p[0] * SS, p[1] * SS) for p in pts], fill=col("amber"), width=4 * SS, joint="curve")
        if extending:
            ex, ey = pts[-1]
            d.ellipse(((ex - 7) * SS, (ey - 7) * SS, (ex + 7) * SS, (ey + 7) * SS), fill=col("amber"))
    ov.alpha_composite(layer_alpha(im, a), (int(x0 * SS), int(y0 * SS)))


def draw_bracket(ov, d, anchors, t):
    """'20-30 cm' dimension between the container mouth (assembled position) and the ram face."""
    prog = TL.ram_progress(t)
    if "mouth" not in anchors or prog <= MOUTH_FRAC:
        return
    a = TL.clamp01((prog - MOUTH_FRAC) / 0.05) * fade(t, 9.5, 12.0, 0.2)
    mx, my = anchors["mouth"][:2]
    rx, ry = anchors["ram_face_low"][:2]
    off = 26
    p0, p1 = (mx, my + off), (rx, ry + off)
    d.line((p0[0] * SS, p0[1] * SS, p1[0] * SS, p1[1] * SS), fill=col("teal", a), width=3 * SS)
    for (x, y), (bx, by) in ((p0, (mx, my)), (p1, (rx, ry))):
        d.line((x * SS, (y - 12) * SS, x * SS, (y + 12) * SS), fill=col("teal", a), width=3 * SS)
        dashed(d, (bx, by + 6), (x, y - 12), col("teal", 0.6 * a), 1.5, 4, 4)
    txt = "20–30 cm"
    f = font("monomed", 28)
    tw, _ = text_size(txt, f)
    cx = (p0[0] + p1[0]) / 2
    d.text(((cx - tw / 2) * SS, (max(p0[1], p1[1]) + 12) * SS), txt, font=f, fill=col("teal", a))


def draw_ghost_note(ov, d, anchors, t):
    a = fade(t, TL.MOUTH_GHOST[0] + 0.15, TL.MOUTH_GHOST[1], 0.3)
    if a <= 0 or "mouth" not in anchors:
        return
    mx, my = anchors["mouth"][:2]
    f = font("reg", 26)
    txt = "container mouth (assembled position)"
    tw, _ = text_size(txt, f)
    x, y = mx - tw - 40, my + 64
    d.text((x * SS, y * SS), txt, font=f, fill=col("muted", a))
    d.line(((x + tw + 6) * SS, (y + 16) * SS, (mx - 4) * SS, (my + 8) * SS), fill=col("muted", 0.7 * a),
           width=int(1.5 * SS))


def draw_sensors(ov, anchors, t, labels=True):
    d = ImageDraw.Draw(ov)
    out_a = 1.0 - TL.seg(t, *TL.LABELS_OUT)          # labels fade out at reassembly
    # leaders + dots first, boxes on top
    boxes = []
    for lab in (LABELS if labels else []):
        t_on = TL.sensor_on(lab["key"])
        if t < t_on:
            continue
        a = TL.clamp01((t - t_on) / 0.3) * out_a
        grow = TL.clamp01((t - t_on) / 0.35)
        im, w, h = label_box(lab, 1.0)
        x, y = lab["pos"]
        x = min(x, W - 48 - w)                     # never run off the right edge
        gutter = 48 + LEFT_W + 30 if lab.get("col") == "left" else None
        if a > 0:
            for an in lab["anchors"]:
                if an in anchors:
                    draw_leader(ov, d, (x, y, w, h), anchors[an][:2], a, grow, gutter)
            boxes.append((im, x, y, a))
    # dots: lit sensors glow; after the labels fade, every sensor keeps a small dot
    for k in SENSOR_DOTS:
        if k not in anchors:
            continue
        t_on = TL.sensor_on(DOT_GROUP[k])
        if t < t_on:
            continue
        x, y, depth, vis = anchors[k]
        if depth <= 0 or not (-50 < x < W + 50 and -50 < y < H + 50):
            continue
        if k.startswith("loadcell") and not vis:   # under the machine: no marker
            continue
        flash = TL.clamp01((t - t_on) / 0.6) if t - t_on < 0.6 else 0.0
        r = 7 if t < TL.LABELS_OUT[1] else 6
        draw_dot(ov, d, x, y, 1.0, bool(vis), flash, r)
    for im, x, y, a in boxes:
        ov.alpha_composite(layer_alpha(im, a), (int(x * SS), int(y * SS)))


def draw_card(ov, t):
    a = TL.seg(t, *TL.CARD_IN)
    if a <= 0:
        return
    bg = Image.new("RGBA", (W * SS, H * SS), col("bg", a))
    ov.alpha_composite(bg)
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    sizes = {"card": ("semi", 40, 62), "small": ("reg", 28, 44), "gap": ("reg", 28, 26)}
    total = sum(sizes[k][2] for _, k, _ in CARD)
    y = (H - total) / 2 - 20
    d.line(((W / 2 - 60) * SS, (y - 40) * SS, (W / 2 + 60) * SS, (y - 40) * SS), fill=col("teal"), width=3 * SS)
    for txt, kind, c in CARD:
        fam, px, lh = sizes[kind]
        if txt:
            f = font(fam, px)
            tw, _ = text_size(txt, f)
            d.text(((W - tw) / 2 * SS, y * SS), txt, font=f, fill=col(c))
        y += lh
    ov.alpha_composite(layer_alpha(lay, TL.seg(t, TL.CARD_IN[0] + 0.1, TL.CARD_IN[1] + 0.15)))


def compose(base: Image.Image, t: float, anchors: dict, labels: bool = True) -> Image.Image:
    """base: 1920x1080 RGB 3D frame; anchors: name -> [x, y, depth, visible] in 1920 space."""
    ov = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    draw_title(ov, t)
    draw_heading(ov, t)
    d = ImageDraw.Draw(ov)
    if labels:   # the QC close-up camera gets dots + caption only
        draw_bracket(ov, d, anchors, t)
    draw_sensors(ov, anchors, t, labels)
    if labels:
        draw_inset(ov, t)
    draw_caption(ov, t)
    draw_card(ov, t)
    ov = ov.resize((W, H), Image.LANCZOS)
    out = base.convert("RGBA")
    out.alpha_composite(ov)
    return out.convert("RGB")


# ---------------------------------------------------------------------------------
# drivers
# ---------------------------------------------------------------------------------
_ANCH = None


def _init(anchor_path):
    global _ANCH
    _ANCH = json.loads(Path(anchor_path).read_text())["frames"]


def _one(job):
    f, overwrite = job
    dst = OUT / "frames" / f"f{f:04d}.png"
    if dst.exists() and not overwrite:
        return f, "skip"
    src = OUT / "frames3d" / f"f{min(f, TL.LAST_3D_FRAME):04d}.png"
    if not src.exists():
        return f, "missing"
    base = Image.open(src).convert("RGB")
    if base.size != (W, H):                    # SCALE=50 preview passes
        base = base.resize((W, H), Image.LANCZOS)
    img = compose(base, TL.t_of(f), _ANCH[str(f)])
    tmp = dst.with_suffix(".tmp.png")
    img.save(tmp, compress_level=3)
    tmp.replace(dst)
    return f, "ok"


def run_frames(jobs: int, overwrite: bool):
    (OUT / "frames").mkdir(parents=True, exist_ok=True)
    for p in (OUT / "frames").glob("*.tmp.png"):
        p.unlink()
    todo = [(f, overwrite) for f in range(1, TL.N_FRAMES + 1)]
    with Pool(jobs, initializer=_init, initargs=(str(OUT / "anchors.json"),)) as pool:
        res = pool.map(_one, todo, chunksize=4)
    stats = {}
    for f, s in res:
        stats[s] = stats.get(s, 0) + 1
    missing = [f for f, s in res if s == "missing"]
    print(f"COMPOSED {stats}" + (f" first missing frame {missing[0]}" if missing else ""))


def scale_anchors(points, k):
    return {n: [v[0] * k, v[1] * k, v[2], v[3]] for n, v in points.items()}


def run_qc():
    meta = json.loads((QC / "anchors_qc.json").read_text())
    for name, m in meta.items():
        src = QC / f"{name}_3d.png"
        base = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
        k = 1.0 / m["scale"]
        t = TL.t_of(m["frame"])
        # label columns are laid out for the main camera; the close-up shows dots + caption
        img = compose(base, t, scale_anchors(m["points"], k), labels=(name != "03_sensor_closeup"))
        img.resize((W // 2, H // 2), Image.LANCZOS).save(QC / f"{name}.png")
        print("QC", name)


def run_stills():
    meta = json.loads((QC / "anchors_stills.json").read_text())
    for f, pts in meta.items():
        src = QC / f"still_{int(f):04d}.png"
        base = Image.open(src).convert("RGB")
        k = W / base.width
        base = base.resize((W, H), Image.LANCZOS)
        compose(base, TL.t_of(int(f)), scale_anchors(pts, k)).save(QC / f"ann_{int(f):04d}.png")
        print("STILL", f)


def run_sheet():
    frames = OUT / "frames"
    poster_f = int(10.95 * TL.FPS) + 1          # ram 25 cm into the mouth, curve at its peak
    Image.open(frames / f"f{poster_f:04d}.png").convert("RGB").save(OUT / "poster.jpg", quality=92)
    picks = [1.5, 5.2, 8.6, 10.95, 13.6, 15.8]
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * 3 + 4 * 16, th * 2 + 3 * 16 + 2 * 40), hexa(C["bg"])[:3])
    d = ImageDraw.Draw(sheet)
    fnt = ImageFont.truetype(str(FONT_DIR / "IBMPlexMono-Regular.ttf"), 24)
    for i, ts in enumerate(picks):
        f = int(ts * TL.FPS) + 1
        im = Image.open(frames / f"f{f:04d}.png").convert("RGB").resize((tw, th), Image.LANCZOS)
        x = 16 + (i % 3) * (tw + 16)
        y = 16 + (i // 3) * (th + 40 + 16)
        sheet.paste(im, (x, y))
        d.text((x, y + th + 6), f"t = {ts:4.1f} s   frame {f}", font=fnt, fill=hexa(C["muted"])[:3])
    sheet.save(OUT / "contact_sheet.jpg", quality=90)
    print("SHEET", OUT / "poster.jpg", OUT / "contact_sheet.jpg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", action="store_true")
    ap.add_argument("--qc", action="store_true")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--jobs", type=int, default=16)
    args = ap.parse_args()
    if args.frames:
        run_frames(args.jobs, args.overwrite)
    if args.qc:
        run_qc()
    if args.stills:
        run_stills()
    if args.sheet:
        run_sheet()


if __name__ == "__main__":
    main()
