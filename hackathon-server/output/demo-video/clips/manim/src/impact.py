"""impact.mp4 (25.0 s), v2: the business model of 7 Nov 2026.

Beats (times match the captions in timeline.json, segment "impact"):
    0.2 – 7.7   hotel group: cost → savings → three levers → SMART fee (25 %) vs what the customer keeps
    7.8 – 15.6  demo fleet, three sides: customers, partners, Europress
   15.8 – 22.0  next step: weigh a reference group, retrain, roll out as software
   22.1 – 25.0  end card: trust and control

Numbers: src/data/impact_v2.json, written by export_impact_v2.py from the dashboard data
(ORG-0049.json, customers/*.json, operators/*.json). v1 of this scene is kept as impact_v1.mp4.
"""

from __future__ import annotations

from manim import (
    DOWN, LEFT, RIGHT, UP, UL, Arrow, Create, FadeIn, FadeOut, Indicate, LaggedStart, Line,
    Polygon, Rectangle, RoundedRectangle, VGroup,
)

from common import C, EASE, Timed, card, data_tag, eur, load, mono, txt

LEVER_NAMES = {"early_lifts": "empty when full", "sorting": "better sorting", "avoidable_fees": "avoidable fees"}
LEVER_COLS = {"early_lifts": C["mark"], "sorting": C["note"], "avoidable_fees": C["warn"]}
BX0, BX1 = -6.2, 6.2
BW = BX1 - BX0


def k_eur(v: float) -> str:
    """€1,245,163 → €1.25M; €311,291 → €311k."""
    return f"€{v / 1e6:.2f}M" if v >= 1e6 else f"€{v / 1e3:.0f}k"


def bar(x0: float, w: float, y: float, h: float, col: str, op: float = 1.0) -> Rectangle:
    r = Rectangle(width=max(w, 0.001), height=h, stroke_width=0).set_fill(col, op)
    return r.move_to([x0 + w / 2, y, 0])


class Impact(Timed):
    def construct(self) -> None:
        d = load("impact_v2.json")
        cu, fl, ref = d["customer"], d["fleet"], d["reference_group"]
        total, save = cu["total_cost"], cu["savings"]
        levers = sorted(cu["levers"], key=lambda l: -l["eur"])
        assert sum(l["eur"] for l in levers) == save and levers[0]["id"] == "early_lifts"
        assert cu["fee"] + cu["keeps"] == save
        tag = data_tag("practice data · estimate")
        self.add(tag)
        beat1 = self.beat_customer(cu, total, save, levers)
        beat2 = self.beat_fleet(fl, beat1)
        beat3 = self.beat_next(ref, beat2)
        self.beat_end(beat3)

    # ------------------------------------------------------------------ 0.2 – 7.7 s
    def beat_customer(self, cu: dict, total: int, save: int, levers: list[dict]) -> VGroup:
        head = txt(f"{cu['name']} · a year", 44, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        y1, y2, y3 = 1.6, 0.1, -1.55
        share = save / total
        sx0 = BX1 - BW * share

        tot = bar(BX0, BW, y1, 0.62, C["ink"], 0.85)
        tot_lab = txt(f"{eur(total)} waste cost", 38, C["ink"], "SEMIBOLD").next_to(tot, UP, buff=0.16).align_to(tot, LEFT)
        seg = bar(sx0, BX1 - sx0, y1, 0.62, C["mark"])
        gap = Rectangle(width=0.08, height=0.66, stroke_width=0).set_fill(C["ground"], 1).move_to([sx0, y1, 0])
        save_lab = VGroup(txt(f"{eur(save)} SMART can save", 38, C["good"], "SEMIBOLD"),
                          txt(f"({share * 100:.0f} %)", 32, C["good"])).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
        save_lab.next_to(seg, UP, buff=0.16).align_to(seg, RIGHT)

        self.at(0.2)
        self.p(FadeIn(head), rt=0.4)
        grow = tot.copy().stretch_to_fit_width(0.01).align_to(tot, LEFT)
        self.add(grow)
        self.p(grow.animate.become(tot), FadeIn(tot_lab), rt=0.8, rate_func=EASE)
        self.remove(grow)
        self.add(tot)
        self.at(1.5)
        self.p(FadeIn(seg), FadeIn(gap), FadeIn(save_lab, shift=UP * 0.1), rt=0.7, rate_func=EASE)

        # the saving, split into its three levers
        h2 = 0.8
        funnel = Polygon([sx0, y1 - 0.31, 0], [BX1, y1 - 0.31, 0], [BX1, y2 + h2 / 2, 0], [BX0, y2 + h2 / 2, 0],
                         stroke_width=0).set_fill(C["mark"], 0.14)
        blocks, x = VGroup(), BX0
        for l in levers:
            w = BW * l["eur"] / save
            b = bar(x, w, y2, h2, LEVER_COLS[l["id"]], 1 if l["id"] == "early_lifts" else 0.85)
            b.set_stroke(C["card"], 3)
            blocks.add(b)
            x += w
        big = VGroup(txt(LEVER_NAMES["early_lifts"], 32, C["mark_ink"], "SEMIBOLD"),
                     txt(eur(levers[0]["eur"]), 32, C["mark_ink"], "SEMIBOLD")).arrange(RIGHT, buff=0.3).move_to(blocks[0])
        legend = VGroup()
        for l in levers[1:]:
            sw = Rectangle(width=0.24, height=0.24, stroke_width=0).set_fill(LEVER_COLS[l["id"]], 0.85)
            t = VGroup(txt(LEVER_NAMES[l["id"]], 26, C["ink2"]), mono(eur(l["eur"]), 24, C["ink"])).arrange(RIGHT, buff=0.16)
            legend.add(VGroup(sw, t).arrange(RIGHT, buff=0.14))
        legend.arrange(RIGHT, buff=0.55).next_to(blocks, DOWN, buff=0.2).align_to(blocks, RIGHT)
        self.at(2.4)
        self.p(FadeIn(funnel), LaggedStart(*[FadeIn(b, shift=DOWN * 0.08) for b in blocks], lag_ratio=0.25), rt=0.9, rate_func=EASE)
        self.p(FadeIn(big), FadeIn(legend), rt=0.4)

        # who gets the saving: SMART fee (share) vs what the customer keeps
        fee_w = BW * cu["fee_share"]
        fee_b = bar(BX0, fee_w, y3, 0.6, C["ink"], 0.85)
        keep_b = bar(BX0 + fee_w, BW - fee_w, y3, 0.6, C["mark"])
        gap3 = Rectangle(width=0.08, height=0.64, stroke_width=0).set_fill(C["ground"], 1).move_to([BX0 + fee_w, y3, 0])
        fee_lab = VGroup(txt(f"SMART fee · {cu['fee_share'] * 100:.0f} % of the saving", 26, C["ink2"]),
                         txt(eur(cu["fee"]), 34, C["ink"], "SEMIBOLD")).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        fee_lab.next_to(fee_b, DOWN, buff=0.14).align_to(fee_b, LEFT)
        keep_lab = VGroup(txt("the hotel group keeps", 26, C["ink2"]),
                          txt(eur(cu["keeps"]), 34, C["good"], "SEMIBOLD")).arrange(DOWN, aligned_edge=RIGHT, buff=0.06)
        keep_lab.next_to(keep_b, DOWN, buff=0.14).align_to(keep_b, RIGHT)
        self.at(4.0)
        self.p(FadeIn(fee_b, shift=DOWN * 0.08), FadeIn(keep_b, shift=DOWN * 0.08), FadeIn(gap3), rt=0.7, rate_func=EASE)
        self.p(FadeIn(fee_lab), FadeIn(keep_lab), rt=0.5)
        self.at(5.9)
        self.p(Indicate(VGroup(keep_b, keep_lab), color=C["mark"], scale_factor=1.03), rt=0.9)
        return VGroup(head, tot, tot_lab, seg, gap, save_lab, funnel, blocks, big, legend,
                      fee_b, keep_b, gap3, fee_lab, keep_lab)

    # ------------------------------------------------------------------ 7.8 – 15.6 s
    def beat_fleet(self, fl: dict, prev: VGroup) -> VGroup:
        self.at(7.6)
        head = txt("Across the demo fleet, every year", 48, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        self.p(FadeOut(prev), FadeIn(head), rt=0.5)
        tiles = []
        for who, big, sub1, sub2, col in (
            ("customers", k_eur(fl["savings_eur"]), "savings found", f"{fl['customers']} demo customers", C["good"]),
            ("waste-operator partners", f"{fl['trips_saved']:,}", "fewer truck trips", f"{fl['partners']} demo partners", C["ink"]),
            ("Europress", f"≈ {k_eur(fl['fee_eur'])}", "SMART fees", "at a 25 % share of savings", C["ink"]),
        ):
            c = card(3.9, 3.0)
            g = VGroup(mono(who, 24, C["muted"]), txt(big, 76, col, "SEMIBOLD"),
                       txt(sub1, 32, C["ink"], "MEDIUM"), txt(sub2, 26, C["muted"])).arrange(DOWN, buff=0.16)
            g[1].shift(UP * 0.04)
            tiles.append(VGroup(c, g.move_to(c)))
        row = VGroup(*tiles).arrange(RIGHT, buff=0.45).move_to([0, 0.05, 0])
        tiles[2][0].set_stroke(C["mark"], 3)
        for t, start in zip(tiles, (8.2, 10.5, 12.7)):
            self.at(start)
            self.p(FadeIn(t, shift=UP * 0.12), rt=0.6, rate_func=EASE)
        return VGroup(head, row)

    # ------------------------------------------------------------------ 15.8 – 22.0 s
    def beat_next(self, ref: dict, prev: VGroup) -> VGroup:
        self.at(15.6)
        head = txt("Next step: train on real weight", 48, C["ink"], "SEMIBOLD").to_corner(UL, buff=0.6)
        self.p(FadeOut(prev), FadeIn(head), rt=0.5)
        lo, hi = (v // 1000 for v in ref["loadcell_eur_total"])
        steps = (
            ("1", "Weigh a reference group", ["partner weighbridge weights first;",
                                              f"load cells ≈ €{lo}–{hi}k for {ref['machines']} machines"]),
            ("2", "Retrain the model", ["on real weights, tested on", "machines outside the group"]),
            ("3", "Roll out as software", ["to every SMART machine,", "no new hardware"]),
        )
        cards = []
        for n, title, lines in steps:
            c = card(3.9, 2.6)
            num = txt(n, 40, C["mark_ink"], "SEMIBOLD")
            dot = RoundedRectangle(width=0.62, height=0.62, corner_radius=0.31, stroke_width=0).set_fill(C["mark"], 1)
            badge = VGroup(dot, num.move_to(dot))
            body = VGroup(txt(title, 32, C["ink"], "SEMIBOLD"),
                          *[txt(s, 24, C["ink2"]) for s in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            body[1].shift(DOWN * 0.08)
            body[2].shift(DOWN * 0.08)
            g = VGroup(badge, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            cards.append(VGroup(c, g.move_to(c)))
        row = VGroup(*cards).arrange(RIGHT, buff=0.55).move_to([0, 0.15, 0])
        arrs = [Arrow(cards[i].get_right(), cards[i + 1].get_left(), buff=0.06, color=C["ink2"], stroke_width=4,
                      max_tip_length_to_length_ratio=0.35) for i in range(2)]
        note = txt("all figures so far are simulated; this is how they become measured", 26, C["muted"])
        note.next_to(row, DOWN, buff=0.4)
        self.at(16.0)
        self.p(FadeIn(cards[0], shift=UP * 0.12), rt=0.6, rate_func=EASE)
        self.at(17.9)
        self.p(Create(arrs[0]), FadeIn(cards[1], shift=UP * 0.12), rt=0.6, rate_func=EASE)
        self.at(19.4)
        self.p(Create(arrs[1]), FadeIn(cards[2], shift=UP * 0.12), rt=0.6, rate_func=EASE)
        self.p(FadeIn(note), rt=0.5)
        return VGroup(head, row, *arrs, note)

    # ------------------------------------------------------------------ 22.1 – 25.0 s
    def beat_end(self, prev: VGroup) -> None:
        self.at(21.9)
        self.p(FadeOut(prev), rt=0.3)
        e1 = VGroup(txt("SMART Insights", 80, C["ink"], "SEMIBOLD"), txt("·", 80, C["mark"], "SEMIBOLD"),
                    txt("weight at source", 80, C["ink2"])).arrange(RIGHT, buff=0.35)
        rule = Line([-1.2, 0, 0], [1.2, 0, 0], color=C["mark"], stroke_width=6)
        e2 = txt("Europress × Since AI 2026", 40, C["ink2"], "MEDIUM")
        e3 = txt("Europress never sells data. Data is exchanged only when both parties agree.", 28, C["ink"])
        e4 = txt("All data synthetic: Europress practice data + our simulator. Prices hypothetical.", 24, C["muted"])
        e1.move_to([0, 1.3, 0])
        rule.next_to(e1, DOWN, buff=0.2)
        e2.next_to(rule, DOWN, buff=0.3)
        e3.next_to(e2, DOWN, buff=0.55)
        e4.next_to(e3, DOWN, buff=0.25)
        self.p(FadeIn(e1, shift=UP * 0.1), Create(rule), FadeIn(e2), rt=0.7, rate_func=EASE)
        self.p(FadeIn(e3), FadeIn(e4), rt=0.5)
        self.at(25.0)
