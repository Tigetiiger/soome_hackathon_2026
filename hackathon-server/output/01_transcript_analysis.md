# Europress briefing — what they told us

Source: `input-files/Europress_SinceAI2026_FINAL/europress-brefing.txt` (≈ 40 min, Speaker 0 = Europress representative).
Part 1 (00:01–20:40) is mostly **Finnish** feedback to other teams (some Estonian side-talk). Part 2 (20:45–40:20) is **our team's English Q&A**.
Our own notes from the session are cross-referenced at the end.

---

## 1. Finnish section — translated key messages

| Time | What Europress said (FI → EN) | Implication for us |
|---|---|---|
| 00:12 | "Most of these questions are already covered by the SMART system. So you can focus on this — the **weight**." | Don't rebuild SMART; build around weight. |
| 00:19 | "Always consider **for whom** — put your hat on, pitch it as you would pitch to that customer." | Dashboard is written *to* the end customer. |
| 00:45 | "Many times it has a domino effect: it benefits the customer, and **sales** follow." | Customer value → machine + SMART sales. |
| 05:10 | "Most of our devices already **predict fill-up**; scheduling systems use the forecast. Operators combine two pickups in remote areas." | Fill prediction is solved — don't sell it. |
| 06:05 | "For fill prediction there's maybe no need." | Same. |
| 06:14 | "With weight — **every invoice, every contract, everything is about weight**." | Weight is the currency of the customer–operator relationship. |
| 06:37 | "Fill level correlates quite well with weight. **We just don't know it. We only estimate. We have no evidence.**" | Show weight *with* its evidence level (ticket-verified vs device-only). |
| 07:25 | "If the data is OK and noise can be cleaned, prediction isn't the point of this product — take it as a hypothesis." | Weight algorithm = separate workstream (another team). |
| 08:12 – 10:04 | Driver incentive idea from another team: "win-win-win — driver, operator, customer". "We should be able to offer something to operators too; today we can't." | Side goal: an operator view. |
| 10:16 | Customers care about: **machines as full as possible, as few transports as possible (CO₂), no trucks idling in the yard.** | KPIs: fill at emptying, pickups, CO₂. |
| 10:54 | "The **customer chooses the next operator**." | Tender-readiness view is high value. |
| 12:37 | "Reducing one pickup pays for itself to some extent… our optimisation service already reached a bit over **10 %** of the target; now we aim higher." | Early-lift lever must be shown in euros. |
| 16:30 | "Think of the **whole loop**: machine on site → customer throws waste → alert → transport → weighing. **What visibility, at which step, for whom?**" | Provenance on every number = visibility of the loop. |
| 17:40 | "We have **no long-term data on how volume/density varies, e.g. cardboard, winter vs summer**." | Density-by-month chart is new information for Europress. |
| 18:45 | Pressure + season/weather could explain weight; moisture can't be measured reliably from the mass. | Out of scope for dashboard; note as limitation. |
| 20:13 | Some products have expensive sensors — "costs so much it's not worth it". | Software-first, near-zero hardware. |
| 20:23 | "Make a **statement of how you got there** (weighing) — but **the meat is the business model**." | Dashboard = business model in action. |

## 2. English section — our Q&A

| Topic | Answer | Implication |
|---|---|---|
| Is SMART the most profitable? | Yes — technical + digital features + service as one value-added service. | Upsell vehicle. |
| Pricing | **Only a service fee, no up-front charge.** "Solution based." | Free/intro view → paid SMART conversion. |
| What SMART optimises | Max weight per emptying without overflow; empty as close to 100 % fill as possible. SMART Center reviews target vs actual monthly. | Fill-at-emptying gauge vs 85 % target. |
| Missing | "**What we don't have is the weight**… we can only guesstimate." | Weight evidence panel. |
| Who sets prices | Operator and customer contract; **Europress is not a party**. | Neutral language; "recommend, not decide". |
| Europress' role | "**Safeguards or controllers on behalf of the customer** — that your operator is not overcharging you." Visibility of when the machine was emptied already exists. | Sense of control for the customer. |
| Customer questions they can't answer today | Am I paying the right amount? Is the operator doing its best? Are SLAs kept? Would another operator serve me better? | Operator scorecard + invoice check + €/t benchmark. |
| Contracts | Usually **3-year** contracts, then a **tender**; customers lack tools to compare. | Notice-by dates, tender lever. |
| LLM wish | "LLMs could crunch the data: **mixed waste growing, recycling rate going the wrong way**." Customers need it for **environmental reporting**. | AI advisor; mixed-waste insight; ESG summary prompt. |
| Win-win-win | Customer gets best operator/price; operator keeps or wins customers; Europress sells machines and services. | Customer view + operator view. |
| Fill prediction | Predicts "**next 7 days no worries**" from compaction starts, motor run time, real-time fill, pressure curve. Works well; nothing needed. | Don't compete with it. |
| Compaction start | Always started by a user — safety rules prohibit automatic start. | FAQ. |
| Sustainability | With weight they can tell a customer "your mixed waste has grown over 6 months"; three-party optimisation of recycling rates. | Recycling vs mixed-share chart. |
| Remote service | Remote diagnostics: sensor states, electrical connections, blown fuses; physical faults need a visit. | FAQ. |
| Strategy | "**More than a device manufacturer** — earlier in the value chain; weight is the key." | Pitch framing. |
| Existing weighing | Platform scale (costs as much as the compactor — few want it); Scaletipper dynamic weighing. "Holy grail: the compactor always knows its weight." | Evidence levels in the dashboard. |
| Our idea: strain on walls | Open — "what factors? humidity? winter vs summer?" | Weight team. |
| E-stop | Emergency stop. | FAQ. |
| Connectivity | **SIM card, 4G/5G**; tilt sensor, GPS, movement sensors → they know when the container is lifted/transported. | FAQ; event source. |
| Electricity | **3–5 kW motor — "peanuts"**. | FAQ. |
| ERP integration | Either the **waste operator's ERP** or the **property manager's** system — "those are the two who don't have the data". | Side goal: operator data feed. |

## 3. Our notes ↔ what we built

| Our note | Where it is handled |
|---|---|
| "Loppcustomer on peamine" (end customer is the main one) | Whole customer dashboard, FI/EN. |
| Safeguards & controllers — **feeling of control, at least visibility** | Clickable provenance on every value; operator scorecard; invoice second look. |
| Problem: **they don't advertise what an average small/medium customer saves** | "Customers like you" card: median savings per segment (small / medium / large). |
| Price agreed or fluctuating? | Contract price list per version; invoice check compares to it. |
| Is SMART most profitable? → yes | SMART CTA on the dashboard. |
| Idea: SMART discount first 12 months | Business-model note in `02_dashboard.md` §6. |
| **PRIORITY: EDUCATE THE CLIENT** | Insights + AI advisor + explanations; every lever has a plain-language description. |
| **IMPORTANT: % by stream — mixed is bad, make it less; recommend what to do** | Recycling-rate vs mixed-share chart, mixed-rising insight, sorting lever, AI. |
| Prediction model: machine fill-up | Already in SMART — not rebuilt. Used only for the operator 14-day forecast. |
| IDEA: LLM + ERP integration | AI advisor over the same data; operator view = ERP-ready feed. |
| **IMPORTANT: clicking on a value shows where the info comes from** | Drawer: value, formula (FI/EN), assumption, source tables, contributing rows, "ask AI". |
| Goal: show the most information to the end customer | KPIs, 5 levers, machine table, operators, weight evidence, density. |
| IMPORTANT: WEIGHT | Weight evidence donut + tonnes everywhere; algorithm left to the weight team. |
| We are more than a manufacturer | Pitch framing. |
| Is info different winter vs summer? | Density-by-month chart; AI answers it from data. |
| Electricity 3–5 kW → FAQ | FAQ page. |
| ERP data to the best | Operator tab. |

## 4. Five takeaways

1. **The product is trust in the invoice.** Weight is what customers pay for; Europress wants to be the neutral party that makes it visible.
2. **Don't rebuild fill prediction.** It works. Use it, don't sell it.
3. **Educate → save money → buy SMART.** The customer must *see* savings in euros, with the calculation behind them.
4. **Win-win-win.** Customers get a better deal, operators get data to plan and to keep customers, Europress sells machines and services.
5. **Business model over sensor physics.** Say how weight is obtained, then spend the pitch on value.
