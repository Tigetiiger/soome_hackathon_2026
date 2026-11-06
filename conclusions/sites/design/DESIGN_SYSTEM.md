# SMART Verified Weight — design system

**v2, 2026-11-06 ("utilitarian").** Supersedes v1 of the same day after user feedback: *"rethink the colours and design, and have it more utilitarian."* One neutral palette, one action colour, semantic status colours only; flat surfaces, thin rules, dense information-first layouts, one type family with tabular numerals, no gradients/illustrations/hero blocks/shadows. Still recognisably Europress SMART: the portal's navy chrome and its blue for actions.

Scope: (1) **Product** — an add-on panel inside the Europress SMART portal (`sites/product`). (2) **Business explainer** — internal plan document (`sites/business`). Both consume `theme.css`.

Tags: **[fact]** read at the cited URL on 2026-11-06; **[derived]** our AA-safe variant; **[decision]** our choice.

## 1. What the real surfaces look like (research, unchanged from v1)

| Surface | Look [fact] | What we keep |
|---|---|---|
| **smart.europressgroup.com** (the SMART portal; React + Tachyons; CSS bundle `/assets/index-Ga-EnddW.css`) | `:root` tokens: `--col-214269 #214269` (navy chrome, app "Order Maintenance" button), `--twilight-blue #0d477d`, `--cool-blue #2c83d7`, ice greys `#f8fafb/#eff3f6/#e1e9f1`, `--background #fafbfc`, `--seafoam-blue #72c0a2`, `--tangerine #ff9800`, `--col-1-c-2020 #1c2020`; body stack `-apple-system, …, Poppins, Roboto, Europress`; `html.dark-mode` = `#1c2022` bg, `#2a2e30` bar, `#f0f1f1` text, `#51a8ff` links. SMARTwaste App Store shots: navy top bar, white sheet, full-width navy button, grey tab bar, orange map pins | Navy chrome, blue-for-action idea, grey family, dark-mode base, Roboto |
| **europressgroup.com** (WordPress Uncode) | white / `#f7f7f7` bands, text `#303133`, cyan `#03b4e0` accent, UPPERCASE bio-sans/Montserrat headings, 2 px-radius outlined buttons, `#141618` footer, photo heroes with dark overlay | Uppercase section titles with a short rule (document only) |
| **epsmart.fi** (SMART marketing) | space navy `#000d61`, mint pill CTAs `#54dea9`, pink tags `#ff2962`, Loos Wide, cards on ice | Nothing (marketing palette, not the app) |

## 2. The v2 palette (from scratch) — `theme.css` is the source of truth

### 2.1 Neutral ramp (cool grey, one hue) [decision, derived from the portal's ice greys and `#1c2020`]

| Token | Light | Dark | Use | Contrast (light, on white) |
|---|---|---|---|---|
| `--n0` | `#ffffff` | `#1e2226` | surface | |
| `--n1` | `#f7f9fa` | `#262b30` | zebra, panels, table head | |
| `--n2` | `#f1f4f6` | `#16191c` | page background | |
| `--n3` | `#e3e8ec` | `#343a40` | hairline | |
| `--n4` | `#c2cbd3` | `#4d555d` | strong line, control border, axis | |
| `--n5` | `#8a95a0` | `#7c868f` | 3rd data series, disabled ink — **never body text** | 3.0:1 |
| `--n6` | `#626c76` | `#a4adb5` | muted text | 4.8:1 |
| `--n7` | `#3d4750` | `#cfd5da` | secondary text, 2nd data series | 9.0:1 |
| `--n8` | `#1f2429` | `#eef1f3` | text, headings, "observed" | 16:1 |

### 2.2 Chrome (the only navy) [fact: portal `--col-214269`]
`--chrome #214269` (dark `#111417`), `--chrome-text #fff`, `--chrome-muted #b8c6d6` (6.4:1 on navy). Used **only** for the top bar, side nav, count badges, the document's 3 px top rule and wordmark square, and the segmented-control "on" state. Not for headings, not for data.

### 2.3 One action colour [derived from portal `--cool-blue #2c83d7`, darkened to pass AA as text]
`--action #1f6fc4` (5.1:1 on white; white on it 5.1:1), hover `#185ca6`, press `#134a86`, wash `#e8f0fb`. Dark: `#5aa0ea` with `#0b1a2b` text. Every interactive thing is this colour and nothing non-interactive is (exception: the device series in charts, see 2.5, because "device" is the thing the user acts on).

### 2.4 Semantic status (icon + label always; never colour alone)
| | ink | fill | wash |
|---|---|---|---|
| ok | `#1a7f4b` | — | `#e3f1e8` |
| warning / synthetic / simulated | `#8a5a00` | `#e9b949` | `#f6ecd6` |
| serious | `#b4432a` text `#9a3a24` | — | `#f7e4df` |

The SYNTHETIC DATA badge is the warning fill with ink text. Red is never applied to the ticket, the operator or a hauler; it marks only invoice errors, negative NPV and critical faults.

### 2.5 Data colours (no new hues)
- Series: **device** `--action`, **ticket** `--n8` (ink, diamond marker), **invoice** `--n5` (grey, dashed line, square marker). Bands: 14 % action / 10 % ink.
- Cause ramp (ordered by rank, each with its own hatch): `#1f6fc4 #7fa8dc #3d4750 #8a95a0 #c5ccd3 #214269`. Lightness order = rank order, so the bar reads without the legend.
- Evidence chips are shape- and border-coded (filled dot solid / half dot solid / diamond dashed / ring dotted italic) on neutral washes: observed = ink, estimated = action, simulated = warning, hypothetical = muted.
- Explainer tags: F fact (ink solid), T Tommi (chrome), D synthetic data (warning dashed), E estimate (action), A assumption (muted dotted italic).

### 2.6 Type
**Roboto** only (Google Fonts; OFL 1.1, static builds Apache 2.0) — it is in the portal's own stack and has tabular lining figures (`font-variant-numeric: tabular-nums` set on `body`). Panel scale: 11 / 12 / **13** / 14 / 16; h1 18 / h2 16 / h3 14, weight 500; KPI 22 / 500. Document scale: body 14, h1 22 uppercase 700, section h2 16 uppercase 700 + 32 px action rule, h3 15/500. Sentence case everywhere else; uppercase only for 11 px labels and document section titles.

### 2.7 Shape and rhythm
Radius 3 px everywhere (2 px on document buttons). No box shadows. 1 px hairlines `--n3`; strong lines `--n4`. Spacing 4/8/12/16/24. Top bar 44 px, side nav 200 px, card padding 8–12 px, table cells 5 × 8 px, grid gaps 8–12 px.

## 3. Components (`theme.css`)
Portal shell (`.ep-portal`, `.ep-topbar`, `.ep-sidenav`), view header with one claim sentence, **KPI strip** `.ep-kpis` (several KPIs in one bordered row — preferred over tiles), insight card `.ep-insight` (3 px status bar, kicker + chip, claim, why, actions), chips `.ep-chip--obs|est|sim|hyp|synthetic`, status `.ep-status--*`, buttons (`--primary` action blue, `--secondary` outlined, `--ghost`), controls (select, segment, tabs), table `.ep-table` (uppercase 11 px head on `--n1`, right-aligned tabular numbers, action-wash selected row), drawer `.ep-drawer`, chart classes (`.s1/.s2/.s3`, band, recessive grid), `.ep-foot`. Document skin `.ep-doc` (topbar, toc, sections alternating `--n0/--n1`, opening section with navy top rule, `.tag.*`, notes, footer).

## 4. Light / dark
Light is the default. Dark re-maps the neutral ramp onto the portal's own dark base (`#16191c/#1e2226/#262b30`, text `#eef1f3`), action `#5aa0ea`, status inks lightened; segmented "on" and primary buttons become action blue with dark text. Both pages expose `data-theme=auto|light|dark` and honour `prefers-color-scheme`.

## 5. Do / don't
**Do**: one claim per screen; every number carries a chip; every action shows its decision source and reversal path; tabular numerals and `fi-FI` formatting; alphabetical haulers; "Not enough data" instead of 0; hatch + lightness order on categorical bars; a legend for ≥ 2 series.
**Don't**: no Europress logo/photos/icon font (wordmark text "SMART" + "Verified Weight", "a Europress SMART concept"); no navy outside chrome; no colour that is not in §2; no gradients, shadows, illustrations, hero blocks or oversized headings; no red for ticket/operator; no `--n5` as text; no dual axes; no remote assets (Google Fonts stylesheet only).

## 6. Files
- `theme.css` — v2 tokens and components (both skins).
- `comp.html`, `comp.png` — the **v1** comp (portal + corporate look), kept for the record; the live pages are the v2 reference now.
- Applied: `sites/business/index.html` (v4) and `sites/product/index.html` (v4); see `sites/reviews/*_changelog.md`.
