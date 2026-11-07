# Prompt: integrate the compactor "hydraulic soft sensor" into the dashboard

> Paste everything below into the Claude session that works on the dashboard project.

---

You are integrating an existing, already-trained machine-learning model and its simulator data into
**our dashboard project**. Everything below describes what exists, where it lives and how it
works. **Before you write any integration code, ask me the clarifying questions listed in the
section "Ask before you build"** (plus any others you need). Don't guess the dashboard's stack,
data source or hosting.

## 1. What this is

Europress × Since AI Hackathon 2026. A **hydraulic soft sensor** for waste compactors: it estimates
the **mass of waste (kg) inside a compactor container every hour**, from signals the machine already
has. Those signals are the fill level (which the machine itself estimates from ram back pressure),
press counts, peak ram pressure, the per-stroke pressure graph, oil temperature and public weather.
The value one hour before each emptying ("lift") is what a customer compares with the transporter's
weighbridge ticket. Each prediction comes with a calibrated **p10–p90 interval**.

**All data is synthetic** (a physics-based simulator). Nothing represents real Europress data or
real Europress pressure settings. The dashboard should say so wherever it shows these numbers.

## 2. Where everything is

Machine: host `hackathon` (Tailscale IP `100.87.158.27`). Project root:
`/home/hackathon/simulator-weather-and-stuff/`. Python 3.13 venv at `.venv/` (numpy 2.5,
pandas 3.1, pyarrow 26, LightGBM 4.7, matplotlib 3.11, PyYAML 6). Always run Python as
`.venv/bin/python` from the project root.

| path | what |
|---|---|
| `compactor_sim/` | simulator package (`python -m compactor_sim`) |
| `config.yaml` | every simulator parameter (fleet, weather, hydraulics, sensors, operations) |
| `runs/full400/` | simulated dataset: 400 machines × 365 days (2025-10-01 … 2026-09-30, Europe/Helsinki) |
| `runs/bins25/` | small 25-machine dataset (same format), handy for development |
| `weight_train/` | soft-sensor package: features, training, prediction, report (`python -m weight_train`) |
| `models/full400/` | **the trained model for the 400-machine run** (+ metrics, report, predictions) |
| `models/bins25/` | model trained on the 25-machine run (dev/testing) |
| `README.md` | simulator documentation (model, assumptions, machine behaviour, validation) |
| `weight_train/README.md` | soft-sensor documentation (method, every feature in one line, licences) |
| `models/full400/REPORT.md` | full evaluation report with tables and plots |
| `make_site.py`, `site_*.py`, `site/` | existing static results website (served at `http://100.87.158.27:8765/`) |
| `validate.py`, `baseline.py` | simulator sanity report / quick baseline |
| `tests/` | pytest suite (`.venv/bin/python -m pytest -q`) |

### Simulator dataset files (`runs/full400/`)
| file | rows | content |
|---|---|---|
| `hourly.parquet` | 3,504,000 | one row per machine-hour (see columns below) |
| `bins.parquet` | 400 | machine attributes **including hidden truth** (density_factor, sensor biases, …) |
| `lifts.parquet` | ~20,300 | one row per emptying: lift/order time, trigger, true removed mass split by water pathway, `weighbridge_net_kg`, tare, gross |
| `strokes.parquet` | ~5.7 M | one row per ram stroke: peak pressure, duration, energy, pressure-graph features |
| `pressure_curves.parquet` | ~1.1 M | raw pressure graphs (16 points along the ram stroke) for the first 5 machines |
| `weather_daily.parquet` | 1,965 | per region and day (incl. 28 burn-in days before the start) |
| `summary.json`, `config_used.yaml`, `validate_report.txt`, `plots/` | | run summary, exact config, sanity checks |

`hourly.parquet` columns:
- **Device / known inputs**: `bin_id` (str, `BIN-0001`…), `ts` (timestamp[ns, Europe/Helsinki], hour start), `material` (`cardboard|paper|plastic_film|mixed_waste`), `equipment_class` (`COMBI|DUO`), `container_volume_m3`, `region` (`UUS|VAR|PIR|POP|LAP`), `infeed` (`open_hopper|lidded_hopper|indoor_shaft`), `drainage` (bool), `temp_c`, `rh_pct` and `precip_mm_day` (that day's mean/total), `fill_pct` (firmware estimate from back pressure, NaN on dropout), `presses`, `peak_pressure_bar` (NaN without a stroke), `lift_event` (1 = emptied at the start of this hour), `oil_temp_c`, `energy_kwh`, `precip_mm` (hourly), `snow_mm_day`.
- **Pressure graph (hourly mean over strokes)**: `curve_contact_pos`, `curve_rise_slope_bar`, `curve_mean_bar`, `curve_completion`.
- **Truth (evaluation only, never model inputs)**: `true_mass_kg` (the label), `true_fill_pct`, `true_density_kg_m3`, `true_moisture_extra`, `true_water_*_kg`, `true_free_water_kg`, `true_ice_kg`, `true_false_full`, `lifted_mass_kg`, `side_waste_kg`, `ref_scale_kg`.

### Trained model (`models/full400/`)
| path | what |
|---|---|
| `time/` | **deployable bundle "same machines, later months"** (pilot fleet). `predict` uses it by default |
| `bins/` | bundle validated on **unseen machines** ("new installation" case) |
| `<split>/bundle.json` | model manifest: model selection per material, conformal calibration, pressure-inversion constants, feature lists |
| `<split>/*.txt` | LightGBM text models named `<setup>__<material\|all>__<point\|q_lo\|q_hi>.txt` |
| `<split>/test_predictions.parquet` | test-period predictions vs truth (y_kg, pred_kg, lo_kg, hi_kg, is_lift, material, bin_id, ts, …) |
| `<split>/shap_<material>.parquet` | SHAP values for explanations |
| `predictions.parquet` | **hourly predictions for all 400 machines × 1 year**: `bin_id, ts, material, mass_pred_kg, mass_p10_kg, mass_p90_kg` |
| `metrics.json` | every evaluation number (per split, per material, ladder, breakdowns, learning curve, feature importance, compute) |
| `comparison.csv`, `learning_curve.csv`, `feature_list.json`, `plots/*.png`, `REPORT.md`, `predict_stats.json` | evaluation artefacts |

Ignore any `*mixed_plastic*` files in the bundle folders. They are leftovers from an older
material set and are not referenced by `bundle.json`.

## 3. How the model works (short)

1. **Input**: hourly rows per machine, **contiguous and sorted by `bin_id`, `ts`**, with the device
   columns above (truth columns are ignored even if present; there is a whitelist plus a leakage guard).
2. **Features** (`weight_train/features.py`, one function `build_features(hourly, inverter, strokes=None)`
   used for training and prediction). They are backward-looking only; a *cycle* starts at each
   `lift_event`. They cover hours since the lift, forward-filled and maximum fill, presses since the
   lift, peak-pressure statistics, a pressure-implied density (physics inversion), pressure-graph
   features, oil temperature, weather of *completed* days (rain d1…d7, RH), machine configuration
   and calendar.
3. **Model**: LightGBM. The target is **kg per m³ of container**, multiplied back by the volume. Per
   material the bundle picks a per-material or shared model. p10/p90 quantile models are widened by
   conformal calibration (target 80 % coverage).
4. **Output**: `mass_pred_kg`, `mass_p10_kg`, `mass_p90_kg` per machine-hour.
5. Rows in a machine's **first, incomplete cycle** in the data have incomplete "since lift"
   features and are less accurate.

### Performance (`models/full400/metrics.json`)
| | same machines, later months (`time`) | unseen machines (`bins`) |
|---|---|---|
| mean % error at lift | **3.75 %** (cardboard 4.0, paper 4.0, film 3.3, mixed waste 3.1) | 5.26 % (cardboard 5.2, paper 5.4, film 4.7, mixed waste 6.7) |
| lifts within 5 % | 73 % | 55 % |
| p10–p90 coverage at lift (target 80 %) | 78 % | 77 % (mixed waste only 31 %) |
| hourly MAE | 66 kg | 90 kg |

Naive "fill × nominal density" has about 28–32 % error. Inference cost is about **20 µs per
machine-hour** including features (3.5 M rows in about 71 s, about 4 GB peak RAM). Training takes
about 13 min on this server (16–36 cores).

## 4. How to run it

```bash
cd /home/hackathon/simulator-weather-and-stuff
# batch prediction (input may lack true_ columns; strokes.parquet next to the input is used if present)
.venv/bin/python -m weight_train predict --models models/full400 --input runs/full400/hourly.parquet \
    --output /path/predictions.parquet [--split time|bins]
# regenerate data (deterministic per seed) / retrain / rebuild report
.venv/bin/python -m compactor_sim --bins 400 --days 365 --seed 7 --out runs/full400
.venv/bin/python -m weight_train train --data runs/full400 --out models/full400
.venv/bin/python -m weight_train report --models models/full400
```

Python API (run with the project root on `PYTHONPATH`):
```python
from pathlib import Path
import pandas as pd
from weight_train.bundle import SoftSensor
from weight_train.predict import predict_hourly          # -> bin_id, ts, material, mass_pred_kg, mass_p10_kg, mass_p90_kg

sensor = SoftSensor.load(Path("models/full400/time"))
hourly = pd.read_parquet("runs/full400/hourly.parquet", filters=[("bin_id", "in", ["BIN-0001", "BIN-0002"])])
pred = predict_hourly(sensor, hourly)                    # strokes=None -> per-stroke stats NaN (slightly less accurate)
```
Features need each machine's history since its last lift and 7 days of weather. When predicting
"now" for a machine, pass at least that machine's last ~30 days of hourly rows, then take the
last row.

## 5. Things the dashboard will probably want

- **Per machine**: hourly mass curve with the p10–p90 band; fill reading vs estimated mass; lifts
  marked from `lift_event` / `lifts.parquet`; at each lift, predicted mass one hour before vs
  `weighbridge_net_kg` (weighbridge check) and vs true mass.
- **Fleet**: error by material, coverage, the comparison ladder (`comparison.csv`), the learning
  curve, feature importance (`metrics.json → feature_importance_gain`), SHAP.
- **Simulator context**: pressure graph examples (`pressure_curves.parquet`), validation plots
  (`runs/full400/plots/`), assumptions and machine behaviour (`README.md`).
- Timestamps are tz-aware **Europe/Helsinki**. Masses in kg, volumes in m³, pressure in bar.

## 6. Rules and caveats

- **Never feed `true_*`, `lifted_mass_kg`, `side_waste_kg`, `ref_scale_kg` or hidden `bins.parquet`
  truth columns into the model.** Use them only to display ground truth or evaluation.
- Don't retrain or regenerate data unless I ask; both overwrite the files above (about 13 min and
  about 1 min). If the dashboard needs fresh data, write to a new folder (`--out runs/<new>`, `--out models/<new>`).
- Leave the running static site server on port 8765 alone.
- Known simulator limitation: 34 of about 20,300 lifts (all mixed waste in 20 m³ DUO containers)
  exceed the ~10 t truck limit (max 11.7 t). A container-size fix is pending.
- Mixed-waste intervals on unseen machines are under-calibrated (31 % coverage). Show the band
  with that caveat.

## 7. Ask before you build

Before writing integration code, ask me (at least):
1. What is the dashboard's tech stack (frontend framework, backend language, database), and where
   does it run (same host, another machine on the Tailscale network, cloud)?
2. Should it **read precomputed files** (`predictions.parquet`, `metrics.json`, …), **call the Python
   model** (import, subprocess, or a small HTTP API we add), or **store results in its own database**?
3. Is the data **static** (this synthetic year) or should it **simulate "live"** (replay hour by hour
   or stream new simulated hours), and at what refresh cadence?
4. Which views and KPIs matter most: per-machine detail, fleet overview, weighbridge check, model
   evaluation, simulator explanation?
5. Which bundle to show by default: `time` (pilot fleet) or `bins` (new installations), or both?
6. How many machines and what time range must the UI handle at once (3.5 M hourly rows is about 200 MB parquet)?
7. Any auth, access or hosting constraints (Tailscale only, public demo, read-only)?
8. Should the "synthetic data" disclaimer and the model caveats appear in the UI, and where?
9. Do you want the dashboard to reuse or replace the existing static site (`site/`, port 8765)?
