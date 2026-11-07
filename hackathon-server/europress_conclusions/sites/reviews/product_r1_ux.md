# Product page r1: UX, design and front-end QA

Scope: `sites/product/index.html` (600 KB, 494 KB of it inline JSON). Screenshots failed because no Chromium is installed. This is a full code read, and rendered sizes are calculated from viewBox maths.

**Verdict.** Strong bones: a real data demo, evidence chips everywhere, neutral series colours, "what could make this wrong" on every screen, and an approval gate with CloudEvents. The worst problems are at 400px, plus one honesty slip and one accuracy contradiction.

CSP is clean: Google Fonts only, no fetch, alert, image or download. Storage, clipboard and UUID calls have fallbacks. A `#trace` on the outer claude.ai URL probably does not reach the iframe, so do not promise deep links.

## P0: fix before showing

1. **Charts are unreadable at 400px.** Every `svg.chart` scales a 640–760 viewBox into a ~330px card, so the 11px text renders at **~5px**. Fix: wrap each chart div in `.chart-x{overflow-x:auto}` with `.chart-x svg{min-width:560px}`. Better: pass `W = max(560, el.clientWidth)` into each draw function and redraw on a debounced `resize`.
2. **The sticky header hides the app bar on every tab click.** `showTab` calls `#app.scrollIntoView()`, and the 64px sticky `header.nav` then covers the navy app bar and the top of `.tabs`. At 400px the nav wraps to 2–3 rows, so the tabs are fully hidden. Fix: `#app, section[id]{scroll-margin-top:72px}`. Under 640px, put `nav.top` on one scrolling row (`flex-wrap:nowrap;overflow-x:auto`) or behind a "Menu" button.
3. **The Reject copy claims something false.** It says "Logged with your reason", but no reason is ever asked for (`renderInbox` `.done`). Fix: on Reject, offer 3 radio reasons and store `reason` in the event and audit row, or change the copy to "Rejected and logged".
4. **The accuracy numbers contradict each other.** The Trace tier toggle says `T1 ±8%` per lift (`TIER.T1=.08`). The How-it-works T1 card says per-lift error "stays near ±12%". Fix: relabel to `T1 ±12% (target)`, or drop T1 from the per-lift toggle.

## P1: high value, under an hour each

5. **The hero does not show the differentiator.** `.hero-card` lists `4.125 t / 4.20 t / 5.08 t`, with mixed decimals and **no ± band**, which is the thing no competitor shows. Fix: `4.13 t ± 0.12`, `4.20 t ± 0.32`, `5.08 t (document, exact)`. The "€111.61" is in pink `#ff9db6`, which reads as "bad" against the brand rule. Use white with a `Needs a look` chip.
6. **The first screen tries to say too much.**
   - The eyebrow says "working title". Move it to the footer.
   - Shorten the lead to one sentence: "Verified Weight turns the compactor you already lease into a weight estimate with an honest ± band, checked against the weighbridge ticket and the invoice."
   - Move the chip legend (`.chipline`) to the demo intro.
   - Remove "Tommi's rule" and "Tommi's ±10% ballpark" (#how, `#detTbl` note). A product page does not name a jury member.
7. **The story order buries the best asset.** The demo comes third, after Kalman, CUSUM and NAWI detail. Use the Linear and Sensoneo order: hero → a **stat strip** with 3 tagged numbers (lifts checked, 73.5% with a ticket, 0.88 t invoice gap found) → demo → How it works → integration → pricing → limits.
8. **The series colours break the one-colour-per-source rule.** Source hues are reused for unrelated series:
   - `drawSim`: per-lift = `s-dev`, monthly = `s-tk`. Make both `--navy`/`--wave`, solid vs dashed.
   - `#gapHist`: stored tare = `s-inv` (the invoice colour). Use weighed = `--c-tk` solid and stored = `--cz-tare` dashed, so it matches the Causes screen.
   - `#pofChart`: the fill line is `s-tk`. Use `--line-strong` grey; keep the lift dots on device.
   - `massTrace`: the lift marker is `s-tk`. Use neutral `.ax2`.
9. **Labels collide in the cause bar.** The small_load (6.0%, 44px) % label and the "Device 3.9% →" label share y=78 and **overlap**. Fix: segments under 60px get leader lines to a label row, or a ranked bar list (Tremor) under the bar. Rename "Unlabelled" to "Unexplained", as in the spec.
10. **Proof of fullness has no weight in its chart.** The hero says "the compactor's weight is the only proof", but `#pofChart` plots fill only. Add a kg bar strip per lift below it, and label the dashed line "40% fill".
11. **The inbox drawer puts detail before summary.** The decision buttons sit last, ~900px down. Reorder to title, a p50 value line with its tag, and a **decision bar** (checkbox + Approve / Reject / Ask), then the details. Add `.drawer{max-height:calc(100vh - 88px);overflow:auto}` so the sticky panel cannot hide its buttons.
12. **Approval feedback is weak.**
    - After `act()`, focus is lost because the clicked button is destroyed. Move focus to `.done` (`tabindex=-1`).
    - Add a "Next waiting →" button.
    - The outbox is below the fold. Add "Event `approval.decided` written to the outbox ↓" to `.done`, and give the new `.evt` a brief mint-wash highlight (none under reduced motion).
    - "Ask for more evidence" re-renders the same form with no message. Show "Evidence requested from {to}; the item stays open."
    - Move `aria-live` off the whole drawer onto a small `.sr` status line.
13. **Dark mode gaps.**
    - The focus ring `--wave #4b5ac3` on `#0f1640` is ~2.9:1. Add a `--focus` token (light `#3a47a8`, dark `#9aa6ff`) and use it in `:focus-visible`.
    - `.check input` and `input[type=range]` use `accent-color:var(--navy)`, which is invisible on dark. Use `var(--focus)`.
    - `--g30` vehicle bars are bright on dark. Override it to `#3a4475`.
    - The dark token block is duplicated. Merge the two copies to avoid drift.
14. **Keyboard access.**
    - 200 `tr.click[tabindex=0]` rows put 200 tab stops before Causes. Render 25 rows and add "Show all 447".
    - Strip dots: use a roving tabindex with ←/→, and `.pt:focus-visible circle{stroke:var(--focus)}`, because SVG outlines are unreliable.
    - The theme button's `aria-label="Colour theme"` hides the current state and breaks label-in-name. Remove it.
15. **Trace controls are hard to find.** "Invoice gap / Says no / Stored tare" has only an aria-label. Add a visible `Examples` label. An invalid `#tDev` entry is ignored silently. Devices with no tickets leave empty cards with stale titles; show one empty-state card.

## P2: polish

- The type scale sprawls across 14 sizes (.68–.92rem). Collapse to `.75 / .875 / 1 / 1.125rem` tokens.
- The integration `<table class="card">` loses its radius under `border-collapse`. Wrap it in `div.card`.
- Make the `#devTbl` header sticky: `th{position:sticky;top:0;background:var(--surface)}`. Default-sort by "Outside band", not "€ not needed".
- `.sev` has no glyph. The spec asks for circle-i, triangle and diamond; add them via `::before`.
- The strip chart clips values past ±lim with no marker. Draw ▲/▼ at the edge.
- Vehicle-bar detail is hover-only (`<title>`). Add a "largest 5 offsets" list.
- Performance is fine. `openDevice` renders Trace twice, and compacting `d_eur`/`seq` saves ~60 KB.
- The spec's "FI | EN" toggle and Scorecard screen (e) are missing. (e) fits as a dumbbell chart per hauler: raw gap vs residual after removing explained causes.

## Three wow upgrades (2–3 h each)

**Wow 1: a live lift in the hero (uncertainty bands nobody shows).** Replace the hero card rows with a compact version of `#bandChart`, built from the same `liftStats()` on H1:
- device band, ticket band, an invoice square, and a bracket labelled "+0.88 t outside both bands";
- under it, a 3-button seg `T0 | T1 | T2`, so the device band visibly widens and the verdict line updates.

Static at rest: it says what the product is in 5 seconds, a Greyparrot simulator in one control.

**Wow 2: "Show the math" on every verdict (Watershed / Climatiq lineage).** Add a `<details class="math">` under `#verdict` and under each Fleet tile. A mini stepper runs Inputs (rows with evidence chips) → Formula with real numbers substituted (e.g. `band = 2√(σd² + σt²) = … kg`, `z = (invoice − best) / bsd = …σ`) → Assumptions (tier σ, contract version) → Result. `liftStats` already returns every value, and this makes the 20% "traceable calculation" criterion visible.

**Wow 3: a proposal lifecycle stepper with an outbox pulse (Modern Treasury / Tradeshift).** In each `.pbtn` and at the top of the drawer, add a 5-step stripe: Created → Reviewed → Approved → Queued → Delivered. "Delivered" is greyed with the note "production only". Each step links to its CloudEvent id, and "Reversed" is a side branch. Approving moves the stripe and lights the new event, so human-in-the-loop status shows at a glance.
