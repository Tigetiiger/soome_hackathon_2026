# Brand + dashboard design lens: "Verified Weight" as a native Europress SMART product

Method: fetched epsmart.fi HTML and its compiled stylesheet `theme.css` (read 2026-11-06), europressgroup.com HTML and CSS, the SMART features page, Scale Solutions and Scaletipper X1 pages, and the App Store listing. Tags: **[fact]** = read at the cited URL, **[estimate]**, **[assumption]**. All numbers inside wireframes are **illustrative placeholders** to be replaced by pipeline output. Prices and savings are hypothetical.

## 1. What the real identity is (and corrections to the shared brief)

| Item | Finding | Source |
|---|---|---|
| Navy | `#000d61` ("space"). Headings, text on light, footer/hero gradient `#001494` to `#000d61` (180deg) | [fact] epsmart.fi/wp-content/themes/epsmart-theme/dist/styles/theme.css |
| Pink-red | `#ff2962` is an **accent**: tag chips, hover border and title, link underline. It is **not** the button colour | [fact] same |
| Primary CTA | **Mint `#54dea9`** with navy text. Hover `#87e8c3` plus cyan glow `0 6px 30px rgba(51,214,255,.5)`. Active `#29d694`. Focus ring `#c3f3e1` | [fact] same. **Correction: the brief omitted mint** |
| Washes | ice `#e0f1f5` (page background), pink wash `#fff0f4`, mint wash `#ddf8ee`/`#e1f9f0`, greys `#f7f9fc #ecf0f6 #dee5f0 #c9d1de #999ea7 #323d4e` | [fact] same |
| Theme extras | wave `#4b5ac3` (default link), forest `#235041`, autumn `#b95041` (**the theme's error colour**), amber `#fabe69`, fog `#e6e1dc`, cyan `#33d6ff` (image multiply overlay) | [fact] same |
| Fonts | Title: **Loos Wide Bold**, 700, line-height 1.1, navy. Body: Open Sans. Secondary and buttons: Source Sans Pro. Self-hosted woff2 | [fact] same (`--font-family-title/base/secondary`) |
| Heading case | epsmart.fi headings are **sentence case**, not caps ("Reduce your waste management costs and emissions."). **Correction.** Caps appear only on buttons (Source Sans Pro Bold, `letter-spacing:.05em`) and pink tags (Loos Wide 14px). europressgroup.com headings are **caps** ("KEEPING THE VALUE IN CIRCULATION", "SAVE MONEY") on a WordPress "Uncode" theme that loads Montserrat among 8 Google fonts | [fact] both HTML sources |
| Sizes | h1 32px mobile, 52px desktop. h2 22px, 38px. Container 1200px. Nav is white, 72px on desktop | [fact] theme.css |
| Shapes | Buttons: **pill** (`9999px`), padding `1rem 1.5rem`. Arrow button: 44px mint circle. Cards: **16px** (article cards), **24px** (content blocks), hero image 20px. Inputs 8px, tags 16px. Cards are white on ice with a 2px transparent border that turns pink on hover | [fact] theme.css |
| Imagery | Product and site photos, 150x80 client-logo strip (18 logos), cyan multiply duotone over card photos. No data-visualisation style exists publicly [estimate: icon set not inspected] | [fact] HTML/CSS |
| Numbers | Six bare big-number blocks ("40 % lower total waste management costs per year", "58 % higher fill levels"). They are labelled averages and carry **no uncertainty** | [fact] epsmart.fi/en/ |
| Tone | Short, plain, benefit-led. "Fiksumpaa jätehuoltoa, aidosti." CTA "Contact us" | [fact] epsmart.fi |
| Product vocabulary | SMART portal (map + list, Analytics, Reporting incl. "operator service levels and misuse such as overloading"), SMARTwaste app (Quick Order, notifications, estimated fill-up dates, "5 % fill-level accuracy for selected machines" in v1.5.3), SMART Center 24/7, "electronic service book" | [fact] /en/features/, apps.apple.com/bh/app/smartwaste/id1444009270 |
| Scale Solutions | Scaletipper X1 spec table says "Weight accuracy 1.0 kg", "fully integrated in the Europress SMART platform, both our website and our SMARTwaste APP", reports "SMART / XLS / PDF". The scale page makes no legal-for-trade claim | [fact] europressgroup.com/scaletipper-x1/, /scale-solutions/ |
| Limits | No public screenshots of the portal or the Fleet Management UI were found. The App Store page has no screenshot text. **We cannot copy the real portal layout**; the screens below borrow the public web identity only | [fact] absence, searched |

**Design stance.** Take the epsmart.fi look (navy type, white cards on ice, mint pill CTAs, pink accent tags). Differentiate by being honest about uncertainty, which the public SMART stat blocks are not.

## 2. Tokens

```css
:root{
  /* verified from epsmart.fi theme.css */
  --ep-space:#000d61; --ep-space-hi:#001494; --ep-red:#ff2962; --ep-red-wash:#fff0f4;
  --ep-ice:#e0f1f5;  --ep-mint-wash:#ddf8ee; --ep-mint:#54dea9; --ep-mint-hover:#87e8c3; --ep-mint-press:#29d694;
  --ep-cyan:#33d6ff; --ep-wave:#4b5ac3; --ep-forest:#235041; --ep-autumn:#b95041; --ep-amber:#fabe69;
  --ep-g5:#f7f9fc; --ep-g15:#ecf0f6; --ep-g30:#c9d1de; --ep-g100:#323d4e;
  /* ours: AA-safe ink variants (see section 3) */
  --ep-red-ink:#d1003f; --ep-wave-ink:#3a47a8; --ep-green-ink:#0b7a52; --ep-amber-ink:#6b4100;
  --ep-autumn-ink:#9c3a2c; --ep-muted:#5b6577; --ep-amber-wash:#fff4dc;
  --font-title:"Archivo","Montserrat",Helvetica,Arial,sans-serif;   /* stand-in for Loos Wide */
  --font-base:"Open Sans",Helvetica,Arial,sans-serif;
  --font-ui:"Source Sans 3","Source Sans Pro",sans-serif;
  --r-card:1rem; --r-block:1.5rem; --r-input:.5rem; --r-pill:9999px; --container:1200px;
  --glow:0 6px 30px rgba(51,214,255,.5);
}
h1,h2,h3{font-family:var(--font-title);font-weight:700;line-height:1.1;color:var(--ep-space);
  font-stretch:125%;}                       /* Archivo wdth axis; ignored by Montserrat fallback */
.kpi{font-family:var(--font-title);font-variant-numeric:tabular-nums}
.btn{border-radius:var(--r-pill);padding:1rem 1.5rem;font:700 1rem/1 var(--font-ui);
  letter-spacing:.05em;text-transform:uppercase;background:var(--ep-mint);color:var(--ep-space)}
.btn:hover{background:var(--ep-mint-hover);box-shadow:var(--glow)} .btn:active{background:var(--ep-mint-press)}
:focus-visible{outline:3px solid var(--ep-space);outline-offset:2px}  /* site's #c3f3e1 ring is 1.2:1 on white */
```

Tailwind v4: `@theme { --color-space:#000d61; --color-brand-red:#ff2962; --color-ice:#e0f1f5; --color-mint:#54dea9; --color-wave:#4b5ac3; --color-ink-red:#d1003f; --color-ink-green:#0b7a52; --color-ink-wave:#3a47a8; --font-title:"Archivo",sans-serif; --font-sans:"Open Sans",sans-serif; --radius-card:1rem; --radius-block:1.5rem; }`. For v3, put the same keys under `theme.extend.colors/fontFamily/borderRadius`.

**Fonts (no commercial font shipped).** Loos Wide Bold is the only proprietary face and its licence terms are unverified [assumption: treat as commercial]. Open Sans and Source Sans are what Europress already self-hosts, and both are SIL OFL 1.1 [estimate: standard knowledge; confirm in the font package at freeze].

| Role | Use | Licence |
|---|---|---|
| Headings, KPIs | **Archivo** at width 125%, weight 700 (closest free wide grotesque) | SIL OFL 1.1 [fact: github.com/Omnibus-Type/Archivo README]. Width-axis range 62-125 [estimate, verify in the Google Fonts build] |
| Fallback heading | Montserrat 700 (already used on europressgroup.com) | SIL OFL 1.1 [estimate] |
| Body | Open Sans | OFL 1.1 [estimate] |
| Buttons, labels | Source Sans 3 | OFL 1.1 [estimate] |

State on the licence slide: "Heading font is a free look-alike; production would license Loos Wide."

## 3. Contrast and colour (WCAG 2.2 AA, computed with the standard relative-luminance formula)

| Pair | Ratio | Verdict |
|---|---|---|
| Navy `#000d61` on white / ice / red-wash / mint `#54dea9` | 17.1 / 14.7 / 15.5 / 10.1 | AAA |
| **Brand pink `#ff2962` on white** | **3.66** | Fails for normal text. Fine for borders, large text, graphics (3:1). The live site's white-on-pink 14px tags also fail AA |
| Ink red `#d1003f` on white / on `#fff0f4` | 5.55 / 5.03 | Use for small red text and tag fills |
| Wave `#4b5ac3` on white; wave-ink `#3a47a8` on ice | 5.92; 6.83 | Pass |
| Autumn `#b95041` on white / on red-wash | 4.90 / **4.44** | Use autumn-ink `#9c3a2c` (6.23) on tinted backgrounds |
| Forest `#235041` on mint wash | 8.16 | Pass |
| Amber `#fabe69` on white | **1.66** | Fill only, never text. Use `#6b4100` on `#fff4dc` (8.07) |
| Grey `#999ea7` on white | **2.69** | Never for text. Use muted `#5b6577` (5.88) |
| Cyan `#33d6ff`, mint `#54dea9` on white | 1.72, ~1.7 | Fills and glows only |

Rule: **pink is brand accent (selection, hover, tag), never "bad".** Error and severity use autumn, which is the theme's own `--color-error`.

**Chart palette.** Direct labels, shape, and line style always accompany colour. Simulated protan/deutan/tritan separation (Machado matrices, CIE76) was computed.

| Series | Colour | On white | Mark |
|---|---|---|---|
| Device kg (observed device) | `#000d61` | 17.1 | filled circle, solid line, band = 14% navy |
| Ticket kg (weighbridge) | `#0b7a52` | 5.36 | diamond, solid |
| Invoiced kg | `#d1003f` | 5.55 | square, **step** line |
| Cause: sensor drift / stored tare / side waste / combined load / unexplained | `#4b5ac3` / `#b86e00` / `#00789e` / `#b95041` / `#5b6577` | 5.9 / 4.0 / 5.0 / 4.9 / 5.9 | each with a hatch pattern; "unexplained" is grey cross-hatch |

Weights palette min dE under CVD: 16.5 (protan green vs red), backed by marker shape. Cause palette min dE 13.0 (tritan wave vs teal), so patterns and labels are mandatory [estimate: dE76 only, no user test].

**Evidence tags** (all four exist in every table and tooltip; they differ by glyph and border style, not hue alone):

| Tag | Glyph + border | Text / background | Ratio | Meaning |
|---|---|---|---|---|
| OBSERVED | filled dot, solid | `#235041` on `#ddf8ee` | 8.16 | A device reading or an issued document row |
| ESTIMATED | half dot, solid | `#3a47a8` on `#e0f1f5` | 6.83 | Computed from observed rows with a stated interval |
| SIMULATED | diamond, dashed | `#6b4100` on `#fff4dc` | 8.07 | Synthetic hackathon data or future-scenario hardware |
| HYPOTHETICAL | empty ring, dotted, italic | `#323d4e` on `#ecf0f6` | 9.60 | Assumed tariff, price or adoption. Never shown as a saving |

**Severity** (glyph plus label): Info (circle-i, wave-ink on ice 6.83), Notice (triangle, amber-ink on amber-wash 8.07), Warning (diamond, autumn-ink `#9c3a2c` on red-wash 6.23), Critical (square, white on `#d1003f` 5.55). Sensor `FAULT` is Critical; `DEGRADED` is Warning; a lift beyond 2 sigma is Notice. Nothing here is a verdict on an operator.

## 4. Screens

Shared chrome: white 72px nav, logo left, `FI | EN` pill toggle right (plus an "i18n-ready: SV NB PL" note; epsmart.fi already ships 5 languages [fact]). Page on ice `#e0f1f5`, white 16px cards. Footer chip "Synthetic data v1.0.1" (SIMULATED tag) on every screen. Each card shows its evidence tag top-right.

### (a) Fleet overview. Hero: "118 of 142 lifts agree with the weighbridge within the expected band."

```
+------------------------------------------------------------------------------------------+
| [E] SMART  Fleet | Lifts | Discrepancies | Actions (3) | Scorecard | Weighing      FI | EN  |
+------------------------------------------------------------------------------------------+
| Weight you can check                                          Period [Oct 2026 v] [Site v]|
| 118 of 142 lifts reconcile within the expected band.   (heading, Archivo wide, navy)      |
| +--------------------+ +--------------------+ +--------------------+ +------------------+ |
| | COLLECTED   (ESTIM)| | VERIFIED SHARE (OBS)| | OPEN GAPS  (ESTIM) | | ACTIONS WAITING  | |
| | 412.6 t  +/-6.1    | | 83 %               | | 24 lifts           | | 3                | |
| | random error only  | | tickets for 73% of | | 9 above 2 sigma    | | none sent yet    | |
| | ===[----*----]=== | | lifts shared       | |                    | |  [Open inbox >]  | |
| +--------------------+ +--------------------+ +--------------------+ +------------------+ |
| +----------------------------------------------+ +-------------------------------------+ |
| | Devices: gap vs ticket, last 30 days   [map|list]| | Sensor health                    | |
| | DEV-0142 COMBI  cardboard   2.84 t +/-0.19  o | | OK 61 | DEGRADED 3 | FAULT 1       | |
| | DEV-0087 DUO    mixed       3.10 t +/-0.22  o | | Drift suspected: DEV-0311 (Warning) | |
| | DEV-0311 COMBI  bio         1.92 t +/-0.31  ^ | |                                     | |
| |  (o within band, ^ outside; click row > screen b)| | [Why we think so >]                | |
| +----------------------------------------------+ +-------------------------------------+ |
| Footnote: +/- covers sensor noise only. Systematic bias is shown per device, not averaged. |
+------------------------------------------------------------------------------------------+
```
Components: KPI card = white, 16px, big Archivo number, `±` in the same line, evidence tag, one-line plain caption, tiny bullet range glyph. Row status uses glyph + label, not a traffic light. Data: `telemetry_hourly.mass_kg/mass_uncertainty`, `collection_events.weight_reconciliation_status` recomputed as-of.

### (b) Single compactor lift. Hero: "The invoice bills 0.09 t more than the ticket, and device error does not explain that."

```
| DEV-0142 COMBI cardboard | Lift 14 Oct 2026, 09:12 | Hauler Alpha | tare: STORED (not weighed)     |
| Last 12 lifts  gap = ticket - device (t)                                                  |
|  +0.4|            .                                                                       |
|   0  |--.--.--.--.--.-----*--.--.--.--  shaded = +/-1 sigma, light = 2 sigma   (* selected)|
|  -0.4|                                                                                    |
| ------------------------------------------------------------------------------------------|
|  kg axis    2.6 t       2.8        3.0        3.2         3.4                              |
|  Device  (OBS)   2.84 t   |-----[=====o=====]-----|        +/-0.19 sensor                  |
|  Ticket  (OBS)   3.11 t          |---[==<>==]---|          +/-0.12 stored tare            |
|  Invoice (OBS)   3.20 t                      [#]  <- exact (a document, no sensor error)   |
|  Device vs ticket: 0.27 t, expected spread 0.23 t (1.2 sigma)  -> consistent, no action    |
|  Ticket vs invoice: 0.09 t (2.9 %)  -> document mismatch, line HAUL_PER_TONNE  [Why? >]     |
| Evidence rows: collection_events #… | weighbridge_tickets #… | invoice_lines #…             |
| [DRAFT QUERY TO FINANCE]  (opens action in inbox, nothing sent)                           |
```
Components: bullet-range chart (three rows sharing one kg axis), band = interval, overlap shading where bands intersect. The timeline strip above shows lifts in sequence with a residual dot plot. Plain-language verdict line sits under the chart.

### (c) Discrepancy explorer. Hero: "Where devices and tickets disagree, the biggest identified cause is the weighbridge's stored vehicle tare."
(Phrase is a **hypothesis** until validated on real data; mark ESTIMATED and show n.)

```
| Filters: Material [all v] Hauler [all v] Period [90 d v] Min gap [0.2 t v]     n = 318 gaps|
| Cause share of unexplained gap (tonnes-weighted)               ESTIMATED, model v0.3       |
| [##### stored tare 41% #####][=== sensor drift 17% ===][// side waste 12% //][: combined :][xx unexplained 21% xx]
| Lift         Device  Ticket  Gap    Most likely cause (probability)          Evidence       |
| DEV-0142/14  2.84    3.11   +0.27  within noise (0.71)                       OBS OBS        |
| DEV-0311/09  1.92    2.46   +0.54  sensor drift (0.64) / stored tare (0.22)  OBS EST        |
| DEV-0087/22  3.10    3.62   +0.52  combined load, split EQUAL (0.58)         OBS OBS        |
| Right panel: "Why this cause" = 3 evidence bullets, rejected alternatives, [Create action >]|
```
Stacked bar uses the cause palette with hatches; table rows list top-2 causes with probabilities that sum to 1 with "unexplained". Percentages are placeholders. Data: `weighing_event_id`, `allocation_method`, `driver_reported_side_waste`, `stored_tare_kg`, `sensor_status`.

### (d) Recommended actions inbox. Hero: "Three drafts are waiting. Nothing is sent without your approval."

```
| Inbox (3)  [Waiting v]  Sort: expected value                                               |
| +--------------------------------------------------------------------------------------+ |
| | REQUEST_WEIGHBRIDGE_DATA   Hauler Delta   (tag: NOTICE)         Decided by: rule R4  | |
| | Why: 0 of 41 lifts have a ticket; invoice weight cannot be checked.                  | |
| | Evidence  o OBS 41 lifts, 0 tickets   o OBS invoice lines 312-352   <> EST gap +/-   | |
| | Expected value  EUR 30-180 / quarter   (HYPOTHETICAL tariff)  Confidence: medium     | |
| | Draft by AI, checked against 6 source rows: "Dear ... please share weighbridge ..."  | |
| | [APPROVE & SEND]  [Reject]  [Ask for more evidence]     Reversible: yes (recall mail)| |
| +--------------------------------------------------------------------------------------+ |
| | DISPUTE_INVOICE ... | RENEGOTIATE_CONTRACT ... (collapsed rows, same anatomy)         | |
| Audit log: who approved, when, which draft version, which rows were shown.                |
```
Components: primary mint pill APPROVE, secondary white+mint-outline Reject (neutral, never red), arrow-circle for "Ask for more evidence". Show the decision source (rule ID versus AI draft) and an "AI vs rules" mini-badge that links to the bake-off [fact: GBM lost to rules in BENCHMARK.md per red-team-judge.md]. Value is always a range plus tag.

### (e) Operator-neutral scorecard. Hero: "Most of the gap between haulers disappears once sensor drift, stored tare and side waste are taken out."

```
| Hauler (A-Z, not ranked)  Raw gap    After cause adjustment   Data shared   Lifts   Notes  |
| Alpha     +2.1 %  o----|--  0.4 % +/-1.1  o-|-      82 %        58     [Explain]          |
| Bravo     +0.8 %  ...                                91 %        44                        |
| Charlie   +3.5 %  ...    1.9 % +/-1.4     o--|--     51 %        60                        |
| Delta     n/a  "no tickets shared": cannot be scored; request sent? [Open action]  0 %      |
| Epsilon   ...                                                                              |
| Dumbbell: raw gap -> adjusted gap per hauler. Grey band = ESTIMATED measurement noise.       |
| Footer: "Gaps have causes besides the hauler. This page is not a ranking."                 |
```
No red/green. Order alphabetical by default; sorting by value needs an explicit click and shows a banner. Per-row `[Explain]` opens a causes panel as in (c). Missing data shows "insufficient data", never zero.

### (f) Weighing concept explainer (Part 1). Hero: "Start free, add accuracy only where it pays."

```
| TIER 0  INTRO        | TIER 1  INSIGHTS         | TIER 2  INTEGRATED                       |
| Hydraulic signal     | + calibrated by tickets  | + strain or load cells (retrofit kit)    |
| +/-10-12 % target    | target set by validation | accuracy target from hardware lens       |
| BOM ~ EUR 0          | EUR 0 extra hardware     | BOM from hardware lens                   |
| [ASSUMPTION]         | [ASSUMPTION]             | [ASSUMPTION]                             |
| Error budget waterfall: sensor | material | moisture | tare | geometry  ->  total +/-       |
| Validation experiment: steps 1-5 (tickets as reference, bias, interval coverage)          |
```
The ±10-12 % figure is Tommi's stated tolerance (shared brief); tier accuracies are our design targets and must carry the ASSUMPTION tag. Keep this screen static and illustrated; it earns the 25% weighing-concept criterion, not the demo.

## 5. Microcopy (EN, FI) and rules

Europress voice: short declarative, benefit-first, plain verbs. Ours adds a number, an interval and a source.

| EN | FI (needs native review) [assumption] |
|---|---|
| Weigh at source. Check at the invoice. | Punnitse lähteellä. Tarkista laskulta. |
| 2.84 t ±0.19, device estimate | 2,84 t ±0,19, laitteen arvio |
| Within the expected band. | Odotetun vaihteluvälin sisällä. |
| The invoice bills 0.09 t more than the ticket. | Lasku veloittaa 0,09 t enemmän kuin punnituslippu. |
| Device error does not explain this. | Laitteen virhe ei selitä eroa. |
| Gaps have causes besides the hauler. | Erojen syynä voi olla muukin kuin kuljetusliike. |
| Draft by AI, checked against 6 source rows. | Tekoälyn luonnos, tarkistettu kuudesta lähderivistä. |
| Nothing is sent without your approval. | Mitään ei lähetetä ilman hyväksyntääsi. |
| Hypothetical tariff, not a saving. | Kuvitteellinen hinnasto, ei säästö. |
| Not enough data to score. | Tietoa ei riitä arviointiin. |
| Fiksumpaa jätehuoltoa, aidosti. (house line, reuse as is) | (original) |

Rules: use `Intl.NumberFormat('fi-FI')` (decimal comma, narrow no-break space before `t` and `€`, dd.mm.yyyy). Never say "accurate to the kilo", "catches overbilling", "X overcharged you", "saves X %", "AI detected fraud". Say "consistent with", "likely", "needs a look", "ask for". Quote Europress's own claims only with "vendor-reported averages" [fact: epsmart.fi/en/ calls them averages].

## 6. Judge-friendly checklist and open questions

- One hero sentence per screen, written as a claim and a limit. Every number carries a tag. Every action carries a reversal path.
- Screens (b), (c), (d) deliver the "traceable calculation" criterion (20%) and (d) the human-approval requirement. (e) shows neutrality. (f) covers the 25% weighing criterion.
- Open: (1) Will Tommi accept a free heading font, given Loos Wide is the SMART look? (2) The stored-tare share in (c) is a simulator-sensitive hypothesis, so confirm with the analytics lens before wording the hero. (3) Is there any portal screenshot Europress can share? We could not find one publicly. (4) Finnish strings need a native check.
