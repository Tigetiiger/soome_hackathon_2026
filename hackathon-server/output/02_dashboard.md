# SMART Insights — customer dashboard (FI / EN)

**URL (now, tailnet only):** http://hackathon.tail8f13e3.ts.net:8080 · **Later:** https://europress.acq.ee · **Code:** `/home/hackathon/europress-dashboard/`
**Goal:** give the end customer the most information possible about their waste, educate them, and show — in euros — how to save money, so that more customers buy SMART (today ≈ 15 % of customers).

## 1. What the customer sees

| Area | Content | Clickable → provenance |
|---|---|---|
| KPI row | Waste cost (12 mo), cost per tonne, recycling rate, **savings potential / yr** | ✔ formula, sources, rows |
| Where you can save | 5 levers ranked by € with effort pill (quick win / some work / at tender) | ✔ each lever |
| Fill at emptying | Gauge vs SMART 85 % target, pickups, lifts below 60 %, wasted trips | ✔ |
| Monthly cost by stream | Stacked bars | ✔ click a stream |
| Recycling vs mixed waste | Two lines — "mixed is bad, make it less" | — |
| Your machines | Per machine: stream, avg fill ring, €/t vs fleet median, status pill | ✔ each row |
| Insights for you | Rule-based alerts (mixed waste rising, contamination, tender window, early lifts) + "Ask SMART AI" | → AI |
| Customers like you | Median saving for small / medium / large customers — the "what does an average customer save" message Europress does not advertise today | — |
| Your operators | On-time %, weighbridge data shared %, order→pickup hours, **notice-by date** before the 3-year contract renews | ✔ scorecard rows |
| Weight evidence | Lifts where device weight ≈ weighbridge (±10 %), differ > 10 %, device-only | ✔ |
| Density by month | kg/m³ per stream — the winter vs summer question Europress has no data on | — |
| SMART Advisor (AI) | Chat panel; Claude reads the customer's data files and answers in FI or EN, citing the file and field | — |
| For waste operators | 14-day pickup forecast (Figma dot columns), expected tonnes by stream, fill-at-emptying histogram, customers renewing in 12 months | ✔ |
| FAQ & method | SIM 4G/5G, 3–5 kW, remote service, E-stop, pricing, method & assumptions | — |

Language toggle FI/EN everywhere (UI, numbers `140 574 €` vs `€140,574`, dates, AI answers). Finnish is the default.

## 2. Demo customer (hero, opens by default)

**Hospitality Customer 0049** — hotels, 3 sites, 9 machines (synthetic). Picked automatically: mid-size, has mixed waste, mixed share rising.

| Metric | Value |
|---|---|
| Waste cost, Oct 2025 – Sep 2026 | **140 574 €** |
| Cost per tonne | 283 €/t |
| Recycling rate | 43.0 % (mixed waste 55 % → 58.5 % of tonnes) |
| Avg fill at emptying | **49 %** (target 85 %) — 255 of 395 lifts below 60 % |
| Savings potential | **60 471 € / yr** |
| → Empty when full | 39 955 € |
| → Compare price per tonne (after fuller pickups) | 6 386 € |
| → Sort more | 6 318 € |
| → Avoid extra fees | 5 881 € |
| → Invoice second look | 1 931 € |
| Contract notice | Hauler Delta — give notice by 17 Oct 2026 |

**Customers like you (all 52):** small (≤3 machines, n=26) median 5 562 €/yr = 22 % of cost · medium (4–10, n=14) 16 448 € = 20 % · large (11+, n=12) 69 404 € = 32 %.

## 3. How every number is calculated

All formulas are shown in the drawer in both languages; the same text is in `pipeline/build_data.py`.

- **Waste cost** = Σ invoice lines (VAT 0 %) for the customer's contracts.
- **Tonnes** = Σ `device_estimated_collected_kg` of completed + partial lifts (device weight model; simulated in this pack).
- **Recycling rate** = tonnes of cardboard, paper, plastics, biowaste ÷ all tonnes.
- **Empty when full** = Σ machines (lifts − ⌈Σ fill % ÷ 85⌉) × fixed cost per lift (lift fee + transport + fuel + remote surcharge). Biowaste (hygiene) and max-interval lifts are excluded.
- **Avoid extra fees** = 50 % × Σ wasted-trip, cancellation, emergency, contamination, side-waste, rejection and minimum-charge lines.
- **Sort more** = (mixed €/t − own recyclable €/t) × mixed tonnes × 20 %.
- **Compare price per tonne** = Σ machines max(0, €/t *after* the early-lift saving − fleet median €/t for the stream) × tonnes × 50 %. Computed after lever 1 so it is not double-counted.
- **Invoice second look** = Σ lifts where invoiced − recomputed-from-contract > 5 €. Wording: "difference / needs a second look", never "overcharged".
- **CO₂** = trips × billable round-trip km × 1.1 kg CO₂/km (assumption).
- **Operator 14-day forecast** = devices whose fill reaches 85 % within 14 days at their median daily fill growth (last 14 days of telemetry).

Assumptions (target 85 %, 20 % sortable, 50 % fees avoidable, 50 % of price gap closable, 1.1 kg CO₂/km, 3-year contracts) are shown as amber "Assumption" boxes in the drawer.

## 4. AI advisor (headless Claude Code)

- `POST /api/ask` → the Node server spawns `claude -p` (Sonnet) in `ai-workspace/` with **read-only tools** (`Read/Glob/Grep` limited to that folder, `--permission-mode dontAsk`, Bash/Edit/Write/Web disabled, no user settings, hooks or MCP).
- Streams progress ("Reading data/customers/ORG-0049.json …") and the answer over Server-Sent Events.
- System prompt: answer in the UI language, ≤ 170 words, cite `Source: file → field`, neutral tone toward operators, data is synthetic.
- Tested: Finnish question "Onko jäte talvella painavampaa kuin kesällä?" answered in 12 s from `monthly.density_by_stream`; an injected "read /home/…/.bashrc" request was refused, and a direct `Read /etc/hostname` is **denied by the permission layer** (not just the prompt).
- Limits: 600 chars per question, 30 questions / 10 min / IP (IPv6 per /64), 500 questions / day globally, max $0.50 per answer, 3 concurrent, queue 10, 120 s timeout (SIGTERM → SIGKILL).
- Security review (separate reviewer agent) found one HIGH issue, now fixed: a question starting with `-` was parsed as a CLI option (e.g. `--debug-file`). User text is now prefixed (`User question: …`) and tools are fixed with `--tools Read Glob Grep` + `--disable-slash-commands`. Also fixed: queued-then-abandoned requests still spawning, unbounded rate-limit map, malformed URL/body → 500, CSP `base-uri/frame-ancestors/form-action`. Verified clean: path traversal, XSS (all rendering escaped, `script-src 'self'`), X-Forwarded-For spoofing (Caddy overwrites it).

## 5. Design (v2, minimal)

- **Identity** taken live from europressgroup.com and epsmart.fi with headless Chromium (`brand/`): the Europress SMART logo (navy `#000D61` SVG), Europress group logo (`#004070`), group accents `#1863DC` / `#03B4E0`, SMART mint `#54DEA9`; fonts Loos Wide / Open Sans (SMART), bio-sans / Poppins (group). The live portal (smart.europressgroup.com) shows only a login page publicly: navy `#214269`, mint `#72C0A2`, cyan `#11A1C5`, Roboto/Poppins.
- **System** follows the minimal principles of the reviewed "Haldus" stylesheet (not its colours or logo):
  - **Colour:** one token layer (hex values only in `:root`); ink = SMART navy for type and every primary action; neutral ground and white surfaces, **hairline borders, no shadows at rest** (only the drawer and menu float).
  - **Type and shape:** **Archivo** (close to Loos Wide) with **five sizes** (11/13/15/20/30); **four radii** (8/12/16/pill); a 4 px spacing grid; tabular numbers everywhere.
  - **State:** one `.state` pill recipe with **six roles** (good/warn/bad/info/mute/note), always with a word, never colour alone. Charts use muted categorical stream colours, with mixed waste as the dark neutral.
  - **Accessibility:** a global focus ring, 44 px touch targets, `prefers-reduced-motion`, and `aria-current` on the active tab.
- **Navigation:** the left links are **real tabs**: Overview · Savings · Machines · Operators & contracts · Weight & seasons · SMART Advisor (full page) · Account · For waste operators · FAQ.
- **Account switcher:** a top-right account button (initials, name, sector, machines) opens a menu with **Switch account** and **Account details**. The Account tab shows the customer profile, sites, and **every contract**: stream, operator, pricing model, lift fee, renewal and notice-by dates. A click opens the full price list (lift fee, per km, free km, haul/processing €/t, credit share, rental, minimum charge, penalties, fuel surcharge), its valid-from date, the change reason and the version.
- **Savings explained immediately:** the savings KPI says what most of it comes from, and right under the KPIs a **"How you save X € a year"** card shows a proportion bar plus the five levers in plain words with effort and euros. Each one opens its calculation.

Screenshots: `screenshots/` (01–02 overview FI/EN, 03 lever calculation, 05 operators, 06 FAQ, 07 mobile, 08 AI advisor, 09 account menu, 10 savings, 11 machines, 12 contracts, 13 weight, 14 account, 15 advisor empty, 16 contract price list).

## 6. Business-model hooks shown in the UI

- "Customers like you save X %" — the missing average-customer savings message.
- CTA "Talk to SMART Center" next to the savings potential.
- Idea from our notes: **first 12 months of SMART at a discount**, paid back by lever 1 (fuller pickups) alone for most customers.
- Operator tab = data operators do not have (forecast, fill at emptying, renewals) → ERP feed → operators gain from SMART too (win-win-win).

## 7. Limits (say them out loud)

- Synthetic data, hypothetical prices; savings are estimates.
- Weight is from the device weight model in this future scenario; the real algorithm is the weight team's work.
- No authentication — this is a demo; production needs per-customer login (SMART portal SSO).

## 8. Figma design system (node 4:44, file tODJ1f5NDUh2pWYVcB9SXW) — applied 2026-11-07

Node 4:44 is the template's style page (text styles, colour, components, assets), so it is applied as a system rather than as one screen:
- **Type:** Radio Canada Big (UI, headings, numbers), Source Serif 4 (explanations, the design's "Paragraph 2"), Geist Mono (buttons, captions, labels).
- **Colour:** `#6C6C6C` secondary text, `#DBE0EC` dividers, `#F6F8FB` grey surfaces, links blue, **"Quick win" green `#007E3F`**.
  - Design black → **SMART navy** and design yellow `#FFF546` → **SMART mint**, so the Europress identity stays.
- **Components:**
  - square ink buttons with the 4 px bullet ("▪ Explore all savings");
  - borderless 16 px cards with the design's 42 px icons (`img/icons/`);
  - hairline numbered lists (001–005).
- **Content block 4:430**, rebuilt as the top of the Overview:
  - left: the design's sky/textile photo (`img/fig/sky-textile.png`) with the floating number card showing live savings;
  - right: "How you save" as the numbered list, with an inline effort prefix ("Quick win:" in green, "Some work:" in amber, "At tender:" in blue), the euro amount, the number top-right and a serif description, closed by the black button.
- **Fix:** tabular figures were removed from proportional text. In Radio Canada Big they widen the space, comma and period glyphs, which caused the gaps in "How  you  save" and "€140 , 574".
- **Not used:** the template's own brand ("Aetherfield" logo, stickers, footer wordmark) and its other stock photos.

## 9. Machines: CombiMax drawing, 85 % pickup line, waste types (2026-11-07)

- **Drawing.** A line drawing of a Europress CombiMax, based on product photos (europressgroup.com, linemedia, vincit, csseadmed). Front to back:
  - hook-lift A-frame with hook;
  - press unit with sloped hopper lid, service door, control panel with socket and red E-stop;
  - tall collar frame;
  - container with top and bottom bands and a slightly rising roof;
  - rear door with hinges and lock;
  - skid rail with brackets, and front and rear rollers.
  Container length scales with the volume in m³. The code is `compactorSvg()` in `public/js/machines.js`; standalone SVGs are in `brand/combimax/` (mixed, cardboard, bio).
- **85 % is the top of the scale.** SMART orders the pickup automatically at 85 %, so the drawing never fills above the solid "85 %" line and the shown fill is capped there. At ≥ 80 % the card says "Pickup ordered automatically".
- **Pickup forecast = the earlier of:**
  - (a) reaching 85 % at the machine's recent daily fill rate;
  - (b) the stream's maximum days between collections (biowaste 7, mixed 21, others 28, from `material_classes`).
  The card names the reason ("auto pickup at 85 %" or "max interval"). The pipeline fields are `days_to_pickup`, `pickup_on`, `pickup_reason`, `pickup_ordered` and `fill_sensor_pct` (raw sensor value).
- **Waste types are distinct:** stream-coloured fill plus a type tag.
  - **Cardboard and plastic:** "Recyclable · earns credit".
  - **Paper:** "Recyclable".
  - **Biowaste:** "Bio · max 7 days".
  - **Mixed waste:** "Mixed · reduce it", with a hatched fill, a warning outline and an "Ask how to cut mixed waste →" link that sends the advisor a question about sorting that machine's waste.
- **Order.** "Your machines now" is the first block on the Overview.

## 10. Who sends the truck, and when (machine cards)

Every machine card has a truck line that says which waste operator collects it and how the truck is scheduled. The operator comes from the device record; the data's fictional "Hauler Delta" stands where a real operator such as Ragn-Sells would appear.
- **SMART on-call machines:**
  - before the order: "SMART orders the truck from {operator} on {date}, at {threshold} % full";
  - after the order: "SMART has ordered the truck from {operator}";
  - then "Truck expected ≈ {date} · usually {h} h after the order".
  - The threshold is each machine's own SMART order setting (here 60–80 %). The lead time is the machine's median order-to-truck time from past on-call lifts, falling back to the operator's scorecard median. If the stream's maximum interval comes first (biowaste 7 days), the card says "(max interval)".
- **Fixed-schedule machines:** "{operator} drives by timetable: every Monday & Thursday / every other Wednesday …" plus "Next truck {date} · machine ≈ {fill} % full". If that visit will empty a machine below 60 %, the card says "Truck comes half-empty — switch to SMART on-call".
- **Tips and trust:**
  - Non-bio machines that order below 75 % get "Orders at {x} % — raise to 85 % for fewer trucks". This is the card-level view of savings lever 1.
  - Each card shows the operator's on-time rate from the scorecard.
- **Data fields** (also documented for the AI advisor): `operator`, `operator_on_time_pct`, `policy`, `order_threshold_pct`, `schedule_weekdays`, `schedule_per_week`, `lead_h`, `order_on`, `truck_on`, `visit_fill_pct`, `pickup_reason`.

## 11. Machine views and Trends tab

- **Machine view toggle** (Design · Mixed · Table) on both machine sections. The Overview opens in **Design** (drawing cards); the Machines tab opens in **Mixed**.
  - **Mixed:** one row per machine, with a small CombiMax drawing and fill % on the left and an information grid on the right: machine and site, stream and type tag, scheduling (SMART on-call threshold or operator timetable), operator and on-time rate, next truck, weight now (demo) and fill per day. Mixed-waste rows keep the "Ask how to cut mixed waste" link.
  - **Table:** machine, stream, fill now, scheduling, operator, next truck, fill when the truck arrives, weight.
- **Trends tab:**
  - **"What changed":** a numbered findings list in the Figma list style. The last 3 months are compared with the first 3 and tagged Better / Watch / Pattern: mixed-waste tonnes and share, €/t, fill at emptying, pickups per month and recycling rate, then the busiest day, busiest hours, winter vs summer and truck day.
  - **Charts:** mixed waste over time (tonnes + share), tonnes by stream, €/t + pickups, and fill at emptying vs the 85 % target.
  - **When the work happens:**
    - a weekday × hour heatmap of compactions (a person always starts one, so this shows when waste is thrown in);
    - fillings vs pickups by weekday and by hour;
    - fill gained per machine-day and compactions by month, with winter in blue and summer in amber.
- **Demo customer:**
  - Saturday brings the most waste (17 %) and Monday the least, but **most trucks come on Monday**.
  - Waste is thrown in mostly 18–21 h (25 %) and in shift blocks 7–9 / 11–13 / 17–20, while trucks come mostly 7–10 h.
  - Winter fills 3 % faster per day, but summer has 15 % more compactions.
  - Mixed waste rose from 22.6 to 28.6 t a month (56 → 60 %) and the recycling rate fell from 44 to 40 %. €/t improved from 278 to 253.
- **Data:** hourly telemetry is aggregated once in `pipeline/build_data.py` (`hourly_activity`, `time_patterns`, `monthly_ops`, `trend_findings`). The full rebuild takes about 36 s.

## 12. After the 2nd Europress briefing (second_transript.txt): simplify, answer first, sales alerts, weight model

Tommi's feedback: "simplify, simplify, simplify"; show ready-made answers instead of reports and drill down on click; write "instructions for dummies"; tell sales "what to tell the customer"; quality is not graded (a load is accepted or burned); make the weight model extendable and retrainable (seasons, frozen waste, a cheap reference sensor plus a trained model); customer invoice upload is "probably not feasible", so it was **not built**. **SMART Lite / Complete tiers: postponed (user decision).**
- **"What should I do?"** is the first card on the Overview. It answers Tommi's framework of questions:
  - are you using your machines well;
  - is something not adding up (half-empty pickups, invoice lines off the price list, device weight vs weighbridge);
  - are you paying the right price;
  - is everyone keeping the contract;
  - how do I recycle more;
  - CO₂;
  - is everything safe (hours the machines stood full).

  Three levels: a one-line answer → click for why + numbered steps → "Show the calculation" or "Ask SMART Advisor". Answers are sorted worst first.
- **SMART Advisor floats bottom-right** on every page and is context-aware:
  - it shows "Looking at: {page} · {account}";
  - it sends the page plus whatever the user clicked to the server, which adds page-specific hints;
  - it offers ready-made questions per page;
  - it answers short: one line, ≤ 3 steps, source, and a "Tell the customer" line for sales.
- **Quality:** A/B/C grades are removed everywhere. The site now shows accepted vs rejected (burned) per stream, rejection hotspots, and an insight when > 3 % of a customer's loads are rejected (fleet average 2 %; mixed plastic 8.5 %).
- **Weight model with a version toggle** (Weight & seasons tab). Fitted on clean weighbridge tickets (single load, weighed tare, no side waste), trained Oct–Mar, tested Apr–Sep on 3,522 lifts:
  - **v1** fill × volume × density table: median error 15.4 %, 34 % of lifts within ±10 %.
  - **v2** + density per stream × season (frozen winter waste): 13.7 %, 38 %.
  - **v3** + per-machine calibration from the machine's own tickets: **7.0 %, 63 %**. 345 machines are calibrated; Hauler Delta's are not, because that operator shares no tickets.
  - **v4** (planned): + temperature, humidity and pressure curve once the firmware exports them.

  The retrain path is shown in the card. The selected version drives every "≈ kg inside" on the machine cards.
- **Sales alerts** (Europress workspace → Sales pipeline): one notification per customer, ranked by €.
  - **Rules:** order levels still < 75 % (→ SMART optimisation review), timetable trucks finding machines half-empty (→ SMART on-call), mixed waste rising (→ baler / recycling compactor), contract notice within 90 days (→ tender benchmark), machines standing full for many hours (→ bigger or second machine).
  - **Each alert has** the numbers, "Tell the customer: …", what to offer, and "Get a briefing from SMART Advisor" (tested: a 17 s briefing with offer, ROI and deadline).
- **Fonts:** Radio Canada Big, Source Serif (Figma's "Source Serif Pro" = Google's "Source Serif 4") and Geist Mono already match the Figma file.
