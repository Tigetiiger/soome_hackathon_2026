# Assumptions and what remains untested

_Required by the Challenge Brief §07 ("Include assumptions and what remains untested") and the 5 % criterion "clarity, uncertainty and practical limitations". This file gathers the key points in one place. Each section links to the detailed source._

## What is real, what is not

- **No physical prototype was built.** The brief does not require one.
- **All data is synthetic.** We used the Since AI pack (~500 fictional compactors × 365 days) and our own `compactor_sim` hourly simulator. Nothing is real Europress data, and no real pressure settings were used.
- The Since AI pack supports Part 2 only. **It validates no weighing hardware** (brief §05).
- **Prices and tariffs are hypothetical.** BOM prices are vendor list prices at the time of research. Labour and type-examination costs are assumed ranges.
- Evidence tags in the Part 1 documents: `[measured: source]`, `[derived]`, `[simulated]` (physics simulation, not field performance), `[assumed: why]`.

## Key assumptions

### Part 1: weighing
1. The weight is used to **verify** the operator's weighbridge tonnage, not as the legal billing basis (smartweight ISSUES #1).
2. Machine geometry, support layout, tare masses and ram geometry are **assumed**; no Europress drawings were available (ISSUES #8).
3. The load range comes from the dataset: cardboard and mixed loads have p90 ≈ 5.7 t, not the "≤ 3 t" in the spec (ISSUES #13).
4. Waste moisture fractions are assumed: 5–25 % for wet cardboard (ISSUES #14). Snow on the roof averages 40 kg in winter (ISSUES #16).
5. The density laws (pressure → density) per material are modelling hypotheses `[hyp]` (virtual_scale §4).
6. Legal reading: billing by weight in Finland needs a class III NAWI. Consent does not exempt it (Act 707/2011). This is **our interpretation; confirm with Tukes** (ISSUES #10, #17).

### Part 2: value
7. € savings use hypothetical tariffs from the synthetic contracts.
8. The demo uses the device weight model in a "future scenario". The real production algorithm is the weight-track work (`02_dashboard.md` §7).
9. Production weather comes from FMI (CC BY 4.0). The mockups use ERA5 via Open-Meteo, which is non-commercial.
10. Europress does not sell data and the customer owns it. Every price is a tool or service subscription (`05` decisions).
11. Integration goes through the ~20 operators, not through invoice upload by end customers (second Europress briefing).

## Simulated results that need real-world confirmation

| Claim | Status |
|---|---|
| 4 load cells under every support reach P95 2.3 % (cheap grade) / 1.4 % (approved) | `[simulated]` |
| Indirect sensing (ram pressure, motor power, fill × density, ML) gives P95 25–49 %, so mass is not identifiable from these signals alone | `[simulated]` + `[derived]` proof |
| About 5 audit machines detect a 1 % operator bias in 30 pooled pickups (power 98 %) | `[simulated]` |
| Verification alone pays back Tier 2 on only about 4–11 % of machines | `[derived]`, hypothetical tariffs |
| Weight-based pickup timing is worth about €2.5k per device-year | `[derived]` from the synthetic data |

## What remains untested (needs real machines)

1. Whether real hydraulic stroke curves carry mass information beyond fill. Phase 0 go/no-go: at least 30 % error reduction (virtual_scale §9).
2. Real density laws per material, season, and wet or frozen state. **Frozen wet cardboard and frozen biowaste are unsolved** (virtual_scale §1.1–1.2).
3. Parasitic load through the DUO docking lock, and the different load paths of COMBI and DUO; each class must pass separately.
4. Load-cell behaviour under hooklift shock, corrosion, ground settling and multi-year drift. Pressure-sensor drift and hydraulic wear.
5. Installation effort on customer sites, whether controllers have analog inputs, and the data link.
6. Whether operators accept device weights as evidence, since they are not legal-for-trade.
7. Real customer willingness to pay, and operator willingness to share weighbridge tickets.
8. Calibration independence: calibrating an indirect estimator on the operator's own tickets absorbs a constant overbilling. This is why a load-cell reference cohort is needed (ISSUES #15).

Validation plan: `europress_conclusions/smartweight/EXPERIMENT_PLAN.md`
- Phase 0: desk test on existing data, about €0
- Phase 1: bench and rig test of Tier 2
- Phase 2: 8–12 week field pilot with pre-registered pass/fail criteria

## Practical limits of the demo

- No authentication. Production needs per-customer login (SMART portal SSO).
- The demo runs on a Tailscale tailnet. The public domain with HTTPS is prepared but not live.
- The AI advisor answers only from the synthetic data in a read-only sandbox. Its answers are advisory and need human approval before any action (brief §04).

Detailed sources:
- `europress_conclusions/smartweight/ISSUES.md` (20 items)
- `virtual_scale/ASSUMPTIONS_AND_EXCEPTIONS.md`
- `europress_conclusions/smartweight/HARDWARE_PROPOSAL.md` "Main risks"
- `output/02_dashboard.md` §7
- the data pack's `docs/ASSUMPTIONS_AND_LIMITATIONS.md`
