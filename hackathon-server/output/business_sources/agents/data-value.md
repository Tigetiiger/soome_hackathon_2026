# Data-value analyst: traceable € per use case

Author: data-value agent, 2026-11-06. Dataset: `data/competition/public`, label window 2025-10-01 to 2026-08-01 (304 days, annualised ×365/304). **365.4 active device-years.** In this dataset each device has exactly one contract, so per device-year equals per contract-year.

**Tags.** [data] = computed here on synthetic data. Every € uses the dataset's **hypothetical** customer–operator tariffs. They show relative size only and are not savings. [fact/sourced] = dataset docs. [assumption] = our choice. [estimate] = judgement.

**Scripts** (rerun with the shared venv): `/home/hackathon/europress_conclusions/analysis/10_…61_*.py`. Outputs go to `analysis/outputs/`. I reused `soome_hackathon_2026/analysis/common.py` and `01_pairs_eur.parquet`, and changed neither.

---

## 0. Summary table

| # | Use case | € per device-year (mean / p50 / p90 across devices) | What weight adds, specifically | Evidence | Proving rows / file |
|---|---|---|---|---|---|
| 1a | Invoice assurance, all billing errors (overcharge) | **€150 / €12 / €449**. 55% of devices have at least one. | Only **3%** (WEIGHT_BASIS_MISMATCH, €4.6/dy). The rest is contract logic, not weight. | [data] | `anomaly_labels` billing families → `10a_*.csv` |
| 1b | Mass-dependent billing that only device weight can verify | €9,050/dy of billing depends on mass. Tickets cover 77% of it. **Device weight adds 19% (€1,730/dy)** | Verification coverage rises from 77% to 96% of mass-billed € | [data] exposure, not saving | `10c_mass_billing_evidence.csv` |
| 2 | Unnecessary lifts, **FIXED + HYBRID** ("Poland") | **€2,597 / €759 / €6,333**, with 18–20 avoidable lifts per dy. 30–32% of their lifts are unjustified. | Fill alone already catches about 92% of the €. Weight adds +3 pp, plus the **tonnage proof** needed to change a schedule. Task C: €317 of €2,779/yr is weight-only. | [data] + simulated counterfactual | `20a_*`, `20b_*`, `20c_*` |
| 2' | Same for ON_CALL (Finland) | €434 / €176 / €1,124 | Raises € recall from 68% to **97%** (false-high fill sensor S40 plus precautionary orders S39), about **+€120/dy** | [data] | `20b_detection_by_policy.csv` |
| 3 | €/t benchmark → renegotiate or tender | Best action set **€1,064 per contract-year** (n=207 dev, mean). Ceiling: €1,675/contract-yr above peer median. | **28%** of positive renegotiate/tender value sits on contracts where **device weight is the only mass**. A further 8% relies on operator-reported invoice tonnage alone. | [data] + C2 valuation rules | `30a_*`, `30b_*` |
| 4 | Quality: contamination and moisture | €655/dy at stake in grade loss (€1,283 per credit-stream dy) | **Not demonstrable.** The density proxy has precision of about 1%. | [data], negative | `40_density_pr.csv` |
| 5 | Drift and calibration faults | 0.05 episodes/dy, median 78 days unnoticed | Ticket-based alarm fires about 47 days into the episode, 33 days before today's fix. € value is [assumption]. | [data] | `50_*` |

**Headline [estimate].** For a typical FIXED or HYBRID device, the defensible stack is about €0.8–2.6k/yr of avoidable lifts (p50–mean), plus about €0.15k/yr of billing corrections, plus about €1k/yr of contract actions in hypothetical €. Weight is **strictly required** for roughly €0.3–0.6k of that. The rest needs fill, contracts and invoices, which SMART plus customer documents already provide. **The pitch is "weight makes it provable", not "weight makes the euros".**

---

## 1. Invoice assurance (UC1)

**1a. € at stake** [data]. Over 10 months, billing labels contain €45.6k of overcharges and €28.2k of undercharges. The undercharges are reported neutrally because they are the operator's risk. By family (€/dy): duplicate lines 60.3, unmatched (phantom) lines 44.6, missing credit lines 30.1, wrong surcharge 8.9, **weight-basis mismatch 4.6**, uninvoiced 1.4, outdated tariff 0.0.

Segments (€/dy): FIXED 117, HYBRID 198, ON_CALL 149; cardboard 204, bio 209, mixed 127; shopping centre 371, grocery 154. Full split by operator and sector in `10a_overcharge_by_segment.csv`. Operator differences reflect contract mix and volume, so they are not a ranking.

**1b. Cause attribution for device-vs-ticket gaps above 10%** [data, n=2,250 of 9,062 pairs]:

| Cause | Share |
|---|---|
| Side waste on the same truck | 34.3% |
| Stale stored tare at the weighbridge | 30.4% |
| Combined-load 50/50 allocation | 12.0% |
| Unlabelled | 13.5% |
| Small-load noise | 6.0% |
| **Device fault, drift or calibration** | **3.9%** |

**77% of large gaps come from weighbridge-side hygiene** (tare, allocation, side waste), not from the sensor and not from intent. The pattern holds per operator (`10b_gap_cause_by_operator.csv`). OP-D shares no tickets, so it has no pairs.

**1c. Detection power: per lift vs aggregated.** The aggregate is the median of per-lift ticket/device ratios. It uses only observable filters: single load, weighed tare, more than 500 kg, no driver-reported side waste. The alarm threshold gives 2.5% false alarms [data]:

| Level | Robust σ | Detects +5% inflation | Detects +10% inflation |
|---|---|---|---|
| Per lift | 2.8% | 10% | 53% |
| Device-month (median 1 clean pair) | 2.3% | 18% | 87% |
| Device-quarter (3 pairs) | 1.7% | 54% | 97% |
| Device over 10 months (9 pairs) | 1.1% | **96%** | 99% |

Sums instead of medians fail (sd 36%) because side-waste and tare outliers dominate. **Use robust statistics, and verify at contract level, not per lift.**

Parametric sweep (`10d_detection_sigma_sweep.csv`, real lift counts): at **σ=10% (Tommi's ballpark)** +10% overbilling is caught 17% per lift, 29% per month, 62% per quarter; at σ=5%, 97% per quarter. **So the ±10% tier is enough for quarterly tonnage assurance only against inflation of 10% or more. The 5% tier is enough at the quarter.**

---

## 2. Unnecessary lifts on FIXED / HYBRID (UC2, Poland pitch)

[data] (`20a`):

| Policy | Device-yrs | Lifts unjustified | €/dy (mean) | Lifts avoidable/dy |
|---|---|---|---|---|
| FIXED_SCHEDULE | 43.8 | **31.7%** | **€2,540** | 17.7 |
| HYBRID | 34.9 | **29.7%** | **€2,698** | 19.6 |
| ON_CALL | 286.8 | 6.5% | €434 | 2.7 |

- On FIXED/HYBRID, all of this is OVER_SERVICING (S01). On ON_CALL it splits into fill-sensor false highs (S40, €53k) and precautionary orders (S39, €50k).
- Skewed: biowaste €1,640/dy and shopping centres €1,749/dy are highest.
- **Honest split** (`20b`, recall on €):
  - FIXED: fill<40% catches 92.7%; adding mass catches 95.6%.
  - HYBRID: 92.8% → 95.8%.
  - ON_CALL: **68.4% → 96.6%**.
- On fixed schedules, weight's role is **evidence**: tonnes per lift and €/t make the case to the customer and operator for stepping down the frequency ladder. Weight's detection uplift there is small.
- Task C simulated counterfactual [data, `20c`], annualised best permissible action:
  - FIXED: €2,779/yr per device, of which **€317 needs weight** (mass-target trigger).
  - HYBRID: €1,735/yr, of which €77 needs weight.
  - ON_CALL: €764/yr, of which €245 needs weight.
  - **19%** of cases carry a hidden-cost trap, so cutting naively loses money.

---

## 3. €/t transparency and contract benchmarking (UC3)

- **Net cost €/t per contract vs peer median** [data, `30a`]. Peers are the same stream (plus region when there are at least 5). n=446.
  - 41% of contracts sit 12% or more above peer, and 35% sit 25% or more above.
  - Excess over peer median totals €747k/yr, mean **€1,675 per contract-yr**. Treat this as a **ceiling**: remote sites, small streams and minimums explain part of it (S03/S04/S32).
  - FIXED contracts are a median +14% above peer (€2,879 per contract-yr). ON_CALL contracts are −2.4%.
- **C2 valuation** (official rules, dev cases n=207) [data]:
  - Best set €1,064 per contract-yr on €13.5k annual cost (7.9%).
  - Positive value: tender €176.8k, renegotiate €114.6k, dispute €2.6k, request data €0.6k.
  - **It is tariff-driven** [fact/sourced: red-team, confirmed].
- **How much needs weight** (`30b`), share of renegotiate+tender value:

| Contract group | Contracts | Value | Share |
|---|---|---|---|
| Ticket shared | 164 | €186k | 64% |
| Invoice tonnage only (operator-reported) | 29 | €22k | 8% |
| **Device weight is the only mass** | 13 | **€83k** | **28%** |

  - Without device weight, the last group has no independent €/t at all. That is almost entirely OP-D, which shares 0 tickets.

---

## 4. Quality: contamination and moisture (UC4), a negative result

- **Detector.** Device kg per fill-% before each lift, compared with the device's own as-of median of its last 8 lifts. Labels were not used to fit it [data, `40_density_pr.csv`, 9,189 lifts].
  - MOISTURE_HEAVY_LOAD: at z>+0.10, **precision 0.7%, recall 16%**. The median z of wet loads is only +0.026, against a true +16% water.
  - CONTAMINATION_INCIDENT: at |z|>0.10, precision 0.6%, recall 20%. The hourly kg/fill ratio inside incidents is 0.99× the pre-incident level (n=86).
- **€ context.** Grade loss (B 0.85 / C 0.6 / R) totals €199k in the window: €655/dy overall, €1,283 per credit-stream dy. Cardboard is €1,518/dy. Water mass billed through processing fees is only €1.4k (69 loads, mean +491 kg).
- **Conclusion.** This synthetic world does not encode a usable density signature. **Do not demo a contamination detector as working.** Present it as a hypothesis that needs real pressure-curve and density data. Weight's measurable role here is pricing the grade loss in € for the customer. The grade itself remains the operator's assessment.

---

## 5. Sensor drift and calibration (UC5)

There are 19 labelled episodes (15 drift, 4 calibration) over 365 dy, lasting a median 78 days before today's fix [data, `50_drift_detectors.csv`]:

| Detector | Detected | Lead after onset | Days before fix | False-alarm episodes/dy |
|---|---|---|---|---|
| Ticket-based, 6% (median of 3 clean pairs) | 7/19 (7 of the 10 with any clean pair) | 47 d | 33 d | **0.30** |
| Ticket-free, 6% (kg/fill vs own baseline) | 12/19 | **20 d** | 42 d | 2.8 (too noisy alone) |

- **Recommendation.** Use the ticket-free signal to raise a *watch*, and require ticket confirmation (or a VERIFY_WEIGHT_SENSOR work order) before acting.
- **Value.** Fewer months of biased mass data, and targeted recalibration instead of calendar recalibration. There were 129 SENSOR_RECALIBRATION work orders in a year. The € per visit is an [assumption] that the team must set. Do not claim money here.

---

## 6. Baselines to beat (validation, from `baselines_run.log`) and improvements

| Task | Best baseline | Score |
|---|---|---|
| A (B1) | net exact to cent 0.964, €/t within 5% 0.976, 3 fabricated €/t | |
| B macro-F1 | hybrid ML + rules | **0.782** (rules 0.731, GBM 0.352) |
| B2 | B5 | **67.75** (weight-bias metric 0.02, over/undercharge 0.33/0.39) |
| C | B4 GBM | acceptable 0.723, regret €100 (no-action 0.630 / €167) |
| C2 | B6 | value capture **0.774**, regret €240 |

Improvements, expected gain [estimate]:
1. **Task B, mass-aware PREMATURE rule on ON_CALL.** Add (fill<40) OR (mass-implied fill<40), plus an S40 signature (fill≥80 with mass-fill<50). In our test, ON_CALL lift recall rose from 0.69 to 0.95 at precision 0.40→0.46. Expected PREMATURE_UNJUSTIFIED F1 0.72 → about 0.80, and macro-F1 +0.01–0.02.
2. **Task C2, device-weight €/t for contracts without tickets**, plus a lower renegotiate threshold where the dispute evidence is strong. B6 recall is only 0.44 for renegotiate and 0.46 for tender, and 28% of the value sits on device-only-mass contracts. Expected value capture 0.77 → 0.83–0.88.
3. **Task B2 weight-bias metric (0.02).** Measure bias on weighed-tare, single-load pairs with a per-vehicle stored-tare correction, not against raw device estimates. Raising that one metric to about 0.5 lifts the overall score by about +4–5 points, to about 72.
4. Optional Task A: take grade from published `quality_assessments` and keep €/t NULL on 0-kg tickets (net-exact 0.964 → ~0.98).

---

## 7. Hero stories (traced end to end; `outputs/61_hero_traces.txt`)

**H1. "Invoice says 5.08 t; weighbridge and compactor both say about 4.2 t."**
- Chain: job `OP-E-003920032` → `COL-00392-0032`, CMP-00392, mixed waste, HYBRID → ticket `WB-OP-E-00392-0032` (net 4,200 kg) → device 4,200 → 75 kg, so 4,125 kg collected (−1.8% vs ticket) → contract `CTR-00392-V1`, HYBRID, processing €126.82/t.
- Invoice line `INV-00392-202512-L045`: PROCESSING 5.080 t = €644.25. Reference: 4.2 t = €532.64.
- **€111.61 overbilled** (label WEIGHT_BASIS_MISMATCH, clear). Job €/t is €249.5 invoiced vs €222.9 per contract.
- Two independent masses agree, so this is a clean, human-approved dispute draft.

**H2. "It's the truck's tare, not anyone's intent" (neutral attribution).**
- Vehicle `OP-E-V06`: stored tare 15,960 kg vs a weighed median of 16,320 kg (n=209). Every stored-tare net is therefore about 360 kg too high. Median device/ticket gap is −19.7% (124 loads).
- Example: job `OP-E-000700009` → ticket `WB-OP-E-00070-0009` (19,060 − 15,960 = 3,100 kg) → device 2,675 kg → contract `CTR-00070-V1`, processing €126.72/t → about **€45.6 per lift** on the processing line [estimate: corrected net ≈ 2,740 kg].
- Mirror case: vehicle `OP-A-V12` stores 16,140 kg vs a weighed 15,855 kg, so its nets are about 285 kg *low*. On cardboard job `OP-A-001950014` (`CTR-00195-V1`, credit €89.97/t), the customer loses about €25.6 of credit.
- Same mechanism, opposite sign. The fix is weighbridge hygiene (re-weigh the tare), shared first with the operator.

**H3. "Poland-like" fixed schedule, and no tickets ever (CMP-00430, ORG-0049).**
- FIXED 2 lifts/week, 8 m³ mixed waste, operator OP-D (0% ticket sharing, so **device weight is the only mass**).
- In the window: 78 lifts, median fill at lift **27.9%**, median 1,058 kg. **45 lifts unjustified, €14.7k** [data].
- Example: `OP-D-004300011` → `COL-00430-0011`: fill 17%, 615 kg, invoice lines L004–L006 = €472.77 → **€675/t** (contract `CTR-00430-V1`, FIXED_PER_LIFT €409.06/lift).
- Task C: REDUCE_FREQUENCY is the only acceptable action in 7 consecutive cases, worth €3,750 per 56 days. The mass trigger and switching to on-call are *impermissible* because of overflow, which is a useful demo of human-approved, constrained advice.
- C2: contract €/t €436 vs peer €194 (+125%). TENDER is valued at €3.5k.

**H4. Contract benchmark that only device weight makes visible (CTR-00142, OP-D, cardboard, HYBRID_MIN).**
- 287.5 t and 42 lifts; no tickets.
- Positive C2 values: RENEGOTIATE €9,953 or TENDER €16,072, on €13.1k annual cost.
- Use it to show "€/t from device weight → peer comparison → proposal + approval + reversal path".
- Present it as an option for the customer to *discuss* with its operator, not as a switch.

**Caveats.** Weight error σ≈1.4% is a future-scenario simulation; Task C/C2 values are simulated expected values, not causal evidence (ECONOMIC_MODEL §6); denominators include the ~10% of devices without weight.
