# Data analyst: where does weight create measurable value? (Part 2 evidence)

Scope: competition public pack: 447 devices (404 with integrated weight), 52 customers, 5 fictional operators, 18,477 lifts. Labels exist only for 1 Oct 2025 – 31 Jul 2026 (304 d = **365.4 device-years, 330.9 with weight**), so EUR below are 10-month label-window sums; "per device-year" divides by those. Tags: **[data]** computed from the synthetic public tables (scripts in §10), **[sim]** the dataset's own simulated counterfactual, **[est]** my extrapolation. **All prices are hypothetical; none is a real saving.**

## 1. Findings in one screen
1. **Weight is mostly a denominator, not an overbilling detector.** Mass-linked charges are 46% of gross correct charges (EUR 2.50M of 5.44M), yet billing errors needing an independent mass total only EUR ~8k in 10 months (§3) [data].
2. **Task C2 value capture needs *a* mass, hardly its accuracy**: 50% (no mass) → 55% (invoice tonnage only) → 72% (tickets+invoice) → 73% (device weight alone) → 77% (all sources; oracle 77.5%). A hypothetical device at σ=10% still captures 74.3% [data/sim].
3. **Weight beats fill outright only for S40 (fill sensor falsely high)**: a fill-vs-mass order guard has 96% precision, fill-only 5% [data].
4. **ECONOMIC_MODEL §2b's ±3.3% is unusable as a lift-reconciliation tolerance**: 53% of paired lifts exceed it, and 36% of "clean" ones [data]. Use |diff|>100 kg and >10% (or ~3σ of the observed gap, σ≈2.6%).
5. **A naive operator weight-bias score (device vs ticket) wrongly blames operators**: +5.5 pp bias, 74% of operator-region-months falsely flagged; cause adjustment cuts error to 1.2–1.6 pp [data].
6. Moisture, contamination and mis-sorting are **not** visible in mass-vs-fill here (AUC 0.5–0.7) [data].

## 2. Q1: device mass vs weighbridge net (9,062 paired lifts)
|gap|>3.3%: **52.8%**; >10%: **24.8%**; >100 kg: 36.4% (whole year, 11,955 pairs: 53.1/25.2%). OP-D shares no tickets, OP-C 53%: untestable there.

| Cause (`WEIGHT_DISCREPANCY`) | lifts | share of 2,250 gaps >10% | median gap kg | actionable | EUR effect of billing on device mass, net / gross |
|---|---|---|---|---|---|
| Side waste on same truck | 771 | 34.3% | -840 | no | +18.3k / 59.6k |
| Stale stored tare (weighbridge side) | 684 | 30.4% | -255 | **yes** | +2.9k / 13.8k |
| Combined load, 50/50 split | 271 | 12.0% | -340 | no | -0.1k / 17.6k |
| Noise/timing, small loads | 134 | 6.0% | -170 | no | -0.2k / 2.2k |
| Device drift/degraded/calibration | 87 | 3.9% | +295 | **yes** | -0.1k / 4.1k |
| No label (≤100 kg or agree) | 7,115 | 13.5% | -25 | n/a | +7.4k / 33.4k |

Total gross |Δ| EUR 130.6k on EUR 2.58M billed (5.1%), net +28.3k (1.1%); gross includes device noise, so read net. On 2.5–3.5 t loads only **49.8% are within ±100 kg (77.6% for clean lifts)** vs the 95% single-reading target: lift gaps add timing, residual and 20 kg weighbridge resolution (median -30 kg). Stale tares are concentrated: 19 of 70 vehicles, **top 10 = 79%**; 42–46% of tickets at every operator use a stored tare (fleet practice, not one operator). `FIXED_PER_LIFT` contracts (29%) have little mass exposure (mean |Δ| EUR 5 per lift vs 18–24).

## 3. Q2: invoice discrepancies and what needs independent weight (10 months)
| Family | n | overcharge EUR | needs independent mass? |
|---|---|---|---|
| Duplicate line | 133 | 18,353 | no |
| Unmatched/phantom line | 138 | 13,563 | no |
| Omitted material credit | 54 | 9,161 | flag no; valuing yes (22 lines, EUR 3.5k, have no ticket; device mass is their only source) |
| Wrong surcharge | 150 | 2,708 | no |
| **Weight-basis mismatch** (tonnage +8…+25%, mean +16%) | 77 (0.54% of 14,219 per-tonne lines) | 1,392 (net 729) | **yes**: 64% have a ticket, 84% a device estimate; device >10% below invoice for 67% |
| Outdated tariff, uninvoiced, omitted lift lines | 500 | 430 (net -27,132, undercharges) | no |

All families: EUR 45.6k over, 28.2k under. Weight-only part: 1.4k (mismatch) + 3.5k (credit valuation) + 2.9k (net stale-tare effect) ≈ **EUR 8k ≈ EUR 21 per device-year**. `REQUEST_WEIGHBRIDGE_DATA` is positive for 7 of 63 candidate contracts (EUR 620). Do not headline overbilling recovery.

## 4. Q3: EUR/t coverage (13,840 lifts with reference economics)
| Operator | A | B | C | D | E | All |
|---|---|---|---|---|---|---|
| lifts | 2,071 | 2,382 | 1,565 | 2,160 | 5,662 | 13,840 |
| published ticket | 96% | 89% | 53% | **0%** | 94% | 74.3% |
| invoice tonnage only (unverifiable) | 3% | 8% | 37% | **70%** | 5% | 18.8% |
| EUR/t NULL today | 0.7% | 3.4% | 10.1% | **30.2%** | 0.8% | **6.9% of lifts, 11.1% of collection spend (EUR 349k)** |
| median ticket lag, d | 1.8 | 7.4 | 27.9 | – | 0.3 | 0.6 (p90 23) |

26% of lifts (26% of EUR 3.14M collection cost) have no verifiable mass. A device estimate exists for 95.5% of the NULL lifts and makes 2,249 invoice-only lifts (16% of all) verifiable. Timeliness: ticket within 7 d for 57%, 30 d for 69%; invoice median 8 d after month end; device mass at lift time for 88%. EUR/t from device mass: median error 3.4%, within 10% for 76% (89% without a disagreement label); B1's device-only EUR/t is within 5% only 65%.

## 5. Q4: unnecessary lifts, what weight adds beyond fill
Pools = illustrative avoidable logistics cost (`value_at_stake_eur`, true fill <40%). Mass-implied fill = `mass / kg-per-fill-pp`, calibrated per device on its first 120 days; evaluated Feb–Jul (6,582 lifts).

| Cause | lifts / EUR | fill-only `fill<40` recall / precision | mass-aware | verdict |
|---|---|---|---|---|
| S40 fill falsely high | 295 / 53.3k (EUR 161 per weighted device-yr) | 47% / **5%** | signature `fill≥80 & mass-fill<50`: 51.5% / 81%; order-time guard: recall 50.7%, **precision 95.8%** (fires on 2.2% of fill-triggered orders; EUR 13.2k of 25.1k); hourly alert: 89% of 163 episodes, median 3 h, 9 false-alert devices of 375; precedes the order in 44% of S40 lifts | **weight unique** |
| S39 precautionary order | 343 / 50.4k | 87% / 12.5% | `CUSTOMER_REQUEST & fill<40`: 86% / 72%; with mass 90% / 74% | ~no gain |
| S01 over-servicing | 1,216 / 171.0k | 91% / 44% | 91% / 45% | ~no gain |

Exceptions are needed either way: 94% of explained early lifts (max-interval, pre-closure) are flagged by `fill<40` (80% by mass-fill). **Mass-target trigger (Task C, [sim])**: over 3,573 weighted-device cases, adding `MASS_TARGET_TRIGGER` lifts the best permissible 56-day benefit from EUR 131.6 to 171.9 (**+40.2, +23%**; >EUR 25 in 20% of cases); best action in 25.5%, truly needed in 12.5%; +74 (film), +104 (mixed plastic), +17 (bio); permissible only 59%. Indicative **EUR 262 per weighted device-year [est]**.

## 6. Q5: density, contamination, moisture
Implied density (mass / volume×fill), median kg/m³: cardboard 212, paper 345, film 133, mixed plastic 114, mixed waste 383, bio 684 (assumed 190/330/140/115/380/620). Between-device CV 22–28%, within-device MAD 6.4%: only device-relative z-scores work, and half (111 of 220) of z<-3 lifts are S40. **Moisture** (S28, 69 events, +12–35% water): density z AUC 0.61; kg per compaction cycle AUC 0.70 (best 16% precision at 33% recall); EUR at stake EUR 144 on 34 loads. **Contamination**: grade vs density AUC 0.51–0.52, incident periods 0.507; mixed-waste density 387 vs 384 kg/m³ with/without a recyclable stream on site. Grade losses (B 27.7k, C 123.9k, rejected 47.8k) are real but invisible to mass, which only prices them. **Not a use case.**

## 7. Q6: operator scorecard and C2 pool
| Truth, lift-weighted | on-time | missed | shared ≤7 d | over | under | discrepant lines | weight bias |
|---|---|---|---|---|---|---|---|
| OP-A | 68% | 0.7% | 91% | 0.53% | 0.24% | 1.0% | -1.1 pp |
| OP-B | 53% | 1.4% | 41% | 1.16% | 0.94% | 2.0% | 0.0 |
| OP-C | 43% | 2.1% | 0% | 2.29% | 0.97% | 3.2% | +0.2 |
| OP-D | 57% | 1.3% | 0% | 1.77% | 1.57% | 2.4% | -0.7 |
| OP-E | 62% | 0.7% | 89% | 0.85% | 0.42% | 1.4% | +0.7 |

Weight bias per operator-region-month (n=108): truth -0.04±0.88 pp; naive device-vs-ticket (B5 method) MAE 5.54 pp, 74% falsely >3.3%; dropping combined and side-waste lifts: MAE 1.2–1.6 pp, 0.9% false. **C2** (207 dev contracts = 40% of customers, as of 1 Jul 2026, annual cost EUR 2.79M): best-set value **EUR 220k = EUR 1,064/contract-year (7.9% of cost)** = tender 170k + renegotiate 47k + dispute 2.6k + request 0.6k; 3.8% (OP-E) to 16.3% (OP-C) of cost. Extrapolated to 437 active contracts ≈ EUR 465k/yr [est]. Verification actions are only 1.5% of the value; renegotiation/tender need mass for repricing. Weight uplift: **+EUR 190/contract-year where tickets are not shared (device-only vs invoice-only), +56 where they are (default vs no device)**.

## 8. Q7: value vs weighing accuracy σ
σ = relative 1 sd of lift mass, 15 kg floor, reference = clean tickets (n=7,088), seed 20261106.
| σ | 0.5% | 1% | 1.5% | 3% | 5% | 10% |
|---|---|---|---|---|---|---|
| EUR/t within ±10% | 99.4% | 99.5% | 99.2% | 99.2% | 94.9% | 68.3% |
| EUR/t median / p95 error | 0.6/3.6% | 0.8/3.5% | 1.1/3.9% | 2.1/6.2% | 3.3/10.0% | 6.7/20.2% |
| detect +10% tonnage overbilling (false alarm) | 94.6% (0.7%) | 94.6% (1.0%) | 94.6% (1.3%) | 85.1% (1.8%) | 46.9% (2.0%) | 15.3% (2.2%) |
| observed mismatch EUR detected of 1,330 | 1,328 | 1,328 | 1,328 | 1,306 | 1,155 | 581 |
| tare/drift flag recall / precision | .93/.87* | .93/.87* | .93/.87* | .87/.81 | .81/.69 | .73/.32 |
| S40 guard recall | .51 | .51 | .51 | .50 | .50 | .51 |
| C2 value captured | 74.9% | 74.9% | 74.9% | 74.8% | 74.7% | 74.3% |

*Observed; the data cannot emulate σ below its own 1.5–2.6% floor. The provided example script reproduces the overbilling/EUR/t rows (`outputs/07_example_script_output.txt`). **Tiers**: σ≤10% suffices for C2 benchmarking and S40 (false blocks rise ×10 only at σ=30%); 3–5% for ticket reconciliation and tare detection; ≤1.5% only for +5% tonnage overbilling.

## 9. Baselines and AI vs rules
Reference scores (public validation, reproduced in `analysis/baseline_run`): **A** B1 net exact 0.964, collection exact 0.998, EUR/t coverage 0.997, within 5% 0.976. **B** macro-F1 rules B2 **0.731**, GBM B4 0.352, hybrid **0.782** (WEIGHT_DISCREPANCY F1 0.887 vs 0.913; PREMATURE 0.716 vs 0.925; B4 scores 0 on invoice families). **B2** B5 scorecard 67.75 (weight-bias metric 0.021). **C** regret EUR 166.7 (no action) / 150.4 (B3) / **100.1** (B4). **C2** B6 regret **EUR 240.1**, captured 0.774 (no action 1,063.9; everything 658.1).

Weight-anomaly detectors (train <1 Jun 2026, validate Jun–Jul, 189 actionable positives = tare or device fault):
| Detector | Precision | Recall | F1 |
|---|---|---|---|
| R1 B2 rule (|diff|>100 kg, >10%, single load, no side-waste flag) | .864 | .910 | **.887** |
| R2c rule + as-of vehicle/device bias evidence | .762 | 1.000 | .865 |
| GBM basic features | .933 | .884 | .908 |
| GBM + as-of vehicle/device history | .955 | .899 | **.926** |
| Isolation forest (unsupervised) | .102 | .095 | .098 |

GBM beats R1 by +4.0 pp F1 (paired bootstrap 95% CI [0.3, 7.9]); cause attribution 91.8% (GBM) vs 85.2% (rule). The "any weight-discrepancy" label is a deterministic size test (rule recall 1.0), so only the actionable target is informative. Unsupervised ML fails; supervised ML needs human-confirmed cases that do not exist on day 1. **Rules flag and explain; GBM later ranks and classifies cause; an LLM only words the evidence pack; a human approves.**

## 10. Ranked use cases
| # | Use case | Headline | Tables / columns | Caveats |
|---|---|---|---|---|
| 1 | Independent mass for EUR/t and C2 actions | capture 50%→77%; +EUR 190 (no sharing) / 56 (sharing) per contract-year; 26% of lifts unverified today; σ≤10% OK | `collection_events.device_estimated_collected_kg`, `weighbridge_tickets.allocated_net_kg`, `contract_versions`, `invoice_lines`, `labels_dev/operator_action_values` | hypothetical tariffs; most value is tariff gap; published C2 rules; 40% of customers |
| 2 | Fill-vs-mass order guard (S40) | EUR 161 per weighted device-yr pool; guard 51% recall, 96% precision | `telemetry_hourly.fill_pct/mass_kg`, `collection_events.order_placed_at` | S40 frequency is a synthetic assumption; illustrative cost; calibration uses fill itself |
| 3 | Mass-target pickup option beyond SMART fill | +EUR 40.2 per 56-day case (+23%), ~EUR 262/device-yr | `labels_dev/decision_outcomes` | [sim]; 59% permissible; SMART's domain |
| 4 | Neutral cause-attributed reconciliation and scorecard | bias error 5.5→1.2–1.6 pp; F1 .89–.93; 10 vehicles = 79% of tare errors | tickets (`tare_method`, `loads_on_vehicle`), `driver_reported_side_waste` | cash small (~EUR 21/device-yr); value is evidence and trust |
| 5 | Invoice reconciliation, weight as one input | EUR 45.6k over / 28.2k under; F1 .84–.96 on structural families | `invoices`, `invoice_lines`, `reference_charge_lines` | weight not needed for most; weight-only ~EUR 5k |

**Price ceiling [est]**: weight-attributable value ≈ EUR 120–270 per weighted device-year (S40 guard 67–82 + C2 uplift 56–190), up to ~EUR 530 with the simulated mass trigger. RESEARCH.md's EUR 49/month (EUR 588/yr) exceeds it; a standalone fee should be well under EUR 20/month unless bundled.

**Caveats / open question.** Labels end 31 Jul 2026, test labels hidden, one synthetic realisation (CIs only in §9). The σ study uses billing mass as truth proxy (includes tare error). 43 devices (9.6%) lack weight; 11.6% of lifts lack a device estimate. Open question for Tommi/Part 1: is a lift tolerance of |diff|>100 kg and >10% (not ±3.3%) acceptable to operators, and can a static calibration test replace weighbridge reconciliation, which hits ±100 kg on only 78% of clean 3 t lifts?

## 11. Reproduce (outputs in `analysis/outputs/`, seed 20261106 in `analysis/common.py`)
Run `analysis/run_all.sh` (python `/home/hackathon/.claude/jobs/717fee2a/tmp/v/bin/python -I`).
| Question | Script |
|---|---|
| Q1 | `01_weight_disagreement.py` |
| Q2, Q3 | `02_invoice_value_and_eurt_coverage.py` |
| Q4 | `03_unnecessary_lifts_s39_s40.py`, `08_decisions_mass_trigger.py` |
| Q5 | `04_density_contamination_moisture.py` |
| Q6 | `05_operator_scorecard_c2.py`, `05c_scorecard_weight_bias.py`, `05b_c2_mass_ablation.py MODE` |
| Q7 | `06_accuracy_sensitivity.py` |
| AI vs rules / baselines / SQL | `07_rules_vs_ml.py`, `baseline_run/baselines/run_all.py competition`, `10_sql_crosschecks.py` |

```sql
WITH w AS (SELECT DISTINCT ON (operator_job_ref) operator_job_ref, allocated_net_kg FROM wb ORDER BY 1, ticket_id)
SELECT count(*), avg((abs(rel)>0.033)::INT) gt33, avg((abs(rel)>0.10)::INT) gt10 FROM (
  SELECT (c.device_estimated_collected_kg-w.allocated_net_kg)/w.allocated_net_kg rel FROM ce c JOIN ref r USING(collection_id) JOIN w USING(operator_job_ref)
  WHERE c.status IN ('COMPLETED','PARTIAL') AND c.device_estimated_collected_kg IS NOT NULL AND w.allocated_net_kg>0);
SELECT observable_mass_source, count(*), sum(collection_cost_eur) FROM ref WHERE status IN ('COMPLETED','PARTIAL') GROUP BY 1;
```
```python
kgpp = (mass_kg/fill_pct).groupby(device).median()      # first 120 d, VALID, fill 50-95
guard = (fill_at_order >= 80) & (mass_at_order/kgpp < 50)  # S40 order guard
# C2 ablation: B1 -> B2 invoice flags -> B6 with billing mass from {none, invoice, tickets+invoice, device, default, oracle, oracle+N(0,max(15kg, s*m))}
```
Third-party: pandas, numpy, scipy, scikit-learn, duckdb, pyarrow (BSD/MIT/Apache-2.0). The dataset's own `europress_data` code (copied read-only into `analysis/baseline_run`) provides the pricing engine and baselines.
