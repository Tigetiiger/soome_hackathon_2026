# BUSINESS PLAN: Weight add-ons for Europress SMART

Europress × Since AI Hackathon 2026. This is the merged conclusion of 4 competing business-plan agents (CFO, ESG/chains, cheapest-wins/Poland, data-platform), a strategy agent, a company-research agent, a data-value analyst, and a comparison against the parallel Sonnet session. Sources and full reasoning are in `agents/`.

**Tags:** [F] = fact, sourced in `agents/company-profile.md` or `business-strategy.md`. [T] = said by Tommi at the kick-off. [D] = computed on the synthetic dataset (hypothetical prices, not real savings). [E] = estimate. [A] = assumption.

---

## 0. The plan in five lines

1. Europress **already sells weighing** [F]: the Scale Solutions 4-corner platform, the Scaletipper X1, and a "waste volume calculator" that estimates weight without a scale. It also has SMART tiers, SMART Center, an operator API and Retrofit kits [F]. **We do not propose a new business. We propose upgrades to these.**
2. **Weigh.** Upgrade the volume calculator into a **pressure-based virtual scale** with an uncertainty band. It is free on every SMART machine (€0 BOM). Operator tickets calibrate it, and the existing scale platforms supply ground truth.
3. **Create value.** Europress becomes the **neutral second opinion** on what the operator weighs and invoices. The products are Verified Weight reconciliation, Proof of Fullness for fixed schedules, a €/t contract benchmark and a reporting pack. The system drafts every action and **a human approves it**.
4. **Money.** Charge add-on fees inside the existing **Insights / Integrated** tiers and the **lease / service contract**. As a standalone product the software is small. The real return is **more customers on SMART and more service-contract renewals**, which is where Europress makes its profit [T].
5. **Sequence.** Start with the 20% who hold the value (multi-site chains). Keep a free kg teaser for the other 80%. Use Proof of Fullness to open **Poland**.

## 1. Problem: Tommi's words mapped to the evidence

| Tommi [T] | Evidence |
|---|---|
| "The operator only has the information about the weight… who owns the data is the holy grail" | Weight decides charges and credits (challenge brief) [F]. In the data, 21% of retail lifts have **no ticket**, and one operator shares **0%** of its tickets [D] |
| Customers "never even trust" the operator's figures | **77%** of large device-vs-ticket gaps are on the weighbridge side: side waste 34%, stale stored tare 30%, combined loads 12%. **Only 3.9% are sensor faults** [D]. Stored-tare tickets scatter about 2× more than weighed-tare ones (robust SD 7.5% vs 3.8%) [D] |
| SMART already makes machines as full as possible | So we **do not** sell pickup timing. On **fixed and hybrid schedules** (Poland, Central Europe), 30–32% of lifts are unjustified, worth about €2.5–2.7k per device-year [D] |
| "Cheapest wins"; ballpark accuracy is fine | T0 has €0 BOM. Our error budget puts it at ±12–15% (1σ) per lift, and ticket calibration does not shrink that per-lift error [E]. Its value is removing *bias*: monthly totals reach ≈5–6% after ~20 clean tickets [E] (error budget: `soome_hackathon_2026/docs/agents/science-researcher.md` §2). At σ≈10% a +10% overbilling is caught 62% of the time per quarter [D]. The 96%/10-month figure only holds for the dataset's simulated precise sensor (±1.4%), not for T0 |
| Bio-waste is hard; humidity changes weight | Bio-waste gets wider uncertainty bands. Moisture becomes a money story: under EN 643, recovered paper above 10% moisture can be claimed back [F, from the Sonnet science lens] |
| "Recognise material that doesn't fit" | Our density proxy **fails** on this data (~1% precision) [D]. This goes on the roadmap because it needs pressure-curve shape from new firmware. It is not a demo claim |

**Who has the pain: value is concentrated.**
- The mean is about €1,064 per contract-year, but the **median is €0**. 52% of contracts show no positive value [D].
- Among the 20 customers with contract-action cases, the top 5 hold 75% of the value [D]. Across all 52 customers, the top 5 hold 54% of realisable value [D].
- This matches Tommi's 80/20: "big chains want more SMART, small want to save money".

## 2. Part 1 in business terms: an accuracy ladder on existing assets

| Tier | What it is | BOM per unit | Accuracy (honest) | Existing Europress asset it reuses |
|---|---|---|---|---|
| **T0 Virtual scale** | Ram back-pressure per stroke, plus cycles and fill → kg ± band | **€0.** Firmware only: 10–20 Hz logging, delivered over the air | ±12–15% per lift uncalibrated; ±5–6% on monthly totals [E, error budget]. Our simulator: 5.3% mean error per lift on unseen machines [S] | 0–200 bar pressure sensor, fill algorithm, Vincit ML pipeline, "waste volume calculator" |
| **T1 Ticket-calibrated** | Clean tickets (weighed tare, single load) update a per-machine gain via a Kalman/robust update. A CUSUM alarm flags drift | €0 | Per lift still ≈ ±12% [E]; monthly bias ≈ ±5–6% after ~20 clean tickets [E]; plus a drift alarm | Existing operator API and emptying calls |
| **T2 Measured** | 4 stainless IP68 C3 shear-beam load cells under the supports | €3.4–6.3k installed, mid €4.85k (`smartweight/BILL_OF_MATERIALS.md`). Sold **inside the lease**: hardware alone is ≈ €47–88/month over 72 months (€3.4–6.3k ÷ 72) | P95 2.3% [S]; certified cells (Tier 3, €5.4–10k) P95 1.4% [S]; verification grade | **The Scale Solutions platform, already a product** |
| **Golden cohort** | T2 on 2–5% of the fleet, used as ground truth for the fleet model | €34–63k for 10 machines (10 × €3.4–6.3k) [E] | A fleet model trained on 25 scale-fitted machines reached 4.96% error on unscaled ones (Mansouri 2025, via the Sonnet science lens) | Kerava manufacturing and the existing platform |

**Validation experiment (pilot).**
- Setup: 10 machines, about 150–240 lifts. The reference is the T2 platform plus weighed-tare tickets.
- Analysis: Bland-Altman agreement, leave-one-machine-out error, and an ablation of how many tickets T1 needs.
- Acceptance: monthly error ≤6% and per-lift p90 ≤20%.

**Legal position.** This is verification, not a billing basis. Billing on device weight would fall under NAWI 2014/31/EU legal metrology.

## 3. The add-ons, attached to what Europress already sells

All prices are hypothetical; the logic is in §4.

| Add-on | Attaches to | Who buys | What the customer gets (measurable) | Price |
|---|---|---|---|---|
| **kg teaser:** a monthly kg band per machine | **SMART Intro**; it also upgrades the volume calculator | Everyone, including the ~85% not on SMART today | "Your cardboard this month: 11.8 t ± 0.7" | **Free.** An acquisition hook costing about €15 per device-year to serve [E] |
| **Verified Weight:** device vs ticket vs invoice per lift, cause attribution, drift alarm | **SMART Insights** | Chains, logistics firms, property owners | Gaps explained neutrally. Recoverable billing errors average €150 per device-year [D]. The share of mass-billed € that can be verified rises from 77% to **96%** [D] | **+€15/device/month** list price; **€12 when bundled** into new leases |
| **Proof of Fullness:** tonnage and fill evidence that a scheduled lift was not needed, plus a schedule-change request that a human approves | Insights. Launch in **Poland, Benelux and Central Europe**, and for the 30–40% of Finnish pickups not on call | Fixed-schedule sites | 18–20 avoidable lifts per device-year, worth about €2.5k [D]. Switching fixed → on-call is positive in 74% of simulated cases [D] | **Gain-share: 25% of the verified avoided-lift cost** in year 1, then convert to Insights |
| **Contract and €/t benchmark + action inbox:** dispute, request ticket data, renegotiate. Tendering is shown last and is gated | **SMART Integrated** | Procurement teams at chains | 28% of renegotiation value sits on contracts where **device weight is the only mass figure** [D]. Drafts cite evidence rows, and nothing is sent without approval | Included in Integrated (+€25/device/month), or a **chain licence at €10–40k per year** |
| **Reporting pack:** kg per fraction, recycling rate, "unknown destination" share, Poland BDO mass cross-check | Integrated. Builds on the per-tenant reports Scale Solutions already produces | Sustainability teams; Polish customers (BDO reporting is mandatory) | Covers the 21% of lifts that are untracked today. Ready for ESRS E5-5 (the Omnibus has narrowed CSRD to large companies) and for BDO | Part of Integrated, or €X per legal entity per year [A] |
| **Operator data feed (give-to-get):** operators push tickets via the API and get back a reconciliation receipt and a private tare-hygiene report | Existing operator API | Operators. Fortum, Remeo and Alba are already Europress references [F] | Fewer disputes and better weighbridge hygiene. Operators see findings **first** | Free for operators who share; a paid analytics feed later |
| **Measured tier:** scale platform as a lease uplift | **Lease + service contract** | Sites that need verification-grade weight (tenant billing, disputes) | P95 1.4–2.3% weight [S] | Inside the lease, priced from Europress's real platform cost. Our retrofit hardware alone is ≈ €47–88/month over 72 months, so the earlier +€39–49/month would not cover it |
| **Calibration and drift checks** | **Service contract**, during technician visits that already happen | All service-contract customers | The ticket-based drift alarm fires about 33 days before today's fix [D] | Bundled; it helps justify the service price |

**Why AI, and where.**
- **Rules decide.** In the benchmark, rules beat ML (0.73 vs 0.35 macro-F1) [D].
- **Claude drafts** explanations, dispute letters and operator notes, with row-level citations.
- **SMART Center staff or the customer approve** before anything is sent.

This is a managed service that SMART Center can run without hiring a data team.

## 4. Pricing logic

This replaces the €10–25 spread between the agent plans with one consistent set.

- **Rule.** The fee is at most ⅓ of the value the customer can realise. This is **our own assumption**: the dataset's business-case template uses a softer 2× value-to-price condition [A].
- **€15/month (€180/year).** The customer must realise about €540 per year. That is plausible for the top-value segments (chains, fixed schedules) but not for the median contract. **So the median customer is not charged; they get the free teaser.**
- **Integrated +€25.** Justified only by compliance/reporting value plus the contract benchmark. The ESG lens puts realisable value at ≈ €545 per device-year, only 1.8× the fee, which is borderline. Offer a **chain licence** instead whenever it is cheaper for the customer.
- **Gain-share.** It removes the price objection in Poland ("cheapest wins"), and converts to a subscription once the value is proven.
- **Traceability.** Every € figure lives in one `params.yaml`, and the demo shows a sensitivity grid. We say out loud that the prices are hypotheses.

## 5. Economics (illustrative; replace the inputs with Europress numbers)

| | Low | Base | High |
|---|---|---|---|
| Paying devices, year 3 | ~1,000 | ~3,000 | ~7,000 |
| Add-on ARR, year 3 | ~€0.18M | **~€0.6–0.75M** | ~€1.8M |
| Recurring gross margin | ~75% | ~79% | ~82% |
| Software break-even | Not reached | ~3,100 active devices (early Y4) | Y2–3 |

Sources: `agents/business-strategy.md` (`analysis/pl_model.py`), `bizplan-esg-chains.md` and `bizplan-cfo.md` (`bizplan-cfo_model.py`).

**CFO view [E].**
- The subscription alone has a **negative 6-year NPV**: −€0.33M at a 10% discount rate.
- Adding an assumed +5 pp service-contract renewal uplift and higher SMART attach (worth about €60 per adopter per year) gives a **base NPV of +€0.23M**, with a low case of −€0.83M and a high case of +€2.37M. Payback comes in year 5.
- The biggest levers are adoption and the renewal uplift.

**The board pitch is therefore "weight makes SMART and the service contract stickier, which is where Europress makes its profit", not "a new revenue line".**

**Company context [F].**
- The Finnish parent had €40.0M revenue in 2025, at a 6% EBIT margin.
- The group is about €61–63M before eliminations, which makes Tommi's ~€70M plausible.
- About 15% of customers are on SMART [T].
- On a fleet of about 12k machines [A], each +1 pp of SMART attach is about 120 devices.

## 6. Go-to-market: stage gates with kill criteria

| Phase | When | What | Gate to continue (kill if missed) |
|---|---|---|---|
| **0 Pilot** | Q1–Q2 2027 | 10-machine golden cohort (T2 platform), plus 50 T0/T1 machines at 1–2 existing chain customers and 1 friendly operator. Tamro and Citycon are public references that "monitor filling weights" and transport efficiency [F], so customers like them are natural fits | Monthly error ≤6%; at least 1 operator sharing tickets via the API; the customer says they would pay at least €12 |
| **1 Finland Insights launch** | H2 2027 | Free kg teaser on all SMART devices; Verified Weight in Insights; SMART Center reviews the drafts | At least 10% of Insights devices adopt; disputes resolved neutrally; no operator escalation |
| **2 Poland / Benelux** | 2028 | Proof of Fullness gain-share, BDO mass cross-check, an operator partner of the Alba type | At least 30% of pilot sites switch fixed → on-call; gain-share revenue ≥ cost to serve |
| **3 Platform** | 2029+ | Operator give-to-get feed at scale. A volume-only material-flow index, with at least 5 customers per region × stream cell (20 of 32 cells qualify [D]). Paid operator analytics | EU Data Act consent clauses in every contract; competition-law review passed |

**Cost to start [E].**
- People: about 2–3 FTE for 6 months, working with Vincit, on firmware logging, the model and the portal screens.
- Golden cohort: €34–63k (10 × €3.4–6.3k).
- Phase 0 budget: ≈ €211–267k in total, itemised in `output/05_business_plan_addon.md` §6. The Phase 0 gate caps the downside at that budget.

## 7. Operator stance (critical)

Europress's **new CEO (from Oct 2025) and incoming CCO both come from environmental services at Lassila & Tikanoja**, a major Finnish operator [F]. Operators are also Europress customers and public references [F].

So the product must be framed as **verified service quality for everyone**, never as "catching operators":
- **Cause attribution comes first.** Findings about an operator's own vehicles go **to that operator first**.
- **Tendering or switching** is the last action, and it is gated.
- **Give-to-get:** operators that share tickets get a free hygiene report in return.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Per-lift accuracy too weak for verification | Sell verification at monthly/contract level; T1 calibration; T2 where needed; publish the bands |
| The median customer sees €0 of value | Free teaser for them; paid add-ons only for chains and fixed schedules |
| Legal metrology (NAWI) | Position as "second opinion, not billing basis"; T2 legal-for-trade only if required |
| Operator backlash | Neutral attribution, operator-first disclosure, give-to-get, gated tendering |
| EU Data Act / competition law | Use data only under customer contract clauses; the index is volume-only and k-anonymous, with no prices |
| Price sensitivity | Free tier, gain-share, bundling into the lease |
| Evidence is synthetic | Every number is tagged; the pilot is designed to replace it with real data |
| Patent prior art (e.g. US8794135B1, US11162834B2) | Freedom-to-operate check before productising |

## 9. KPIs

| Area | KPIs |
|---|---|
| Commercial | SMART attach rate · Insights/Integrated upgrade rate · service-contract renewal |
| Weight quality | Monthly weight error vs reference · % of lifts with tickets (operator sharing) |
| Outcomes | Disputes opened → resolved without escalation · fixed → on-call conversions |
| Efficiency | Cost to serve per device |

## 10. Industry-change vision (3–5 years)

**"Every kilo known at the source."** Today the truck owner reveals the weight at the end of the chain. In this vision it becomes a shared, neutral, continuously checked fact at the compactor. Contracts are priced per verified tonne, recycling is reported from source data, and operators compete on service quality instead of on information. Europress gets there without owning a single truck.

Optional bolt-ons for the pitch, from `agents/creative-ideas.md`:
- **Anchor scheduler:** send calibration visits where uncertainty × € is highest.
- **"Water you paid for":** split dry vs wet tonnes, and support an EN 643 moisture claim.
- **Trolley-photo pre-sort (future):** a wrong-material warning before the drop.
- **BDO waste-card autofill:** for Poland.

## 11. Questions for Tommi (Saturday)

1. Do the "filling weights" that Tamro and Citycon see today already come from a pressure-based kg estimate? If so, we pitch an **upgrade**.
2. What do Intro, Insights and Integrated contain today, and at what price? What is "SMART FullService"?
3. How many machines are installed, and how many are connected? How many scale platforms exist, and what are their accuracy and price?
4. What are the service-contract margin and churn? Do leases bundle SMART?
5. Is per-stroke pressure data archived, and at what sampling rate (Hz)?
6. Who owns the data under the operator API terms?
7. Poland: is there a factory? What is the installed base? Is BDO reporting a pain point for customers?

## 12. One-paragraph pitch

Europress compactors already know how full they are. With a firmware upgrade they can also estimate how heavy they are, for €0 of extra hardware. Operator tickets keep that estimate honest, and Europress's own scale platforms supply ground truth. Inside SMART, that weight becomes a neutral second opinion:
- every lift is reconciled against the ticket and the invoice;
- differences are explained by cause, without blame;
- fixed-schedule customers get proof of which pickups they didn't need;
- AI drafts every recommended action, and a person approves it.

It is sold as an add-on to the existing SMART tiers, the lease and the service contract. Small customers get a free kg number; chains and fixed-schedule sites pay from the value they measure. The result: more customers on SMART, stickier service contracts, and Europress earlier in the waste value chain, without owning a single truck.
