# ECONOMIC OPPORTUNITIES (goal 3, secondary)

**Scope.** This is what else the recommended sensors reveal, prioritised by value per unit of **no extra hardware**. The recommended sensors are:
- Tier 2 load cells on an audit cohort;
- Tier 1 firmware (pressure, fill, oil temperature) everywhere.

**€ evidence.** € figures marked `[D]` are computed on the synthetic Europress dataset with **hypothetical tariffs**. They show structure and order of magnitude, never real savings. Figures marked `[A]` are assumptions.

**Prior figures.** Figures from the earlier business analysis (`../BUSINESS_CASE.md`) are cited as such.

**Basis.** The data window is about 1 year. Per device-year, the median **mass-sensitive spend** (per-tonne fees plus material credits) is **€2,765**; the mean is €6,018 and P90 €15,562 `[D: results/dataset_checks.json C8]`. The median device hauls 51 t/yr in 33–53 lifts, depending on stream `[D]`.

## 1. Billing verification (the purpose set by the user)

**Signals.**
- Tier 2: net mass per pickup (direct). Tier 1: indirect estimate (plausibility only).
- The operator's ticket and invoice, as shared or uploaded by the customer.

**Model.**
- Per machine: D_N = median_N((m_bill − m̂)/m̂).
- Per operator: the same statistic pooled over the audit cohort (MATHEMATICAL_MODELS §7).

**Direct or inferred.** Direct (Tier 2). Tier 1 only flags gross mismatches, above about 30 %.

**Confounders that create false conclusions:**
- Combined loads with equal split.
- Side waste loaded at the lift.
- Snow on the roof (direct method).
- Stored-tare drift, which is real but an operator weighbridge issue, not intent.
- A sensor fault (caught by health_check rules).

The dataset shows **77 % of large gaps come from weighbridge-side causes and 3.9 % from sensor faults** `[D, BUSINESS_CASE.md]`. A gap is therefore a discrepancy to explain, **not evidence of fraud** (spec §9).

**Who benefits.**
- The customer: correct invoices.
- Honest operators: weighbridge hygiene (stale stored tares on about 15 % of vehicles, ±160 kg `[D/assumed]`).
- Europress: a neutral position in the value chain.

**€ value.**
- Each 1 % of systematic tonnage error is worth **€28 per device-year at the median and €60 at the mean** `[D]`.
- Earlier analysis on the same dataset found about €150 per device-year of recoverable billing errors `[D, BUSINESS_CASE.md]`.

**Economics of the hardware** (annualised over 8 years, `[A]`):
- Tier 2 costs **€746/yr** per machine. That pays back from verification alone only if the overbilling is ≥ 3 % on devices with ≥ €25k/yr of mass-sensitive spend: **4 % of devices** `[D]`. At ≥ 5 % overbilling it is **11 %** of devices.
- **Consequence:** do not put Tier 2 everywhere. Weighbridge-side errors are per operator, per bridge or per vehicle, so an **audit cohort** of about 5 Tier 2 machines per operator and region detects a 1 % operator-level bias with about 98 % power in 30 pooled pickups `[simulated: results/audit_cohort_power.txt]`.
- Cost: about €25k per operator-region, spread over every customer served by that operator. The rest of the fleet gets the free Tier 1 estimate.

**How to verify that the benefit is real.**
- Field pilot P7 (EXPERIMENT_PLAN).
- Count invoices disputed and credited, and the € recovered per audited operator per year, against a control region without an audit cohort.

## 2. Weight-based pickup timing and payload (largest €)

**Signals.** Net mass and its trend (Tier 2), plus fill. With no new hardware, the Tier 1 estimate gives a weaker version.

**Model.**
- Pick up when *mass or* volume reaches the limit: m̂ ≥ m_target or f ≥ f_target. Forecast with m̂(t_pickup) = m̂ + ṁ·Δt.
- For per-lift contracts, maximise kg per lift. For dense streams (mixed waste, wet cardboard), stop before the truck, container or road mass limit.

**Direct or inferred.** Mass is direct; the forecast is inferred.

**Confounders.** Seasonal and holiday variation of inflow. Operator lead time.

**Who benefits.**
- Customers on per-lift or fixed schedules: fewer lifts.
- Operators: full loads.
- Europress: SMART uptake.

**€ value.** Earlier dataset analysis found **30–32 % of lifts on fixed and hybrid schedules unjustified, about €2.5–2.7k per device-year** `[D, BUSINESS_CASE.md]`. Weight sharpens "justified" for dense streams where volume underestimates the load. The incremental value over fill-only is **not quantified** here; it needs field data.

**Verify.** A/B schedule change on pilot sites: lifts per tonne before and after.

## 3. Effective density per pickup: compaction efficiency and composition *hints*

**Signals.** ρ̂_eff = m̂/(f̂·V), from Tier 2 mass and the existing fill.

**Model.** A per-machine control chart of ρ̂_eff. A step change suggests one of:
- a material change (for example plastics in a cardboard stream, or wet cardboard);
- a compaction setting change;
- a fill-sensor fault.

**Direct or inferred.** Inferred. **It does not establish contamination**; it only prioritises an inspection or an operator quality check. The earlier density test on synthetic data had about 1 % precision for contamination `[D, BUILD_PLAN.md]`.

**Who benefits.** Customers, through credit grade (A/B/C quality factors 1.00/0.85/0.60 in the dataset tariffs `[D]`), and operators.

**€ value.** Losing one grade (A→B) on cardboard costs about 15 % of the credit, about €9/t `[D: median credit €60.6/t]`. On 85 t/yr that is about €770 per device-year if it happened all year `[derived from D]`. Realised value depends on the true-positive rate, which is **unknown**.

**Verify.** Compare flags with operator quality assessments over 6 months.

## 4. Incomplete emptying and residual-tare detection

**Signals.** The empty-return reading of Tier 2.

**Model.** A residual of Ŵ_empty − Ŵ_tare,ref above k·σ (for example 50 kg) means waste or ice was left in the container, a "partial" lift, or a container swap.

**Direct or inferred.** Direct mass; the cause is inferred.

**Confounders.** Snow on the roof; a different container swapped in (DUO). A container ID via RFID is needed.

**Who benefits.** Customers paying full lift fees for partial emptying (the dataset has `driver_reported_partial`), and operators (dispute evidence).

**€ value.** One lift fee (€100–520 in the dataset tariffs `[D]`) per detected partial lift. The frequency is **unknown** `[A]`.

**Verify.** Photo check on flagged returns.

## 5. Hydraulic and machine health (Tier 1 signals, no new hardware beyond the €20–40 oil probe)

**Signals.** Plateau pressure per stroke, stroke time, oil temperature, cycle counts. Motor power if a meter exists.

**Model.** Per machine, the residual of p_plateau against the expected value given fill and oil temperature, with CUSUM:

| Pattern | Indicates |
|---|---|
| Rising residual with no fill change | wall/floor friction, blockage, a jammed charge |
| Falling efficiency (longer stroke time at the same pressure) | internal leakage or pump wear |
| Cold-oil losses | heater or oil-grade issue |

**Direct or inferred.** Pressure is direct; the diagnosis is inferred.

**Confounders.** Material changes also change pressure. The material-change flag (§3) must be separated from it.

**Who benefits.** Europress service, where "the service contract is the real profit" (earlier work, briefing). Customers get fewer breakdowns.

**€ value.** Europress claims SMART gives 50 % fewer maintenance calls `[VEN, SMART brochure]`. The incremental value of pressure diagnostics is **not quantified**. Assumption for scoping: avoiding one emergency visit of €300–600 per machine every 3 years is worth €100–200 per device-year `[A]`.

**Verify.** Lead time from the first pressure flag to the recorded fault in maintenance work orders.

## 6. Overload and handling risk

**Signals.** Gross mass (Tier 2) and the per-cell centre of mass; the existing tilt sensor.

**Model.** Flag when gross > the container/hooklift rating, or when the centre of mass is outside the safe envelope before lift.

**Direct or inferred.** Direct.

**Who benefits.** The operator (driver safety, legal axle loads) and the customer (liability).

**€ value.** Risk reduction; not quantified.

## 7. Material-flow reporting (mixed-waste growth, recycling rate)

**Signals.** Monthly kg per stream per site. Tier 2 where installed; the Tier 1 band elsewhere.

**Model.** Monthly sums. Recycling rate = recyclable kg / total kg.

**Who benefits.** Retail and property chains with CSRD or ESG reporting. Europress named this explicitly: "your mixed waste amounts have started to grow" (briefing).

**€ value.** A reporting subscription. The price is a business-case assumption (see `../BUSINESS_PLAN.md`).

**Caveat.** Tier 1 bands (±30 % P95 per lift) average down only for the random part. The machine-level bias of about 5–10 % remains in monthly totals `[simulated: the anchors calibrate the mean only]`.

---

## Most valuable additional insight

**From the recommended sensors without new hardware:** weight-based pickup timing and payload (§2). It has the largest € in the data (≈ €2.5k per device-year on fixed and hybrid schedules, `[D]`, prior analysis). Second is the incomplete-emptying check (§4), which comes free with auto-tare.

**From the free Tier 1 signals:** hydraulic health (§5) is the most credible value. It needs no mass identifiability.
