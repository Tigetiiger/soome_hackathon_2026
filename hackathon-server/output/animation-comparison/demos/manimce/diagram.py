"""Manim Community demo: technical diagram of a sensed waste compactor.

Side view of a compactor: the hydraulic ram compresses waste, a pressure
transducer reads the cylinder pressure, load cells under the feet read the
reaction forces, an ultrasonic sensor reads the fill level. The readouts feed
a simple virtual-scale estimate  m̂ = (R1 + R2 − R0) / g.

All numbers are illustrative. LaTeX is not available in this environment, so
all typography uses Pango text (IBM Plex) instead of MathTex.

Render:  ./render.sh
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, UL, DR, PI,
    AnimationGroup, Arc, Arrow, Circle, Create, DashedLine, Dot, FadeIn, FadeOut,
    GrowArrow, GrowFromCenter, LaggedStart, Line, MarkupText, Polygon, Rectangle,
    RoundedRectangle, Scene, SurroundingRectangle, Text, ValueTracker, VGroup,
    Write, always_redraw, config, rate_functions,
)

ROOT = Path(__file__).resolve().parents[2]
STYLE = json.loads((ROOT / "shared" / "style.json").read_text())
C = STYLE["colors"]
SANS, MONO = STYLE["font_sans"], STYLE["font_mono"]

config.background_color = C["bg"]

EASE = rate_functions.ease_in_out_cubic
SEED = 2026
P_MAX_BAR = 182.0
R0_KN = 2.4          # tare reading of the empty container
LOAD_KN = 28.85      # payload reaction (sum of both cells)
G = 9.81


def label(text: str, size: int = 22, color: str = C["muted"], weight: str = "NORMAL") -> Text:
    return Text(text, font=SANS, font_size=size, color=color, weight=weight)


def mono(text: str, size: int = 22, color: str = C["ink"]) -> Text:
    return Text(text, font=MONO, font_size=size, color=color)


class CompactorSensors(Scene):
    def construct(self) -> None:
        # ------------------------------------------------------------ frame --
        title = label("Sensing a compactor", 40, C["ink"], "SEMIBOLD")
        subtitle = label("three low-cost signals → one mass estimate", 24, C["muted"], "LIGHT")
        head = VGroup(title, subtitle).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        head.to_corner(UL, buff=0.5)
        tag = mono("Manim Community 0.22.1  ·  1920×1080  ·  30 fps", 16, C["muted"])
        tag.to_corner(DR, buff=0.35)

        # --------------------------------------------------------- machine --
        ground_y = -2.55
        ground = Line([-6.9, ground_y, 0], [1.4, ground_y, 0], color=C["grid"], stroke_width=3)
        hatch = VGroup(*[
            Line([x, ground_y, 0], [x - 0.22, ground_y - 0.22, 0], color=C["grid"], stroke_width=2)
            for x in np.arange(-6.8, 1.45, 0.3)
        ])

        body = RoundedRectangle(width=5.6, height=2.9, corner_radius=0.12,
                                stroke_color=C["ink"], stroke_width=3).move_to([-2.0, -0.55, 0])
        body.set_fill(C["panel"], 1)
        hopper = Polygon([-4.4, 0.9, 0], [-3.2, 0.9, 0], [-2.9, 1.75, 0], [-4.7, 1.75, 0],
                         stroke_color=C["ink"], stroke_width=3)
        chamber_left, chamber_right = -4.55, 0.55
        floor_y, roof_y = -1.85, 0.75

        feet = VGroup(*[
            Polygon([x - 0.35, -2.0, 0], [x + 0.35, -2.0, 0], [x + 0.25, -2.25, 0],
                    [x - 0.25, -2.25, 0], stroke_color=C["ink"], stroke_width=2.5)
            for x in (-4.1, 0.1)
        ])

        cyl = Rectangle(width=1.55, height=0.62, stroke_color=C["ink"], stroke_width=3)
        cyl.move_to([-5.75, -0.9, 0]).set_fill(C["panel"], 1)
        ram_x = ValueTracker(chamber_left + 0.1)

        def make_ram() -> VGroup:
            x = ram_x.get_value()
            plate = Rectangle(width=0.16, height=2.45, stroke_width=0)
            plate.set_fill(C["ink"], 0.9).move_to([x, (floor_y + roof_y) / 2, 0])
            rod = Line([-5.0, -0.9, 0], [x - 0.08, -0.9, 0], color=C["ink"], stroke_width=7)
            return VGroup(rod, plate)

        ram = always_redraw(make_ram)

        # ----------------------------------------------------------- waste --
        rng = np.random.default_rng(SEED)
        stream_col = STYLE["streams"][0]["color"]
        blocks = VGroup()
        cols, rows = 9, 5
        w = (chamber_right - chamber_left - 0.45) / cols
        h = (roof_y - floor_y - 0.25) / rows
        for i in range(cols):
            for j in range(rows - (1 if i % 3 == 0 else 0)):
                b = RoundedRectangle(width=w * 0.86, height=h * 0.82, corner_radius=0.05,
                                     stroke_width=0)
                b.set_fill(stream_col, rng.uniform(0.45, 0.85))
                b.move_to([chamber_left + 0.35 + w * (i + 0.5), floor_y + 0.1 + h * (j + 0.5), 0])
                b.rotate(rng.uniform(-0.12, 0.12))
                blocks.add(b)

        # --------------------------------------------------------- sensors --
        def sensor(symbol: str, color: str, pos) -> VGroup:
            ring = Circle(radius=0.24, color=color, stroke_width=3).set_fill(C["bg"], 1)
            txt = Text(symbol, font=SANS, font_size=20, color=color, weight="SEMIBOLD")
            return VGroup(ring, txt).move_to(pos)

        p_sensor = sensor("P", C["teal"], [-5.75, -0.18, 0])
        p_stem = Line([-5.75, -0.42, 0], [-5.75, -0.59, 0], color=C["teal"], stroke_width=3)
        lc = VGroup(*[sensor("LC", C["violet"], [x, ground_y, 0]).scale(0.85) for x in (-4.1, 0.1)])
        us = sensor("US", C["blue"], [-1.0, 1.15, 0])
        us_stem = Line([-1.0, 0.91, 0], [-1.0, 0.8, 0], color=C["blue"], stroke_width=3)
        sensor_labels = VGroup(
            label("pressure\ntransducer", 18, C["teal"]).next_to(cyl, DOWN, buff=0.15, aligned_edge=LEFT),
            label("load cells", 18, C["violet"]).next_to(lc[1], RIGHT, buff=0.2),
            label("ultrasonic fill sensor", 18, C["blue"]).next_to(us, UP, buff=0.12),
        )

        # -------------------------------------------------------- readouts --
        pressure = ValueTracker(0.0)
        fill = ValueTracker(0.0)
        load = ValueTracker(R0_KN)

        panel_x = 1.95

        def readout(name: str, color: str, value_fn, y: float):
            def build() -> VGroup:
                left = VGroup(Dot(radius=0.07, color=color), label(name, 20)).arrange(RIGHT, buff=0.18)
                left.move_to([panel_x, y, 0], aligned_edge=LEFT)
                value = mono(value_fn(), 30).move_to([panel_x + 4.9, y, 0], aligned_edge=RIGHT)
                return VGroup(left, value)
            return always_redraw(build)

        rows_ = VGroup(
            readout("hydraulic pressure  p", C["teal"], lambda: f"{pressure.get_value():.0f} bar", 1.55),
            readout("fill level  h", C["blue"], lambda: f"{fill.get_value():.0f} %", 0.95),
            readout("load cells  R1 + R2", C["violet"], lambda: f"{load.get_value():.1f} kN", 0.35),
        )

        # Pressure gauge, wired to the transducer
        gauge_c = np.array([-5.75, 1.0, 0])
        g_arc = Arc(radius=0.62, start_angle=-PI / 6, angle=4 * PI / 3, arc_center=gauge_c,
                    color=C["grid"], stroke_width=9)

        def gauge_angle() -> float:
            return 7 * PI / 6 - 4 * PI / 3 * pressure.get_value() / 220

        g_fill = always_redraw(lambda: Arc(
            radius=0.62, start_angle=7 * PI / 6,
            angle=-max(1e-3, 4 * PI / 3 * pressure.get_value() / 220), arc_center=gauge_c,
            color=C["teal"], stroke_width=9))
        needle = always_redraw(lambda: Line(
            gauge_c, gauge_c + 0.5 * np.array([np.cos(gauge_angle()), np.sin(gauge_angle()), 0]),
            color=C["ink"], stroke_width=4))
        hub = Dot(gauge_c, radius=0.07, color=C["ink"])
        g_lbl = label("bar", 16).move_to(gauge_c + DOWN * 0.36)
        g_wire = Line([-5.75, 0.06, 0], gauge_c + DOWN * 0.62, color=C["teal"], stroke_width=2)
        gauge = VGroup(g_wire, g_arc, g_fill, needle, hub, g_lbl)

        # ---------------------------------------------------------- forces --
        f_ram = always_redraw(lambda: Arrow(
            [ram_x.get_value() + 0.12, 0.35, 0], [ram_x.get_value() + 1.42, 0.35, 0],
            buff=0, color=C["coral"], stroke_width=6, max_tip_length_to_length_ratio=0.25))
        f_lbl = always_redraw(lambda: label("F = p · A", 22, C["coral"])
                              .next_to([ram_x.get_value() + 0.75, 0.42, 0], UP, buff=0.1))
        com = np.array([-1.3, -0.65, 0])
        mg = Arrow(com, com + DOWN * 1.05, buff=0, color=C["ink"], stroke_width=6)
        mg_lbl = label("m · g", 22, C["ink"]).next_to(mg, RIGHT, buff=0.12)
        mg_lbl.add_background_rectangle(color=C["bg"], opacity=0.85, buff=0.06)
        reactions = VGroup(*[
            Arrow([x, -3.45, 0], [x, -2.85, 0], buff=0, color=C["violet"], stroke_width=6,
                  max_tip_length_to_length_ratio=0.35)
            for x in (-4.1, 0.1)
        ])
        r_lbls = VGroup(label("R1", 20, C["violet"]).next_to(reactions[0], LEFT, buff=0.12),
                        label("R2", 20, C["violet"]).next_to(reactions[1], LEFT, buff=0.12))

        pulses = VGroup(*[
            Arc(radius=0.25 + 0.22 * k, start_angle=-PI / 2 - 0.5, angle=1.0,
                arc_center=[-1.0, 0.85, 0], color=C["blue"], stroke_width=3,
                stroke_opacity=0.9 - 0.2 * k)
            for k in range(4)
        ])
        level_line = DashedLine([chamber_left + 0.3, 0.63, 0], [chamber_right - 0.05, 0.63, 0],
                                color=C["blue"], dash_length=0.1, stroke_width=2.5)

        # -------------------------------------------------------- equation --
        eq = MarkupText('m̂ = (R<sub>1</sub> + R<sub>2</sub> − R<sub>0</sub>) / g',
                        font=SANS, font_size=34, color=C["ink"])
        eq.move_to([panel_x, -0.45, 0], aligned_edge=LEFT)
        mass_kg = LOAD_KN * 1000 / G
        result = VGroup(
            label("estimated payload", 18),
            Text(f"{mass_kg:,.0f} kg".replace(",", " "), font=SANS, font_size=54,
                 color=C["ink"], weight="SEMIBOLD"),
            mono("± 90 kg  (1σ, illustrative)", 18, C["muted"]),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        result.next_to(eq, DOWN, aligned_edge=LEFT, buff=0.45).shift(RIGHT * 0.22)
        box = SurroundingRectangle(result, color=C["amber"], buff=0.22, corner_radius=0.12,
                                   stroke_width=2.5)
        divider = Line([panel_x - 0.35, 2.0, 0], [panel_x - 0.35, -2.9, 0],
                       color=C["grid"], stroke_width=2)

        # ======================================================= timeline ===
        self.play(FadeIn(head, shift=UP * 0.2), FadeIn(tag), run_time=0.8)
        self.play(Create(ground), FadeIn(hatch), Create(body), Create(hopper),
                  Create(feet), Create(cyl), Create(divider), run_time=1.6, rate_func=EASE)
        self.add(ram)
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.6) for b in blocks],
                              lag_ratio=0.02), run_time=1.3)
        self.play(LaggedStart(
            AnimationGroup(GrowFromCenter(p_sensor), Create(p_stem)),
            AnimationGroup(*[GrowFromCenter(s) for s in lc]),
            AnimationGroup(GrowFromCenter(us), Create(us_stem)),
            lag_ratio=0.3), FadeIn(sensor_labels, lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(rows_, shift=LEFT * 0.3, lag_ratio=0.2), FadeIn(gauge), run_time=0.8)

        # Compaction stroke
        self.add(f_ram, f_lbl)
        new_left = chamber_left + 1.5
        right_edge = chamber_right - 0.1
        factor = (right_edge - (new_left + 0.15)) / (right_edge - (chamber_left + 0.35))
        self.play(
            ram_x.animate.set_value(new_left),
            blocks.animate.stretch(factor, 0, about_edge=RIGHT),
            pressure.animate.set_value(P_MAX_BAR),
            run_time=2.4, rate_func=EASE)

        # Fill level + weight
        self.play(LaggedStart(*[Create(a) for a in pulses], lag_ratio=0.25),
                  fill.animate.set_value(78), Create(level_line), run_time=1.1)
        self.play(FadeOut(pulses), FadeOut(f_ram), FadeOut(f_lbl), GrowArrow(mg), FadeIn(mg_lbl),
                  LaggedStart(*[GrowArrow(r) for r in reactions], lag_ratio=0.2),
                  FadeIn(r_lbls), load.animate.set_value(R0_KN + LOAD_KN),
                  pressure.animate.set_value(24), ram_x.animate.set_value(chamber_left + 0.1),
                  run_time=1.6, rate_func=EASE)

        self.play(Write(eq), run_time=1.0)
        self.play(FadeIn(result, shift=UP * 0.15), Create(box), run_time=0.9)
        self.wait(1.4)
