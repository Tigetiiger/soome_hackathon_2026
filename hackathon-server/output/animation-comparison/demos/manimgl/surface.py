"""ManimGL demo: animated 3D calibration surface with orbiting camera.

m̂(fill, pressure; ρ) — the estimated payload of a compactor as a function of
fill level and ram pressure. The material parameter ρ morphs the surface from
light plastic film to dense cardboard while the camera orbits; a glowing
"current lift" point then travels across the surface with a live readout.

Render (see ../../README.md):  ./render.sh
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from manimlib import (
    DEG, DOWN, LEFT, RIGHT, UL, UR, DR,
    DashedLine, DecimalNumber, FadeIn, FadeOut, GlowDot, Line, Scene,
    ShowCreation, SurfaceMesh, Text, ThreeDAxes, ValueTracker, VGroup, Write,
    always_redraw, smooth,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
from mockdata import mass_surface  # noqa: E402

STYLE = json.loads((Path(__file__).resolve().parents[2] / "shared" / "style.json").read_text())
C = STYLE["colors"]
SANS = STYLE["font_sans"]
MONO = STYLE["font_mono"]

AXIS_LEN = 6.0
Z_MAX = 3.6
GRADIENT = [C["violet"], C["teal"], C["amber"]]


def hex_rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


GRAD_RGB = np.array([hex_rgb(c) for c in GRADIENT])


def gradient_rgba(t: np.ndarray, opacity: float = 0.92) -> np.ndarray:
    """Vectorised 3-stop colour ramp, t in [0, 1]."""
    t = np.clip(t, 0, 1) * (len(GRAD_RGB) - 1)
    i = np.minimum(t.astype(int), len(GRAD_RGB) - 2)
    f = (t - i)[:, None]
    rgb = GRAD_RGB[i] * (1 - f) + GRAD_RGB[i + 1] * f
    return np.hstack([rgb, np.full((len(t), 1), opacity)])


def stream_color(d: float) -> str:
    keys = ("film", "mixed", "cardboard")
    idx = 0 if d < 0.4 else 1 if d < 0.7 else 2
    return next(s["color"] for s in STYLE["streams"] if s["key"] == keys[idx])


class CalibrationSurface(Scene):
    def construct(self) -> None:
        frame = self.frame
        frame.reorient(-50, 64, 0, (0.2, 0.3, 1.0), 10.8)

        axes = ThreeDAxes(
            x_range=(0, 1, 0.25), y_range=(0, 1, 0.25), z_range=(0, Z_MAX, 1),
            width=AXIS_LEN, height=AXIS_LEN, depth=Z_MAX,
            axis_config=dict(stroke_color=C["muted"], stroke_width=2, include_tip=False),
        )
        axes.shift(-axes.c2p(0.5, 0.5, 0))
        # Mass axis drawn at the back-left corner so the surface never hides it.
        axes.z_axis.set_opacity(0)
        z_line = Line(axes.c2p(0, 1, 0), axes.c2p(0, 1, Z_MAX)).set_stroke(C["muted"], 2)

        floor = VGroup(*[
            Line(axes.c2p(a, 0, 0), axes.c2p(a, 1, 0)) for a in np.linspace(0, 1, 9)
        ] + [
            Line(axes.c2p(0, a, 0), axes.c2p(1, a, 0)) for a in np.linspace(0, 1, 9)
        ]).set_stroke(C["grid"], 1.2, opacity=0.8)

        def axis_label(text: str, point) -> Text:
            """Billboard label: always faces the camera while it orbits."""
            base = Text(text, font=SANS, font_size=26).set_color(C["muted"])
            base.move_to(np.zeros(3))
            return always_redraw(lambda: base.copy()
                                 .apply_matrix(frame.get_orientation().as_matrix())
                                 .move_to(point))

        labels = VGroup(
            axis_label("fill level  →", axes.c2p(0.5, -0.16, 0)),
            axis_label("ram pressure  →", axes.c2p(-0.2, 0.45, 0)),
            axis_label("mass (t)", axes.c2p(0, 1, Z_MAX + 0.35)),
            *[axis_label(f"{k} t", axes.c2p(-0.08, 1, k)) for k in (1, 2, 3)],
        )

        growth = ValueTracker(0.0)
        density = ValueTracker(0.15)

        def make_surface():
            g, d = growth.get_value(), density.get_value()
            surf = axes.get_graph(
                lambda u, v: g * mass_surface(np.array(u), np.array(v), d),
                u_range=(0, 1), v_range=(0, 1), resolution=(72, 72),
                shading=(0.22, 0.18, 0.45),
            )
            z = (surf.get_points()[:, 2] - axes.c2p(0, 0, 0)[2]) / 3.2
            surf.set_rgba_array(gradient_rgba(z))
            return surf

        surface = always_redraw(make_surface)
        mesh = always_redraw(
            lambda: SurfaceMesh(surface, resolution=(11, 11))
            .set_stroke(C["bg"], 0.8, opacity=0.35)
        )

        # ---------------------------------------------------------- HUD ---
        title = Text("Virtual-scale calibration surface", font=SANS,
                     font_size=44, weight="SEMIBOLD").set_color(C["ink"])
        subtitle = Text("estimated payload  m̂(fill, pressure; ρ)  in tonnes",
                        font=SANS, font_size=26, weight="LIGHT").set_color(C["muted"])
        head = VGroup(title, subtitle).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        head.to_corner(UL, buff=0.55).fix_in_frame()

        tag = Text("ManimGL 1.7.2  ·  1920×1080  ·  30 fps", font=MONO, font_size=20)
        tag.set_color(C["muted"]).to_corner(DR, buff=0.4).fix_in_frame()

        rho_lbl = Text("material density ρ", font=SANS, font_size=24).set_color(C["muted"])
        rho_val = DecimalNumber(0.15, num_decimal_places=2, font_size=34).set_color(C["ink"])
        rho_val.add_updater(lambda m: m.set_value(density.get_value()))
        rho = VGroup(rho_lbl, rho_val).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        rho.to_corner(UL, buff=0.55).shift(DOWN * 1.45).fix_in_frame()
        stream = always_redraw(lambda: Text(
            "plastic film" if density.get_value() < 0.4 else
            "mixed waste" if density.get_value() < 0.7 else "cardboard (OCC)",
            font=SANS, font_size=24, weight="MEDIUM",
        ).set_color(stream_color(density.get_value()))
            .next_to(rho_val, RIGHT, buff=0.3).fix_in_frame())

        self.add(frame)
        self.play(
            ShowCreation(axes, lag_ratio=0.1), ShowCreation(z_line), FadeIn(floor), FadeIn(labels),
            Write(head), FadeIn(tag), run_time=1.6,
        )
        frame.add_ambient_rotation(3.2 * DEG)
        self.add(surface, mesh)
        self.add(labels)  # labels have no depth test: re-add so they draw over the surface
        self.play(growth.animate.set_value(1.0), FadeIn(rho), FadeIn(stream),
                  run_time=2.0, rate_func=smooth)
        self.play(density.animate.set_value(0.95), run_time=3.0, rate_func=smooth)

        # -------------------------------------------------- tracked lift ---
        path_t = ValueTracker(0.0)

        def lift_uv() -> tuple[float, float]:
            s = path_t.get_value()
            return 0.25 + 0.6 * s, 0.3 + 0.45 * np.sin(np.pi * s * 1.2)

        def lift_point():
            u, v = lift_uv()
            return axes.c2p(u, v, mass_surface(np.array(u), np.array(v), density.get_value()))

        dot = GlowDot(lift_point(), color=C["ink"], radius=0.35, glow_factor=2.2)
        dot.add_updater(lambda m: m.move_to(lift_point()))
        drop = always_redraw(lambda: DashedLine(
            lift_point(), axes.c2p(*lift_uv(), 0), dash_length=0.08,
        ).set_stroke(C["ink"], 2, opacity=0.8))

        def readout_text():
            u, v = lift_uv()
            m = float(mass_surface(np.array(u), np.array(v), density.get_value()))
            rows = VGroup(
                Text("CURRENT LIFT", font=MONO, font_size=18).set_color(C["muted"]),
                Text(f"fill {u * 100:.0f} %  ·  pressure {v:.2f}", font=MONO, font_size=24)
                .set_color(C["ink"]),
                Text(f"m̂ = {m:.2f} t", font=SANS, font_size=40, weight="SEMIBOLD")
                .set_color(C["ink"]),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
            return rows

        readout = always_redraw(lambda: readout_text().to_corner(UR, buff=0.6).fix_in_frame())

        self.play(FadeIn(dot), ShowCreation(drop), FadeIn(readout), run_time=0.6)
        self.play(path_t.animate.set_value(1.0), density.animate.set_value(0.55),
                  frame.animate.increment_phi(-4 * DEG).set_height(10.4).move_to((0.4, 0.2, 1.3)),
                  run_time=4.2, rate_func=smooth)
        self.wait(0.8)
        self.play(*map(FadeOut, [dot, drop, readout]), run_time=0.5)
