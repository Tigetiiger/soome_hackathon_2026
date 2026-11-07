# Hydraulic soft sensor - container mass report (`bins25`)

On the `time` (same machines, later months) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **3.8 %** (median 2.8 %, 76 % of lifts within 5 %, n = 303), against 26.8 % for the naive fill × nominal density estimate; 4 of 4 materials meet the < 5 % target. The calibrated p10–p90 interval covers 71 % of lift masses (target 80 %). On the `bins` (unseen machines) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **8.9 %** (median 6.5 %, 43 % of lifts within 5 %, n = 84), against 32.7 % for the naive fill × nominal density estimate; 0 of 4 materials meet the < 5 % target (missing: cardboard, paper, plastic_film, mixed_waste). The calibrated p10–p90 interval covers 67 % of lift masses (target 80 %).

> **All data is synthetic** (simulator output for the Europress hackathon). The numbers demonstrate the method, not field performance.

![mean % error at lift by material](plots/lift_error_by_material.png)

## Compute

| item | value |
|---|---|
| training wall time (all splits) | 278 s |
| feature build | 2.4 s |
| peak memory (RSS) | 0.69 GB |
| hourly rows / machines | 219,000 / 25 |
| split `time` wall time | 179 s |
| split `bins` wall time | 97 s |

## Split `time` (same machines, later months)

Same machines, trained on the first 75 % of time and tested on the last 25 %. Training machines: 25, test machines: 25, test from 2026-07-01 17:15:00+03:00. Rows: train 129,152, val 17,082, cal 15,768, test 54,750.

Selected setup: cardboard → **shared**, paper → **shared**, plastic_film → **per_material**, mixed_waste → **per_material**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 152 | 103 | 4.3 | 3.0 | 72 % | 95 % | -36 | 73 % | 368 |
| paper | 51 | 95 | 3.3 | 2.9 | 78 % | 98 % | -33 | 57 % | 233 |
| plastic_film | 68 | 50 | 2.8 | 1.7 | 87 % | 97 % | -16 | 74 % | 186 |
| mixed_waste | 32 | 200 | 4.8 | 3.2 | 69 % | 88 % | -123 | 78 % | 657 |
| **overall** | 303 | 100 | 3.8 | 2.8 | 76 % | 95 % | -40 | 71 % | 335 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 70 | 5.9 | 79 % |
| paper | 63 | 4.6 | 65 % |
| plastic_film | 31 | 4.0 | 72 % |
| mixed_waste | 79 | 4.6 | 80 % |
| overall | 60 | 5.1 | 75 % |

![predicted vs true at lift, time](plots/pred_vs_true_time.png)

## Split `bins` (unseen machines)

Unseen machines (25 % held out, stratified by material), tested on the last 25 % of the period. Training machines: 14, test machines: 7, test from 2026-07-01 17:15:00+03:00. Rows: train 90,446, val 19,644, cal 6,531, test 15,330.

Selected setup: cardboard → **shared**, paper → **shared**, plastic_film → **per_material**, mixed_waste → **shared**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 35 | 183 | 7.2 | 4.5 | 54 % | 69 % | -148 | 54 % | 389 |
| paper | 11 | 148 | 9.2 | 4.3 | 64 % | 82 % | 15 | 82 % | 610 |
| plastic_film | 23 | 211 | 8.7 | 6.3 | 39 % | 61 % | -172 | 100 % | 950 |
| mixed_waste | 15 | 553 | 12.9 | 12.9 | 7 % | 33 % | -416 | 33 % | 1,131 |
| **overall** | 84 | 252 | 8.9 | 6.5 | 43 % | 62 % | -181 | 67 % | 704 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 93 | 7.3 | 75 % |
| paper | 61 | 5.7 | 90 % |
| plastic_film | 73 | 7.4 | 85 % |
| mixed_waste | 149 | 6.8 | 79 % |
| overall | 91 | 7.0 | 81 % |

![predicted vs true at lift, bins](plots/pred_vs_true_bins.png)

## Comparison ladder (mean % error at lift)

Each step adds signals: naive fill × nominal density → fill + press counts (LightGBM) → + peak hydraulic pressure → + pressure graph (pressure along the ram stroke: contact point, rise slope, mean pressure, completion) → + weather (full model, shared across materials); then the full per-material models and the setup selected per material on validation. The reported fill level itself is the machine's approximate, pressure-derived estimate.

**`time` (same machines, later months)**

| step | cardboard | paper | plastic_film | mixed_waste | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 26.3 | 21.2 | 27.0 | 37.4 | 26.8 |
| fill + presses | 5.3 | 5.4 | 6.3 | 7.1 | 5.8 |
| + pressure (peak) | 4.8 | 4.0 | 2.8 | 4.4 | 4.2 |
| + pressure graph | 4.5 | 4.4 | 2.7 | 4.1 | 4.0 |
| + weather (full, shared) | 4.3 | 3.3 | 3.0 | 5.5 | 4.0 |
| full, per material | 3.8 | 3.5 | 2.8 | 4.8 | 3.6 |
| selected | 4.3 | 3.3 | 2.8 | 4.8 | 3.8 |

**`bins` (unseen machines)**

| step | cardboard | paper | plastic_film | mixed_waste | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 28.8 | 44.2 | 29.2 | 38.6 | 32.7 |
| fill + presses | 11.8 | 5.9 | 17.3 | 20.0 | 14.0 |
| + pressure (peak) | 7.6 | 6.0 | 3.8 | 13.9 | 7.5 |
| + pressure graph | 7.2 | 10.4 | 4.3 | 13.0 | 7.9 |
| + weather (full, shared) | 7.2 | 9.2 | 4.8 | 12.9 | 7.8 |
| full, per material | 7.0 | 7.3 | 8.7 | 12.6 | 8.5 |
| selected | 7.2 | 9.2 | 8.7 | 12.9 | 8.9 |

![comparison ladder](plots/ladder.png)

## Per-material vs shared model

Setup is chosen per material on the validation lifts (mean % error); `–` means no validation lifts of that material, in which case the shared model is kept.

| material | split | val shared | val per-material | test shared | test per-material | selected | better on test |
|---|---|---|---|---|---|---|---|
| cardboard | time | 3.7 | 3.8 | 4.3 | 3.8 | shared | per_material |
| paper | time | 3.0 | 3.7 | 3.3 | 3.5 | shared | shared |
| plastic_film | time | 3.7 | 2.3 | 3.0 | 2.8 | per_material | per_material |
| mixed_waste | time | 5.8 | 4.7 | 5.5 | 4.8 | per_material | per_material |
| cardboard | bins | 3.8 | 3.9 | 7.2 | 7.0 | shared | per_material |
| paper | bins | 14.5 | 15.5 | 9.2 | 7.3 | shared | per_material |
| plastic_film | bins | 4.5 | 3.0 | 4.8 | 8.7 | per_material | shared |
| mixed_waste | bins | – | – | 12.9 | 12.6 | shared | per_material |

## Interval coverage (target 80 %)

Intervals come from LightGBM quantile models (p10/p90) calibrated by **normalised conformalised quantile regression (CQR)**: on a separate calibration slice (machines/hours used neither for training nor for validation) the score max(q_lo − y, y − q_hi) / width is computed and the interval is widened by its finite-sample 80 % quantile. Calibration is **Mondrian** by material × fill bucket (fill edges 50.0, 80.0 %); strata with fewer than 30 calibration points fall back to the material, then to the pool.

| material | split | lift coverage | lift width kg | hourly coverage | hourly width kg |
|---|---|---|---|---|---|
| cardboard | time | 73 % | 368 | 79 % | 255 |
| paper | time | 57 % | 233 | 65 % | 167 |
| plastic_film | time | 74 % | 186 | 72 % | 110 |
| mixed_waste | time | 78 % | 657 | 80 % | 338 |
| overall | time | 71 % | 335 | 75 % | 213 |
| cardboard | bins | 54 % | 389 | 75 % | 345 |
| paper | bins | 82 % | 610 | 90 % | 344 |
| plastic_film | bins | 100 % | 950 | 85 % | 383 |
| mixed_waste | bins | 33 % | 1,131 | 79 % | 568 |
| overall | bins | 67 % | 704 | 81 % | 388 |

Lift coverage more than 5 pp below target: cardboard/time (73 %), paper/time (57 %), plastic_film/time (74 %), cardboard/bins (54 %), mixed_waste/bins (33 %). Calibration pools all hours of a stratum, while the lift hour is the fullest, hardest hour of a cycle; on unseen machines the calibration machines are also few, so their error scale need not transfer.

![interval coverage](plots/coverage_by_material.png)

## Hourly mass curves

![hourly mass curves](plots/mass_curves_time.png)

## Error breakdowns (lift, selected model)

**Infeed type**

| infeed | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| indoor_shaft | 4.8 | 81 | 3.1 | 9 |
| lidded_hopper | 4.2 | 91 | 12.5 | 31 |
| open_hopper | 2.9 | 131 | 7.6 | 44 |

**Drainage (0 = no, 1 = yes)**

| drainage | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| 0.0 | 3.7 | 219 | 9.6 | 74 |
| 1.0 | 4.1 | 84 | 3.9 | 10 |

**Equipment class**

| equipment_class | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| COMBI | 4.0 | 248 | 8.9 | 84 |
| DUO | 3.2 | 55 | – | – |

**Container size**

| container_size | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| <=14 m3 | 3.6 | 140 | 10.1 | 52 |
| 15-20 m3 | 4.0 | 152 | 6.9 | 32 |
| >20 m3 | 3.6 | 11 | – | – |

**False-full episode in the cycle**

| false_full_in_cycle | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| no | 3.1 | 267 | 7.9 | 74 |
| yes | 9.5 | 36 | 16.5 | 10 |

**Weather in the week before lift**

| week | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| dry (bottom 25 %) | 4.0 | 76 | 7.4 | 22 |
| middle | 3.6 | 150 | 9.9 | 41 |
| wet (top 25 % rain7) | 4.1 | 77 | 8.5 | 21 |

## Learning curve (unseen machines, shared model)

| training machines | **overall** | cardboard | paper | plastic_film | mixed_waste |
|---|---|---|---|---|---|
| 10 | 9.7 | 7.6 | 13.4 | 7.6 | 15.1 |
| 14 | 7.8 | 7.2 | 9.2 | 4.8 | 12.9 |

No size below the full 14 training machines gets within 0.5 pp of the all-machines 7.8 %, so by this rule a pilot needs all 14 and the curve has not flattened yet. The largest gain is from 10 to 14 machines (9.7 → 7.8 %).

![learning curve](plots/learning_curve.png)

## Feature importance (top 5 by gain share)

Materials served by the shared model show the same ranking (one model).

| material | split | model | top features |
|---|---|---|---|
| cardboard | time | shared | pressure_kg_m3 (55 %), naive_kg_m3 (30 %), curve_rise_slope_ewm (8 %), graph_kg_m3 (2 %), p_ewm (1 %) |
| mixed_waste | time | per_material | presses_cycle (84 %), fill_ffill (6 %), pressure_kg_m3 (6 %), curve_rise_slope_ewm (2 %), fill_max_cycle (1 %) |
| paper | time | shared | pressure_kg_m3 (55 %), naive_kg_m3 (30 %), curve_rise_slope_ewm (8 %), graph_kg_m3 (2 %), p_ewm (1 %) |
| plastic_film | time | per_material | p_ewm (45 %), pressure_kg_m3 (29 %), curve_rise_slope_ewm (23 %), fill_ffill (1 %), presses_cycle (1 %) |
| cardboard | bins | shared | pressure_kg_m3 (53 %), naive_kg_m3 (33 %), curve_rise_slope_ewm (8 %), graph_kg_m3 (2 %), presses_cycle (1 %) |
| mixed_waste | bins | shared | pressure_kg_m3 (53 %), naive_kg_m3 (33 %), curve_rise_slope_ewm (8 %), graph_kg_m3 (2 %), presses_cycle (1 %) |
| paper | bins | shared | pressure_kg_m3 (53 %), naive_kg_m3 (33 %), curve_rise_slope_ewm (8 %), graph_kg_m3 (2 %), presses_cycle (1 %) |
| plastic_film | bins | per_material | curve_rise_slope_ewm (60 %), p_ewm (18 %), pressure_kg_m3 (16 %), fill_ffill (2 %), naive_kg_m3 (1 %) |

![feature importance time](plots/feature_importance_time.png)

![SHAP summary time](plots/shap_time.png)

![feature importance bins](plots/feature_importance_bins.png)

![SHAP summary bins](plots/shap_bins.png)

## Target check (mean % error at lift < 5 %)

| material | split | mean % at lift | n lifts | < 5 % |
|---|---|---|---|---|
| cardboard | time | 4.3 | 152 | yes |
| paper | time | 3.3 | 51 | yes |
| plastic_film | time | 2.8 | 68 | yes |
| mixed_waste | time | 4.8 | 32 | yes |
| cardboard | bins | 7.2 | 35 | **no** |
| paper | bins | 9.2 | 11 | **no** |
| plastic_film | bins | 8.7 | 23 | **no** |
| mixed_waste | bins | 12.9 | 15 | **no** |

**Not met, and the likely reasons from the data:**

- **cardboard, `bins` split (7.2 %)**: the median is 4.5 %, so a few large misses pull the mean up; 3 of 35 lifts had a false-full episode in the cycle (13.0 % vs 6.7 % without); the fleet has 13 cardboard machine(s) of 25, at most 10 of them in training; systematic bias of -6.1 %.
- **paper, `bins` split (9.2 %)**: only 11 test lifts on 1 test machine(s), so a few cycles dominate; the median is 4.3 %, so a few large misses pull the mean up; the 3 worst lifts carry 79 % of the summed % error; 2 of 11 lifts had a false-full episode in the cycle (35.3 % vs 3.3 % without); the fleet has 4 paper machine(s) of 25, at most 3 of them in training; systematic bias of +4.2 %.
- **plastic_film, `bins` split (8.7 %)**: only 23 test lifts on 2 test machine(s), so a few cycles dominate; the error is broad-based (median 6.3 %), not driven by a few outliers; the 3 worst lifts carry 27 % of the summed % error; the fleet has 6 plastic_film machine(s) of 25, at most 4 of them in training; the shared model scores 4.8 % on test (validation chose the other setup); adding weather did not help (4.3 % with pressure → 4.8 % full shared); systematic bias of -5.2 %.
- **mixed_waste, `bins` split (12.9 %)**: only 15 test lifts on 1 test machine(s), so a few cycles dominate; the error is broad-based (median 12.9 %), not driven by a few outliers; the 3 worst lifts carry 35 % of the summed % error; 3 of 15 lifts had a false-full episode in the cycle (15.1 % vs 12.4 % without); the fleet has 2 mixed_waste machine(s) of 25, at most 1 of them in training; no validation lifts for this material, so its setup choice was not validated; systematic bias of -6.9 %.
