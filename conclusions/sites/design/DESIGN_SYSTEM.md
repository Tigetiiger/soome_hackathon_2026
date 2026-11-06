# SMART Verified Weight — design system (Phase 1)

Scope: two sites. (1) **Product**: an add-on panel *inside* the Europress SMART portal (app shell, dense, operational, auto-generated conclusions). (2) **Business explainer**: internal business-plan page. Both must read as Europress, not as a generic hackathon template.

Everything below was read on 2026-11-06 from the sources cited. Tags: **[fact]** read at the URL; **[derived]** our AA-safe variant of a brand colour; **[decision]** our choice.

## 1. Which real look for which page, and why

Europress has **three** public visual identities, not two:

| Surface | What it is | Look | Use it for |
|---|---|---|---|
| **smart.europressgroup.com** (the SMART portal, React + Tachyons) | What the CIO and every customer sees daily when they log in. Its CSS bundle is public: `/assets/index-Ga-EnddW.css` | Navy `#214269` chrome, cool-blue `#2c83d7` actions, ice-blue greys, tangerine alerts, Poppins/Roboto system stack, 4 px radii, dark-mode variant built in | **Product add-on panel** (shell, Overview, detail screens, drawer) |
| **epsmart.fi** (SMART marketing site) | Sales site for SMART | Space navy `#000d61`, mint pill CTAs `#54dea9`, pink tags `#ff2962`, Loos Wide headings, sentence case, white cards on ice `#e0f1f5` | Not used as the base (it is a brochure, the product is not). Its *evidence-chip* idea and plain-verb tone carry over |
| **europressgroup.com** (corporate, WordPress Uncode) | Group site | White + `#f7f7f7` bands, charcoal footer `#141618`, text `#303133`, cyan accent `#03b4e0`, **UPPERCASE** bio-sans/Montserrat headings, 2 px-radius outlined buttons, dark photo heroes with overlay, dashed rule under headings | **Business explainer** |

**Decision.** The product lives in the portal, so it inherits the portal's own tokens (the only honest "native" look; the two SMARTwaste app screenshots in the App Store confirm the same navy top bar / white sheet / full-width navy button / light-grey tab bar). The explainer is a corporate document, so it takes the europressgroup.com look. Both share one `theme.css`; the corporate skin is a class (`.ep-corp`), so tokens, chips and tables stay consistent across the two.

Why not epsmart.fi's mint-and-pink for the product: it is a marketing palette; nothing in the portal uses mint pills or pink tags, and the CIO would read them as "not our app". We keep mint only as a possible *marketing* accent and do not use it in the panel.

## 2. Verified tokens

### 2.1 Portal (product) — source: `https://smart.europressgroup.com/assets/index-Ga-EnddW.css` `:root` [fact]

| Token (theirs) | Hex | Role we give it | Contrast |
|---|---|---|---|
| `--col-214269` | `#214269` | Top bar, side nav, primary button (app "Order Maintenance" button is this navy) | white on it 10.3:1 |
| `--col-214269-dark` | `#1d3a5d` | pressed | |
| `--twilight-blue` | `#0d477d` | Headings on light | 9.5:1 on white |
| `--cool-blue` | `#2c83d7` | Links, active nav marker, approve button, focus ring | white on it 3.9:1 (OK for 14 px+ bold / UI; not for 12 px body) |
| `--denim` | `#3c6390` | Secondary text on light | 6.2:1 |
| `--light-blue-grey` | `#bfcfde` | Borders, muted text on navy (6.4:1 on navy) | |
| `--ice-blue-light / --ice-blue / --ice-blue-dark` | `#f8fafb / #eff3f6 / #e1e9f1` | Zebra, panel bg, hairlines | |
| `--background` | `#fafbfc` | Page background | |
| `--seafoam-blue` | `#72c0a2` | OK / success fill (2.2:1: fill only) | |
| `--tangerine` | `#ff9800` | Notice fill, SYNTHETIC badge, nav count badge (text must be `#1c2020`, 7.6:1) | |
| `--f-08038`, `--df-6940` | `#f08038`, `#df6940` | App map pins / fault fill | |
| `--col-11-a-3-c-7` | `#11a1c5` | Decorative only (3.0:1) | |
| `--col-1-c-2020` | `#1c2020` | Body text | 16.5:1 |
| portal `html.dark-mode` | bg `#1c2022`, topbar `#2a2e30`, text `#f0f1f1`, link `#51a8ff`, border `#b7bcbf` | Our dark theme | [fact] |
| body font stack | `-apple-system, BlinkMacSystemFont, Poppins, Roboto, Europress, …` | Poppins is the first web font; Roboto for inputs (`.login input{font-family:Roboto}`) | [fact] |
| icon font | "Europress" (icon-menu, icon-search, icon-tree, icon-user, icon-arrow-down) | We draw our own inline SVG icons; never copy theirs | [fact] |
| manifest | name "Europress SMART", short "SMART App", theme `#000000` | Wordmark text "SMART" in the top bar is the only brand reference | [fact] |

AA-safe inks we add [derived]: `--ep-ok-ink #0d7a6f` (5.2:1), `--ep-notice-ink #8a5a00` (5.9:1), `--ep-warn-ink #b84a24` (5.2:1), `--ep-muted #545d61` (6.7:1, also in their bundle).

App screenshots (App Store, SMARTwaste 1.6.0) [fact]: navy top bar with white title and back chevron; map with orange numbered pins; white bottom sheet with device id, status line "Device status OK.", "Last online: …"; one full-width navy button; light-grey tab bar with cool-blue active icon. Sizes read as iOS defaults (17 px title, 15 px body).

### 2.2 Corporate (explainer) — source: `https://europressgroup.com/` HTML + `wp-content/uploads/uncode/style-custom.css` [fact]

| Item | Value |
|---|---|
| Body | Poppins 400 (Google Fonts), colour `#303133`, 15 px/1.7 |
| Headings | `bio-sans, sans-serif, Montserrat`, weight 600, letter-spacing 0, **UPPERCASE on all page/section titles** ("KEEPING THE VALUE IN CIRCULATION", "SAVE MONEY", "EUROPRESS SCALE SOLUTIONS"). Default h1 31 px; hero uses `fontsize-338686` = 75/50/35 px responsive, `fontsize-155944` = 50/33 px |
| Menu | Poppins 600, 11–12 px, uppercase, letter-spacing .05em, colour `#303133`, hover/active `#03b4e0`, white 90 px bar, sticky with soft shadow |
| Buttons | `.btn`: 1 px solid border, **border-radius 2 px**, uppercase, letter-spacing .1em, 600, padding 13 px 31 px; `.btn-lg` 15 px / 16 px 39 px; home CTA "Book free consultation" uses `btn-color-vyce` = `#0cb4ce` with white text (2.4:1, fails AA — we use navy fill instead and keep cyan for hover/underline/dark bands) |
| Bands | White, `#f7f7f7` (lxmt), `#eaeaea` (gyho), navy `#0d426e` (210407) and `#214269` (186284), charcoal `#141618` (wayh, footer). Media cards use `style-dark-bg` overlay over photos |
| Palette extras | `#72c1a1` mint, `#b4975a` gold, `#43cb83`, `#c92228`, `#e9168c`, `#6442ff`, `#ffea01` exist in the theme but are not used on the pages we read |
| Layout | 1140–1200 px container; single-column stacked sections separated by hairlines; headings "underlined by dashes"; news/references as a vertical list (thumbnail, D.M.YYYY date, linked headline, `* * *`, "Read More") |
| Tone | Short, confident, sustainability + savings; CTAs "Book free consultation", "Contact us", "Read More" |

### 2.3 epsmart.fi (reference only) — `wp-content/themes/epsmart-theme/dist/styles/theme.css` [fact]
Space `#000d61`, dark-blue gradient `#001494→#000d61`, red `#ff2962`, light-blue `#e0f1f5`, mint button `#54dea9` (hover `#87e8c3` + glow `0 6px 30px rgba(51,214,255,.5)`, active `#29d694`), pill radius 9999, card radius 16 px, hero image radius 20 px, Loos Wide 700 headings (h1 52 px desktop / 32 px mobile, h2 22 px), Open Sans body, Source Sans Pro buttons/nav (uppercase, .05em), sentence-case headings, 72 px white nav (109 px with top row), footer gradient navy with mint `#54dea9` headings and pink link underline. Big-number blocks "40 % lower total waste management costs per year" with no uncertainty. (Earlier notes in `agents/brand-dashboard.md` are correct on these.)

## 3. Typography

| Role | Font | Licence | Why |
|---|---|---|---|
| Portal UI (chrome, labels, headings) | **Poppins** 400/500/600/700 | SIL OFL 1.1 (Google Fonts) | First web font in the portal's own body stack and europressgroup.com's body font |
| Data (tables, KPI numbers, chart labels) | **Roboto** 400/500/700, `font-variant-numeric: tabular-nums` | Apache 2.0 → OFL 1.1 since the 2023 variable release on Google Fonts | Portal inputs use Roboto; Poppins digits are proportional and misalign in columns |
| Corporate headings | **Montserrat** 600/700/800 uppercase | SIL OFL 1.1 | Uncode declares Montserrat as bio-sans's fallback, so it is literally what their site shows when Typekit fails. bio-sans (Adobe Fonts) is commercial — do not embed |
| Not used | Loos Wide (commercial, epsmart.fi), Europress icon font | — | Never copy |

Load once: `https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Montserrat:wght@600;700;800&family=Roboto:wght@400;500;700&display=swap`.

Scale (portal): 11 / 12 / **13 base** / 14 / 16 / h3 15 / h2 18 / h1 22 / KPI 28 (Roboto 500). Line-height 1.5 body, 1.25 headings. Sentence case everywhere except small uppercase labels (table headers, kickers, chips) at .06em.
Scale (corporate): body 15/1.7, lead 18/300, h3 20, h2 22–31, h1 31–50, uppercase, letter-spacing 0, Montserrat 600/700.

## 4. Components (all in `theme.css`)

**Portal shell** `.ep-portal` — CSS grid: 52 px top bar spanning both columns, 220 px side nav, main. Top bar: wordmark "SMART" (white square mark + text) · module label "Verified Weight" · spacer · customer selector (tree-select in the real portal) · as-of date picker · **SYNTHETIC** tangerine badge · theme toggle · avatar. Side nav: group label, items Overview / Lifts / Causes / Proof of Fullness / Recommendations (count badge) / Devices / Integration / Method & limits; active item = 3 px cool-blue left bar + 10 % white wash (portal/app pattern: active = cool blue). Collapses under 860 px.

**View header** `.ep-view__head`: h1 claim sentence (one per screen: a claim and its limit), lede in muted, tools right (period, site, export).

**KPI tile** `.ep-kpi`: uppercase 11 px label + evidence chip, Roboto 28 px value with `±` in 14 px muted, one-line note. Never a bare number.

**Insight card** `.ep-insight` (the auto-generated conclusion): 4 px left bar coloured by severity (cool-blue info / tangerine notice / coral warning / seafoam ok), kicker (view + rule id) + chip, claim sentence, "why" line, actions (ghost "Trace", primary "Draft action"). Decision source is always shown ("rule R4", "template, rule-filled, no LLM").

**Evidence chips** `.ep-chip--obs|est|sim|hyp` and `.ep-chip--synthetic`: glyph + border style differ (filled dot solid / half dot solid / diamond dashed / ring dotted italic). All four appear in every table and tooltip.

**Status** `.ep-status--ok|notice|warn|crit|none`: glyph shape + label. No traffic light without words; "Not enough data" is a state, never 0.

**Buttons** `.ep-btn--primary` navy (portal/app), `--accent` cool-blue (approve), `--secondary` white outlined, `--ghost`; 34 px, radius 4 px, 500 weight, sentence case. Reject is secondary (neutral), never red.

**Controls**: `.ep-select`, `.ep-input` 32 px radius 4; `.ep-segment` (list/map style); `.ep-toggle`.

**Tabs** `.ep-tabs`: text with 2 px cool-blue underline (secondary navigation inside a view only; primary navigation is the side nav).

**Table** `.ep-table`: uppercase 11 px grey header on `#eff3f6`, 1 px `#e1e9f1` rows, Roboto right-aligned numbers, hover `#f8fafb`, selected row in estimate-blue wash, inline mini bars for shares.

**Drawer** `.ep-drawer`: used as the right column (340 px) on desktop; header, body (why / evidence rows / draft text with "Draft by template" meta), sticky foot with Approve (accent) · Reject (secondary) · Ask for evidence (ghost). Audit line under it.

**Charts**: inline SVG, 2 px lines, ≥ 8 px markers with 2 px surface ring, bands as 14 % blue fill, recessive grid, Roboto 11 px labels, direct labels ≤ 4 series + legend. Series order fixed: 1 device `#2c83d7`, 2 ticket `#e8702a`, 3 invoice `#17a87a`, 4 `#c58a06`, 5 `#7d6bd9`, 6 `#c04b8c` (validated with the dataviz validator, light; dark set `#3987e5 #d95926 #199e70 #c98500 #9085e9 #d55181` validated on `#1c2022`). Status colours are never series colours. One axis per chart.

**Footer strip** `.ep-foot`: "Synthetic data v1.0.1" chip, method link, build id.

**Corporate skin** `.ep-corp`: `.co-nav` (90 px white sticky, uppercase 12 px menu, cyan hover), `.co-hero` (navy gradient + dark overlay + inline SVG compactor silhouette instead of a photo), `.co-band` white / `--grey` / `--navy` / `--charcoal`, `.co-head-rule` (short cyan rule under uppercase heading = their dashed underline), `.co-btn` (2 px radius, 1 px border, uppercase .1em; navy fill or outline; `--cyan` only on dark bands), `.co-stat` (44 px Montserrat number, cyan unit, uppercase label), `.co-card`, `.co-quote` (cyan left rule, italic, uppercase cite), `.co-footer` (charcoal, social circles), `.co-chip--f|e|a` (fact / estimate / assumption).

## 5. Light / dark

Light is the brand. The portal ships a dark mode (`html.dark-mode`), so ours is legitimate: `[data-theme="dark"]` re-maps surfaces to the portal's own `#1c2022 / #2a2e30 / #f0f1f1 / #51a8ff`, chips to deeper washes, and the chart palette to the validated dark set. Primary button becomes cool-blue in dark (navy on charcoal has no contrast). The corporate skin stays light only (their site has no dark mode; the explainer is a document).

## 6. Do / don't

**Do**
- One claim sentence per screen; every number carries a chip; every action shows its decision source and a reversal path.
- Sentence case in the portal; UPPERCASE only for section titles in the corporate explainer and 11 px labels.
- Navy chrome, white cards, ice background, cool-blue for "interactive", tangerine for "attention / synthetic".
- Roboto tabular numbers; `Intl.NumberFormat('fi-FI')` (decimal comma, narrow space before t and €).
- Alphabetical hauler order by default; "Not enough data to score" instead of zero.

**Don't**
- No Europress logo, no "Europress" icon font, no their photos. Wordmark text only: "SMART" mark + "Verified Weight" + "a Europress SMART concept".
- No mint pills / pink tags in the panel (that is epsmart.fi marketing, not the app).
- No cyan `#03b4e0` as small text on white (2.4:1); no tangerine or seafoam as text.
- No red/green verdicts on haulers; reject buttons are neutral.
- No remote images, fetch, or external JS (artifact CSP). Google Fonts stylesheet only.
- No dual-axis charts; no rainbow; no number on every point.

## 7. Evoking their imagery without their images

The real sites lean on photos: compactor/baler product shots, Kerava factory, map views with orange pins, industrial yards. Substitutes (all inline SVG or CSS, our own work):
- **Compactor silhouette**: flat two-tone SVG (navy body, cool-blue hopper, seafoam status lamp) in the corporate hero and as a 18 px icon in the side nav.
- **Map**: a light `#eff3f6` panel with a faint grid and a few orange `#f08038` pin circles with white numbers (mirrors the SMARTwaste map) — only where a location concept is needed.
- **Photo-hero feel**: navy→steel gradient + the Uncode-style dark overlay + a large silhouette at low opacity; grain via a tiny data-URI SVG noise if wanted (keep under 2 KB).
- **Weighbridge / ticket / invoice**: three small line icons (scale platform, ticket, document) used consistently as series markers.
- **Logo strips**: never; use text "18 reference customers (epsmart.fi)" if needed.

## 8. Files

- `theme.css` — tokens + components for both skins (this document's single source of truth in code).
- `comp.html` — static comp: portal shell + Overview (KPIs, insight cards, device table) + Lifts detail (three-mass chart, residual timeline, approval drawer) + corporate explainer section (nav, hero, stats, CFO band, footer). Single file, Google Fonts only, theme.css inlined.
- `comp.png` — 1280 px light screenshot of the comp.

Phase 2 plan: replace the product page's `:root` with `theme.css` tokens, wrap the demo in `.ep-portal` (side nav = existing tab list), convert tag/chip classes to `.ep-chip--*`, restyle KPIs with `.ep-kpi`, move the existing drawer to `.ep-drawer`; wrap the business page in `.ep-corp`, map its sections to `.co-band` and its headings to uppercase Montserrat, keep its fact/estimate/assumption tags as `.co-chip--f|e|a`.
