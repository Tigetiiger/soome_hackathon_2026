# Prompt: update the dashboard to the retrained soft-sensor model

> Paste everything below into the Claude session working on the dashboard (`/home/hackathon/europress-dashboard`).

---

The soft-sensor model the dashboard uses has been **retrained**. Please update the dashboard so that
everything it shows comes from the new model files. Before you change anything in the UI copy, ask me
if anything below is unclear.

## What changed in the model (`/home/hackathon/simulator-weather-and-stuff`)

1. **Oil temperature is no longer a model input.** We assume real machines have no oil-temperature
   sensor. `oil_temp_c` is removed from `weight_train`'s input whitelist and from the features: there
   are now **45 features instead of 46**. The pressure-implied density (`rho_p`, `rho_p_smooth`,
   `pressure_kg_m3`) now corrects for oil viscosity using the **air temperature** (`temp_c`). The
   telemetry still *contains* an `oil_temp_c` column, but the model ignores it; a test checks that
   scrambling or removing it changes nothing.
2. **Retrained** `models/full400/` (both bundles, `time/` and `bins/`), plus `models/bins25/`. Regenerated:
   `predictions.parquet` (batch job), `metrics.json`, `comparison.csv`, `learning_curve.csv`,
   `feature_list.json`, `test_predictions.parquet`, `shap_<material>.parquet`, `plots/`, `REPORT.md`,
   `predict_stats.json` and `material_curve_cardboard.{json,csv}`.
   **The simulated data (`runs/full400`, `runs/bins25`) did NOT change.**
3. **New headline numbers** (mean % error at lift; take exact values from `metrics.json`, don't copy these by hand):

   | | same machines, later months (`time`) | unseen machines (`bins`) |
   |---|---|---|
   | overall | 3.80 % (was 3.75) | 5.21 % (was 5.26) |
   | cardboard / paper / film / mixed waste | 4.0 / 4.3 / 3.3 / 3.1 | 5.2 / 5.5 / 4.6 / 6.3 |
   | p10–p90 coverage at lift | 78 % | 78 % (mixed waste 34 %, was 31 %) |
   | hourly MAE | 67 kg | 90 kg |

   The cardboard machines-needed curve on unseen machines is now 14.4 % with 1 machine, 5.7 % with 24
   and 5.3 % with 120 (curve file `models/full400/material_curve_cardboard.json`).

## What to update in the dashboard

1. **`softsensor/engine.py`**: remove `"oil_temp_c"` from `DISPLAY_FEATURES`. The feature frame no
   longer has that column, so the machine page would fail or show nothing. Check for any other place that
   indexes `oil_temp_c` from the feature frame (grep the repo). Showing raw telemetry `oil_temp_c` as
   context is fine only if it's clearly labelled "not used by the model". My preference is to drop it from
   "what the model saw".
2. **Copy and strings**: remove oil temperature from the list of model inputs wherever it is stated:
   - `public/js/sensor/strings.js`: `ss.in.oil_temp_c` in English and Finnish, the "Machine signals" text (`ss.h.f1.d`), and any other mention;
   - `softsensor/__init__.py` docstring and `softsensor/README.md` ("…16-point pressure graph, oil temperature, plus public weather").
   Mention that the pressure correction uses the air temperature.
3. **Hard-coded numbers**: search the UI (`public/`, `strings.js`, HTML, README) for result numbers typed
   in by hand. One example is the Finnish text `ss.h.l6` quoting "5,3 %". Either source them from the
   generated JSON, or update them to the new `metrics.json` values. Do this in both languages.
4. **Regenerate the static data**:
   `/home/hackathon/simulator-weather-and-stuff/.venv/bin/python pipeline/softsensor_data.py`. This rewrites
   `public/data/softsensor/*.json` (evaluation, weighbridge check, explainer) from the new `metrics.json`,
   SHAP and test predictions. If the AI workspace keeps copies (`ai-workspace/data/softsensor/*.json`),
   refresh those the same way.
5. **Restart the model API** so it loads the new bundle and the new `predictions.parquet`:
   `systemctl --user restart europress-softsensor`, or the manual `python -m softsensor` (it's currently
   `inactive` as a systemd unit, so check how it is actually being run). It takes about 12 s to load,
   about 1.8 GB RAM.
6. **Tests**: `/home/hackathon/simulator-weather-and-stuff/.venv/bin/python -m pytest softsensor -q`. Update any
   test that expects `oil_temp_c` or 46 features.

## Verify

- `/meta`, `/fleet?at=…` and `/machines/<BIN>?at=…` return `success: true`. The machine page shows the feature
  list without oil temperature, and its live value still equals the batch value from `predictions.parquet`
  for a few random machine-hours.
- The Model and How-it-works pages show 45 features and the new numbers (3.80 % / 5.21 %, per material as above).
- No UI text or API payload lists oil temperature as a model input.
- Report back what you changed, and any place where numbers were hard-coded.
