
## v2 (round 1 improver, 2026-11-06)

**Restructure, per user direction:** the page is no longer a marketing site. It is now a Verified Weight module inside a thin SMART portal shell (DECISION.md hybrid "H").
- Top bar: SMART portal nav (Fleet · Devices · Reports · SMART Center · Verified Weight NEW), labelled "concept mock, not the real SMART UI". It also has a customer view (sector), the as-of date, a SYNTHETIC DATA badge and the theme switch.
- Left sub-nav, which becomes scrolling tabs under 820 px: Conclusions · Approval lane · Reconciliation · Causes · Proof of Fullness · Device card & drift · Integration · Method & limits. Plain `#hash` routing; old hashes (`#fleet`, `#how`, `#limits`, …) are aliased.
- Removed: the hero, sales copy, the pricing section and the CTAs. Pricing lives in the business explainer.

**Global filters that recompute every evidence view:** hauler, stream, schedule, period and customer view, plus one device-accuracy switch (T0 ±13% / T1 ±12% bias removed / T2 ±1.4% dataset). T0 is the default.

**Conclusions feed:** 10 insight cards computed live from the filtered rows.
- Ranked observed first, then estimated, then hypothetical; "cannot conclude" comes last.
- Every € is per year, with the basis shown.
- Each card has a ± band (95% CI), a rows count, a "Show the math" panel, a suggested action with its proposal id, and "Open the N rows in the grid". The "checked and dismissed" card for the €0 gaps is kept.

**Reconciliation grid:** pre-filtered by the card you came from (outside band / R1 / large gaps / €0 dismissed / stored-tare vehicles). Columns: device ± band | ticket | invoiced | gap | z | cause | status. A row opens the lift detail with the full document chain and a "Show the math" panel with the real numbers substituted.

**Device card:** a Verified Weight strip (30-day kg ± band at the chosen tier, last lift, ticket coverage, median gap, drift watch) and a pickup history with "Weighed" columns marked NEW. These are the two SMART hooks.

**Approval lane:**
- Approve / Hold / Reject. Hold and Reject require a reason, which is stored in the event and the audit log.
- Lifecycle stepper: Created → Reviewed → Approved → Queued → Delivered, where Delivered is production only.
- Focus moves to the result. There is a "Next open proposal" button, the new outbox event is highlighted and an sr-only status line announces it.
- Events are `approval.decided.v1` / `approval.reversed.v1`. The operator API receipt is shown for tare notices.
- The drawer now puts the summary and decision first and the detail after.

**One source of truth:** a `RULES` constant drives the band, the large-gap threshold, R1 (z > 3, > 100 kg), R2 (200 kg), R5 (6%) and R6 (€0). The rules table on Method & limits is rendered from it.

**Accuracy made consistent:**
- T0 is ±12–15% per lift, ≈ ±5–6% monthly.
- T1 is "≈ ±5% monthly (target ±3–5%, untested)", and per lift stays ≈ ±12%. The page now states the measured 2.8% → 2.8% (rolling correction) and 3.0% → 5.3% (naive correction).
- T2 is ±1–2% (≈1.4%).
- The old "T1 ±8%" toggle is gone.

**Method & limits (Part 1):**
- Reference-data note: the dataset's weights are used as ground truth to build, calibrate and evaluate. Being synthetic, with no pressure curves, it cannot prove hardware accuracy; the golden cohort does that.
- Five-step physics chain: P(t) → F = P·A − F_fric(T_oil) → W = ∫F dx → Δm = W/w_mat(σ) → m = g·ΣΔm.
- Sensor placement and installation, calibration scheme, and an options/BOM table (virtual scale, tickets, load-cell platform, strain gauges, load pins, truck scale, camera).
- Error-budget table with T0, T1 and T2 columns.
- Validation plan with acceptance and falsification criteria, a limits list (adds bio 78% vs cardboard 88% within ±10%, Poland BDO untested, press_load_index = fill), the glossary and the simulator.

**AI, made visible and honest:**
- How the module was built, using our own numbers (R1: 25 of 25 flags correct, recall 66%; dataset benchmark rules 0.73 vs GBM 0.35). It states that no LLM bake-off was run.
- P-001 has a clearly labelled pre-written sample LLM draft. The guard runs live in the browser (row citations, numbers ±0.5%, blame words), with a "Try a bad sentence" demo that fails all three checks.

**Over-claims removed:**
- PoF: "only proof" becomes "fill shows it; kg is the only tonnage". Also "45 of 78 labelled lifts", "€327 avg per avoidable lift (fee €409)", and the 9-case range €0–3,951.
- P-005 is now **CTR-00184**. It is €49.1/t vs a €23.5/t peer median (+108%, stream+region, n=21), with 0% tickets and the compactor as the only mass; renegotiate €3,620/yr. It replaces CTR-00142, which is 37% *below* its peer median. This change is in `build_data.py`, and data.json was rebuilt; the build now inlines atomically via a temp file and rename.
- V06 counts are explained: 174 tickets / 137 window lifts / 102 clean pairs.
- Tile 4 now leads with weight-only € (19% of mass-billed €, 77% → 96% coverage, €1,730/yr per mass-billed device).
- Integration: flow diagram (PLC → SMART cloud [exists] → engine in cloud → CloudEvents → portal / ERP / operator API [new]), data-ownership line, and a pilot plan Q1–Q2 2027 with gates.

**UX and accessibility:**
- Charts: a narrow viewBox (560) with min-width and horizontal scroll under 700 px, redrawn on resize.
- No sticky overlap: scroll-margin, and the top bar is static on mobile.
- `--focus` token; dark `--g30`.
- Neutral series colours: fill line grey, sim lines in ink, stored tare in the tare hue; never red for device, ticket or invoice.
- Cause bar labels replaced by a ranked list, "Unlabelled" renamed "Unexplained", PoF kg strip under the fill chart, clipped strip points marked ▲/▼.
- Device table: 25 rows plus "Show all", sticky header, default sort by outside-band.
- Invalid device ids show a message; devices with no tickets get an empty state.
- Jargon tooltips (tare, stored tare, ± band, drift, z, σ) plus a glossary.
- Licence table adds Claude/Anthropic, Google Fonts GDPR, Playwright (test-only) and patents.

**Skipped, and why:**
- Wow 1, the live hero band chart: there is no hero any more. The global T0/T1/T2 switch and the lift band chart cover it.
- Merging the duplicated dark-token block: CSS cannot share it between the media query and the attribute selector without JS. It is kept with a comment, and both copies are updated.
- Roving tabindex on strip dots: time.
- FI/EN toggle and a scorecard dumbbell: time.
- Visual polish: deferred to the designer's theme.css. The CSS is token-only.

**Caveat:** at T0, rule R1 flags 17 lines instead of 25 at T2. Some of the 17 are lifts where only the wide T0 band makes device and ticket "agree" (e.g. COL-00255-0013, −21% side waste). This is shown honestly, live.

Verified: node syntax check, JSDOM click-through of all 8 views with 0 errors, Playwright screenshots `prod_v2*.png` (1280 light, 400 light, dark trace, 400 inbox, method) with 0 console errors. Not published.

## v3: SMART-portal skin, then v4 utilitarian re-palette (designer, 2026-11-06)

Visual/structural only. All content, data, filters, views, insight cards, grid, approval lane, Method & limits and JS unchanged; `build_data.py` still inlines between the same `<script id="data">` markers (untouched). Written atomically (temp file, rename).

**v3 (portal look):** tokens replaced with the real smart.europressgroup.com `:root` set (navy `#214269` chrome, cool-blue actions, ice greys, tangerine notice, its `html.dark-mode` values); Poppins/Roboto; 4 px radii; side nav on navy with a blue active bar; portal-style buttons and tables.

**v4 (utilitarian, user feedback):** re-palette from scratch, see `sites/design/DESIGN_SYSTEM.md` v2.
- One neutral ramp (`#f1f4f6 / #fff / #e3e8ec / #c2cbd3 / #8a95a0 / #626c76 / #3d4750 / #1f2429`), **one action colour** `#1f6fc4` (primary buttons, links, active nav bar, count badge, device series), navy only as chrome; status colours only (ok `#1a7f4b`, warning `#8a5a00`/`#e9b949` incl. the SYNTHETIC badge and simulated chips, serious `#b4432a`). Dark theme on the portal's dark base with `#5aa0ea` actions.
- Series: device action blue, ticket ink `#1f2429`, invoice grey `#8a95a0` — never red/orange for ticket or operator. Cause ramp = blue/grey lightness order + existing hatches.
- Evidence chips neutral, shape/border coded (observed ink, estimated blue, simulated amber dashed, hypothetical grey dotted).
- Flat: no shadows, 3 px radii, hairlines; dense: body 13 px, h1 18 px, KPI 1.2 rem, card padding .7 rem, table cells .32 rem, top bar 44 px, grid gaps .5–.7 rem.
- One font: Roboto, tabular numerals; licence row updated.
- Verified: Playwright 1280 light (#overview, #trace, #inbox, #method, #causes), 400 light (#overview, #trace), 1280 dark (#trace, #inbox), 400 dark (#inbox); 0 console errors in all.

## v5 — R1 design plan (designer, 2026-11-06)

Implements `sites/reviews/r1_product_design_plan.md` steps 1–25 in order. Visual/layout only: content, data, filters, views and JS behaviour unchanged; the `<script id="data">` block is untouched, so `build_data.py` still re-inlines it. Built on a temp copy (`scratchpad/v5/patch.py`) and moved into place atomically.

**Done:**
1. Every SVG is sized to its container (`cw(w, el)`); the 560 px min-width rule is gone. Measured scale 0.999–1.001 for all 8 charts at 1280 and 400, and no figure scrolls at 400. The resize handler re-renders the active chart view when the width changes.
2. Chart text uses only `font-size` 11 and 12.
3. Last x label is end-anchored in the strip, fullness and mass-trace charts; "Jul 2026" is visible. At widths under 520 px the strip and fullness charts show 3 date ticks.
4. Fixed mark sizes, plus a legend under the fullness chart. **Bug fixed:** the `.s-dev` CSS class overrode the `fill="var(--surface)"` attribute, so "hollow" markers (and the mass-trace line) were painted solid. They now use inline `style`.
5. The cause bar, patterns and list share one ranked order. Colour comes from rank (`--cz-1…6`), and navy is gone from the chart.
6–8. Top bar is one 44 px row at 1280 and 1100. At 400 it is 2 rows, 80 px, with the portal links scrolling. The side nav paints the full column.
9–11. KPI strip (one border, no chips on overview); quieter insight cards (scope tag moved to the footer, "Show the math" is a disclosure); kicker colour shows severity only.
12–16. Links in `--wave-ink`. Primary button is action blue (#1f6fc4). Buttons are 26 or 30 px tall. No navy outside chrome and `.seg`. Type is on the px scale. One minus sign (`nf`, axis ticks).
17–25. Status glyphs. Neutral states in the approval lane. Chain IDs break only after a hyphen (`<wbr>`). Chips sit at the end of bullets. Verdict is a single list. Device strip uses auto-fit columns. Drift table header shortened. Outbox/audit split: 8 events take 316 px. Spacing on the 4/8/12/16/24 scale. Dark-mode tweaks.

**Deviations / skipped, and why:**
- Step 1: the resize handler re-renders the panel instead of calling `route()`, because `route()` scrolls to top. It only does so for chart views.
- Step 5: in light mode a white hatch is invisible on the two lightest ranks (and in dark mode on the light ranks), so hatch colour is set per rank (`--czh-N`).
- Step 7: the customer-view select is moved into the filter bar by a small matchMedia script at ≤640 px, and stays in the top bar on wide screens. A static markup move would have conflicted with step 6.
- Step 9: the chipline already carries an Observed chip, so nothing was added there.
- Step 12: `nav.side a{color:inherit}` would have turned the nav text dark on navy, and `.btn{color:inherit}` would have broken secondary buttons, so both get `text-decoration:none` only. In dark mode `--wave-ink` is set to #7fb5f0, as the acceptance criterion requires.
- Step 13: the dark-mode primary keeps dark text for contrast, and is now `:not(:disabled)` so the disabled state shows.
- Step 15: `sub`/`sup` in formulas, and step 20's 10 px inline chips, fall outside the size set. The "NEW" tag in content is neutral grey at weight 500.
- Step 23: events use 4/8 px padding (step 23 wins over step 24). The "JSON" summary sits in the header row so that 8 rows stay ≤420 px.
- Step 25: `--line-strong` equals `--g30` in dark mode (#4d555d, about 2:1). The vehicle bars use the new `--veh-bar` token instead (#7c868f in dark).
- Not in the plan, left as is: the `ⓘ` icon on info kickers renders as a box in headless Chromium (pre-existing).

Verified: `node --check` on the inline script; 24 screenshots `r1i_prod_<view>_<1280|400>_<light|dark>.png`, 0 console errors; approve flow, resize and dark mode spot-checked.
