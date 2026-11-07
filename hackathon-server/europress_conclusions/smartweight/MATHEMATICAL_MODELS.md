# MATHEMATICAL MODELS

These are the derivations behind the simulation in `simulation/`.

**Evidence tags:**
- `[derived]` follows from physics or from other tagged inputs.
- `[assumed: why]` is a sensitivity assumption.
- `[simulated]` is a simulation output (`results/`).
- `[measured: source]` is measured; the dataset is synthetic.

**SI units throughout:** mass kg, force N, pressure Pa (1 bar = 10⁵ Pa), length m.

## 0. Target quantity and what it is for

The target is **m**, the mass of waste removed at one emptying (kg). It is the quantity the operator bills on (gross − tare at the weighbridge).

The purpose is verification: an estimate m̂ independent of the operator, used to check that the billed tonnage m_bill is right (user clarification, ISSUES #1).

**Performance target (main prompt §3):** |m̂ − m| ≤ 2–5 % of m. The reference case is ±100 kg at 3,000 kg, i.e. 3.3 %. The research acceptance criterion is P95(|m̂ − m|/m) ≤ 5 % on loads ≥ 1 t, with ≤ 2 % as stretch.

The verification error that matters is the difference between the estimator error and the ticket error:

Δ = m_bill − m̂ = (m + ε_ticket + b_operator) − (m + ε_est)

A systematic operator bias b_operator is detectable with N pickups if

 b > z₁₋α · sd(ε_ticket − ε_est)/√N + |bias(ε_est)|

where the median-of-N statistic is used in `results/verification_power.csv`. **An estimator whose calibration uses the operator's tickets has bias(ε_est) ≈ b_operator, so it cannot detect a constant b_operator** `[derived]`.

---

## 1. Stage-1 screening: which principles can identify m at all?

Mass enters physics only through **gravity** (F = mg) and **inertia** (F = m·a). Every other observable responds to volume, stiffness, friction or water content, not to mass as such.

| Principle | Observable | Relation to m | Identifiable? | Verdict |
|---|---|---|---|---|
| Load cells under **all** supports | ΣR_i | ΣR_i = (m + m_tare)g | yes, directly | keep (Model A) |
| Load cells / pins at **some** supports | R_rear | R_rear = W(L − x_G)/L | only if the centre of mass x_G is known | keep as counterexample (A′) |
| Strain on load-carrying members | ε = σ/E | ε ∝ local internal force, a share of W that depends on the load distribution | yes only for shear sections at every support | keep (A″) |
| Lift-cylinder pressure (hooklift) | Δp·A | moment about the pivot: Δp·A·r = W·x_G + friction + dynamics | W·x_G only | keep (Model B) |
| Ram compaction pressure / work | p, ∫F dx | depends on stress–density law, friction and history | **no** (moisture, material) | keep to prove (Model C) |
| Motor current / power | P_el ≈ pQ/η | as C, plus efficiency | **no** | variant of C |
| Fill level × density | V·f | m = ρ_eff·V·f | only if ρ_eff is known per load | baseline (Model D) |
| Vibration / natural frequency | ω = √(k/m) | m = k/ω² | in principle; k changes with packing, contact and ground | rejected: k unknown and nonlinear, compacted waste damps strongly `[assumed]` |
| Acoustics, camera, ToF, humidity | volume, appearance, RH | context only | no | context sensors only |
| Inertial (shake test) | F = m·a | needs a known force excitation | impractical on a 6–15 t unit | rejected |

The three strongest directions taken to Stage 2:
1. Model A (direct, all supports).
2. Model B (hooklift lift pressure).
3. The firmware-only route via Models C/D with ticket anchors.

Model E fuses C and D.

---

## 2. Model A: direct gravitational-load sensing

### 2.1 Geometry and equilibrium

A container (DUO) or a complete unit (COMBI) rests on supports i = 1…n at positions (x_i, y_i). Its total weight is W = (m + m_T + m_s)g, where:
- m_T is the tare, the unit's own mass.
- m_s is snow or ice on the roof.

With the ram retracted and no horizontal external load, equilibrium gives:

 Σ R_i = W − F_bypass                (vertical)
 Σ R_i x_i = W x_G,  Σ R_i y_i = W y_G   (moments)

F_bypass is any vertical force carried by an unmeasured path:
- the docking lock or seal to the press unit (DUO)
- the power cable or hydraulic hose
- a stop or guide in friction contact
- ice frozen to the ground.

**Identifiability.** With n = 3 the supports are statically determinate: ΣR_i = W for any (x_G, y_G). With n ≥ 4 they are indeterminate. R_i then depends on ground flatness and stiffness, but **ΣR_i is still W**. So every support must be measured. The individual readings carry no extra information about W; they reveal x_G and y_G (useful for diagnostics). If one support is unmeasured, W cannot be found without x_G (§2.4).

### 2.2 Sensor model

Load cell i outputs a ratiometric signal:

 u_i = S_i · R_i / R_cap + z_i(T) + n_i   [mV/V]

- S_i = rated output (e.g. 2 mV/V at capacity R_cap).
- z_i(T) = z_i0 + TK0_i (T − T_0) is the zero drift.
- n_i is noise.

The span also drifts, by TKC (% of reading per K).

The digitised sum after corner adjustment (k_i) and system calibration (c) is:

 Ŵ = c Σ k_i u_i

### 2.3 Estimator and calibration

**Net-by-difference** (auto-tare at each empty return):

 m̂ = [Ŵ(t_full) − Ŵ(t_empty)] / g

This removes:
- the tare
- the constant parts of z_i
- the tare's centre-of-mass effect.

**Calibration**, done once at commissioning with test weights M_j at several positions (OIML R76 eccentricity test):
- Corner factors k_i come from placing a test mass over each support in turn (least squares on Σ k_i u_ij = M_j g).
- The span c comes from a known total mass.

Residual errors:
- a corner-gain mismatch δk_i, which turns into error when the load distribution changes;
- a span error δc.

**Error model** for a load whose content shares are s_i (Σs_i = 1):

 m̂ − m = m Σ s_i(δk_i + δc) − ε_p s_front m + TK0_Σ·ΔT + Δm_s + n_Σ√2 + hysteresis

with:
- ΔT = temperature change between the empty and full readings;
- ε_p = parasitic share at the front (docking) supports;
- Δm_s = change in snow or ice between the two readings.

The Jacobian is ∂m̂/∂δk_i = s_i m, ∂m̂/∂ΔT = TK0_Σ, ∂m̂/∂Δm_s = 1, ∂m̂/∂ε_p = −s_front m. The variance is

 σ_m² = JΣJᵀ = m² Σ s_i² σ_k² + m² σ_c² + (s_front m)² σ_εp² + TK0_Σ² σ_ΔT² + σ_snow² + 2σ_n² + σ_wind²

At 3,000 kg (results/uncertainty_summary.csv, linear vs Monte Carlo):
- Certified C3 system: σ ≈ 23 kg, P95 ≈ 45 kg. 92 % of the variance is **snow/ice**; cell gains contribute under 1 % `[simulated]`.
- Cheap cells and electronics: σ ≈ 30 kg, P95 ≈ 60 kg. Snow 54 %, uncompensated temperature drift 29 % `[simulated]`.

### 2.4 Fewer sensors (A′): two rear cells or pins, front unmeasured

Supports are at x = 0 (rear, measured) and x = L (front, a pivot). Then

 R_rear = W(L − x_G)/L ⇒ Ŵ = R_rear L/(L − x̂_G)

 ∂ ln Ŵ / ∂ x̂_G = 1/(L − x_G) ⇒ σ_m/m ≈ σ_x/(L − x_G)

The centre of mass of the content x_c moves as the container fills and depends on how the pack lies. A fill-based estimate x̂_c = f̂ L/2 with σ_x ≈ 0.08–0.15 L gives σ_m/m ≈ 13–25 % `[derived]`. **Rejected for the target.** It would be acceptable only if the centre of mass were measured, for example with a third cell.

### 2.5 Strain gauges on structure (A″)

**Strain to voltage.** A full Wheatstone bridge with gauge factor k_g ≈ 2 gives

 U_out/U_exc = k_g·ε·(1 + ν)/2   (two axial gauges + two Poisson gauges)

with:
- ε = σ/E (E_steel ≈ 2.1·10¹¹ Pa);
- σ = M_b·c/I for bending (moment M_b, section modulus I/c);
- τ = V·Q/(I·t) for shear (shear force V).

**Bending gauges on a runner** measure the local moment M_b(x_s). This equals Σ(loads × lever arms) on one side of the section, so it depends on how the waste is distributed along the runner:

 M_b(x_s) = R_rear · x_s − ∫₀^{x_s} q(x)(x_s − x) dx

The share of W "seen" changes with the load distribution. With a sensitivity of 0.45 W and a share CV of 0.12 `[assumed: sensor_sim.yaml]`, error is about 12 % or worse.

**Shear-web gauges** (±45° rosettes on a web between a support and the load) measure the shear force V = R_i, independent of where the load sits beyond the section. That is the load-cell principle built into the structure. Instrumenting the shear section next to **every** support reproduces Model A.

Costs and limits:
- In-situ calibration is needed (test weights), because E, t and gauge placement are not known to better than about 1–3 %.
- The signal is small: τ = V/A_web ≈ 7,500 N / 1.5·10⁻³ m² ≈ 5 MPa at one support for 3 t → ε ≈ 30 µε → U ≈ 60 µV/V `[derived; assumed web area]`. That is about 30 times less than a load cell's 2 mV/V, so the thermal and zero-walk terms dominate.

### 2.6 Billing-grade condition (reference only)

To be certifiable (2014/31/EU, class III) the total instrument error must stay within the MPE at every load:
- MPE = ±1.5e for 2,000e < m ≤ 10,000e at verification, ±3e in service.
- Example: a COMBI unit with Max 15 t and e = 5 kg (n = 3,000) gives an MPE in service of ±15 kg at gross loads above 10 t.

The net is m = Ŵ_full − Ŵ_empty with tare subtracted by the instrument. The full system must meet this under −10…+40 °C (default NAWI range; a wider range must be declared), tilt limits and eccentric loading. The snow term (§2.3) is part of the weighed load and is legally just "load", so it does not violate the MPE; it is only an error for *waste* mass.

---

## 3. Model B: hydraulic lift (hooklift truck)

During the lift the container pivots about the truck's rear roller (x = 0) while the hook (x = L) carries the front. Moment equilibrium of the container about the roller:

 F_hook·L·cos α = W·(x_G cos α − z_G sin α) + I_p·θ̈

The cylinder force at arm angle θ, with geometric lever ratio r(θ), is:

 Δp·A_eff = F_hook·r(θ) + F_fric·sgn(θ̇) + m_arm g r_arm(θ)

A_eff = A_bore − A_rod·(p_rod/p_bore). The estimator, at a fixed angle window with steady speed (θ̈ ≈ 0), calibrated with the empty container (tare) and one known load, is:

 Ŵ_content·x̂_c = [Δp·A_eff − F̂_fric − m_arm g r_arm]·L/r(θ) − m_T g x_T

 m̂ = Ŵ_content / (g·x̂_c)

**Identifiability.** One force about one pivot measures W·x_G, not W. Mass needs a second reaction or a known x_G:

 σ_m/m ≈ √((σ_x/x_c)² + σ_fric² + σ_dyn²)

With x̂_c from fill (σ_x/x_c ≈ 15 %), the centre of mass dominates (results: median error about 12 %) `[simulated]`. Commercial hooklift scales reaching class III use load cells between the subframe and chassis, or several pressure readings over the lift; US11320299 claims mass *and* centre of mass during the lift. Truck hardware is the hauler's, so this cannot be a Europress-owned verification.

---

## 4. Model C: compaction pressure, work and power

### 4.1 Forces on the ram

Ram force F = p_b A_b − p_r A_r. At the plateau of a stroke into the pack, a slice model of the pack in a rectangular channel (cross-section A_f, perimeter P, wall friction μ, lateral stress ratio K) gives (Janssen-type):

 dσ/dx = −(μ K P / A_f)·σ ⇒ σ(x) = σ_face·exp(−μKPx/A_f)

The ram sees **face stress**: σ_face = F/A_f. That depends on:
- the stiffness of the pack at its current density, and
- friction over the packed length.

### 4.2 Material law (stress–density)

The simulation uses ρ(σ) = ρ_l + (ρ_∞ − ρ_l)(1 − e^{−σ/σ_c}) `[assumed: saturating law; the literature supports log-type laws for MSW (SOURCES #47); no fitted OCC law was found]`. Mass then follows:

 m = ρ̄_dry·(1 + w)·V_pack, V_pack = f·V

with:
- w = water fraction carried by the solids (kg water per kg dry);
- ρ̄_dry = effective mean density of the dry skeleton;
- f = fill.

### 4.3 Estimator

 σ̂ = (p̂ − p_loss(T_oil)) A_b/A_f,  p_loss = p_0 e^{c(40 − T_oil)}

 m̂_C = ρ(σ̂; θ̂_mat)·f̂·V

θ̂_mat = (ρ_l, ρ_∞, σ_c) is the nominal material law for the declared stream.

### 4.4 Identifiability proof and counterexamples

Observations y = (p, f). Unknowns θ = (m, ρ_∞, σ_c, w). The Jacobian ∂y/∂θ has rank ≤ 2 < 4, and in particular

 ∂p/∂w = 0, ∂f/∂w = 0, but ∂m/∂w = m/(1+w) ≠ 0

So water mass is **unobservable** by pressure and fill: m is not identifiable `[derived]`.

**Counterexample 1 (moisture)** (results/identifiability.json):
- 20 m³ container, fill 0.75, face stress 94 kPa → dry cardboard pack 2,850 kg.
- The same pack with 20 % absorbed water weighs **3,420 kg**.
- Same pressure curve, same fill.

**Counterexample 2 (material law):**
- A batch with σ_c 30 % higher (stiffer: more corrugated board, less soft paper) at the same face stress and fill is about 10 % lighter.
- Pressure cannot tell "softer and heavier" from "stiffer and lighter" without that batch's law.

**Compaction work.** W_c = ∫F dx = A_f ∫σ dx. Per stroke this equals the energy to reduce the volume of the newly fed charge, W_c ≈ m_charge ∫σ d(1/ρ). Its relation to mass needs the same material law and is additionally confounded by friction, springback and elastic energy in the pack (Voicu 2023: the force–stroke trajectory is random for cardboard). No proportionality to mass is claimed.

**Motor power** P_el = pQ/η_total + P_0 adds the unknown efficiency η and the idle power P_0. It is never more informative than pressure `[derived]`.

**Uncertainty budget at 3 t** (results/uncertainty_budget.csv):

| Condition | σ | Largest variance shares |
|---|---|---|
| Uncalibrated | ≈ 615 kg (20 %) | ρ_∞ (site/batch) 54 %, fill 23 %, moisture 12 %, σ_c 11 % |
| Ticket-anchored | ≈ 450 kg (15 %) | ρ_∞ 39 %, moisture 22 %, σ_c 20 %, fill 17 % |

Sensor noise and area tolerance together are about 1 % of the variance. **A better pressure sensor does not help.**

**Required accuracy:** to reach P95 ≤ 5 % the total per-load density-law CV must be ≤ 2.6 %, and moisture alone (sd about 7 % `[assumed]`) already exceeds it (results/required_accuracy.csv).

### 4.5 Where the hydraulic signal is still useful

- Relative changes on one machine: friction rise, blockage, a hydraulic leak.
- Cycle work per charge as an infeed counter.
- Detecting a change in material stiffness, for example plastics in a cardboard stream.

These need no mass identifiability (ECONOMIC_OPPORTUNITIES.md).

---

## 5. Model D: volume × effective density

 m̂_D = ρ̂_eff·f̂·V

Calibrating ρ̂_eff per machine from k clean tickets:

 ln ρ̂_eff = (Σ_{j≤k} ln(m_j/(f̂_j V))/σ_r² + ln ρ_table/σ_0²) / (k/σ_r² + 1/σ_0²)

This is a log-normal conjugate update with prior σ_0 = 15 % and per-load scatter σ_r estimated from the pooled anchors.

The error after calibration is bounded below by the **within-machine, load-to-load** density CV. Measured values:
- 7–11 % on the synthetic dataset `[measured: dataset_checks.json C3, synthetic]`.
- 7 % on homogeneous paper/card in WRAP's rear-end-loader data `[measured: WRAP 2010]`.

The dataset's calibrated fill-only baseline has a median error of 5.8–6.2 % and is within ±5 % for only 41–44 % of loads `[measured: dataset_checks.json C7, synthetic]`.

---

## 6. Model E: hybrid fusion

Fusion of estimators with relative error sds σ_j in log space:

 ln m̂_E = Σ_j w_j ln m̂_j,  w_j = σ_j⁻² / Σσ⁻²

This gives σ_E² = (Σσ_j⁻²)⁻¹ **only if the errors are independent**. C and D share the fill input, the site density factor and the moisture, so their errors are strongly correlated. The real gain is small (results: core_comparison.csv, HYBRID_A5 vs FILL_D_A5) `[simulated]`.

The ML comparator is gradient-boosted trees on (fill, plateau pressure, oil T, volume, class, material), trained on golden-cohort machines with reference-scale truth (20 % of machines) and evaluated on unseen machines. It cannot beat the identifiability bound. It learns the fleet-mean law and extrapolates worse to unseen materials (results/heldout_material.csv).

**Bayesian state per machine (implemented in the proposal, not needed for the simulation):**
- State x = ln g (machine gain).
- Random-walk drift: x_t = x_{t−1} + η, η ~ N(0, q²) per month.
- Measurement update at each clean ticket: y = ln(m_ticket/m̂_raw) = x + ν, ν ~ N(0, σ_r²). This is a scalar Kalman filter.
- A CUSUM on the innovations flags a change point (a sensor fault or a material change) instead of absorbing it.

After each emptying the content estimate resets to zero (direct: auto-tare; indirect: pack integral reset).

---

## 7. Output of the recommended estimator (Model A with diagnostics)

For each pickup t:
1. **m̂_t** = Ŵ_full − Ŵ_empty, using the median of a 5–10 s window with the ram retracted, standstill (|dŴ/dt| < 1 e/s), and tilt within limits.
2. **95 % interval:** ±1.96·σ_m, with σ_m from §2.3 using the measured ΔT and a winter flag (snow).
3. **Health:**
   - Each R_i against its own history for the same fill. A dead or drifting cell gives an abnormal centre-of-mass jump (x̂_G outside the container).
   - Zero after emptying within ±k·e.
   - Cross-check with Model D: |m̂_A − m̂_D|/m̂_D > 3σ_D flags a fault, not a billing error.
4. **Trust statement:** "trusted" if the standstill, tilt, temperature, zero and cross-checks pass and the last test-weight check is under 12 months old; otherwise "estimate only" with the reason.
5. **Forecast at the next collection:**

 m̂(t_pickup) = m̂_now + ṁ·(t_pickup − t_now)

 ṁ is a robust slope of m̂ over the last days, using the same machine's weekday profile.

**Verification statistic (per machine, rolling N pickups):**

 D_N = median_N((m_bill − m̂)/m̂)

Flag if D_N > threshold. The threshold is set from honest-period data at a 5 % false-alarm rate (results/verification_power.csv). The flag opens a dispute draft that a person must approve.
