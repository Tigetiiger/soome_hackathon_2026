# Business plan — SMART Verified Weight

_Europress × Since AI Hackathon 2026 · draft 1 · 2026-11-06 · merges the six agent reports in `docs/agents/`. Companion: `BUILD_PLAN.md`._

**Tags:** **[data]** computed from the synthetic pack (scripts in `analysis/`) · **[sim]** the dataset's own simulated counterfactual · **[est]** our estimate or extrapolation · **[hyp]** hypothetical price/adoption we chose · **[src]** external source · **[unverified]** could not be confirmed.
**Standing caveat:** all prices, tariffs and savings are hypothetical (Europress is not a party to transport or treatment). Nothing here is a real saving. Operators are fictional and treated neutrally.

---

## 1. The thesis in three sentences

Customers pay per tonne for a weight they cannot see, measured and graded by the party that is paid per tonne. Europress compactors already know how full they are; a calibrated **virtual scale** lets them also know roughly how heavy, at near-zero hardware cost, and a small **premium platform tier** gives hard evidence where it pays. We sell the customer an **independent, explainable second opinion on every lift**, and we let the customer, not Europress, decide what to do with it.

**What we deliberately do not claim:** better pickup timing (SMART already does it), legal-for-trade weighing, moisture or contamination detection from mass (not visible in the data), or that weight alone recovers large sums (see §4).

## 2. Who has the problem

| Party | Pain | What they get from us |
|---|---|---|
| Customer: facility, property or procurement manager (retail chains, industry) | Cannot check EUR/t, tonnage, tariffs or operator behaviour; operator may not share tickets | Independent tonnage + EUR/t, invoice second opinion, evidence pack to dispute or renegotiate |
| Customer: ESG or finance lead | Material flows and credits are opaque | Auditable monthly tonnes per stream with uncertainty |
| Europress | Sells machines and leases; SMART reaches only ~15% of customers (Tommi's notes); wants to be a service provider and to be "earlier in the value chain" | A weight-based service tier, lease differentiation, a data asset that operators cannot hold alone |
| Operators (not our customer) | Weight and grade data are their leverage | Neutral treatment, a "weight handshake" that rewards sharing tickets, no accusations |

**Segments** (Tommi's 80/20 note, data from the strategist's model [data/hyp]): large chains and property groups (16+ devices) want features and ESG data → Integrated; industrial/food customers with credit-eligible cardboard and plastic want material-value transparency → Insights; small sites mostly want to save money → Intro with a free ballpark weight and outcome pricing. Value is concentrated: the top 5 of 52 synthetic customers hold 54% of realisable value [data].

## 3. The product: a weighing ladder you pay for by accuracy needed

| Tier | How the weight is obtained | Expected error, 1σ per lift | Extra hardware | Good enough for (from our σ-sweep) |
|---|---|---|---|---|
| **T0 Ballpark** (free in Intro) | fill × volume × density table, no anchors | ~16% median abs. on the synthetic fill-only baseline [data] | none | indication, monthly totals, trends |
| **T1 Anchor-calibrated virtual scale** (Insights) | ram pressure curve + fill + stroke count in a physics model; per-machine gain set by clean weighbridge tickets, Student-t update, CUSUM drift guard | 9.4% median with 3 anchors using fill only [data]; **6.6% (weighing agent, untested)** vs **12–15% (literature view)** with pressure features [est] | none (optional oil-temperature probe €10–25 [est]) | €/t reporting, C2 operator actions (capture stays ≥74% even at σ=10% [data/sim]), fill-vs-mass order guard |
| **T2 Platform** (Integrated / critical sites; "golden cohort") | 4-corner load-cell platform; Europress already lists a "Scale platform" and the Scaletipper X1 [src] | ~1.4% [est] | BOM ~€1.0–1.9k (4× Kern 5 t C3 cell €124 + junction box €220 sourced; rest estimated) | ticket reconciliation, stored-tare detection, small tonnage deviations; labels that train the whole fleet |

**Why this is the right answer to "cheapest wins":** the base tier costs nothing in hardware; the expensive tier is used on 2–5% of machines to teach the rest. Precedent: a sensor-fusion model of bale weight estimated bale weight on balers without built-in scales at 4.96% mean relative error with no extra hardware (Mansouri et al., GIL 2025, DOI 10.18420/giljt2025_35 [src, abstract checked]; the "25,000 bales / 25 machines" detail is from the full text per our research agent [unverified]). It is hay and silage baling, so it is an analogue, not proof for waste compactors.

**Honest accuracy position.** Our range is 6.6–15% per lift at T1, about 5–6% on device-month totals [est]. That meets Tommi's "ballpark, ±10–12%" for totals and the typical lift, not ±3.3% on every lift. We say so on the first slide that shows accuracy. The literature search found **no peer-reviewed mass-from-ram-pressure study for waste compactors**, which is both our risk and our opening for novelty.

## 4. What the data shows (and does not)

All from the competition pack: 447 devices (404 with simulated weight), 52 customers, 5 fictional operators, 18,477 lifts; labels cover 304 days so euro figures are 10-month sums [data].

**Findings that hold up**
1. **Weight is mostly the denominator.** Mass-linked charges are 46% of correct charges (€2.50M of €5.44M), yet billing errors that *need* independent mass total only ~€8k in 10 months (~€21 per device-year) [data]. Do not headline overbilling recovery.
2. **Operator and contract actions (Task C2) need a mass, not an accurate one.** Value captured by the best action set: 50% with no mass → 55% invoice tonnage only → 73% device weight alone → 77% all sources; a device at σ=10% still captures 74.3% [data/sim]. Weight uplift is **+€190 per contract-year where tickets are not shared, +€56 where they are** [data].
3. **26% of lifts have no verifiable mass today** (operator D shares nothing; operator C ~53%) and 11.1% of collection spend (€349k) has no EUR/t; the device estimate covers 95.5% of those lifts [data].
4. **Fill-vs-mass order guard (S40, fill sensor falsely high):** 96% precision at 51% recall against 5% precision for a fill-only rule; pool ~€161 per weighted device-year [data]. This is the one case where weight beats fill outright. S40's frequency is a synthetic assumption.
5. **The headline trust finding:** a large share of device-vs-weighbridge disagreement is *not* the operator and not the sensor: 34% of gaps >10% are side waste on the same truck, 30% stale stored tare at the weighbridge (10 of 70 vehicles cause 79% of tare errors), 12% combined loads, only ~4% device drift [data]. A naive device-vs-ticket "operator bias" score wrongly flags 74% of operator-region-months; cause adjustment cuts error from 5.5 to 1.2–1.6 percentage points [data]. This is why our scorecard can be neutral and still useful.
6. **Operator-level tender/renegotiate value dominates C2:** best action set = €220k over 207 contracts (7.9% of cost; ≈ €465k/yr extrapolated to 437 contracts [est]), 99% of it from tender and renegotiate, which are mostly tariff gaps that weight only *enables* [data].

**Negative findings we state openly**
- Moisture, contamination and mis-sorting are not detectable from mass vs fill (AUC 0.5–0.7). We do not sell them in v1 [data].
- Over-servicing and precautionary orders gain nothing from weight (S01, S39) and belong to SMART [data].
- ±3.3% is unusable as a per-lift reconciliation tolerance: 53% of paired lifts exceed it, and the weighbridge itself is within ±100 kg on only 78% of clean 3 t lifts. We propose |diff| > 100 kg **and** > 10% [data].
- Isolation forest is useless here (F1 0.10); simple rules reach F1 0.89 and gradient boosting 0.93, so **rules flag and explain, ML ranks later, a human approves** [data].
- Per-device self-calibration from tickets does not improve median error on this data; its real value is drift detection. We do not claim "gets more accurate every pickup" [data].

## 5. Customer value and price

**Weight-attributable value ceiling: ~€120–270 per weighted device-year** (order guard €67–82 + operator-action uplift €56–190) [est], up to ~€530 if the simulated mass-target pickup option is counted (SMART's own domain, so we exclude it) [sim]. A typical 8.6-device customer: about €1,000–2,300 per year [est].

The business strategist's €576 per device-year counts every lever (operator performance, contract review, over-servicing...) and most of those need invoices and contracts rather than weight; its own low case (€242) is the weight-attributable reading. We use the data analyst's range as the price ceiling.

### Offer (all prices [hyp])
| Offer | Price | Logic |
|---|---|---|
| Intro: ballpark weight (T0) | free | hook, builds the anchor dataset |
| **Insights + Verified Weight (T1)** | **€8 / device-month** (low €5, high €12) | €96/yr against €120–270 value = 1.25–2.8× multiple; deliberately below the €20/month ceiling the analyst warns about |
| Integrated: chain licence | €20k / year base (strategist, **[hyp], unvalidated**) + per-device fee | API, ESG export, multi-site benchmark |
| **Operator Review service** (weight as the evidence layer for dispute/renegotiate/tender, human-approved) | 15% of *verified* recovered or avoided cost, capped | ≈ €160 per contract-year at the data's €1,064 per contract-year C2 value [hyp]. Weight is the trust layer, not the whole source of value |
| T2 platform | in the lease: +€14–26 / month over 72 months for BOM €1.0–1.9k [est] | only where value > cost; Europress funds the 2–5% golden cohort (≈ €10–19k per 10 of 500 machines [est]) |

The strategist's lease model is parameterised in `docs/agents/business-strategist_params.yaml` and `business-strategist_model.py`; re-run it with the platform cost above before quoting any payback.

### Europress economics (honest version)
Cost to serve ≈ €4.8 per device-month (operations €2.5 + support €2.3, strategist [hyp]). At €8 the contribution is ~€3.2 per device-month, so a €135k/year team needs **~3,500 paying devices** (at the strategist's €15 it was ~1,100). We therefore do **not** present Verified Weight as a standalone P&L line. The case rests on: (a) a differentiator for machine sales and 6-year leases (retention), (b) attach rate of Insights and Integrated, (c) Operator Review outcome revenue, (d) a data asset (weight handshake) operators cannot hold alone. Three-year revenue scenarios in the strategist's file (base ≈ €267k, low €64k, high €934k at its €15 price and assumed SMART base of 1,500 / 2,400 / 4,000 devices) are **low-confidence and must be re-run at €8**. The SMART paid base is the biggest unknown; ask Tommi.

## 6. Productisation inside SMART

- **Tier mapping:** Intro (free ballpark weight + status) → Insights (T1 add-on, EUR/t, S40 guard, invoice second opinion) → Integrated (chain licence, API, ESG export, optional T2).
- **Integration surface:** the dataset already carries `mass_kg`, `mass_uncertainty_kg`, fill and status per hourly message. We propose (1) an `/estimate` endpoint returning mass ± interval and its provenance (`observed` / `estimated`), (2) an `/evidence-pack` endpoint for a lift (device record + ticket + invoice line + rule that fired), (3) a human-approval queue that writes an action log; all advice-only. See `examples/recommendation_api_mock.py` in the pack for the expected shape.
- **Firmware/data need:** per-stroke pressure trace export (10–30 pilot machines + ≥20 clean tickets each). Without it, stroke-curve features remain an untested hypothesis.
- **Rollout:** Phase 0 desk falsification on archived curves (go/no-go: pressure cuts MAE ≥30% vs fill-only) → Phase 1 six-machine golden rig, ~150 lifts → Phase 2 thirty-machine field test. Pre-registered acceptance criteria are in the weighing agent's §4 (≥80% of ≥1 t lifts within ±10%, monthly-total bias ≤5% for ≥80% of device-months, 80% interval covers 75–85%).
- **Weight handshake:** customers who upload tickets get calibrated weight sooner; operators who share tickets get a better scorecard. This turns the data-ownership fight into a trade.

## 7. Trust, neutrality, legal

- **Language:** "difference", "needs a second look", never "overbilled" or "fraud". Every flag shows the cause attribution (side waste, stale tare, combined load, device drift) and an interval.
- **Not legal-for-trade.** Labelled "indicative, verification-grade". Trade-grade bin weighing is certified only up to 600 kg; an EU legal-for-trade path needs NAWI 2014/31/EU / OIML R76 class III or MID instruments, and only the platform tier could ever qualify [src via agents; national authority, e.g. Tukes, to confirm].
- **Patents:** US11162834 (BACE, retrofit container weighing) and US8794135B1 (active to ~2028 per the research agent) need a freedom-to-operate check before any hardware commitment [claims unread].
- **Data:** the EU Data Act needs a contract basis for Europress to use customer contract and invoice data; the customer hands it over to the service. Open question for Tommi: may a SMART tab show invoice and contract data, and who owns it?
- **Human approval:** nothing is sent or disputed automatically.

## 8. Risks and what remains untested

| Risk | Mitigation |
|---|---|
| No pressure curves in the dataset: Part 1 cannot be validated on it (`press_load_index` correlates 0.985 with fill) | Say so on slide 1 of the weighing section; test only fill-only + anchors; use a labelled synthetic pressure generator solely to unit-test code; deliver a pre-registered validation protocol |
| Accuracy over-claim (6.6% vs 12–15%) | Show both numbers and their sources; claim totals, not every lift |
| Value pool inflated by hypothetical tariffs | Tag every euro; show low/base/high and the sensitivity grid; headline the ladder, not the sum |
| Operator pushback (largest Finnish operator owns trucks and earns per transport) | neutral scorecard, cause attribution, handshake, no accusations |
| Anchors are noisy (44% of tickets use stored tare, ~2× the noise of weighed tare) | filter to SINGLE_LOAD + WEIGHED tare + no side waste; robust update; evaluate against noise-adjusted truth |
| SMART paid base unknown, revenue scales linearly with it | state as assumption; ask Tommi |
| Over-scope in 48 h | scope freeze at H+36 (see build plan); cut list below |

**Cut list (do not build, do not pitch):** pickup optimisation and routing, map/CO₂-flight hero, fake chat assistant, marketplace, tonne-based full service, moisture/contamination detection, any product brand that clashes with an existing one ("TrueLoad" is a live truck-overload product).

## 9. Pitch

**60-second hook.** "Every month a retailer gets an invoice per tonne, weighed on a scale it cannot see, graded by the party paid per tonne. Our compactors already know how full they are; now they know roughly how heavy, with no new hardware, and we tell you exactly how sure we are. In our synthetic test of 52 customers, the biggest finding wasn't blame: a third of weight disagreements are side waste on the truck and another third a stale truck tare at the weighbridge. So we built a neutral second opinion: the machine keeps the receipt, rules explain the difference, and you press approve."

**Three-minute arc:** (1) phantom lift: the device never emptied on 24 Aug but the invoice charged for it (synthetic CTR-00038: 2 phantom lifts, 4 lines, €1,215.20; needs device status, not weight) → (2) 335 kg gap where the tool says "no action, €0" because the contract is per lift and the tare was stored (restraint builds trust) → (3) EUR/t with provenance for the 26% of lifts that had none → (4) the accuracy ladder and the value-vs-σ curve that links Part 1 to Part 2 → (5) business model and SMART integration.

**Scoring map**
| Criterion | Where we earn it |
|---|---|
| 25% weighing concept | §3 ladder, error budget, BOM, validation protocol, falsification gates |
| 25% customer/business value | §4–5, Operator Review, lease component, segment logic |
| 20% data-driven value, traceable | `analysis/` scripts + tags + sensitivity |
| 15% software demo + SMART path | `BUILD_PLAN.md`, §6 |
| 10% productisation | §5–6 tiers, rollout, handshake |
| 5% clarity and limits | §4 negatives, §8 |

## 10. Assumptions register (all [hyp] or [est])
€8/device-month (5–12); €20k chain licence; 15% outcome fee; €4.8 cost to serve; €135k team; SMART paid base 1,500 → 2,400 → 4,000 devices; platform BOM €1.0–1.9k; 72-month lease; golden cohort 2–5% of fleet. Everything else is tagged where used.

## 11. Questions for Tommi (ranked)
1. Does SMART archive the full per-stroke pressure trace, at what rate, and can 10–30 machines plus ≥20 clean tickets each be exported?
2. Price, accuracy and retrofit effort of the existing Scale platform; maximum extra BOM and monthly price customers accept; is a technician visit for calibration acceptable?
3. How many devices are on paid SMART tiers, at what price and churn?
4. Is |diff| > 100 kg and > 10% an acceptable lift tolerance to operators, and may a SMART tab show customer invoice and contract data?
5. Would you show an operator scorecard to customers, or to operators first? What would make operators share tickets?
6. Licences you accept (MIT/Apache yes, AGPL no?) and confirmation that outputs are ownable by Europress.
7. Live or recorded judging; is a real LLM in the demo wanted?