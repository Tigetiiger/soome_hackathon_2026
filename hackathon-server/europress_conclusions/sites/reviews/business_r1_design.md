# Business explainer, round 1: design and front-end QA

Scope: `sites/business/index.html` (1,079 lines), all of the HTML, CSS and JS. I could not take screenshots because the Playwright headless shell is not installed, so this review comes from reading the code. I checked every chart's width against its stated value.

**Passing now.** CSP is clean: Google Fonts only, no remote images or scripts, no fetch, alert or download. Everything is visible at rest. Light and dark tokens are complete in all three required blocks. `body` takes its background from a token. Sentence-case headings. Range inputs have ids, labels and outputs.

## P0: fix before sharing

1. **Horizontal scroll at 400px in the accuracy ladder.** `.err span` uses `position:absolute; left:100%; white-space:nowrap` and `.scale` does not clip. At 400px the scale is about 324px wide. "per lift ±12–15%" starts at 75% and ends near 350px. The golden-cohort label (about 330px of text, starting at 25%) ends near 417px. Both push the page wider than the viewport. Fix: put labels in their own grid column so they cannot overflow. Use `.rung{grid-template-columns:200px 1fr 11rem}`, or below 720px put the label under the bar (`position:static; display:block`). Shorten the golden label to "fleet model 4.96%" and move "literature" into the caption. Add `main{overflow-x:clip}` as a backstop.
2. **The tornado chart has no base line.** `diverge()` draws `.dzero` at 0, but every tornado bar starts at BASE = 230, so bars float with nothing to anchor them. Pass a `ref` value, draw a navy line at 230 with the label "base +230", and keep a light grey line at 0 marked "NPV = 0".
3. **The tornado legend is wrong for 4 of 8 rows.** The legend reads "low input = autumn, high input = green", but the first value is the bad case. For example, "Cost to serve €6 / €2" shows €6 (the higher input) as "low". Rename the legend to "downside case" and "upside case", and write the inputs as "€6 → €2".

## P1: should fix

4. **Value chain (§1): make it a real flow diagram, not text in boxes.** Replace `.chain` with one inline SVG (`viewBox="0 0 960 360"`, scaled with `width:100%`):
   - **Nodes:** four fixed nodes in a row (Customer site, Compactor + SMART, Truck, Weighbridge) and a SMART cloud node above the compactor.
   - **Three flow types, each with its own stroke and an end label:**
     - Material: solid navy, 3px, left to right.
     - Money (invoice): dashed autumn `#b95041`, arcing *under* the nodes from Weighbridge back to Customer. This replaces the `.backflow` text line.
     - Data: dotted wave `#3a47a8`, Compactor → Cloud.
   - **Where weight is measured:** draw a scale glyph and a pink dot at the Weighbridge only, captioned "the only kg today".
   - **Step-by-step buildup (Ciechanowski):** add a segmented control "Today / With our add-ons". The default state is "with add-ons", so everything is visible at rest. It adds a second scale glyph at the compactor ("kg ± band"), a data line Cloud → Customer, and a dotted "tickets, if shared" line Weighbridge → Cloud.
   - **Accessibility and mobile:** the chain must not be `role="img"` (that hides the node lists from screen readers). Keep the node text as an `<ol class="sr-only">` fallback. Below 720px, switch to a vertical SVG (`viewBox` 360×720), either through a second `<svg>` or by toggling `display`.
5. **Accuracy ladder (§3): show uncertainty, not plain bars.** The current bars run from 0 to the upper bound, which hides the fact that "12–15%" is a range.
   - Redraw as symmetric bands on one shared −20…+20% axis, centred on the true value.
   - Each band is solid to the lower bound and hatched (`repeating-linear-gradient`) out to the upper bound.
   - Label the reference lines inline at the axis top ("Tommi ±11%", "pilot gate 6%"). Today they only have `title` tooltips.
   - Put the cost on the left of each rung as a large number (€0 / €0 / €14–26 per month / €10–19k pilot), so the trade-off reads as a ladder.
   - Add a worked example underneath: a row of 8 lift dots, each ±13%, then their sum, "monthly 11.8 t ± 0.7 (±6%)". The caption explains why totals tighten (errors partly cancel). This is the core idea the team must be able to explain.
   - Remove the empty T2 `.err.month` stub (5% wide, blank label).
6. **Offering map (§4): add who buys what.** Turn `.stack` into a matrix.
   - Rows are the four existing layers (navy-bordered boxes, kept as they are).
   - Columns are buyer segments: Everyone (80%) / Chains (20%) / Fixed-schedule / Operators.
   - Each add-on chip sits in its row × column cell, with a 2px mint connector to its layer box instead of the "+" glyph.
   - Distinguish free, paid and bundled by fill as well as colour: free = mint-wash with a dashed border, paid = solid mint, bundled = hatched.
   - Put prices in a right-aligned pill in a fixed position so they scan vertically.
   - Then cut the "Add-on details" table to the three columns the chips lack (benefit, evidence tag, condition), so the same information is not shown twice.
7. **Roadmap (§8): use a time scale.** All four phases are equal width, but they cover 6 months, 6 months, 12 months and an open end.
   - Use a real time axis (Q1 2027 to 2030), with one swimlane per add-on (kg teaser, Verified Weight, Proof of Fullness, Reporting, Operator feed) as bars starting at their launch.
   - Place gate diamonds on the axis, with the kill criteria in autumn `.kill` cards linked to them.
   - Add a small cumulative-spend line that stops at gate 0, labelled "€150k max at risk".
   - On mobile, use a vertical timeline.
8. **Pricing calculator: show the arithmetic (Supabase, Watershed).** The seven equal `.res` cards have no hierarchy.
   - Move `#verdict` to the top.
   - Add a worked-arithmetic block in monospace with tabular numbers: `€15 × 12 = €180/yr` · `€540 ÷ 3 = €180 cap` · `180 ≤ 180 ✓`.
   - Use mint only on the final line.
   - Rename "black line" to "navy line", because in dark mode `--ink` is white. Better still, label the cap directly on the meter.
9. **Use one scale per comparison in §5.** The gap-cause bars use a 0–36.5% scale, the policy bars 0–31.7%, and the verifiable bars 0–100%, all in the same grid. Put every percentage bar in §5 on 0–100%, or on one shared maximum, and draw a faint 25/50/75 grid.
   - Gap causes: group them and draw a bracket labelled "weighbridge-side 77%" across the first three rows. That bracket replaces the nested `.card.mint` boxes, which also removes three levels of nested cards.
10. **Detection power: put both panels in one chart.** Draw one SVG line chart: x = lift / month / quarter / 10 months, y = 0–100% caught, with gridlines.
    - Three lines with direct end labels: σ1.4 +5%, σ1.4 +10%, σ10 +10%. The σ10 line stops at "quarter", and a ghost point marks it as not computed.
    - Add "%" to the values.
11. **Scoring bars (§2): drop the arbitrary colours.** Navy, wave and mint currently mean nothing. Draw the 25 + 25 + 10 that "this page serves" in navy and the others outlined (`background:transparent; box-shadow:inset 0 0 0 2px var(--line)`), as the caption claims.
12. **Mint fills against `--track` in light theme (about 1.5:1).** Non-text graphics need 3:1. Give `.fill.mint`, `.err.month` and `.sb3` a 1px `--green-ink` inset outline, or use `--green-ink` in light theme for data bars and keep mint for chips. The mint range thumb fails the same way: set `accent-color:var(--green-ink)`, or style `::-webkit-slider-thumb` and `::-moz-range-thumb` with a navy border.
13. **Accessibility fixes:**
    - Dots in the "who knows" table carry meaning only in a `title`. Add `<span class="sr-only">yes</span>` and glyphs (●, ◐, ○).
    - `.ladder` has an `aria-label` but no `role`. Give it `role="img"` plus an sr-only table.
    - The theme button's `aria-label` replaces its visible text "Theme: auto" (WCAG 2.5.3). Remove the `aria-label`, or start it with "Theme".
    - Add a skip link to `<main>`.
14. **Clipped stack-bar labels at 400px.** "28% device only" does not fit 28% of about 324px, and `overflow:hidden` cuts it. Put labels above the bar with leader ticks when a segment is under 120px, or move them into a legend below.
15. **NPV chart labels.** "+ renewal & attach: low" sits at −0.83, below the subscription-only −0.33, which reads as if renewal hurts. Rename the rows "Low scenario (with renewal)", and so on, and add a caption: "low also halves adoption".

## P2: polish

16. **Too many font sizes.** There are 13 (.68–1.08rem). Reduce them to 4 tokens: `--fs-xs:.75rem; --fs-s:.875rem; --fs-m:1rem; --fs-l:1.125rem`. Raise `.tag` to at least .72rem (12px).
17. **Load Archivo's width axis to match the brand spec** (Archivo at 125%): `family=Archivo:wdth,wght@125,500;125,700;125,800` and `h1,h2,h3,.big{font-stretch:125%}`.
18. **Make the page less monotonous.** All 13 sections are the same white rounded box on ice, which looks generic. Give the four diagram sections a full-width ice "stage" panel (`.stage{background:var(--ice);border-radius:var(--r-block);padding:24px}`), with a figure caption line under each ("Fig 3 · source · tag", Page B pattern 7). Use question headings for §5 and §6 ("What does a disputed tonne cost?").
19. **Replace inline styles with classes.** Swap the `style="margin-top:20px"` and similar inline rules for a `.stack-l > * + *{margin-top:20px}` rhythm class. Tokenise `.disclaimer` (`--amber-wash`, `--amber-ink`).
20. **Small text fails in dark theme.** `.sb2` is white on `#6f7ce0` in dark (about 3.9:1, small text). Use `color:var(--on-mint)` or darken the dark-theme `--bar-2` to `#5361d6`.
21. **The theme toggle cannot return to "auto".** Cycle auto → light → dark, removing the attribute for auto.
22. **Range sliders read as bare numbers.** Add `aria-valuetext` on the ranges ("€15 per device per month").
23. **Mobile fallback for wide tables.** Below 460px, turn the "Add-on details" table into stacked cards (`display:block` rows with `td::before{content:attr(data-th)}`).
24. **Squares chart counts customers, not value.** The `.squares` chart shows the top 5 of 20 customers but not "75% of value". Replace it with a 100% bar of 20 segments, each as wide as that customer's share of value (Pareto), with the top 5 in pink.
