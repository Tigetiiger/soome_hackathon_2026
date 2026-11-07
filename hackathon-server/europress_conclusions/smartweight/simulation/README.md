# SmartWeight simulation

Physics-informed simulation of compactor weighing options. **Every output is SIMULATED under the
assumptions in `params.yaml`. It is not validated real-world performance.**

## Reproduce

```bash
cd europress_conclusions/smartweight/simulation
python3 -m venv .venv && . .venv/bin/activate      # or reuse /home/hackathon/virtual_scale/.venv
pip install -r requirements.txt
python verify_dataset_claims.py   # claims in the Europress dataset docs vs raw data -> results/dataset_checks.json
python run_all.py                 # all estimators, stress tests, ablation, verification power, plots (~3-5 min)
python run_all.py --quick         # 80-machine smoke test (~40 s)
python uncertainty.py             # J Sigma J^T budgets, Monte Carlo check, identifiability counterexamples
python make_comparison.py         # builds ../SENSOR_COMPARISON.csv from results/core_comparison.csv
python health_check.py            # dead/drifting load-cell detection rules -> results/health_check.csv
python sensitivity.py             # break-even multipliers of each 4-cell error term -> results/sensitivity_lc4.*
python audit_cohort.py            # operator-level audit-cohort detection power
```

`verify_dataset_claims.py` needs the Europress v1.0.1 competition pack; pass `--data <path to data/competition/public>`
if it is not at the default location. The other scripts need no input data. Seeds are fixed in `params.yaml`.

## Files

| File | Content |
|---|---|
| `params.yaml` | every physical, sensor and environment parameter, each tagged measured / derived / assumed |
| `costs.yaml` | installed cost per configuration with price tags (L listed, E estimate, A assumption) |
| `world.py` | machines (COMBI/DUO), compaction law, pickups: true mass, moisture, centre of mass, temperature, snow |
| `sensors.py` | observation models: load cells (4 / 2 rear), strain (bending / shear), hooklift pressure, ram pressure, motor power, fill, weighbridge ticket |
| `estimators.py` | inversions (fill x density, pressure -> density -> mass), ticket-anchor Bayesian gain, gradient boosting, inverse-variance fusion |
| `metrics.py` | MAE, RMSE, bias, P90/P95, share within +-100 kg, +-2 %, +-5 %, breakdowns |
| `run_all.py` | experiments; writes `../results/*.csv|png` |
| `uncertainty.py` | analytic propagation, required accuracy, identifiability |
| `make_comparison.py` | builds the comparison matrix |
| `health_check.py` | sensor-health rules (COM plausibility, cross-check, per-cell share) |
| `sensitivity.py` | how far each load-cell error term can grow before P95 > 2 % / 5 % |

`audit_cohort.py`: operator-level audit cohort, pooled detection power, written to `results/audit_cohort_power.txt`.

## Evaluation design

* 400 machines x 40 pickups. 20 % of machines form a "golden cohort" (reference scale) used only to train the ML
  model and to estimate fusion weights. All metrics are on the other 80 % (unseen machines).
* Ticket-anchored estimators use each machine's first 5 pickups (weighed-tare weighbridge tickets) for calibration;
  those pickups are excluded from evaluation.
* Held-out tests: unseen machine population (wider tolerances), unseen material (ML trained without plastics),
  changed calibration (pressure-sensor drift, load-cell failure and drift), material-mix shift and wet season after
  calibration.
* Verification test: operator overbilling of 0-10 % with a 5 % false-alarm threshold, in two modes (overbilling starts
  after calibration / was present in the anchor tickets).
