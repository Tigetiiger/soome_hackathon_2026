# Business findings and decisions

Europress × Since AI Hackathon 2026 · consolidated 2026-11-07.

This document merges everything we found about the business side:
- the Europress briefing (see `01_transcript_analysis.md`);
- the merged business plan and business case from the weight track (`europress_conclusions/`);
- the alternative draft plan (`input-files/message.txt`);
- nine agent reports: company, strategy, four competing business plans, data value, creative ideas, and a comparison with a parallel session;
- the decisions taken while building the customer dashboard.

Full source documents are in `business_sources/`.

**Tags:**
- **[T]** said by Europress (Tommi, the kick-off or the briefing)
- **[F]** public fact (sources in `business_sources/agents/company-profile.md` and `business-strategy.md`)
- **[D]** computed on the synthetic dataset, with hypothetical prices. These are not real savings.
- **[E]** our estimate
- **[A]** our assumption

---

## 1. What Europress asked for

| Ask | Source |
|---|---|
| Focus on **weight**. Fill prediction and pickup optimisation already work in SMART | [T] briefing 00:12, 05:10, 29:00 |
| Always say **for whom**. Pitch it as you would pitch to that customer | [T] 00:19 |
| "**The meat is the business model.**" Give a short statement on how weight is obtained | [T] 20:23 |
| Win-win-win: customer, operator, Europress | [T] 25:20 |
| "We want to be **more than a device manufacturer**", earlier in the value chain. Weight is the key | [T] 33:10 |
| More SMART customers. Only **~15%** of customers are on SMART today | [T] |

## 2. Company facts

- **Europress Group Oy** (Kerava, founded 1977, family-owned) [F].
- **Finnish entity:** €40.0M revenue in 2025 (+12%), €2.47M operating profit (6% margin), 138 staff [F].
- **Group:** subsidiaries in Sweden (118 MSEK), Norway (105 MNOK), Poland (6–8 MPLN) and Benelux. That totals ≈ **€61–63M** before eliminations, which makes Tommi's "~€70M" plausible [F/E].
- **Leadership:**
  - The new **CEO (Oct 2025), Petri Salermo**, spent 24 years at Lassila & Tikanoja, a major Finnish waste operator [F].
  - The incoming **CCO (Jan 2027), Eljas Tuovinen**, is also ex-L&T [F].
  - → Leadership knows operators well, and operators are Europress customers. The product must not "catch operators".
- **Offering:**
  - Compactors (COMBI, DUO) and balers, sold or leased; ~6-year leases are typical [T].
  - **Service contracts are "the real profit"** [T].
  - Retrofit kits for any brand [F].
  - Scale Solutions: a 4-corner scale platform and the Scaletipper X1 (1 kg resolution) [F].
  - A "waste volume calculator" that estimates weight without a scale [F].
- **SMART:**
  - About 15 years old, built with Vincit [F].
  - SMART Center gives remote support and claims "up to 90% of problems solved remotely" [F].
  - Operator API; tiers Intro / Insights / Integrated [T]; no public price list.
  - Sold as a **service fee only, with no up-front charge** [T briefing 21:44].
- **Published SMART claims** (vendor averages, no uncertainty): −40% waste cost, −37% emptyings, +58% fill rate [F epsmart.fi].

## 3. Market and competitors

- **Fill-level vendors sell volume, not weight.** That covers Compology/RoadRunner, Sensoneo, Enevo, Nordsense, Bramidan BRA-IN and Waste Harmonics [F].
- **Every existing weight source belongs to the operator:** the weighbridge, or on-truck weighing (Hyva, RDS) [F].
- **We found no vendor offering customer-side, operator-neutral weight verification per lift in the Nordics** [E]. Europress already owns the hardware and the channel; what's missing is the verification product.
- **Greyparrot** (raised $27M in 2026) shows that waste data can be sold to third parties and accepted by regulators [F].
- **Closest prior art:** patents US11162834 (BACE, retrofit weighing) and US8794135B1. Both need a **freedom-to-operate check** [F].

**Regulatory tailwinds [F]:**
- CSRD/ESRS E5-5 (waste mass by treatment), narrowed by the Omnibus to large companies.
- The Waste Framework Directive revision, Directive (EU) 2025/1892 (food waste −30% by 2030).
- PPWR (cardboard stays the core compactor stream).
- The Finnish Waste Act (separate collection).
- **Poland's BDO register** (mandatory reporting of mass per waste code).
- NAWI 2014/31/EU: device weight is **verification only, not a billing basis**.

## 4. The customer problem and what the data shows

**The problem in Europress's words [T]:**
- The customer pays per tonne for a weight they cannot see.
- The weight is measured by the party that is paid per tonne.
- Customers ask: "Am I paying the right amount? Is the operator doing its best? Would another operator serve me better?"
- Contracts run 3 years and then go to tender, and customers lack tools to compare.

**Findings from the synthetic data [D]:**

| Finding | Number |
|---|---|
| Lifts with no verifiable weight today | **26%** (one operator shares 0% of tickets). With the device estimate, **97%** of lifts have at least one independent weight (74% with a ticket today) |
| Collection spend with no €/t | 11% (€349k) |
| Mass-billed € that can be verified | **77% → 96%** with device weight |
| Causes of device-vs-ticket gaps > 10% | Side waste 34%, stale stored tare 30%, combined loads 12%, **device drift only ~4%** → the gaps are explainable, not bad intent |
| Naive "operator bias" score | Wrongly flags 74% of operator-region-months; cause adjustment cuts the error from 5.5 to 1.2–1.6 pp |
| Value concentration | Mean ≈ €1,064 per contract-year, but the **median is €0**. The top 5 of all 52 customers hold 54% of realisable value; among the 20 customers with contract-action cases, the top 5 hold 75% (matches Tommi's 80/20) |
| Billing errors that *need* independent weight | Only ~€8k in 10 months (~€21 per device-year) → **don't headline overbilling recovery** |
| Fixed/hybrid schedules | 30–32% of lifts unjustified, ≈ €2.5–2.7k per device-year |
| Operator/contract actions (tender, renegotiate) | Best action set = 7.9% of cost. Weight *enables* it (+€190 per contract-year where tickets aren't shared) |
| Fill-vs-mass order guard | 96% precision against 5% for a fill-only rule (the one case where weight beats fill outright) |

**Negative results, stated openly [D]:**
- **Moisture and contamination can't be detected from mass vs fill** (AUC 0.5–0.7, density proxy ~1% precision).
- **Over-servicing gains nothing from weight**; that belongs to SMART.
- **±3.3% per lift is unrealistic**: 53% of paired lifts exceed it, and the weighbridge itself is only ±100 kg on 78% of lifts.
- **Isolation forest is useless** for weight gaps (F1 0.10 on actionable device-vs-ticket gaps). On that same test, rules reach 0.89 and gradient boosting 0.91–0.93. On the full anomaly benchmark (all families), rules beat ML: 0.73 vs 0.35 macro-F1, and a rules + ML hybrid reaches 0.78.

**Findings from the customer dashboard (all 52 synthetic customers) [D/E]:**
- **Median savings potential** across five levers:
  - small customers (≤3 machines): **€5.6k a year, 22% of cost**;
  - medium (4–10): **€16.4k, 20%**;
  - large (11+): **€69.4k, 32%**.
  - → The "what does an average customer save" message Europress doesn't advertise today [our note].
- **Demo customer** (hotels, 9 machines):
  - **Cost:** €140.6k a year at 283 €/t; recycling rate 43%.
  - **Fill:** machines average 49% full when emptied (target 85%).
  - **Savings potential:** €60.5k a year, of which €40k is from emptying only when full.
  - **Mixed waste** rose from 56% to 60% of tonnes, and recycling fell from 44% to 40% (Oct–Dec 2025 vs Jul–Sep 2026).
  - **A contract notice deadline** falls on 17 Oct 2026 (data as of 30 Sep 2026).

## 5. Product decisions: what we sell and what we don't

**We sell:**
1. **An accuracy ladder for weight, built on existing assets.**
   - **T0 virtual scale:** firmware only, €0 BOM. About ±12–15% per lift and ±5–6% on monthly totals [E, error budget]. Our simulator: 5.3% mean error per lift on unseen machines [S].
   - **T1 ticket-calibrated:** €0 extra hardware. Adds a drift alarm.
   - **T2 load cells:** €3.4–6.3k installed, in the lease, P95 2.3% [S] (certified Tier 3 cells: P95 1.4%), for 2–5% of the fleet as ground truth (the "golden cohort").
2. **A neutral second opinion.**
   - Each lift is reconciled: device vs ticket vs invoice, with cause attribution.
   - A €/t benchmark and an operator scorecard.
   - **Proof of Fullness** for fixed schedules.
   - A reporting pack (ESRS E5-5, Polish BDO).
3. **The customer dashboard (built).** Every number is clickable with its formula, source tables and rows. Five savings levers in euros, an AI advisor, Finnish and English.
4. **An operator view (built)** as a give-to-get offer:
   - operators get a 14-day pickup forecast, fill at emptying, and a list of customers renewing;
   - in return they share weighbridge tickets.

**We don't sell or pitch:**
- pickup optimisation or routing (SMART already does it);
- moisture or contamination detection;
- legal-for-trade weighing;
- "gets more accurate every pickup";
- a headline on overbilling recovery;
- fully automatic actions;
- the brand name "TrueLoad" (it's already a truck-overload product).

**How AI is used:**
- **Rules decide** (on the full anomaly benchmark they beat ML: 0.73 vs 0.35 macro-F1 [D]).
- **Claude explains and drafts** dispute letters and advice, citing evidence rows.
- **A person approves** every action, either SMART Center staff or the customer.

## 6. Commercial model

| Offer | Attaches to | Price [A] | Logic |
|---|---|---|---|
| **Free kg teaser plus a dashboard preview** | SMART Intro; replaces the volume calculator | Free (cost to serve ≈ €15 per device-year [E]) | Acquisition hook for the ~85% not on SMART |
| **Verified Weight** | SMART Insights | **€15 per device per month list, €12 bundled into a new lease** (draft range €5–15) | Fee ≤ ⅓ of realisable value. Charge chains and fixed schedules; the median customer stays free |
| **Proof of Fullness** | Insights; launch in Poland and Benelux | **25% gain-share** of verified avoided-lift cost in year 1, then a subscription | Answers "cheapest wins" |
| **Contract benchmark, action inbox and reporting pack** | SMART Integrated | +€25 per device per month, or a **chain licence of €10–40k a year** | Procurement and ESG teams |
| **Operator Review service** | Integrated / SMART Center | 15% of *verified* recovered or avoided cost, capped | Weight is the evidence layer |
| **Measured tier (scale platform)** | Lease plus service contract | In the lease, priced from Europress's real platform cost. Our retrofit hardware alone is ≈ €47–88 per month over 72 months (€3.4–6.3k ÷ 72), so the earlier +€39–49 would not cover it | Only where value > cost |
| **Operator data feed** | Operator API | Free for operators who share; paid analytics later | Turns the data-ownership fight into a trade |
| *Idea from our notes* | SMART | **Discounted SMART for the first 12 months** | Lever 1 (fuller pickups) usually pays it back alone |

**Price decision:** we use **€15 list / €12 bundled**, and record the alternative.
- The draft plan (`business_sources/message_draft_plan.md`) argues for **€8** per device per month. At €8 the contribution is only ~€3.2 per device per month, so break-even needs ~3,500 paying devices.
- The merged plan picks €12–15, which matches the parallel session's €15.
- **Europress's real tier prices should replace both.**

## 7. Economics (illustrative)

| | Low | Base | High |
|---|---|---|---|
| Paying devices, year 3 | ~1,000 | ~3,000 | ~7,000 |
| Add-on ARR, year 3 | ~€0.18M | ~€0.6–0.75M | ~€1.8M |
| Recurring gross margin | ~75% | ~79% | ~82% |
| Software break-even | not reached | ~3,100 devices (early year 4) | years 2–3 |

**The CFO lens says the subscription alone doesn't pay back:**
- Its 6-year NPV is **−€0.33M** at 10%.
- Adding a +5 pp service-contract renewal uplift and higher SMART attach (≈ €60 per adopter per year) gives a **base NPV of +€0.23M** (low −€0.83M, high +€2.37M), with payback in year 5 [E].

**→ Board message: "weight makes SMART and the service contract stickier", not "a new revenue line".** Each +1 pp of SMART attach is about 120 devices on an assumed ~12k-machine fleet [A].

## 8. Go-to-market with kill criteria

| Phase | When | What | Continue only if |
|---|---|---|---|
| 0 Pilot | Q1–Q2 2027 | 10-machine golden cohort (T2) + 50 T0/T1 machines at 1–2 Finnish chains + 1 operator sharing tickets. Tamro and Citycon are natural fits [F] | Monthly error ≤ 6%; ≥1 operator sharing tickets; the customer would pay ≥ €12 |
| 1 Finland launch | H2 2027 | Free kg teaser + dashboard on all SMART devices; Verified Weight in Insights | ≥10% of Insights devices adopt; no operator escalation |
| 2 Poland / Benelux | 2028 | Proof of Fullness on gain-share, BDO cross-check | ≥30% of pilot sites move fixed → on-call; gain-share ≥ cost to serve |
| 3 Platform | 2029+ | Operator feed at scale; anonymised material-flow index (≥5 customers per cell) | EU Data Act consent in every contract; competition-law review passed |

- **Cost to start:** ~2–3 FTE for 6 months (with Vincit), plus €34–63k for the golden cohort (10 × €3.4–6.3k).
- **Downside:** capped by the Phase 0 gate at the Phase 0 budget, ≈ €211–267k, itemised in `05_business_plan_addon.md` §6 [E].

## 9. Operator stance (critical)

Frame the product as **verified service quality for everyone**:
- Cause attribution comes first.
- Findings about an operator's vehicles go **to that operator first**.
- Tendering is the last action and is gated.
- Language is "difference / needs a second look", never "overcharged" or "fraud".
- Operators who share tickets get a better scorecard and a free hygiene report.
- In the dashboard, the operator table is labelled "neutral, not a verdict", and the AI is instructed to stay neutral.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Per-lift accuracy is too weak | Verify at monthly/contract level; T1 calibration; T2 where needed; publish the bands |
| The median customer sees €0 | Free teaser and dashboard; charge only chains and fixed schedules |
| Legal metrology (NAWI) | "Second opinion, not billing basis" |
| Operator backlash | Neutral attribution, operator-first disclosure, give-to-get |
| EU Data Act / competition law | Contract consent clauses; volume-only, k-anonymous index with no prices |
| Price sensitivity | Free tier, gain-share, bundling into the lease |
| Evidence is synthetic | Every number is tagged; the pilot replaces it with real data |
| Patents | Freedom-to-operate check before any hardware commitment |
| SMART paid base unknown | Revenue scales with it linearly; ask Europress |

## 11. KPIs

- **Commercial:** SMART attach rate; Insights/Integrated upgrade rate; service-contract renewal.
- **Weight quality:** monthly error vs reference; % of lifts with tickets.
- **Outcomes:**
  - disputes resolved without escalation;
  - fixed → on-call conversions;
  - customer fill at emptying (toward 85%);
  - mixed-waste share (down).
- **Efficiency:** cost to serve per device.

## 12. Decision log

| # | Decision | Alternatives considered | Why | Source |
|---|---|---|---|---|
| 1 | Build on **weight**, not fill prediction | Time-series fill forecasting (other teams) | Europress: fill prediction already works; "everything is about weight" | [T] briefing |
| 2 | **Upgrade existing products** (scale platform, volume calculator, SMART tiers) instead of a new business | New standalone product | Europress already sells weighing; the profit is in SMART and service | Business plan §0 |
| 3 | Position as a **neutral second opinion**, not a billing basis | Legal-for-trade weighing | NAWI rules; data shows gaps are mostly weighbridge-side causes | [F]/[D] |
| 4 | **Rules decide, AI drafts, a person approves** | ML-first; automatic actions | Rules beat ML on the benchmark; trust; operator relations | [D] |
| 5 | **Free tier for the median customer**, charge chains and fixed schedules | Charge everyone | The median contract value is €0 | [D] |
| 6 | Price **€15 list / €12 bundled** in Insights | €8 (draft plan), €10, €25 | Fee ≤ ⅓ of value; agrees with the parallel session | §6 |
| 7 | Board pitch = **stickier SMART and service contracts** | "New revenue line" | Standalone NPV is negative | CFO lens |
| 8 | Main product of this track = an **end-customer dashboard** that educates and shows savings in euros | Internal SMART Center tool | Our session goal; "educate the client" was the priority note | User brief |
| 9 | **Every number is clickable** to its formula, sources and rows | Plain KPI tiles | "Clicking on the value will show where the info is coming from" | User brief |
| 10 | **Five savings levers**: empty when full, avoid fees, sort more, compare €/t, invoice second look | Single headline number | Explainable, and each one is actionable | Dashboard |
| 11 | **Biowaste and max-interval pickups excluded** from "too early"; the €/t lever is computed **after** the fuller-pickups saving | Raw counts | Avoids hygiene-bound lifts and double counting (this cut the demo customer's total from 55% to 43% of cost) | Dashboard |
| 12 | Assumptions shown as amber boxes: 85% target, 20% sortable, 50% of fees avoidable, 50% of the price gap closable, 1.1 kg CO₂/km | Hide them | Honesty; Europress can replace them | Dashboard |
| 13 | **"Customers like you"** savings by segment | — | Europress doesn't advertise average savings today | Our notes |
| 14 | Demo opens on a **mid-size customer** (hotels, 9 machines) with a switcher for all 52 | Largest chain; single hero | A relatable story: mixed waste rising, a notice deadline, low fill | User choice |
| 15 | **Operator tab** as a secondary view | Customer only; full parity | Side goal: data operators don't have | User choice |
| 16 | **Finnish default, English toggle** | English only | Home market plus expansion abroad | User brief |
| 17 | AI = **headless Claude Code** on the server, read-only over the data folder | Anthropic API key with custom tools | Matches the "Claude Code demo server" ask; no key needed | User choice |
| 18 | AI hardening: argument prefix, `--tools Read Glob Grep`, dontAsk, rate and spend caps | — | Security review found a HIGH argument-injection issue; fixed | Security review |
| 19 | Visual base: Figma PM dashboard layout + epsmart.fi tokens (navy, mint CTA, pink accent) | Pure Figma style; pure epsmart | "Match their visual identity with a fresher look" | User brief |
| 20 | Hosting: **tailnet only for now** (http://hackathon.tail8f13e3.ts.net:8080); europress.acq.ee later via port forwarding or a VPS relay | Tailscale Funnel; Cloudflare Tunnel | The NAT blocks 80/443; DNS is at Zone.ee, not Cloudflare; the user chose tailnet access | User choice |
| 21 | The weight algorithm is **out of scope** for this track | — | Another team builds it | User brief |
| 22 | **Minimal redesign**: the Haldus stylesheet principles (tokens, ink actions, hairlines, 5 sizes, 4 radii, state-only colour) with the Europress SMART logo and navy | Keep the v1 colourful look | User: "more minimalistic… clean"; Haldus colours and logo explicitly excluded | User brief |
| 23 | Left navigation = **separate tabs**, not anchors in one long page | Single scrolling page | User: "links on the left shall show different tabs" | User brief |
| 24 | Customer picker → **account menu + Account tab** with contracts and price lists | Plain select | User: show "the customer contract and everything there is needing to be known" | User brief |
| 26 | **Ready-made answers first**, drill down on click (3 levels) | Reports and charts first | Tommi (2nd briefing): "simplify, simplify, simplify", "instructions for dummies" | Transcript 2 |
| 27 | **No quality grades**: accepted vs rejected (burned) only | Show the A–D grades from the dataset | Tommi: plants don't grade, "either it's total crap or…" | Transcript 2 |
| 28 | **Versioned, retrainable weight model** (v1–v3 fitted, v4 planned) | One fixed estimate | Tommi: make it extendable, retrain with humidity/temperature; hybrid with a cheap reference sensor | Transcript 2 |
| 29 | **Sales alerts with "Tell the customer"** | Sales reads the dashboards | Tommi: salespeople need "tell me what I should tell the customer" | Transcript 2 |
| 30 | **No customer invoice upload** | Upload and AI analysis of invoices | Tommi: point-to-point integrations with thousands of customers are "probably not feasible"; work through the ~20 operators instead | Transcript 2 |
| 31 | **SMART Lite / Complete tiers postponed** | Build them now | User decision | User |
| 25 | **Savings explained at first sight** ("How you save" card under the KPIs) | Single number + separate tab | User: "money saved should explain right away how the money is saved" | User brief |

## 13. Open questions for Europress

1. What do Intro, Insights and Integrated contain today, and at what price? How many devices are on paid SMART, and what is the churn?
2. Is the per-stroke pressure trace archived, and at what sampling rate? Can 10–30 machines plus ≥20 clean tickets each be exported for a pilot?
3. Price, accuracy and retrofit effort of the existing scale platform? What is the maximum extra cost per month customers accept?
4. May a SMART view show customer invoice and contract data, and who owns it under the operator API terms (EU Data Act)?
5. Should an operator scorecard go to customers, or to operators first? What would make operators share tickets?
6. Is the |diff| > 100 kg **and** > 10% lift tolerance acceptable to operators?
7. Poland: installed base, factory (not found publicly), and is BDO reporting a pain point?
8. Service-contract margin and churn. Do leases bundle SMART?
