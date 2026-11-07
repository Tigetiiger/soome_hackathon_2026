# Virtual Scale: Assumptions and Exceptions

_Europress × Since AI Hackathon 2026 · project `virtual_scale/` · written 2026-11-07_

This file lists every assumption behind the simulated sensor data, the density rig and the mass models,
and every known exception: situations the method does not handle, or handles only partly.
**Everything is synthetic.** No number here is measured on a real Europress machine.

Tags used below and in `config/sensor_sim.yaml`:
**[pack]** taken from the Europress synthetic data pack · **[est]** our engineering estimate ·
**[hyp]** modelling hypothesis that a real pilot must test · **[unsolved]** known gap with no solution yet.

---

## 1. Unsolved exceptions (read these first)

### 1.1 Wet cardboard (or paper) that freezes [unsolved]

**What happens in reality.** Cardboard stored outdoors or delivered in rain absorbs water. Below 0 °C
that water freezes inside the fibres and between the sheets. The material changes completely:

- **Wet, unfrozen:** fibres go soft. The pack compacts *more easily*, so the same pressure gives a
  *higher* density. The water also adds real mass that the operator's weighbridge will charge for.
- **Wet and frozen:** the ice makes the pack *harder*. It needs *more* pressure to reach the same density,
  or reaches a *lower* density at the same pressure. Frozen clumps do not deform like dry board.
- **Mixed states:** one container can hold dry layers, wet layers and frozen layers at the same time,
  and their state changes with every thaw and refreeze (day and night, weekend vs weekday).
- **Ice in and on the container:** ice can stick to the walls and floor (extra mass that stays after the
  lift, changes the friction the ram feels) and melts later as water.

**Why this breaks the method.** The whole estimate rests on *pressure → density*. Wet-and-frozen
cardboard moves that relationship in the opposite direction from wet cardboard, so the same pressure
reading can mean very different masses:

| State of the cardboard | Pressure needed for a given density | If we assume dry board, the mass estimate is |
|---|---|---|
| dry | normal | correct (within normal scatter) |
| wet, above 0 °C | lower | too low (and the water mass is missed) |
| wet, frozen | higher | wrong in the other direction (too high or too low, depends on the ice share) |
| mixed layers | unknown mix | unpredictable |

**What our simulation does (and does not).**
- The simulator applies a *wet softening* factor (rain on outdoor-staged paper/cardboard) and a separate
  *cold stiffening* factor. They are simply multiplied together. **There is no ice phase**: no
  freezing of absorbed water, no frozen clumps, no ice on the walls, no thaw cycles.
- The rig tests wet samples at −15 °C, but with the same independent factors, so it cannot reveal
  the real frozen-wet behaviour.
- In the field, **no sensor tells us the material is wet**. The model does not use rain data; the
  weather-API idea is not built. So even the simple wet effect is invisible to the estimator.

**Consequence:** our accuracy numbers for cardboard and paper are optimistic for Finnish winters,
especially at sites with outdoor material staging. **We have no validated solution to this today.**
Section 10 lists options to accommodate it.

**Ideas, not implemented and not validated:**
- Flag lifts as *low confidence* (wider interval) when: site stages material outdoors + rain or snow in
  the last ~72 h (weather API) + air temperature near or below 0 °C.
- Run a dedicated freeze-thaw rig campaign: wet board frozen at several water contents, compacted
  frozen and partly thawed.
- Use season-specific per-machine calibration (separate winter anchor tickets).
- Test whether the pressure *curve shape* (e.g. a sharper rise for frozen clumps) can detect the state.
- A cheap moisture or humidity probe in the hopper. Doubtful: the briefing said moisture measurement in
  bulk material is unreliable, even in agriculture.

### 1.2 Frozen biowaste [unsolved, partly modelled]
Biowaste freezes to the container walls in winter. Part of it stays in the container after the lift
(the pack's partial-lift rate rises from 0.6 % to 5 % in winter biowaste [pack]), and frozen material is
stiffer. The simulator has a cold stiffening factor for biowaste and residual mass from the pack, but no
freezing-to-the-wall mechanism. The residual estimate after a lift (fill after × volume × loose density)
will be wrong when frozen chunks remain.

### 1.3 The pressure-to-mass physics itself is unvalidated [hyp]
The data pack contains **no hydraulic pressure curves** (`press_load_index` correlates 0.985 with fill),
so the whole compaction model is our hypothesis: a material law, a confinement term, floor friction and
a density gradient. The results show what pressure *could* add if real machines behave like this. They
are **not** evidence that they do. Phase 0 of the rollout (Europress's archived stroke curves vs shared
tickets) must test it first.

### 1.4 Aluminium cans are poorly described
For aluminium cans the pressure-density method (12.7 % median error) was *worse* than the plain table
method (9.9 %). Light, springy cans give a flat, poorly constrained law, and the fit found implausible
parameters (negative cold coefficient, very high limit density). It needs more low-pressure rig points
and springback measurements.

### 1.5 Glass is hypothetical
Glass is brittle (it crushes step by step instead of compressing), abrasive, a safety risk, and is
rarely compacted in practice. Its law uses the same smooth form as the other materials, which is
almost certainly wrong for crushing behaviour. Treat all glass results as illustrative only.

---

## 2. Other exceptions the method handles poorly

| Situation | What goes wrong | Current handling |
|---|---|---|
| Container overfull, ram stalls at maximum (relief) pressure | Pressure stops at relief; extra mass is invisible | Stroke completion is a feature; mass is underestimated. Flag needed |
| Wrong material in the container (mixed waste in a cardboard unit, contamination) | Wrong density law is used | Not detected; quality is only judged by the operator [pack] |
| Pack relaxes or creeps (weekend, long pause) | Springback changes density between cycles | Not modelled (pack density assumed set by the current stroke) |
| Layered pack with different histories | Real pack is not uniform | Simplified to one average density with a fixed gradient |
| Hydraulic faults (leaks, worn pump, wrong oil) | Pressure losses change | Only temperature-driven losses modelled |
| Pressure sensor drift | Slow bias in all estimates | 4 % of devices drift in the sim; anchor tickets correct it partly; no drift alarm (CUSUM) built |
| Fill sensor bias (±4 pp, ±7 % gain per device) [pack] | Volume error feeds straight into mass | Corrected only by per-machine ticket calibration |
| Residual after the lift (stuck material) | Collected mass wrong | Estimated from fill after × loose density; crude |
| New machine type, new ram geometry | Catalogue areas and laws unknown | Must be measured; not covered |
| Very light lifts (< 300 kg) | Relative errors large | Reported separately (acceptance uses ≥ 1 t lifts) |
| Machines with no clean tickets (Hauler Delta never shares; Gamma ~55 %) [pack] | Cannot be calibrated from tickets | Only fleet model or platform cohort; 15.8 % of pack lifts are on such machines |

---

## 3. Assumptions: data and ground truth

- **Device roster, sites and lift timeline come from the Europress pack** (447 devices, 18.3k lifts) [pack].
- **True mass per lift = the pack's `device_mass_kg_before / after`.** The pack's own simulated integrated
  scale has ~1.5 % noise and injected faults, so our "truth" inherits that. Where it is missing or
  implausible (ratio to fill × density outside 0.3–3), we fall back to fill × volume × typical density
  (~11 % of lifts).
- **Glass, aluminium and steel cans are not in the pack.** Their 60 devices, lift timelines and intake
  rates are fully synthetic [est].
- **Climate:** approximate Finnish monthly normals per region, a day-to-day AR(1) anomaly of 4 °C, a
  diurnal swing of 3 °C, 40 % rain-day probability (less when freezing) [est].
- **Cycle timing:** compaction cycles fall inside site opening hours (from the pack); Helsinki time is
  approximated as UTC+2 all year (daylight saving is ignored).
- **Cycle count:** kg loaded per press varies by site habit (35 %) and over time (25 %), so cycle count is
  only a loose proxy for mass. An earlier version without this leaked the answer and was fixed [hyp].

## 4. Assumptions: physics (all [hyp] unless tagged)

- **Material law:** density rises with ram face stress, `ρ(σ) = ρ_loose + (ρ_inf − ρ_loose)(1 − e^(−σ/σc))`,
  reaching the pack's typical compacted density [pack] at 55 % of relief stress.
- **Material variability:** stiffness varies by device (10–20 %) and by day (5–10 %) [pack-derived].
- **Confinement:** stress rises with volume fill as `K·φ³`, K = 85 % of relief stress.
- **Floor friction:** the pack slides until it locks against the back wall (sigmoid around 45 % fill).
  Friction ×1.2 when wet, ×0.8 on ice below −2 °C.
- **Cold stiffening:** plastics +20–25 %, biowaste +30 %, fibre +3–5 % at −20 °C.
- **Wet softening:** wet fibre compacts up to 25 % more easily. Independent of temperature (see 1.1).
- **Field vs lab:** the field pack is less dense far from the ram (average density × (1 − 0.12 φ)). The lab
  rig does not see this, so the rig law reads about 5 % high in the field. Its size is a guess.
- **Press geometry [est]:** COMBI 80 cm² cylinder area / 0.95 m² ram face / 180 bar relief;
  DUO 126 cm² / 1.45 m² / 200 bar; ±2 % manufacturing tolerance.
- **Hydraulic losses [est]:** 6 bar at 40 °C oil, rising exponentially when cold (~18 bar at 9 °C).
  Oil warms 1.2 °C per cycle and cools toward air temperature with a 1.5 h time constant.

## 5. Assumptions: sensors and hardware costs [est]

| Sensor | Error model | Indicative cost |
|---|---|---|
| Pressure transducer 0–250 bar | 0.4 % FS noise, 1 % gain, 1 bar offset, 4 % of units drift | €60–150 |
| Oil temperature probe (PT1000) | 0.5 °C | €10–25 |
| Motor current clamp | 4 % | €20–40 |
| Frame strain gauges | 45 % load share ±10 %, 40 kg noise, 6 kg/°C thermal drift, zero walk | ~€350 installed |
| SMART fill (existing) [pack] | 3.5 pp noise, ±4 pp bias, ±7 % gain per device | €0 |
| Platform scale (T2) [pack] | max(15 kg, 1.4 %) | ~€1,500 (business plan BOM €1.0–1.9k) |

Costs are order-of-magnitude, not quotes. Installation labour is not included.

**Stroke curves:** 50 Hz, a generic shape (spike, free travel, plateau, rise, hold if stalled, return),
1 bar noise and 1.2 % pump ripple. Real curves will look different. The extraction algorithm is tuned to
our own synthetic shape; a real controller also knows the valve reversal directly.

## 6. Assumptions: scales and labels

- **Weighbridge [pack]:** 12 kg noise, 20 kg resolution, 45 % stored tare.
- **Stale tare [pack-derived, hyp]:** 15 % of vehicles carry a stored-tare bias (sd 160 kg), modelled on
  the business-plan finding that 10 of 70 vehicles cause 79 % of tare errors.
- **Combined loads** 5 % (allocation error 25 %); **side waste** 4 %, 60–400 kg, reported by the driver
  70 % of the time [hyp].
- **Ticket sharing per operator [pack]:** A 97 %, B 88 %, C 55 %, D 0 %, E 95 %.
- **Clean anchor ticket** = shared, single load, weighed tare, no reported side waste.
- **Golden cohort:** 4 % of devices on platform scales [hyp].
- **Training uses only these labels**, never the hidden truth. Scores are against the hidden truth.

## 7. Assumptions: the density rig experiment

- 0.7 × 0.7 m press box, 200 kPa maximum face stress, 10 pressure steps [est].
- Batch weighed on a 0.2 % bench scale; ram position by draw-wire ±3 mm.
- 8 batches per condition: −15 / +5 / +20 °C, plus wet for paper and cardboard.
- Batch-to-batch variation of the dense limit 5 % [hyp]. The measured scatter (5–11 % by material) is the
  floor of any pressure-based estimate before per-machine calibration.
- Densities for glass and cans are rough literature-order placeholders [est] that a real campaign must
  replace.
- **Recommended real-world alternative:** calibrate in place on a production compactor standing on a
  platform scale, which also captures the field density gradient (section 4).

## 8. Assumptions: models and scoring

- Gradient-boosted trees on log mass; 5-fold split by device, so scores are for machines never seen.
- Per-machine calibration: shrunk median log-ratio of earlier clean tickets (weight k/(k+2)). Only
  tickets dated before the lift are used.
- Acceptance criteria are from the team business plan: ≥ 80 % of ≥ 1 t lifts within ±10 %, device-month
  totals within 5 % for ≥ 80 % of device-months, 80 % interval covering 75–85 %.
- The physics estimator uses the **same formula family** as the simulator, which gives it a built-in
  advantage. Real-world error will be larger.
- Results from different runs are not all on the same simulation version: the hardware-tier comparison in
  `reports/scores.csv` predates the added materials and the field density gradient.

## 9. What remains untested (needs real machines)

1. Whether real stroke curves carry mass information beyond fill (Phase 0 go/no-go: ≥ 30 % error cut).
2. Real density laws per material, per season, wet and frozen (section 1.1).
3. Field-vs-lab density difference.
4. Long-term pressure sensor drift and hydraulic wear.
5. Installation effort, controller analog input availability, data link.
6. Whether operators accept device weights as evidence (not legal-for-trade; business plan §7).

---

## 10. Options to accommodate cold and wet weather

None of these are validated. They are grouped by what they do. Costs are [est].

The problem has four separate parts, and each option below says which ones it addresses:
- **W1 Water adds real mass.** The weighbridge charges for it.
- **W2 Wet fibre is softer.** The same pressure gives a higher density.
- **W3 Ice makes the pack harder.** The same pressure gives a lower density.
- **W4 Ice and frozen material stay in the container.** This changes the residual and the floor friction.

### A. Know the state of the material (inputs)

| # | Option | Addresses | Cost | Notes |
|---|---|---|---|---|
| A1 | **Weather data per site** (Finnish Meteorological Institute open data: precipitation, air temperature, humidity). Compute a *wetness index* (rain or snow in the last 72 h) and a *frost index* (hours below 0 °C since the last wetting) | W1–W4 (detects, does not fix) | €0, software only | Only meaningful where material is staged outdoors (`outdoor_material_staging` in the pack) |
| A2 | **Site metadata:** is material staged outdoors, is it covered, is the compactor indoors or outdoors, and is the hopper roofed? | W1–W3 | €0, one-off survey | Most of the risk sits at a minority of sites. Find them first |
| A3 | **Material-temperature probe** in the hopper or chamber wall (PT1000 or a small IR sensor), in addition to the oil probe | W3, W4 | €15–40 | Material temperature lags air temperature. Board from a heated store is not frozen even at −15 °C outside |
| A4 | **Pressure-curve shape features** from the 50 Hz trace: roughness and spikes during the rise (frozen clumps fracturing), how sharply pressure rises, and pressure decay during the hold (springback) | W2, W3 | €0 (same transducer) | Hypothesis: frozen packs give a jagged, steep curve and wet packs a smooth, low one. Must be checked on the rig |
| A5 | **Headspace humidity sensor** in the chamber | W1, W2 (weak) | €10–20 | A rough "wet material present" signal only |
| A6 | **Bulk moisture sensor** (microwave or NIR) | W1, W2 | ~€1,000+ | Accurate, but costs as much as a platform scale. The briefing said bulk moisture measurement is unreliable even in agriculture |

### B. Model the state (physics)

| # | Option | Addresses | Notes |
|---|---|---|---|
| B1 | **Extend the density law** to ρ(pressure, material temperature, water content), with an explicit ice term: below 0 °C, stiffness rises with the share of water that is frozen. Measure it in a **freeze-thaw rig campaign**: board with 0 / 10 / 20 / 40 % added water, conditioned at +5, −2, −10 and −20 °C, plus thaw-refreeze cycles | W2, W3 | The core fix. Replaces the two independent factors that are simply multiplied today |
| B2 | **Layered pack model:** the controller knows when each cycle happened, so each charge gets its own temperature and wetness at insertion (from A1 and A3). Density is computed per layer and the layer masses are summed | W2, W3 (mixed layers) | Handles a container with dry, wet and frozen layers at once |
| B3 | **Separate dry mass from water mass.** Report both: "2.4 t, of which about 0.3 t is water" | W1 | Turns the exception into a service: "this month you paid for about 400 kg of rainwater; cover the staging area" |
| B4 | **Winter residual model:** after a winter biowaste lift, use the fill-after reading and the frost index to estimate the frozen material left behind | W4 | Prevents the next lift from being over-credited |

### C. Correct with data (calibration)

| # | Option | Addresses | Notes |
|---|---|---|---|
| C1 | **Calibration per weather regime:** keep separate per-machine ticket gains for "dry", "wet" and "frozen". When a machine has few tickets in a regime, fall back to the fleet's gain for that regime | W1–W3 | Software only. Needs tickets from every regime |
| C2 | **Weather-aware ML:** add the A1 and A3 indices as model features and train on winter tickets | W1–W4 | Needs one full winter of labelled data |
| C3 | **Pilot must run through a full winter** (November–March), including northern sites (Pohjois-Pohjanmaa, Lappi) and outdoor-staged cardboard | all | Without this, nothing above can be validated |
| C4 | **Drift alarm per regime** (CUSUM on ticket residuals), so a machine whose winter estimates drift gets recalibrated | W2, W3 | Already on the list of things not built (section 2) |

### D. Handle what cannot be fixed (uncertainty and product)

| # | Option | Addresses | Notes |
|---|---|---|---|
| D1 | **Confidence flag and wider intervals** whenever the wetness or frost index is high: "low confidence: wet or frozen material" | all | Honest, and cheap. Keeps trust |
| D2 | **Reconciliation tolerance per regime:** do not raise a device-vs-ticket difference in the wet or frozen regime unless it is large. In that regime, treat the weighbridge as the better measurement | W1–W3 | Avoids false disputes with operators |
| D3 | **Report monthly totals, not per-lift values,** in winter at risky sites | W2, W3 | Errors partly average out over a month |
| D4 | **Platform scale (T2) at the worst sites** (outdoor-staged, high-value cardboard, in the north) | W1–W4 | A direct scale weighs water and ice without caring about the state. Strain gauges do not help: they have their own thermal drift |

### E. Prevent the problem (operations)

| # | Option | Addresses | Notes |
|---|---|---|---|
| E1 | **Advise customers to cover outdoor staging** and roof the hopper | W1–W3 | Also saves the customer money: no paying for rainwater |
| E2 | **Hydraulic oil heater** (common on machines in cold climates) | oil losses only | Stabilises pressure losses. Does nothing for the material itself |

### Recommended combination

1. **Now, software only:** A1 + A2 + C1 + D1 + D2. Find the risky sites, detect wet and frozen
   conditions from weather data, calibrate per regime, widen intervals and do not dispute in those conditions.
2. **With the pressure retrofit (+€15–40):** A3 + A4, measuring material temperature and recording
   curve shape.
3. **Research before claims:** B1 + B2 through a freeze-thaw rig campaign and a winter pilot (C3).
4. **Product:** B3 and E1 as a customer service ("rainwater you paid for"). D4 only where the value
   justifies a platform scale.
