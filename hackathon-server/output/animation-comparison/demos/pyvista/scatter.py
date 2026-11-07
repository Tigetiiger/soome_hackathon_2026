"""PyVista demo: animated 3D scatter of compactor lifts.

Each sphere is one (synthetic) container lift: x = fill level, y = peak ram
pressure, z = weighbridge mass. Points rise into place, take on their
material-stream colours, the heavy-for-volume anomalies are highlighted,
and per-stream covariance ellipsoids fade in while the camera orbits.

Render:  ./render.sh          (writes out/lift_scatter.mp4)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("VTK_DEFAULT_OPENGL_WINDOW", "vtkEGLRenderWindow")  # headless GPU/llvmpipe

import numpy as np  # noqa: E402
import pyvista as pv  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "shared"))
from mockdata import lifts  # noqa: E402

STYLE = json.loads((ROOT / "shared" / "style.json").read_text())
C = STYLE["colors"]
FONT = str(ROOT / "assets" / "fonts" / "IBMPlexSans-Regular.ttf")
FONT_SB = str(ROOT / "assets" / "fonts" / "IBMPlexSans-SemiBold.ttf")
FONT_MONO = str(ROOT / "assets" / "fonts" / "IBMPlexMono-Regular.ttf")
W, H, FPS = STYLE["width"], STYLE["height"], STYLE["fps"]
DURATION = float(os.environ.get("DEMO_DURATION", 12.0))
OUT = Path(__file__).resolve().parent / "out" / "lift_scatter.mp4"

log = logging.getLogger("pyvista-demo")


def rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def ease(x: np.ndarray | float) -> np.ndarray:
    """easeInOutCubic on [0, 1]."""
    x = np.clip(x, 0, 1)
    return np.where(x < 0.5, 4 * x**3, 1 - (-2 * x + 2) ** 3 / 2)


def ease_out(x: np.ndarray | float) -> np.ndarray:
    x = np.clip(x, 0, 1)
    return 1 - (1 - x) ** 3


def window(t: float, a: float, b: float) -> float:
    return float(ease((t - a) / (b - a)))


# ------------------------------------------------------------------ data ----
data = lifts()
X = (data.fill_pct - 35) / 65 * 10
Y = (data.pressure_bar - 50) / 170 * 10
Z = data.mass_kg / 4200 * 7
N = len(X)
stream_rgb = np.array([rgb(s["color"]) for s in STYLE["streams"]])[data.stream]
anom = data.anomaly
order = np.argsort(np.argsort(X))            # rise left-to-right
delay = order / N * 1.4
BASE_R = 0.12


def frame_state(t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Positions, radii and colours of every point at time t (seconds)."""
    rise = ease_out((t - 0.3 - delay) / 1.3)
    pos = np.column_stack([X, Y, Z * rise])
    radius = BASE_R * rise

    colour_in = window(t, 3.0, 4.2)
    col = (1 - colour_in) * rgb(C["muted"]) + colour_in * stream_rgb

    hi = window(t, 6.0, 6.9) * (1 - window(t, 9.0, 9.8))
    dim = hi * 0.7
    col = np.where(anom[:, None], col * (1 - hi) + rgb(C["coral"]) * hi,
                   col * (1 - dim) + rgb(C["bg"]) * dim)
    anomaly_after = window(t, 9.0, 9.8)
    col = np.where(anom[:, None], col * (1 - anomaly_after) + rgb(C["coral"]) * anomaly_after, col)
    pulse = 1 + (0.9 * hi + 0.35 * anomaly_after) * (0.85 + 0.15 * np.sin(2 * np.pi * 1.6 * t))
    radius = np.where(anom, radius * pulse, radius)
    return pos, radius, col


def build_glyphs(pos: np.ndarray, radius: np.ndarray, col: np.ndarray, sphere: pv.PolyData):
    cloud = pv.PolyData(pos)
    cloud["r"] = np.maximum(radius, 1e-4)
    cloud["rgb"] = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    return cloud.glyph(geom=sphere, scale="r", orient=False)


def floor_grid() -> pv.PolyData:
    lines = []
    for a in np.linspace(0, 10, 11):
        lines += [[a, 0, 0], [a, 10, 0], [0, a, 0], [10, a, 0]]
    pts = np.array(lines, float)
    cells = np.hstack([[2, i, i + 1] for i in range(0, len(pts), 2)])
    return pv.PolyData(pts, lines=cells)


def ellipsoid(points: np.ndarray, k: float = 2.0, res: tuple[int, int] = (48, 48)) -> pv.PolyData:
    mean = points.mean(0)
    vals, vecs = np.linalg.eigh(np.cov(points.T))
    m = np.eye(4)
    m[:3, :3] = vecs @ np.diag(k * np.sqrt(vals))
    m[:3, 3] = mean
    return pv.Sphere(radius=1, theta_resolution=res[0], phi_resolution=res[1]).transform(m, inplace=False)


def camera_at(t: float) -> list:
    az = np.deg2rad(-58 + 70 * float(ease(t / DURATION)))
    el = np.deg2rad(24 - 6 * float(ease(t / DURATION)))
    dist = 23.5 - 2.5 * float(ease((t - 7) / 5))
    focal = np.array([5.0, 5.0, 2.6])
    eye = focal + dist * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    return [tuple(eye), tuple(focal), (0, 0, 1)]


CAPTIONS = [
    (0.0, "Each sphere is one lift  ·  height = weighbridge mass"),
    (3.0, "Colour = material stream"),
    (6.0, "14 lifts are far heavier than their volume suggests → audit"),
    (9.0, "Per-stream 2σ ellipsoids = the calibration envelope"),
]


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    p = pv.Plotter(off_screen=True, window_size=(W, H))
    p.set_background(C["bg"], top=C["bg_glow"])
    p.enable_anti_aliasing("ssaa")
    if os.environ.get("DEMO_DEPTH_PEELING", "1") == "1":
        p.enable_depth_peeling(number_of_peels=4)

    p.add_mesh(floor_grid(), color=C["grid"], line_width=1.5, opacity=0.9)
    p.add_mesh(pv.MultipleLines(points=[[0, 0, 7.2], [0, 0, 0], [10.4, 0, 0]]),
               color=C["muted"], line_width=2.5)
    p.add_mesh(pv.Line((0, 0, 0), (0, 10.4, 0)), color=C["muted"], line_width=2.5)
    p.add_point_labels(
        np.array([[5.0, -1.3, 0], [-0.6, 10.9, 0], [0, -0.3, 7.7]]),
        ["fill level", "ram pressure", "mass"], font_file=FONT, font_size=26,
        text_color=C["muted"], shape=None, show_points=False, always_visible=True)

    sphere = pv.Sphere(radius=1, theta_resolution=18, phi_resolution=18)
    glyphs = build_glyphs(*frame_state(0.0), sphere)
    p.add_mesh(glyphs, scalars="rgb", rgb=True, smooth_shading=True, pbr=True,
               metallic=0.05, roughness=0.38, show_scalar_bar=False)

    hulls, cages = [], []
    pts3 = np.column_stack([X, Y, Z])
    for s, spec in enumerate(STYLE["streams"]):
        sel = (data.stream == s) & ~anom
        hulls.append(p.add_mesh(ellipsoid(pts3[sel]), color=spec["color"], opacity=0.0,
                                smooth_shading=True, specular=0.4))
        # A sparse wireframe "cage" makes the translucent 2σ envelope readable on a dark background.
        cages.append(p.add_mesh(ellipsoid(pts3[sel], res=(24, 12)), style="wireframe",
                                color=spec["color"], line_width=1.2, opacity=0.0))

    p.add_text("Lifts in sensor space", position=(64, H - 110), font_size=30,
               color=C["ink"], font_file=FONT_SB)
    p.add_text(f"fill level × ram pressure × weighbridge mass  ·  {N} synthetic lifts",
               position=(66, H - 160), font_size=15, color=C["muted"], font_file=FONT)
    caption = p.add_text(CAPTIONS[0][1], position=(66, 60), font_size=18, color=C["ink"],
                         font_file=FONT)
    for i, spec in enumerate(STYLE["streams"] + [{"label": "Anomaly", "color": C["coral"]}]):
        p.add_text(f"—  {spec['label']}", position=(W - 330, H - 110 - 40 * i), font_size=15,
                   color=spec["color"], font_file=FONT)
    p.add_text("PyVista 0.49 / VTK 9.7  ·  1920×1080  ·  30 fps", position=(W - 700, 40),
               font_size=12, color=C["muted"], font_file=FONT_MONO)

    def update(t: float) -> None:
        glyphs.copy_from(build_glyphs(*frame_state(t), sphere))
        reveal = window(t, 9.2, 10.4)
        for h, cage in zip(hulls, cages):
            h.prop.opacity = 0.2 * reveal
            cage.prop.opacity = 0.55 * reveal
        start, text = [(ts, c) for (ts, c) in CAPTIONS if t >= ts][-1]
        caption.SetInput(text)
        caption.GetTextProperty().SetOpacity(window(t, start, start + 0.5) if start > 0 else 1.0)
        p.camera_position = camera_at(t)

    still = os.environ.get("DEMO_STILL")
    if still is not None:  # single-frame QC mode: DEMO_STILL=11.5 ./render.sh
        update(float(still))
        p.screenshot(str(OUT.with_name(f"still_{still}.png")))
        p.close()
        return

    p.open_movie(str(OUT), framerate=FPS, quality=9, macro_block_size=1)
    n_frames = int(DURATION * FPS)
    for f in range(n_frames):
        update(f / FPS)
        p.write_frame()
        if f % 60 == 0:
            log.info("frame %d/%d  %.1fs elapsed", f, n_frames, time.time() - t0)
    p.close()
    log.info("wrote %s in %.1fs", OUT, time.time() - t0)


if __name__ == "__main__":
    main()
