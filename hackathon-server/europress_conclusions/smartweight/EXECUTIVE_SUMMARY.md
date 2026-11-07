# EXECUTIVE SUMMARY: Europress SmartWeight

**Date:** 2026-11-07.

**Question.** What is the cheapest sensor set-up that predicts the waste mass hauled per emptying to within ±2–5 % (±100 kg at 3 t), and what else does it reveal?

**Purpose (user clarification, 2026-11-07).** The weight is used to **verify that the client is billed accurately**. It is an independent check of the operator's weighbridge tonnage. It is not the legal billing basis (ISSUES #1).

**Evidence tags.**
- `[measured: source]`
- `[derived]`
- `[simulated]`: physics simulation in `simulation/`, **not** field performance
- `[assumed: why]`

No physical prototype exists. No Europress pressure curve or drawing was available. The hackathon dataset is synthetic and validates no hardware.

## Verdicts at a glance

| Goal (main prompt §3) | Answer |
|---|---|
| **1. Mass at pickup, ±2–5 %** | **Reachable only with gravitational sensing at every support**: four load cells under the container or unit. Simulated P95 is 2.3 % (cheap grade) and 1.4 % (approved grade) `[simulated]`. **It cannot be reached with cheap or indirect sensors.** Ram pressure, motor power, fill × density, rear-only load pins, bending strain gauges, hooklift pressure and ML on those signals all give P95 of 25–49 % `[simulated]`, because mass is **not identifiable** from them `[derived]`. This is stated plainly per §6: **the cheap-sensor version of goal 1 fails.** The goal itself is not redefined. |
| **2. Cheapest hardware that reaches goal 1** | **Tier 2: four stainless IP68 C3 shear beams, €3.4–6.3k installed (mid €4.85k)** `[price: listed parts + assumed labour]`. A shear-web strain-gauge variant (€3.6k, P95 4.2 %) meets 5 % but not 2 %. The low tier (€60–130, firmware + oil probe) gives P95 ≈ 29 %. |
| **3. Economic value** | Verification alone pays for Tier 2 on only about 4–11 % of machines `[D, hypothetical tariffs]`. So deploy Tier 2 as an **audit cohort per operator** (about 5 machines detect a 1 % operator-level bias in 30 pooled pickups, power 98 % `[simulated]`) and the free Tier 1 estimate everywhere. The largest extra € is weight-based pickup timing (≈ €2.5k per device-year on fixed/hybrid schedules, `[D]`, prior analysis). |
| **Billing grade** (main prompt §4) | Billing by weight in Finland requires a class III NAWI: CE+M, type examination, initial verification, and re-verification every 3 years. **Consent does not exempt it** (Act 707/2011 §2–3; our reading, to be confirmed with Tukes) `[measured: Finlex]`. Only Tier 3 can become billing grade. Verification use with uncertified weights is allowed `[measured: Act 707/2011 reading, _research/legal_metrology.md §7]`. |
| **Engineering verdict** | **Promising but unvalidated** for Tier 2 load cells. **Rejected** for indirect and cheap sensing as a ±2–5 % solution. |

## 1. Best overall solution

**Sensors.**
- 4 × stainless, IP68, double- or single-ended shear-beam load cells, OIML R60 C3, 5–10 t each.
- One junction box and an industrial transmitter wired into the existing SMART controller and modem.

**Where.** Under **every** ground support:
- **DUO:** in a docking frame under the detachable container. The lock to the press must be vertically compliant.
- **COMBI:** under the unit's feet or rollers.

Rocker or pendulum load introduction, lift-off and lateral stops (HBK guidance) `[measured: hbm.com]`.

**What it measures.** The sum of the vertical support reactions = gravity on container + waste (+ snow).

**Procedure.**
1. Read with the ram retracted, the motor stopped, at standstill, and within tilt limits (SMART tilt sensor), using a 5–10 s median.
2. Net = full reading − empty-return reading (auto-tare), which cancels the 2.3–3.0 t tare `[measured: Europress container weights]`.

**Cost.** €3.4–6.3k installed per machine. An approved, certifiable version costs €5.4–10k (`BILL_OF_MATERIALS.md`). Europress says its existing platform scale "costs as much as the compactor" `[measured: briefing]`. Factory fitting should cut the frame and labour share `[assumed]`.

## 2. Mathematical model

m̂ = c Σ k_i (u_i,full − u_i,empty)/g (MATHEMATICAL_MODELS §2).

**Calibration.**
- Corner factors k_i and span c from test weights at commissioning (eccentricity test).
- Auto-zero at each empty return.
- A test-weight check every 1–3 years.

**Error model at 3 t** (JΣJᵀ, confirmed by Monte Carlo) `[simulated]`:

| Grade | σ | P95 | Dominant terms |
|---|---|---|---|
| Cheap | ≈ 30 kg | ≈ 60 kg | snow/ice change on the roof 54 %, temperature drift between readings 29 % |
| Approved | ≈ 23 kg | ≈ 45 kg | snow/ice 92 % |

**Identifiability.**
- All supports must be measured. Two rear cells leave mass dependent on the centre of mass (σ ≈ 13–25 %) `[derived]`.
- Ram pressure cannot separate water or material stiffness from mass. Counterexample: a dry 2,850 kg load and a wet 3,420 kg load give identical pressure and fill `[derived]`.

**Health.** The per-cell share rule flags a dead cell on 100 % of pickups, with 0.8 % false flags `[simulated]`. Small gain drifts are caught by test-weight checks and the long-run ticket ratio.

**Verification statistic.** D_N = median over N pickups of (billed − m̂)/m̂. The flag threshold gives 5 % false alarms on honest bills. A person approves every action.

## 3. Accuracy: what is plausible and what is missing

| Configuration (unseen machines, loads ≥ 1 t) | Median | P95 | Within ±100 kg at 2.5–3.5 t | Mid cost |
|---|---|---|---|---|
| Approved 4-cell | 0.2 % | 1.4 % | 98 % | €7,680 |
| **Cheap 4-cell (recommended)** | **0.5 %** | **2.3 %** | **98 %** | **€4,850** |
| Shear-web strain, all supports | 1.4 % | 4.2 % | 90 % | €3,600 |
| Pressure + oil T + 5 tickets (best low tier) | 9.9 % | 29 % | 19 % | €95 |
| Fill × density + 5 tickets | 10.8 % | 32 % | 16 % | €0 |
| Gradient boosting on pressure/fill | 11.3 % | 34 % | 17 % | €95 |
| Operator weighbridge, weighed tare (reference) | 0.4 % | 1.6 % | 100 % | — |

All values above are `[simulated]` (`results/core_comparison.csv`). Further simulated results:
- **±100 kg target.** Plausible for Tier 2/3: 98 % within ±100 kg at 2.5–3.5 t, meeting the 95 % research criterion `[simulated]`.
- **Robustness.** Load cells are robust to unseen machines, material-mix shift, the wet season and 2 % single-cell drift (P95 stays 2.1–2.6 %) `[simulated: stress_tests.csv]`.
- **Margin.** The 5 % goal tolerates about 3× the assumed temperature drift, 4.5× the snow change and 5× the parasitic load share. The 2 % stretch has no margin at cheap grade `[simulated: sensitivity_lc4.csv]`.
- **Indirect methods degrade.** Unseen machines: P95 32–39 %. Wet season: bias −245 kg `[simulated]`.

**Missing evidence (needs physical validation):**
- real support layout and parasitic paths on DUO docking;
- outdoor snow and temperature behaviour;
- cell durability under hooklift shock;
- installation tolerance;
- the real error of today's SMART pressure-based estimate (Phase 0 desk test).

## 4. Alternatives

1. **Shear-web strain bridges at every support** (€2.4–4.8k). Use it where cells cannot be fitted mechanically. It meets 5 % (P95 4.2 %) but has about 30× less signal and needs in-situ calibration.
2. **Approved Tier 3** (€5.4–10k + €150–400/yr). Choose it where the customer or operator wants the weight to become the invoice basis, after EU type examination or a WELMEC 2.10 modular approval. Partnering with a vendor that already holds approvals (Pfreundt, Tamtron) is the fast route `[measured: vendor claims]`.
3. **€0 Tier 1** (pressure + fill + tickets). It is **not** a ±2–5 % solution. It gives a free per-lift band (±30 % P95), catches gross mismatches and supports hydraulic-health diagnostics. Calibrated on the operator's own tickets, it **cannot detect a constant overbilling** (detection power equals the 5 % false-alarm rate) `[simulated: verification_power.csv]`.

## 5. Economic bonus

**Most valuable additional insight from the recommended hardware without adding sensors:** **weight-based pickup timing and payload.** Prior dataset analysis found 30–32 % of fixed/hybrid lifts unjustified, about €2.5k per device-year `[D, hypothetical tariffs]`.

**Others:**
- incomplete-emptying detection from the empty-return reading;
- per-pickup effective density as a composition **hint** (not proof);
- hydraulic health from the free pressure signal.

See `ECONOMIC_OPPORTUNITIES.md`.

## 6. Dataset claims checked against the raw data (main prompt §2)

| Claim (dataset docs) | Measured on raw data | Held up? |
|---|---|---|
| About 91 % of devices have integrated (simulated) weighing | 90.4 % (404 of 447) | yes |
| Simulated weighing within ~100 kg on 3 t cardboard for ~95 % of normal readings | 77.9 % of clean-ticket 2.5–3.5 t cardboard pickups within ±100 kg (median 55 kg, P95 208 kg) | **no** for all readings (faults and ticket noise included) |
| `press_load_index` is derived from fill | r = 0.984 with fill; adds 0.0001 R² for mass | yes |
| Compacted densities (cardboard 190, mixed 380 kg/m³ …) | medians within 15 % (cardboard 212); between-device CV ≈ 25 %, within-device ≈ 7–11 % | yes (central values) |
| Weighbridge resolution 20 kg, 45 % stored tare | 100 % multiples of 20; 44.4 % stored | yes |
| Stored-tare tickets scatter more | median gap vs device 4.6 % (stored) vs 1.8 % (weighed), loads ≥ 1 t | yes |
| Fill-only can estimate mass | after per-device calibration: median error 5.8–6.2 %, only 41–44 % of loads within ±5 % | partially: it cannot reach the goal |

Source: `results/dataset_checks.json` (`simulation/verify_dataset_claims.py`). All these numbers are measured on **synthetic** data.

## 7. Next experiment

The fastest decisive test is the **Phase 1 rig** (`EXPERIMENT_PLAN.md`):
- 1 DUO container and 1 COMBI unit on four C3 cells at Kerava.
- Test weights (3 t), 20 dock/undock cycles, rigid vs compliant lock, and ≥ 10 real loads per material checked on a weighed-tare weighbridge.
- Pass if ≥ 95 % of 2.5–3.5 t loads are within ±100 kg and |bias| ≤ 0.5 %.
- About 4–6 weeks and €15–30k.

In parallel, a **two-week desk test** on archived SMART pressure curves with shared tickets measures the true error of the free estimate (Phase 0).

## 8. Main risks

| Risk | Mitigation |
|---|---|
| Parasitic vertical path through the DUO docking lock (simulated tolerance is about 5 % share) | Compliant lock, or read with the lock released |
| Snow and ice on the roof | Re-tare at the empty return; winter flag in the uncertainty band |
| Hooklift shock damaging cells | Lift-off stops, overload rating ≥ 150 % |
| Cost vs value: verification alone pays on only about 4–11 % of machines | Audit cohort instead of fleet-wide fitting; factory option; bundle with pickup optimisation |
| Legal | Uncertified weights only for verification and disputes. Ask Tukes about any per-kg pricing on device weight (ISSUES #10) |

Conflicts and assumptions are logged in `ISSUES.md`. The team proposal is in `HARDWARE_PROPOSAL.md`.
