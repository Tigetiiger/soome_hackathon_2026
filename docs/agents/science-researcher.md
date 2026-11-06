# Science lens: how the weight/mass problem has been solved, and what transfers to a Europress virtual scale

Author: science-researcher, 2026-11-06. Length exceeds the ~2,000-word guideline because the brief asks for seven literature strands plus six deliverables; section 0 is the 1-minute read.

**Tags.** [fact/sourced] = read in the source named. [estimate] = my arithmetic or judgement. [assumption] = needs a team or Tommi answer. [data] = my own quick probe of the quickstart pack (50 devices, synthetic; not real-world evidence). **Access status in the tables:** [O] = I opened the paper, abstract or patent text; [S] = seen only in a search snippet, treat as unverified detail; [V] = vendor claim, no independent test seen. Numbered IDs like [8] point to the citation table in section 6.

---

## 0. Bottom line

1. **No peer-reviewed paper found that estimates mass from ram pressure in a waste compactor or recycling baler.** More than 25 searches (standard and extended) found only patents that infer *fullness* from pressure ([20], [21], [22]) and none that infer weight from pressure. That is a risk (no published accuracy to lean on) and an opening (a calibrated, uncertainty-aware version is publishable and defensible as new). [fact/sourced for the search; absence is not proof]
2. **Excavator and loader results (1-4 %) do not transfer directly.** There, pressure is proportional to weight through gravity and known geometry ([1], [3]). In a compactor, pressure measures the *material's resistance*, which links to mass only through density, compressibility, friction and moisture. The transferable parts are the method (staged calibration against a known reference, explicit friction and temperature terms, learned correction, mean-plus-SD reporting), not the accuracy figure. [estimate]
3. **The closest analogue that did work is a fleet-learning pattern**: 25,000 bales from 25 scale-equipped machines in 5 countries trained a Random Forest that estimates weight on machines *without* scales, 4.96 % mean relative error, r = 0.96, no added hardware ([8]; weakness: ground-truth scales themselves had 2.9 % mean relative error, and the split method is not stated). This supports the "golden cohort plus tickets" design.
4. **Honest accuracy range for Europress** [estimate, section 2]: per lift about 12-15 % (1 sigma) with fill + tickets only; 8-11 % if stroke-curve features carry independent density information (unproven); device-month totals about 5-6 %. The literature does not support "+-10 % for 90 % of lifts" per lift. Tommi's ballpark (+-10-12 %) is plausible for monthly totals and the median lift, not for every lift.
5. **Ground truth is itself fuzzy.** A class III weighbridge with e = 20 kg (assumed from the dataset's 20 kg ticket resolution) allows +-20 kg per reading above 10 t gross at initial verification, doubled in service ([11] Table 6), so a gross-minus-tare net can be off by +-40 kg (initial) or +-80 kg (in service) before any stale-tare or side-waste effect. Evaluate the model with this noise removed, not against tickets as if exact.

---

## 1. Evidence by strand

### 1.1 Payload from hydraulic pressure (excavators, loaders, refuse arms, balers)

| ID | Method | Reported accuracy and conditions | Sensors and data | Transfer to a compactor |
|---|---|---|---|---|
| [1] Werner et al. 2025 [O] | Identified dynamic model plus optimisation, staged calibration (about 30 min: cylinder area with one known load, inertia, friction, gravity) | 25 t excavator: payload error mean 5.7 kg, SD 30.4 kg (about 1 % of 9,210 kg rated capacity; 3 sigma about 91 kg). Commercial system: mean 101.7 kg, SD 51.3 kg. Quasi-static method: mean 264.7 kg, SD 2,263 kg. 12-13.5 t machine: mean 4.5 kg, SD 20 kg. | 2 pressure sensors (both chambers, boom and stick), inertial/kinematic sensors, link lengths | Method lessons only (staged calibration, benchmarks, mean+SD). Accuracy is "% of full scale", not of reading. |
| [2] Ferlibas & Ghabcheloo 2021 [O] | Least-squares dynamic parameter identification, loaded minus no-load torque | Static: 250 kg load 14.0 % / 13.6 % error, 500 kg 9.4 % / 6.8 % (two variants). Dynamic: headline "2 % at high enough velocity", individual runs 0.1-17 % on 318 and 618 kg loads. Static friction is the main error. | IMUs and pressure sensors on a Komatsu excavator | Shows error as % of reading explodes when the load is small relative to machine range, as in a half-empty compactor. |
| [3] Savia & Koivo 2002 (IFAC) [O] | Kalman filter extracts steady signal levels, one-hidden-layer MLP maps to payload | Underground loader, loads up to 11,660 kg: relative error -3.86 to +3.20 % for 95 % of validation data; best mean relative error 1.68 %. | Both boom-cylinder pressures, boom position (most important extra input), inclination (second), oil temperature | Template for "physics inputs plus learned nonlinear map plus oil temperature". |
| [4] Volvo Load Assist; Cat Production Measurement [V][S] | Cylinder pressure plus position sensors | Vendor claim +-1 % per bucket; no test protocol seen | Pressure, position | Marketing figure only; do not quote as evidence. |
| [5] US10982415B2 (CQMS, 2021) [O] | Calibration factor = comparison error (known-load weigh) + temperature-dependent pressure-drop term (Darcy-Weisbach / Hagen-Poiseuille) | No measured accuracy; illustrative 5 % and 2 % corrections | Two pressures, hose temperature, geometry, flow | Confirms temperature and hose losses as standard error terms. |
| [7] EP0496166A2 (Mobile Computing, 1991) [O] | Pressure-based weighing of lifted refuse container | Applicants state error "in the order of 20-40 %" when centre of gravity is not where assumed; viscosity and stiction vary with temperature and pressure | Lift-cylinder pressure | Why pressure alone is not weight. Applicant's background claim, not a test. |
| [6] RWTH dissertation 2022/23 [S] | Analytical payload model plus ML correction | Not read; abstract says requirements met | Joint torques, motion | Same physics-plus-learned-correction structure we propose. |

**Baler and press analogues.**

| ID | Method | Accuracy | Data | Transfer |
|---|---|---|---|---|
| [8] Mansouri et al. 2025 [O] | Random Forest on bale diameter, moisture, roller pressure, speeds, work state; trained on machines with scales, applied to machines without | MRE 4.96 %, MAE 41.34 (unit not stated), r = 0.96 on a "separate test set" | 25,000 bales, 25 machines, 5 countries; scale ground truth had 2.9 % mean relative error | Strongest precedent for the fleet-teacher design. Measured moisture was an input, which we lack. |
| [9] Yin et al. 2023 [O abstract] | Dynamic weighing model for a round baler plus calibration equations | Max error 3.63 %, 3.40 % after calibration equations | Contact pressure on inclined surface, attitude angle, cylinder oil pressure | Calibration equations gave only a small gain once the physics was right. |
| [10] Kadam, SAE 2025 (John Deere) [O abstract] | Model-based, dynamic torque monitoring, no load cells | No accuracy figure in abstract | Torque | Shows OEMs are moving to load-cell-free weighing. |

### 1.2 Refuse vehicles, bin weighing, legal status

| ID | Finding |
|---|---|
| [12] OIML certificate R51/2006-GB1-16.01 (AMCS Vehicle Data Hub, 2016) [O] | Automatic catchweighing, one load cell on the lift, Y(a)/Y(b). Individual container Max 300 kg, e = 0.5 kg; trade container Max 600 kg, e = 1.0 kg. Dynamic weighing window during lift, gross on the way up, tare on the way down. "Does not bestow any form of legal international approval." Alternative 8 covers a lift on a fixed platform "e.g. waste compactor". |
| [13] VWS bin-weighing EU type approval, 2020 [O, trade press] | Wheeled bins within 0.5 % or 1 kg; front-loader systems certified to 20 kg, up to 3,500 kg. |
| [14] US6422800 (Stress-Tek, 2002, expired per Google) [O] | Strain gauges on fork flexure beams; design goal "within 20 pounds or 1 %". |
| [7] above | Pressure-only arm weighing 20-40 % error claim. |
| [15] MID 2014/32/EU Annex VIII (MI-006), UK R51 schedule [S] | Catchweighers are category X or Y; certificates cite OIML R51 and WELMEC guides. Y(b) instruments may only weigh ballast or waste listed in the pattern approval. Authoritative text is on EUR-Lex. |
| [11] OIML R 76-1:2006 [O] | Class III maximum permissible error on initial verification +-0.5 e (to 500 e), +-1.0 e (500-2,000 e), +-1.5 e (2,000-10,000 e); in-service errors are twice these (3.5.2). |

Transfer: trade-grade bin weighing is certified at <= 600 kg. A 3 t compactor load sits in weighbridge territory (R76 class III), so any Europress virtual scale must be labelled "indicative, not legal for trade". Finnish authority check (Tukes) is [assumption, unverified].

### 1.3 Soft sensing and compaction physics

| ID | Content | Use |
|---|---|---|
| [16] Tudor, Zabava, Voicu, Lazea, Constantin 2023 [O] | Horizontal cardboard baler, 10 charges per bale, about 360 kg bale. Pressure in main cylinder vs stroke: 0 to about 90 bar over 1.2 m, near-identical curves across charges, 12 s per charge, pressure-vs-time linear with R^2 > 0.9, return-stroke force plateau from relaxation (springback) of pressed cardboard. | Only open data on pressure-stroke curves for cardboard baling; confirms curve repeatability and a springback signature. **Caution:** the paper converts 29.0 tf*m to "about 29.0 kJ" (1 tf*m is about 9.81 kJ), so its 0.77-0.83 kJ/kg specific energy may be off by up to 10x. Do not quote that figure. |
| [17] Voicu et al. 2023; Lazea et al. 2022 [O] | Small vertical press: forces below 1,000 daN, 8-9 kJ total energy, 7-stage bale; "compaction ratio 6:1" for cardboard (intro claim). | Low-quality but shows force-stroke-energy are measurable. |
| [18] Sanchez et al. 2002 (WIT) [O] | Mass conservation through a baler; two-constant empirical output-density vs specific pressure law (equation garbled in my extraction); constants from two lab runs. | Supports a low-parameter pressure-density law and the "volume not mass per hour" view. |
| [19] Heckel 1961; Kawakita & Lüdde 1971; Denny 2002 [S] | Classic powder compaction laws. Kawakita: C = abP/(1+bP), so density rho(P) = rho0 (1+bP)/(1+(1-a)bP). Heckel: ln(1/(1-D)) = kP + A. Denny shows Kawakita is a special case of a modified Heckel. | Biomass studies report Kawakita fits with R^2 near 0.99 and Heckel fitting poorly (snippets of CIGR and BioResources, not opened). No fit to cardboard bales found. |
| [20]-[22] compactor patents [O] | US5299142 (Marathon, 1994): pressure or motor current "not an accurate means of determining fullness when the container is relatively empty"; counts rams until 50 % of max pressure, then uses pressure; temperature and material type listed as influences. US6123017 (PMDS, 2000): pressure-per-use average; max uses = PSIMAX/PPUA. US6738732 (One Plus, 2004): compares recent pressure curves with stored baselines. US8794135B1 (One Plus, 2014; listed active to about 2028): oil viscosity from pressure decay, fullness from max pressure. | None estimates weight. Prior art for pressure-based fullness and curve baselining; US8794135B1 is a possible freedom-to-operate flag for diagnostics claims (not legal advice). |
| [23] FHWA intelligent compaction [S] | Roller response used as a soil stiffness proxy; an FHWA official: "Consistently reliable correlation ... with in situ density ... have not been established." | Cautionary analogy: machine-response-to-material-state needs local calibration. |

Janssen silo theory (wall friction saturates pressure with depth): searches returned silage and grain work only, nothing on compactors [S]. Use at most as a shape prior for the pressure-vs-fill curve. [assumption]

### 1.4 Composition, contamination, moisture

| ID | Finding |
|---|---|
| [25] CEPI Paper for Recycling Quality Control Guidelines, April 2018 (quoting EN 643) [O] | Recovered paper is supplied "with moisture of not more than the naturally occurring level of 10 %"; above 10 % of air-dried weight the excess weight may be claimed back; test method agreed between parties; NIR, microwave and electromagnetic devices are in use; discount above 10 % and rejection above the agreed maximum. |
| [24] Silveira et al. 2021, Appl. Sci. [O abstract, CC BY] | 48 wastepaper and cardboard bales: dielectric plate meter vs oven drying, fitted equation R^2 = 0.76. |
| [26] ContamiNet, Ibrahim et al. 2019 [O abstract] | CNN on 30,000+ Recology curbside images: AUC 0.86 vs human experts 0.88. |
| [27] DFKI bio-waste scanner; truck-hopper detectors [S] | CNN accuracy 0.86 on RGB, contaminants must be visible; YOLOv8 mAP 0.395 (0.463 with transfer) on cluttered hopper scenes. |
| [22] US6738732 | Pressure-curve baseline comparison for fault diagnosis; no learned material classifier found. Material or contamination identification from pressure curves is a **gap** in the literature I could find. |

### 1.5 Smart-bin fill level and weight

| ID | Finding |
|---|---|
| [29] Ahmed et al. 2022, IJERPH, CC BY [O] | 32 public bins (Wyndham, Australia), 2018-2021, 80/20 split: LSTM test MAPE 2.198, 1D-CNN lowest test RMSE 1.132. Paper's "LSTM best" rests on MAPE and training metrics. |
| [30] Pollak et al. 2024, IEEE Access [S] | XGBoost fill-level classifier 82 % vs 59 % baseline; simulated routing saves 26 % time. |
| [31] Cetkin et al. 2024 [O abstract] | Sound impulse response plus ensemble learning, >90 % fill-class accuracy. |
| [32] Ferrer & Alba 2018 (BIN-CT) [O abstract]; [33] Vicentini et al. 2009 [exists, abstract not read] | Fill-level forecasting for routing; no numeric error in abstract. |

Fill-to-weight regression with measured densities: only textbook tables found (compacted MSW in trucks about 300-400 kg/m3, baled waste 470-900 kg/m3, uncompacted cardboard about 50 kg/m3 [S, secondary]); no regression on weighbridge data. Fit locally.

### 1.6 Calibration, uncertainty, drift

| ID | Relevance |
|---|---|
| [34] Angelopoulos & Bates 2021 [O abstract] | Distribution-free prediction intervals for any black-box model; extends to distribution shift and time series. |
| [35] Romano, Patterson, Candes 2019 (CQR) [O abstract] | Quantile regression plus conformal calibration: valid finite-sample coverage with heteroscedastic widths. |
| [36] Gibbs & Candes 2021 (ACI) [O abstract] | Keeps long-run coverage when the data distribution drifts, by updating the miscoverage level online. |
| [37] Xu & Xie 2021 (EnbPI) [O abstract] | Conformal intervals for time series without exchangeability. |
| [38] Kadlec et al. 2009, 2011 [S] | Soft-sensor review; adaptation mechanisms grouped as moving windows, recursive updating, ensembles. |
| [39] Bifet & Gavalda 2007 (ADWIN) [S] | Adaptive windowing drift detector with false-positive/negative bounds. |
| [41] Xiang et al. 2016 (AMT); Takruri et al. [S] | Recursive Bayesian recalibration of drifting field sensors with sparse reference. I found no source combining hierarchical partial pooling across a fleet with online updating from sparse noisy references; the pieces exist separately. [gap] |
| [42] Karniadakis et al. 2021 [S] | Review of physics-informed ML. |

### 1.7 Metrology basics we must respect

- **Error budget and uncertainty reporting:** GUM JCGM 100:2008 (law of propagation, k = 2 expanded uncertainty) and JCGM 101 (Monte Carlo) [43] [O page].
- **Repeatability vs accuracy:** VIM JCGM 200:2012 separates trueness (bias) from precision (repeatability); our shared gain error is trueness, per-lift scatter is precision. [43]
- **Verification vs trade grade:** R76 classes and MPE [11]; in-service MPE is double. Trade grade needs type approval and a notified body.
- **Dynamic weighing:** needs a stable window and tilt/vibration gating: the R51 certificate [12] shows a weighing window and a tilt interlock at 10 %; loader work [3] found boom position and tilt most important; a dynamic-payload-monitor patent (US5067572) notes the small sampling window as an accuracy limit [S].
- **Method agreement:** Bland-Altman difference plots, not correlation [44].
- **Forecast scoring:** interval score for quantile intervals [45] [S].

---

## 2. (a) Ranked methods for a cheap virtual or hybrid scale

| Rank | Method | Expected error [estimate] | Why, and where the literature stops |
|---|---|---|---|
| 1 | **Ticket-anchored, physics-prior plus learned-correction model with per-machine gain, partially pooled across the fleet; golden cohort of scale-equipped machines for training** | Per lift 12-15 % (1 sigma); device-month total 5-6 %; machine gain error about 3.4 % after 20 clean tickets (15 % / sqrt(20)) | Precedent [8] (25 scales train a no-scale model, 4.96 %); physics+ML precedent [1], [3], [6]. No compactor-specific validation exists. |
| 2 | **Stroke-curve features** (work per stroke, peak and hold pressure, return-stroke relaxation, strokes per fill-percent) as density and compressibility covariates | Per lift 8-11 % **if** they carry density information beyond fill | Curve repeatability and springback signature seen in one cardboard baler [16]; learned nonlinear models beat quasi-static ones by 10x+ in SD on excavators [1]. Unproven for compactors, and Europress's fill already uses back-pressure, so the independent information may be small. [assumption] |
| 3 | **Conformal and quantile uncertainty with online recalibration** (CQR + adaptive conformal, Kalman update of gain) | Does not reduce error; makes it honest: target 80 % interval coverage within +-5 points | [34]-[37]; needed for the "uncertainty and human approval" scoring. |
| 4 | **Residual-based anomaly, drift, moisture and contamination flags** (CUSUM/ADWIN on log-residuals; weather and moisture covariates; optional camera) | Detects persistent gain shifts above about 8-10 % within several lifts [estimate] | Moisture is commercially real (10 % rule [25]); sensors are R^2 0.76 [24]; vision contamination near-expert [26]. No pressure-curve material classifier in literature. |
| 5 | **Cheap physical anchor on a subset** (load cells on 2-5 % of machines) | +-1-2 % on those machines [estimate; other lens] | Gives labels for ranks 1-2. Not a scientific question; see weighing-engineer. |

**Not recommended:** excavator-style "pressure times lever arm equals weight" ([7] reports 20-40 % errors even there) and any claim of legal-for-trade accuracy.

**Error budget behind rank 1** [estimate, 1 sigma, % of lift]:

| Source | Uncalibrated | Ticket-calibrated |
|---|---|---|
| Fill estimate (+-5 points, Tommi) and within-machine density scatter, combined | 15 (weighing-engineer reports 14.6 % implied-density CV on synthetic data) | 12-15 (8-11 with curve features, hypothesis) |
| Machine gain and offset | 10 | 3.4 (n = 20 tickets) |
| Moisture not seen by pressure | 5-7 | 5-7 (about 3 with weather or NIR) |
| Ticket noise leaking into calibration | - | 1.3-2.7 |
| **Total (RSS)** | about 20 | about 13-16, or 9-12 with curve features |

Share of lifts within +-10 % / +-12 % if errors are Gaussian: sigma 13 % gives 56 % / 64 %; sigma 9 % gives 73 % / 82 %. Month total with 6-8 lifts, random 12 % per lift and shared gain 3.4 %: sqrt(12^2/n + 3.4^2) = 5.4-6.0 %. Only the random terms average out. **Cross-check with the weighing-engineer file:** its calibrated +-6.6 % per lift is at the optimistic end of what [8] supports (4.96 % needed direct moisture, bale diameter and 25,000 labels).

---

## 3. (b) Recommended model structure

For machine m, stream s, completed fill period k (between emptyings), observed net ticket mass y_k with relative noise sigma_t,k.

1. **Physics prior (volume x density):** M0_k = V_m * phi_k * rho_s(P_k), with Kawakita density rho_s(P) = rho0_s (1 + bP) / (1 + (1 - a) bP), where P_k is a robust end-of-stroke pressure and phi_k the existing Europress fill fraction. If P adds nothing beyond phi, drop to constant rho_s. Alternative or complement: work per stroke W_i = integral of F dx with F = p_A*A_A - p_B*A_B - F_fric (ram force from both chambers); charge mass from W_i divided by a fitted specific compaction work, summed since last emptying (container re-zeroes at each emptying). [assumption: bore areas known; fixed-displacement pump unknown]
2. **Learned correction in log space:** ln y_k = ln M0_k + alpha_m + g(z_k) + eps_k, with g a gradient-boosted model (monotone constraints on peak and hold pressure and stroke count), eps_k ~ N(0, sigma_m^2(phi)).
3. **Fleet pooling:** alpha_m ~ N(mu_s, tau_s^2). Posterior mean alpha_hat_m = (n_m * abar_m / sigma^2 + mu_s / tau_s^2) / (n_m / sigma^2 + 1 / tau_s^2). New machines start at mu_s.
4. **Online calibration (Kalman, local level):** alpha_t = alpha_{t-1} + w, w ~ N(0, q). At each valid ticket: R = sigma_m^2 + sigma_t^2, K = P / (P + R), alpha <- alpha + K * (ln y_obs - ln M_hat), P <- (1 - K) * P + q. Gate out tickets that are combined loads, stored tare, or flagged side waste; use a Student-t or Huber residual. [pattern from [38], [41]]
5. **Uncertainty:** Mondrian split-conformal on log-residuals by stream and fill bin: q_hat = the ceil((n+1)(1-delta))/n quantile of |r|; interval M_hat * exp(+-q_hat); update delta online with ACI: delta_{t+1} = delta_t + gamma * (delta - 1[y_t outside C_t]). Finite-sample coverage at least 1 - delta under exchangeability [34].
6. **Aggregation:** T = sum of M_hat_k; Var(T) is approximately sum of sigma_k^2 + (T * sigma_alpha)^2, so report the gain term separately.
7. **Anomaly layer:** CUSUM or ADWIN on r_k per machine; persistent shift means drift or calibration fault; isolated large residual means side waste, moisture or combined load.

**Feature list** (evidence tag in brackets):

| Group | Features |
|---|---|
| Stroke curve | Peak pressure, hold pressure and its decay [16 relaxation], work per stroke, rise slope, stroke time or end-of-stroke position, return-stroke plateau, strokes per fill-percent [all hypotheses] |
| State | Fill fraction [fact, Tommi], cycles since emptied, hours since emptied, previous residual |
| Machine | Container volume, equipment class, stream, age, installed gain alpha_m |
| Thermal | Oil temperature (viscosity and seal friction: [5], [7], US8794135B1) [assumption: logged] |
| Moisture and weather | Rain or humidity over last 72 h, outdoor staging flag; cardboard moisture rule [25] |
| Context | Weekday, site type, previous lift mass |

---

## 4. (c) Validation protocol (grounded in how the papers validated)

| Item | Protocol | Grounding |
|---|---|---|
| Split | Leave-one-machine-out as the primary test; rolling-origin time split for drift; leave-one-stream-out for transfer. Never random row splits. | Blocked CV for hierarchical data [40]; [8] reports a "separate test set" without saying how, which we should not copy; [3] reports on unseen loads (11,660 kg held out). |
| Labels | Single-load tickets only, WEIGHED tare preferred, no side waste; remove combined and equal-split allocations. | Dataset has `allocation_method` and `tare_method`; ticket noise from [11]: +-16 kg RSS initial, +-33 kg in service for net with weighed tare [estimate]. |
| Baselines | B0 fill x V x typical density; B1 per-stream constant density; B2 B0 plus per-machine median gain; B3 full model. | [1] benchmarked against quasi-static and commercial systems. |
| Metrics | Bias (mean error), MAE kg, median and P90 absolute percentage error, WAPE, RMSE; mean + SD of error as in [1]; device-month tonnage error; 80 % and 90 % interval coverage and mean width; interval score [45]. | [3] 95 % bounds; [8] MRE, MAE, r; [1] mean + SD. |
| Agreement | Bland-Altman on log-ratio ln(model / ticket), bias and limits of agreement (mean +- 1.96 SD) reported as %, by stream and by mass band. | [44]. |
| Ground-truth deconvolution | sigma_model^2 = sigma_obs^2 - sigma_ticket^2 (assuming independence). | Applies to [8]: sqrt(4.96^2 - 2.9^2) is about 4.0 % if independent. |
| Ablations | Calibration tickets per machine k = 0, 3, 5, 10, 20; with and without curve features; with and without moisture covariates. | Shows the value of each data source; k-curve answers "how many tickets". |
| Acceptance | Median lift error <= 10 %; 80 % interval coverage 75-85 %; device-month bias <= 5 % for >= 80 % of device-months; no machine with bias > 10 % after 3 tickets. | Aligned with Tommi's ballpark and the weighing-engineer acceptance list. |
| Pilot size | About 10 machines x 20-30 clean tickets; with per-lift SD 15 %, SE of machine gain is about 3-3.4 %. | [estimate] |

---

## 5. (d) What the synthetic dataset can and cannot test

**Can test (pipeline and statistics):**
- Hierarchical gain pooling, Kalman recalibration, ticket gating (323 tickets in the quickstart; 260 single-load matches to collections [data]).
- Conformal coverage and its width under known simulator noise (about max(15 kg, 1.4 %)), and drift/fault detection using `labels_dev_anomaly_labels` (SENSOR_DRIFT, SENSOR_DEGRADED, WEIGHT_DISCREPANCY: 32 rows in the quickstart; MOISTURE_HEAVY_LOAD only 4 rows with 12-20 % extra water).
- Leave-one-device-out and time-forward evaluation mechanics, and the sparse-ticket ablation.
- My quick probes [data, quickstart, 50 devices]: fill_before x V x typical density gives median absolute error 18.1 % (mean 36.5 %, n = 278, per-stream log-ratio SD 0.39-0.49); device before-minus-after vs single-load ticket gives median 4.2 %, mean 10.7 %, P90 29.3 %, bias -79 kg (n = 260). The weighing-engineer reports 15.9 % (fill-only, competition set). Treat fill-only as the bar to beat.

**Cannot test:**
- Whether pressure curves contain mass information: there are none, and `press_load_index` is derived from the device's own fill estimate (correlation 0.98 with fill in my probe; ASSUMPTIONS item 8), so it adds no independent pressure information.
- Real compaction physics: density-pressure-moisture laws, springback, oil temperature, seal friction, cross-model transfer. Any ML will learn the simulator's rules, so accuracy there is circular.
- Legal metrology, true weighbridge behaviour beyond the simulated tare and allocation quirks, real wet-cardboard weight gain (the 4 moisture rows are a labelled scenario).
- The private `truth/` tables (true mass, sensor gain) are described in the data dictionary but are not in the packs; only tickets exist as references.

Recommend a **synthetic pressure-curve generator only to unit-test the code**, labelled as such in the demo.

---

## 6. (e) Citation table (paste-ready), with licence and permission notes

"Cite only" = we reference and summarise, we do not copy text, figures or code. All papers below are cite-only unless the note says otherwise.

| ID | Reference | URL / DOI | Status | Licence / use note |
|---|---|---|---|---|
| [1] | Werner L., Eyschen P., Costello S., Micarelli P., Hutter M. (2025). Calibrated Dynamic Modeling for Force and Payload Estimation in Hydraulic Machinery. arXiv:2510.11574 | https://arxiv.org/abs/2510.11574 | O | CC BY-NC-ND 4.0: cite only, no figure reuse. |
| [2] | Ferlibas M., Ghabcheloo R. (2021). Load weight estimation on an excavator in static and dynamic motions. SICFP'21, Linkoping | https://ecp.ep.liu.se/index.php/sicfp/article/view/30 ; doi:10.3384/ecp182p90 | O | Licence not stated on page: cite only. |
| [3] | Savia M., Koivo H. (2002). On-line payload determination of a moving loader using neural networks. IFAC 2002 | https://skoge.folk.ntnu.no/prost/proceedings/ifac2002/data/content/02553/2553.pdf | O | IFAC copyright: cite only. |
| [4] | Volvo CE Load Assist (OEM Off-Highway press release); Cat Production Measurement (2015 release) | https://www.oemoffhighway.com/electronics/smart-systems/press-release/21008486/volvo-construction-equipment-volvo-pushes-load-assist-realtime-onboard-weighing-accuracy-to-1 | V, S (page returned 403) | Vendor claims: say "vendor-reported". |
| [5] | US10982415B2 CQMS Pty Ltd. System and method of calculating a payload weight (granted 2021-04-20) | https://patents.google.com/patent/US10982415 | O | Public document, cite only. In force status not checked. |
| [6] | RWTH Aachen dissertation: A Method for Dynamic Payload Estimation in Hydraulic Excavators (2022/23), doi:10.18154/RWTH-2023-00533 | https://publications.rwth-aachen.de/record/862531 | S | Not read; cite only after reading. |
| [7] | EP0496166A2 Mobile Computing Corp. Load measuring system for refuse trucks (filed 1991-12-20) | https://data.epo.org/publication-server/rest/v1.2/patents/EP0496166NWA2/document.pdf | O | Public document. |
| [8] | Mansouri M., Puckmayr D., Riegler-Nurscher P. (2025). Predictive model for hay and silage bale weight estimation. GIL 2025, LNI P358, pp. 315-320 | https://dl.gi.de/items/24c3be51-a52a-41b3-b316-b5003080dcae ; doi:10.18420/giljt2025_35 | O | Licence not stated: cite only. |
| [9] | Yin J. et al. (2023). Design and Experiments of a Real-Time Bale Density Monitoring System Based on Dynamic Weighing. Sensors 23(4):1778 | https://doi.org/10.3390/s23041778 | O (abstract via Crossref) | CC BY 4.0: quoting with attribution allowed. |
| [10] | Kadam P. (2025). A Load Cell-Free Solution for Weighing. SAE 2025-28-0346 | https://saemobilus.sae.org/papers/a-load-cell-free-solution-weighing-2025-28-0346 | O abstract | SAE copyright: cite only. |
| [11] | OIML R 76-1:2006 Non-automatic weighing instruments | https://www.oiml.org/en/files/pdf_r/r076-1-e06.pdf | O | OIML publication, freely downloadable: cite only. |
| [12] | OIML Certificate R51/2006-GB1-16.01 (AMCS Ltd., Vehicle Data Hub, 2016-04-07) | https://www.oiml.org/en/files/pdf_c/r051-2006-gb1-2016-01.pdf | O | Certificate may be quoted only "in full" per its note; paraphrase and cite. |
| [13] | Resource Media (2020-01-31). VWS bin-weighing system awarded EU approval | https://resourcemedia.eco/article/vws-bin-weighing-system-awarded-eu-approval | O | Trade press, vendor-sourced. |
| [14] | US6422800B1 Stress-Tek. On-board weighing system for front loading refuse vehicles | https://patents.google.com/patent/US6422800 | O | Public; expired per Google (assumption, not legal conclusion). |
| [15] | Directive 2014/32/EU Annex VIII (MI-006); UK Catchweighing Regulations schedule (R51 classes) | https://legislation.gov.uk/eudr/2014/32/annex/VIII/data.htm?view=plain ; https://legislation.gov.uk/nisr/2006/154/schedules/data.html | S | Archived UK copies; use EUR-Lex for the authoritative text. |
| [16] | Tudor P., Zabava B.-S., Voicu G., Lazea M.-B., Constantin G.-A. (2023). Resistance to compaction/baling of recyclable cardboard waste using stationary horizontal presses. J. Eng. Studies Res. 29(3) | https://jesr.ub.ro/journal/article/view/407 | O | Cite only. Flag the tf*m vs kJ inconsistency. |
| [17] | Voicu G. et al. (2023), Annals of Faculty Engineering Hunedoara XXI(3); Lazea M.-B. et al. (2022), same journal XX(3) | https://annals.fih.upt.ro/pdf-full/2023/ANNALS-2023-3-19.pdf ; https://annals.fih.upt.ro/pdf-full/2022/ANNALS-2022-3-28.pdf | O | Cite only; low-quality lab-scale data. |
| [18] | Sanchez S., Colomina J., Phi R., Masia J. (2002). Definition of a methodology for compactors and baler presses selection. WIT, Waste Management and the Environment | https://www.witpress.com/Secure/elibrary/papers/WM02/WM02065FU.pdf | O | WIT copyright: cite only. |
| [19] | Heckel R.W. (1961) Trans. Metall. Soc. AIME 221:671-675; Kawakita K., Ludde K.H. (1971) Powder Technol. 4:61-68; Denny P.J. (2002) Powder Technol. 127:162-172 | no stable URL used | S (citations confirmed via secondary listings) | Equations are public knowledge; cite only. |
| [20] | US5299142A Marathon Equipment Co. Determining the fullness of a waste compactor (1994) | https://patents.google.com/patent/US5299142 | O | Expired per Google; cite only. |
| [21] | US6123017A PMDS LLC. Evaluating the fill state of a waste container (2000) | https://patents.google.com/patent/US6123017 | O | Expired per Google; cite only. |
| [22] | US6738732 (One Plus Corp, 2004); US8794135B1 (One Plus Corp, 2014) | https://patents.google.com/patent/US6738732 ; https://patents.google.com/patent/US8794135B1/en | O (US8794135 partly read) | US8794135B1 listed active to about 2028: freedom-to-operate check by Europress counsel before claiming pressure-based diagnostics. Not legal advice. |
| [23] | FHWA. Intelligent compaction for soils and subbase (tech brief) | https://www.fhwa.dot.gov/pavement/ic/techbriefs/ic_soils.pdf | S | US government work. |
| [24] | Silveira A., Cardoso J., Correia M.J., Martinho G. (2021). Moisture Measurement in Paper and Cardboard Packaging Waste Bales for Recycling. Appl. Sci. 11(10):4586 | https://doi.org/10.3390/app11104586 | O (abstract) | CC BY 4.0. |
| [25] | CEPI (April 2018). Paper for Recycling Quality Control Guidelines (revised), quoting EN 643 | https://www.cepi.org/wp-content/uploads/2021/09/REC-18-024-002.pdf | O | Cite only; EN 643 itself is a paid standard. |
| [26] | Ibrahim K. et al. (2019). ContamiNet: Detecting Contamination in Municipal Solid Waste. arXiv:1911.04583 | https://arxiv.org/abs/1911.04583 | O abstract | Cite only. |
| [27] | DFKI AI-enabled bio-waste contamination scanner; Mewada et al., IEEE Access 2024 | https://dfki.de/fileadmin/user_upload/import/11903_AI_enabled_bio_waste_contamination-scanner.pdf ; https://doaj.org/article/564aedf946a640a69d340fdc8acf1809 | S | Detail unverified. |
| [28] | Proenca P.F., Simoes P. (2020). TACO: Trash Annotations in Context. arXiv:2003.06975 | https://arxiv.org/abs/2003.06975 | S | Dataset reported as CC BY 4.0 by mirrors, toolkit MIT; not used by us. |
| [29] | Ahmed S., Mubarak S., Du J.T., Wibowo S. (2022). Forecasting the Status of Municipal Waste in Smart Bins Using Deep Learning. IJERPH 19(24):16798 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9779277/ | O | CC BY 4.0. |
| [30] | Pollak A., Gupta A., Gohlich D. (2024). Optimized Operation Management With Predicted Filling Levels of the Litter Bins ... IEEE Access 12:7689-7703, doi:10.1109/ACCESS.2024.3352436 | https://doaj.org/article/9d42004d236a47f7bbdda21ce253d882 | S | Cite only. |
| [31] | Cetkin B. et al. (2024). Spatial Impulse Response Analysis and Ensemble Learning for Efficient Precision Level Sensing. arXiv:2405.19341 | https://arxiv.org/abs/2405.19341 | O abstract | Cite only. |
| [32] | Ferrer J., Alba E. (2018/19). BIN-CT. arXiv:1807.01603 | https://arxiv.org/abs/1807.01603 | O abstract | Cite only. |
| [33] | Vicentini F. et al. (2009). Sensorized waste collection container for content estimation and collection optimization. Waste Manag. 29(5):1467-1472 | doi:10.1016/j.wasman.2008.10.017 | Bibliographic data only (Crossref) | Abstract not read: do not state findings. |
| [34] | Angelopoulos A.N., Bates S. (2021). A Gentle Introduction to Conformal Prediction. arXiv:2107.07511 | https://arxiv.org/abs/2107.07511 | O abstract | Cite only. |
| [35] | Romano Y., Patterson E., Candes E. (2019). Conformalized Quantile Regression. arXiv:1905.03222 | https://arxiv.org/abs/1905.03222 | O abstract | Cite only. |
| [36] | Gibbs I., Candes E. (2021). Adaptive Conformal Inference Under Distribution Shift. arXiv:2106.00170 | https://arxiv.org/abs/2106.00170 | O abstract | Cite only. |
| [37] | Xu C., Xie Y. (2021/23). Conformal prediction for time series. arXiv:2010.09107 | https://arxiv.org/abs/2010.09107 | O abstract | Cite only. |
| [38] | Kadlec P., Gabrys B., Strandt S. (2009). Data-driven soft sensors in the process industry. Comput. Chem. Eng. 33(4):795-814; Kadlec P., Grbic R., Gabrys B. (2011). Review of adaptation mechanisms for data-driven soft sensors | https://eprints.bournemouth.ac.uk/8498/ | S | Cite only. |
| [39] | Bifet A., Gavalda R. (2007). Learning from Time-Changing Data with Adaptive Windowing. SIAM SDM, pp. 443-448, doi:10.1137/1.9781611972771.42 | doi link | S | Cite only. |
| [40] | Roberts D.R. et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography 40(8):913-929, doi:10.1111/ecog.02881 | doi link | S | Cite only. |
| [41] | Xiang, Tang, Zhu (2016), Atmos. Meas. Tech. 9:347 (title not retrieved); Takruri, Challa, Chakravorty, recursive Bayesian auto-calibration in drift-aware WSNs | https://amt.copernicus.org/articles/9/347/2016/ ; https://opus.cloud1.lib.uts.edu.au/handle/10453/15437 | S | Cite only, mark unverified detail. |
| [42] | Karniadakis G.E. et al. (2021). Physics-informed machine learning. Nat. Rev. Phys. 3:422-440, doi:10.1038/s42254-021-00314-5 | doi link | S | Cite only. |
| [43] | JCGM 100:2008 (GUM); JCGM 101:2008; JCGM 200:2012 (VIM) | https://doi.org/10.59161/JCGM100-2008E ; https://doi.org/10.59161/JCGM101-2008 ; https://doi.org/10.59161/JCGM200-2012 | O (BIPM listing) | BIPM copyright: cite only. |
| [44] | Bland J.M., Altman D.G. (1986). Lancet 1(8476):307-310 | https://pubmed.ncbi.nlm.nih.gov/2868172/ | S | Cite only. |
| [45] | Gneiting T., Raftery A.E. (2007). Strictly proper scoring rules, prediction, and estimation. JASA 102:359-378, doi:10.1198/016214506000001437 | doi link | S | Cite only. |

**Libraries we may reuse** (licence checked on the project pages, 2026-11-06): MAPIE (conformal intervals) BSD-3-Clause; River (online learning, drift detectors) BSD-3-Clause; scikit-learn BSD-3-Clause; LightGBM MIT; PyMC (hierarchical Bayes) Apache-2.0; statsmodels (quantile regression, state space) modified BSD-3; ruptures (change points) BSD-2-Clause. All allow commercial use with notice retention. Project pages: github.com/scikit-learn-contrib/MAPIE, online-ml/river, scikit-learn/scikit-learn, microsoft/LightGBM, pymc-devs/pymc, statsmodels/statsmodels, deepcharles/ruptures. **Open datasets:** none directly usable for compactor mass; the Wyndham bin series in [29] (data.gov.au, licence not checked) and TACO [28] are not needed.

---

## 7. (f) Five quotable facts for the pitch

1. **"Pressure-based payload estimation reaches about 1 % of full scale on a 25 t machine after about 30 minutes of staged calibration, versus 101.7 kg mean error for a commercial system and 2.3 t SD for the quasi-static method."** (Werner et al. 2025, arXiv:2510.11574 [1].) Say it is gravity-based, so it shows the calibration approach works, not that compactors reach 1 %.
2. **"A model trained on 25,000 bales from 25 scale-equipped machines estimates bale weight on machines without scales with 4.96 % mean relative error and r = 0.96, using existing sensors only."** (Mansouri et al. 2025 [8].) The same design as our golden cohort plus fleet model.
3. **"Pressure alone is not weight."** Pressure-based weighing of a lifted refuse container can be off by 20-40 % when the load's centre of gravity is not where assumed (applicants' statement, EP0496166 [7]); compactor patents say pressure-based fullness is inaccurate when the container is relatively empty (US5299142 [20]). Hence calibration against weighbridge tickets, not a physics-only claim.
4. **"Water weight is already a commercial fact."** EN 643, as quoted by CEPI, allows 10 % moisture in recovered paper and lets buyers claim back the excess weight [25]; dielectric plate meters correlate with oven drying at R^2 = 0.76 over 48 bales [24]. Moisture flags are therefore worth money.
5. **"Legal-for-trade bin weighing is certified at 300-600 kg with 0.5-1 kg resolution; a weighbridge is class III with +-0.5/1/1.5 e initial limits, doubled in service."** (OIML certificate R51/2006-GB1-16.01 [12]; OIML R76-1 Table 6 [11].) Our virtual scale is explicitly indicative; the weighbridge stays the legal reference and our calibration anchor.

---

## 8. Gaps, negative results, and open items

- **Negative result:** no peer-reviewed mass-from-pressure study for compactors or balers found; no pressure-curve material classifier found; no hierarchical-fleet-plus-online-sparse-reference calibration paper found. Say so in the submission as "limitations".
- **Items I could not open** and therefore do not quote beyond snippets: [4], [6], [15], [19], [23], [27], [30], [33], [38]-[42], [44], [45]. A pitch-critical check before use: [4] (vendor ±1 %).
- **Source quality warnings:** [16] has a unit inconsistency; [17] is lab-scale; [29] headline favours LSTM on training metrics; [8] does not say how its test set was split.
- **Biggest open question for Tommi:** Does Europress archive the full per-stroke pressure-vs-time trace centrally (at roughly 10 Hz or better), and can it be exported for 10-30 pilot machines together with at least 20 single-load, weighed-tare weighbridge tickets each? Without that pair, rank 2 cannot be tested and rank 1 falls back to fill-only plus tickets.
- **Also needed:** whether the fill algorithm already consumes the information in peak pressure (if so, curve-shape features must supply the independent density signal), and whether oil temperature is logged.
- **Scratch analysis:** `/tmp/sci_work/scripts/ds_probe.py` and `ds_probe2.py` (read-only on the quickstart CSVs; not part of the repo).
