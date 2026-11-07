# 05 · SMART Weight & Insight: business plan and dashboard add-on

**Europress × Since AI 2026**, 7 November 2026.

- **Visual version:** `05_business_plan_addon.html`, published at https://claude.ai/artifact/MeVR2iDqkQvdfK25AYEpMp (private until shared). It includes live mockups: the five-answer customer home, the fleet map with real weather, the weather alerts, the 3D weight lab, the operator feed, the sales brief, quality charts and the architecture diagram.
- **What this builds on:** `01`–`04`, the second Europress feedback session (`input-files/second_transript.txt`), the SmartWeight hardware study, the compactor simulator (`simulator-weather-and-stuff`), the virtual-scale study, and the dashboard code.

**Evidence tags:**
- **[P]** practice data (synthetic, with invented prices)
- **[S]** our simulator
- **[R]** real public data
- **[E]** our estimate
- **[A]** our assumption

## 0. In one minute

- **The problem.** Every invoice and every contract is about weight, and only the party paid per tonne knows it.
  - Customers can't answer "am I paying the right amount, is the operator keeping the contract?"
  - Salespeople need "tell me what to tell the customer".
  - Europress can offer operators nothing today.
- **The add-on.** Seven modules on one data spine:
  - M1 Weight engine
  - M2 Answers
  - M3 Sales briefs
  - M4 Operator feed
  - M5 Map & weather
  - M6 Quality
  - M7 Reporting pack
  
  Rules decide, Claude explains with citations, and a person approves.
- **The money.** Expected add-on revenue is about €0.91M a year by 2029 [E]. The real value is stickier SMART and service contracts: the subscription alone has a 6-year NPV of −€0.33M, which becomes +€0.23M once service retention and upsell are counted.
- **Phase 0 cost.** About €211–267k, with a stop gate. The €0 first test runs archived SMART pressure curves against shared tickets.

## 1. What changed since 04 (from the second feedback session and new research)

| New input | Effect on the plan |
|---|---|
| Tommi gave a framework of questions: cost, safety, CO₂, contract/SLA, recycling. He wants ready-made answers instead of forcing users to ask, and drill-down after | **M2 Answers** becomes the customer home page: five cards, one sentence each, red/amber/green, and an email when a card turns red |
| "Tell me what I should tell to the customer", "60–70 % of information is ignored" | **M3 Sales briefs**: rules rank customers each night, Claude writes 3 cited sentences, a salesperson approves → CRM |
| He liked the predictive pickups for operators | **M4 Operator feed** with expected tonnes, delivered as JSON/CSV/webhook into the operator's ERP |
| Quality is "our next exercise"; weight plus quality is "a super position" | **M6 Quality**, starting from operator grades already in the data (6,721 assessments [P]) and adding cameras later |
| Hybrid: "one cheap sensor as a reference point + trained model"; the model must handle seasons and frozen waste and stay extendable | Weight ladder T0–T3 with a reference cohort; FMI weather as model features |
| Retrofit machines expose only a "full" lamp, no pressure | Their weight is labelled a rough fill × density estimate |
| Europress doesn't sell data; the customer owns it | Every price is a tool or service subscription |
| End-customer invoice upload is "probably not feasible"; integrate with the ~20 operators instead | No invoice upload; integration goes operator-side only |
| "Simplify, simplify, simplify" | Same three workspaces; answers before reports; 3D only in the Europress Weight lab |
| Open-Meteo's free tier is non-commercial | Production weather comes from **FMI** (CC BY 4.0), with MET Norway as fallback |
| CSRD scope narrowed (Omnibus I: >1,000 staff and €450M turnover, in force 18 Mar 2026) | The reporting pack is pitched as voluntary or supply-chain driven |
| Dashboard CO₂ factor of 1.1 kg/km is likely low | Shown as a range of 1.5–3.8 kg/km (from EU JRC 57–141 L/100 km) until Statistics Finland publishes its factor |
| Weighing in motion falls under OIML R51 / MID 2014/32/EU, not only NAWI | Legal note updated; T3 is verified by Kiwa (notified body 0424) |
| 04 put the reference scales at €10–19k | Corrected to €34–63k for 10 machines × T2, per `BILL_OF_MATERIALS.md` |

## 2. Problems → modules

| # | Problem | Module | Proof |
|---|---|---|---|
| 1 | Weight is only estimated | M1 | Monthly error ≤ 6 % vs the reference cohort |
| 2 | "Am I paying right / are SLAs kept?" | M2 + M1 | Checkable pickups 9 % → 90 %+ (demo: 37 of 395 today [P]) |
| 3 | Customers aren't experts | M2 + digest | Weekly active users |
| 4 | Sales needs clear answers | M3 | SMART adoption beyond 15 % |
| 5 | Nothing to offer operators | M4 | Ticket sharing ≥ 90 % |
| 6 | Seasons, frost, rain unknown | M5 | Weather features help in the Phase 0 test |
| 7 | Quality unmeasured, mixed waste rising | M6 | Mixed share ↓, rejections ↓ |
| 8 | Environmental reporting | M7 | Reports exported |

## 3. Dashboard integration

**Navigation.**
- **Customer:** Answers (new home) · Savings · Machines with site map ↑ · Contract & service level ↑ · Weight & quality ↑ · Trends & weather ↑ · Advisor · Reports (new) · Account/FAQ.
- **Europress:** Overview · Fleet map (new) · Sales briefs (was Pipeline) · Fleet health · Weight lab 3D (new) · Data products.
- **Partners:** Pickup feed with tonnes ↑ · Route map (new) · Quality feedback (new) · API keys & ticket sharing (new).

**Build items.**

| Item | Where | Library or source | Effort |
|---|---|---|---|
| Answers + email digest | `pipeline/answers.py`, `public/js/answers.js` | existing `traced()` helper | 3 wk |
| Weight engine | `pipeline/weight_engine.py` (runs the `weight_train` model) | LightGBM + conformal intervals | 4 wk |
| Weather + alerts | `pipeline/weather.py` → `/api/weather` | FMI WFS (opendata.fmi.fi), MET Norway fallback | 2 wk |
| Map | `public/js/map.js` | MapLibre GL + MML/Digitransit vector tiles, deck.gl | 3 wk |
| Weight lab 3D | `public/js/lab3d.js` (Europress only) | plotly.js / three.js | 1 wk |
| Sales briefs | `pipeline/briefs.py`, existing read-only Claude sandbox | Claude Sonnet, citations required | 3 wk |
| Operator feed API | `server.mjs` `/api/operator/feed` | JSON/CSV/webhook; AMCS/WasteHero mapping | 3 wk |
| Quality panel | quality_assessments → tickets → lifts | Chart.js | 1 wk |
| Login + consent | SMART portal SSO, Data Act flags | Vincit | 4 wk |

**Demo customer answers** (Hospitality Customer 0049, data to 30 Sep 2026) [P]:

| Card | Answer | Supporting facts |
|---|---|---|
| Cost | €140,574 a year, about €60k of it saveable | Mostly half-full pickups: 49 % average fill |
| Safety & uptime | No open faults | 2 door-interlock faults fixed; 146 h downtime; 5 electrical faults |
| CO₂ | 2,060 truck-km a year avoidable | ≈ 3–8 t CO₂ |
| Contract & service | Hauler Delta on time 57 %, shares 0 % of tickets | Notice due by 17 Oct 2026 |
| Recycling | 43 % | Mixed waste rose from 55 % to 58.5 % of tonnes |

**Weather** [R, ERA5]:
- **Helsinki, Oct 2025–Sep 2026:** 71 frost days; the minimum was −18.7 °C on 1 Feb 2026; Sep 2026 had 108 mm of rain.
- **Oulu region, Jan 2026:** −14.2 °C mean, 30 frost days.

**Alert rules:**
- Rain week + open hopper → close the lids. In the simulator, wet open-hopper cardboard weighed +4–6 % [S].
- Frost → collect biowaste before the cold spell.
- Snowfall → re-tare and widen the weight range.
- Storm → the operator moves pickups forward.

## 4. Weight ladder

| Tier | Hardware | Cost per machine | Accuracy | Grade |
|---|---|---|---|---|
| T0 soft sensor | firmware stroke logging | €0 | ≈ 4–7 % mean per pickup [S]; ±5–6 %/month [E] | estimate |
| T1 + cheap sensors + tickets | oil-temp probe €20–40, lid switch ~€10, hopper T/RH ~€15 [A] | €60–130 | ≈ 3.5 % after 5 tickets [S] | estimate |
| T2 reference cohort | 4 × IP68 C3 load cells | €3.4–6.3k | P95 ≈ 2.3 % [S] | verification |
| T3 certified | OIML cells, indicator, Kiwa verification | €5.4–10k + €150–400/yr | P95 ≈ 1.4 % [S] | billing |
| Quality camera | hopper camera + edge AI | ≈ €300–800 [A] | contamination score | estimate |

**Open conflict.** The two studies disagree on pressure-based weight:
- The simulator soft sensor reaches 4.7 % mean error on unseen machines (61 % of pickups within ±5 %).
- The hardware study reaches only about 29 % P95 on pressure-only estimates, because water and stiffness change the mass without changing the pressure.

Phase 0a, the €0 archive test, settles it.

## 5. Market

All of these products measure fill. **We found no commercial compactor "virtual scale"**, only patents.

| Product | Weight? | Notes |
|---|---|---|
| Bramidan BRA-IN | No | Optimize tier sends schedules to haulers; Retrofit tier covers other brands |
| Orwak Connect | Premium built-in scale | Alerts in a portal |
| Marathon / 3rd Eye | No | Fill, status, location |
| Sensoneo | No | Fill sensors + SaaS |
| Nordsense | No | ≈ DKK 1,000 per sensor per year |
| Enevo | No | Monthly fee per container |
| Compology | No | In-container camera, ≈ $30 per camera per month |
| WasteHero, AMCS, Ecomond | Uses truck/weighbridge weights | Operator software; integration partners |
| Tamtron | Yes, the operator's | Legal-for-trade truck scales: Urbaser 40+, Remeo 17 |
| Stena, L&T portals | Yes, the operator's tickets | CO₂ and CSRD exports |

## 6. Money

**Pricing** [A]:
- Answers + weight preview: free, in Intro.
- Verified Weight: €15 per machine per month, €12 in a lease.
- Proof of Fullness: 25 % gain-share.
- Integrated reporting pack: €10–40k per chain per year.
- Operator feed: free with ticket sharing; Pro €500/month.
- Camera tier: €25 per machine per month.
- Scale on lease: +€39–49 per month.

**Revenue** [E], €M per year:

| Case | 2027 | 2028 | 2029 |
|---|---|---|---|
| Pessimistic | 0.05 | 0.15 | 0.26 |
| Expected | 0.15 | 0.50 | 0.91 |
| Optimistic | 0.30 | 1.0 | 2.1 |

Expected 2029 breaks down as:
- Verified Weight on 3,000 machines: €540k
- 8 chain licences: €160k
- Proof of Fullness: €90k
- Operator Pro: €60k
- Cameras: €60k

**Phase 0 budget:**

| Item | Cost |
|---|---|
| Software, 15 person-months | €150k |
| Kerava rig | €15–30k |
| 10 T2 reference machines | €34–63k |
| Sensor kits | €4–6k |
| Camera pilot | €5–15k |
| Cloud and LLM | ≈ €3k |
| **Total** | **≈ €211–267k** |

**Funding:** Business Finland circular-economy aid, or the DUT 2026 call (€200–500k per Finnish sub-consortium).

## 7. Partners

- Vincit
- Pilot chains (Tamro and Citycon are candidates)
- One operator that shares tickets
- Tamtron
- A load-cell supplier (Flintec, Zemic or HBM)
- Kiwa and Tukes
- FMI
- AMCS, WasteHero, Ecomond
- WasteVision or Greyparrot
- VTT, LUT or Aalto
- Business Finland, Sitra, Motiva (Materiaalitori)
- Elisa or Telia IoT
- Sweep or Envoria

The HTML version gives each partner's role, what they get and when.

## 8. Communication

| Audience | Message | Channel | Cadence |
|---|---|---|---|
| Board | Weight makes SMART stickier; downside capped by gates | gate deck | per gate |
| SMART Center | Answer cards = monthly review agenda | training, runbook | monthly |
| Sales | Briefs first, approve, send | dashboard + CRM + Monday email | weekly |
| Operators (~20 FI) | You hear findings first; free feed for tickets | council, data agreement | council twice a year; feed daily |
| Customers | Five answers, money first | cards, short email, red alerts | monthly + on alert |
| Chains | Evidence ready for tenders, ESG export | quarterly review | quarterly |
| Tukes, Kiwa | Second opinion, not billing | meeting | before Phase 1 |
| Market | First independent compactor weight in the Nordics | case study, Kerava open day, trade media | launch |

**Operator protocol:** the operator gets the finding first, with 5 working days to explain, before the customer sees "needs a second look". The words "overcharged" and "fraud" are never used.

## 9. Roadmap and gates

| Phase | When | What | Go on only if |
|---|---|---|---|
| Sprint 0 | Nov 2026–Jan 2027 | Answers, Sales briefs, FMI weather, map, quality panel; €0 archive test | Soft sensor ≥ 30 % better than fill only; 5 salespeople use briefs weekly |
| Phase 0 pilot | Q1–Q2 2027 | Kerava rig, 10 T2 + 50 T0 machines, 1 operator feed, 3 cameras | Monthly error ≤ 6 %; one operator shares tickets; customers would pay ≥ €12 |
| Phase 1 Finland launch | H2 2027 | Verified Weight, Operator Pro, reporting pack | ≥ 10 % Insights uptake; no senior operator complaint |
| Phase 2 Poland, Benelux, quality | 2028 | Proof of Fullness, BDO cross-checks, camera tier | ≥ 30 % of pilot sites move to on-call |
| Phase 3 platform | 2029 onwards | Feed at scale, k-anonymous statistics, T3 | Data Act consent in every contract; competition-law review passed |

## 10. Main risks

| Risk | Mitigation |
|---|---|
| Soft sensor worse on real machines (the study conflict) | €0 test first; reference cohort |
| Operator backlash | Operators hear findings first |
| Median customer saves €0 | Free tier |
| LLM error | Rules decide; citations; human approval |
| Weather API outage | FMI with MET Norway fallback |
| Camera privacy | Hopper-only view; keep scores, not images |
| Retrofit machines lack pressure data | Labelled as rough |
| Legal metrology | Never bill on the estimate |
| Data Act and competition law | Consent; volumes only; ≥ 5 customers per published cell |

## 11. Questions for Europress

1. Is ram pressure logged per stroke? Can 10–30 machines' archives be exported with ≥ 20 tickets each?
2. What are the real SMART prices, and how many machines pay?
3. Which operator would share tickets first?
4. What do the scale platform and Scaletipper cost, and how accurate are they?
5. Can a SMART screen show invoices and contracts? Who owns that data under the Data Act?
6. Should the operator scorecard go to customers or to operators first?
7. Which CRM do salespeople use?
8. How many machines are installed per country, especially Poland?

## Sources (web, checked 7 Nov 2026)

**Europress and SMART**
- Vincit, Europress SMART: https://www.vincit.com/our-work/europress
- Vanheede case: https://recyclinginside.com/recycling-technology/instrumentation-and-control/vanheede-a-partner-in-the-circular-economy-in-a-smart-way/

**Connected compactors and fill sensors**
- Bramidan BRA-IN: https://www.bramidan.com/bra-in/
- Orwak Connect: https://global-recycling.info/?p=5200
- Marathon Connected Compactor: https://www.marathonequipment.com/ismart/
- 3rd Eye: https://www.3rdeyecam.com/products/connected-compactor/
- Sensoneo: https://sensoneo.com/?p=10966
- Nordsense: https://nordsense.com/?p=9697
- Enevo: https://recyclingproductnews.com/article/18538/subscription-based-container-monitoring
- Compology: https://wastetodaymagazine.com/article/compology-miami-metering-commerical-waste-camera
- RoadRunner acquires Compology: https://waste360.com/mergers-and-acquisitions/roadrunner-recycling-acquires-compology

**Operator software and operators**
- WasteHero: https://wastehero.io
- AMCS and Ragn-Sells: https://www.amcsgroup.com/press-releases/ragn-sells-and-amcs-group-partner-to-enable-intelligent-fleet-and-logistics-optimisation/
- L&T and Futurice: https://www.futurice.com/case-studies/lassila-tikanoja-environmental-services
- Stena digital services: https://www.stenarecycling.com/what-we-offer/digital-services/follow-up/

**Weighing**
- Tamtron onboard scale: https://tamtrongroup.com/en/product/one-power-truck-on-board-scale
- Urbaser case: https://tamtrongroup.com/en/customer-cases/case-urbaser-oy-weighing-while-lifting
- Rice Lake TradeRoute: https://www.ricelake.com/traderoute
- Kern 10 t load cell: https://kern-sohn.com/shop/en/products/promotions/last-chance/CD-10-3P1
- Pressure-transducer weighing patent: https://patents.google.com/patent/US5117373

**Quality and vision**
- Greyparrot Sync: https://www.greyparrot.ai/products/sync
- WasteVision: https://wastevision.ai
- Prairie Robotics: https://www.wastedive.com/news/prairie-robotics-tacoma-ai-camera-technology-expansion/757521/

**Data sources and maps**
- FMI open data licence: https://en.ilmatieteenlaitos.fi/open-data-licence
- Open-Meteo terms: https://open-meteo.com/en/terms
- MET Norway terms: https://api.met.no/doc/TermsOfService
- MML vector tiles: https://maanmittauslaitos.fi/en/node/13251
- Digitransit API registration: https://digitransit.fi/en/developers/api-registration/
- MapLibre GL JS: https://github.com/maplibre/maplibre-gl-js
- deck.gl: https://github.com/visgl/deck.gl

**Regulation and reporting**
- CSRD Omnibus: https://www.akd.eu/insights/provisional-agreement-on-omnibus-i-changes-to-the-scope-and-reporting-obligations-under-the-csrd
- Simplified ESRS (EY): https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/technical/csrd-technical-resources/documents/ey-gl-eu-sustainability-developments-v2-07-2026.pdf
- EU JRC truck fuel use: https://greenbestpractice.jrc.ec.europa.eu/print/pdf/node/37
- Finnish landfill tax: https://vero.fi/yritykset-ja-yhteisot/verot-ja-maksut/valmisteverotus/jatevero/
- SIIRTO waste transfer documents: https://www.ymparisto.fi/sites/default/files/documents/SIIRTO%20koulutus%20valvojille%2015032024.pdf
- Wider disclosure of waste data (Borenius): https://www.borenius.com/insights/2026/08/28/working-group-proposes-wider-disclosure-of-waste-data/
- Kiwa verification: https://www.kiwa.com/fi/fi/palvelutyyppi/kalibrointi-ja-varmennus/mittauslaitteiden-varmennus/
- WELMEC Finland: https://www.welmec.org/welmec/documents/Country_Information/Finland.pdf
- R51 vs R76 (IMEKO): https://www.imeko.info/publications/wc-2000/IMEKO-WC-2000-TC3-P102.pdf

**Funding and partners**
- Business Finland circular-economy aid: https://businessfinland.fi/en/for-finnish-customers/services/funding/investment-aid-for-circular-economy
- Business Finland DUT 2026 call: https://www.businessfinland.fi/en/services/funding/calls/2026/dut-funding-call-2026/
- Materiaalitori (Solita): https://solita.fi/asiakkaat/materiaalitori-palvelu-vauhdittaa-kiertotaloutta
- Elisa IoT: https://yrityksille.elisa.fi/en/iot
- Sweep: https://www.sweep.net/platform

**Not verified:** Europress Scaletipper specs, Pellenc ST, incineration gate fees, current FMI rate limits, Kiwa certification cost.

**Weather data:** ERA5 via the Open-Meteo archive API, used for the mockups only, because the free tier is non-commercial.
