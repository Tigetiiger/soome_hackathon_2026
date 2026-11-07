# Business plan: "Verified Weight" in SMART (CFO / sceptical-board lens)

Tags: **[S]** = sourced (URL), **[D]** = computed from the synthetic dataset, **[E]** = estimate, **[A]** = assumption. All dataset prices are hypothetical (Since AI). These are not Europress prices or real savings. Model script: `/home/hackathon/europress_conclusions/agents/bizplan-cfo_model.py`.

## 0. Board summary

- **The ask is a ~€150k pilot, not a €1.35M programme.** Weight is a software feature on the existing pressure transducer. A load-cell tier exists for the few customers who need audit-grade weight.
- **Subscription revenue alone does not pay back in 6 years in our base case** (NPV −€0.33M at 10%). The case turns positive (**NPV +€0.23M base, −€0.83M low, +€2.37M high**) only when we count the lever Europress already lives on: **renewal of service contracts and leases**.
- So the KPI the board should fund against is **renewal and attach rate, not ARR**. The plan has kill gates that cap the downside at the pilot spend.

## 1. Context: Europress as a business

- **Revenue.** Tommi: group ≈ €70M, aim to double [S: kick-off]. Europress Group Oy (Finnish entity): **€35.6M sales 2024 (€39.2M 2023), net profit ≈ €0.57M (≈1.6%)** [S: search snippet of https://scoris.eu/company/FI/0889611-2, page 403, not opened]; Vainu ≈ €40M, year unstated [S: https://search.vainu.com/company/europress-group-oy-taloustiedot-ja-liikevaihto/FI08896112/yritystiedot]. €70M is likely consolidated [A]; **ask Tommi**. Thin margins → fund only with stage gates.
- **Poland:** Europress Poland Sp. z o.o., Poznań, inc. 2019, +11.6% net sales 2024 [S: https://www.emis.cn/php/company-profile/PL/Europress_Poland_Sp_z_oo_en_8355341.html]. **Ownership:** not verified; none invented.
- **Position:** "leading … manufacturer of waste compactors and balers in Northern Europe" [S: https://www.eastcham.fi/finnishwastemanagement/europress/]. ~6-yr leases + service contract ("the real profit"); SMART on ~15% of customers [S: kick-off].

### Competitors

| Competitor | Remote monitoring | Integrated weighing |
|---|---|---|
| Orwak | Orwak Connect: modem, alerts, bale statistics portal [S: https://global-recycling.info/?p=5200] | None found |
| Marathon (ESG) | Pandora remote monitoring [S: https://directindustry.com/prod/environmental-service-group/product-173775-2087137.html] | None found |
| Presona | – | "On request" via a reseller [S: https://www.exapro.com/presona-lp40-eh1-p260209144/] |
| Bramidan | – | No official option found [S: search, 2026-11-06] |
| Europress | SMART | Scaletipper X1 and a "Scale platform" [S: europressgroup.com/scale-solutions, per weighing-engineer.md] |

Third-party container load cells exist, for example from Interface [S: https://www.interfaceforce.com/solutions/test-and-measurement/waste-management-container-weighing/]. A retrofit patent also exists (US11162834B2, title only, not read) [S: https://patents.google.com/patent/US11162834].

**Conclusion [E]:** monitoring is table stakes. *Ballpark weight on every machine at zero BOM, with a neutral invoice second opinion,* is not visibly offered by Nordic peers.

## 2. Problem and customer

- **The problem.** The waste operator alone holds the weighbridge weight and the quality grade. Customers distrust invoices and cannot compute €/t [S: kick-off].
- **Who buys.**
  - **Chains** with 2–3 compactors per site and many sites (S-Group, Tamro…) want transparency and ESG figures.
  - **Small customers** want to save money (80/20) [S: kick-off].
- **Who signs.** The facility or sustainability manager, with the CFO's procurement team approving.
- **Europress's own problem.** About 85% of customers have no SMART, and every lease end is a moment when Orwak, Bramidan or Presona can win the replacement [A].

## 3. Value proposition (quantified, hypothetical prices)

- **Identified value.** On the dataset, the best action set is worth **≈ €1,064 per contract-year against €13.5k annual contract cost (7.9%)** [D, team figure, hypothetical prices]. Each contract has exactly one device (447 devices, 447 contracts) [D]. So this is **€1,064 per device-year**.
- **Where the value comes from.** About 99% is renegotiation and tender gaps that weight makes visible as €/t. Weight-basis disputes are small, €729 in the dev set [D, red-team §0]. We sell **€/t transparency plus neutral verification**, not "catching operators".
- **Realisable value.** We assume 50% is realisable [A], which gives **€532 per device-year**. At €15/month (€180 per year) the customer gets **2.96× the fee**, which clears the dataset's purchase condition of 2× [D/A].
- **Accuracy is fit for purpose.**
  - The virtual scale with anchors gives about ±6.6% (1σ). That is enough for monthly €/t reporting (median error 6.7% at σ = 10%) [D].
  - It is **not** enough for per-lift invoice proof. At σ = 10% only 16% of +10% overbilling is caught [D].
  - Per-lift proof is what the load-cell tier is for (±1.4%) [E, weighing-engineer.md].

## 4. Product and tiers, mapped to SMART

| SMART tier | Weight feature | Accuracy (1σ) | BOM | Price to customer [A] |
|---|---|---|---|---|
| **Intro** | "Ballpark kg" per container, computed from fill and pressure. Free, as a retention hook | ±10–14% | €0. Firmware for 10–20 Hz pressure logging (OTA) | Included |
| **Insights + Verified Weight** | Calibrated from tickets (anchors), €/t per stream, monthly invoice second opinion, drift alerts, human-approved draft actions | ±6.6% per lift, about 4% monthly | €0. €60 onboarding per device (desk calibration) | **+€15 per device-month** |
| **Integrated + Audit-grade** | 4-corner load-cell platform, signed lift records, ERP/API export | ±1.4% | €1.0–1.4k at volume plus €600–900 installation [E]. €1.9k capex in the model | **€49 per device-month**, inside the 72-month lease |

- **Enabler: the golden cohort.** 6–10 platforms cost **€10–19k** [E] and generate ground truth for the fleet model.

## 5. Unit economics per device [A]

- **Cost to serve €3.5/device-month** (cloud+ML €1.5, support €2.0).
- **Insights add-on:** €15 − €3.5 = **€11.5/month (77% margin)**; onboarding payback €60/11.5 = **5 months**; 72-month contribution €828 before churn.
- **Audit-grade:** €45.5/month vs €1.96k capex+onboarding → **43-month payback**. Works inside a 72-month lease, thin otherwise: **never sell as stand-alone retrofit.**
- **Retention credit €60/adopter-year [A]:** one won renewal ≈ machine margin €5k [A] + 6 yrs service gross margin €600/yr [A], discounted ≈ €7.6k; +5 pp renewal probability [A] → €380 per renewal event; 1/6 of fleet hits lease end yearly → ≈ €63/adopter-year.

## 6. Revenue model and pricing sensitivity

Per-device subscription + hardware tier recovered through the lease + a retention credit (avoided lost renewals, shown separately, never booked as revenue). Excluded: data resale, tonne-based full service, marketplace (future hypotheses; Tommi's red lines on trucks/waste trading).

**Six-year NPV against price** (base adoption, 10% discount rate):

| Price per month | €10 | €15 (base) | €20 |
|---|---|---|---|
| NPV, k€ | −287 | **+230** | +746 |

Customer value multiple at €20 is 2.2×. That is still above the 2× purchase condition, so **€15–20 is the defensible band [E]**.

## 7. Three-year P&L (k€; Y1 = 2027) [model output, all A/E]

Assumptions: eligible base 12,000 connected Nordic devices, +4%/yr [A, validate with Tommi], Poland +1,500 from Y3. Adoption Y1/Y2/Y3 low 2/5/9%, base 3/10/18%, high 5/15/28%; premium share 8% of adopters; churn 12/8/5%; price low €12, base €15, high €19; fixed (2–3 FTE firmware/ML/UI + validation) €380k/€200k/€230k.

| | Low Y1 | Low Y2 | Low Y3 | Base Y1 | Base Y2 | Base Y3 | High Y1 | High Y2 | High Y3 |
|---|---|---|---|---|---|---|---|---|---|
| Active devices (year end) | 240 | 625 | 1,170 | 360 | 1,250 | 2,610 | 600 | 1,875 | 4,060 |
| Subscription revenue | 22 | 75 | 154 | 38 | 168 | 400 | 77 | 314 | 750 |
| − Cost to serve | −6 | −23 | −46 | −8 | −33 | −79 | −11 | −44 | −105 |
| − Onboarding | −14 | −25 | −37 | −22 | −55 | −88 | −36 | −78 | −137 |
| − Fixed development and operations | −380 | −200 | −230 | −380 | −200 | −230 | −380 | −200 | −230 |
| + Retention credit | 2 | 11 | 21 | 12 | 47 | 113 | 33 | 134 | 321 |
| **EBITDA impact** | **−376** | **−162** | **−138** | **−360** | **−73** | **+116** | **−317** | **+126** | **+599** |
| Hardware capex (premium tier) | −36 | −63 | −94 | −55 | −140 | −222 | −91 | −198 | −346 |

**Six-year results** (lease horizon, 10% discount rate [A: PE-style hurdle for a thin-margin manufacturer]):

| | Low | Base | High |
|---|---|---|---|
| NPV | −€826k | **+€230k** | +€2,368k |
| Payback | none | year 5 | year 4 |
| Cumulative cash flow | | +€0.69M | |

**Board-level framing.** Base Y3 subscription revenue of €0.4M is **0.6% of €70M**. This is a retention and attach engine, not a doubling engine on its own.

## 8. Sensitivity tornado (six-year NPV, k€; base = +230)

| Driver (low / high value) | NPV low | NPV high | Swing |
|---|---|---|---|
| Adoption (×0.5 / ×1.5) | −395 | +855 | 1,250 |
| Renewal uplift (€0 / €120 per adopter-year) | −332 | +791 | 1,123 |
| Price (€10 / €20) | −287 | +746 | 1,033 |
| Fixed development (×1.5 / ×0.75) | −280 | +485 | 765 |
| Cost to serve (€6 / €2 per device-month) | −51 | +398 | 449 |
| Churn (15% / 4%) | +50 | +332 | 282 |
| Discount rate (14% / 7%) | +116 | +337 | 221 |
| Poland (none / 2,500 devices) | +116 | +305 | 189 |

- **Break-even adoption** is about 0.8× base, roughly 14% of eligible devices by Y3.
- **What dominates.** Adoption and the renewal effect are the two largest bars. Both are measurable in the pilot, so that is what the gates test.

## 9. Go-to-market and stage gates

| Gate | Scope and spend | Kill / continue criteria |
|---|---|---|
| **0. Desk falsification** (Q1 2027, ≈ €25k) | Pressure archives + shared tickets, ≥30 machines | **Kill** if pressure features cut MAE < 30% vs fill-only (weighing-engineer A6) |
| **1. Finland pilot** (Q2–Q3 2027, ≈ €150k cumulative) | 3 retail chains, 40–60 devices, 6 golden-cohort platforms (€11k); free 6 months, then paid offer | **Kill** if < 80% of lifts within ±10% (A1), or paid conversion < 30%, or verified value < 2× fee, or operator push-back blocks tickets at > 1 of 3 customers |
| **2. Finland rollout** (2028) | Pitch to all SMART customers at renewal/upgrade; Intro "ballpark kg" in every new lease | **Continue** if Y2 adoption ≥ 7%, churn ≤ 10%, adopter renewal ≥ +3 pp vs matched non-adopters |
| **3. Poland** (2029) | Fixed-schedule fleets (weight also proves unnecessary lifts); ticket formats and EPR untested | **Go** only if Gate 2 met and a Polish anchor partner (operator or chain) signed |

**Channel.** The existing Europress sales and service organisation and SMART Center. The pitch is positioned **neutrally toward operators**: "a second opinion, disclosed to the operator first".

## 10. Risks

| Risk | Mitigation |
|---|---|
| The virtual scale misses ±10% in the field | Gate 0 and Gate 1. Fall back to the audit-grade tier for chains only |
| Operators refuse to share tickets, which cuts calibration anchors | Manual or service-visit weighs at €100–250 [A]. The golden cohort gives a fleet prior |
| Customers will not pay ("cheapest wins") | Intro stays free, so retention value accrues even at zero ARPU |
| Customers or operators treat the weight as billing-grade | It is verification only, not legal-for-trade (NAWI 2014/31/EU). Contract wording must say so |
| The renewal effect is unproven | It is measured in Gate 2 against a matched cohort. NPV without it is −€0.33M, and this is disclosed |
| Fleet size and margins are guessed | Replace with Europress actuals. The model is parameterised |

## 11. KPIs

SMART attach rate (baseline 15%); Verified Weight adoption and pilot paid conversion; adopter vs non-adopter renewal rate; lease win rate in tenders; % lifts within ±10% of clean tickets and monthly bias; cost to serve per device-month; customer value-to-fee multiple; operator ticket-sharing rate.

## 12. Pitch (one paragraph)

Europress already knows how full every machine is. Only the waste operator knows how much it weighs, and that is why customers distrust their invoices. With a firmware update and no new hardware, every SMART machine gets a ballpark weight. Calibrated against the operator's own weighbridge tickets, it turns into €/t per stream and a neutral monthly second opinion. On the challenge dataset, that is about €1,064 of identified value per contract-year (hypothetical prices) for a €15 monthly add-on. Customers who need audit-grade weight get the load-cell platform inside their lease. For Europress, the prize is not the subscription. It is the renewal: the customer who sees their €/t does not switch to Orwak at year six. We ask for €150k and two kill gates, not a blank cheque.

## 3 strongest ideas in this plan

1. **The business case is framed around service-contract and lease renewal**, which is where Europress makes its money. It is honest that subscription alone gives a negative NPV.
2. **Stage gates with pre-registered, numeric kill criteria** cap the downside at about €150k and test exactly the two drivers that dominate the tornado (adoption and renewal).
3. **Hardware is sold only inside the lease.** The 43-month payback works within a 72-month lease and fails as a retrofit sale. Intro stays free, which respects "cheapest wins".

## 3 weakest points

1. **The fleet size (12,000), service margin (€600 per year), machine margin (€5k) and +5 pp renewal uplift are all assumptions.** The base case NPV hinges on them.
2. **The €1,064 per contract-year value comes from synthetic, hypothetical prices.** About 99% of it is tariff gaps, not weight. A sceptic can say "a tariff benchmark without weight gets most of this".
3. **Europress's public financials are unclear.** The €70M (Tommi) does not match €35.6M (Finnish entity). Ownership and the competitors' weighing roadmaps are unverified, and the competitor scan was shallow (search snippets only).
