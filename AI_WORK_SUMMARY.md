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
   (in progress).

How the AI was used: Claude (Claude Code) designed the module layout, wrote the simulator,
tests, validation and baseline scripts, ran and calibrated them, and used an independent
AI reviewer agent to audit the core code. Background agents handled side tasks
(documentation refresh) in parallel.

---

## 2. The simulator (`compactor_sim`) — done and validated

* 400 machines × 365 days, hourly: 3.5 M rows + 5.7 M individual ram strokes, ~30 s on a laptop.
* All parameters in `config.yaml`; same seed ⇒ bit-identical output.
* 18 pytest tests pass; per-machine mass balance closes to ~1e-9 kg.

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
  (c = 0.25 cardboard, 0.15 paper, 0.35 film, 0.30 mixed plastic).
* Each layer remembers the highest pressure it felt (compaction is plastic).
* Springback: after a stroke the pack relaxes 2–8 % over ~3 h.
* `fill = Σ layer volume / container volume`; what doesn't fit is side waste.

### 2.4 Hydraulics

* `P_peak = min(relief, visc(T_oil) · (P_idle + k · f(fill) · stiffness · (ρ/ρ_typ)^1.5 · softening · frost))`
* `f(fill) = clip((fill − 0.3)/0.7, 0, 1)^1.6` — at low fill the ram barely touches the pack.
* Cold oil reads higher: `visc = 1 + 0.004·max(40 − T_oil, 0)`; oil warms 0.8 °C per stroke.
* The relief valve (~240 bar) caps pressure — the pack stops densifying when it opens.

### 2.5 Sensors and operations

* Fill sensor: 3 % noise, gain bias ±3 % with drift, **false-full** bridging episodes
  (reads 88–97 % for 1–4 days), 1 % dropouts + outages.
* Pressure transducer: 4 bar noise, 0.5 bar steps, ~2 %/yr drift.
* Order at observed fill ≥ 80/85/90 %; truck 4–30 h later, only 06–18, no Sundays/holidays.

### 2.6 Validation highlights

* Lift masses inside target ranges for cardboard, paper and film; mixed plastic slightly
  above — the brief itself conflicts (DUO-only, ≥ 20 m³, 115 kg/m³ ⇒ ≥ ~1.9 t when full).
* Pressure separates densities at high fill (correlation 0.77–0.94).
* Weather effect: open-hopper cardboard ~4–6 % heavier after a wet week; indoor shaft ~0 %.
* ~6 % of lifts are triggered by false-full readings (those containers are light).

### 2.7 AI code review → fixes

An independent AI reviewer found no significant correctness bugs, but showed that
**overflow was the normal case** (44 % of lifts had side waste). We recalibrated the
median time to the order threshold from 4.5 to 8 days (still within the brief's 2–10 days),
cutting side waste from 9.7 % to ~3.5 % of inflow, and fixed two small labelling issues.

---

## 3. First ML evidence (simulator baseline, before the recalibration)

LightGBM, 5-fold cross-validation grouped by machine (no memorising a machine):

| features | mean % error per lift |
|---|---|
| fill only | 24.4 % |
| + pressure | 6.0 % |
| + press count | 5.1 % |
| + rain/RH (last 7 days) | 5.09 % |

**Takeaway:** pressure is the big win — it reveals each machine's hidden density and exposes
false-full readings (error on those lifts drops from 94 % to 13 %). Weather adds only a little
on top. These numbers predate the recalibration and are being refreshed.

---

## 4. The training pipeline (`weight_train`) — in progress

* **No leakage:** only device-known columns are whitelisted; `true_*` columns and hidden
  machine parameters are forbidden; today's daily weather totals are excluded (they
  contain future hours).
* **Features** (one function for training and prediction, backward-looking only):
  hours since lift, forward-filled fill, max fill since lift, 24 h fill change, presses
  since lift, pressure statistics, rain for each of the last 7 days, rain × infeed exposure,
  frost days since lift, machine type, hour and weekday.
* **Physics-based pressure inversion** (fitted per material on training rows only):
  `log(P/visc − P_idle) = log k + a·log(fill) + b·log(ρ)`, inverted to an implied density ρ̂.
  The fitted exponent b ≈ 1.4–1.6 recovers the simulator's 1.5 without ever seeing it.
* **Target:** kg per m³ of container, multiplied back by volume (one model for all sizes).
* **Two evaluation splits:** unseen machines (25 % held out, tested on the last 25 % of the
  period) and same machines in later months; each with separate validation and calibration slices.
* **Models:** shared model vs per-material models, the better one kept per material;
  small tuning grid; monotonic-constraint check.
* **Prediction interval:** p10/p90 quantile models + conformal calibration (normalised CQR,
  stratified by material × fill bucket) targeting 80 % coverage.
* **Status:** an early test fit on the same-machines split reached ~3.4 % mean error per lift
  (pre-recalibration data). Plots, REPORT.md, tests and the full 400-machine training run
  are next.
