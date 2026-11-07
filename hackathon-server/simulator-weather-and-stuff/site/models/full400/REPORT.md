# Hydraulic soft sensor - container mass report (`full400`)

On the `time` (same machines, later months) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **3.6 %** (median 2.8 %, 75 % of lifts within 5 %, n = 4958), against 29.7 % for the naive fill × nominal density estimate; 4 of 4 materials meet the < 5 % target. The calibrated p10–p90 interval covers 76 % of lift masses (target 80 %). On the `bins` (unseen machines) split the selected soft sensor estimates the mass in the hour before emptying with a mean error of **4.7 %** (median 3.9 %, 61 % of lifts within 5 %, n = 1260), against 28.5 % for the naive fill × nominal density estimate; 3 of 4 materials meet the < 5 % target (missing: paper). The calibrated p10–p90 interval covers 76 % of lift masses (target 80 %).

> **All data is synthetic** (simulator output for the Europress hackathon). The numbers demonstrate the method, not field performance.

![mean % error at lift by material](plots/lift_error_by_material.png)

## Compute

| item | value |
|---|---|
| training wall time (all splits) | 555 s |
| feature build | 21.8 s |
| peak memory (RSS) | 3.43 GB |
| hourly rows / machines | 3,504,000 / 400 |
| split `time` wall time | 214 s |
| split `bins` wall time | 319 s |
| prediction run | 3,504,000 rows in 62.2 s (features + predict 61.0 s) |
| prediction cost | 17.4 µs per machine-hour |
| prediction peak memory | 3.36 GB |

## Split `time` (same machines, later months)

Same machines, trained on the first 75 % of time and tested on the last 25 %. Training machines: 400, test machines: 400, test from 2026-07-01 17:15:00+03:00. Rows: train 2,070,009, val 262,800, cal 262,800, test 876,000.

Selected setup: cardboard → **per_material**, paper → **per_material**, plastic_film → **per_material**, mixed_plastic → **per_material**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 2528 | 104 | 3.6 | 2.8 | 74 % | 96 % | -31 | 76 % | 353 |
| paper | 720 | 121 | 3.9 | 3.2 | 72 % | 95 % | -26 | 77 % | 408 |
| plastic_film | 1231 | 55 | 3.4 | 2.6 | 78 % | 96 % | -8 | 76 % | 186 |
| mixed_plastic | 479 | 61 | 3.3 | 2.5 | 81 % | 95 % | -15 | 71 % | 181 |
| **overall** | 4958 | 90 | 3.6 | 2.8 | 75 % | 96 % | -23 | 76 % | 303 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 74 | 6.0 | 80 % |
| paper | 87 | 6.5 | 80 % |
| plastic_film | 41 | 5.4 | 79 % |
| mixed_plastic | 43 | 5.3 | 78 % |
| overall | 65 | 5.9 | 79 % |

![predicted vs true at lift, time](plots/pred_vs_true_time.png)

## Split `bins` (unseen machines)

Unseen machines (25 % held out, stratified by material), tested on the last 25 % of the period. Training machines: 240, test machines: 100, test from 2026-07-01 17:15:00+03:00. Rows: train 1,556,747, val 200,818, cal 188,500, test 219,000.

Selected setup: cardboard → **per_material**, paper → **shared**, plastic_film → **per_material**, mixed_plastic → **per_material**.

**At lift (hour before emptying vs weighbridge):**

| material | n | MAE kg | mean % | median % | within 5 % | within 10 % | bias kg | coverage | width kg |
|---|---|---|---|---|---|---|---|---|---|
| cardboard | 631 | 128 | 4.7 | 3.9 | 59 % | 92 % | -31 | 80 % | 440 |
| paper | 189 | 178 | 5.3 | 4.6 | 56 % | 87 % | -23 | 78 % | 578 |
| plastic_film | 320 | 65 | 4.2 | 3.3 | 68 % | 95 % | -4 | 72 % | 191 |
| mixed_plastic | 120 | 100 | 4.7 | 4.2 | 61 % | 92 % | -1 | 61 % | 245 |
| **overall** | 1260 | 117 | 4.7 | 3.9 | 61 % | 92 % | -20 | 76 % | 379 |

**Hourly (every test hour):**

| material | MAE kg | mean % | coverage |
|---|---|---|---|
| cardboard | 83 | 7.0 | 85 % |
| paper | 120 | 8.1 | 73 % |
| plastic_film | 49 | 6.4 | 79 % |
| mixed_plastic | 59 | 6.6 | 82 % |
| overall | 78 | 7.0 | 81 % |

![predicted vs true at lift, bins](plots/pred_vs_true_bins.png)

## Comparison ladder (mean % error at lift)

Each step adds signals: naive fill × nominal density → fill + press counts (LightGBM) → + hydraulic pressure → + weather (full model, shared across materials); then the full per-material models and the setup selected per material on validation.

**`time` (same machines, later months)**

| step | cardboard | paper | plastic_film | mixed_plastic | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 26.8 | 28.6 | 34.1 | 35.3 | 29.7 |
| fill + presses | 5.8 | 6.0 | 6.2 | 5.3 | 5.9 |
| + pressure | 3.8 | 4.2 | 3.6 | 3.7 | 3.8 |
| + weather (full, shared) | 3.7 | 4.1 | 3.7 | 3.7 | 3.8 |
| full, per material | 3.6 | 3.9 | 3.4 | 3.3 | 3.6 |
| selected | 3.6 | 3.9 | 3.4 | 3.3 | 3.6 |

**`bins` (unseen machines)**

| step | cardboard | paper | plastic_film | mixed_plastic | **overall** |
|---|---|---|---|---|---|
| naive fill x density | 26.0 | 27.3 | 36.5 | 21.9 | 28.5 |
| fill + presses | 6.4 | 7.2 | 8.7 | 6.7 | 7.1 |
| + pressure | 4.7 | 5.2 | 4.5 | 5.7 | 4.8 |
| + weather (full, shared) | 4.7 | 5.3 | 4.6 | 6.0 | 4.9 |
| full, per material | 4.7 | 5.5 | 4.2 | 4.7 | 4.7 |
| selected | 4.7 | 5.3 | 4.2 | 4.7 | 4.7 |

![comparison ladder](plots/ladder.png)

## Per-material vs shared model

Setup is chosen per material on the validation lifts (mean % error); `–` means no validation lifts of that material, in which case the shared model is kept.

| material | split | val shared | val per-material | test shared | test per-material | selected | better on test |
|---|---|---|---|---|---|---|---|
| cardboard | time | 3.4 | 3.3 | 3.7 | 3.6 | per_material | per_material |
| paper | time | 3.6 | 3.5 | 4.1 | 3.9 | per_material | per_material |
| plastic_film | time | 3.4 | 3.0 | 3.7 | 3.4 | per_material | per_material |
| mixed_plastic | time | 3.5 | 3.2 | 3.7 | 3.3 | per_material | per_material |
| cardboard | bins | 4.5 | 4.4 | 4.7 | 4.7 | per_material | shared |
| paper | bins | 6.6 | 7.3 | 5.3 | 5.5 | shared | shared |
| plastic_film | bins | 5.0 | 4.8 | 4.6 | 4.2 | per_material | per_material |
| mixed_plastic | bins | 3.1 | 3.0 | 6.0 | 4.7 | per_material | per_material |

## Interval coverage (target 80 %)

Intervals come from LightGBM quantile models (p10/p90) calibrated by **normalised conformalised quantile regression (CQR)**: on a separate calibration slice (machines/hours used neither for training nor for validation) the score max(q_lo − y, y − q_hi) / width is computed and the interval is widened by its finite-sample 80 % quantile. Calibration is **Mondrian** by material × fill bucket (fill edges 50.0, 80.0 %); strata with fewer than 30 calibration points fall back to the material, then to the pool.

| material | split | lift coverage | lift width kg | hourly coverage | hourly width kg |
|---|---|---|---|---|---|
| cardboard | time | 76 % | 353 | 80 % | 253 |
| paper | time | 77 % | 408 | 80 % | 290 |
| plastic_film | time | 76 % | 186 | 79 % | 139 |
| mixed_plastic | time | 71 % | 181 | 78 % | 144 |
| overall | time | 76 % | 303 | 79 % | 219 |
| cardboard | bins | 80 % | 440 | 85 % | 320 |
| paper | bins | 78 % | 578 | 73 % | 348 |
| plastic_film | bins | 72 % | 191 | 79 % | 165 |
| mixed_plastic | bins | 61 % | 245 | 82 % | 206 |
| overall | bins | 76 % | 379 | 81 % | 274 |

Lift coverage more than 5 pp below target: mixed_plastic/time (71 %), plastic_film/bins (72 %), mixed_plastic/bins (61 %). Calibration pools all hours of a stratum, while the lift hour is the fullest, hardest hour of a cycle; on unseen machines the calibration machines are also few, so their error scale need not transfer.

![interval coverage](plots/coverage_by_material.png)

## Hourly mass curves

![hourly mass curves](plots/mass_curves_time.png)

## Error breakdowns (lift, selected model)

**Infeed type**

| infeed | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| indoor_shaft | 3.5 | 1633 | 4.6 | 290 |
| lidded_hopper | 3.7 | 1203 | 4.7 | 444 |
| open_hopper | 3.5 | 2122 | 4.7 | 526 |

**Drainage (0 = no, 1 = yes)**

| drainage | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| 0.0 | 3.6 | 3568 | 4.7 | 865 |
| 1.0 | 3.6 | 1390 | 4.6 | 395 |

**Equipment class**

| equipment_class | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| COMBI | 3.6 | 3538 | 4.6 | 949 |
| DUO | 3.4 | 1420 | 5.0 | 311 |

**Container size**

| container_size | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| <=14 m3 | 3.7 | 2305 | 5.0 | 568 |
| 15-20 m3 | 3.5 | 2128 | 4.2 | 594 |
| >20 m3 | 3.3 | 525 | 5.5 | 98 |

**False-full episode in the cycle**

| false_full_in_cycle | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| no | 3.2 | 4378 | 4.4 | 1113 |
| yes | 6.6 | 580 | 7.0 | 147 |

**Weather in the week before lift**

| week | time mean % | time n | bins mean % | bins n |
|---|---|---|---|---|
| dry (bottom 25 %) | 3.6 | 1257 | 4.7 | 319 |
| middle | 3.5 | 2438 | 4.6 | 624 |
| wet (top 25 % rain7) | 3.6 | 1263 | 4.9 | 317 |

## Learning curve (unseen machines, shared model)

| training machines | **overall** | cardboard | paper | plastic_film | mixed_plastic |
|---|---|---|---|---|---|
| 10 | 7.6 | 6.8 | 10.4 | 7.8 | 7.3 |
| 25 | 6.5 | 5.7 | 8.3 | 6.9 | 7.3 |
| 50 | 5.9 | 5.4 | 6.7 | 5.9 | 7.2 |
| 100 | 5.4 | 5.3 | 7.0 | 4.7 | 5.7 |
| 240 | 5.0 | 4.9 | 5.5 | 4.5 | 6.1 |

A pilot needs about **100 machines**: the smallest size whose error on unseen machines is within 0.5 pp of the all-machines value (5.0 %). The largest gain is from 10 to 25 machines (7.6 → 6.5 %).

![learning curve](plots/learning_curve.png)

## Feature importance (top 5 by gain share)

Materials served by the shared model show the same ranking (one model).

| material | split | model | top features |
|---|---|---|---|
| cardboard | time | per_material | p_max_cycle (56 %), p_last (19 %), pressure_kg_m3 (11 %), fill_max_cycle (6 %), fill_ffill (4 %) |
| mixed_plastic | time | per_material | presses_cycle (64 %), p_max_cycle (20 %), p_last (7 %), pressure_kg_m3 (5 %), naive_kg_m3 (2 %) |
| paper | time | per_material | p_max_cycle (53 %), p_last (21 %), pressure_kg_m3 (10 %), presses_cycle (9 %), fill_max_cycle (3 %) |
| plastic_film | time | per_material | p_max_cycle (57 %), p_last (12 %), pressure_kg_m3 (9 %), p_ewm (8 %), fill_max_cycle (7 %) |
| cardboard | bins | per_material | p_max_cycle (50 %), p_last (20 %), pressure_kg_m3 (15 %), fill_max_cycle (5 %), fill_ffill (4 %) |
| mixed_plastic | bins | per_material | presses_cycle (64 %), p_max_cycle (19 %), p_last (7 %), pressure_kg_m3 (7 %), naive_kg_m3 (2 %) |
| paper | bins | shared | pressure_kg_m3 (37 %), naive_kg_m3 (31 %), rho_p_smooth (19 %), p_max_cycle (8 %), p_last (2 %) |
| plastic_film | bins | per_material | p_max_cycle (59 %), p_last (10 %), p_ewm (10 %), pressure_kg_m3 (7 %), fill_max_cycle (4 %) |

![feature importance time](plots/feature_importance_time.png)

![SHAP summary time](plots/shap_time.png)

![feature importance bins](plots/feature_importance_bins.png)

![SHAP summary bins](plots/shap_bins.png)

## Target check (mean % error at lift < 5 %)

| material | split | mean % at lift | n lifts | < 5 % |
|---|---|---|---|---|
| cardboard | time | 3.6 | 2528 | yes |
| paper | time | 3.9 | 720 | yes |
| plastic_film | time | 3.4 | 1231 | yes |
| mixed_plastic | time | 3.3 | 479 | yes |
| cardboard | bins | 4.7 | 631 | yes |
| paper | bins | 5.3 | 189 | **no** |
| plastic_film | bins | 4.2 | 320 | yes |
| mixed_plastic | bins | 4.7 | 120 | yes |

**Not met, and the likely reasons from the data:**

- **paper, `bins` split (5.3 %)**: the error is broad-based (median 4.6 %), not driven by a few outliers; 19 of 189 lifts had a false-full episode in the cycle (8.8 % vs 4.9 % without); the fleet has 60 paper machine(s) of 400, at most 45 of them in training.
