# Hydraulic soft sensor — what we built with AI, and the math behind it

*Europress × Since AI Hackathon 2026 (Turku). All data is synthetic; nothing represents real Europress data.*

## 1. The idea

Europress compactors already report **fill level**, **press count** and **ram pressure**. A
*soft sensor* turns those signals (plus weather) into an estimate of the **mass of waste in
the container every hour** — no scale needed — so a customer can check the weight the
transporter reports at the weighbridge. The number that matters most is the estimate
**just before each lift**.

There was no real data, so the work has two parts:

1. **`compactor_sim`** — a physics-motivated simulator producing realistic hourly telemetry
   *and* the true mass (ground truth).
2. **`weight_train`** — the machine-learning pipeline that learns mass from telemetry only
   (finished; deployed model `models/full400`, results in §4).

How the AI was used: Claude (Claude Code) designed the module layout, wrote the simulator,
tests, validation and baseline scripts, ran and calibrated them, and used an independent
AI reviewer agent to audit the core code. Background agents handled side tasks
(documentation refresh) in parallel.

---

## 2. The simulator (`compactor_sim`) — done and validated

* 400 machines × 365 days, hourly: 3,504,000 rows + 3.5 M individual ram strokes and 20,281 lifts
  (run `runs/full400`, seed 7).
* All parameters in `config.yaml` (the run's copy is `runs/full400/config_used.yaml`); same seed ⇒ bit-identical output.
* pytest suite in `tests/` (simulator and `weight_train`); mass balance closes to ~2e-9 kg (`validate_report.txt`).
* Four waste streams: cardboard 50 %, paper 15 %, plastic film 25 %, `mixed_waste` 10 % of machines.

### 2.1 Weather (5 Finnish regions, south → north)

* **Temperature:** seasonal sine + AR(1) anomaly, partly shared between regions
  `T(d) = T̄ + A·cos(2π(d − d_warm)/365) + σ(d)·x_d`,  `x_d = φ·x_{d−1} + √(1−φ²)·ε_d`
* **Precipitation:** two-state Markov chain for wet/dry days
  (`p(wet|dry) = π(1−r)`, `p(wet|wet) = π(1−r) + r`, persistence r = 0.35, keeps the wet-day share π),
  gamma-distributed wet-day amounts, spread over showery hours with Dirichlet weights.
* **Snow** below 0 °C; snowpack melts with a degree-day model (3 mm per °C per day).
* **Indoor humidity** from outdoor vapour pressure (Magnus formula)
  `e_sat(T) = 6.112·exp(17.62·T / (243.12 + T))` evaluated at 21 °C → dry indoor air in winter.

### 2.2 Moisture — four pathways, each kept as its own truth column

| pathway | math |
|---|---|
| humidity → fibre | Oswin isotherm `MC% = 5.8·(h/(1−h))^0.30` (7 % at 65 % RH, 14 % at 95 % RH), 24 h memory |
| wet material carried in | a few % of mass × yard wetness index (rain/melt store with 6 h decay) |
| rain into the hopper | `kg water = rain_mm × hopper_area_m²` (1 mm on 1 m² = 1 kg); lid lets in 10 % |
| free water | fibre soaks 30 % (plastics 10 %); rest drains, seeps or pools; freezes below 0 °C |

Wet fibre compacts denser: `ρ × (1 + 0.6·moisture_extra)`. Free water adds mass, not volume.

### 2.3 Compaction (one layer per loading day)

* Log-law: `ρ = ρ_typ · machine_factor · daily_factor · g(P_max)`
  with `g(P) = (1 + c·ln(1 + P/P₀)) / (1 + c·ln(1 + P_ref/P₀))`
  (c = 0.25 cardboard, 0.15 paper, 0.35 film, 0.12 `mixed_waste`).
* Each layer remembers the highest pressure it felt (compaction is plastic).
* Springback: after a stroke the pack relaxes 2–8 % over ~3 h.
* `fill = Σ layer volume / container volume`; what doesn't fit is side waste.

### 2.4 Hydraulics

* `P_peak = min(relief, visc(T_oil) · (P_idle + k · f(fill) · stiffness · (ρ/ρ_typ)^1.0 · softening · frost))`
  (`density_exponent 1.0`: pressure depends about linearly on pack density).
* `f(fill) = clip((fill − 0.07)/0.93, 0, 1)` (`fill_onset 0.07`, `fill_exponent 1.0`): back pressure
  starts at about 7 % fill and rises linearly.
* Cold oil reads higher: `visc = 1 + 0.004·max(40 − T_oil, 0)`; oil warms 0.8 °C per stroke.
* The relief valve (~240 bar) caps pressure — the pack stops densifying when it opens.

### 2.5 Sensors and operations

* Fill sensor: derived from pressure (rolling over ~10 strokes, `sensors.fill_mode: pressure_derived`),
  3 % noise, gain bias (sd 1.5 %, clipped at ±3 %) with drift, **false-full** bridging episodes
  (reads 88–97 % for 1–4 days), 1 % dropouts + outages.
* Pressure transducer: 4 bar noise, 0.5 bar steps, ~2 %/yr drift.
* Order at observed fill ≥ 80/85/90 %; truck 4–30 h later, only 06–18, no Sundays/holidays.

### 2.6 Validation highlights (`runs/full400/validate_report.txt`)

* Mean lift masses inside the target ranges for all four streams: cardboard 3,044 kg, paper 3,390 kg,
  plastic film 1,843 kg, `mixed_waste` 4,856 kg. One warning: the heaviest net lift is 11.7 t,
  above the ~10 t truck limit.
* Pressure separates densities at high fill (correlation 0.73–0.87 per material); below 30 % fill
  the pressure is near idle (median 45 bar).
* Weather effect: open-hopper cardboard 4.4 % heavier after a wet week; indoor shaft −1.4 %.
* 10.2 % of lifts are triggered by false-full readings (mean true fill 52 % vs 88 %; those containers are light).

### 2.7 AI code review → fixes

An independent AI reviewer found no significant correctness bugs, but showed that, before
recalibration, **overflow was the normal case** (44 % of lifts had side waste). We recalibrated the
median time to the order threshold from 4.5 to 8 days (still within the brief's 2–10 days)
and fixed two small labelling issues. In the current run side waste is 2.6 % of inflow
(18 % of lifts carry some).

---

## 3. Baseline ML evidence (current run, `runs/full400/baseline_report.txt`)

LightGBM, 5-fold cross-validation grouped by machine (no memorising a machine), 19,881 lifts:

| features | mean % error per lift |
|---|---|
| fill only | 23.3 % |
| + pressure | 7.2 % |
| + press count | 5.2 % |
| + rain/RH (last 7 days) | 5.2 % |

**Takeaway:** pressure is the big win — it reveals each machine's hidden density and exposes
false-full readings (error on those lifts drops from 80 % to 7 %). Weather adds little on
average. (Earlier figures from before the recalibration, such as 24.4 % → 5.09 %, are superseded.)

---

## 4. The training pipeline (`weight_train`) — finished

* **No leakage:** only device-known columns are whitelisted; `true_*` columns and hidden
  machine parameters are forbidden; today's daily weather totals are excluded (they
  contain future hours).
* **Features** (one function for training and prediction, backward-looking only):
  hours since lift, forward-filled fill, max fill since lift, 24 h fill change, presses
  since lift, pressure statistics, pressure-graph features along the ram stroke, rain for
  each of the last 7 days, rain × infeed exposure, frost days since lift, machine type,
  hour and weekday.
* **Physics-based pressure inversion** (fitted per material on training rows only):
  `P/visc(oil) − 25 bar = k · fill^a · ρ^b`, inverted to an implied density ρ̂.
  The fitted exponent b ≈ 0.9–1.1 recovers the simulator's 1.0 without ever seeing it
  (`models/full400/metrics.json`, `inverter`).
* **Target:** kg per m³ of container, multiplied back by volume (one model for all sizes).
* **Two evaluation splits:** unseen machines (`bins`: 25 % held out, tested on the last 25 % of the
  period) and same machines in later months (`time`); each with separate validation and calibration slices.
* **Models:** shared model vs per-material models, the better one kept per material;
  small tuning grid; monotonic-constraint check.
* **Prediction interval:** p10/p90 quantile models + conformal calibration (normalised CQR,
  stratified by material × fill bucket) targeting 80 % coverage.

**Results** (`models/full400/metrics.json`, error in the hour before each lift):

| split | mean error at lift | within 5 % | coverage of 80 % interval | naive fill × density |
|---|---|---|---|---|
| unseen machines (`bins`, n = 1,221) | **5.3 %** | 55.4 % | 77.1 % | 32.1 % |
| same machines, later months (`time`, n = 4,876) | **3.7 %** | 72.7 % | 78.4 % | 28.3 % |

Known gap: on unseen machines the `mixed_waste` interval is under-calibrated (31 % coverage
instead of 80 %). Full report: `models/full400/REPORT.md`.
