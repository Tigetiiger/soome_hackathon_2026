"""solution.mp4 (13.0 s): pressure -> weight, then the error ladder.

Curves: src/data/pressure_curves_bin0001.json (simulator runs/full400/pressure_curves.parquet,
machine BIN-0001, joined to hourly.parquet true_fill_pct).
Ladder: src/data/comparison_bins.json (models/full400/comparison.csv, split=bins, material=all).
"""

from __future__ import annotations

from manim import (
    always_redraw,
    DOWN, LEFT, RIGHT, UP, UL, Arrow, Create, FadeIn, FadeOut, LaggedStart, Line,
    Rectangle, RoundedRectangle, VGroup, VMobject, interpolate_color, ManimColor,
)

from common import C, EASE, Timed, card, data_tag, load, mono, txt

AX0, AX1 = -6.1, 0.2
AY0, AY1 = -2.2, 1.9
P_MAX = 180.0
LIGHT = "#b8c4e6"


def px(r: float) -> float:
    return AX0 + (AX1 - AX0) * r


def py(p: float) -> float:
    return AY0 + (AY1 - AY0) * p / P_MAX


def fill_color(alpha: float):
    return interpolate_color(ManimColor(LIGHT), ManimColor(C["ink"]), alpha)


class Solution(Timed):
    def construct(self) -> None:
        cur = load("pressure_curves_bin0001.json")
        ladder = load("comparison_bins.json")
        self.add(data_tag("simulated"))

        # ---------------------------------------------------------------- beat 1: 0 - 6.3 s
        head = txt("Ram pressure per stroke", 52, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        sub = txt(f"one simulated {cur['material']} compactor · colour = true fill", 28, C["muted"])
        sub.next_to(head, DOWN, aligned_edge=LEFT, buff=0.15)

        axis = VGroup(Line([AX0, AY0, 0], [AX1, AY0, 0], color=C["ink2"], stroke_width=2),
                      Line([AX0, AY0, 0], [AX0, AY1, 0], color=C["ink2"], stroke_width=2))
        yl = VGroup(*[mono(f"{v}", 26).next_to([AX0, py(v), 0], LEFT, buff=0.12) for v in (0, 50, 100, 150)])
        grid = VGroup(*[Line([AX0, py(v), 0], [AX1, py(v), 0], color=C["line"], stroke_width=1.5) for v in (50, 100, 150)])
        ytit = mono("bar", 26).next_to(yl, UP, buff=0.25).align_to(yl, RIGHT)
        xl = VGroup(mono("0", 26).next_to([px(0), AY0, 0], DOWN, buff=0.12),
                    mono("1", 26).next_to([px(1), AY0, 0], DOWN, buff=0.12),
                    txt("ram position →", 26, C["ink2"]).next_to([px(0.5), AY0, 0], DOWN, buff=0.12))

        self.p(FadeIn(head, shift=UP * 0.1), FadeIn(sub), Create(axis), FadeIn(grid), FadeIn(yl),
               FadeIn(ytit), FadeIn(xl), rt=0.7, rate_func=EASE)

        curves = cur["curves"]  # sorted by fill ascending
        fmin, fmax = curves[0]["fill"], curves[-1]["fill"]
        lines = VGroup()
        for c in curves:
            a = (c["fill"] - fmin) / (fmax - fmin)
            v = VMobject(stroke_color=fill_color(a), stroke_width=3.2, stroke_opacity=0.95)
            v.set_points_as_corners([[px(x), py(p), 0] for x, p in zip(c["x"], c["p"])])
            lines.add(v)

        # legend: gradient bar
        seg = VGroup(*[Rectangle(width=0.12, height=0.22, stroke_width=0).set_fill(fill_color(i / 19), 1)
                       for i in range(20)]).arrange(RIGHT, buff=0)
        leg = VGroup(mono(f"fill {fmin:.0f} %", 26), seg, mono(f"{fmax:.0f} %", 26)).arrange(RIGHT, buff=0.15)
        leg.move_to([px(0.04), py(112), 0], aligned_edge=LEFT)

        self.p(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.12), FadeIn(leg), rt=2.6, rate_func=EASE)

        note = txt("fuller → contact earlier, peak higher", 28, C["ink2"])
        note.move_to([px(0.04), py(135), 0], aligned_edge=LEFT)
        self.p(FadeIn(note, shift=UP * 0.1), rt=0.5)

        # flow: signals -> kg ± range (right side)
        self.at(3.9)
        chips = VGroup()
        for s in ("pressure", "strokes", "oil temp", "weather"):
            t = txt(s, 32, C["ink"], "MEDIUM")
            box = card(2.7, 0.7).set_stroke(C["line"], 2)
            t.move_to(box)
            chips.add(VGroup(box, t))
        chips.arrange(DOWN, buff=0.22).move_to([2.3, 0.0, 0])
        out = RoundedRectangle(width=2.6, height=1.5, corner_radius=0.16, stroke_width=0).set_fill(C["mark"], 1)
        out_t = VGroup(txt("kg", 48, C["mark_ink"], "SEMIBOLD"), txt("± range", 30, C["mark_ink"], "MEDIUM")).arrange(DOWN, buff=0.08)
        out_g = VGroup(out, out_t.move_to(out)).move_to([5.5, 0.0, 0])
        arrows = VGroup(*[Arrow(ch.get_right(), out.get_left(), buff=0.1, stroke_width=3, color=C["ink2"],
                                max_tip_length_to_length_ratio=0.12) for ch in chips])
        self.p(LaggedStart(*[FadeIn(ch, shift=RIGHT * 0.15) for ch in chips], lag_ratio=0.25), rt=1.0, rate_func=EASE)
        self.p(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.1), rt=0.5)
        self.p(FadeIn(out_g, scale=0.9), rt=0.5, rate_func=EASE)

        # ---------------------------------------------------------------- beat 2: 6.3 - 13 s
        self.at(6.1)
        everything = VGroup(head, sub, axis, grid, yl, ytit, xl, lines, leg, note, chips, arrows, out_g)
        head2 = txt("Mean error at lift · machines the model never saw", 44, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        self.p(FadeOut(everything), FadeIn(head2), rt=0.4)

        steps = [("fill × density (formula)", "naive_fill_x_density"), ("+ strokes", "fill_presses"),
                 ("+ pressure", "pressure"), ("+ curve shape", "pressure_graph"), ("final model", "full_selected")]
        vals = [round(ladder[k], 1) for _, k in steps]
        BX = -1.0
        scale = 6.0 / vals[0]
        ys = [1.75, 1.13, 0.51, -0.11, -0.73]
        cols = [C["bad"], C["link"], C["link"], C["link"], C["mark"]]
        prev_w = 0.02
        rows = []
        for i, ((lab, _), v, y) in enumerate(zip(steps, vals, ys)):
            label = txt(lab, 32, C["ink"] if i in (0, 4) else C["ink2"], "MEDIUM" if i in (0, 4) else "NORMAL")
            label.move_to([BX - 0.3, y, 0], aligned_edge=RIGHT)
            w = v * scale
            bar = Rectangle(width=prev_w, height=0.44, stroke_width=0).set_fill(cols[i], 0.9 if i else 0.75)
            bar.move_to([BX, y, 0], aligned_edge=LEFT)
            val = txt(f"{v:.1f} %", 34, C["ink"], "MEDIUM")
            rows.append((label, bar, val, w, y))
            prev_w = w

        def show_row(i: int, rt: float) -> None:
            label, bar, val, w, y = rows[i]
            val_r = always_redraw(lambda b=bar, t=val: t.copy().next_to(b, RIGHT, buff=0.2))
            self.add(bar, val_r)
            self.p(FadeIn(label, shift=RIGHT * 0.1),
                   bar.animate.stretch_to_fit_width(w).move_to([BX, y, 0], aligned_edge=LEFT),
                   rt=rt, rate_func=EASE)

        show_row(0, 0.8)
        self.at(7.7)
        for i in range(1, 5):
            show_row(i, 0.55)
        # (row widths for later rows start at the previous row's width, so they visibly shrink)

        self.at(10.3)
        call = VGroup(txt(f"{vals[4]:.1f} % mean error", 56, C["ink"], "SEMIBOLD"),
                      txt("· machines it never saw", 40, C["ink2"], "MEDIUM")).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
        call.move_to([0, -1.6, 0])
        hl = RoundedRectangle(width=call.width + 0.6, height=call.height + 0.4, corner_radius=0.14,
                              stroke_color=C["mark"], stroke_width=3).set_fill(C["card"], 1).move_to(call)
        time_v = round(ladder["time_full_selected"], 1)
        mnote = txt(f"same machines, later months: {time_v:.1f} %", 28, C["muted"]).next_to(hl, DOWN, buff=0.18)
        self.p(FadeIn(hl), FadeIn(call, shift=UP * 0.1), rt=0.6, rate_func=EASE)
        self.p(FadeIn(mnote), rt=0.4)
        self.at(13.0)
