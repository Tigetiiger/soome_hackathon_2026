"""Shared style + timing helpers for the three demo-video Manim scenes.

Style follows the live SMART Insights web app (light ground, navy ink).
Frame: 1920x1080 -> 14.22 x 8 Manim units, 1 unit = 135 px.
Captions are burned in later into the bottom 180 px (= 1.333 units), so all
content stays above y = SAFE_BOTTOM.
"""

from __future__ import annotations

import json
from pathlib import Path

from manim import (
    UR, RoundedRectangle, Scene, Text, VGroup, config, rate_functions,
)

DATA = Path(__file__).resolve().parent / "data"
FPS = 30

C = {
    "ground": "#f6f8fb",
    "card": "#ffffff",
    "line": "#dbe0ec",
    "ink": "#000d61",
    "ink2": "#3d4257",
    "muted": "#6b717c",
    "mark": "#54dea9",
    "mark_ink": "#003d2a",
    "link": "#1863dc",
    "good": "#1a7a47",
    "warn": "#9a6a00",
    "bad": "#b43c3c",
    "note": "#6b4fbf",
    "grey": "#cfd5e2",
}
SANS = "IBM Plex Sans"
MONO = "IBM Plex Mono"
SAFE_BOTTOM = -4.0 + 180 / 135  # -2.667
EASE = rate_functions.ease_in_out_cubic

config.background_color = C["ground"]


# Pango renders Text noticeably larger than its nominal px size at 1080p; sizes in the
# scenes are "design px" and are scaled once here (26 design px ~ 28 px cap+desc on screen).
TEXT_SCALE = 0.72


def txt(s: str, size: int = 32, color: str = C["ink"], weight: str = "NORMAL", font: str = SANS) -> Text:
    return Text(s, font=font, font_size=size * TEXT_SCALE, color=color, weight=weight)


def mono(s: str, size: int = 26, color: str = C["muted"]) -> Text:
    return Text(s, font=MONO, font_size=size * TEXT_SCALE, color=color)


def card(w: float, h: float, r: float = 0.14) -> RoundedRectangle:
    c = RoundedRectangle(width=w, height=h, corner_radius=r, stroke_color=C["line"], stroke_width=2)
    c.set_fill(C["card"], 1)
    return c


def data_tag(label: str) -> VGroup:
    t = mono(label, 26, C["ink2"])
    pill = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.3, corner_radius=(t.height + 0.3) / 2,
                            stroke_color=C["line"], stroke_width=2)
    pill.set_fill(C["card"], 1)
    t.move_to(pill)
    g = VGroup(pill, t)
    g.to_corner(UR, buff=0.4)
    g.set_z_index(100)
    return g


def load(name: str):
    return json.loads((DATA / name).read_text())


def eur(v: float) -> str:
    return f"€{v:,.0f}"


class Timed(Scene):
    """Scene that tracks elapsed time so beats can be pinned to caption times."""

    def setup(self) -> None:
        self.t = 0.0

    @staticmethod
    def _q(x: float) -> float:
        return round(x * FPS) / FPS

    def p(self, *anims, rt: float = 1.0, **kw) -> None:
        rt = self._q(rt)
        self.play(*anims, run_time=rt, **kw)
        self.t = self._q(self.t + rt)

    def at(self, T: float) -> None:
        """Wait until absolute time T (seconds)."""
        T = self._q(T)
        dt = self._q(T - self.t)
        if dt > 1e-9:
            self.wait(dt)
            self.t = T
        elif dt < -1e-9:
            raise RuntimeError(f"timeline overrun: at {self.t:.3f} > {T:.3f}")
