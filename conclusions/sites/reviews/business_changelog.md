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
