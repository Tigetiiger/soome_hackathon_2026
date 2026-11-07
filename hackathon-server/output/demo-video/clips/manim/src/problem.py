"""problem.mp4 (15.0 s): the weight gap, Hospitality Customer 0049.

Dots: src/data/org0049_pickups.json, exported from the practice dataset
(operations/collection_events.parquet, customer ORG-0049, status COMPLETED|PARTIAL;
ticket = weight_reconciliation_status != WEIGHBRIDGE_NOT_AVAILABLE).
"""

from __future__ import annotations

from datetime import datetime

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, Circle, Create, DashedLine, Dot, FadeIn, FadeOut,
    LaggedStart, Line, Polygon, Rectangle, RoundedRectangle, Text, ValueTracker,
    VGroup, Write, always_redraw,
)

from common import C, EASE, Timed, card, data_tag, load, mono, txt

X0, X1 = -6.0, 6.3      # chart x range (units)
Y0, Y1 = -2.25, 1.75    # chart y range: fill 0 % .. 100 %
D0 = datetime(2025, 10, 1)
DAYS = 365.0


def fx(d: datetime) -> float:
    return X0 + (X1 - X0) * ((d - D0).total_seconds() / 86400.0) / DAYS


def fy(fill: float) -> float:
    return Y0 + (Y1 - Y0) * fill / 100.0


def truck() -> VGroup:
    body = RoundedRectangle(width=1.5, height=0.8, corner_radius=0.06, stroke_color=C["ink"], stroke_width=3)
    cab = Polygon([0.75, -0.4, 0], [1.3, -0.4, 0], [1.3, 0.05, 0], [1.05, 0.3, 0], [0.75, 0.3, 0],
                  stroke_color=C["ink"], stroke_width=3)
    body.move_to([0, -0.0, 0])
    wheels = VGroup(*[Circle(0.17, stroke_color=C["ink"], stroke_width=3).set_fill(C["card"], 1).move_to([x, -0.45, 0])
                      for x in (-0.45, 0.35, 1.05)])
    return VGroup(body, cab, wheels)


def weighbridge() -> VGroup:
    deck = Rectangle(width=3.0, height=0.14, stroke_color=C["ink"], stroke_width=3).set_fill(C["line"], 1)
    pit = Line([-1.6, -0.12, 0], [1.6, -0.12, 0], color=C["ink2"], stroke_width=3)
    disp = RoundedRectangle(width=0.9, height=0.5, corner_radius=0.06, stroke_color=C["ink"], stroke_width=3)
    disp.set_fill(C["card"], 1).move_to([1.9, 0.75, 0])
    pole = Line([1.9, 0.5, 0], [1.9, -0.12, 0], color=C["ink"], stroke_width=3)
    kg = mono("kg", 26, C["ink"]).move_to(disp)
    return VGroup(pit, deck, pole, disp, kg)


def hotel() -> VGroup:
    b = Rectangle(width=1.4, height=1.6, stroke_color=C["ink"], stroke_width=3).set_fill(C["card"], 1)
    wins = VGroup(*[Rectangle(width=0.24, height=0.2, stroke_width=0).set_fill(C["line"], 1)
                    .move_to([x, y, 0]) for x in (-0.38, 0, 0.38) for y in (0.5, 0.15, -0.2)])
    door = Rectangle(width=0.32, height=0.42, stroke_width=0).set_fill(C["ink"], 1).move_to([0, -0.59, 0])
    return VGroup(b, wins, door)


def compactor(fill_frac: float) -> VGroup:
    body = RoundedRectangle(width=4.2, height=2.2, corner_radius=0.12, stroke_color=C["ink"], stroke_width=4)
    body.set_fill(C["card"], 1)
    inner_w = 3.0
    chamber = Rectangle(width=inner_w, height=1.6, stroke_color=C["ink2"], stroke_width=2).move_to([0.45, 0, 0])
    fill = Rectangle(width=inner_w * fill_frac, height=1.6, stroke_width=0).set_fill(C["mark"], 0.85)
    fill.align_to(chamber, RIGHT).align_to(chamber, DOWN)
    ram = Rectangle(width=0.18, height=1.6, stroke_width=0).set_fill(C["ink"], 1)
    ram.next_to(chamber, LEFT, buff=0.05)
    rod = Line(ram.get_left(), [-1.95, 0, 0], color=C["ink"], stroke_width=6)
    feet = VGroup(*[Rectangle(width=0.5, height=0.16, stroke_width=0).set_fill(C["ink"], 1)
                    .move_to([x, -1.18, 0]) for x in (-1.5, 1.5)])
    return VGroup(body, chamber, fill, ram, rod, feet)


class Problem(Timed):
    def construct(self) -> None:
        cust = load("org0049_customer.json")
        pts = load("org0049_pickups.json")
        n_all = len(pts)
        n_tk = sum(1 for p in pts if p["tk"])
        avg = round(sum(p["f"] for p in pts if p["f"] is not None) / sum(1 for p in pts if p["f"] is not None))
        assert n_all == cust["lifts"] == 395 and n_tk == cust["with_ticket"] == 48 and avg == cust["avg_fill"] == 49

        self.add(data_tag("practice data"))

        # ---------------------------------------------------------------- beat 1: 0 - 5 s
        title = txt("Waste is billed by the tonne", 64, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        self.at(0.3)
        self.p(FadeIn(title, shift=UP * 0.15), rt=0.9, rate_func=EASE)

        left = card(6.0, 4.2).move_to([-3.4, -0.35, 0])
        right = card(5.0, 4.2).move_to([3.6, -0.35, 0])
        tr = truck().scale(1.0).move_to([-3.4, 0.55, 0])
        wb = weighbridge().scale(0.85).move_to([-3.2, -0.55, 0])
        tr.next_to(wb[1], UP, buff=0.0).shift(LEFT * 0.4 + UP * 0.25)
        l_lab = txt("hauler weighs", 40, C["ink"], "MEDIUM").move_to([-3.4, -1.75, 0])
        l_sub = txt("and is paid per tonne", 28, C["muted"]).next_to(l_lab, DOWN, buff=0.15)
        ho = hotel().move_to([3.6, 0.45, 0])
        q = txt("?", 72, C["bad"], "SEMIBOLD").next_to(ho, RIGHT, buff=0.3)
        r_lab = txt("customer: ?", 40, C["ink"], "MEDIUM").move_to([3.6, -1.75, 0])
        r_sub = txt("hotel group · 3 sites · 9 machines", 28, C["muted"]).next_to(r_lab, DOWN, buff=0.15)
        self.p(FadeIn(left, shift=UP * 0.1), FadeIn(tr, shift=RIGHT * 0.3), FadeIn(wb), rt=0.8, rate_func=EASE)
        self.p(FadeIn(l_lab), FadeIn(l_sub), rt=0.5)
        self.at(2.6)
        self.p(FadeIn(right, shift=UP * 0.1), FadeIn(ho), rt=0.6, rate_func=EASE)
        self.p(FadeIn(r_lab), FadeIn(r_sub), FadeIn(q, scale=1.3), rt=0.5)

        # ---------------------------------------------------------------- beat 2: 5 - 10.5 s
        self.at(4.9)
        head = txt("Hospitality Customer 0049 · one year of pickups", 44, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        self.p(FadeOut(VGroup(left, right, tr, wb, l_lab, l_sub, ho, q, r_lab, r_sub)),
               FadeOut(title), FadeIn(head), rt=0.5)

        axis = VGroup(Line([X0, Y0, 0], [X1, Y0, 0], color=C["ink2"], stroke_width=2),
                      Line([X0, Y0, 0], [X0, Y1, 0], color=C["ink2"], stroke_width=2))
        grid = VGroup(*[Line([X0, fy(v), 0], [X1, fy(v), 0], color=C["line"], stroke_width=1.5) for v in (50, 100)])
        ylab = VGroup(*[mono(f"{v} %", 26).next_to([X0, fy(v), 0], LEFT, buff=0.15) for v in (0, 50, 100)])
        ytitle = txt("fill % at emptying", 28, C["ink2"]).next_to([X0, Y1, 0], UP, buff=0.18).align_to([X0 - 0.9, 0, 0], LEFT)
        months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
        xlab = VGroup()
        for i, m in enumerate(months):
            yr, mo = (2025, 10 + i) if i < 3 else (2026, i - 2)
            x = fx(datetime(yr, mo, 15))
            xlab.add(mono(m, 26).move_to([x, Y0 - 0.3, 0]))
        self.p(Create(axis), FadeIn(grid), FadeIn(ylab), FadeIn(ytitle), FadeIn(xlab), rt=0.4)

        dots = VGroup()
        tk_flags = []
        for p in pts:
            d = datetime.strptime(p["d"], "%Y-%m-%d %H:%M")
            f = p["f"] if p["f"] is not None else cust["avg_fill"]  # 1 pickup has no fill reading
            dots.add(Dot([fx(d), fy(f), 0], radius=0.05, color=C["link"]).set_fill(opacity=0.85))
            tk_flags.append(p["tk"])

        n = ValueTracker(0)
        counter = always_redraw(lambda: txt(f"{int(round(n.get_value()))} pickups", 40, C["ink"], "SEMIBOLD")
                                .move_to([X1, 2.55, 0], aligned_edge=RIGHT))
        self.add(counter)
        self.p(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.004),
               n.animate.set_value(n_all), rt=1.5, rate_func=EASE)

        avg_line = DashedLine([X0, fy(avg), 0], [X1, fy(avg), 0], color=C["ink"], stroke_width=3, dash_length=0.12)
        avg_lab = txt(f"avg fill at emptying {avg} %", 28, C["ink"], "MEDIUM")
        avg_bg = RoundedRectangle(width=avg_lab.width + 0.3, height=avg_lab.height + 0.2, corner_radius=0.08,
                                  stroke_width=0).set_fill(C["ground"], 0.92)
        avg_g = VGroup(avg_bg, avg_lab).next_to([X1, fy(avg), 0], UP, buff=0.08).align_to([X1, 0, 0], RIGHT)
        self.p(Create(avg_line), FadeIn(avg_g), rt=0.6)

        # ticket highlight ~ "Only 48 came with a weighing ticket"
        self.at(8.0)
        final = VGroup(
            txt(f"{n_tk}", 40, C["link"], "SEMIBOLD"),
            txt(f"of {n_all} with a weighing ticket", 40, C["ink"], "SEMIBOLD"),
        ).arrange(RIGHT, buff=0.18).move_to([X1, 2.55, 0], aligned_edge=RIGHT)
        grey_anims = [d.animate.set_fill(C["grey"], 0.9) for d, t in zip(dots, tk_flags) if not t]
        tk_dots = VGroup(*[d for d, t in zip(dots, tk_flags) if t])
        self.remove(counter)
        static_counter = txt(f"{n_all} pickups", 40, C["ink"], "SEMIBOLD").move_to([X1, 2.55, 0], aligned_edge=RIGHT)
        self.add(static_counter)
        self.p(*grey_anims, tk_dots.animate.scale(1.35), FadeOut(static_counter), FadeIn(final), rt=0.9, rate_func=EASE)
        # keep ticket dots on top
        self.remove(tk_dots)
        self.add(tk_dots)

        # ---------------------------------------------------------------- beat 3: 10.5 - 15 s
        self.at(10.4)
        chart = VGroup(axis, grid, ylab, ytitle, xlab, dots, avg_line, avg_g, final, head)
        self.p(FadeOut(chart), rt=0.5)

        comp = compactor(avg / 100.0).scale(0.85).move_to([-4.2, 0.1, 0])
        c_lab = txt("Hospitality Customer 0049 · compactor", 28, C["muted"]).next_to(comp, DOWN, buff=0.35)
        self.p(FadeIn(comp, shift=UP * 0.15), FadeIn(c_lab), rt=0.7, rate_func=EASE)

        fill_t = VGroup(txt("fill:", 48, C["ink2"]), txt("known ✓", 48, C["good"], "SEMIBOLD")).arrange(RIGHT, buff=0.2)
        dot_t = txt("·", 48, C["muted"])
        wt_t = VGroup(txt("weight:", 48, C["ink2"]), txt("?", 56, C["bad"], "SEMIBOLD")).arrange(RIGHT, buff=0.2)
        status = VGroup(fill_t, dot_t, wt_t).arrange(RIGHT, buff=0.4).next_to(comp, RIGHT, buff=0.7)
        for m in (fill_t, dot_t, wt_t):
            m.align_to(fill_t[0], DOWN)
        self.p(FadeIn(fill_t, shift=LEFT * 0.2), rt=0.6, rate_func=EASE)
        self.at(12.6)
        self.p(FadeIn(dot_t), FadeIn(wt_t, shift=LEFT * 0.2), rt=0.6, rate_func=EASE)
        self.at(15.0)
