# BILL OF MATERIALS: three hardware tiers per machine

**Price basis.** Prices are in EUR excluding VAT, per machine. USD is converted at 0.93 EUR/USD `[assumed]`.
- **L**: listed price found online on 2026-11-07. Product URLs are in `_research/hardware_prices.md`.
- **E**: estimate or derived figure.
- **A**: assumption; no public figure exists.

**Model basis.** Specifications are the vendors' own, not tested. Accuracy figures come from `results/core_comparison.csv` and are `[simulated]`. They are not field-validated.

**Purpose (user, 2026-11-07).** The system verifies the operator's billed weight. Only Tier 3 can additionally be made billing grade.

## Summary

| Tier | What | Installed cost (low–high, mid) | Simulated P95 error, loads ≥ 1 t | Grade |
|---|---|---|---|---|
| **1. Low: €0–130** | Firmware logging of the existing SMART ram pressure + fill, oil-temperature probe, ticket anchors | €60–130 (mid €95) | ≈ 29 % (median ≈ 10 %) | Estimate grade. **Fails** the ±2–5 % goal. Not independent of the operator. |
| **2. Mid: €3.4–6.3k** | 4 stainless IP68 C3 shear beams under **every** support + industrial transmitter into SMART | €3,400–6,300 (mid €4,850) | ≈ 2.3 % (median ≈ 0.5 %) | Verification grade, independent. Not legal-for-trade. |
| **3. High: €5.4–10k** | Tier 2 hardware with an OIML R60 C3 set and an R76-approved indicator, type approval or modular approval, initial verification | €5,360–10,000 (mid €7,680) + €150–400/yr re-verification | ≈ 1.4 % (median ≈ 0.2 %) | Verification grade; billing grade possible after certification. |

Cheaper partial options (2 rear load pins, 2 bending strain gauges) cost €1.5–3.7k. They **fail** the target because the centre of mass is unknown (P95 ≈ 25 %). They are listed at the end as rejected.

---

## Tier 1: low cost (firmware + €20–40 probe)

| Item | Spec | Qty | Unit price | Tag |
|---|---|---|---|---|
| Existing SMART ram pressure transducer | already installed; confirm range and accuracy with Europress | 1 | €0 | EP (briefing: pressure curves are recorded) |
| Firmware: log mid-stroke plateau pressure, stroke count and ram position per cycle at 10–20 Hz | OTA update | 1 | €0–30 | A |
| Oil-temperature probe, PT1000 or digital, IP67, in the tank return | −40…+100 °C | 1 | €20–40 | L (€19.60 RS485 probe, IP not stated) / E |
| Fitting and wiring by a service technician during a planned visit | — | 1 | €40–90 | A |
| Ticket anchors: operator weighbridge tickets with weighed tare, single load | data agreement | 5+ | €0 | — |
| **Total** | | | **€60–130** | |

**What it gives.** It gives a kg estimate per pickup with a band of about ±20–30 % (P95), and a monthly total. It also gives the hydraulic diagnostics described in `ECONOMIC_OPPORTUNITIES.md`.

**What it cannot do.** It cannot meet ±2–5 %. Because it is calibrated on the same operator's tickets, it cannot detect a constant overbilling by that operator (see ISSUES #15).

## Tier 2: mid cost, recommended for verification

Mounting is in the **docking frame / foot positions**. The cells sit under every point where the container (DUO) or the complete unit (COMBI) rests on the ground.

| Item | Spec | Qty | Unit price | Line | Tag |
|---|---|---|---|---|---|
| Stainless double-ended or single-ended shear beam, IP68 welded, C3 | 5–10 t per cell (COMBI gross up to ≈ 15 t; DUO gross ≈ 6–10 t). E.g. ANYLOAD 102ES 25 klb (TC zero <0.004 % Cn/K, creep <0.03 %/30 min, service −30…+70 °C) or Rice Lake RL32018S | 4 | €410–810 | €1,640–3,240 | L (USD 440–870) |
| Load introduction: rocker or pendulum foot, anti-lift-off stop, lateral stop | HBK guidance: no side loads; ram reaction must not pass through the cells | 4 | €100–300 | €400–1,200 | E (mount ≈ cell price at catalogue level; fabricated in-house) |
| Stainless 4-cell junction box with trim | IP67/68 | 1 | €140–150 | €140–150 | L (USD 153–162) |
| Industrial weighing transmitter, 4–20 mA / Modbus, into the SMART controller | e.g. Laumas TLE | 1 | ≈ €195 | €195 | L (≈ USD 210) |
| Cable glands, protective conduit, surge protection | — | 1 set | €50–100 | €50–100 | E |
| Integration I/O to the SMART modem (existing 4G/5G) | — | 1 | €0–100 | €0–100 | E |
| Docking-frame steel (reinforced seats for the cells) | design per machine class | 1 | €400–1,200 | €400–1,200 | A |
| Installation: 2 technicians, ½–1 day | lift the unit or container onto the frame | 1 | €600–1,200 | €600–1,200 | A |
| Commissioning calibration with test weights (≈ 1–2 t at each corner and centre) | corner adjustment + span | 1 | €300–700 | €300–700 | A |
| **Total** | | | | **€3,400–6,300** | |
| Annual: test-weight check every 1–3 years, cell inspection | | | | €80–200/yr | A |

**Measurement procedure.**
- **Static reading.** Read with the ram retracted, the motor stopped and the container closed. Use a 5–10 s median, with a standstill test and a tilt check from SMART's existing tilt sensor.
- **Auto-tare.** Tare on the empty return after each pickup, so net = full − empty. Because both readings come from the same scale, the 2.3–3.0 t tare cancels.
- **Health monitoring.** Track per-cell shares, which give the centre of mass. Check the zero after each emptying. Cross-check against the Tier 1 estimate, which costs nothing because it runs on the same machine.

**Design notes.**
- **COMBI units.** The press reaction stays inside the welded unit, so it is not a problem.
- **DUO units.** The container is locked to the stationary press, which creates a parasitic load path. The lock must be vertically compliant, or released before reading, or the frame must carry the press unit as well.
- **Factory fit.** Fitting at the factory (Kerava) instead of retrofit removes most of the installation and frame cost (E).

## Tier 3: high accuracy, certifiable

Tier 3 uses the Tier 2 layout with metrologically approved components.

| Item | Spec | Qty | Unit price | Line | Tag |
|---|---|---|---|---|---|
| OIML R60 C3-certified stainless shear beams (check the certificate number on oiml.org) | as Tier 2 | 4 | €410–810 | €1,640–3,240 | L |
| Approved weigh-module mounts | stainless, self-aligning | 4 | €250–650 | €1,000–2,600 | L (Rice Lake mount USD 695) / E |
| Junction box | approved / sealed | 1 | €140–150 | €140–150 | L |
| R76 / EN 45501 approved weighing indicator with alibi memory and sealed parameters | e.g. Rice Lake 482 Plus (US price) or an EU type-approved equivalent (Dini Argeo, Laumas, quote-only) | 1 | €715–780 | €715–780 | L (USD 770–839) |
| Tilt sensor or switch (WELMEC 2 vehicle/waste guidance) | IP67 | 1 | €80–330 | €80–330 | L (€333 Elkome; USD 85 WitMotion) |
| Reinforced frame | as Tier 2 | 1 | €800–2,000 | €800–2,000 | A |
| Installation | | 1 | €800–1,500 | €800–1,500 | A |
| Test weights + initial verification by a notified/inspection body | Kiwa (FI) | 1 | €500–1,100 | €500–1,100 | A (Kiwa periodic list €89 + VAT, scope unclear) |
| Type examination (Module B) or WELMEC 2.10 modular approval, amortised | notified body quote needed | — | — | €60–200 | A (cost not public; €30–100k over 500 units) |
| **Total** | | | | **€5,360–10,000** (mid ≈ €7,680) | |
| Annual: 3-yearly re-verification, test-weight logistics, seals | | | | €150–400/yr | A |

**Cross-checks.**
- **WeDi K3 container scale.** 15 t, 4 cells plus indicator, complete, listed at **€4,800–5,620** ex VAT (2024 listing); trade approval is not stated (L).
- **Europress.** Europress says its platform scale "costs as much as the compactor itself" (briefing).

## Rejected partial options (for reference)

| Option | Cost | Why rejected |
|---|---|---|
| 2 load pins in the rear roller axles (ANYLOAD 535TS 10 t, USD 868 each, L) + transmitter | €2,400–4,300 | The front reaction is unmeasured. Mass depends on the centre of mass, giving σ ≈ 13–25 %, simulated P95 ≈ 25 %. |
| 2 weldable bending gauges on the runners (Micro-Measurements LWK-06, ≈ €250 each, L) + amplifier | €1,350–2,600 | They measure a load-distribution-dependent share, with thermal stress and zero walk. Simulated P95 ≈ 25 %. |
| 4 shear-web strain bridges at every support | €2,400–4,800 | It works in principle (simulated P95 ≈ 4 %), but it costs about the same as Tier 2, has about 30 times less signal and needs in-situ calibration. Keep it only if cells cannot be fitted mechanically. |
| Hooklift cylinder pressure + inclinometer on the hauler's truck | €1,250–2,400 per truck (≈ €40–80 per container served) | The centre of mass is not identifiable from one force (P95 ≈ 39 %). The hardware also belongs to the operator being verified. |
| Motor power meter (Eastron SDM630 MID, €91, L) | €190–390 | It is never better than pressure: it adds motor and pump efficiency error. |
