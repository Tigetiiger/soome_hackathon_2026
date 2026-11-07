# Business explainer changelog

## v2 (round 1 reviews: clarity + design, plus user feedback)

**Fixed, P0**
- Accuracy ladder: T1 per lift ≈ ±12% (unchanged); T0 per lift ±12–20%, monthly ≈ ±11% until calibrated. Added the worked month (7 lifts → 11.8 t ± 1.3 uncalibrated, ± 0.7 after ~20 clean tickets) and the line "Averaging kills noise, not bias".
- Replaced the 96% detection claim: 62% per quarter at σ 10% for +10% overbilling, and 96% only with the simulated precise sensor.
- Added a "10 words" strip after the hero, about 30 glossary links, and 10+ new glossary entries.
- Explained €1,064 (mean of best contract actions on €13.5k, 7.9%) against the €0 median, and the €532 realisable figure.
- Added the "How does a compactor know kg?" 3-step box. It states that the dataset has no pressure curves.
- At 400px: no horizontal scroll. Labels sit in normal flow, `main{overflow-x:clip}`, and sr-only elements are contained.

**Done, P1**
- Value chain is an SVG with material, money and data flows and a Today / With add-ons toggle. Horizontal and vertical layouts come from one spec, with an sr-only fallback.
- Ladder: symmetric bands on a shared ±20% axis, solid and hatched, cost column, inline reference labels.
- Detection power is one line chart, with a ghost point for the value that was not computed.
- Offering is a buyer-segment matrix; the details table is cut to benefit, evidence and condition.
- Roadmap is a 48-month axis with add-on lanes, gates G0–G3 (incl. the CFO Gate 0 desk test, €25k), kill cards and money at risk.
- Tornado: base line at +0.23, NPV = 0 line, downside/upside legend, inputs written "a → b". NPV and tornado share one €M scale.
- All % bars use 0–100% with a 25/50/75 grid. The 77% bracket is drawn on the chart.
- Calculator:
  - 2-decimal multiple and floored price cap.
  - Verdict comes first; worked arithmetic follows, with mint used only on a passing final line.
  - Our 3× rule and the dataset's 2× are both checked. The base case is shown as 1% short.
  - Revenue on a fail is labelled "if bought anyway". The gain-share line is relabelled.
  - Uses aria-valuetext.
- The ⅓ rule is re-sourced as our own assumption (stricter than the dataset's 2×). Corrected the ESG wording, "rules beat pure ML; rules + ML 0.78 [D]", drift "7 of 19 episodes", €150 = 3% weight, and "no (bias)".
- Reconciled the three revenue figures with a source column and a "why they differ" note.
- Narrative order is now problem → solution → money → execution/risks. The pitch moved to the top. The triangle "Three weights, one truth" is the hero diagram.
- Contrast and accessibility: mint fills have outlines, slider accent is green-ink, dark --bar-2 is darker, the theme cycles auto/light/dark, visible label "Theme", skip link, sr-only dot text and tables, hero tags keep their colours.

**User feedback**
- Jargon is explained inline in plain words. Every `.gl` term also shows a hover/focus/tap tooltip whose text is read from the glossary, so there is one source.
- New section "What the dataset's weights are for: reference answers" with a loop diagram (reference → model → error check → better model). It covers uses a–d and limits (synthetic data, no pressure curves, so the pilot proves real accuracy).

**Done, P2**
- Gate 0 desk test, Archivo width 125 axis, 4 font-size tokens (mostly applied), tokenised disclaimer, ice "stage" panels with Fig captions, question headings.
- Stacked-card tables below 460px.
- Value share shown as a value-weighted 75/25 bar instead of customer squares.

**Skipped, and why**
- True Pareto bar of 20 customers: we have no per-customer shares, and I did not want to invent them.
- PNG export and node side panels for the chain: would need downloads, which hosting forbids, and add complexity.
- Full removal of inline styles: only partly done, to keep the diff safe.
- Gate labels G0/G1 crowd each other at 400px (they are 4 months apart). Left as is.
- Changes to BUSINESS_PLAN.md (T1 accuracy, the 96% figure, the ⅓ rule): this page follows the reviews and the data, but the plan file itself is not edited.

## v3: redesign to the Europress corporate look (designer, 2026-11-06)

Visual/structural only; all content, diagrams, tooltips, calculator logic and the reference-data loop are unchanged. Source of the look: europressgroup.com (WordPress Uncode theme) — see `sites/design/DESIGN_SYSTEM.md` and `theme.css`.

- **Tokens** (light + dark) re-mapped: page white, bands `#f7f7f7`, hairlines `#eaeaea`, text `#303133`, headings/strong navy `#0d426e`, accent cyan `#03b4e0` (fills, rules, TOC marker; text uses `#077a98`, 4.9:1), links `#1c6fc2`, "good" fills seafoam `#72c1a1` (their palette), radii 2–4 px, no card shadows. Dark theme uses the SMART portal's own charcoal set (`#141618 / #1c2022 / #e4e6e6`).
- **Type:** Montserrat (Uncode's declared fallback for bio-sans) for headings, Poppins body; h1 and section h2 UPPERCASE with the short cyan rule, as on europressgroup.com. Archivo/Open Sans removed; footer note updated.
- **Chrome:** white sticky top bar with uppercase brand + "a Europress SMART concept · internal", outlined 2 px-radius theme button; flat TOC with hairline and cyan active marker; sections become hairline-bordered bands that alternate white / `#f7f7f7`; charcoal footer band.
- **Hero:** navy gradient (`#0d426e → #214269`) with the Uncode dark overlay; triangle SVG recoloured (cyan / blue-grey / amber edges, navy boxes); numbered steps cyan.
- **Controls:** segmented control, presets and pills are 2 px-radius uppercase buttons; table headers uppercase 12 px grey.
- **Fixes while restyling:** `.big` stat numbers no longer collide in 3-column grids; theme button no longer overflows at 400 px.
- Verified: Playwright 1280 light and 400 dark, 0 console errors; smooth scroll disabled only in the capture script.

## v4: utilitarian re-palette (designer, 2026-11-06, after user feedback)

User: "rethink the colours and design, and have it more utilitarian." Visual only; content, diagrams, tooltips, calculator and reference-data loop unchanged.

- One neutral cool-grey ramp (`#f1f4f6` page, white surfaces, `#e3e8ec` hairlines, text `#1f2429`), **one action colour** `#1f6fc4` (links, TOC marker, heading rule, blue data series), navy `#214269` only for the wordmark square, the opening section's 3 px top rule and step counters; status colours only (ok green, warning amber, serious red-brown). Dark theme on the SMART portal's dark base.
- Removed: hero gradient and overlay, Montserrat, cyan accent, mint, shadows; radii 3 px; denser spacing (section padding 22 px, cards 12 px, TOC 4 px rows); body 14 px, section titles 16 px uppercase.
- One font: Roboto with tabular numerals.
- Triangle diagram recoloured for a white surface: device edge action blue, no-ticket edge grey, billing-errors edge serious; **ticket box stroke neutral** (not red); boxes 4 px radius.
- Weighbridge-side cause bars are neutral ink, not red; bracket rule neutral. Red remains only for "bad" values (negative NPV, €0 median).
- Verified: 1280 light (hero, §2), 400 dark; 0 console errors.

## v5 — R1 design plan (designer, 2026-11-06)

Implements `reviews/r1_business_design_plan.md` steps 1–25. Visual/layout only; all content, tooltips, diagrams' meaning, calculator logic and the reference-data loop unchanged. Verified: `node --check` on the inline script; full-page shots `reviews/r1i_biz_1280_light.png`, `r1i_biz_1280_dark.png`, `r1i_biz_400_light.png`; 0 console errors at all three.

**Done**
1. Tokens: the three stacked `:root` skins replaced by one token set copied from `theme.css` v2 (light, `[data-theme="dark"]`, and the same dark values in the `prefers-color-scheme` block) plus the plan's alias block, so old class names still work. Computed `--action` is `#1f6fc4` light and `#5aa0ea` dark. Hex appears only in the token blocks.
2. Dead skins removed (marketing gradient hero, words/pitch marketing, Uncode corporate hero, the v4 override layer). One rule per selector. The only non-repeating `linear-gradient` left is `.dot.half`; the bar-track quartile lines are now a `repeating-linear-gradient`.
3. One series rule for bars and stackbars as specified. Legends added under the hbar groups in `#gaps` and `#tommi` (stackbars keep their `.sblegend`). "Tickets only" in the mass-billed bars is now the ink series (ticket = ink), so it differs from "tickets + device weight" (action).
4–6. Hero triangle rebuilt: action-wash device node, ink ticket node, dashed grey invoice node; 3 lines, 3 rects, 5 `<text>` elements; the person icon is gone and the centroid is labelled "a person approves". The stat stacks moved into a 3-column `.tri-notes` row under the SVG, each headed in its edge colour (one column at ≤460 px). Dark mode works because every colour is a class mapped to a token.
7–8. Value chain: node and edge colours as specified. Money is grey dashed. Edge labels are 12 px/500 with a surface halo. The long invoice formula moved into the Fig 1 caption. Legend now has Europress, operator and customer swatches.
9. `#gaps`: two `.stack-l` columns (left: causes, fixed schedules; right: value concentration, device-only check) with `align-items:start`, so cards no longer stretch. At 400 px the card order becomes 1, 3, 2, 4.
10. Red removed from "€0 median", the gate cards (`.kill` neutral) and the "≤ €150k" tile.
11. Roadmap: `.sg.open` is solid ink with a dashed grey end, with no gradient. Phase labels are 500 weight, and the first phase shows "desk" in full at 1280.
12. Ladder: per-lift is light blue `--cz-2`, monthly is action, fleet model is `--n7`. The same mapping is used in the mini-ladder and the legend. The Tommi line is ink and the pilot gate line is ok green.
13. Detection chart: series are ink, action and grey dashed; lines 2 px, markers r = 4 with a surface ring; no red.
14–15. Offering: paid chips are action-wash with a solid action price badge, free chips are dashed, bundled chips are dotted with no hatch. Header rule added. Cells align to the top, and empty cells show an em-dash. `.exist` has a navy left rule.
16. Calculator: fee bar is action, cap line is ink, label reads "Fee (bar) vs cap (line = value ÷ 3)", the range accent is action, presets are sentence case, `.fin.ok` is a wash and `.verdict` has a 1 px border.
17. Roadmap and company-context tiles are now `.kpis` strips with equal-height cells; they stack to one column at ≤720 px.
18. Radii: only `0`, `1px` (tracks and fills), `2px` (tags, segmented control), `3px` (`var(--r)`), `0 3px 3px 0` and `50%`. No 9999 px.
19–20. Spacing set to 4/8/12/16/24. Type: h1 22 px uppercase, h2 16 px, h3 15/500, h4 14/500, `.big` and KPI values 22/500, tags and `th` at 500. No SVG text is under 11 px (measured).
21. No `fill="#…"` anywhere. `#tip` uses n1/n8 with an n4 border.
22. At ≤1000 px the top bar is static and the TOC is sticky at 0. The sticky band measures 44 px at 400 px.
23. `.know` table has `min-width:560px` and scrolls inside `.tbl` (`scrollbar-gutter:stable`). At ≤720 px the gate labels are hidden (diamonds stay) and segment text is 10 px.
24. The SYNTHETIC chip uses the warning fill and is 18 px tall; the theme pill is 28 px, sentence case.
25. Checked with Playwright: blue, red and green appear only in the places §25 allows, plus the amber D tags. Hue count per section is ≤3 except `#weigh` and `#proof` (4: blue, a red `.note.warn`, a green `.note.ok`, amber D tags; all are allowed classes).

**Changes beyond the plan, and why**
- Tokens are inlined instead of linked with `<link href="../design/theme.css">`. The page must stay a single HTML file and an artifact cannot load a relative stylesheet; the values are identical to `theme.css`.
- Added page-level tokens `--chrome-ink` (navy in light, `#9cc3f0` in dark) so navy rules and the T tag stay visible in dark; `--seg-on` (navy in light, action in dark, as DS §4 says); and `--on-warn` / `--on-mid` / `--on-action` for text on fills.
- Roadmap lead "Each pink diamond is a gate" changed to "blue diamond", because the diamonds have been blue since v4.
- Step counters (`.five`, `.steps3`) are ink, not navy, per the §25 navy list. The "a human approves" flow step, the ladder2 top rungs and the gloss `:target` highlight use action-wash instead of green. The "tender or switch" rung is neutral dashed instead of red (DS: no red for operators). The loop's "reference weights" box is action-wash instead of amber.
- At ≤720 px the first phase segment goes back to `overflow:hidden`, because the visible "desk" label overlapped "0 · pilot" at 400 px.

**Skipped / left as is**
- Step 23 right-edge `mask-image` fade: the plan itself drops it in favour of `overflow-x:auto; scrollbar-gutter:stable`.
- Step 3 stackbar mapping: implemented as written (`.sb2` = action for "invoice tonnage only", `.sb3` = grey for "device weight only"). This is the reverse of DS §2.5 (device = action, invoice = grey); swapping the two would match the DS. Flagged for the next round.
- Calculator: "Customer keeps per year" still turns serious-red when negative. The colour is set in JS and changing it would alter JS behaviour; it also counts as a "negative value", which the DS allows.
- Tornado and NPV bars keep red/green (downside/upside), as the plan does not change them.
