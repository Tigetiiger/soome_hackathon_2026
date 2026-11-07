# Hydraulic soft sensor - container mass report (`bins25`)

On the `time` (same machines, later months) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **3.6 %** (median 2.7 %, 77 % of lifts within 5 %, n = 303), against 26.8 % for the naive fill × nominal density estimate; 3 of 4 materials meet the < 5 % target (missing: mixed_waste). The calibrated p10–p90 interval covers 72 % of lift masses (target 80 %). On the `bins` (unseen machines) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **9.0 %** (median 7.6 %, 38 % of lifts within 5 %, n = 84), against 32.7 % for the naive fill × nominal density estimate; 0 of 4 materials meet the < 5 % target (missing: cardboard, paper, plastic_film, mixed_waste). The calibrated p10–p90 interval covers 63 % of lift masses (target 80 %).

> **All data is synthetic** (simulator output for the Europress hackathon). The numbers demonstrate the method, not field performance.

![mean % error at lift by material](plots/lift_error_by_material.png)

## Compute

| item | value |
|---|---|
| training wall time (all splits) | 220 s |
| feature build | 0.8 s |
| peak memory (RSS) | 0.73 GB |
| hourly rows / machines | 219,000 / 25 |
| split `time` wall time | 119 s |
| split `bins` wall time | 100 s |

## Split `time` (same machines, later months)

Same machines, trained on the first 75 % of time and tested on the last 25 %. Training machines: 25, test machines: 25, test from 2026-07-01 17:15:00+03:00. Rows: train 129,152, val 17,082, cal 15,768, test 54,750.

Selected setup: cardboard → **per_material**, paper → **shared**, plastic_film → **per_material**, mixed_waste → **per_material**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 152 | 98 | 3.6 | 3.0 | 76 % | 99 % | -47 | 73 % | 352 |
| paper | 51 | 112 | 3.8 | 2.7 | 73 % | 98 % | -47 | 61 % | 282 |
| plastic_film | 68 | 47 | 2.7 | 2.0 | 87 % | 96 % | -10 | 78 % | 204 |
| mixed_waste | 32 | 213 | 5.2 | 3.8 | 62 % | 84 % | -124 | 72 % | 746 |
| **overall** | 303 | 101 | 3.6 | 2.7 | 77 % | 96 % | -47 | 72 % | 348 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 71 | 6.0 | 78 % |
| paper | 64 | 4.7 | 69 % |
| plastic_film | 33 | 4.1 | 71 % |
| mixed_waste | 81 | 4.6 | 81 % |
| overall | 62 | 5.2 | 75 % |

![predicted vs true at lift, time](plots/pred_vs_true_time.png)

## Split `bins` (unseen machines)

Unseen machines (25 % held out, stratified by material), tested on the last 25 % of the period. Training machines: 14, test machines: 7, test from 2026-07-01 17:15:00+03:00. Rows: train 90,446, val 19,644, cal 6,531, test 15,330.

Selected setup: cardboard → **per_material**, paper → **shared**, plastic_film → **per_material**, mixed_waste → **shared**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 35 | 182 | 6.5 | 6.4 | 37 % | 80 % | -146 | 51 % | 536 |
| paper | 11 | 147 | 9.3 | 3.6 | 73 % | 82 % | 24 | 82 % | 733 |
| plastic_film | 23 | 237 | 9.4 | 6.9 | 39 % | 57 % | -206 | 91 % | 1,025 |
| mixed_waste | 15 | 655 | 14.4 | 15.7 | 13 % | 20 % | -566 | 33 % | 1,138 |
| **overall** | 84 | 277 | 9.0 | 7.6 | 38 % | 63 % | -215 | 63 % | 803 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 82 | 6.6 | 83 % |
| paper | 59 | 5.5 | 91 % |
| plastic_film | 74 | 7.4 | 90 % |
| mixed_waste | 177 | 7.4 | 83 % |
| overall | 90 | 6.8 | 86 % |

![predicted vs true at lift, bins](plots/pred_vs_true_bins.png)

## Comparison ladder (mean % error at lift)

Each step adds signals: naive fill × nominal density → fill + press counts (LightGBM) → + peak hydraulic pressure → + pressure graph (pressure along the ram stroke: contact point, rise slope, mean pressure, completion) → + weather (full model, shared across materials); then the full per-material models and the setup selected per material on validation. The reported fill level itself is the machine's approximate, pressure-derived estimate.

**`time` (same machines, later months)**

| step | cardboard | paper | plastic_film | mixed_waste | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 26.3 | 21.2 | 27.0 | 37.4 | 26.8 |
| fill + presses | 5.3 | 5.4 | 6.3 | 7.1 | 5.8 |
| + pressure (peak) | 4.6 | 4.1 | 3.1 | 4.0 | 4.1 |
| + pressure graph | 4.7 | 4.5 | 3.2 | 4.2 | 4.3 |
| + weather (full, shared) | 4.4 | 3.8 | 2.9 | 4.6 | 4.0 |
| full, per material | 3.6 | 3.3 | 2.7 | 5.2 | 3.5 |
| selected | 3.6 | 3.8 | 2.7 | 5.2 | 3.6 |

**`bins` (unseen machines)**

| step | cardboard | paper | plastic_film | mixed_waste | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 28.8 | 44.2 | 29.2 | 38.6 | 32.7 |
| fill + presses | 11.4 | 7.2 | 18.3 | 18.5 | 14.0 |
| + pressure (peak) | 7.4 | 3.9 | 4.3 | 13.3 | 7.2 |
| + pressure graph | 7.3 | 6.4 | 4.2 | 12.5 | 7.2 |
| + weather (full, shared) | 7.0 | 9.3 | 3.8 | 14.4 | 7.7 |
| full, per material | 6.5 | 4.6 | 9.4 | 12.8 | 8.2 |
| selected | 6.5 | 9.3 | 9.4 | 14.4 | 9.0 |

![comparison ladder](plots/ladder.png)

## Per-material vs shared model

Setup is chosen per material on the validation lifts (mean % error); `–` means no validation lifts of that material, in which case the shared model is kept.

| material | split | val shared | val per-material | test shared | test per-material | selected | better on test |
|---|---|---|---|---|---|---|---|
| cardboard | time | 4.1 | 3.9 | 4.4 | 3.6 | per_material | per_material |
| paper | time | 3.9 | 3.9 | 3.8 | 3.3 | shared | per_material |
| plastic_film | time | 4.5 | 2.8 | 2.9 | 2.7 | per_material | per_material |
| mixed_waste | time | 5.7 | 5.4 | 4.6 | 5.2 | per_material | shared |
| cardboard | bins | 4.4 | 3.8 | 7.0 | 6.5 | per_material | per_material |
| paper | bins | 14.1 | 14.8 | 9.3 | 4.6 | shared | per_material |
| plastic_film | bins | 5.0 | 2.7 | 3.8 | 9.4 | per_material | shared |
| mixed_waste | bins | – | – | 14.4 | 12.8 | shared | per_material |

## Interval coverage (target 80 %)

Intervals come from LightGBM quantile models (p10/p90) calibrated by **normalised conformalised quantile regression (CQR)**: on a separate calibration slice (machines/hours used neither for training nor for validation) the score max(q_lo − y, y − q_hi) / width is computed and the interval is widened by its finite-sample 80 % quantile. Calibration is **Mondrian** by material × fill bucket (fill edges 50.0, 80.0 %); strata with fewer than 30 calibration points fall back to the material, then to the pool.

| material | split | lift coverage | lift width kg | hourly coverage | hourly width kg |
|---|---|---|---|---|---|
| cardboard | time | 73 % | 352 | 78 % | 239 |
| paper | time | 61 % | 282 | 69 % | 182 |
| plastic_film | time | 78 % | 204 | 71 % | 113 |
| mixed_waste | time | 72 % | 746 | 81 % | 376 |
| overall | time | 72 % | 348 | 75 % | 211 |
| cardboard | bins | 51 % | 536 | 83 % | 448 |
| paper | bins | 82 % | 733 | 91 % | 338 |
| plastic_film | bins | 91 % | 1,025 | 90 % | 423 |
| mixed_waste | bins | 33 % | 1,138 | 83 % | 687 |
| overall | bins | 63 % | 803 | 86 % | 459 |

Lift coverage more than 5 pp below target: cardboard/time (73 %), paper/time (61 %), mixed_waste/time (72 %), cardboard/bins (51 %), mixed_waste/bins (33 %). Calibration pools all hours of a stratum, while the lift hour is the fullest, hardest hour of a cycle; on unseen machines the calibration machines are also few, so their error scale need not transfer.

![interval coverage](plots/coverage_by_material.png)

## Hourly mass curves

![hourly mass curves](plots/mass_curves_time.png)

## Error breakdowns (lift, selected model)

**Infeed type**

| infeed | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| indoor_shaft | 3.5 | 81 | 5.1 | 9 |
| lidded_hopper | 4.1 | 91 | 11.5 | 31 |
| open_hopper | 3.3 | 131 | 8.1 | 44 |

**Drainage (0 = no, 1 = yes)**

| drainage | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| 0.0 | 3.8 | 219 | 9.8 | 74 |
| 1.0 | 3.0 | 84 | 3.1 | 10 |

**Equipment class**

| equipment_class | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| COMBI | 3.6 | 248 | 9.0 | 84 |
| DUO | 3.5 | 55 | – | – |

**Container size**

| container_size | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| <=14 m3 | 3.8 | 140 | 9.4 | 52 |
| 15-20 m3 | 3.4 | 152 | 8.4 | 32 |
| >20 m3 | 4.2 | 11 | – | – |

**False-full episode in the cycle**

| false_full_in_cycle | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| no | 3.1 | 267 | 8.5 | 74 |
| yes | 7.0 | 36 | 13.3 | 10 |

**Weather in the week before lift**

| week | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| dry (bottom 25 %) | 3.5 | 76 | 7.6 | 22 |
| middle | 3.7 | 150 | 9.7 | 41 |
| wet (top 25 % rain7) | 3.6 | 77 | 9.2 | 21 |

## Learning curve (unseen machines, shared model)

| training machines | **overall** | cardboard | paper | plastic_film | mixed_waste |
|---|---|---|---|---|---|
| 10 | 8.3 | 7.6 | 10.0 | 5.0 | 14.0 |
| 14 | 7.6 | 7.0 | 7.3 | 3.8 | 15.1 |

No size below the full 14 training machines gets within 0.5 pp of the all-machines 7.6 %, so by this rule a pilot needs all 14 and the curve has not flattened yet. The largest gain is from 10 to 14 machines (8.3 → 7.6 %).

![learning curve](plots/learning_curve.png)

## Feature importance (top 5 by gain share)

Materials served by the shared model show the same ranking (one model).

| material | split | model | top features |
|---|---|---|---|
| cardboard | time | per_material | curve_rise_slope_ewm (64 %), p_ewm (24 %), pressure_kg_m3 (4 %), presses_cycle (2 %), fill_ffill (2 %) |
| mixed_waste | time | per_material | presses_cycle (67 %), fill_ffill (23 %), curve_rise_slope_ewm (4 %), pressure_kg_m3 (3 %), p_ewm (1 %) |
| paper | time | shared | pressure_kg_m3 (77 %), naive_kg_m3 (12 %), curve_rise_slope_ewm (4 %), graph_kg_m3 (2 %), p_ewm (1 %) |
| plastic_film | time | per_material | p_ewm (45 %), curve_rise_slope_ewm (26 %), pressure_kg_m3 (23 %), p_last (3 %), presses_cycle (1 %) |
| cardboard | bins | per_material | curve_rise_slope_ewm (58 %), p_ewm (29 %), pressure_kg_m3 (4 %), presses_cycle (3 %), fill_ffill (2 %) |
| mixed_waste | bins | shared | pressure_kg_m3 (74 %), naive_kg_m3 (16 %), curve_rise_slope_ewm (3 %), graph_kg_m3 (2 %), p_ewm (1 %) |
| paper | bins | shared | pressure_kg_m3 (74 %), naive_kg_m3 (16 %), curve_rise_slope_ewm (3 %), graph_kg_m3 (2 %), p_ewm (1 %) |
| plastic_film | bins | per_material | curve_rise_slope_ewm (65 %), pressure_kg_m3 (14 %), p_ewm (14 %), fill_ffill (3 %), p_last (1 %) |

![feature importance time](plots/feature_importance_time.png)

![SHAP summary time](plots/shap_time.png)

![feature importance bins](plots/feature_importance_bins.png)

![SHAP summary bins](plots/shap_bins.png)

## Target check (mean % error at lift < 5 %)

| material | split | mean % at lift | n lifts | < 5 % |
|---|---|---|---|---|
| cardboard | time | 3.6 | 152 | yes |
| paper | time | 3.8 | 51 | yes |
| plastic_film | time | 2.7 | 68 | yes |
| mixed_waste | time | 5.2 | 32 | **no** |
| cardboard | bins | 6.5 | 35 | **no** |
| paper | bins | 9.3 | 11 | **no** |
| plastic_film | bins | 9.4 | 23 | **no** |
| mixed_waste | bins | 14.4 | 15 | **no** |

**Not met, and the likely reasons from the data:**

- **mixed_waste, `time` split (5.2 %)**: the 3 worst lifts carry 30 % of the summed % error; 4 of 32 lifts had a false-full episode in the cycle (9.4 % vs 4.6 % without); the fleet has 2 mixed_waste machine(s) of 25; the shared model scores 4.6 % on test (validation chose the other setup); adding weather did not help (4.2 % with pressure → 4.6 % full shared); systematic bias of -2.1 %.
- **cardboard, `bins` split (6.5 %)**: the error is broad-based (median 6.4 %), not driven by a few outliers; 3 of 35 lifts had a false-full episode in the cycle (8.9 % vs 6.2 % without); the fleet has 13 cardboard machine(s) of 25, at most 10 of them in training; systematic bias of -5.3 %.
- **paper, `bins` split (9.3 %)**: only 11 test lifts on 1 test machine(s), so a few cycles dominate; the median is 3.6 %, so a few large misses pull the mean up; the 3 worst lifts carry 79 % of the summed % error; 2 of 11 lifts had a false-full episode in the cycle (36.4 % vs 3.3 % without); the fleet has 4 paper machine(s) of 25, at most 3 of them in training; the per-material model scores 4.6 % on test (validation chose the other setup); adding weather did not help (6.4 % with pressure → 9.3 % full shared); systematic bias of +4.7 %.
- **plastic_film, `bins` split (9.4 %)**: only 23 test lifts on 2 test machine(s), so a few cycles dominate; the error is broad-based (median 6.9 %), not driven by a few outliers; the 3 worst lifts carry 27 % of the summed % error; the fleet has 6 plastic_film machine(s) of 25, at most 4 of them in training; the shared model scores 3.8 % on test (validation chose the other setup); systematic bias of -6.7 %.
- **mixed_waste, `bins` split (14.4 %)**: only 15 test lifts on 1 test machine(s), so a few cycles dominate; the error is broad-based (median 15.7 %), not driven by a few outliers; the 3 worst lifts carry 30 % of the summed % error; the fleet has 2 mixed_waste machine(s) of 25, at most 1 of them in training; no validation lifts for this material, so its setup choice was not validated; adding weather did not help (12.5 % with pressure → 14.4 % full shared); systematic bias of -10.9 %.
