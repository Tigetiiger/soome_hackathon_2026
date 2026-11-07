# Business plan: SMART Weight Exchange, a neutral weight-data layer for the recycling chain
Lens: ecosystem and data platform. Author: bizplan-data-platform agent, 2026-11-06.
Tags: [S] sourced (URL), [D] computed on synthetic `data/competition/public` (not real-world evidence), [E] estimate, [A] assumption. All € are hypothetical.

## 1. Problem and customers
The operator alone holds the weight (ticket and grade), and customers distrust invoices. Ticket coverage of completed lifts: OP-A 96%, B 88%, E 94%, C 51%, **OP-D 0%** [D]. Mills see published recovered-paper prices (Fastmarkets FOEX PIX [S: fastmarkets.com/uploads/2024/04/PIX_Recovered-Paper-Europe_Methodology_Apr2024.pdf]) but no **source-level volume flows**. Europress sits at the source of every lift, runs no trucks and trades no waste, so it competes with no one in the chain.

| Side | Job to be done | Pays? |
|---|---|---|
| **A. Waste producers** (retail, logistics, industry) | Know €/t, verify invoices, ESG evidence | SMART subscription |
| **B. Operators** | Fewer disputes, verified-service credential, vehicle-tare hygiene | Tickets in kind (give-to-get); analytics tier later |
| **C. Recyclers, paper mills** | Feedstock forecast by stream and region | Index licence |
| **D. EPR bodies, municipalities** (e.g. Rinki compiles mandatory packaging statistics [S: rinkiin.fi/en/producer-responsibility/reporting-packaging-data/]) | Collected-volume data from commercial sites | Pilot licence. Rinki reporting covers packaging placed on the market, not collected waste, so fit is a hypothesis [A] |

## 2. Value per side
- **A.** Best-set value about **€1,064 per contract-year on €13.5k** contract cost (7.9%) [D, team figure]. One contract = one device (447/447) [D]. Most value is tariff gaps exposed by €/t normalisation; pure weight disputes total €729 [D]. Base fee €10/device-month = €120/yr, **value multiple 8.9x** [A].
- **B.** Per-vehicle stored-tare bias runs from **-21% to +23%** (red-team §0) [D, may be a simulator artefact]. A tare report fixes operators' own weighbridge errors before they become disputes. Ticket-pushing operators get auto-reconciled lifts. € value to be measured in pilot [E].
- **C.** Weekly tonnes by stream and region plus a 2-6 week forecast. Cardboard devices average **118 t/yr**, biowaste 94 t [D]. Value unquantified [A].
- **D.** Signed lift records as source data for recycling statistics. Value unquantified [A].

## 3. Product and tiers
| SMART tier | Module | Content |
|---|---|---|
| **Intro** | Weight Ledger | Weight ± interval per lift, monthly totals, Data Act export |
| **Insights** | Verified Weight | Device vs ticket vs invoice reconciliation, €/t, human-approved dispute and data-request drafts, signed lift passport |
| **Integrated** | Exchange API | Operator ticket ingest, ERP feed, verified-weight certificates, consent console |
| **Partner products** | Operator Analytics; Material Flow Index | Tare diagnostics and service benchmark (own data plus aggregate only); licensed volume index |

Weighing layer: anchor-calibrated virtual scale **±6.6% 1σ [E]**, zero BOM; load-cell platform (€1.0-1.9k) for verification-grade sites (weighing-engineer §0).

## 4. Pricing and revenue streams
1. **Verified Weight** (Insights uplift): €6/10/14 per device-month, low/base/high [A]. The core revenue.
2. **Exchange API**: free for ticket contributors; Operator Analytics €15-30k per operator-year [A].
3. **Material Flow Index**: €15-40k per licensee-year, volume-only in v1 [A]. Comparable: DAT RateView licenses pooled transaction rates and shows no rate without **≥3 contributors and ≥7 reports** [S: dat.com/blog/post/where-do-dat-freight-rates-come-from].
4. **Certificates and evidence packs**: €150-250 per site-year [A].

## 5. Three-year illustration (€k)
Assumptions [A], Y1/Y2/Y3. Devices: low 300/800/1,500; base 600/2,000/4,000; high 1,000/3,500/7,000. Paying operators: 0/0/2; 0/2/4; 1/4/6. Licensees: 0/0/1; 0/2/5; 0/3/8. Certificate sites: 0/0/50; 0/100/300; 0/300/800.

| €k | Low | Base | High |
|---|---|---|---|
| Subscriptions | 22 / 58 / 108 | 72 / 240 / 480 | 168 / 588 / 1,176 |
| Operator Analytics | 0 / 0 / 30 | 0 / 40 / 80 | 30 / 120 / 180 |
| Index licences | 0 / 0 / 15 | 0 / 50 / 125 | 0 / 120 / 320 |
| Certificates | 0 / 0 / 8 | 0 / 20 / 60 | 0 / 75 / 200 |
| **Total** | **22 / 58 / 161** | **72 / 350 / 745** | **198 / 903 / 1,876** |
| Data share (rows 2-4) | 0 / 0 / 33% | 0 / 31% / 36% | 15% / 35% / 37% |

Cost [A]: 3-5 FTE, €300-500k/yr, plus €50-100k one-off legal opinion. **Base breaks even in Y3; low does not.** The main return is strategic: retention of the 6-year lease and service contract ("the real profit"). Unquantified [E].

## 6. Roadmap and gates
| Phase | Scope | Must be true |
|---|---|---|
| **0. To Q1 2027** | Demo; data-use clause in SMART terms | Customers contractually permit use and aggregation of non-personal data (Data Act Art. 4(13)) |
| **1. 2027** | Verified Weight pilot, 30 machines | Virtual-scale gates A1-A6 pass (≥80% of lifts within ±10%); renewals at ≥€6 |
| **2. 2027-28** | Exchange API, ≥2 operators | Operators gain measurably; pilot ticket coverage ≥90% |
| **3. 2028-29** | Index v1 (volume only), certificates | ≥5 customers and ≥3 operators per cell; external competition opinion; one paying recycler |
| **4. 2029+** | Historical €/t benchmark; Poland | Index runs without complaints |

Feasibility [D]: of 32 region×stream cells, **20 have ≥5 customers (381 of 447 devices, 85%)**, but only **15 have ≥3 operators**.

## 7. Go-to-market
- **Land with producers.** 2-3 retail-chain SMART customers, 10 machines each, 6 months free in exchange for index consent.
- **Operator first.** Each pilot operator sees its tare report before any customer finding. Never lead with tendering.
- **Side C.** One Nordic mill gets a free quarterly flow report; test willingness to pay at month 6.
- **Precedents.** Materiaalitori (Motiva for the Ministry of the Environment) is Finland's neutral waste-material platform [S: interregeurope.eu/good-practices/materiaalitori-material-matketplace]. Fingrid Datahub (live 21 Feb 2022, about 3.8 M metering points) [S: fingrid.fi/en/news/news/2022/information-exchange-in-the-electricity-retail-market-enters-a-new-era--datahub-goes-live-successfully/] was mandated by law. Europress has no mandate [E].
- **Cautions.** Rubicon, a US waste marketplace, ran about 7.7% adjusted gross margin (2022 filing) by reselling hauling [S: sec.gov/Archives/edgar/data/1862068/000182912623001260/rubicontech_424b3.htm], so stay asset-light. Compology's container-camera data was absorbed by broker RoadRunner in Oct 2022 [S: wastedive.com/news/roadrunner-recycling-compology-acquisition-ai-technology/633392/]; sensor data alone was hard to monetise [E].

## 8. Risks, including legal (not legal advice)
| Risk | Sev. | Mitigation |
|---|---|---|
| **Competition law, Art. 101 TFEU.** 2023 Horizontal Guidelines treat pricing, costs and quantities as sensitive, cover indirect exchange via a platform operator (hub-and-spoke), and Chapter 6 has **no safe harbour** [S: nortonrosefulbright.com/en-hk/knowledge/publications/7debe299/the-new-horizontal-guidelines-information-exchange] | High | v1 volumes only. Any €/t is historical (≥3 months lag), non-disaggregable, k≥5, no contributor >25% of a cell [A]. Participants see own data plus final aggregate. Clean team, no forward prices. Opinion before Phase 3 |
| **EU Data Act, applies since 12 Sep 2025** [S: mondaq.com/privacy-protection/1662530/]. Data holder "shall only use any readily available data that is non-personal data on the basis of a contract with the user", must not "derive insights about the economic situation" of the user to its detriment, and may not share non-personal product data with third parties beyond that contract (Art. 4(13)-(14)) [S: eur-lex.europa.eu/eli/reg/2023/2854/oj/eng] | High | Phase-0 contract clauses; opt-in index; contributors get free tiers or revenue share |
| **Exclusivity erodes.** Users can send data to third parties on FRAND terms (Art. 8-9; SMEs pay cost only) [S: technologyquotient.freshfields.com/post/102mlk6/]. Access-by-design for products placed after 12 Sep 2026 [S: traverssmith.com/knowledge/knowledge-container/the-eu-data-act-compliance-countdown-for-connected-products/] | Med | The export API is the Exchange. Moat = calibration plus ticket network, not lock-in |
| Operators refuse tickets (OP-D 0%) [D] | High | Give-to-get; customers can request tickets contractually |
| Virtual scale fails Phase-1 gate | High | Load-cell tier for verification; index uses aggregates where random error averages out [E] |
| Not legal-for-trade | Med | Verification and evidence, never billing |
| Recyclers will not pay | Med | Subscription case stands alone |

## 9. KPIs
Devices on Verified Weight; ticket coverage (≥90%); share of lifts within tolerance; dispute cycle time; contributing operators; cells passing gates (20 to 25 of 32); paying licensees; value/fee ≥5x; lease retention vs non-platform customers.

## 10. Pitch
Whoever owns the weight owns the money. Today that is the operator's weighbridge, and nobody can check it. Europress sits at the source of every lift and competes with no one. SMART Weight Exchange makes each compactor a calibrated, signed weight record. Customers get €/t and a second opinion on every invoice: about €1,064 of hypothetical value per contract-year for €120. Operators who share tickets get disputes auto-resolved and tare errors fixed. Recyclers license an anonymised, lawful material-flow feed. No trucks, no trading, mostly no new hardware: Europress becomes the neutral data layer of the circular economy, built the way the Data Act and competition law require.

## 11. Three strongest ideas
1. **Data Act as product.** The mandatory export and third-party path is the Exchange API, and the Art. 4(13) user contract is the index consent mechanism.
2. **Operator-first give-to-get with tare hygiene as the hook.** Operators become contributors and Europress stays neutral.
3. **Volume-only index with gated cells.** 20 of 32 cells qualify [D]; it is new data nobody publishes and avoids price exchange.

## 12. Three weakest points
1. **Side C and D willingness to pay is unvalidated**; Rinki's duty may not cover collected waste.
2. **Economics lean on the subscription.** Data is ≤37% of revenue even in the high case; the industry-change upside is strategic and unquantified.
3. **Cold start without a mandate.** Nothing forces operators in, and only 15 of 32 cells have ≥3 operators.
