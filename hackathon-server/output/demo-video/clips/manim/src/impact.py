"""impact.mp4 (25.0 s): value for the customer and for Europress.

Numbers: src/data/org0049_customer.json (dashboard ORG-0049.json),
src/data/impact_sources.json (09_summary.log, NUMBERS.md §6, SENSOR_RESEARCH.md).
"""

from __future__ import annotations

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, Arrow, Create, FadeIn, FadeOut, Indicate, LaggedStart,
    Line, Polygon, Rectangle, RoundedRectangle, ValueTracker, VGroup, always_redraw,
)

from common import C, EASE, Timed, card, data_tag, eur, load, mono, txt

LEVER_NAMES = {"early_lifts": "empty when full", "tender": "tender", "sorting": "sorting",
               "avoidable_fees": "avoidable fees", "invoice_check": "invoice check"}
LEVER_COLS = {"early_lifts": C["mark"], "tender": C["link"], "sorting": C["note"],
              "avoidable_fees": C["warn"], "invoice_check": C["muted"]}
BX0, BX1 = -6.2, 6.2


class Impact(Timed):
    def construct(self) -> None:
        cu = load("org0049_customer.json")
        src = load("impact_sources.json")
        total, save = cu["total_cost"], cu["savings"]
        levers = sorted(cu["levers"], key=lambda l: -l["eur"])
        assert sum(l["eur"] for l in levers) == save
        share = save / total
        self.add(data_tag("practice data · estimate"))

        # ------------------------------------------------------------ beat 1: 0 - 6.7 s
        head = txt("Hospitality Customer 0049 · cost per year", 44, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        W = BX1 - BX0
        y1 = 0.95
        bar = Rectangle(width=W, height=0.7, stroke_width=0).set_fill(C["ink"], 0.85).move_to([0, y1, 0])
        tot_lab = txt(f"{eur(total)} a year", 40, C["ink"], "SEMIBOLD").next_to(bar, UP, buff=0.18).align_to(bar, LEFT)
        self.at(0.2)
        self.p(FadeIn(head), rt=0.4)
        bar_grow = bar.copy().stretch_to_fit_width(0.01).align_to(bar, LEFT)
        self.add(bar_grow)
        self.p(bar_grow.animate.become(bar), FadeIn(tot_lab), rt=0.9, rate_func=EASE)
        self.remove(bar_grow)
        self.add(bar)

        sx0 = BX1 - W * share
        seg = Rectangle(width=W * share, height=0.7, stroke_width=0).set_fill(C["mark"], 1)
        seg.move_to([(sx0 + BX1) / 2, y1, 0])
        gap = Rectangle(width=0.08, height=0.74, stroke_width=0).set_fill(C["ground"], 1).move_to([sx0, y1, 0])
        save_lab = VGroup(txt(f"{eur(save)} saveable", 40, C["good"], "SEMIBOLD"),
                          txt(f"({share * 100:.0f} %)", 34, C["good"])).arrange(RIGHT, buff=0.25, aligned_edge=DOWN)
        save_lab.next_to(seg, UP, buff=0.18).align_to(seg, RIGHT)
        self.at(1.7)
        self.p(FadeIn(seg), FadeIn(gap), FadeIn(save_lab, shift=UP * 0.1), rt=0.8, rate_func=EASE)

        # expanded saveable bar
        y2 = -0.85
        H2 = 0.95
        funnel = Polygon([sx0, y1 - 0.35, 0], [BX1, y1 - 0.35, 0], [BX1, y2 + H2 / 2, 0], [BX0, y2 + H2 / 2, 0],
                         stroke_width=0).set_fill(C["mark"], 0.14)
        blocks = VGroup()
        x = BX0
        for l in levers:
            w = W * l["eur"] / save
            b = Rectangle(width=w, height=H2, stroke_color=C["card"], stroke_width=3)
            b.set_fill(LEVER_COLS[l["id"]], 1 if l["id"] == "early_lifts" else 0.85)
            b.move_to([x + w / 2, y2, 0])
            blocks.add(b)
            x += w
        big = levers[0]
        assert big["id"] == "early_lifts"
        big_lab = VGroup(txt(LEVER_NAMES[big["id"]], 36, C["mark_ink"], "SEMIBOLD"),
                         txt(eur(big["eur"]), 36, C["mark_ink"], "SEMIBOLD")).arrange(RIGHT, buff=0.35)
        big_lab.move_to(blocks[0])
        self.at(2.7)
        self.p(FadeIn(funnel), FadeIn(blocks[0], shift=DOWN * 0.1), rt=0.7, rate_func=EASE)
        self.p(FadeIn(big_lab), rt=0.4)

        legend = VGroup()
        for l in levers[1:]:
            sw = Rectangle(width=0.26, height=0.26, stroke_width=0).set_fill(LEVER_COLS[l["id"]], 0.85)
            t = VGroup(txt(LEVER_NAMES[l["id"]], 28, C["ink2"]), mono(eur(l["eur"]), 26, C["ink"])).arrange(RIGHT, buff=0.18)
            legend.add(VGroup(sw, t).arrange(RIGHT, buff=0.15))
        legend_cols = VGroup(VGroup(legend[0], legend[2]).arrange(DOWN, aligned_edge=LEFT, buff=0.22),
                             VGroup(legend[1], legend[3]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
                             ).arrange(RIGHT, buff=0.6, aligned_edge=UP)
        legend_cols.next_to(blocks, DOWN, buff=0.3).align_to(blocks, RIGHT)
        self.p(LaggedStart(*[FadeIn(b) for b in blocks[1:]], lag_ratio=0.2), FadeIn(legend_cols), rt=0.9, rate_func=EASE)
        self.at(4.9)
        self.p(Indicate(VGroup(blocks[0], big_lab), color=C["mark"], scale_factor=1.04), rt=0.9)

        # ------------------------------------------------------------ beat 2: 6.9 - 12.3 s
        self.at(6.6)
        beat1 = VGroup(head, bar, tot_lab, seg, gap, save_lab, funnel, blocks, big_lab, legend_cols)
        head2 = txt("Pickups with an independent weight", 52, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        src2 = txt("practice data, all customers", 28, C["muted"]).next_to(head2, DOWN, aligned_edge=LEFT, buff=0.15)
        self.p(FadeOut(beat1), FadeIn(head2), FadeIn(src2), rt=0.5)

        a = round(src["fleet_ticket_share"] * 100)
        b = round(src["fleet_ticket_or_device_share"] * 100)
        TX0, TW = -2.0, 7.6
        rows = []
        for i, (lab, sub, v, col) in enumerate([
            ("today", "weighing ticket", a, C["link"]),
            ("with machine weight", "ticket or device weight", b, C["mark"]),
        ]):
            y = 0.45 - i * 1.8
            l1 = txt(lab, 36, C["ink"], "MEDIUM")
            l2 = txt(sub, 28, C["muted"])
            lg = VGroup(l1, l2).arrange(DOWN, aligned_edge=RIGHT, buff=0.08).move_to([TX0 - 0.35, y, 0], aligned_edge=RIGHT)
            track = RoundedRectangle(width=TW, height=0.7, corner_radius=0.1, stroke_color=C["line"], stroke_width=2)
            track.set_fill(C["card"], 1).move_to([TX0 + TW / 2, y, 0])
            tr = ValueTracker(0.0)

            def mk(tr=tr, y=y, col=col):
                w = max(TW * tr.get_value() / 100, 0.001)
                return Rectangle(width=w, height=0.7, stroke_width=0).set_fill(col, 1).move_to([TX0 + w / 2, y, 0])

            def mkv(tr=tr, y=y, col=col):
                fg = C["mark_ink"] if col == C["mark"] else C["card"]
                t = txt(f"{tr.get_value():.0f} %", 40, fg, "SEMIBOLD")
                w = TW * tr.get_value() / 100
                return t.move_to([TX0 + max(w, t.width + 0.4) - 0.2, y, 0], aligned_edge=RIGHT)

            rows.append((lg, track, tr, mk, mkv, v))

        for k, start in ((0, 7.1), (1, 9.0)):
            lg, track, tr, mk, mkv, v = rows[k]
            self.at(start)
            fill = always_redraw(mk)
            val = always_redraw(mkv)
            self.p(FadeIn(lg), FadeIn(track), rt=0.4)
            self.add(fill, val)
            self.p(tr.animate.set_value(v), rt=1.1, rate_func=EASE)
            rows[k] = (lg, track, tr, fill, val, v)
        arrow = Arrow([TX0 + TW * a / 100, 0.05, 0], [TX0 + TW * b / 100, -0.95, 0], buff=0.05,
                      color=C["good"], stroke_width=4, max_tip_length_to_length_ratio=0.2)
        self.p(Create(arrow), rt=0.4)

        # ------------------------------------------------------------ beat 3: 12.5 - 18.9 s
        self.at(12.1)
        beat2 = VGroup(head2, src2, arrow, *[VGroup(r[0], r[1], r[3], r[4]) for r in rows])
        head3 = txt("For Europress: weight makes SMART stickier", 42, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        self.p(FadeOut(beat2), FadeIn(head3), rt=0.5)

        fleet = src["fleet_machines_assumed"]
        machines = round(fleet / 100)
        price = src["list_price_eur_per_machine_month"]
        per_year = machines * price * 12
        cards = []
        for big_t, small_t, col in (("+1 pp", "SMART adoption", C["ink"]),
                                    (f"≈ {machines}", "machines", C["ink"]),
                                    (f"≈ {eur(per_year)}", "per year", C["good"])):
            cc = card(3.7, 2.3)
            t1 = txt(big_t, 64, col, "SEMIBOLD")
            t2 = txt(small_t, 32, C["ink2"])
            VGroup(t1, t2).arrange(DOWN, buff=0.15).move_to(cc)
            cards.append(VGroup(cc, t1, t2))
        row = VGroup(*cards).arrange(RIGHT, buff=0.9).move_to([0, 0.2, 0])
        cards[2][0].set_stroke(C["mark"], 3)
        arrs = [Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=0.12, color=C["ink2"], stroke_width=4,
                      max_tip_length_to_length_ratio=0.3) for i in range(2)]
        est = txt(f"estimate: ~{fleet // 1000}k fleet, €{price} per machine per month", 28, C["muted"])
        est.next_to(row, DOWN, buff=0.45)

        self.at(13.4)
        self.p(FadeIn(cards[0], shift=UP * 0.1), rt=0.6, rate_func=EASE)
        self.at(15.4)
        self.p(Create(arrs[0]), FadeIn(cards[1], shift=UP * 0.1), rt=0.6, rate_func=EASE)
        self.at(16.6)
        self.p(Create(arrs[1]), FadeIn(cards[2], shift=UP * 0.1), rt=0.6, rate_func=EASE)
        self.p(FadeIn(est), rt=0.5)

        # ------------------------------------------------------------ beat 4: 19.1 - 23 s
        self.at(18.8)
        beat3 = VGroup(head3, row, *arrs, est)
        self.p(FadeOut(beat3), rt=0.4)

        p95 = src["hardware_study_pressure_p95_pct"]
        hw = VGroup(mono("hardware study", 26, C["warn"]),
                    txt(f"pressure-only P95 error {p95} %, so we test before we build", 30, C["ink2"])).arrange(RIGHT, buff=0.3)
        hw_box = RoundedRectangle(width=hw.width + 0.6, height=hw.height + 0.4, corner_radius=0.12,
                                  stroke_color=C["warn"], stroke_width=2).set_fill(C["card"], 1)
        hw_g = VGroup(hw_box, hw.move_to(hw_box)).move_to([0, 2.3, 0])
        step = txt("Step 1: a €0 test", 88, C["ink"], "SEMIBOLD").move_to([0, 0.55, 0])
        subl = txt("archived SMART pressure curves from 10–30 machines vs weighbridge tickets", 34, C["ink2"])
        subl.next_to(step, DOWN, buff=0.35)
        self.p(FadeIn(hw_g, shift=DOWN * 0.1), rt=0.6, rate_func=EASE)
        self.at(20.6)
        self.p(FadeIn(step, shift=UP * 0.15), rt=0.7, rate_func=EASE)
        self.p(FadeIn(subl), rt=0.5)

        # ------------------------------------------------------------ beat 5: 23 - 25 s
        self.at(22.8)
        self.p(FadeOut(VGroup(hw_g, step, subl)), rt=0.3)
        e1 = VGroup(txt("SMART Insights", 80, C["ink"], "SEMIBOLD"), txt("·", 80, C["mark"], "SEMIBOLD"),
                    txt("weight at source", 80, C["ink2"])).arrange(RIGHT, buff=0.35)
        e2 = txt("Europress × Since AI 2026", 40, C["ink2"], "MEDIUM")
        e3 = txt("All data synthetic: Europress practice data + our simulator. Prices hypothetical.", 26, C["muted"])
        end = VGroup(e1, e2, e3).arrange(DOWN, buff=0.45).move_to([0, 0.6, 0])
        rule = Line([-1.2, 0, 0], [1.2, 0, 0], color=C["mark"], stroke_width=6).next_to(e1, DOWN, buff=0.2)
        e2.next_to(rule, DOWN, buff=0.3)
        e3.next_to(e2, DOWN, buff=0.45)
        self.p(FadeIn(e1, shift=UP * 0.1), Create(rule), FadeIn(e2), FadeIn(e3), rt=0.7, rate_func=EASE)
        self.at(25.0)
