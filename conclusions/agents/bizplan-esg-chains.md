# Business plan: "SMART Weight Ledger" for multi-site chains (ESG/CSRD-first lens)

Author: bizplan-esg-chains agent, 2026-11-06. Working title only, not a brand.
Tags: **[F]** fact with source · **[D]** computed by me on `data/competition/public` (synthetic data, hypothetical prices, dev labels covering 10 months, annualised ×1.2) · **[E]** estimate · **[A]** assumption. Every euro below is hypothetical, not a real saving.

## 1. Problem and customer

**Buyer.** The head of sustainability, working with group procurement, at a large multi-site chain: grocery, non-food or a shopping-centre owner with 50–1,000 sites. In this group's world, SMART is the "big fries" 15% of customers who want more [F: shared brief]. The day-to-day user is a central environment manager plus store or region managers.

**Pain 1: reporting duty with weak data.**
- The CSRD is now scoped to firms with more than 1,000 employees and more than €450M net turnover [F: Omnibus I, Directive (EU) 2026/470, https://www.mofo.com/resources/insights/251222-eu-sustainability-omnibus-i-detailed-omnibus]. Big chains are exactly the companies left in scope.
- Revised ESRS E5-5 §16 asks for:
  - a description of waste streams;
  - the **total weight of waste generated**;
  - the % diverted from disposal (preparation for reuse, recycling, other recovery);
  - the % directed to disposal (incineration, landfill, other);
  - the **share of waste whose final destination is unknown** [F: https://knowledgehub.efrag.org/eng/interactive/simplified-esrs/esrs-e5/delegated-act].
- CSRD statements need limited assurance [F: CSRD 2022/2464, not re-read today].
- Today the tonnes come from whoever owns the truck, and "the waste operator alone holds the weight" [F: Tommi, shared brief].

**Pain 2: public targets they must hit store by store.**
- Kesko: recycling rate 67% (2024), 66% (2025), target 73% by 2030; 81% in stores under its central waste agreement; the page does not say how tonnes are measured [F: https://www.kesko.fi/en/sustainability/climate-and-nature/circular-economy/].
- Schwarz Group targets a 95% internal recycling rate by 2030 [F: https://gruppe.schwarz/en/press/archive/2025/the-companies-of-schwarz-group-set-an-ambitious-95-percent-recycling-target].
- Finnish businesses must separately collect their waste fractions under Waste Decree 978/2021 §21 [F: https://rinkiin.fi/en/producer-responsibility/companies-waste-management/ (secondary source); thresholds not verified].
- PPWR (EU) 2025/40 has applied since 12 Aug 2026; transport-packaging reuse targets start 2030, cardboard boxes exempt [F: https://www.coolset.com/academy/ppwr-what-companies-must-have-in-place-from-august-12-2026]. Back-of-store cardboard and film flows will be scrutinised [E].

**In the dataset (retail = grocery + non-food + shopping centre)** [D]:
- Scale: 26 customers, 95 sites, 281 devices (about 3 per site); the largest chain has 20 sites and 60 devices.
- Volume and cost: 28.8 kt/yr and **€2.84M/yr** total customer cost, which is **€29.9k per site-year**.
- Mixed waste costs €181/t vs cardboard €24/t, net of credit.
- Mass-based recycling proxy: 72% (everything except mixed waste). This is close to Tommi's "~70%".
- Grades: 14.2% of graded retail lifts are grade C or R (710 of 4,993).
- Missing weights: **21% of completed lifts have no weighbridge ticket** (OP-D 0%, OP-C 50.5% coverage). These tonnes are invisible or defaulted in today's reporting.

## 2. Value proposition

> "One independent, per-site, per-stream tonnage ledger, measured at the source, with uncertainty, reconciled against operator tickets. It is audit-ready for ESRS E5, works across all your operators, and turns into contamination, invoice and contract actions that you approve."

Quantified benefit per **site-year**, with all prices hypothetical [D/E]:

| Value lever | Derivation | Identified | Realisable [A] | Realised |
|---|---|---|---|---|
| Commercial best set (dispute, data request, renegotiate, tender) | Team figure: €1,064 per €13.5k contract-year = 7.9% [D] × €29.9k | €2,360 | 25% (tariff-driven, slow) | €590 |
| Quality / contamination | Retail credit lost vs grade A plus penalties (C: 1,992 t × (50.18−30.80) €/t + €50.4k penalties; R: 262 t × (50.18 + 137.5) €/t; B: €7.6k) = €146k per 10 months = €175k/yr ÷ 95 sites [D] | €1,840 | 30% (site coaching) | €550 |
| Diversion of cardboard out of mixed waste | 3% of 8,021 t mixed [A] × (181 − 24) €/t ÷ 95 sites | €400 | 70% | €280 |
| Reporting labour plus assurance readiness | 0.3 FTE × €70k per 100 sites [A] | €210 | 100% | €210 |
| **Total** | | **€4,810** | | **≈ €1,630 per site-year, ≈ €545 per device-year** |

Unpriced, but what the buyer signs for: a smaller "unknown destination" share (E5 §16(e)), a defensible recycling rate per site, and a neutral evidence trail. Diversion alone adds about 0.8 pp of recycling rate [D/E].

**Accuracy honesty.**
- The zero-BOM virtual scale targets about ±7% (1σ) per lift and ±4–5% on monthly totals [E, weighing-engineer, untested]. That is enough for E5 totals; random error averages out, gain bias needs anchors.
- It cannot verify invoices per lift (at σ = 10% only 16% of +10% overbilling is caught [D, red-team]), so invoice assurance runs at contract-month level using tickets.

## 3. Product and tiers (mapped to SMART)

| | SMART Intro (existing, free add) | **SMART Insights + Weight Ledger** (core paid) | **SMART Integrated, Group ESG** (enterprise) |
|---|---|---|---|
| Weight source | Part 1 T0 virtual scale (pressure + fill), €0 BOM, labelled "estimated" | T0 + ticket anchors (each clean weighed-tare ticket calibrates), drift/fault alarms | + **load-cell platform** (Europress "Scale platform") on 2–5% "golden" sites/DCs: BOM ~€1.0–1.9k, lease €14–26/mo [E, weighing-engineer] |
| Output | Monthly kg per stream per device | Per-site/stream tonnes ± interval; ticket reconciliation; contamination density alerts; grade trend; group invoice-assurance (contract-month) | ESRS E5 data pack: streams, total weight, diverted/disposal split via operator-declared treatment routes, unknown-destination %, methodology note + uncertainty; hash-chained "lift passport" audit trail; API to the chain's ESG/ERP tool |
| Actions (human approval) | none | Coaching tickets to store managers, DISPUTE / REQUEST_WEIGHBRIDGE_DATA drafts | Renegotiation brief, operator data-handshake, multi-operator scorecard (operator-first disclosure) |
| Price [A] | €0 | **€25 / device-month** (≈€900/site-yr) | €25 + €750/customer-month platform fee; hardware lease separate |

The free Intro layer shows a chain it is "missing 21% of its tonnes" and so sells the paid tiers [D/E].

## 4. Pricing and sensitivity

The purchase condition is that realisable value is at least 2× the fee [A: aligned with the Task D template]. Value is €545 per device-year [D/E].

| €/device-month | Fee per device-year | Value multiple | Verdict |
|---|---|---|---|
| 15 | €180 | 3.0× | Easy sell; leaves money on the table |
| **25** | **€300** | **1.8×** | Base. Passes 2× once reporting and assurance value is weighted up for chains [E] |
| 40 | €480 | 1.1× | Only sites with high contamination or few tickets |

- **Value sensitivity.** If realisation halves (€815 per site-year), €15 becomes the ceiling. If the quality lever reaches 50%, €40 becomes viable.
- **Outcome alternative.** A €10 per device-month floor plus 20% of verified, approved savings. This aligns incentives, but savings are slow and disputed [E].

## 5. Revenue model

1. Recurring SaaS add-on to the SMART service contract. This is Europress's "real profit" line [F: brief], and the fee is invoiced inside the existing 6-year lease and service relationship.
2. Hardware lease for golden sites.
3. An onboarding fee per chain (€5k) [A].

Europress never bills transport or waste and never trades material.

## 6. Three-year illustrative numbers (Nordics first, Poland in the high case) [A]

Cost to serve [A]: €5 per device-month for cloud and support, €1,500 onboarding per chain, and one customer-success FTE (€70k) per 2,000 devices. Golden-site hardware is 3% of devices × €2.5k sale price (€1.5k BOM).

| | Low | Base | High |
|---|---|---|---|
| Chains (Y1/Y2/Y3) | 1/2/3 | 1/3/6 | 2/6/12 (Y3 incl. 3 PL) |
| Devices on Ledger (Y3) | 600 | 2,500 | 6,000 |
| Y3 subscription ARR @ €25 | €180k | €750k | €1.8M |
| Y3 platform fees | €27k | €54k | €108k |
| Y3 hardware (golden) | €15k | €38k | €90k |
| Y3 gross margin (subscription) | ~70% | ~78% | ~80% |
| Cumulative 3-yr revenue | ~€0.3M | ~€1.2M | ~€3.0M |

Base Y3 ≈ 1% of Europress revenue (~€70M [F: brief]); the strategic value is lease-renewal retention and an earlier data position [E].

## 7. Go-to-market and pilot

- **Beach-head.** Finnish multi-site grocery and non-food chains that are already SMART customers and are named in public reporting. Do not name them in the demo.
- **Pilot (12 weeks, one chain, 30 sites, ~90 devices)** [A]: wk 0–2 ingest contracts, invoices and tickets and show the "unmeasured tonnes" baseline; wk 2–6 ticket-anchored ledger live, load-cell platforms on 3 sites as ground truth (= weighing-engineer Phase 1); wk 6–12 coach the top-10 contamination sites and give the chain's auditor an E5 pack for a dry run.
- **Pre-registered success:** ≥95% of site-stream tonnes measured or reconciled; monthly bias ≤5% vs weighed-tare tickets; C/R share −2 pp at coached sites; auditor accepts the methodology note; signature at ≥€20 per device-month.
- **Channel.** Key-account managers sell it at service-contract renewal; consultancies and auditors refer.

## 8. Partnerships (operator-neutral)

- **All waste operators, equally:** give-to-get ticket API (auto-reconciled invoices, fewer disputes); scorecards shown to the operator first; "independent second reading", never "operator is wrong" (many gaps are stored tare or side waste [D: red-team]).
- **Rinki / producer-responsibility organisations** (an existing Europress customer [F: brief]): feed measured cardboard and film volumes from stores. Whether this counts toward EPR reporting is unverified [A].
- **ESG reporting platforms and auditors:** an export format and a methodology review.

## 9. Risks

| Risk | Mitigation |
|---|---|
| Virtual-scale accuracy unproven; no pressure data in the dataset | Phase-0 falsification test; golden cohort; intervals on every number; never "validated" |
| Device weight ≠ legal-for-trade (NAWI 2014/31/EU) | Verification and reporting only, never the billing basis |
| ESRS needs a treatment route, which the device cannot see | Use the operator-declared route; report the "unknown destination" share explicitly |
| Operators refuse to share data or feel attacked | Neutral wording, operator-first disclosure, give-to-get |
| Synthetic economics | All € hypothetical; the pilot re-measures real value |

## 10. KPIs

- **Product:** % of site-stream tonnes measured or reconciled; unknown-destination share; monthly bias vs weighed-tare tickets; drift alarms.
- **Customer:** recycling rate per site; C/R grade share; mixed-waste kg per site; approved actions and € realised.
- **Commercial:** devices on Ledger; ARR; net revenue retention ≥110%; pilot conversion; lease renewal of Ledger customers vs others.

## 11. Pitch (one paragraph)

Every big chain must now publish how many tonnes of waste each of its hundreds of stores generates and how much of it is recycled. Today that number comes from the truck owner's weighbridge, and in our data more than one lift in five has no ticket at all. Europress's compactors already feel every stroke. SMART Weight Ledger turns that into an independent, per-site, per-stream tonnage record with honest error bars. Reconciled against operator tickets, exported ready for ESRS E5, it also shows store managers where cardboard leaks into mixed waste and gives group finance a monthly second opinion on invoices. No new sensor is needed on 97% of machines, and a load-cell platform is fitted only where ground truth is needed. Customers pay about €25 per device per month, against roughly €545 of identified, realisable value per device-year on hypothetical prices. Every action waits for a human's approval.

## 3 strongest ideas in this plan
1. **ESRS E5 §16 "unknown destination" share + "21% of lifts without a ticket"**: a regulator-shaped, quantified reason to buy that blames no operator.
2. **Tier ladder respects "cheapest wins"**: €0-BOM Intro, ticket-calibrated Insights, load cells only on 2–5% golden sites; accuracy matched to use (E5 totals tolerate ±7%; invoice checks at contract-month level).
3. **Per-site value stack from traceable dataset rows** (quality loss, diversion, team €1,064 best set), price set against a value-multiple condition with sensitivity.

## 3 weakest points
1. **Reporting/assurance value (€210/site) is assumed**; auditor acceptance of device tonnes is untested, and E5 treatment routes are invisible to the device.
2. **€25 base fails the strict 2× condition (1.8×)**; it leans on unevidenced ESG willingness to pay, and all € are hypothetical.
3. **Market sizing is guesswork**: installed base per chain, SMART ARPU and cost to serve are unknown; Omnibus narrowed CSRD scope.
