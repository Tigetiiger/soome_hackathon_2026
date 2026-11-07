# SENSOR RESEARCH

This file reviews every sensing technology investigated, answering the 15 questions of spec §4.

**Tags**
- `[EP]` Europress confirms
- `[LIT]` independent literature or standard
- `[VEN]` vendor claim
- `[derived]`
- `[simulated]`
- `[assumed]`
- `[needs physical validation]`

**Prices** are EUR excluding VAT, listed on 2026-11-07, unless marked E (estimate). Full price tables with URLs are in `_research/hardware_prices.md`. Source numbers (#) refer to `SOURCES.md`.

**Simulated accuracy** is P95 |error|/m on loads ≥ 1 t, on unseen machines (`results/core_comparison.csv`). It is **not** field performance.

## 0. Machine facts that decide sensor placement

**Two architectures**
- **COMBI** (mobile): the press and container are one welded unit, lifted whole by hooklift. Container 10–22 m³ [EP #5].
- **DUO** (stationary): the press stays on its legs. A detachable 20–35 m³ container is docked and taken away [EP #6].

**Press data**
- Press force 35/40 t (about 343 kN), 5.5/7.5 kW motor [EP #5–6].
- SMART already records ram pressure curves [EP, briefing], and fill appears to be derived from pressure and cycle counts [EP #8, inference].
- Tilt, GPS and movement sensors and a 4G/5G modem are on board [EP, briefing].

**Load path at rest.** The weight goes through the container's rear rollers and front runner ends or feet into the ground. A DUO container's tare is 2.3–3.0 t [VEN #7], about equal to a 3 t payload. A COMBI unit (press + container) is heavier; its tare is not published [assumed 4.7–6.1 t].

**Compaction forces.** These are horizontal, about 343 kN at the ram, and close inside the structure for a COMBI unit. On a DUO they pass through the press–container docking interface. **Compaction force is not a weight measurement**, and it must not pass through weighing sensors while they are read.

**Load-path changes**
- Hooklift pick-up and set-down cause shock loads.
- During compaction the content's centre of mass moves (the pack grows from the rear door forward).
- Snow and ice add roof load.
- On a DUO, the docking lock may carry vertical force.

**Best measurement phase.** At rest, ram retracted, motor stopped, standstill, and with the tilt sensor in limits. Reading full, then empty after the return, gives net = Δ (auto-tare).

**What generalises across both architectures.** Supports under every ground contact plus net-by-difference works for both. Everything that relies on the ram (Models C/D) is architecture-specific.

---

## 1. Compression / shear-beam load cells under all supports (Model A)

| # | Item | Content |
|---|---|---|
| 1 | Quantity | Vertical support force, N (as mV/V) |
| 2 | Principle | Strain-gauge full bridge in a machined elastic element |
| 3 | Mounting | Under the 4 ground contacts in a docking frame (DUO container) or under the feet/rollers of a COMBI unit; rocker or pendulum load introduction, lift-off and lateral stops |
| 4 | Relation to mass | ΣR_i = (m + m_T + m_snow)g, with no dependence on centre of mass if every support is measured |
| 5 | Model | MATHEMATICAL_MODELS §2: m̂ = c Σ k_i (u_i,full − u_i,empty)/g |
| 6 | Confounders | Snow/ice on the roof; temperature (TK0, TKC); parasitic paths (docking lock, cable, ice to ground); side loads from hooklift set-down; uneven ground (redistributes R_i but not ΣR_i) |
| 7 | Resolution | C3 cells: combined error 0.02–0.03 % Cn, TK0 < 0.004 % Cn/K (ANYLOAD 102ES) [VEN]. System: simulated σ ≈ 23–30 kg at 3 t; P95 1.4 % (approved grade) / 2.3 % (cheap grade) `[simulated]` |
| 8 | Calibration | Test weights: corner (eccentricity) adjustment and span at commissioning; auto-zero at each empty return; a test-weight check every 1–3 years |
| 9 | Retrofit | Moderate. The unit must be lifted onto a new frame; easy as a factory option. DUO docking lock must be vertically compliant |
| 10 | Durability | Stainless welded IP68 cells survive washdown and salt; service range −30…+70 °C [VEN]. Alloy or potted IP67 cells are not recommended |
| 11 | Integration | 4 cells into a junction box, then a transmitter (4–20 mA/Modbus) into the SMART controller. 10–30 V supply from the machine |
| 12 | Cost | 4 cells €1,640–3,240 (USD 440–870 each, L); mounts €400–2,600; transmitter about €195 (L); approved indicator about €715–780 (L). Installed: €3.4–6.3k (non-approved), €5.4–10k (approved) |
| 13 | Install / maintenance | ½–1 day for 2 technicians; annual inspection; re-verification every 3 years if certified [LIT #15] |
| 14 | Benefit combined | Cross-check with Model D catches gross faults (health_check.csv); per-cell shares give the centre of mass and flag a dead cell on 100 % of pickups `[simulated]` |
| 15 | Independent validation | Load-cell weighing is standard metrology (OIML R76/R60) [LIT]. Container scales exist (WeDi K3, Interface, Europress Scale Solutions) [VEN]. **No independent field data on Europress units** `[needs physical validation]` |

**Sensitivity** (`results/sensitivity_lc4.csv`): P95 stays ≤ 5 % until any one of these is exceeded:
- temperature drift: about 3× the assumed value (≈ 6 kg/K uncompensated);
- snow change: about 4.5× (≈ 180 kg mean);
- parasitic share: about 5× (≈ 5 %);
- cell mismatch: about 10×.

The 2 % stretch has **no margin** at cheap grade.

## 2. Load cells or pins at only some supports (A′)

**Principle and placement.** Two load pins replace the rear roller axles; the front is unmeasured. Example: ANYLOAD 535TS 10 t, USD 868 each, accuracy 0.5 % FS [VEN].

**Model.** R_rear = W(L − x_G)/L, so mass requires the centre of mass x_G: σ_m/m ≈ σ_x/(L − x_G) ≈ 13–25 % `[derived]`. Simulated P95 is 25 % `[simulated]`.

**Prior art.** Canalytics US12379240B1 "extrapolates" from one end for this reason [PAT #35]. BACE US11162834B2 instead lifts the container so the pins carry the **full** weight [PAT #33].

**Cost.** €2.4–4.3k installed. Custom pins that fit existing pivots are estimated at €1.5–4k each (E).

**Verdict.** **Rejected for mass**, unless the remaining support is also measured, which turns this into Model A.

## 3. Strain gauges on structure (A″)

**Bending gauges on the runners**
- Signal: local bending moment, a share of W that depends on load distribution (MATHEMATICAL_MODELS §2.5).
- Price: weldable LWK-06 ≈ €250 each (L).
- Error: P95 ≈ 25 % `[simulated]`. Thermal stress in sun-heated steel and zero walk dominate.
- No peer-reviewed accuracy figure was found for frame-mounted gauges on containers [LIT gap]. Vendor statements give 1–3 % FS only with in-situ calibration (hardware_prices.md §3).
- **Verdict: rejected.**

**Shear-web bridges at every support**
- These measure the support shear force, which is load-cell physics built into the structure.
- Cost: €2.4–4.8k installed.
- Error: P95 4.2 % `[simulated]`. The signal is about 30 times smaller than a load cell (about 60 µV/V, `[derived]`), which needs in-situ calibration and leads to zero creep.
- **Verdict: backup** only where cells cannot be fitted.

## 4. Measurement during existing lifting or tipping

**Hooklift cylinder pressure on the hauler's truck (Model B)**
- Principle: Δp·A_eff·r(θ) balances the moment W·x_G about the rear roller.
- Transducers cost £156–198 / €264 (Gems 3100, Danfoss MBS 3000, WIKA A-10, L); IP67 inclinometer €333 (L).
- Identifiability: one force about one pivot measures W·x_G, not W. Simulated P95 is 39 % using a fill-based centre-of-mass estimate.
- Prior art: Hiab US11307080B2 integrates pressure over the lift [PAT #38]; US11320299 claims mass and centre of mass [PAT #39].
- Certified hooklift scales exist: Pfreundt class III/IIII [VEN #26]; Rice Lake TradeRoute USD 18,480 [VEN #29].
- **The truck belongs to the operator being verified**, so this is not independent.
- **Verdict: rejected** as a Europress solution. It is useful as a data source if the operator shares it.

**Europress bin tipper (Scaletipper X1)**
- 440 kg maximum, 1.0 kg accuracy [EP #9].
- It weighs the *input* bin by bin. The sum of inputs is a mass estimate for sites where everything enters by tipper (not general). The error accumulates as √n·σ_bin plus manual throw-ins.
- **Context only.**

## 5. Hydraulic pressure (ram), pressure + position, oil temperature (Model C)

| # | Item | Content |
|---|---|---|
| 1 | Quantity | Ram chamber pressure, bar (existing SMART transducer); stroke time or position; oil temperature °C |
| 2 | Principle | Thin-film or piezoresistive pressure transducer |
| 3 | Mounting | Existing port; oil probe in the tank (depressurised work) |
| 4 | Relation to mass | Pressure gives face stress σ; material law ρ(σ); m = ρ(σ)(1+w) f V. Mass enters only through the material law and the water content |
| 5 | Model | MATHEMATICAL_MODELS §4 |
| 6 | Confounders | Moisture (unobservable), material stiffness (batch/site), wall friction, packing history, oil temperature (flow losses), relief-valve saturation at full |
| 7 | Resolution | Transducer 0.25–0.5 % FS [VEN]. That is irrelevant: sensor noise and area tolerance are about 1 % of the error variance (uncertainty_budget.csv). Simulated P95 ≈ 29–32 % even with 5 ticket anchors |
| 8 | Calibration | Ticket anchors (weighed tare); only the machine *mean* is calibrated |
| 9 | Retrofit | Firmware only (logging 10–20 Hz) |
| 10 | Durability | Existing component |
| 11 | Integration | SMART controller |
| 12 | Cost | €0–30 (firmware); oil probe €20–40 + €40–90 fitting |
| 13 | Install / maintenance | None |
| 14 | Benefit combined | With fill (hybrid): no material gain, because errors are correlated (P95 29.2 % vs 29.0 %) `[simulated]` |
| 15 | Independent validation | Payload weighing from **lift** cylinders reaches ±1–3 % on loaders and excavators [LIT #43, VEN #31]. That is a different, gravitational problem. For **compaction** there is no published mass validation; patents use pressure only for *fullness* [PAT #36–37]; Canalytics states pressure is unreliable across waste types [PAT #35]; cardboard force–stroke is random [LIT #44] |

**Verdict: not identifiable for mass** (counterexample: dry 2,850 kg vs wet 3,420 kg give the same signals). Keep it as a free plausibility check and a hydraulic-health signal.

**Oil-temperature probe (€20–40).** It is the only cheap add-on that measurably helped: the P95 of the anchored pressure estimate fell from 31.7 % to 29.0 % (it removes the cold-oil flow-loss bias). **It still misses the target by about 6×** `[simulated]`.

**Machine learning on the same signals** (gradient boosting, trained on a 20 % golden cohort):
- Unseen machines: P95 34 % with anchors, 49 % without — worse than the physics inversion.
- Plastics excluded from training: P95 248 % and bias +2.9 t on plastics (results/heldout_material.csv).
- Verdict: ML does not beat the identifiability limit and extrapolates badly.

## 6. Motor current / true power

- **Products:** clamp CTs (SCT-013, €5–9, hobby grade) and MID 3-phase meters (Eastron SDM630 €91, Carlo Gavazzi EM24 €281) [L].
- **Model:** P_el = pQ/η + P_0. It adds efficiency and idle-power uncertainty to the pressure model.
- **Result:** P95 29.3 % vs 29.0 % for pressure `[simulated]`. Installation requires a qualified electrician.
- **Verdict:** **no mass value**. It is useful for energy reporting and motor or pump fault detection.

## 7. Distance / fill sensors (ultrasonic, ToF, radar, camera)

**Products**
- MaxBotix MB7389 IP67 €82 (L).
- VEGAPULS C 11 radar €576 (L).
- Benewake TF02-Pro IP65 €102 (L, prototype grade).
- Camera €80–150 (E).

**What they measure.** Volume and fill only.

**Ablation.** A *perfect* fill sensor improves the indirect P95 only from 29 % to 25 % `[simulated]`, because density is the problem, not volume.

**Verdict.** Context sensors. A camera can support contamination flags but cannot establish them (spec §9).

## 8. Accelerometers, vibration, acoustics

**Principle.** Natural frequency ω = √(k/m). Stiffness k depends on packing, contact and ground, and compacted waste is highly damped [assumed]. There is no known validated mass method for containers.

**Uses.** IMU modules (WitMotion HWT901B IP67 USD 85, Elkome tilt €333) serve tilt limits for weighing, shock and overload logging on hooklift handling, and motor or pump vibration.

**Verdict.** Context and health only.

## 9. Temperature, humidity, moisture / dielectric

- **Ambient sensors.** T/RH probes (SHT40 RS485 probe €19.60; IP not stated) [L].
- **Moisture in the waste.** This is the key unobservable term for Models C/D. Ambient RH and rain records do not measure water absorbed in cardboard. Europress notes that measuring moisture reliably in bulk material is hard (briefing). Dielectric probes measure locally, not the bulk of a 20 m³ pack.
- **What does see water.** Only a gravitational measurement sees water.
- **Verdict.** Temperature: yes, for compensating load cells and oil. Moisture sensing: not feasible for the bulk mass.

## 10. Other justified low-cost methods considered

| Method | Idea | Why not |
|---|---|---|
| Weighbridge data via operator API | Use the operator's own certified ticket | It is the thing being verified; it is used only as anchors and comparison |
| Weighing the hooklift truck at pick-up (axle load pads) | Portable pads under the truck at the site | Labour per pickup; operator-side |
| Hydraulic load cells / bladders under supports (US5117373A) | Cheap force via oil pressure | Temperature, leakage; no accuracy advantage over strain cells |
| Re-using SMART's tilt sensor | Tilt check before reading | **Adopted** as part of the Model A procedure |
| Cumulative charge counting (strokes × charge mass) | Mass from the number of charges | Charge mass is unknown and variable (Voicu 2023) |
| **Audit cohort** (a found alternative to "sensors everywhere") | Tier 2 on a sample of machines per operator; pooled comparison with that operator's tickets | **Adopted**: 30 pooled pickups detect a 1 % operator-level bias 98 % of the time (results/audit_cohort_power.txt) |

## 11. Ranking (from SENSOR_COMPARISON.csv)

| Rank | Configuration | Mid cost | P95 (sim.) | Use |
|---|---|---|---|---|
| 1 | Approved 4-cell (Tier 3) | €7,680 | 1.4 % | verification; billing grade after certification |
| 2 | Cheap 4-cell (Tier 2) | €4,850 | 2.3 % | **verification: recommended (audit cohort)** |
| 3 | Shear-web strain at every support | €3,600 | 4.2 % | backup where cells cannot be fitted |
| 4 | Pressure + oil T + anchors (Tier 1) | €95 | 29 % | free estimate, plausibility, diagnostics |
| — | 2 rear pins, bending gauges, hooklift pressure, motor power, ML | €95–3,350 | 25–49 % | rejected for mass |
