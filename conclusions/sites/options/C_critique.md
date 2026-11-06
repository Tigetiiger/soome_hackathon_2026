# C critiques A and B (round 2)

Test used: the criteria, Tommi's anchors, and the user's demand: *"an addition to the SMART thing, data displayed, conclusions drawn, like a panel."*

## A: conclusions-first feed

**Strongest points**
1. **Closest to "conclusions drawn, like a panel."** Each finding has one sentence, a € band, a recipient and a CTA.
2. **It shows the engine can say no.** It has a "Checked and dismissed" €0 card, a KPI strip, and a rules page with back-tests.

**Flaws**
1. **The ranking mixes units.** A simulated €3,750 ranks above the hero €121 invoice error, which is the most verifiable finding.
2. **It is a separate module.** SMART integration is asserted rather than shown.
3. **Little data is displayed.** Eight curated cards stand in for 9,062 pairs, and kg ± band per device or lift is barely visible.

## B: reconciliation workbench

**Strongest points**
1. **It shows the denominator.** Facets, saved views and a grid with z, cause and € Δ give the best traceability. The cross-device point is real: one vehicle's tare touches 56 devices.
2. **Bulk approval per counterpart.**

**Flaws**
1. **It is not a panel.** The table is about 4,000 px of rows with a slow "so what", which conflicts with Tommi's readability anchor.
2. **The default view looks noisy.** Its first R1 rows show −1,710 kg "side waste" gaps, and 45 near-identical CMP-00430 rows fill the screen.
3. **It serves auditors, not the facility manager.**

**C's own weaknesses:** it has no fleet view and no ranking, it works one device at a time, and the value has to be clicked to.

## What I would steal

- **From A:** the KPI strip, ranking with "verifiable and actionable now" first, "Checked and dismissed", and Show the math.
- **From B:** saved views and facet counts as the drill-down, bulk select for tare cases, and the z and band per row.

## Recommended design (hybrid)

1. **A Verified Weight panel on the SMART home or fleet page** (A): a KPI strip, the top 3 actionable findings and one "says no" card.
2. **Embedded strips (C):** kg ± band, an agreement badge and a one-line conclusion on the device card, plus "Weighed" columns in emptying history. A toggle shows SMART today vs with the add-on.
3. **Finding → filtered grid (B):** a saved view plus a trace drawer, used as the drill-down rather than the landing page.
4. **The SMART Center queue is the only way out:** approve, hold or reject (bulk per counterpart), with an outbox event and the operator receipt API.
5. **Demo in under 60 s:** panel → hero invoice card → grid row `COL-00392-0032` → approve → event → toggle. Then map it to Intro, Insights and Integrated.
