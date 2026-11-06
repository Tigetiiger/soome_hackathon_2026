# Product designer: customer dashboard, SMART look-and-feel, demo (lens: 15% demo + SMART pathway, carries the pitch)

Tags: **[fact]** observed/sourced (URL, 2026-11-06) · **[estimate]** computed by me from the synthetic quickstart (50 devices x 90 days) · **[assumption]** my design choice. Companion file: `docs/agents/mock_dashboard.html` (one file, no external requests).

## 0. What I found out about Europress's real style

- **[fact]** SMART marketing site CSS (`epsmart.fi/wp-content/themes/epsmart-theme/dist/styles/theme.css`) defines these custom properties: navy `#000d61` (`--color-space`), accent navy `#001494`, wave `#4b5ac3` (`--color-primary`: link hover/focus), pink-red `#ff2962` (`--color-red`), forest `#235041` (`--color-secondary`), autumn `#b95041` (`--color-error`), fog `#e6e1dc`, amber `#fabe69`, tints `#e0f1f5 / #fff0f4 / #ddf8ee / #e1f9f0`, greys `#f7f9fc #ecf0f6 #dee5f0 #c9d1de #999ea7 #323d4e`. Fonts: `Loos wide` (titles), `Open Sans` (body), `Source Sans Pro` (buttons/links/footer).
- **[fact] Correction to the brief:** the SMART **primary button is mint `#54dea9`** (hover `#87e8c3`, glow `0 6px 30px rgba(51,214,255,.5)`), pill-shaped (`border-radius:9999px`), Source Sans Pro 700, 16 px, **uppercase, letter-spacing .05em**, navy text. Pink-red is the *accent*: link underline (`.12em`, offset `.15em`), card-hover border and title, uppercase tag pills (radius 1rem). Links are navy with a pink-red underline.
- **[fact]** Cards: white, 2 px border, radius 1rem; images/video radius 1.5rem; accordion/arrow icons are navy 2 px round-cap strokes inside mint circles. Container 1200 px; gutter 2.5rem; fluid spacing tokens (`--space-3xs ... --space-5xl`). Headings: h1 2rem (mobile) / 3.25rem, h2 1.375 / 2.375rem, h3 1.25 / 2rem, line-height 1.1. Footer = navy gradient `#001494 -> #000d61`.
- **[fact]** `europressgroup.com` (Uncode theme) is a different, older brand surface: Poppins/Montserrat, text `#303133`, cyan `#03b4e0`. The SMART module should follow **epsmart.fi**, not the group site.
- **[fact]** SMARTwaste app (App Store, v1.6.0, 2026-03-19; I looked at the 2 public screenshots, an older build): navy bar (sampled `#00416e`, older than the web navy), bottom tabs **Devices / Map / Profile**, device sheet with fill-level bar, "Device status OK. Last online ...", full-width **"Order Maintenance"** button, coral cluster pins on a map. Store text: "fill level, location, estimated fill-up dates and overall condition ... notifications for optimal haulage timing ... Quick Order".
- **[fact]** SMART vocabulary (epsmart.fi/en): *SMART portal* (map and list views), *Fill Level Management, Fleet Management and Monitoring, SMART Analytics, Predictive Emptying, Lifecycle Optimization, Reporting, Bioradar, electronic service book, digital maintenance log*. Reports "reveal operator service levels and incorrect usage practices such as overloading". **SMART Center**: experts weekdays 07-17 FI/EN, 24/7 on-call for critical faults, "all fault notifications answered within 24 hours", up to 90% of issues solved remotely. FAQ: devices send emptying requests to the operator's system or operators read data via the **SMART API**; "tri-party model".
- **[fact] Tone:** short, declarative, benefit-led ("Pienennä jätehuollon kustannuksia ja päästöjä", "SMART keeps your device in working order - anywhere, anytime", "Fiksumpaa jätehuoltoa, aidosti"). Numbers lead ("40 %").
- **Not inspected [unknown]:** the logged-in SMART portal (behind "Login"), photo style beyond the 1.5rem rounding. Ask Tommi for 2-3 portal screenshots; tokens below are a faithful *web-brand* match, not a pixel copy of the portal.

## 1. Design tokens (native SMART module look)

### 1.1 Colour, with WCAG 2.x contrast (computed, ratio on the stated background)

| Token | Hex | Origin | Use | Contrast / verdict |
|---|---|---|---|---|
| `ink` / navy | `#000d61` | brand | text, headings, nav bar | 17.07 on white: AAA |
| `ink-2` | `#323d4e` | brand grey-100 | body secondary | 10.98 on white |
| `muted` | `#5b6577` | **derived** | captions, axis text (brand `#999ea7` is only 2.69: never for text) | 5.88 white, 5.06 on ice: AA |
| `mint` (primary button) | `#54dea9` | brand | primary fill, selected nav bar | navy on mint **10.08**: AA; mint on white 1.69: *fill only, never a line or text* |
| `mint-hover` | `#87e8c3` | brand | hover | navy on it 11.67 |
| `mint-wash` / `forest` | `#ddf8ee` / `#235041` | brand | OK status | 8.16 |
| `mint-ink` | `#0b7a57` | derived | OK icons/text on white | 5.34 |
| `signal` (pink-red) | `#ff2962` | brand | marks, underline, hover, discrepancy highlights | 3.66 on white: **fails AA for small text**, OK for non-text marks and large type; **navy text on pink-red = 4.67 (use for tags)** |
| `signal-ink` | `#c4003f` | derived | alert text/icons | 6.14 white, 5.56 on `#fff0f4` |
| `pink-wash` | `#fff0f4` | brand | alert/finding background, SYNTHETIC banner | navy 15.46 |
| `wave` / `wave-ink` | `#4b5ac3` / `#3a49b0` | brand / derived | focus ring, links on tint, device series | 5.92 / 7.61 white |
| `ice` | `#e0f1f5` | brand | "reported" badge, info | navy 14.69 |
| `amber` / `amber-wash` / `amber-ink` | `#fabe69` / `#fff4dc` / `#7a5000` | brand / derived | watch, assumption | 10.27 navy on amber; 6.78 ink on wash |
| `canvas` | `#f7f9fc` | brand grey-5 | page background | navy 16.19 |
| `line` / `line-strong` | `#dee5f0` / `#8a93a3` | brand / derived | hairline (decorative) / input and chart-axis boundary | 1.20 (decor.) / 3.10 (meets 1.4.11) |
| `autumn-ink` | `#a23e30` | derived from brand `#b95041` (4.90) | form validation text only | 6.43 |

**Data-source series (one colour = one source, everywhere):** Device `#4b5ac3`, Weighbridge `#009a98`, Invoice `#b07400`; text inks `#3a49b0 / #006b69 / #7a5000` (>= 6.3 on white). Ran the dataviz validator, all-pairs: lightness band, chroma floor and contrast >= 3:1 PASS (3.46 teal, 3.93 ochre, 5.92 wave); worst-pair normal-vision dE 20.4, CVD dE >= 13.3 (target 8). Pink-red is **reserved for discrepancy/alert**, never a series. Navy is ink, not a series. Every series also differs by marker (circle / square / diamond) and is direct-labelled.

### 1.2 Type (free substitutes stated)

| Role | SMART web | Our font (all **SIL OFL 1.1**, self-hosted via `@fontsource/*`) | Note |
|---|---|---|---|
| Display / headings, KPI numbers | Loos Wide Bold (**commercial**, not shipped) | **Montserrat 700/800** (also Europress group's own font), fallback Manrope | wide geometric lookalike; `font-variant-numeric: tabular-nums` for tables/KPIs |
| Body | Open Sans 400/600/700 | **Open Sans** (identical font, free) | |
| Buttons, labels, links, table heads | Source Sans Pro 700, uppercase, .05em | **Source Sans 3** (the maintained successor, OFL) | |

Scale (px/rem, 1.2 ratio, brand h-sizes compressed for density): Display 40 (KPI) · H1 32 / 2rem · H2 24 / 1.5rem · H3 20 · H4 18 · Body 16 / 1.5 · Small 14 · Caption 12 (min; tags, axis). Headings line-height 1.1; table text 14.

### 1.3 Shape, elevation, space, motion

| Token | Value | Origin |
|---|---|---|
| radius `sm / md / card / media / pill` | 4 / 8 / **16** / 24 / 9999 px | brand (.25 / .5 / 1 / 1.5rem / button) |
| shadow `card` / `pop` / `glow` | `0 4px 8px rgba(0,0,0,.1)` / `0 6px 4px rgba(0,13,97,.2)` / `0 6px 30px rgba(51,214,255,.5)` (mint hover only) | brand |
| border | 2 px on cards (white, hover = pink-red), 1.5 px dashed for estimates/assumptions | brand / ours |
| spacing | 4-pt base: 4 8 12 16 24 32 48 64; page gutter 32, card padding 20; content max 1280 | ours (brand uses fluid clamp) |
| motion | 180 ms buttons, 300 ms cards, `ease`; none under `prefers-reduced-motion` | brand + a11y |
| focus | 3 px `#4b5ac3` ring, 2 px offset | brand focus colour |
| icons | Lucide (ISC), 2 px stroke, round caps, navy; in a 30 px mint circle for actions | matches SMART arrow icon |

Components: pill buttons (primary mint, secondary white + 2 px mint border, disabled grey), navy-underline-pink links, 16 px cards, pink uppercase tag pills (navy text), accordions for "How was this computed?", navy top bar + left nav (mirrors SMARTwaste's navy bar and Devices/Map/Profile logic). **Not used:** Europress logos, photos, Loos Wide; the wordmark is plain text `EP·SMART` (placeholder, swap for the official asset if Europress supplies it).

## 2. Information architecture

### 2.1 Personas

| Persona | Question | Lands on | Success |
|---|---|---|---|
| **Facility manager**, retail chain (2-3 compactors per site) | "Is anything wrong with my bins or my invoices this week?" | Overview, Invoice check | decides in < 2 min, 1 approve |
| **Sustainability / ESG lead** | "How many tonnes per stream, how clean, how reliable are the numbers?" | Weight & material, Monthly report | quarterly numbers with +- and source |
| **Procurement / contract manager** | "Do we pay what the contract says, and should we renegotiate or tender?" | Invoice check, Hauler scorecard, Contract & actions | an approved, evidence-backed dispute or request |
| **Europress SMART Center operator** | "Which devices (any customer) have a weight sensor or machine problem, and what do I do remotely?" | Fleet health & sensor trust (operator mode) | triage list, remote fix, no customer finance data [assumption: role-based access] |

### 2.2 Screens, purpose, data (synthetic dataset tables/columns)

| # | Screen | Purpose | Key components | Data used (table.column) |
|---|---|---|---|---|
| 1 | **Overview** | morning triage across sites | KPI tiles, findings queue, "needs your decision", month pulse | `devices.{device_id,material_stream,equipment_class,weight_measurement}`, `telemetry_daily_summary.{fill_pct_last,mass_kg_last_valid,hours_full,hours_down,data_completeness_pct}`, `collection_events.status`, `invoices.{total_eur,dispute_status}` + engine findings |
| 2 | **Invoice check** (flagship) | device vs ticket vs invoice vs contract, human approval | finding list, evidence list, mass-trace with invoice markers, 3-source band chart, line table, approve panel, audit log | `invoice_lines.{invoice_line_id,line_type,service_date,operator_job_ref,quantity,unit,unit_price_eur,amount_eur}`, `invoices.{billing_period,issued_at,total_eur,dispute_status}`, `contract_versions.{effective_from,pricing_model,lift_fee_cents,per_km_cents,free_km,remote_surcharge_cents,fuel_surcharge_bp,haul_fee_cents_per_t,processing_fee_cents_per_t,min_charge_cents,credit_share_bp,side_waste_fee_cents,default_weight_kg}`, `contracts.notice_period_days`, `collection_events.{collection_id,operator_job_ref,actual_at,status,device_mass_kg_before,device_mass_kg_after,device_estimated_collected_kg,weight_reconciliation_status,driver_reported_side_waste}`, `weighbridge_tickets.{ticket_id,gross_kg,tare_kg,tare_method,allocated_net_kg,allocation_method,loads_on_vehicle,published_at}`, `telemetry_hourly.{measured_at,mass_kg,mass_uncertainty_kg,sensor_status,quality_flag}` (dedupe on `message_id`), `sensor_registry.nominal_sigma_*`, `operators.weighbridge_data_shared` |
| 3 | **Weight & material** | tonnes, EUR/t, density and contamination hints | tonnes by stream, EUR/t per lift with source badge + benchmark, implied-density strip, grade/contamination table | `collection_events.device_estimated_collected_kg`, `weighbridge_tickets.{allocated_net_kg,material_declared}`, `telemetry_hourly.{mass_kg,fill_pct}` + `devices.container_volume_m3` -> implied density, `material_classes.{typical_compacted_density_kg_m3,credit_eligible}`, `quality_assessments.{grade,contamination_pct_est,remark_code,rejected}`, `sites.outdoor_material_staging`, `site_calendar`, `contract_versions.target_collection_cost_cents_per_t`, `price_index_monthly.price_eur_per_t` |
| 4 | **Fleet health & sensor trust** (Tommi's machine-health ask) | is the scale trustworthy, is the machine healthy | trust table, ratio-trend chart (device/ticket, coloured by `tare_method`), machine-health strip, work-order timeline, SMART Center CTA | `sensor_registry.{sensor_id,installed_at,removed_at}`, `telemetry_hourly.{sensor_status,quality_flag,delivery_mode,received_at,measured_at,compaction_cycles,press_load_index,operational_state}`, `telemetry_daily_summary.{n_valid_mass,n_buffered,hours_down,hours_full}`, `maintenance_work_orders.{work_order_type,downtime_hours,description_code,completed_at}`, ratio from `collection_events` + `weighbridge_tickets` |
| 5 | **Hauler scorecard** (neutral) | service transparency, never a league table | metric rows with n and range, "explained by" chips, data-sharing metrics | `operators.{operator_name,weighbridge_data_shared,api_feed}`, `collection_events.{status,scheduled_at,actual_at,order_placed_at}`, `weighbridge_tickets.{arrival_at,published_at,tare_method}`, check-engine output; backtest vs `labels_dev/operator_scorecard.*` |
| 6 | **Contract & actions** | renegotiate / tender evidence, approvals log | tariff versions, peer comparison, notice countdown, 4 action cards, audit log | `contracts.{pricing_model_initial,notice_period_days,price_index_id}`, `contract_versions.*`, `benchmark/operator_action_cases.candidate_actions`, `reference/regions`, peers = other contracts in the package |
| 7 | **Monthly report** | printable management + ESG pack | tonnes by stream, EUR and EUR/t, contamination, findings resolved, data quality statement | all of the above, grouped by `site_id/material_stream/month`; QA oracle only: `labels_dev/reference_economics_monthly` |

Rule: `labels_dev/*` and `private_evaluation/*` are **never** shown to the user; labels are unit-test oracles for our engine (e.g. the 4 phantom lines are `UNMATCHED_LINE` in `anomaly_labels`).

## 3. Low-fi wireframes (ASCII)

Legend: `[M]` measured, `[R]` reported, `[~]` estimate, `[?]` assumption. Figures for CMP-00038 / CTR-00038 / SITE-00013, the haulers' table, CMP-00006/-00014/-00050 are real synthetic quickstart rows or my computations from them; everything else in a wireframe is a placeholder.

### 3.1 Overview
```
+--[EP.SMART] Material value ------------------------------------ Facility mgr - ORG-0004 v --+
| ## SYNTHETIC DATA - hypothetical prices - advice only, nothing acts without approval ##      |
+-----------+----------------------------------------------------------------------------------+
| Overview  | Good morning. 2 findings need your decision.                  [Site: all v][Q3 v]|
| Invoice   | +---------------+ +---------------+ +----------------+ +-------------------+      |
| Weight    | |Invoiced Q3    | |Questionable   | |EUR/t last lift | |Sensor trust       |      |
| Fleet     | |EUR 4,195 [R]  | |EUR 1,253 [!]  | |229 [~] vs 180  | |93% valid [M]      |      |
| Scorecard | +---------------+ +---------------+ +----------------+ +-------------------+      |
| Contract  | Findings queue                               | Devices (list | map) <- SMART toggle|
| Report    |  [DISPUTE] 2 invoiced lifts did not happen   | CMP-00038 Kuusamo 5  fill 25%  OK   |
|           |    EUR 1,215  evidence HIGH      > open      | CMP-00001 Oulu       fill 17%  OK   |
|           |  [NO ACTION] weight gap, EUR 0   > open      | CMP-00006 Ylivieska  fill 58%  sensor ? |
|           |  [REQUEST] tickets missing 2/4   > open      | (no map tiles offline: list view only) |
+-----------+----------------------------------------------------------------------------------+
```

### 3.2 Invoice check (flagship; built in the mock)
```
 Invoice check - CMP-00038 - Hauler Gamma (fictional) - CTR-00038 - Jul-Sep - as of 2026-10-13
 [Invoiced EUR 4,195 R] [Questionable EUR 1,253 !] [Expected value EUR 1,067 ?] [Valid mass 93% M]
 +- Findings ---------------------+ +- F1 Two invoiced lifts did not happen -----------------------+
 | [DISPUTE]  EUR 1,215.20        | | [Recommended: DISPUTE] [Evidence HIGH 3/3] [M][R]               |
 |  F1 2 invoiced lifts, no lift  | | WHY: 1 not in collection log (+-3 d)  2 mass never dropped      |
 | [NO ACTION] EUR 0              | |      3 same lump sum as a real lift                              |
 |  F2 gap 335 kg, per-lift price | | WRONG IF: unlogged lift / unknown billing convention             |
 | [REQUEST DATA] n/a             | | mass kg 3000|            _/ \__                                  |
 |  F3 tickets 2/4 missing        | |         2000|    ___/`      [24 Aug ! invoiced, no drop]        |
 | [DISPUTE] EUR 37.35            | |         1000| __/   |        |\_  <- 10 Aug v matches drop       |
 |  F4 fuel 12% vs 6%             | |            0+---1 Aug----15 Aug----29 Aug---                   |
 +--------------------------------+ | table: line | date | job ref | EUR | finding (4 flagged rows)   |
                                    | Value: 1,215.20 (+37.35 F4); EV = 0.9 x 1,252.55 - 60 = 1,067 ? |
                                    | > How was this computed?                                        |
                                    | YOUR DECISION: (o)Dispute ( )Request data (-)Renegotiate (-)Tender |
                                    | [x] I have read the evidence and limits                         |
                                    | [ APPROVE AND PREPARE DRAFT ]  [ Not now ]   audit log: ...     |
                                    +-----------------------------------------------------------------+
 Three-source view (F2), kg:  device   o----------o  1,975 +-42 (2s) [M]
                              ticket   [========x========]  1,640 +-208 (stored tare) [~]   gap 335 |
                              invoice  not billed by weight (fixed price per lift)
```
Per-tonne variant (for chargeable streams): rows `device | ticket | invoice tonnes` with bands; invoice qty > ticket + band => DISPUTE; ticket > device + band => "check sensor + tare" first.

### 3.3 Weight & material
```
 Weight & material - Kuusamo 5 (4 devices) - Jul-Sep                           [Tonnes | EUR/t | Quality]
 Tonnes by stream (device est. [~], +-)     EUR/t per lift, CMP-00038 (dot = source; line = target 179.86 [R])
  mixed waste   ============ 7.87 t          21 Jul  o 2,129 [~ device 310 kg]  "explained: max-interval rule"
  cardboard     ======       3.80 t  credit   10 Aug  o 402 [R ticket]  x 334 [~ device]
  plastic film  ===          1.77 t  credit   27 Aug  o 248 [R ticket]
  mixed plastic ===          1.73 t  credit   16 Sep  o 229 [~ device]   no ticket -> [Request data]
  credit-eligible streams = 48% of tonnes (a stream share, NOT a recycling rate)
 Implied density = mass / (fill% x volume)   Contamination hints (operator grades, [R], pooled quickstart)
  kg/m3  typical 190 (cardboard)              grades A 38% | B 41% | C 17% | R 4%  (n=230 graded tickets)
  CMP-00006 median 118 (-38%)  HINT:          remark WET_MATERIAL where present -> rain, outdoor staging ([R])
   a) sensor drift - ratio .97 -> .71 (see 3.4)  CMP-00014: density step after CONFIG_CHANGE 7 Sep
   b) mis-sorted light material - grades A/B 7 of 7 (weak)   (force setting raised) = explained, no alert
  Tooltip: "fill noise +-4 pp, so density +-8% at 50% fill. Hint only; never an invoice claim."
```
Real inputs: tonnes from `collection_events.device_estimated_collected_kg` per `devices.material_stream` on `SITE-00013` (7.87 / 3.80 / 1.77 / 1.73 t); CMP-00006 implied density 118 vs typical 190 kg/m3 (`material_classes`); grade shares from `quality_assessments` (n=230).

### 3.4 Fleet health & sensor trust
```
 Fleet health & sensor trust     [Customer view | SMART Center view]          [Ask SMART Center]
 Device     Trust  Valid%  Fault h  Device/ticket ratio, last lifts        Work orders          Flags
 CMP-00006  RED    89%     7        .97 .84 .74 .85 .67 .71  (trend down)  PM only              drift?  (2 causes)
 CMP-00050  AMBER  65%     48       sensor replaced 2026-08-31 (step)      SENSOR_REPLACEMENT   re-baselining
 CMP-00014  RED    56%     0        degraded 19% of hours                  CONFIG_CHANGE 7 Sep  DEGRADED
 CMP-00038  AMBER  93%     112      1.20 (stored tare) 1.01                none                 2 faults: 15 h, 96 h
 CMP-00012  GREY   n/a     n/a      no weight sensor (NOT_INSTALLED)       --                   weighing not installed
 Detail CMP-00006:  ratio chart (point = lift, filled = WEIGHED tare, hollow = STORED tare), recal/replace ticks
 Machine health:  hours DOWN 3 | FULL 0 | cycles/day trend | press_load_index (derived from the fill estimate: weak [~])
 Proposed: "Check calibration remotely / schedule visit"  [Create service request]  (SMART Center answers < 24 h)
```
Trust band [assumption], computed on the trailing 30 days and since the last replacement: green = valid >= 95%, FAULT <= 2% of hours, median ratio within +-5%, no monotone trend; amber = any one off, or "re-baselining" for 3 lifts after a recalibration/replacement; red = valid < 70%, FAULT > 10%, or ratio trend > 10% over 3 lifts. Fault windows are always shown as gaps, never interpolated. Valid%, fault hours, ratios, work orders are real quickstart values (CMP-00006 ratio sequence and CMP-00038 ratios computed from `collection_events` + `weighbridge_tickets`). The dataset has no pressure curves; Europress's predictive-maintenance output, when integrated, replaces the derived strip.

### 3.5 Hauler scorecard (neutral)
```
 Service transparency - 3 months - fictional haulers     (no ranking; n shown; "insufficient data" if n < 20)
 Metric                    Alpha(n=175)  Beta(n=68)  Gamma(n=69)  Epsilon(n=74)   Explained by
 Tickets shared            94%           90%         45%          89%             operator policy [R]
 Median days to publish    1.9           6.8         23.0         0.3             operator process [R]
 Ticket vs device, median  +2.6%         +2.0%       +3.3%        +2.5%           spread < 1.5 pp, n small [~]
 Stored (not weighed) tare 46%           57%         73%          46%             widens the band, not blame
 Invoice lines flagged     (rate +- range, rule-based, each links to its evidence)
 > "Differences also come from sensor drift, side waste and combined loads." [Request data] [Open contract]
```
Values: ticket coverage, ticket-vs-device, stored-tare share, publish lag are my computation from the quickstart [estimate]; "invoice lines flagged" comes from the check engine.

### 3.6 Contract & actions
```
 Contract CTR-00038 - fixed price per lift - V1 since 2023-06-24 - notice 60 d       [Renegotiate][Tender]
 Tariff: lift EUR 581.32 | EUR 1.46/km (30 km free, 48 contracted) | fuel 6% | default weight 2,980 kg
 Cost per tonne vs target: 229-402 EUR/t vs 179.86 [R]     peer terms: shown only if >= 3 peers exist
 Action cards:  DISPUTE (EV 1,067 ?) | REQUEST DATA (not valued: fixed price) | RENEGOTIATE (needs peers) |
                TENDER (switch cost EUR 500 ?, benefit starts after 60 d notice)
 Approvals & audit log:  time | finding | action | approver | evidence snapshot | state PENDING/APPROVED/SENT
```
Action values follow the published hypothetical rules (`configs/assumptions.yaml -> operator_actions`: 0.9 dispute recovery, EUR 60 / 20 admin, 0.6 comply probability, 0.5 renegotiation success, EUR 150 effort, 0.8 tender success, EUR 500 switch). Shown as `[?]`, never as promised savings.

### 3.7 Monthly report (printable)
```
 EP.SMART Material value - Monthly report - CMP-00038 Kuusamo 5 - August 2026   SYNTHETIC [Download PDF]
 1 Headline: invoiced EUR 2,065.88 [R] | contract-correct EUR 1,420.93 | difference EUR 644.95 (2 findings)
 2 Tonnes: tickets 4.30 t [R]  device 4.67 t +-0.06 [M]  (+8.6%, both tickets stored tare)   stream table
 3 EUR/t: 402 and 248 vs target 180 [R]       4 Quality: grades, contamination, wet loads (n shown)
 5 Machine & sensor: device DOWN 0 h, weight sensor fault 15 h (Aug), trust AMBER   6 Decisions taken (audit log)
 7 Data quality statement: coverage, late tickets (40 d), assumptions, what is not measured
```
August check: 2 real lifts x EUR 659.96 + rental EUR 101.01 = EUR 1,420.93; invoice 2,065.88 less phantom lines 607.60 less fuel error 37.35 = 1,420.93 (ties out).

## 4. UX rules for explainability and uncertainty

1. **Provenance badge on every number**: Measured (solid navy), Reported (outlined, ice), Estimate (dashed), Assumption (amber dashed). Icon + word + shape, never colour alone.
2. **Always +-**: "1,975 +-42 kg (2 sigma)"; round to the uncertainty; no 3-decimal tonnes unless a ticket gives them.
3. **Why before what**: each finding opens with 1-3 evidence bullets, each with a drill-down to source ids (`collection_id`, `invoice_line_id`, `ticket_id`).
4. **"What could make this wrong"** is mandatory text on every finding, plus counter-evidence (e.g. sensor fault window).
5. **Combined band** = 2 x sqrt(sigma_device^2 + sigma_ticket^2). sigma_device = sqrt(sigma_before^2 + sigma_after^2) from `mass_uncertainty_kg` (median 15 kg), inflated when sensor trust is amber/red because the device "does not know about drift". sigma_ticket from `tare_method`/`allocation_method`: robust SD of ticket minus device in the quickstart **[estimate]**: single load WEIGHED 44 kg (n=117, 3.2%), STORED 104 kg (n=122, 10.5%); combined loads EQUAL_SPLIT 890 to 2,261 kg (n=24 / 8). 44% of stored-tare single loads differ >10% from the device vs 11% for weighed.
6. **Value after contract mechanics**: compute EUR at stake through the tariff (min charge, fixed fee, default weight); a real 335 kg gap can be EUR 0 and we say "no action". Fewer false alarms is the trust feature.
7. **Estimate vs measured**: device = measured (with band); ticket = reported (with band); anything model-derived = estimate. Never fill missing weight with a default; show a gap ("not shared", "sensor fault 15 h").
8. **Rule first, model second**: show a `rule` or `model` tag; rules show their formula under "How was this computed?"; models show band + top drivers.
9. **Nothing acts without approval**: recommendation, then explicit evidence checkbox, then named approver, then **draft** only, then audit entry (payload: `requires_human_approval:true, auto_execute:false`). Nothing is sent from the demo.
10. **Neutral language for operators**: "no matching collection found", "invoice differs from contract by", with a causes list (stored tare, combined load, side waste, drift, publication lag). Banned: "fraud", "overcharged by <name>", rankings or red/green league tables. Show n; under n < 20 show "insufficient data".
11. **Money is hypothetical**: label EUR "at stake" or "expected value", never "savings"; expected value shows its published rule (0.9 recovery, EUR 60 admin [?]).
12. **SYNTHETIC DATA banner** is persistent (not dismissible, `role="note"`), repeated in every export/PDF watermark.
13. **Time honesty**: show "as of", data freshness; late tickets (the data has up to 45-day lags) re-open findings and are marked "new evidence".
14. **Accessibility**: AA contrast (table above), 3 px focus ring, keyboard flow, `aria-live` on decision result, chart `role="img"` + title/desc + table alternative, 48 px primary buttons, reduced-motion.
15. **i18n from day one** (SMART runs FI/EN/SV/NO/PL; Poland is a key market): all strings keyed; locale number format (`1 975 kg` FI/PL, `1,975` EN).
16. **Confidence tiers** (documented, [assumption]): High = deterministic rule + >= 2 independent sources agree; Medium = one source or model with band excluding zero; Low = hint only (e.g. density).

## 5. Demo storyline (3 minutes)

| Time | Screen | Say / show |
|---|---|---|
| 0:00-0:20 | slide, then Overview | "Customers distrust invoices because the hauler alone holds the weight. Your compactor already sees the weight. This is a new SMART tab." SYNTHETIC banner visible. |
| 0:20-0:45 | Overview | 4 tiles, findings queue. "Four findings. We rank by evidence, not by size." |
| 0:45-1:45 | **Invoice check, F1 (the wow)** | Mass trace for August. Point at 24 Aug: "**The invoice says a truck emptied this container on 24 August. Your compactor says it stayed at 2,100-2,400 kg all day.** Same on 16 July. EUR 1,215." Open evidence (not in collection log, no mass drop, same lump sum). Show "what could make this wrong". |
| 1:45-2:10 | F2 (honesty) | "A 335 kg gap between compactor and ticket. We recommend **no action**: stored tare widens the ticket band, and the contract is per lift, so EUR 0. A tool that says no earns the yes." |
| 2:10-2:30 | Approve | tick evidence, **Approve and prepare draft**, audit entry appears. "Nothing sent; a human decides." |
| 2:30-2:50 | Fleet & sensor trust | CMP-00006 ratio trend + "ask SMART Center". "We show how far to trust our own scale." |
| 2:50-3:00 | Monthly report / close | "Intro -> Insights -> Integrated: this lives in Insights; the same JSON feeds the SMART portal and the operator API." |

Backup: pre-recorded screen capture (mp4) + static HTML (section 6, option C). Second wow if time: toggle the default-weight view ("2,980 kg default would put 21 July at EUR 221/t; the compactor says 310 kg, EUR 2,129/t, explained by the hygiene rule").

## 6. Front-end choice for 48 h, 4 students

| Option | Build effort | Look-native | Offline reliability | Risk |
|---|---|---|---|---|
| A. Next.js 16 + shadcn/ui + Tailwind 4 + Recharts 3 | high (App Router, server/static export) | high (shadcn tokens = our CSS vars) | OK only as `output:'export'` | config time, SSR bugs |
| **B. Vite + React + TS + Tailwind 4 + shadcn/ui + Recharts + custom SVG; data = precomputed JSON** | **medium** | **high** | **best**: static `dist/`, fonts via fontsource, no CDN/tiles; `vite-plugin-singlefile` -> one `demo.html` on a USB stick | low |
| C. Python-generated static HTML (Jinja2 + inline SVG, my mock as template) | low | high (tokens as CSS) | perfect | limited interactivity; good fallback |
| D. Streamlit or Dash | lowest | low (generic look, hard to theme) | local server OK | weak pitch visual; use for analyst tooling only |

**Recommendation: B as primary, C as fallback, plus a recorded walkthrough.** Pipeline: pandas/duckdb job writes `findings.json`, `case_*.json`, `fleet.json` (shape in section 7); UI reads static JSON; optional FastAPI endpoint mirrors `smve.recommendation` to show the integration path. Charts: Recharts for bars/lines; three bespoke charts (mass trace with markers, band chart, ratio trend) as hand-written SVG (see mock, ~60 lines each). No map: list view only (tiles need network and OSM tile policy).

Licences (registry values read 2026-11-06; all permit commercial use):

| Component | Licence | Notes |
|---|---|---|
| React 19, Next.js 16, Vite 8, Tailwind CSS 4, Recharts 3, TanStack Table, zod, Vitest, tailwind-merge, sonner, vite-plugin-singlefile | MIT | |
| shadcn/ui (CLI `shadcn`, components copied into repo) + Radix UI primitives | MIT | copy-in, no runtime dependency on shadcn |
| class-variance-authority, Playwright (e2e) | Apache-2.0 | |
| Lucide icons | ISC | |
| Fonts Montserrat, Open Sans, Source Sans 3 via `@fontsource/*` | font files **SIL OFL 1.1**, packaging MIT | may bundle/embed; may not sell the font alone; rename if modified |
| Alternatives: ECharts (Apache-2.0), Observable Plot, D3 (ISC), MapLibre GL (BSD-3), Leaflet (BSD-2), Streamlit (Apache-2.0), Dash and Plotly (MIT), Jinja2 (BSD-3), FastAPI/Pydantic/DuckDB (MIT) | as stated | |
| **Not used**: Loos Wide Bold (commercial), Europress logos/images/CSS files (only read property values) | | tokens re-expressed; trademarks stay Europress's |

## 7. SMART integration pathway (UI contract)

Extend the provided `smve.recommendation.v0` payload (`proposal.requires_human_approval:true`, `auto_execute:false`, `evidence.{observed,estimated,hypothetical}`, `assumptions`, `not_proven`) with: `evidence[]` items `{kind: measured|reported|estimate|assumption, ref:{table,id}, value, unit, sigma}`, `counter_evidence[]`, `confidence: high|medium|low`, `value_at_stake:{eur, formula, hypothetical:true}`, `approval:{state: PENDING|APPROVED|DEFERRED, by, at}`. The UI renders only this contract; SMART portal embeds it as a "Material value" tab (Insights tier), reusing SMART auth, the SMART API for device data [fact: FAQ] and customer-supplied contract/invoice files or operator feeds (2 of 5 fictional operators have `api_feed`). SMART Center sees device and sensor findings only [assumption].

## 8. Verification, limits, open questions

- **Mock verification:** no browser is installed here (chrome-devtools tools failed: no Chrome binary). I verified by running the page script under Node with a DOM stub (all 4 findings render, no exceptions, no NaN), confirming both generated SVGs are well-formed XML and that the file has zero external requests (no `http(s)://` string at all). **Visual rendering is unverified**; open it in any browser and check chart label collisions. Fonts fall back to system fonts offline by design.
- Findings in the mock are real synthetic rows (CTR-00038: 3 invoices, 23 lines, EUR 4,195.42; phantom job refs `...-P2607...`/`...-P2608...`; device mass traces) but the dataset *seeds* these errors (~30% of this contract's value); real rates are 1-3.5% per the dataset's assumptions. Say so in the pitch.
- Untested: band widths for stored tare use pooled small samples (n=122/117); the "no emptying" threshold is illustrative; contrast numbers are WCAG 2.x only (no APCA); keyboard/screen-reader tests not run.
- **Open question for Tommi:** may Europress-branded SMART show customer invoice/contract data (who is the data controller, and does the customer upload it), or should the module be framed as "customer-owned data vault" with Europress as processor?
