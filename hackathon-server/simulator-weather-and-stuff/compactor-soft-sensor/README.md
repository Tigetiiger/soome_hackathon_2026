# Compactor hydraulic soft sensor

**Europress × Since AI Hackathon 2026 (Turku) — submission.**

A waste compactor already measures a lot about itself: how often the ram presses, the peak hydraulic
pressure of each stroke, the pressure along the stroke (the "pressure graph"), the oil temperature,
and a fill level that the firmware estimates from back pressure. What it does not know is **how many
kilograms are inside the container**. Today the customer learns the mass only from the transporter's
weighbridge ticket after the container has been emptied. This project builds a **hydraulic soft
sensor**: a model that estimates the container mass **every hour**, with a calibrated p10–p90 interval,
from signals the machine already has plus public weather. The estimate one hour before each emptying
("lift") is the number a customer can compare with the weighbridge figure.

There are two parts. `compactor_sim/` is a physics-based simulator of a fleet of press containers
(cardboard, paper, plastic film, mixed household waste). It covers weather, inflow, moisture,
compaction, hydraulics, sensor errors and truck logistics, and writes hourly telemetry together with
the ground truth. `weight_train/` is the soft sensor itself: backward-looking features, LightGBM
models of kg per m³, a per-material or shared model chosen on validation, and quantile models widened
by conformal calibration. It is evaluated on both "same machines, later months" and "unseen machines".

> **All data in this folder is synthetic.** Nothing here is real Europress data, and the hydraulic
> parameters are assumptions, not real Europress pressure settings. The results show that the method
> works on a plausible simulated fleet. They are not a measurement of field accuracy.

**Headline (400 simulated machines, 1 year):** mean error of the mass at lift is **3.7 %** on the same
machines in later months and **5.3 %** on machines the model has never seen. The naive estimate
"fill × nominal density" has an error of 28–32 %. Details are under [Results](#results).

---

## Contents

- [Folder layout](#folder-layout)
- [Installation](#installation)
- [Quick start](#quick-start)
- [Command-line reference](#command-line-reference)
- [Runtimes and memory](#runtimes-and-memory)
- [Python API](#python-api)
- [Data formats](#data-formats)
- [The model in brief](#the-model-in-brief)
- [Results](#results)
- [Regenerating everything end to end](#regenerating-everything-end-to-end)
- [Validation and baseline scripts](#validation-and-baseline-scripts)
- [Testing](#testing)
- [Configuration](#configuration)
- [Limitations and known issues](#limitations-and-known-issues)
- [Licences](#licences)

## Folder layout

| path | what |
|---|---|
| `README.md` | this file |
| `docs/SIMULATOR.md` | detailed simulator documentation: physics, every assumption with its source, expert-interview facts, validation results |
| `compactor_sim/` | simulator package (`python -m compactor_sim`) |
| `weight_train/` | soft-sensor package (`python -m weight_train train/predict/report/curve`). [`weight_train/README.md`](weight_train/README.md) describes the method and lists every feature in one line |
| `config.yaml` | every simulator parameter (fleet, weather, moisture, compaction, hydraulics, sensors, operations) |
| `validate.py` | sanity report and plots for a simulator run |
| `baseline.py` | quick LightGBM baseline: fill only vs + pressure vs + weather |
| `tests/` | pytest suite (simulator and soft sensor) |
| `requirements.txt`, `pytest.ini`, `.gitignore` | environment, test config and ignore rules |
| `runs/full400/` | simulated dataset: 400 machines × 365 days (seed 7), with `validate_report.txt`, `baseline_report.txt`/`baseline_results.json` and `plots/` |
| `runs/bins25/` | small dataset with the same format: 25 machines × 365 days, for development |
| `models/full400/` | **trained soft sensor** for `runs/full400`: `time/` and `bins/` bundles, `metrics.json`, [`REPORT.md`](models/full400/REPORT.md), plots, cardboard machines-needed curve |
| `models/bins25/` | soft sensor trained on `runs/bins25` (small dev model, [`REPORT.md`](models/bins25/REPORT.md)) |
| `site/` | technical documentation website (added separately) |

Approximate size: 360 MB. The largest files are `runs/full400/hourly.parquet` (117 MB) and
`runs/full400/strokes.parquet` (101 MB).

## Installation

Requires Python ≥ 3.11 (developed on 3.13). CPU only, no GPU.

```bash
cd compactor-soft-sensor
python -m venv .venv
.venv/bin/pip install -r requirements.txt     # numpy, pandas, pyarrow, pyyaml, matplotlib, lightgbm, pytest
```

Run every command from this folder (the one that contains `config.yaml`). The examples use
`.venv/bin/python`; with an activated venv, plain `python` works too.

## Quick start

```bash
# 1. tests (28 tests, ~30 s)
.venv/bin/python -m pytest -q

# 2. simulate a small fleet (5 machines x 30 days, ~2 s)
.venv/bin/python -m compactor_sim --bins 5 --days 30 --seed 1 --out runs/demo

# 3. predict hourly mass with the shipped 400-machine model (~5 s for 25 machines)
.venv/bin/python -m weight_train predict --models models/full400 \
    --input runs/bins25/hourly.parquet --output runs/bins25_pred.parquet

# 4. train a small model on the 25-machine set (~5 min, 0.7 GB RAM), writes models/demo25/ incl. REPORT.md
.venv/bin/python -m weight_train train --data runs/bins25 --out models/demo25

# 5. rebuild plots + REPORT.md of a trained folder
.venv/bin/python -m weight_train report --models models/demo25
```

Training on 25 machines is only a smoke test. With so few machines the `bins` (unseen-machines)
numbers are noisy.

## Command-line reference

### Simulator: `python -m compactor_sim`

```
python -m compactor_sim [--config PATH] [--bins N] [--days N] [--seed N] [--out DIR] [--no-strokes]
```

| flag | default | meaning |
|---|---|---|
| `--config` | `config.yaml` next to the package | YAML config |
| `--bins` | `run.n_bins` | number of compactors |
| `--days` | `run.days` | days to simulate (after a 28-day burn-in) |
| `--seed` | `run.seed` | random seed. The same seed gives bit-identical output (tested) |
| `--out` | `runs/seed<seed>_<bins>x<days>` | output folder |
| `--no-strokes` | off | skip `strokes.parquet` (smaller, faster). The soft sensor then has NaN per-stroke features |

The command prints a JSON summary: rows, lifts, mean lift mass per material, false-full share and the
mass-balance residual. The folder contents are listed under [Data formats](#data-formats).

### Soft sensor: `python -m weight_train <command>`

**`train`**: train and evaluate, then write a model folder.

```
python -m weight_train train --data RUN_DIR --out MODEL_DIR [--split bins|time|both] [--setup per_material|shared|both] [--seed 7] [--no-report]
```

| flag | default | meaning |
|---|---|---|
| `--data` | required | simulator run folder (`hourly.parquet`; `strokes.parquet` is used if present) |
| `--out` | required | output model folder |
| `--split` | `both` | `time` = same machines, later months (pilot fleet); `bins` = unseen machines (new installations) |
| `--setup` | `both` | train per-material models, one shared model, or both and pick per material on validation |
| `--seed` | 7 | seed (training is deterministic) |
| `--no-report` | off | skip the plots and `REPORT.md` |

**`predict`**: hourly mass and p10/p90 for any hourly table. The input does not need `true_*` columns.

```
python -m weight_train predict --models MODEL_DIR --input HOURLY.parquet --output OUT.parquet [--split time|bins] [--strokes STROKES.parquet]
```

| flag | default | meaning |
|---|---|---|
| `--models` | required | trained folder, e.g. `models/full400` |
| `--input` | required | hourly parquet in the simulator's `hourly.parquet` format |
| `--output` | required | output parquet: `bin_id, ts, material, mass_pred_kg, mass_p10_kg, mass_p90_kg` |
| `--split` | `time` (falls back to `bins`) | which bundle to use |
| `--strokes` | `strokes.parquet` next to the input, if present | per-stroke data for the stroke features |

`predict` also writes `MODEL_DIR/predict_stats.json`: rows, wall time, µs per machine-hour and peak RSS.

The 400-machine prediction file `models/full400/predictions.parquet` (~90 MB) is **not included**.
To regenerate it (~75 s, ~4 GB RAM):

```bash
.venv/bin/python -m weight_train predict --models models/full400 \
    --input runs/full400/hourly.parquet --output models/full400/predictions.parquet
```

**`report`**: rebuild `plots/*.png` and `REPORT.md` from a trained folder.

```
python -m weight_train report --models MODEL_DIR
```

**`curve`**: for one material, error against the number of training machines, using the `bins`
split's settings. It writes `material_curve_<material>.{json,csv}` and `plots/material_curve_<material>.png`.

```
python -m weight_train curve --data RUN_DIR --models MODEL_DIR [--material cardboard] [--sizes 1,2,3,4,6,8,10,12,16,24,32,48,64,96,128]
```

## Runtimes and memory

Measured on the development server (36 cores, 31 GB RAM). The numbers come from
`models/full400/metrics.json → compute`, `predict_stats.json`, `runs/full400/summary.json` and
`models/bins25/metrics.json`.

| task | time | peak RAM |
|---|---|---|
| simulate 400 machines × 365 d (3.5 M hourly rows, 5.7 M strokes) | ~35 s (loop 22 s, strokes 11 s) | a few GB |
| simulate 25 machines × 365 d | ~8 s | small |
| `train` on full400 (both splits, both setups, report) | **~13 min** (798 s) | **~4.1 GB** |
| `train` on bins25 | ~4.6 min (278 s) | 0.7 GB |
| feature building for 3.5 M rows during training | 38 s, parallel over all cores (process pool, split by machine) | |
| `predict` full400 (3.5 M machine-hours) | 72 s; **~20 µs per machine-hour** including features (single process) | ~4.0 GB |
| `predict` bins25 (219 k machine-hours) | ~5 s | 0.5 GB |
| `curve` cardboard (49 fits) | ~5.5 min (332 s) | |
| test suite | ~30 s | |

LightGBM uses all cores (`num_threads=0`). Training is deterministic: the same data and seed give
identical metrics.

## Python API

```python
from pathlib import Path
import pandas as pd
from weight_train.bundle import SoftSensor
from weight_train.predict import predict_hourly

sensor = SoftSensor.load(Path("models/full400/time"))          # or models/full400/bins
hourly = pd.read_parquet("runs/full400/hourly.parquet",
                         filters=[("bin_id", "in", ["BIN-0001", "BIN-0002"])])
strokes = pd.read_parquet("runs/full400/strokes.parquet",
                          columns=["bin_id", "ts", "peak_pressure_bar", "duration_s"],
                          filters=[("bin_id", "in", ["BIN-0001", "BIN-0002"])])
pred = predict_hourly(sensor, hourly, strokes)   # strokes optional (stroke features become NaN, slightly less accurate)
# -> bin_id, ts, material, mass_pred_kg, mass_p10_kg, mass_p90_kg
```

Requirements for the input:

- Pass rows for whole machines, ordered by `bin_id` then `ts`.
- The features look back over the current cycle and 7 days of weather. To estimate "now" for a
  machine, pass at least its last ~30 days of hourly rows and take the last row.
- Hours in a machine's first, incomplete cycle in the data have incomplete "since lift" features and
  are less accurate.

## Data formats

All timestamps are tz-aware **Europe/Helsinki**. Masses are in kg, volumes in m³, pressures in bar.

### Simulator run folder (`runs/<name>/`)

| file | rows (full400) | content |
|---|---|---|
| `hourly.parquet` | 3,504,000 | one row per machine-hour (columns below) |
| `bins.parquet` | 400 | machine and site attributes, **including hidden truth** (`density_factor`, `fill_gain_bias`, `pressure_gain_*`, `relief_bar`, `p_idle_bar`, `k_machine`, `daily_input_kg`, …) |
| `lifts.parquet` | 20,281 | one row per emptying: `ts`, `order_ts`, `trigger`, `false_full_trigger`, fill at order (observed/true), `days_since_last_lift`, `weighbridge_net_kg` (±15 kg, 20 kg steps), the true removed mass split into base / humidity / carried / hopper / free water / ice, `true_mass_removed_kg`, `residue_kg`, tare, gross vehicle load, machine attributes |
| `strokes.parquet` | ~5.7 M | one row per ram stroke: `ts`, `stroke_in_hour`, `oil_temp_c`, `true_peak_bar`, `peak_pressure_bar`, `duration_s`, `energy_kwh`, `curve_*` features |
| `pressure_curves.parquet` | ~1.1 M | raw pressure graphs (16 points along the stroke) for the first 5 machines: `bin_id, ts, stroke_in_hour, ram_position, pressure_bar` |
| `weather_daily.parquet` | 1,965 | per region and day, including the 28 burn-in days: `temp_mean/min/max_c, precip_mm, rain_mm, snow_mm, rh_pct, snow_swe_mm` |
| `summary.json`, `config_used.yaml` | | counts, lift means, mass-balance ledger, timings; the exact config used |
| `validate_report.txt`, `baseline_report.txt`, `baseline_results.json`, `plots/` | | outputs of `validate.py` / `baseline.py` (full400 only) |

`hourly.parquet` columns, grouped by role:

| role | columns |
|---|---|
| **Device / known inputs** (the model may use these) | `bin_id` (`BIN-0001`…), `ts` (hour start), `material` (`cardboard \| paper \| plastic_film \| mixed_waste`), `equipment_class` (`COMBI \| DUO`), `container_volume_m3`, `region` (`UUS \| VAR \| PIR \| POP \| LAP`), `infeed` (`open_hopper \| lidded_hopper \| indoor_shaft`), `drainage`, `fill_pct` (firmware fill estimate derived from back pressure; NaN on dropout), `presses`, `peak_pressure_bar` (NaN without a stroke), `lift_event` (1 = emptied at the start of this hour), `oil_temp_c`, `energy_kwh`, `temp_c`, `rh_pct`, `precip_mm_day`, `precip_mm`, `snow_mm_day` |
| **Pressure-graph features** (hourly mean over strokes) | `curve_contact_pos` (ram position where pressure starts rising, i.e. the pack face), `curve_rise_slope_bar` (rise slope to the peak), `curve_mean_bar` (mean pressure over the stroke), `curve_completion` (share of travel before the relief valve opened) |
| **Truth: evaluation only, never model inputs** | `true_mass_kg` (**the label**: mass in machine at hour end), `true_fill_pct`, `true_density_kg_m3`, `true_moisture_extra`, `true_water_humidity_kg`, `true_water_carried_kg`, `true_water_hopper_kg`, `true_free_water_kg`, `true_ice_kg`, `true_false_full`, `lifted_mass_kg`, `side_waste_kg`, `ref_scale_kg` (load cell on ~5 % of machines) |

Lift timing convention: the lift happens at the start of the `lift_event` hour, so that row's
`true_mass_kg` is the mass after the lift. The row one hour earlier holds the mass that was lifted.
[`docs/SIMULATOR.md`](docs/SIMULATOR.md) documents every column.

### Model folder (`models/<run>/`)

| path | content |
|---|---|
| `time/`, `bins/` | one deployable **bundle** per split. `predict` uses `time` (pilot fleet) by default; `bins` is the bundle validated on unseen machines |
| `<split>/bundle.json` | manifest: the model list with features, parameters and best iteration; the per-material setup selection; pressure-inversion constants; Mondrian conformal calibration; info (nominal densities, feature sets) |
| `<split>/<setup>__<material\|all>__<point\|q_lo\|q_hi>.txt` | LightGBM text models. Only those listed in `bundle.json` are shipped |
| `<split>/test_predictions.parquet` | test-period predictions vs truth: `y_kg, pred_kg, lo_kg, hi_kg, is_lift, material, bin_id, ts, false_full_in_cycle`, machine attributes, `fill_ffill`, `rain_mm_d1..7` |
| `<split>/shap_<material>.parquet` | exact TreeSHAP values (`shap__<feature>`) at test lifts |
| `metrics.json` | every evaluation number: per split, per material, lift and hourly, ladder, breakdowns, learning curve, feature importance, compute |
| `comparison.csv`, `learning_curve.csv`, `feature_list.json` | comparison ladder, learning curve, feature sets |
| `plots/*.png`, `REPORT.md` | figures and the full written report |
| `predict_stats.json` | timing of the last `predict` run (full400) |
| `material_curve_cardboard.{json,csv}` | cardboard machines-needed curve (full400) |

### Prediction output

`bin_id` (str), `ts` (timestamp, Europe/Helsinki), `material` (str), `mass_pred_kg`, `mass_p10_kg`,
`mass_p90_kg` (float64), one row per input machine-hour.

## The model in brief

[`weight_train/README.md`](weight_train/README.md) has the full method and a table of every feature.

- **Features**: about 46, per machine and hour, backward-looking only. A cycle starts at each lift.
  - Cycle: hours since lift, presses since lift, presses per % fill.
  - Fill: forward-filled reading, maximum since lift, 24 h change, naive kg/m³.
  - Peak pressure: now, last, EWM, maximum, count.
  - Pressure-implied density: an inversion of the hydraulic law fitted per material.
  - Stroke peak and duration, energy, oil temperature.
  - Pressure graph: contact point, rise slope, mean pressure, completion, geometric fill.
  - Weather from completed days only: rain 1–7 days ago, 72 h rain, rain exposure since lift, RH,
    frost days.
  - Machine configuration and hour/weekday.
  - Input columns are whitelisted, and a leakage guard rejects any `true_*` or hidden machine column.
- **Target**: kg per m³ of container, multiplied back by the volume. One model then covers all
  container sizes.
- **Models**: LightGBM.
  - A shared model with `material` as a categorical feature, and per-material models.
  - The setup is chosen **per material on validation**, never on test.
  - A small grid on `num_leaves` × `min_data_in_leaf`, with early stopping.
  - Optional monotone constraints on fill and presses.
  - Pre-lift hours get weight 5.
- **Uncertainty**: p10/p90 quantile models, widened by **normalised conformalised quantile
  regression** on a separate calibration slice. The calibration is Mondrian by material × fill bucket,
  with a target coverage of 80 %.
- **Splits** (both reported):
  - `time`: all machines, trained on the first 75 % of the year and tested on the last 25 %.
  - `bins`: 25 % of machines held out (stratified by material), tested on the last 25 % of the year.
  - In both splits, validation and calibration use separate machines and slices.

## Results

Source: [`models/full400/metrics.json`](models/full400/metrics.json). The full report with plots is
[`models/full400/REPORT.md`](models/full400/REPORT.md). The metric is the mean absolute % error of
the estimate in the hour before each lift against the true lifted mass. The test period starts
2026-07-01.

**At lift**

| material | `time` mean % | `time` within 5 % | `time` p10–p90 coverage | `bins` mean % | `bins` within 5 % | `bins` coverage |
|---|---|---|---|---|---|---|
| cardboard | 4.0 | 69 % | 78 % | 5.2 | 55 % | 82 % |
| paper | 4.0 | 69 % | 78 % | 5.4 | 58 % | 86 % |
| plastic film | 3.3 | 78 % | 80 % | 4.7 | 64 % | 82 % |
| mixed waste | 3.1 | 83 % | 77 % | 6.7 | 35 % | **31 %** |
| **overall** | **3.75** (n = 4,876, MAE 110 kg) | 73 % | 78 % | **5.26** (n = 1,221, MAE 166 kg) | 55 % | 77 % |

**Every test hour (not only lifts):** the `time` split has MAE 66 kg (5.2 %) and 79 % coverage. The
`bins` split has MAE 90 kg (6.5 %) and 77 % coverage.

**Comparison ladder, overall mean % at lift, `time` / `bins`:**

| model | `time` | `bins` |
|---|---|---|
| naive fill × nominal density | 28.3 | 32.1 |
| fill + presses (LightGBM) | 5.8 | 7.0 |
| + peak pressure | 4.3 | 5.9 |
| + pressure graph | 4.0 | 5.7 |
| + weather | 4.0 | 5.5 |
| selected per material | 3.7 | 5.3 |

Press counts and hydraulic pressure carry most of the information, the pressure graph adds a little
more, and weather adds very little.

**How many machines are needed?**

- Learning curve on unseen machines, shared model, all materials: 10 machines → 9.7 %, 25 → 7.8 %,
  50 → 6.7 %, 100 → 6.1 %, 240 → 5.6 %. About **100 machines** is enough to come within 0.5 pp of
  using all of them.
- Cardboard only: `material_curve_cardboard.csv`, plot `plots/material_curve_cardboard.png`.
  - Unseen-machine error: 1 machine → 15.3 %, 4 → 8.5 %, 12 → 6.6 %, 24 → 5.7 %, 48 → 5.4 %,
    120 → 5.4 %. The naive estimate is 31.0 %.
  - It levels off at about **25–50 cardboard machines**.
  - On the training machines themselves (later months) the error is 3.3–3.7 % even with a single
    machine. A per-machine pilot is therefore accurate quickly, while generalising to new
    installations needs a few dozen machines.

Target "< 5 % at lift": all four materials meet it on `time`. On `bins` only plastic film meets it;
cardboard (5.2 %) and paper (5.4 %) are just above, and mixed waste (6.7 %) is clearly above.

## Regenerating everything end to end

Everything is deterministic for a given seed. This overwrites the shipped folders, so use new
`--out` names if you want to keep them.

```bash
# data (~35 s + ~8 s)
.venv/bin/python -m compactor_sim --config config.yaml --bins 400 --days 365 --seed 7 --out runs/full400
.venv/bin/python -m compactor_sim --config config.yaml --bins 25  --days 365 --out runs/bins25

# simulator sanity checks and the quick baseline
.venv/bin/python validate.py runs/full400
.venv/bin/python baseline.py runs/full400

# soft sensor (~13 min / ~4 GB, and ~5 min)
.venv/bin/python -m weight_train train --data runs/full400 --out models/full400
.venv/bin/python -m weight_train train --data runs/bins25  --out models/bins25

# full-year predictions, then the cardboard machines-needed curve, then the report
.venv/bin/python -m weight_train predict --models models/full400 --input runs/full400/hourly.parquet --output models/full400/predictions.parquet
.venv/bin/python -m weight_train curve --data runs/full400 --models models/full400 --material cardboard
.venv/bin/python -m weight_train report --models models/full400
```

`runs/bins25` was produced with the config's default seed (`run.seed`). `runs/full400/config_used.yaml`
and `runs/bins25/config_used.yaml` record the exact parameters of the shipped data.

## Validation and baseline scripts

- **`validate.py RUN_DIR`** prints a sanity report for a simulator run and writes plots to
  `RUN_DIR/plots/`. It covers integrity and mass balance, lift masses and intervals, weather against
  Finnish climate targets, the weather effect on lift mass, pressure vs fill, the pressure graph and
  false-full episodes. The shipped output is `runs/full400/validate_report.txt`, and the results are
  summarised in [`docs/SIMULATOR.md`](docs/SIMULATOR.md#validation-results-seed-7-400-bins-365-days-validatepy).
- **`baseline.py RUN_DIR [--folds 5]`** is a quick LightGBM check per lift, with cross-validation
  grouped by machine. Mean % error is 23.3 for fill only, 7.2 with pressure, 5.2 with presses added
  and 5.2 with weather added (`runs/full400/baseline_report.txt`). It is independent of
  `weight_train`.

## Testing

```bash
.venv/bin/python -m pytest -q                              # all 28 tests, ~30 s
.venv/bin/python -m pytest -q tests/test_weight_train.py   # soft sensor only
```

The tests check:

- the simulator: mass balance closes, seed determinism, CLI outputs and columns, FMI weather replay,
  physical ranges;
- the soft sensor: no leakage (scrambling `true_*` or the future changes no earlier feature), the
  `predict` schema without truth columns, and that the same data and seed give the same metrics.

They simulate and train their own tiny datasets in a temp folder and do not need `runs/` or
`models/`.

## Configuration

All simulator parameters are in [`config.yaml`](config.yaml), organised in these sections:

| section | covers |
|---|---|
| `run` | number of machines, days, seed, start date, `write_strokes` |
| `fleet` | material mix, container types and volumes, press models, infeed and drainage |
| `calendar`, `sectors` | holidays, opening hours, seasonal profiles |
| `weather` | synthetic regional weather, or replay of FMI CSV files (`mode: fmi_csv`) |
| `inflow` | event masses and day-to-day variation |
| `moisture` | humidity, carry-in and hopper water |
| `compaction` | density law and springback |
| `hydraulics` | pressure law and pressure graph |
| `sensors` | fill mode, noise, drift, dropouts |
| `operations` | order thresholds and truck logistics |

[`docs/SIMULATOR.md`](docs/SIMULATOR.md) gives every value with its source: the hackathon brief, an
assumption, or the expert interview.

Settings based on the **interview with a Europress expert**:

- **The fill reading comes from pressure only**, not from an ultrasonic sensor
  (`sensors.fill_mode: pressure_derived`). It is a rolling average of back pressure over
  **~10 strokes**, because single strokes spike when a box is crushed on the way in
  (`hydraulics.spikes`). Its accuracy is about 5 %; the simulator gives ≈ 6 pp mean error.
- **Back pressure becomes visible from ~7 % fill** (`hydraulics.fill_onset: 0.07`) and rises
  linearly until the container is full.
- **The ram enters only 20–30 cm** into the container. The pressure graph therefore rises only in
  the last part of the stroke (`hydraulics.curve.ram_ingress_frac`).
- **Fill tells volume; what it says about weight is uncertain.** Pressure depends only moderately on
  pack density (`density_exponent: 1.0`).
- **Mixed household waste replaces mixed plastic** as the fourth material (`mixed_waste`:
  400 kg/m³, compressibility 0.12). It is heavy and compacts less.

Soft-sensor training settings (fractions, grid, quantiles, coverage target, fill buckets) are in
`weight_train/settings.py` (`TrainSettings`). They are also recorded in `metrics.json → settings`.

## Limitations and known issues

- **Synthetic data only.**
  - All parameters of the pressure law, density law, sensor errors and logistics are assumptions or
    brief-level ranges, not real Europress values.
  - The accuracy figures show the method on a plausible fleet. They are not a field guarantee.
  - Real data will need re-training, and probably per-installation calibration.
- **Heavy mixed-waste lifts.** 34 of 20,281 lifts exceed ~10 t (maximum 11.7 t), all of them mixed
  waste in 20 m³ DUO containers. That is above a hook-lift truck's capacity. Restricting mixed waste
  to ≤ 14–17 m³ containers in `fleet.containers` would fix it.
- **Mixed-waste intervals on unseen machines are under-calibrated.** At lift the coverage is 31 %
  (56 % hourly) against an 80 % target, and the bias is −156 kg. There are only 40 mixed-waste
  machines (≤ 30 in training), and the calibration pools all hours while the lift hour is the
  fullest. Treat that band with caution.
- **Unseen machines miss the 5 % target** for cardboard, paper and mixed waste (5.2 / 5.4 / 6.7 %).
  Each machine has a hidden density factor and sensor biases that are hard to infer without its own
  history.
- **False-full episodes** (a jam or bridging that makes the fill reading spuriously high) raise the
  error at lift from 3.5 % to 5.5 % (`time`).
- **Simplifications in the simulator.**
  - Weather is regional (5 points), with no microclimate.
  - Each machine is its own site.
  - There is no pressure gradient along the pack and no partial strokes.
  - Truck logistics are simple.
  - [`docs/SIMULATOR.md`](docs/SIMULATOR.md#limitations) lists all of them.
- **Early cycles.** Predictions in a machine's first, incomplete cycle in the input are less accurate.
- **Large files.** `runs/full400/hourly.parquet` (117 MB) and `runs/full400/strokes.parquet`
  (101 MB) exceed GitHub's 100 MB per-file limit and need Git LFS, or can be regenerated (~35 s).

## Licences

**Project licence: to be decided.** No licence has been chosen for this code yet.

Third-party libraries used:

| library | licence |
|---|---|
| numpy | BSD-3-Clause |
| pandas | BSD-3-Clause |
| pyarrow (Apache Arrow) | Apache-2.0 |
| LightGBM | MIT |
| scikit-learn (in the allowed stack; not imported by this package) | BSD-3-Clause |
| matplotlib | Matplotlib License (PSF-style, BSD-compatible) |
| PyYAML (simulator config) | MIT |
| pytest (tests) | MIT |
