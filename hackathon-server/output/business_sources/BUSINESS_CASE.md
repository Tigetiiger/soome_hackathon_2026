# SMART Verified Weight: customer value and business case

Europress × Since AI Hackathon 2026 · submission item 3

**The case in one paragraph.** Europress should sell weight as verification add-ons inside the SMART tiers it already has, not as a new business:
- a free kg estimate on SMART Intro;
- Verified Weight at €12–15 per device per month on Insights;
- Proof of Fullness on gain-share in fixed-schedule markets such as Poland.

The main return for Europress is more customers on SMART and stickier service contracts, which is where it makes its profit [T].

**Evidence tags:**
- [T] said by Europress at the kick-off
- [F] public fact
- [D] computed on the synthetic hackathon dataset, with hypothetical prices (not real savings)
- [E] our estimate
- [A] our assumption

We assume the Part 1 weighing concept works as specified: a kg estimate per lift with a stated band, about ±5–6% on monthly totals.

---

## 1. Use case: a neutral second opinion on the weight

**The problem.** Today only the waste operator knows the weight, from its weighbridge ticket, and weight drives the customer's charges and material credits [T]. Customers distrust invoices they cannot check. "Who owns the data is the holy grail" [T].

**What the data shows:**
- 21% of retail lifts have no weighbridge ticket, and one operator shares none of its tickets [D].
- 77% of large gaps between device weight and ticket weight come from the weighbridge side: side waste, an outdated stored vehicle tare, or combined loads. Only 3.9% are sensor faults [D].
- So the gaps have explainable causes. They are not proof of bad intent.

**The service.** SMART weighs every lift at the compactor, then for each lift:
1. Compares three figures: the device weight (with its band), the operator's ticket, and the invoiced tonnage.
2. Explains any gap by cause, in neutral terms (sensor drift, stored tare, side waste, combined load, billing error).
3. Drafts a recommended action with the evidence rows attached: dispute an invoice line, request ticket data, renegotiate a contract, or change a fixed schedule.
4. Waits for a person to approve it: SMART Center staff or the customer. Nothing is sent automatically, and every action can be reversed.
5. Sends findings about an operator's own vehicles to that operator first.

**Proof of Fullness** applies the same evidence to fixed schedules. It shows which scheduled pickups collected a container that was not yet full. SMART already gets on-call containers as full as possible [T], so this targets fixed-schedule sites. Those are most sites in Poland and Central Europe, and the 30–40% of Finnish sites not on call [T].

**Who buys:**
- Retail and logistics chains that want more SMART features [T].
- Fixed-schedule sites that want to save money [T].
- Operators, who get a free weighbridge hygiene report if they share tickets.

## 2. Measurable customer benefit

| Benefit | How it is measured | Value in the dataset |
|---|---|---|
| Fewer unnecessary pickups on fixed and hybrid schedules | Lifts collected below a justified fill or mass, per device-year | 30–32% of lifts; 18–20 lifts, about €2.5–2.7k per device-year [D] |
| Verifiable billing | Share of mass-billed euros that have an independent weight to check against | Rises from 77% (tickets only) to 96% (tickets plus device) [D] |
| Billing errors recovered | Disputed invoice lines that are confirmed and credited | About €150 per device-year on average [D] |
| Contract leverage | Value of renegotiate, dispute and request-data actions that need device weight | +€190 per contract-year when device weight is available [D]; 28% of renegotiation value sits on contracts where device weight is the only mass figure [D] |
| Weight known on every lift | Lifts with at least one independent weight | 97% of lifts, against 74% with a ticket today [D] |
| Faster fault detection | Days between a sensor drift starting and it being fixed | The drift alarm fires about 33 days earlier [D] |

**Value is concentrated.**
- Mean contract value is about €1,064 per year, but the median is €0. Half of contracts show no gain [D].
- The top 5 of 20 customers hold 75% of the value [D].

This matches the 80/20 split Europress described [T]. So we charge the chains and the fixed-schedule sites, and give everyone else the kg number for free.

## 3. Commercial model for Europress

| Add-on | Price [A] | Customer value it is priced against |
|---|---|---|
| **kg estimate**: monthly kg band per machine | Free. Costs us about €15 per device-year to serve [E] | An acquisition hook that brings the ~85% of customers not on SMART into it [T] |
| **Verified Weight**: per-lift reconciliation, cause attribution, drift alarm | €15 per device per month list, €12 when bundled into a new lease | ~€150 billing recovery plus ~€190 contract leverage, for chains [D] |
| **Proof of Fullness**: evidence and a schedule-change proposal | 25% of the verified avoided-pickup cost in year 1, then moved to an Insights subscription | ~€2.5k per device-year saved: about €625 to Europress, €1.9k kept by the customer [D] |
| **Contract benchmark, action inbox and reporting pack** | +€25 per device per month in Integrated, or a chain licence of €10–40k per year | Procurement and sustainability teams at chains; mandatory BDO waste reporting in Poland [F] |
| **Measured tier**: Europress's existing scale platform | +€39–49 per month inside the lease [E] | Sites that need verification-grade weight, ±1–2% |

**Pricing rules:**
- The fee is at most one third of the value the customer can realise [A]. The dataset's template accepts a 2× value-to-price ratio, so ours is stricter.
- Gain-share answers the price objection in Poland, where "the cheapest wins" [T].
- All prices live in one parameter file, and the demo shows a sensitivity grid.

**Economics, illustrative [E]:**

| | Low | Base | High |
|---|---|---|---|
| Paying devices, year 3 | ~1,000 | ~3,000 | ~7,000 |
| Add-on revenue per year, year 3 | ~€0.18M | ~€0.6–0.75M | ~€1.8M |
| Recurring gross margin | ~75% | ~79% | ~82% |

**On its own the subscription does not pay back:**
- Its 6-year NPV at 10% is −€0.33M [E].
- Add a 5-point uplift in service-contract renewals and higher SMART attach, worth about €60 per adopter per year [A], and the base NPV becomes +€0.23M, with payback in year 5 [E].

The board message is therefore: **weight makes SMART and the service contract stickier**.

## 4. Productisation inside SMART

| SMART tier or contract | What weight adds |
|---|---|
| **Intro** | Free monthly kg band per machine. This replaces today's waste volume calculator |
| **Insights** | Verified Weight, Proof of Fullness and the drift alarm. SMART Center reviews the AI-drafted actions |
| **Integrated** | Contract and €/t benchmark, action inbox, reporting pack, and an API export to the customer's ERP or ESG tools |
| **Lease and service contract** | Scale-platform option, plus calibration checks during technician visits that already happen |
| **Operator API** | Operators push tickets and get back a reconciliation receipt and a private tare-hygiene report ("give to get") |

**How it is built:**
- Rules decide. They beat ML on the anomaly benchmark (0.73 vs 0.35 macro-F1) [D].
- AI drafts the explanations and letters, citing the evidence rows.
- A person approves every action.

This means SMART Center can run it as a managed service without hiring a data team.

**Rollout with kill criteria:**

| Phase | When | What | Continue only if |
|---|---|---|---|
| 0. Pilot | Q1–Q2 2027 | 50 machines at 1–2 Finnish chain customers, plus 10 with scale platforms as ground truth, plus 1 operator sharing tickets | Monthly weight error ≤ 6%; the customer says they would pay at least €12 |
| 1. Finland launch | H2 2027 | Free kg on all SMART devices; Verified Weight in Insights | At least 10% of Insights devices adopt; no operator escalations |
| 2. Poland and Benelux | 2028 | Proof of Fullness on gain-share; BDO reporting | At least 30% of pilot sites move from fixed to on-call; gain-share revenue covers cost to serve |
| 3. Platform | 2029+ | Operator data feed at scale; anonymised material-flow index | EU Data Act consent in every contract; competition-law review passed |

Starting cost is about 2–3 FTE for 6 months plus €10–19k for the scale-platform pilot machines [E]. The Phase 0 gate caps the downside at about €150k [E].

## 5. Assumptions and what remains unproven

- All euro values come from a synthetic dataset with hypothetical prices. None of them is a real saving.
- We assume the weighing works as specified. Real accuracy needs the pilot.
- Device weight is a second opinion, not a basis for billing. Billing on it would bring in legal metrology rules (NAWI, Directive 2014/31/EU).
- Prices, adoption rates and the renewal uplift are our assumptions. Europress's real tier prices, fleet size and contract churn should replace them.
- Detecting wrong material in a container is not part of this case. Our density test failed on this data (about 1% precision) [D], so it stays on the roadmap and needs pressure-curve data from new firmware.
- Operators are also Europress customers [F]. Their acceptance of operator-first disclosure has not been tested.

Full reasoning and sources are in `BUSINESS_PLAN.md`. The supporting analysis is in `../soome_hackathon_2026/analysis/outputs/`.
