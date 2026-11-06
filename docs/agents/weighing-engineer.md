# Weighing concept (Part 1, "Get the weight") - weighing-engineer

Tags: **[S]** sourced, **[E]** estimate, **[A]** assumption. Prices fetched 2026-11-06, EUR net unless noted.

## 0. Bottom line

- **Primary: "Anchor-calibrated virtual scale"** = options (a)+(d). No new hardware. The ram pressure curve per stroke, stroke count and fill feed a compaction-physics model. A few clean weighbridge tickets (or one manual weigh) set the per-machine gain. Target is **+-7% (1 sigma) per 3 t load and +-4-5% on monthly totals [E, untested]**. That puts about 87-93% of lifts inside Tommi's "+-10-12%". It does **not** meet +-3.3% / 100 kg.
- **Premium: 4-corner load-cell platform** under the compactor/container. This is what Europress already lists as "Scale platform". Expect **+-1.4% (1 sigma), about +-80 kg at 95% [E]**. BOM is about EUR 1.0-1.9k, or EUR 14-26/month over a 72-month lease [E]. Use 2-5% of the fleet as a **golden cohort** that produces ground truth to train the fleet model.
- **Drop:** strain gauges on the frame (dominated), and load pins or truck scales (the operator owns the truck and the data, which is the pain we are trying to fix).
- **Finding [S]:** Europress already sells weighing. Scaletipper X1 tips and weighs each 140-1100 L bin (max 440 kg, 1.0 kg accuracy, 35 s cycle). The "Scale platform" sits beneath the compactor with one weighing sensor per corner. No accuracy figure, price or retrofit info is published for the platform (europressgroup.com/scale-solutions, /scaletipper-x1). The premium tier is therefore a repackaging of an existing product, not a new invention.

## 1. Options compared (3 t cardboard load, 1 sigma)

| | Principle / placement | Retrofit | BOM EUR/unit | Accuracy | Main errors | Fit with "cheapest wins" |
|---|---|---|---|---|---|---|
| **a** Virtual scale, generic | Per-stroke P(t), stroke count and fill -> mass. Uses the existing 0-200 bar transducer. | OTA firmware for 10-20 Hz curve logging [A]. | 0. Optional oil-temperature probe EUR 10-25 [E]. | +-14% uncalibrated [E]. Fill-only baseline on synthetic data: median abs. error 16%. | Unit-to-unit gain, material, oil temperature and friction, springback, moisture | Best |
| **b** Load cells, 4-corner platform (COMBI) or under DUO container cradle | Direct force. 4 x Kern CT 5000-3P2 (5 t, C3, IP67) at EUR 124 = 496 [S]. Junction box Kern CJ X467 EUR 220 [S]. Transmitter EUR 150-300 [E]. Frame, feet, stops EUR 400-900 [E]. | Lift a 6-10 t unit onto the platform, 3-5 h with 2 technicians [E]. Easiest as a factory option. DUO cradle needs lift-off protection. | **1.3-1.9k catalogue; about 1.0-1.4k at 100+ units** [E, -25%]. Cross-checks [S]: PCE-SD 3000U 4-cell floor scale EUR 3,231 incl. VAT; stainless 4-cell legal-for-trade platform EUR 2,400 pre-tax. | **+-1.4%** [E] | Snow and wind outdoors, off-level ground, tare drift, rail flex. A scale does see wet-cardboard weight. | Premium only |
| **b2** Strain gauges on frame or supports | Full-bridge gauges on support beams, plus 24-bit ADC (HX711 board EUR 4.71 [S]) | 3-5 h grinding, bonding, protection, in-situ load test [E] | 250-600 [E]. Omega full-bridge gauges USD 213-397 per 5 [S]. | Vendor claims for bolt-on sensors: 3-5% (Kistler-Morse L-Cell), 1-2% only with high strain and calibration [S]. Frame: **+-5% or worse** [E]. | Ram reaction forces, weld fatigue and drift (patents [S]), signal too small on a stiff frame, temperature | Dominated by (d) |
| **c** Load pins in lift lugs, hook-lift or truck scale | Pins in lugs (ANYLOAD 535TS pin USD 722 single, USD 614 at 100+ [S]). Hyva Titan: 4 chassis load cells, <=1% claimed [S]. Rice Lake TradeRoute list USD 15.4-20.4k [S]. | Wireless or battery pins for lugs [A]. Truck systems sit on the operator's vehicle. | 1.5-3k for lugs [E] | <=1% (vendor claim) | Shock and dynamic loads, one reading per pickup only | Wrong owner. Use only as data ingest via operator API. |
| **d** Hybrid = (a) + anchors | Anchors are weighbridge tickets (SINGLE_LOAD, WEIGHED tare, no side waste), a customer manual weigh, or a service-visit weigh | None | 0. A one-off weigh trip if no tickets: EUR 100-250 [A]. | **+-6.6% [E]** | Anchor noise (~3%), stale tare, side waste | **Primary** |
| **e** Golden cohort + fleet transfer | 2-5% of fleet gets (b). Continuous per-stroke labels train one shared compaction law. New machines need 1-3 anchors. | Cohort only: 10 of 500 machines = EUR 10-19k [E] | 0 for the rest | Prior gain sd 10% -> about 6% [E]. Fleet result about +-6%. | Cohort not representative | **Enabler** |

Camera or vision gives volume and contamination cues, but no density. Treat it as a Part 2 sensor (EUR 80-150 [E]), not a weighing method.

## 2. Pressure -> mass model (physics + ML sketch)

**Features per stroke i:** P_peak, P_hold (0.5-1 s after the plate stops), dP/dt on the rise, stroke time t_s (at constant pump flow it is a position proxy), work W_i = Q_pump * integral of P dt [A: fixed-displacement pump, to be checked], pressure decay during hold (springback / viscoelastic signature), oil temperature (or the t_s of an unloaded stroke as a proxy), strokes since emptying, fill_pct (existing algorithm), container volume, material stream, equipment class, rain flag (`outdoor_material_staging`).

**Physics baseline (grey-box).**
1. Force F = P*A_cyl - F_fric(T). Plate stress sigma = F/A_plate. Example: bore 100 mm, 200 bar -> about 157 kN [A: bore unknown].
2. Compaction law of Walker/Heckel type: rho(sigma) = rho0 + beta*ln(sigma/sigma0), fitted per material [A].
3. Charge mass: Delta m_i = W_i / w_mat(sigma_i). Here w_mat is the specific compaction work, the integral of sigma * d(1/rho), which has a closed form under the law above.
4. Container mass: **m = g_dev * sum(Delta m_i)** since the last emptying, with per-device gain g_dev. Cross-check with the fill route m = V*f*rho(P_hold). Combine both by inverse-variance weighting.

**ML layer.**
- LightGBM quantile regression (q10/q50/q90) on log(m_ticket / m_phys), with monotone constraints on P_hold and strokes.
- Hierarchical shrinkage: g_dev ~ N(0, 0.10^2) a priori. Update it with clean anchors using a Student-t likelihood (noise about 3-4%) and a CUSUM change-point test so drift and fault episodes are not absorbed.
- Conformal calibration of the intervals.
- Report mass +- 80% interval, with a SHAP-style top-3 drivers per lift for explainability.
- Cross-validation is leave-device-out (generalisation) plus forward-chaining in time (drift).
- Zero point: the container is empty after every pickup, so each emptying re-zeroes the integral for free.

## 3. Error budget (1 sigma, % of 3,000 kg)

| Source | (a) generic | (a)+(d) calibrated | (b) platform |
|---|---|---|---|
| Fill / volume (fill +-5% [S: Tommi]; the stroke integral relies less on it) | 5.0 | 3.0 | - |
| Density law and springback | 8.0 | 4.0 | - |
| Unit gain (bore, seals, geometry, wear) | 10.0 | 2.0 | 0.3 (installation, sim 0.4%) |
| Oil temperature and seal friction (viscosity changes ~100x over the working range [S: SKF]) | 2.5 | 1.5 | - |
| Moisture (true mass the pressure model cannot see; weather feature helps) | 3.0 | 3.0 | 0 |
| Sensor (pressure 0.5% FS [S: Tameson/WIKA listing]; C3 load cell 0.023% [S: Kern]) | 0.5 | 0.5 | 0.1 |
| Tare / zero / residual | 1.0 | 1.0 | 0.7 |
| Wind, snow, tilt, vibration, rail flex | - | - | 1.0 |
| Level / off-centre | - | - | 0.5 |
| Anchor truth (20 kg resolution, STORED tare, side waste) | - | 1.5 | - |
| **RSS** | **~14%** | **~6.6%** | **~1.4%** |

All entries are [E], to be replaced by measured values in the validation. If the errors are roughly Gaussian, the share of lifts within +-10% / +-12% is about 87% / 93% for (a)+(d). The 6-lift aggregate error is about 4% because only the random terms average out and the gain and moisture terms do not.

## 4. Validation experiment

1. **Phase 0, desk (2 wk): falsification test.** Pull the SMART pressure archive for at least 30 machines with at least 10 shared tickets each. Fit leave-device-out models: fill-only vs fill + pressure features. Go/no-go gate: pressure features must cut MAE by at least 30% against fill-only with the same anchors.
2. **Phase 1, golden rig (4-6 wk).**
   - Equipment: 6 machines (3 COMBI, 3 DUO; cardboard, plastic, mixed) with a 4-cell platform each, EUR 1.3-1.9k per unit.
   - Ground truth: at least 25 pickups per machine (about 150 lifts) over a weighbridge with WEIGHED tare, preferably Europress's or a partner's own verified bridge, plus the per-stroke platform signal.
   - Charge-by-charge bench test: feed 40 charges of known mass, weighed on a pallet scale (about +-1 kg), and regress the stroke curve on the charge mass. This tests the Delta-m model directly, in one day.
   - Conditions: include rain and snow weeks, and a cold start.
3. **Phase 2, fleet field (8-12 wk).** 30 un-instrumented machines (15 cardboard, 8 plastic, 7 mixed) with at least 8 clean tickets each. Train on the cohort plus k = 1, 3, 5 anchors per machine. Test leave-device-out.
4. **Ground-truth rules.** Join on `operator_job_ref`. Use SINGLE_LOAD tickets only, prefer WEIGHED tare, drop driver-reported side waste, and drop combined or equal-split loads. Double-weigh a subsample to measure ticket noise.
5. **Sample size.** About 150 lifts gives a 95% CI of +-6.4 points on a proportion near 0.8. The 30 machines x at least 8 lifts (at least 240 lifts) in Phase 2 plus about 90 device-months cover the aggregate test.

**Acceptance (pre-registered):**
- A1: at least 80% of >=1 t lifts within +-10% of net, with CI lower bound at least 72%.
- A2: monthly-total bias of at most 5% for at least 80% of device-months.
- A3: median absolute error of at most 5%, and no machine with a persistent bias above 10% after 3 anchors.
- A4: the 80% interval covers 75-85% of lifts.
- A5 (premium): at least 95% of lifts within +-3.3% (+-100 kg at 3 t).
- A6: beats the fill-only baseline by at least 30% on MAE (paired bootstrap, p < 0.05).

**Falsified if:**
- Pressure adds under 10-15% over fill-only.
- Residual sigma stays above 10% after calibration.
- Anchored gain wanders by more than 10% month to month.
- Wet-load bias exceeds 8% and cannot be modelled.
- The oil-temperature residual is not removable.

If falsified, fall back to the fill-only + anchors baseline (about 9% median error) or sell the platform.

## 5. Calibration and operations

- **Commissioning:**
  - Virtual scale: zero (empty after the first emptying) plus one reference weigh.
  - Platform: dead-weight check with certified masses, then auto-tare at each emptying.
- **Run time:** an anchor arrives with every shared ticket. Re-fit the gain monthly. Flag any gain change over 8% for review.
- **Scalability:** the virtual scale is a software rollout and a firmware push. The platform scales with BOM and a service visit.

## 6. Legal metrology

Neither tier is legal-for-trade. EU legal-for-trade weighing needs NAWI 2014/31/EU / OIML R76 class III approved instruments, or MID 2014/32/EU MI-006 for automatic weighing. On-board refuse-vehicle systems certified under MID apply OIML R51 (a FORCE Certification certificate [S]). Irish regulators treat bin-weighing systems on trucks as under metrological control when used for trade [S]. The national authority (Tukes in Finland [A, to confirm]) decides the details.

- **Position:** verification-grade evidence for invoice checks, anomaly flags and disputes, not billing-grade. The invoice basis stays the operator's weighbridge unless the parties agree otherwise (cf. the dataset's ECONOMIC_MODEL section 2b: verification vs billing basis).
- **Upgrade path:** the platform is the only tier that could be certified, but that needs type approval and notified-body verification.

## 7. What the synthetic data can and cannot validate

Measured on the competition set (369 devices, 12,915 single-load tickets, median 30 per device):

- **Sim sensor vs weighbridge, lifts >=1 t:** median -2.2%, 53% within +-3.3%, 78.5% within +-10%, 5th percentile -25%. For cardboard the median absolute error is 85 kg. The ticket itself is noisy, so "truth" is not exact.
- **Ticket quality:** 44% of tickets use STORED tare. Median absolute deviation from the device is 4.6% (STORED) vs 2.4% (WEIGHED). Lifts with side waste deviate by a median of -11%. Anchors must be filtered.
- **Fill-only virtual scale (the bar to beat), median absolute error / share within +-10% per lift:**
  - 0 anchors, typical density table: 15.9% / 32%.
  - 3 anchors: 9.4% / 52%.
  - 8 anchors: 8.3% / 58%.
  - 6-lift aggregate with 3 anchors: 6.4% / 68%.
  - The within-device CV of implied density is 14.6%, so fill alone plateaus at about 8-9%.
- **Naive anchor gain-correction of the simulated sensor made it worse** with 1-5 tickets (median absolute error 3.0% -> 5.3%). Anchors are noisy at about 3%, and the sim's device errors are episodic. So the robust Student-t / CUSUM design in section 2 is a requirement, not a nicety.
- **Cannot validate:** pressure -> mass. `press_load_index` correlates 0.985 with `fill_pct` (it is derived from the fill estimate, ASSUMPTIONS section 8), so it holds no independent pressure information, and the dataset has no curves. A synthetic pressure generator can unit-test the fitting code and the calibration logic, but it proves nothing about reality. Analysis scripts are in `/home/hackathon/.claude/jobs/717fee2a/tmp/weigh/` (an4.py, an5.py, an6.py).

## 8. Third-party components (weighing analysis)

pandas, NumPy, SciPy, scikit-learn (BSD-3); LightGBM, DuckDB (MIT). All allow commercial use. Dataset: Since AI v1.0.1 synthetic data, with licence per its README (to confirm).

## 9. Open questions

1. **For Tommi (biggest):** what are the price, accuracy and install effort of the existing Scale platform, and is the full per-stroke pressure curve archived centrally? The case rests on both.
2. Is the pump fixed-displacement, and is oil temperature already logged?
3. Which operators will share WEIGHED-tare tickets for Phase 0?

## Sources

- europressgroup.com/scale-solutions/, /scaletipper-x1/, /scaletipper-wholesale-market/
- kern-sohn.com CT 5000-3P2, CT 3000-3P1, CJ X467
- hyva.com Titan Weighing System news
- ricelake.com TradeRoute HL
- tacunasystems.com ANYLOAD 535TS
- RS Components WIKA 0-250 bar listings
- tameson.com WIKA 12719332
- Patents US11162834 (BACE, retrofit container scale), US5230393 and the on-board transducer patents
- Applied Measurements / Anderson-Negele bolt-on sensor accuracy
- SKF evolution article on viscosity
- FORCE Certification MID refuse-vehicle certificate and the Irish regulator page
