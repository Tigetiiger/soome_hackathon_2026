# Europress Virtual Scale: Research Brief

_Draft 1, 2026-11-06. To be updated after the 18:50 Europress briefing._

## 1. The problem in one line

Europress compactors know **how full** they are but not **how heavy** the load is. The real weight only appears on the weigh ticket at the processing plant. That means value, pickup timing and problems are all invisible until it is too late.

## 2. What we found

### Europress today
- Europress (Finland) already sells **SMART**-connected compactors (e.g. Combi, CombiMax) that plug into **Europress SMART Fleet Management**. It reports **fill level, location and an estimated fill-up date** (SMARTwaste app). Reference sites include Karisma shopping centre in Lahti and Olvi's recycling centres.
- We found **no public evidence** that SMART exposes raw hydraulic pressure or per-cycle data, and **no weight estimation**. That gap is the one we fill.
- Sources: [Europress SMART compactors](https://www.environmental-expert.com/products/waste-compactors-with-smart-technology-1087149), [Combi/CombiMax listing](https://www.environmental-expert.com/products/waste-compactor-1087154), [Olvi case](https://recyclinginside.com/recycling-technology/volume-reduction-technology/from-waste-centers-to-recycling-centers-positively-finnish-olvi/), [SMARTwaste app](https://apps.apple.com/cd/app/smartwaste/id1444009270), [Vincit × Europress](https://www.vincit.com/work/europress)

### Can weight be estimated from compactor signals?
- **Yes, roughly, and this is established practice.** Patents describe inferring fullness from peak ram pressure (typically 0–2500 psi, rising as the container fills). Load weight is then converted "from past experience" ([US4643087](https://patents.google.com/patent/US4643087), [US5299142](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5299142)).
- **Known confounders** that a model must handle: hydraulic oil temperature, material type (cardboard springs back, while metal and wet waste do not), and container geometry ([US6738732](https://patents.google.com/patent/US6738732)).
- **Nobody seems to learn this from weigh tickets.** The closest ML work is image-based weight estimation (MAE 2.38 kg, MAPE 3.1%, [arXiv 2603.00931](https://arxiv.org/pdf/2603.00931)). It uses a physics-informed fusion approach, which is a good framing to borrow.
- The alternative is load cells under the container ([US12379240](https://patents.google.com/patent/US12379240)), which means new hardware. Our pitch is "**no new scale needed**".

### Market benchmarks for the business case
| Item | Figure | Confidence |
|---|---|---|
| Compactor monitoring subscription | $25–60 / unit / month; another vendor ~$900/yr + $600 hardware | Medium (vendor sites) |
| Break-even | eliminate ~1 pickup every 1–2 months | Medium |
| Collection cost savings from smart pickups | 20–40% (vendor claims, not audited) | Low–medium |
| OCC (cardboard) price, Europe | ~€120/t ex-works, €140–150/t delivered (2025), firm in 2026 | Medium (BIR via trade press) |
| CO₂ avoided per tonne recycled | Cardboard 0.3–3.1 t, steel 0.9–1.8 t, aluminium 9–11.6 t, PET 1.4–3.4 t | Wide spread. Pick one source and cite it |

Sources: [WM compactor monitoring](https://www.wm.com/documents/pdfs-for-services-section/Compactor%20monitoring%20service_Watching%20your%20bottom%20line.pdf), [Harmony savings](https://harmony1.com/?p=7918), [Zters](https://www.zters.com/z-sight-dumpster-cameras), [Recycling Today / BIR](https://www.recyclingtoday.com/news/paper-recycling-global-trading-occ-cardboard-late-2025-bir), [letsrecycle 2026 prices](https://www.letsrecycle.com/prices/waste-paper/uk-domestic-mill-prices/2026-domestic-mill-prices/), [EnvEurope emission table](https://enveurope.springeropen.com/articles/10.1186/s12302-021-00519-6/tables/5), [Turner et al.](https://ideas.repec.org/a/eee/recore/v87y2014icp30-45.html)

> ⚠️ **CO₂ factors**: use one consistent dataset (e.g. EPA WARM or the EnvEurope table) and print the source on the dashboard. Judges may ask.

## 3. Solution design

### 3.1 Virtual scale (the core)
**Inputs per compaction cycle / per container:** peak pressure, pressure curve (ramp time), cycle count since empty, fill level %, material type, container volume, oil temperature (if available), timestamp.

**Approach (fits the 48 h budget):**
1. **Physics baseline:** `weight ≈ volume × fill% × density(material, pressure)`. This works from day one, with zero training data.
2. **Learned correction:** a gradient-boosted model (LightGBM or scikit-learn `HistGradientBoostingRegressor`) predicts the ticket weight from the features above plus the baseline.
3. **Uncertainty:** quantile regression (p10/p90) so the UI shows **"1.84 t ± 0.15 t"**. This builds trust and is a strong demo point.
4. **Self-calibration:** each new weigh ticket updates a per-container bias term. The pitch: "it gets more accurate every pickup". Show the accuracy curve improving over time.

**Metric to show:** MAPE vs weigh tickets, e.g. "within 6% of the plant scale". Use a real number from our validation, not an invented one.

### 3.2 Value view
`€ value = estimated weight × material price (€/t)`, and `CO₂ avoided = weight × factor`. Show this per container, per site and per customer. Hero number on the dashboard: **"€ 12 480 of recyclables sitting in your containers right now"**. Include a material price table with an "as of" date.

### 3.3 Anomaly alerts (plain language)
| Alert | Detection | Message example |
|---|---|---|
| Wrong material | Implied density outside the material's band (e.g. "cardboard" container at metal density) | "Container 3 at Prisma Lahti is much heavier than cardboard should be. Possible metal or wet waste." |
| Faulty sensor | Pressure flatline, fill level stuck, fill rising with no cycles | "Fill sensor at K-Market Oulu hasn't changed in 3 days while the compactor ran 41 times." |
| Strange weight change | Big jump between cycles, or ticket far off the prediction (residual z-score > 3) | "Last pickup weighed 40% more than predicted. Check what went in." |
| Approaching full / high value | Forecast | "Worth collecting: €310 of cardboard, 88% full, full by Thursday." |

Implementation: rules plus residual z-scores, with an optional `IsolationForest`. A templated sentence for each alert makes it read like a human wrote it.

### 3.4 Smarter pickups
- Trigger a pickup when **value ≥ threshold** OR **fill ≥ 85%** OR **forecast full within 48 h**, instead of a fixed weekly schedule.
- KPI: **average truck payload utilisation**, e.g. 55% on a fixed schedule vs 90% value-based (simulated before/after).
- Optional: route the day's pickups with Google **OR-Tools** VRP and draw them on the map.

### 3.5 Customer dashboard + assistant + monthly report
- **Assistant (no API key, so faked):** intent matching (keywords/regex) answered by functions over the same data, e.g. "What did cardboard earn in October?", "Why is site X flagged?", "When is my next pickup?". Stream the answer word by word so it feels like an LLM. Keep it behind one `answer(question)` interface so the Claude API can replace it later.
- **Monthly material report:** a one-page PDF covering tonnes per material, € value, CO₂ avoided, pickups saved and alerts. Generate it with `@react-pdf/renderer`, or print-CSS plus the browser's "Save as PDF".

## 4. Simulated data (until Europress gives us real data)
Generate with Python (numpy/pandas). Use a fixed seed so the demo is reproducible.
- ~10 customers, ~30 sites, ~60 compactors across Finland (real city coordinates).
- Materials: cardboard/OCC, mixed waste, plastic, metal, biowaste, each with a density band and price.
- Per compactor: compaction cycles (timestamps, peak pressure, oil temp), fill level, pickups, and a **weigh ticket with noise** at each pickup.
- **Injected faults** for the demo: 1 wrong-material event, 1 stuck sensor, 1 weight spike.
- A **"live replay" mode** streams events at ×1000 speed so the dashboard visibly updates during the pitch.

Tables: `customers`, `sites`, `compactors`, `cycles`, `pickups`, `weigh_tickets`, `material_prices`, `alerts`.

## 5. Recommended stack and tools

| Layer | Tool | Why |
|---|---|---|
| Frontend | **Next.js (App Router) + TypeScript + Tailwind** | Fast, deploys to Vercel in one click |
| UI kit | **shadcn/ui** + **Tremor** (KPI cards, bar lists, sparklines) | Polished SaaS look with little effort. Both are built on Recharts |
| Charts | Recharts (via shadcn charts/Tremor) | Covers the chart types we need |
| Map | **react-map-gl + MapLibre** (free tiles) or react-leaflet | Site map with coloured fill/value markers |
| Motion | framer-motion / `motion` | Count-up € figure, alert slide-ins |
| Toasts | **sonner** | Live alert pop-ups during the demo |
| Icons | lucide-react | Ships with shadcn |
| Backend | **FastAPI (Python)** | Serves the model, alerts and assistant. SSE for the live stream |
| ML | scikit-learn / **LightGBM**, pandas, numpy | Quantile GBM in a few lines |
| Routing (optional) | Google OR-Tools | VRP for pickup routes |
| Report | @react-pdf/renderer or print CSS | Monthly PDF |
| Data store | SQLite or plain Parquet/JSON | No infra to babysit |
| Deploy | Vercel (frontend) + Render/Fly/Railway (API), or everything local | Have a local fallback for the demo |

Note: some of the Tremor details (now free, Vercel-backed) come from secondary sources ([AdminLTE](https://adminlte.io/blog/tremor-dashboard-templates/), [pkgpulse](https://www.pkgpulse.com/guides/recharts-v3-vs-tremor-vs-nivo-react-charting-2026)). Check tremor.so at setup.

## 6. Dashboard layout (one screen that wins)
```
┌──────────────────────────────────────────────────────────────┐
│  [Logo] TrueLoad          Customer: Kesko ▾     ● Live        │
├──────────────────────────────────────────────────────────────┤
│   € 12 480              38.6 t            21.4 t CO₂          │
│   recyclables value     estimated now     avoided this month  │
│   ▲ 8% vs last month    ± 4% accuracy     ≈ 9 flights HEL-NYC │
├───────────────────────────────┬──────────────────────────────┤
│   Map of sites (colour = €,   │  ⚠ Alerts (plain language)   │
│   size = fill)                │  • Wrong material at …       │
│                               │  • Sensor stuck at …         │
│                               │  ✓ Worth collecting: …       │
├───────────────────────────────┼──────────────────────────────┤
│  Predicted vs ticket weight   │  Pickups: fixed vs smart     │
│  (accuracy improves over time)│  truck fill 55% → 90%        │
├───────────────────────────────┴──────────────────────────────┤
│  💬 Ask: "What did cardboard earn us in October?"             │
└──────────────────────────────────────────────────────────────┘
```

## 7. Business case (example numbers to replace with briefing data)
Assumptions to **verify with Europress**: haul cost per pickup, current pickup frequency, price point.

- Customer site: 1 cardboard compactor, fixed schedule of 8 pickups/month at **€180/haul** (assumption) = €1 440/month.
- Smart pickups cut 25% of hauls (the low end of the 20–40% benchmark) and **save €360/month**.
- Subscription: **€49/compactor/month**, in line with the $25–60 market benchmark. The customer nets **~€310/month, a 7× ROI**.
- Europress: 1 000 connected compactors × €49 × 12 = **€588k ARR**, plus fuller trucks, better route planning and sustainability-report upsell.
- Pricing tiers idea: **Basic** (virtual scale + value) / **Pro** (alerts + smart pickups + assistant) / **Enterprise** (reports, API, ESG export).

## 8. Name ideas
- **TrueLoad**: says what it does
- **Painokas** (Finnish for "weighty" or "significant"): local flavour, good pun
- **KiloSense**
- **PressWeight**

## 9. Suggested 48 h split (4 people)
| Person | Owns |
|---|---|
| A: Data/ML | Simulator, virtual-scale model, accuracy metric, anomaly rules |
| B: Backend | FastAPI endpoints, live SSE replay, fake assistant, report data |
| C: Frontend | Next.js dashboard, map, charts, alerts, assistant UI |
| D: Business/pitch | Business case numbers, name/logo, slides, demo script, monthly report design |

Milestones: **H+6** simulated data + static dashboard · **H+20** model + alerts wired in · **H+32** live replay + assistant + report · **H+40** feature freeze, polish, rehearse the demo ×3.

## 10. Questions for the 18:50 briefing
1. What signals do compactors actually log (pressure curve or just peak? cycles? oil temp? fill-level method)? At what frequency, and in what format?
2. Can we get **historical weigh tickets** joined to compactor IDs? How many?
3. Which materials and container sizes are most common?
4. What does a pickup cost today, and how are pickups scheduled?
5. Who is the paying customer: Europress's direct customers, waste haulers, or both?
6. Does an existing SMART Fleet Management API or brand guideline exist that we should match?
7. Which material prices and CO₂ factors does Europress use or trust?
