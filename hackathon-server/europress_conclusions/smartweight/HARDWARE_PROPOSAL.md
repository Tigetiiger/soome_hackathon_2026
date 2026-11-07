# HARDWARE PROPOSAL: SmartWeight verification scale

**For:** our team. **Date:** 2026-11-07.

**Purpose.** An independent weight per emptying, used to check that the client is billed accurately on the operator's weighbridge tonnage.

**Details.** Costs: [BILL_OF_MATERIALS.md](BILL_OF_MATERIALS.md). Evidence and verdicts: [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md). Numbers come from the physics simulation (`simulation/`). They are **not field-validated**.

## Recommendation in one paragraph

Fit **four stainless IP68 C3 load cells under every support** of the container (DUO) or unit (COMBI), wired into the existing SMART controller. This is Tier 2, at about **€4.85k** installed.

**How to read the weight**
- Read it **at rest**: ram retracted, standstill, tilt in limits.
- Subtract the reading taken when the container comes back empty (auto-tare).

**What it achieves** `[simulated]`
- P95 of about 2.3 % on loads ≥ 1 t.
- 98 % of 3 t loads within ±100 kg.
- It detects a 2 % systematic overbilling on a single machine 90 % of the time within six pickups.

**Where to fit it.** Install it on an **audit cohort of about 5 machines per operator and region**, not on every machine. Pooled, 30 pickups detect a 1 % operator-level bias with 98 % power. Every other machine gets the free **Tier 1** estimate (ram pressure + fill + oil temperature) as a plausibility check and for hydraulic diagnostics.

**What does not work.** No cheap or indirect sensor reaches ±2–5 %. Mass is not identifiable from pressure, power or fill: water and material stiffness change mass without changing those signals.

## Tiers

| | Tier 1: Low | Tier 2: Mid (recommended) | Tier 3: High |
|---|---|---|---|
| Hardware | existing ram pressure sensor (firmware logging) + €20–40 oil-temperature probe; fill; weighbridge tickets as anchors | 4 × stainless IP68 C3 shear beams (5–10 t), junction box, transmitter → SMART | as Tier 2 with OIML R60 C3 cells, approved mounts, an R76-approved indicator, tilt sensor |
| Mounting | in the tank / firmware | docking frame under the DUO container; under the COMBI feet or rollers; rocker feet, lift-off and lateral stops | as Tier 2 |
| Installed cost per machine | €60–130 | €3.4–6.3k (mid €4.85k) | €5.4–10k (mid €7.68k) + €150–400/yr |
| Accuracy, P95 on loads ≥ 1 t `[simulated]` | ≈ 29 % (median 10 %) | ≈ 2.3 % (median 0.5 %) | ≈ 1.4 % (median 0.2 %) |
| Within ±100 kg at 3 t `[simulated]` | 19 % | 98 % | 98 % |
| Independent of the operator? | **no**: calibrated on the operator's tickets, it cannot see a constant overbilling | yes (test-weight calibration) | yes |
| Grade | estimate | verification grade | verification grade; billing grade possible after class III certification (CE+M, initial verification, re-verified every 3 years) |
| Meets goal 1 (±2–5 %)? | **no** | **yes** for 5 %; 2 % only marginally | yes |

**Rejected:**
- two rear load pins (the centre of mass is unknown, P95 ≈ 25 %);
- bending strain gauges on the runners (≈ 25 %);
- hooklift cylinder pressure, which is also on the operator's own truck (≈ 39 %);
- motor-power metering (≈ 29 %);
- ML on pressure and fill (≈ 34 %, and it fails on unseen materials).

**Backup:** shear-web strain bridges at every support (P95 ≈ 4.2 %, €3.6k) where cells cannot be fitted.

## Where it mounts and how it is used

| Step | What happens |
|---|---|
| **Load path** | All vertical load passes through the four cells. The 343 kN horizontal ram reaction must **not**. For COMBI it stays inside the welded unit. For DUO the press–container lock must be vertically compliant, or released before reading. |
| **Reading** | Full reading before pickup and empty reading after the return. Net = difference. |
| **Health** | Per-cell shares (a dead cell is flagged on 100 % of pickups). Zero after emptying. Cross-check with the Tier 1 estimate. A test-weight check every 1–3 years. |
| **Verification** | Per machine and pooled per operator, compute the median of (billed − measured)/measured. Above the 5 % false-alarm threshold, draft a dispute that **a person approves**. Weighbridge-side causes (stale stored tare, combined loads, side waste) are reported neutrally. Most large gaps in the dataset have such causes. |

## Main risks

| Risk | Mitigation |
|---|---|
| Parasitic load through the DUO docking | Compliant or released lock |
| Snow or ice on the roof (the largest error term) | Re-tare at the empty return; winter band |
| Hooklift shock on the cells | Stops; ≥ 150 % overload rating |
| Cost: per-machine verification pays back on only about 4–11 % of machines `[D, hypothetical tariffs]` | Audit cohort; factory-fit option |
| Legal | Uncertified weights only for verification and disputes. Confirm with Tukes before any per-kg pricing on device weight |

## Next validation step

**Phase 1 rig at Kerava** (4–6 weeks, about €15–30k):
- 1 DUO container and 1 COMBI unit on four C3 cells;
- 3 t of test weights;
- 20 dock/undock cycles, with the lock rigid and compliant;
- ≥ 10 real loads per material checked on a weighed-tare weighbridge;
- a cold-weather repeat.

**Pass criteria:**
- ≥ 95 % of 2.5–3.5 t loads within ±100 kg;
- |bias| ≤ 0.5 %;
- zero drift ≤ 0.5 kg/K;
- every injected dead-cell fault flagged.

**In parallel, Phase 0** (2 weeks, about €0): run the archived SMART pressure curves against shared tickets. This measures the real error of the free Tier 1 estimate. The plan is in [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md).

## Final verdict

**Promising but unvalidated** for the Tier 2/Tier 3 load-cell verification scale:
- It is physically well-founded: direct gravitational weighing of all supports is established metrology.
- In simulation it meets the ±2–5 % goal with margin at 5 %.
- It has **not** been tested on a Europress machine. Docking parasitics, snow and shock durability need the Phase 1 rig.

**Rejected** as a ±2–5 % solution: every cheap or indirect option (Tier 1 pressure/fill/power, partial supports, bending strain, hooklift pressure). Their failure is one of identifiability, not of sensor quality.
