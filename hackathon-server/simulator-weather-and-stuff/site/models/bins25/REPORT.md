# Hydraulic soft sensor - container mass report (`bins25`)

On the `time` (same machines, later months) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **3.5 %** (median 2.5 %, 80 % of lifts within 5 %, n = 307), against 25.8 % for the naive fill × nominal density estimate; 3 of 4 materials meet the < 5 % target (missing: mixed_plastic). The calibrated p10–p90 interval covers 71 % of lift masses (target 80 %). On the `bins` (unseen machines) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **5.5 %** (median 3.1 %, 71 % of lifts within 5 %, n = 80), against 37.9 % for the naive fill × nominal density estimate; 2 of 4 materials meet the < 5 % target (missing: plastic_film, mixed_plastic). The calibrated p10–p90 interval covers 56 % of lift masses (target 80 %).

> **All data is synthetic** (simulator output for the Europress hackathon). The numbers demonstrate the method, not field performance.

![mean % error at lift by material](plots/lift_error_by_material.png)

## Compute

| item | value |
|---|---|
| training wall time (all splits) | 153 s |
| feature build | 1.4 s |
| peak memory (RSS) | 0.62 GB |
| hourly rows / machines | 219,000 / 25 |
| split `time` wall time | 77 s |
| split `bins` wall time | 74 s |

## Split `time` (same machines, later months)

Same machines, trained on the first 75 % of time and tested on the last 25 %. Training machines: 25, test machines: 25, test from 2026-07-01 17:15:00+03:00. Rows: train 129,540, val 17,082, cal 15,768, test 54,750.

Selected setup: cardboard → **shared**, paper → **per_material**, plastic_film → **shared**, mixed_plastic → **shared**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 153 | 99 | 3.5 | 3.0 | 79 % | 97 % | -33 | 69 % | 337 |
| paper | 52 | 80 | 2.7 | 1.8 | 85 % | 98 % | -25 | 75 % | 316 |
| plastic_film | 72 | 48 | 2.9 | 2.1 | 82 % | 97 % | -2 | 78 % | 167 |
| mixed_plastic | 30 | 59 | 6.1 | 2.1 | 70 % | 97 % | 1 | 63 % | 144 |
| **overall** | 307 | 80 | 3.5 | 2.5 | 80 % | 97 % | -21 | 71 % | 275 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 63 | 5.4 | 79 % |
| paper | 54 | 5.0 | 86 % |
| plastic_film | 37 | 5.2 | 71 % |
| mixed_plastic | 38 | 6.0 | 78 % |
| overall | 53 | 5.3 | 78 % |

![predicted vs true at lift, time](plots/pred_vs_true_time.png)

## Split `bins` (unseen machines)

Unseen machines (25 % held out, stratified by material), tested on the last 25 % of the period. Training machines: 14, test machines: 7, test from 2026-07-01 17:15:00+03:00. Rows: train 90,744, val 19,473, cal 6,537, test 15,330.

Selected setup: cardboard → **shared**, paper → **per_material**, plastic_film → **shared**, mixed_plastic → **shared**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 33 | 120 | 4.6 | 3.9 | 70 % | 91 % | -8 | 36 % | 199 |
| paper | 11 | 64 | 3.1 | 2.3 | 82 % | 91 % | -43 | 82 % | 326 |
| plastic_film | 25 | 87 | 5.6 | 3.9 | 60 % | 88 % | 29 | 56 % | 284 |
| mixed_plastic | 11 | 68 | 10.7 | 2.1 | 91 % | 91 % | 9 | 91 % | 519 |
| **overall** | 80 | 95 | 5.5 | 3.1 | 71 % | 90 % | 1 | 56 % | 287 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 102 | 8.6 | 61 % |
| paper | 48 | 5.4 | 92 % |
| plastic_film | 74 | 9.6 | 66 % |
| mixed_plastic | 44 | 7.2 | 74 % |
| overall | 78 | 8.2 | 69 % |

![predicted vs true at lift, bins](plots/pred_vs_true_bins.png)

## Comparison ladder (mean % error at lift)

Each step adds signals: naive fill × nominal density → fill + press counts (LightGBM) → + hydraulic pressure → + weather (full model, shared across materials); then the full per-material models and the setup selected per material on validation.

**`time` (same machines, later months)**

| step | cardboard | paper | plastic_film | mixed_plastic | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 22.3 | 16.2 | 32.0 | 46.0 | 25.8 |
| fill + presses | 5.6 | 4.2 | 6.1 | 8.1 | 5.7 |
| + pressure | 3.8 | 2.8 | 2.7 | 6.3 | 3.6 |
| + weather (full, shared) | 3.5 | 2.7 | 2.9 | 6.1 | 3.5 |
| full, per material | 3.2 | 2.7 | 2.7 | 3.4 | 3.0 |
| selected | 3.5 | 2.7 | 2.9 | 6.1 | 3.5 |

**`bins` (unseen machines)**

| step | cardboard | paper | plastic_film | mixed_plastic | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 27.3 | 39.6 | 42.2 | 58.6 | 37.9 |
| fill + presses | 11.6 | 8.5 | 17.8 | 20.5 | 14.3 |
| + pressure | 5.4 | 4.3 | 5.2 | 9.7 | 5.8 |
| + weather (full, shared) | 4.6 | 4.3 | 5.6 | 10.7 | 5.7 |
| full, per material | 5.3 | 3.1 | 7.0 | 6.9 | 5.7 |
| selected | 4.6 | 3.1 | 5.6 | 10.7 | 5.5 |

![comparison ladder](plots/ladder.png)

## Per-material vs shared model

Setup is chosen per material on the validation lifts (mean % error); `–` means no validation lifts of that material, in which case the shared model is kept.

| material | split | val shared | val per-material | test shared | test per-material | selected | better on test |
|---|---|---|---|---|---|---|---|
| cardboard | time | 3.2 | 3.7 | 3.5 | 3.2 | shared | per_material |
| paper | time | 2.3 | 2.3 | 2.7 | 2.7 | per_material | per_material |
| plastic_film | time | 3.0 | 4.5 | 2.9 | 2.7 | shared | per_material |
| mixed_plastic | time | 1.9 | 2.0 | 6.1 | 3.4 | shared | per_material |
| cardboard | bins | 3.1 | 3.5 | 4.6 | 5.3 | shared | shared |
| paper | bins | 11.5 | 10.5 | 4.3 | 3.1 | per_material | per_material |
| plastic_film | bins | 3.5 | 4.2 | 5.6 | 7.0 | shared | shared |
| mixed_plastic | bins | – | – | 10.7 | 6.9 | shared | per_material |

## Interval coverage (target 80 %)

Intervals come from LightGBM quantile models (p10/p90) calibrated by **normalised conformalised quantile regression (CQR)**: on a separate calibration slice (machines/hours used neither for training nor for validation) the score max(q_lo − y, y − q_hi) / width is computed and the interval is widened by its finite-sample 80 % quantile. Calibration is **Mondrian** by material × fill bucket (fill edges 50.0, 80.0 %); strata with fewer than 30 calibration points fall back to the material, then to the pool.

| material | split | lift coverage | lift width kg | hourly coverage | hourly width kg |
|---|---|---|---|---|---|
| cardboard | time | 69 % | 337 | 79 % | 226 |
| paper | time | 75 % | 316 | 86 % | 259 |
| plastic_film | time | 78 % | 167 | 71 % | 100 |
| mixed_plastic | time | 63 % | 144 | 78 % | 114 |
| overall | time | 71 % | 275 | 78 % | 192 |
| cardboard | bins | 36 % | 199 | 61 % | 271 |
| paper | bins | 82 % | 326 | 92 % | 1,132 |
| plastic_film | bins | 56 % | 284 | 66 % | 174 |
| mixed_plastic | bins | 91 % | 519 | 74 % | 162 |
| overall | bins | 56 % | 287 | 69 % | 351 |

Lift coverage more than 5 pp below target: cardboard/time (69 %), mixed_plastic/time (63 %), cardboard/bins (36 %), plastic_film/bins (56 %). Calibration pools all hours of a stratum, while the lift hour is the fullest, hardest hour of a cycle; on unseen machines the calibration machines are also few, so their error scale need not transfer.

Suspiciously wide intervals (wider than the mass itself): paper/bins, fill 0–50 %: mean width 1,932 kg for a mean mass of 576 kg.

![interval coverage](plots/coverage_by_material.png)

## Hourly mass curves

![hourly mass curves](plots/mass_curves_time.png)

## Error breakdowns (lift, selected model)

**Infeed type**

| infeed | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| indoor_shaft | 3.2 | 82 | 6.9 | 8 |
| lidded_hopper | 4.3 | 89 | 7.5 | 26 |
| open_hopper | 3.1 | 136 | 4.2 | 46 |

**Drainage (0 = no, 1 = yes)**

| drainage | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| 0.0 | 3.8 | 220 | 5.8 | 67 |
| 1.0 | 2.7 | 87 | 4.3 | 13 |

**Equipment class**

| equipment_class | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| COMBI | 3.3 | 220 | 4.7 | 69 |
| DUO | 3.9 | 87 | 10.7 | 11 |

**Container size**

| container_size | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| <=14 m3 | 2.6 | 112 | 4.2 | 39 |
| 15-20 m3 | 4.0 | 182 | 6.8 | 41 |
| >20 m3 | 3.7 | 13 | – | – |

**False-full episode in the cycle**

| false_full_in_cycle | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| no | 2.9 | 271 | 3.5 | 70 |
| yes | 8.1 | 36 | 19.8 | 10 |

**Weather in the week before lift**

| week | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| dry (bottom 25 %) | 3.1 | 77 | 3.6 | 20 |
| middle | 2.9 | 152 | 3.8 | 40 |
| wet (top 25 % rain7) | 4.9 | 78 | 10.9 | 20 |

## Learning curve (unseen machines, shared model)

| training machines | **overall** | cardboard | paper | plastic_film | mixed_plastic |
|---|---|---|---|---|---|
| 10 | 7.5 | 6.1 | 4.8 | 7.5 | 14.0 |
| 14 | 5.7 | 4.6 | 4.3 | 5.6 | 10.7 |

Only the full set of 14 training machines gets within 0.5 pp of the final 5.7 %: the curve has not flattened, so a pilot needs at least 14 machines and more would still help.

![learning curve](plots/learning_curve.png)

## Feature importance (top 5 by gain share)

Materials served by the shared model show the same ranking (one model).

| material | split | model | top features |
|---|---|---|---|
| cardboard | time | shared | naive_kg_m3 (38 %), pressure_kg_m3 (36 %), rho_p_smooth (14 %), p_max_cycle (5 %), fill_ffill (2 %) |
| mixed_plastic | time | shared | naive_kg_m3 (38 %), pressure_kg_m3 (36 %), rho_p_smooth (14 %), p_max_cycle (5 %), fill_ffill (2 %) |
| paper | time | per_material | p_max_cycle (48 %), p_ewm (26 %), p_last (8 %), pressure_kg_m3 (6 %), fill_max_cycle (6 %) |
| plastic_film | time | shared | naive_kg_m3 (38 %), pressure_kg_m3 (36 %), rho_p_smooth (14 %), p_max_cycle (5 %), fill_ffill (2 %) |
| cardboard | bins | shared | naive_kg_m3 (39 %), pressure_kg_m3 (35 %), p_last (11 %), rho_p_smooth (7 %), p_max_cycle (3 %) |
| mixed_plastic | bins | shared | naive_kg_m3 (39 %), pressure_kg_m3 (35 %), p_last (11 %), rho_p_smooth (7 %), p_max_cycle (3 %) |
| paper | bins | per_material | p_ewm (55 %), p_max_cycle (28 %), fill_max_cycle (6 %), p_last (5 %), fill_ffill (2 %) |
| plastic_film | bins | shared | naive_kg_m3 (39 %), pressure_kg_m3 (35 %), p_last (11 %), rho_p_smooth (7 %), p_max_cycle (3 %) |

![feature importance time](plots/feature_importance_time.png)

![SHAP summary time](plots/shap_time.png)

![feature importance bins](plots/feature_importance_bins.png)

![SHAP summary bins](plots/shap_bins.png)

## Target check (mean % error at lift < 5 %)

| material | split | mean % at lift | n lifts | < 5 % |
|---|---|---|---|---|
| cardboard | time | 3.5 | 153 | yes |
| paper | time | 2.7 | 52 | yes |
| plastic_film | time | 2.9 | 72 | yes |
| mixed_plastic | time | 6.1 | 30 | **no** |
| cardboard | bins | 4.6 | 33 | yes |
| paper | bins | 3.1 | 11 | yes |
| plastic_film | bins | 5.6 | 25 | **no** |
| mixed_plastic | bins | 10.7 | 11 | **no** |

**Not met, and the likely reasons from the data:**

- **mixed_plastic, `time` split (6.1 %)**: the median is 2.1 %, so a few large misses pull the mean up; the 3 worst lifts carry 62 % of the summed % error; 4 of 30 lifts had a false-full episode in the cycle (27.7 % vs 2.7 % without); the fleet has 2 mixed_plastic machine(s) of 25; the per-material model scores 3.4 % on test (validation chose the other setup); systematic bias of +2.4 %.
- **plastic_film, `bins` split (5.6 %)**: only 25 test lifts on 2 test machine(s), so a few cycles dominate; the median is 3.9 %, so a few large misses pull the mean up; the 3 worst lifts carry 42 % of the summed % error; 2 of 25 lifts had a false-full episode in the cycle (24.2 % vs 4.0 % without); the fleet has 6 plastic_film machine(s) of 25, at most 4 of them in training.
- **mixed_plastic, `bins` split (10.7 %)**: only 11 test lifts on 1 test machine(s), so a few cycles dominate; the median is 2.1 %, so a few large misses pull the mean up; the 3 worst lifts carry 90 % of the summed % error; 3 of 11 lifts had a false-full episode in the cycle (33.8 % vs 2.1 % without); the fleet has 2 mixed_plastic machine(s) of 25, at most 1 of them in training; no validation lifts for this material, so its setup choice was not validated; systematic bias of +7.5 %.
