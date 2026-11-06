# Red-team judge: Tommi Häkkinen + Since AI jury lens

Author: red-team-judge agent, 2026-11-06. Length exceeds the ~2,000-word guideline because the assignment has seven parts; read section 0 first.

**Tags.** [fact/sourced] = from the dataset docs, the shared brief or a cited page. [estimate] = my judgement. [assumption] = needs a team or Tommi answer. [data] = computed by me on `data/competition/public` (synthetic, so it is not real-world evidence). The numbers marked [data] reproduce with these filters: COMPLETED lifts, single-load ticket, `allocated_net_kg` > 100, no `driver_reported_side_waste`, `device_estimated_collected_kg` not null. Relative gap = (device - ticket) / ticket. That leaves n = 9,174.
Criteria shorthand: K1 weighing concept 25 · K2 customer/business value 25 · K3 data-driven value and traceable analysis 20 · K4 demo and SMART integration 15 · K5 productisation 10 · K6 clarity, uncertainty and limits 5.

---

## 0. Blunt verdict

1. The old RESEARCH.md plan would score about **39/100** against the real criteria. Its centre of gravity (smarter pickups, a "€ in your containers" dashboard, self-made simulator data, a faked assistant) is either SMART's job already, or it ignores the pain Tommi named: the operator holds the weight and customers distrust invoices.
2. **Part 1 needs a real concept, not a slogan.** "Virtual scale from pressure" is the right zero-BOM direction (Tommi: "cheapest wins"). The dataset has no pressure data, so we cannot validate it here. The plan must therefore be an error budget, a tiered fallback, a calibration scheme and a validation experiment. All of these can be demonstrated on the dataset, but none of them is a measured accuracy.
3. **The most important thing I found in the data** [data]:
   - **Tickets are not ground truth.** 44% of all tickets (6,019 of 13,569) use a *stored* tare. Against a *weighed*-tare ticket, the device is within ±3.33% in 68% of loads (median |gap| 2.1%). Against a stored-tare ticket the figures are 43% (median |gap| 4.3%).
   - **The bias is per vehicle.** Median device-vs-ticket gaps for stored-tare vehicles run from -21% (OP-E-V06, n=115) to +23% (OP-A-V12, n=41). That is a weighbridge hygiene effect, not a device effect, and a fleet model can separate the two.
   - **±10% accuracy cannot verify invoices per lift.** Using `examples/weighing_accuracy_value.py`: at σ=10% (Tommi's ballpark) a +10% tonnage overbilling is caught on only 16% of loads. At σ=5% it is 47%, at σ=3% 86%, at σ=1.5% 95%. €/t reporting is fine at σ=10% (median error 6.7%, p95 20.8%).
   - **Self-calibration will not show an "accuracy improves each pickup" curve.** A rolling per-device median correction from tickets leaves the median |error| unchanged (2.8% to 2.8% on all tickets, 2.3% to 2.2% on weighed-tare tickets) and is slightly worse on the 19 drift/calibration-fault devices (3.1% to 3.8%). Its real value is drift detection.
   - **Weight-based billing disputes are small money.** `WEIGHT_BASIS_MISMATCH` is 77 lines worth €729. `DISPUTE_INVOICE` positives sum to €2.6k and `REQUEST_WEIGHBRIDGE_DATA` to €0.6k, on €2.79M annualised contract cost across the 207 dev contracts. `TENDER_OR_SWITCH` (€177k) and `RENEGOTIATE` (€115k) are about 99% of positive action value, and they come mostly from tariff gaps. Weight enables €/t normalisation, not the euros themselves.
4. **Do not lead with tendering or "operators are wrong".** Tommi is protective of operator relationships. Lead with "independent, neutral, fixable", and use the vehicle-tare finding as the neutral-attribution showpiece.

---

## 1. RESEARCH.md scored against the official criteria

| Criterion | Max | Score | Why |
|---|---|---|---|
| K1 Weighing concept | 25 | **11** | Right direction (no new BOM, physics baseline + GBM + quantiles). It is a sketch. There is no error budget, no BOM or cost, no install or calibration plan, no option comparison (load cells, strain, hydraulic), no validation experiment. It says "no public evidence SMART exposes pressure", but Tommi said back-pressure per stroke (0-200 bar) is exactly what SMART uses for fill. Biowaste and cardboard springback are not handled. |
| K2 Customer/business value | 25 | **8** | The value story is smart pickups, "€ in your containers" and CO₂ flights. Pickups are SMART's domain. The real pain (operator holds the weight, invoice distrust, data ownership) is absent. Only cardboard and plastics earn a credit, so "value in containers" is negative for paper, mixed and bio. |
| K3 Data/analysis | 20 | **7** | It builds its own simulator and ignores the provided 447-device, 18k-lift dataset and Tasks A-E. The 55% to 90% truck-fill KPI comes from our own assumptions, so it is circular. No row-level traceability. |
| K4 Demo + SMART path | 15 | **8** | Good craft (live replay, Next.js/FastAPI) but on self-made data. The assistant is faked on purpose ("stream word by word so it feels like an LLM"). There is no SMART integration pathway (API, payloads, tier mapping). |
| K5 Productisation | 10 | **3** | Basic/Pro/Enterprise is not mapped to SMART Intro/Insights/Integrated. €49/month and the €588k ARR are invented. It ignores the lease and service-contract model that is Europress's real profit. |
| K6 Clarity/uncertainty | 5 | **2** | Quantile intervals are a good idea. But the hero tile "± 4% accuracy" and "within 6% of plant scale" are unvalidated claims. |
| **Total** | 100 | **~39** | |

### What is now wrong, outdated or risky

| # | Item in RESEARCH.md | Problem | Fix |
|---|---|---|---|
| 1 | §3.4 smart pickups as a core | SMART already does fullness-based pickup (60-70% of FI pickups are automatic at ~80% fill). | Cut. Mention only as context. |
| 2 | "No evidence SMART exposes pressure" | Contradicted by Tommi's own description. | State that the pressure series exists. Ask about sampling rate and retention. |
| 3 | Virtual scale "validated" by MAPE | The dataset has no pressure curves. `press_load_index` is derived from the device's own biased fill estimate [fact/sourced: A&L §B.8]. Training on it learns the simulator. | Present Part 1 as design plus a physics simulation, labelled *simulated*, plus a validation protocol. Never quote an accuracy as "validated". |
| 4 | Own simulator for ~60 devices | The provided data already has 447 devices, 13.6k tickets, contracts and invoices, and is scored on Tasks A-E. | Use the provided dataset as primary evidence. Use our own physics sim only for the Part 1 experiment. |
| 5 | Hero "€12,480 of recyclables" | Prices are hypothetical, and Europress is not a party. Credit equals index share × grade factor (A 1.0, B 0.85, C 0.6). Three of six streams earn nothing. | Show net contribution and €/t with evidence tags, not "recyclables value". |
| 6 | €180/haul, €49/compactor/month, OCC €120/t, 20-40% savings | Invented or US vendor claims. Task D asks for prices *derived from customer value in the data* with sensitivity. | Derive fee bands from data-measured value per device. Label every price [assumption] or hypothetical. |
| 7 | CO₂ factors and "≈ 9 flights HEL-NYC" | The range is 0.3-3.1 t/t for cardboard. Avoided CO₂ from recycling is not caused by a weighing service. The flight equivalence is a gimmick judges will attack. | Drop it from the hero. If kept, use one cited source, show a range, and attribute only the service-caused part. |
| 8 | Name "TrueLoad" | A live "TrueLoad" truck-axle overload product exists [fact/sourced: VEI catalogue via web search]. An old US TRUELOAD weighing mark was cancelled in 1992 [fact/sourced: Justia]. I did not check EU or FI registries. Europress must be able to own the result. | Use a neutral working title ("SMART weight service, working title"). No logo or brand claims. |
| 9 | Real brand names in the demo (Kesko, Prisma, K-Market) | Real retail chains in a synthetic demo are misleading, and some are Europress customers or competitors of customers. | Use the dataset's fictional customers and operators (Hauler Alpha-Epsilon). |
| 10 | Assistant faked with regex | Tommi asked for *creative AI use* and the brief asks for AI vs rules comparison. Disguising regex as an LLM is a credibility bomb. | Either a real grounded LLM with cached outputs, or an honestly labelled rule router. |
| 11 | "Self-calibration: gets more accurate every pickup" | Not supported in the data (section 0). | Reframe as drift and calibration-fault detection, plus per-vehicle tare diagnostics. |
| 12 | "Hardware-free, no scale needed" only | The brief asks to compare options. At ±10% the product cannot verify invoices. | Add tiers and a fallback BOM (concept C2). |
| 13 | Operator absent | The dataset and the Europress review stress neutral tone and cause separation (rubric row). | Add cause attribution (C4) and neutral wording. |

---

## 2. Fourteen divergent concepts

Feasibility refers to what we can *demonstrate in 48 h on this dataset*. Orig = originality 1-5.

### Part 1: get the weight

| ID | Pitch | Why Tommi cares | Scores | 48 h feasibility | Orig | Risk |
|---|---|---|---|---|---|---|
| **C1** Hydraulic-signature virtual scale | Weigh with signals already logged: per-stroke peak/impulse of ram pressure, cycles, fill, oil temp → kg. Zero BOM. | "Nearly free". Uses data Europress already has. | K1, K6 | **Low-Med.** No pressure in the dataset. Deliver a physics model, a synthetic stroke simulator (labelled simulated) and a validation protocol. | 2 | **High.** Cannot show accuracy. Springback and wet or liquid loads hurt. Patents on pressure-to-fullness exist (cited in RESEARCH.md, not re-verified). |
| **C2** Tiered accuracy ladder | T0 pressure-virtual (±10-12%, €0 BOM) → T1 ticket-calibrated → T2 strain or load-cell kit only for the ~15% of customers who need verification-grade. Mapped to SMART Intro/Insights/Integrated. | The 80/20 "big fries" logic and "cheapest wins" are respected by default, with an upgrade path. | K1, K5, K2 | **High.** A cost-and-accuracy table, and `weighing_accuracy_value.py` shows what each use case needs (section 0). | 3 | Med. T2 BOM must come from the hardware lens. Do not let T2 dominate the pitch. |
| **C3** "Every ticket is a calibration" | Quality-gated tickets (weighed tare, single load, no side waste) become free labels for per-device calibration and drift alarms. No technician visit. | Cuts calibration visits. Uses the operator's data and makes the case for data sharing. | K1, K3, K6 | **High.** 9,174 clean pairs on 335 devices (~27 per device). Be honest: the normal-state gain is nil, the value is drift detection (19 labelled devices, small n). | 4 | Med-High. Tickets exist for only 73% of completed lifts (OP-D 0%, OP-C 51%). 44% use stored tare. Risk of learning the tare error. |
| **C4** Fleet peer calibration with cause attribution | Model each device-vs-ticket gap as device bias + vehicle-tare bias + material effect, pooled across the fleet, so we can say *whose* error it is before anyone is blamed. | Operator relationships, the neutrality rubric, and a creative "crowd calibration" angle. | K1, K3, K6 (+neutrality) | **High.** A two-way mixed model on ~9k pairs. The vehicle-level stored-tare bias (±20%) is strong in the data. | **5** | Med. The vehicle effect may be a simulator artefact, so call it a hypothesis to confirm on real data. |
| **C5** Density-signature alerts (contamination, moisture) | Mass-per-fill vs the stream's expected band (and, in production, pressure-curve shape) → "wrong material" and "wet cardboard +100 kg" alerts with weather context. | Tommi's stated second problem and his rain example. | K2, K3 | **Med.** Labels exist (`MOISTURE_HEAVY_LOAD` 69, `CONTAMINATION_INCIDENT` 118). Only a density proxy is testable, and pressure-curve shape is a hypothesis. | 3-4 | Med-High. Low precision, grades are operator-only. Claiming curve-shape detection would be untestable over-claiming. |

### Part 2: create value from the weight

| ID | Pitch | Why Tommi cares | Scores | 48 h feasibility | Orig | Risk |
|---|---|---|---|---|---|---|
| **C6** Lift-level second opinion = invoice assurance | Each lift shows device kg vs ticket kg vs invoice kg with an uncertainty band. Breaches become human-approved dispute or data-request drafts. Sold to the customer's finance team. | The core pain: customers distrust invoices. A natural Insights feature. | K2, K3, K4 | **High.** Tasks A, B, E, baselines B1/B2. | 2 | Med. The € are small (section 0), so it is a wedge, not a revenue engine. At ±10% it detects only 16% of +10% overbilling, so verify at contract or monthly level, where random error averages out (about σ/√n, not systematic bias) [estimate]. |
| **C7** Operator-neutral benchmark index | Scorecard plus fleet index (on-time, missed, data sharing, billing accuracy, weight bias) with cause attribution. Shown to the operator first as "verified service level". | Operator relations. Operators do not share data and earn per transport. | K2, K3 | **High.** B2 labels (135 rows). The baseline B5 scores 67.75. | 3 | Med. It can read as a "gotcha". Tone, order of disclosure and neutrality are everything. |
| **C8** Contract/tender copilot | Weight gives €/t, benchmarked to peer-median terms. It proposes RENEGOTIATE or TENDER with an expected-value range and approval. | The biggest euro lever in the data. | K2, K3 | **High.** C2 baseline B6 already captures 0.77 of value. | 2-3 | **High narrative.** It looks like pushing customers away from operators. Value comes mostly from tariffs, not weight. Use it as one action, not a headline. |
| **C9** Signed audit trail and "lift passport" | The device signs each reading. Each lift becomes a hash-chained record (device mass before/after, ticket, grade, invoice lines, contract version), exportable as an ESG, EPR or insurance evidence pack. | "Who owns the data". Tamper-evidence answers distrust. Relevant to EPR reporting. | K2, K3, K5 | **Med-High.** Hash chain plus Ed25519 signing in a day. Real key management is out of scope. | 4 | Med. Tamper-evident is not legal-for-trade or certified. The ESG euro value is unquantified. Never claim an insurer would accept it. |
| **C10** Weight handshake and data cooperative | Give-to-get. Operators that share tickets via API get auto-reconciled invoices and fewer disputes. Europress is the neutral custodian. An anonymised cross-customer €/t index (k ≥ 5) can be licensed. | His "holy grail" (data ownership) and "resell data to others". | K2, K5 | **Med.** Simulate verification value vs ticket-sharing rate (sharing ranges 0-91% by operator in the scorecard). A k-anonymity demo. | 4 | **High.** Needs operator consent. Competition-law risk of exchanging price information. Contract confidentiality. Speculative. |
| **C11** Weight-included leasing | A per-tonne-compacted component (or a fair-use band) in the ~6-year lease and service contract. Europress earns on throughput without touching transport. | It fits his existing model and the subscription goal. | K5, K2 | **Med.** Tonnes per device are in the data. Revenue-vs-fixed calculator with sensitivity. | 4 | **High.** Price-sensitive customers. Billing on device weight needs ~±3% trust, and disputes shift to Europress. Legal metrology applies [fact/sourced: NAWI under Directive 2014/31/EU, via web search, not read in full]. |
| **C12** Tonne-based full service | One €/t price for the whole service, with Europress in the middle and a margin on spend. | Listed in `commercial_assumptions.yaml` by Since AI. | K5, K2 | **Med.** The calculator exists. | 3 | **High.** Tommi said Europress will not operate trucks or enter waste. Only acceptable as asset-light brokerage. |
| **C13** Materials marketplace / second life | Verified-weight, grade-tagged cardboard and plastic lots (and 100-500 kg bales from balers) sold at a credit uplift. | Recycling mission, balers. | K2, K5 | **Med-Low.** The uplift €/t is a pure parameter, and grades are operator-only. | 3 | **High.** It is waste trading, and the uplift is hypothetical. Use it as a future-hypothesis slide only. |
| **C14** LLM audit analyst + AI-vs-rules bake-off | A deterministic engine decides. Claude drafts evidence-cited dispute letters, data requests and site-coaching notes. Every proposal carries rationale, uncertainty and a reversal path. It is scored against the rules baseline. | "Creative AI use in the work itself", explainability, human approval. | K3, K4, K6 | **Med-High.** Needs an API key, with cached outputs as fallback. | 4 | Med. Hallucination (so ground every sentence in a row ID). Token cost vs "cheapest wins". In the baseline, GBM lost to rules (macro-F1 0.35 vs 0.73, hybrid 0.78 [fact/sourced: BENCHMARK.md]), so be honest about where AI helps. |

---

## 3. Top 3 portfolios

### A. "Verified Weight" (recommended spine)
**C2 + C3 + C4 + C6 + C7, with C8 as one action only, and a light C14.**
- **Defence.** It covers K1 fully (tiered concept, calibration, error budget, validation design). It covers K2 with the pain Tommi named. It gives K3 row-level traceability on the provided dataset. K4 comes naturally because the demo runs on the real dataset schema. K6 is built in, because every output is an interval.
- **Headline insight.** The vehicle-tare finding (C4): "a large share of discrepancies is the weighbridge's stored tare, not the operator's intent and not the sensor."
- **Expected score** ~72-80 [estimate].
- **Cut.** Pickup optimisation, routing, the map, CO₂ hero, the flight equivalence, marketplace, full service, the fake assistant, and any named product brand.
- **Weak spot.** Originality can read as "baseline plus polish". Make C4 and the honest AI-vs-rules numbers the headline.

### B. "Weight in the lease" (business-model bold)
**C1 + C2 + C6 + C11 + C10, with a light C9.**
- **Defence.** It scores high on K5 and on the business-model part of K2. It fits "service provider, subscription" and respects his red lines (no trucks, no waste trading).
- **Cut.** Operator tendering, detailed scorecard, marketplace, full service.
- **Risk.** Weak data support. It needs sharp K3 reasoning on price vs measured value per device, with a sensitivity grid.
- **Expected** ~68-80 [estimate], with high variance.

### C. "Audit-grade evidence + creative AI"
**C2 + C3 + C5 + C6 + C9 + C14.**
- **Defence.** The most original. The signed lift passport answers "who can prove what". The AI analyst answers "creative AI". It avoids operator-comparison politics.
- **Cut.** C7, C8, C10-C13.
- **Risk.** Scope (crypto plus LLM plus alerts) and legal over-reach (legal-for-trade, insurance claims).
- **Expected** ~65-78 [estimate].

**Recommendation.** Build A as the spine. Add one slide from B (a lease-component sensitivity in the business case). Add the signed evidence-pack export from C only if on schedule at H+30. Freeze scope at H+36.

---

## 4. Pre-mortem: ten ways we lose

| # | Failure | How it shows up | Mitigation |
|---|---|---|---|
| 1 | Part 1 is hand-waved (K1, 25 pts) | "Virtual scale" with no error budget, BOM, install, calibration or validation experiment. | A one-page error budget (repeatability, oil temperature, material springback, geometry, fill-estimate error). A fallback BOM (T2). A validation protocol with pilot devices, matched weighbridge tickets, sample size and acceptance criteria. All hypotheses tagged [assumption]. |
| 2 | Over-claiming accuracy | Quoting ±3.3%, "within 6%" or "±4%" as achieved. The ±100 kg on 3 t target is a simulation target, "not a specification of any Europress solution" [fact/sourced]. In the data, only 68.5% of 2.5-3.5 t loads are within ±100 kg of the ticket (n=1,086) [data]. | Never say "validated". Show the distribution and explain that the reference itself is noisy (stored tare, side waste, combined loads). |
| 3 | Ignoring uncertainty, and treating tickets as truth | Point estimates, disputes at 1σ. The model learns the stored-tare error. | Intervals everywhere. Flag only beyond 2 combined σ. Gate calibration to weighed-tare, single-load tickets. Note that `mass_uncertainty_kg` "does not know about drift" [fact/sourced]. |
| 4 | Dishonest numbers | Hypothetical prices shown as savings. Vendor claims (-40% cost, -40% CO₂) quoted as results. Invented prices. | An evidence tag on every figure: observed / estimated / simulated / hypothetical (a rubric row). All prices in one params file. Label vendor figures as vendor-reported averages. |
| 5 | Narrative collision | "Smart pickups" (SMART does that). Or the pitch reads anti-operator. | Lead with verification, neutrality and cause attribution. Show the operator-first disclosure flow. |
| 6 | Cost/BOM sin | Anything above near-zero on the standard machine. Install labour is the hidden cost. | T0 = no BOM. Hardware only in the top tier, with a per-unit and per-visit cost, and a payback calculation vs customer value. |
| 7 | Demo fails | Wi-Fi, SSE, map tiles, LLM API, or a hosted deploy dies on stage. | Local one-command start. A recorded walkthrough as backup (submission allows it). No map tiles (a regional bar chart instead). Cached LLM outputs. Pinned lockfiles. Rehearse three times. |
| 8 | Missing licences/IP | Table incomplete or wrong. AGPL or proprietary dependency slipped in. Dataset and Europress code licence not stated. Patent prior art ignored. | Run `pip-licenses` and `license-checker` at the freeze. Keep the list in section 6. Name the patents we found (US11162834B2 weight-measurement retrofitting for compactors, US11148383B2 for balers, US12379240 load cells; found by title via web search, not read) and state "no freedom-to-operate analysis". |
| 9 | Fake AI | The regex assistant exposed in Q&A. | Real grounded LLM with row-ID citations, or an honestly labelled rule router. Report the AI-vs-rules numbers, including where AI loses. |
| 10 | Scope sprawl and leakage | Fourteen half-built concepts. A demo with no traceable number. Tuning on test or ignoring `as_of`. | Spine A only. One number traced end to end (job ref → ticket → contract version → invoice lines → €/t). Score on validation labels only. Use `open_dataset(..., as_of=...)` for decisions. |

---

## 5. The 15 hardest questions

"Need data" flags where the team or Tommi must supply facts.

| # | Question | Best short answer | Need data |
|---|---|---|---|
| 1 | SMART already optimises fullness. Why is this not just that? | We do not touch pickup timing. We add the weight that SMART lacks and use it to verify and price what the customer buys. | No |
| 2 | How accurate is your weight, honestly? | We have no real pressure curves, so we show an error budget and a validation plan, not a measured accuracy. In the synthetic data, device vs weighed-tare tickets agree within ±3.33% on 68% of loads [data]. ±10-12% is enough for €/t. Verification needs about ±3% per lift. | **Yes**: a sample of per-stroke pressure plus matched tickets |
| 3 | What does it cost per machine? | T0 has no BOM (software only), so the cost is a firmware update and cloud. T2 hardware is a priced option for the few who need it. | **Yes**: hardware BOM, install cost, Tommi's ceiling |
| 4 | Customers will not pay more. Who pays? | Bundled in Insights, funded by customer-measured value. Fee is set as a fraction of value per contract, with a sensitivity grid. Dev best-set value is about €1,064 per contract-year on €13.5k contract cost [data, hypothetical prices]. | **Yes**: Europress cost to serve and ARPU |
| 5 | Operators will hate this. | It is neutral, separates causes (sensor, tare, side waste, combined loads), and goes to the operator first. The vehicle-tare finding shows many differences are fixable hygiene. | **Yes**: do operators buy Europress machines? |
| 6 | Who owns the data? | Customer owns device and contract data. Operator owns tickets and grades. Europress is the neutral custodian under explicit consent. Not legal advice. | **Yes**: Europress T&C |
| 7 | Is this legal for trade? | No. It is verification, not billing. A breach triggers review. Billing on device weight would need legal metrology, and the dataset does not show it is possible [fact/sourced: ECONOMIC_MODEL §2b]. | Yes (metrology expert) |
| 8 | What about wet or biowaste? | Weight error is larger there. In the data, device-vs-ticket within 10% holds for 78% (bio) vs 88% (cardboard) of loads [data]. We widen intervals or move those devices to T2. | No |
| 9 | Drift and faults? | A residual change-point detector, plus the `quality_flag` and fill-vs-mass consistency. Honest n: 15 `SENSOR_DRIFT` and 4 `CALIBRATION_ERROR` labels. | No |
| 10 | What does the human approve, and what if AI is wrong? | A proposal object: action, evidence rows, uncertainty, expected-value range, reversal path. Nothing executes. | No |
| 11 | Why AI at all? Where is the creative part? | Rules beat GBM on the baseline (0.73 vs 0.35 macro-F1), so we use rules for detection. AI drafts the evidence-cited explanations and handles the long tail. We report our own bake-off. | **Yes**: our own bake-off numbers |
| 12 | Business case, payback, Europress margin? | Task D parameter file, sensitivity grid, break-even. Prices are hypotheses. | **Yes**: SMART pricing, lease structure |
| 13 | Where does it plug into SMART? | Telemetry already carries `mass_kg`, `mass_uncertainty_kg`, `quality_flag`. New: a reconciliation event stream and a recommendation endpoint (cf. `examples/recommendation_api_mock.py`). Mapped to Insights. | **Yes**: the real SMART API |
| 14 | What did you not prove? | No real pressure data, no live validation, prices hypothetical, operator behaviour modelled, the vehicle-tare effect may be a simulator artefact, legal metrology, competition law for cross-customer indices. | No |
| 15 | Does it work for Poland and fixed-schedule fleets? | Fixed schedules gain most from weight evidence for unnecessary-lift proof. Ticket formats and EPR reporting differ and are untested. | **Yes**: Poland operations |

---

## 6. Submission checklist

### Mandatory items
| Item | Must contain | Done |
|---|---|---|
| 1. Weighing concept (short, illustrated) | Principle · placement · indicative BOM + cost · installation · calibration · error sources (budget) · validation plan · comparison of load cells, structure/strain, hydraulic and a justified alternative · limitations | [ ] |
| 2. Demo or recorded walkthrough on synthetic data | Runs from one command · code and setup notes · traceable economics (row-level audit) · proposed SMART integration (API, tier mapping) | [ ] |
| 3. Customer value + business case | Use case · measurable customer benefit · Europress commercial model · how to productise inside SMART · prices from the params file, with sensitivity | [ ] |
| 4. Third-party licence table | Library/model/dataset/service, licence, commercial-use restriction (below) | [ ] |
| 5. Assumptions and untested | What remains unproven, plus the evidence tags | [ ] |
| Rubric D/E | Evidence separation · traceability · quantified uncertainty · pricing and adoption reasoning · human approval · no over-claiming · neutral tone | [ ] |

### Third-party list (starter; confirm every version and licence at freeze)
Licences below are from my memory unless marked, so run `pip-licenses` and `license-checker` before submitting.

| Component | Licence | Commercial-use note |
|---|---|---|
| numpy, pandas, scipy, scikit-learn, uvicorn | BSD-3-Clause | OK |
| pyarrow, OR-Tools (if used) | Apache-2.0 | OK |
| duckdb, LightGBM, PyYAML, FastAPI, Pydantic, tabulate | MIT | OK |
| matplotlib | Matplotlib licence (BSD-style) | OK |
| cryptography (if signing used) | Apache-2.0 or BSD | OK |
| Next.js, React, Tailwind, shadcn/ui (copied components), Recharts, react-map-gl, Motion, sonner, @react-pdf/renderer | MIT | OK |
| lucide-react | ISC | OK |
| Tremor | Apache-2.0 (verify) | OK |
| MapLibre GL JS | BSD-3-Clause | Tiles are separate. Avoid tiles. |
| Open Sans, Montserrat, Manrope | SIL OFL 1.1 | OK to embed. State that it is a free lookalike for Loos Wide. |
| **Loos Wide Bold** | Commercial | **Do not embed or ship.** |
| OpenStreetMap tiles (if used) | ODbL + tile-usage policy | Attribution required. Public tile server is not for heavy use. |
| Claude API / any LLM | Provider commercial terms | List it as a service. Send synthetic data only. |
| Hosting (Vercel Hobby etc.) | Plan terms | Hobby is non-commercial. Prefer a local run. |
| **Since AI / Europress dataset v1.0.1** | **No licence file in the package.** README: use "follows the Since AI Hackathon 2026 rules" [fact/sourced] | Confirm commercial use and IP with organisers. |
| `europress_data` package and baselines (if reused) | Not stated | Same: confirm before reusing code. |
| Avoid | AGPL (PyMuPDF), Mapbox GL JS ≥2, Highcharts, anything GPL | Copyleft or commercial. |

### Other checks
- [ ] `pip install tabulate` (the dataset example script imports it, and it is missing in the shared venv).
- [ ] No Europress logo, brand claims or proprietary fonts. No real company names in the demo.
- [ ] Every price sits in one params file and is labelled hypothetical.
- [ ] Patent note: "found by title only, no freedom-to-operate analysis".
- [ ] A single end-to-end traced example in the deck.

---

## 7. Questions for Tommi (ranked, max 10)

| # | Question | Why it matters |
|---|---|---|
| 1 | What is the maximum extra BOM per machine, and the maximum price per device per month, you believe customers accept? Is a one-off technician visit for calibration acceptable? | Defines "cheapest wins" quantitatively and decides T0 vs T2. |
| 2 | What exactly leaves the compactor via SMART: the per-stroke pressure curve (sampling rate), stroke count, ram position, oil temperature? Is it retained long-term? | Decides whether C1 is feasible and what we can ask for in a validation experiment. |
| 3 | What accuracy do you need per use case: €/t reporting, invoice-verification trigger, billing? Is verification of operator tonnage in scope at all? | At ±10% we detect only 16% of +10% overbilling. This decides tiers. |
| 4 | Do operators buy or lease Europress machines? Would you show an operator scorecard to customers, or only to operators first? What would make operators share tickets? | Channel conflict and the C7/C10 design. |
| 5 | Can anonymised cross-customer benchmarks be sold, and what do customer contracts allow? | C10 viability. |
| 6 | Weight-linked pricing in leases vs a subscription: acceptable? What do Intro/Insights/Integrated cost today, and what is the SMART integration surface (API, event schema)? | C11 and the K5/K4 pathway. |
| 7 | The brief names Scaletipper X1 and "scale solutions". Is that a weighing product? What did you try before and what stops reuse? | My web search found nothing, so I could not confirm it. Avoid duplicating. |
| 8 | Confirm that the outputs are ownable by Europress, and which licences you accept (MIT/Apache yes, AGPL no?). | Licence table and IP. |
| 9 | Poland: is it a priority, are weighbridge tickets accessible, and is EPR reporting demanded? | C9 and scalability. |
| 10 | Will judging be live or recorded, synthetic data only, and do you want a real LLM in the demo? | Demo plan and the AI choice. |
