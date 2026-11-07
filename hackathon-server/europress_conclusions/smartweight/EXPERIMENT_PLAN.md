# EXPERIMENT PLAN: physical validation

**Goal of the experiment.** Test whether the recommended configuration measures the waste mass per emptying to within the ±2–5 % target, independently of the operator, in Finnish outdoor conditions. The recommended configuration is Tier 2: four load cells under every support, static reading, auto-tare at the empty return.

A second goal is to measure what the €0 Tier 1 (pressure + fill + anchors) actually achieves on real machines. That number replaces the simulated estimate.

**Safety.**
- All mechanical, hydraulic and electrical work is done by Europress-authorised technicians, under Europress's authority as the machine manufacturer.
- Nobody opens pressurised hydraulic lines. Tier 1 reuses the existing SMART pressure transducer port, so it is non-invasive. Fitting an oil-temperature probe means work on the tank, done with the machine depressurised and locked out.
- Nobody works on live 400 V circuits. The motor-power meter, if used, is installed by a qualified electrician.
- No one is near the ram or the hooklift during cycles.

## Phase 0: desk test on existing data (2 weeks, about €0)

1. Pull the archived SMART ram pressure curves for at least 30 machines that have at least 10 shared weighbridge tickets each. This covers cardboard, plastic and mixed waste, COMBI and DUO, and at least one winter month.
2. Fit three models with leave-machine-out validation:
   - fill-only, Model D;
   - fill + plateau pressure + oil temperature (or ambient temperature as proxy), Model C;
   - gradient boosting on the same inputs.
3. **Go/no-go for Tier 1 as a product.** Pressure must reduce the median absolute error by at least 30 % compared with fill-only. The ticket-anchored error must reach a P95 of at most 10 %. The simulation predicts that this **fails**: the simulated median is about 9 % and the P95 about 29 %. The test is cheap, and it tells Europress how far it can trust the existing "waste volume calculator".

## Phase 1: bench and rig test of Tier 2 (4–6 weeks)

**Setup**
- **Machines:** 2 DUO containers (20 and 30 m³) and 1 COMBI 20 m³ unit at the Kerava factory yard, outdoors on concrete.
- **Sensors:** 4 stainless C3 shear beams (5–10 t) under the four support points in a docking frame, with rocker feet and lift-off stops; trimmed junction box; industrial transmitter logging at ≥ 10 Hz.
- **Logged alongside:** each cell's raw signal, the SMART tilt sensor, the ambient and frame temperatures (2 × PT1000 on the frame), and a roof-load camera snapshot for snow.
- **Docking interface (DUO):** fitted with a vertically compliant lock. Repeat the tests with the lock rigid, to measure the parasitic load path.
- **Reference:** certified test weights totalling 3 t (class M1, in 500 kg blocks), plus a class III weighbridge with e ≤ 10 kg and weighed tare. The weighbridge is used before and after on the hooklift truck: the same truck, the same driver, the fuel level noted, and a double weighing.
- **Data acquisition:** an industrial logger or the SMART controller. Timestamps are synchronised over NTP with the truck/weighbridge logs, to ±1 s.

**Measurement sequences**

| # | Sequence | Repeats | Measures |
|---|---|---|---|
| S1 | Zero stability: empty container for 72 h, logged every 10 min | 1 per machine | zero drift vs temperature (kg/K), creep |
| S2 | Test weights 0 → 500 → … → 3,000 kg → 0, centre | 3 | linearity, hysteresis, span |
| S3 | Eccentricity: 1,000 kg block over each support and at front/rear quarter points | 3 | corner errors (sets corner trims) |
| S4 | Repeated dock/undock cycles with 2,000 kg inside | 20 | repeatability after hooklift handling, parasitic paths |
| S5 | Ram cycles with load (DUO lock compliant vs rigid) | 20 + 20 | effect of the ram reaction; confirm that reading only at rest is required |
| S6 | Real material: fill with weighed bales or charges of cardboard, plastic and mixed waste, then read at 25 %, 50 %, 75 % and 100 % fill, then take to the weighbridge | ≥ 10 loads per material | net-mass error against the weighbridge, by material and centre of mass |
| S7 | Wetting: spray a measured volume of water onto a cardboard load | 5 | confirms that the direct method sees water (and the indirect one does not) |
| S8 | Temperature: repeat S2 at the coldest and warmest available days (target ΔT ≥ 25 K) | 2 | span tempco, cold behaviour |
| S9 | Fault injection: disconnect one cell; add a 2 % shunt resistor on one cell | 3 each | does the health monitor flag it? |

**Calibration and hold-out**
- Corner trims and span come from S2–S3 on machine A only.
- Machines B and C are evaluated with A's procedure applied fresh: same procedure, their own trims.
- S6 loads are never used for calibration.

## Phase 2: field pilot (8–12 weeks)

- **Machines:** 10 Tier 2 machines at 2 customer sites (one retail chain with cardboard, one logistics site with mixed waste and plastics), all with an operator who shares tickets.
- **Comparison:** 30 more Tier 1 machines on the same operators. This measures the real indirect error, using the Tier 2 machines as ground truth for Tier 1 on the same site.
- **Reference:** the operator's weighbridge tickets, single load only. Prefer weighed tare. Record the tare method.
- **Ticket audit:** a sample of 20 tickets is double-weighed on a second certified bridge, to measure ticket noise itself.
- **Verification test:** for each machine, compute the rolling statistic D_N = median over N = 6 pickups of (ticket − device)/device. Count false alarms during honest operation.

## Statistical pass/fail criteria (pre-registered)

| ID | Criterion (net mass, loads ≥ 1 t) | Pass if | Sample |
|---|---|---|---|
| P1 | Share of S6 loads within ±100 kg at 2.5–3.5 t | ≥ 95 %; lower 90 % CI bound ≥ 90 % | ≥ 30 loads |
| P2 | P95 of |error|/m (rig S6 + field), against a weighed-tare ticket | ≤ 5 % (goal); ≤ 2 % (stretch) | ≥ 150 lifts |
| P3 | Mean bias over all lifts | |bias| ≤ 0.5 %; 95 % CI excludes ±1 % | ≥ 150 lifts |
| P4 | Zero drift (S1) | ≤ 0.5 kg/K and ≤ 10 kg over 72 h | 3 machines |
| P5 | Repeatability after dock/undock (S4) | sd ≤ 10 kg | 20 cycles |
| P6 | Fault detection (S9) | 100 % of dead-cell faults and ≥ 80 % of 2 % drifts flagged within 3 pickups | 6 injections |
| P7 | Verification false alarms with honest tickets (N = 6) | ≤ 5 % of machine-windows | field pilot |
| P8 | Tier 1 (indirect) | Report P95; Tier 1 is acceptable as a product only if P95 ≤ 10 % | 30 machines |

**Statistics.**
- Binomial confidence intervals are Clopper–Pearson.
- Paired bootstrap is used for model comparisons.
- With 150 lifts, the 95 % CI on a proportion near 0.95 is about ±3.5 points.

**Failure triggers.** The approach is falsified for verification if any of these occur:
- **Parasitic paths.** The S5 rigid-lock bias is above 1 %, and no compliant lock removes it.
- **Snow and ice.** The P2 failure is driven by an unremovable snow/ice term. Fix: mandatory roof clearing or roof-load compensation.
- **Uncorrectable cold drift.** Cold-weather drift exceeds 2 % after auto-tare.

## Indicative bill of materials for the experiment

| Item | Qty | Cost | Tag |
|---|---|---|---|
| Tier 2 sensor sets (cells, mounts, junction box, transmitter) | 3 | €2,300–4,800 each | L/E (see BILL_OF_MATERIALS) |
| Docking frames (fabricated at Kerava) | 3 | €400–1,200 each | A |
| Test weights 3 t, M1 class (rental) | 1 | €500–1,500 | A |
| Data loggers / PT1000 / camera | 3 | €300–600 each | E |
| Weighbridge fees and truck time (about 60 trips) | — | €3,000–6,000 | A |
| Field pilot: 10 Tier 2 sets (including installation) | 10 | €3,400–6,300 each | E/A |
| **Total** | | **≈ €50–100k** | |

## How the results transfer (and where they might not)

**What transfers directly**
- The rig uses full-size containers, real hooklift handling and outdoor conditions, so most results transfer directly.

**What does not**
- **Fleet variation.** Ground flatness, corrosion and wear over years, and installation quality on customer sites are not represented. Phase 2 and a 12-month follow-up close this gap.
- **Indirect methods.** Bench charges fed by hand do not reproduce real infeed: mixing, moisture history, or compaction across days. That is why Tier 1 is judged only on field data (Phase 0/2), never on the rig.
- **COMBI vs DUO.** Their load paths differ: COMBI has an internal ram reaction, DUO an external lock. Each class must pass P1–P6 separately.
