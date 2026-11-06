# Business strategist: commercial model and productisation

Lens: customer/business value (25 %) + commercial productisation (10 %). Written 2026-11-06. Tags: **[fact]** sourced, **[dataset]** synthetic Since AI data via `baselines/business_case.py`, **[estimate]**, **[assumption]**. Reproduce numbers with `business-strategist_model.py` and `business-strategist_params.yaml` (same folder). No prices exist in the dataset, so every price and adoption rate below is our choice.

## 0. Headlines

1. **Sell Verified Weight as a SMART Insights add-on, priced at about 1/3 of the value it unlocks: EUR 15 per device-month (low 10, high 25).** In the synthetic world, realisable value is EUR 576 per device-year (low 242, high 978) [dataset x assumption], so the base price gives a ~3x value multiple.
2. **Hardware is not the barrier, distribution is.** A factory-fitted EUR 150 sensor costs the customer about EUR 3.2/month inside the 6-year lease. A retrofit costing Europress EUR 600 (EUR 750 price) costs the customer EUR 12.4/month and pays back only where realisable value exceeds ~EUR 330 per device-year (48 % of customers).
3. **Honest P&L: weight analytics alone is a small line.** Base case year 3: ~EUR 270k revenue, ~EUR 180k ARR, ~560 devices (range EUR 64k to 934k revenue). It does not carry a team by itself. The case rests on lifting SMART attach (today ~15 % of customers), winning leases and holding the service contract, which is "the real profit" per Tommi. About 30 extra machine lifecycles over 3 years cover the base-case gap [assumption, see 4.4].
4. **Value is concentrated**: the top 5 of 52 synthetic customers hold 54 % of realisable value [dataset]. This matches Tommi's 80/20 and drives a two-track offer: chains pay for Integrated, small sites get Intro free plus outcome pricing.

## 1. Market and competitor scan

| Player | What it sells | Price signal | Weight? |
|---|---|---|---|
| Enevo (Espoo, FI; acquired by REEN 2021) | Fill-level sensors + forecasting; monthly subscription per container incl. sensor, data, web [fact, RPN 2014-06-02, Cision 2021] | Quote only | No |
| Sensoneo (SK) | Ultrasonic sensors + platform | Sensor EUR 209.90 excl. VAT at a reseller [fact, iot-shop.de]; San Francisco Public Works awarded USD 929,900 for 1,095 days on 2026-07-23, sensor count not stated [fact] | No |
| Nordsense (DK) | 3D optical sensors, SaaS subscription | Not public; 1,000 sensors in San Francisco 2019 [aggregator summary] | No |
| Compology (US) | Camera + AI container monitoring, sold via haulers; Wastequip exclusive on new roll-offs | Haulers pay a recurring per-container fee; vendor claims ~USD 50 hauler saving per container-month [vendor claim, Next City snippet] | No |
| BrighterBins/SmartEnds; Smart Recycling; Lancaster CC (UK) | Cheap fill sensors | ~11/bin-month (currency unstated, unverified page); EUR 9/month (directory); GBP 112-130 purchase + GBP 4.50/sensor-month, or lease ~GBP 8 (snippet, PDF unreachable) | No |
| Marathon iSmart / 3rd Eye | Compactor and baler monitoring; iSmart reportedly estimates fullness **from PSI pressure, the same principle as SMART** (dealer article); 3rd Eye adds per-bale weights | Not public | Bales only |
| Harmony Insite, Bramidan BRA-IN, Orwak Connect | OEM monitoring: fullness, faults, subscription; Bramidan claims an 80 % fill guarantee | Not public | No (Harmony FAQ lists none) |
| Lehtovuori Finbin (FI) | Fill level from compaction data | Not public | No |
| Invoice auditors (P3, Cass, WATS) | Audit hauler invoices | Contingent, ~50/50 savings split over 12-60 months (P3) [fact]; vendor blog claims 3-12 % immediate recovery [weak] | Ticket data only |
| On-truck weighing | Operator-owned | Rice Lake 4-cell underbody kit USD 6,800 list [fact] | Yes, but operator-side |

**What nobody offers [estimate; searches not exhaustive]:** customer-side, operator-independent weight at the compactor, tied automatically to the contract and invoice, with a neutral operator scorecard. Sensor vendors sell route savings to haulers; OEMs sell fullness; auditors only see paper. Europress already owns the installed base, the pressure data and a scale product (Scaletipper X1 and "scale solutions" appear on europressgroup.com) [fact]. **IP flag:** US 11,162,834 B2 (BACE LLC, granted 2021-11-02, adjusted expiry 2033) covers retrofit load-cell weighing for waste containers; claims unread, US-only, run a freedom-to-operate check.
Finland: L&T estimates ~20 % of a EUR 1.7bn market and rank 1 (company estimate, Nov 2025 prospectus) [fact, lt.fi]; we treat the largest operator as that profile, not as a named target.

## 2. Who pays and why

| Segment | Wants | Pays for | Evidence |
|---|---|---|---|
| Large retail and property groups (SMART "big fries") | Features, multi-site benchmarks, ESG data, API into ERP | **Integrated**: per-chain licence + per-device fee | 16+ device customers: EUR 676 realisable per device-year, 5.9 % of spend [dataset] |
| Industrial and food/beverage (cardboard, plastics) | Material value, contamination control | Insights; per-tonne or outcome fee | Credit-eligible tonnes 53 per device-year [dataset]; contract review and contamination are 35 % of realisable value |
| Small sites (the ~85 % outside SMART) | Lower cost, no upfront risk | Intro (free ballpark weight) + outcome fee; weight in the lease | 2-5 device customers: EUR 493 per device-year on average, median customer EUR 262 [dataset] |
| Mid-size operators | Fewer disputes, payload planning (not a core buyer) | Reconciliation API | Dataset: combined loads are split equally, a dispute source [dataset docs] |
| Largest operator (owns trucks, paid per transport) | Status quo | Will not pay; likely blocker | Tommi's note |

Realisable value by lever (base shares): operator performance 39 %, contract review 24 %, contamination 11 %, over-servicing 9 %, billing review 9 %, tendering 8 % [dataset]. **Attribution risk:** over-servicing is already SMART's job and most levers need invoices and contracts rather than weight, so the low case (42 % of base value) is the prudent "weight-attributable" reading. **Reality check:** the dataset identifies 22.8 % of spend as recoverable; our base realises 5.0 %, which sits inside the 3-12 % vendor-claimed audit recovery range [weak source].

## 3. Ranked menu of commercial models

Score = pull + speed + fit with Europress's no-trucks role + low operator conflict, each 1-5 [assumption: our judgement].

| # | Model | Score | Price logic (low / base / high) |
|---|---|---|---|
| 1 | **Verified Weight tier**, per device-month (variants: EUR 2 per verified tonne, about EUR 14/month at 84 t per device-year; per site EUR 40-80) | 17 | EUR 10 / 15 / 25 |
| 2 | **"Weight-included" 6-year lease** | 17 | Integrated BOM EUR 300 / 150 / 90, price +30 %: lease uplift EUR 6.5 / 3.2 / 1.9 per month. Retrofit cost EUR 900 / 600 / 400, +25 %: EUR 18.6 / 12.4 / 8.3 per month |
| 3 | **Chain licence: ESG report + API (Integrated)** | 15 | EUR 10k / 20k / 40k per chain-year, on top of device fees |
| 4 | **Outcome fee**: % of verified, documented savings | 14 | 15 / 20 / 25 %; at 20 % that is EUR 9.6 per device-month in the base case (4.0 in the low-value case, 16.3 in the high) |
| 5 | **Operator "weight handshake"** data licence | 11 | EUR 0.3 / 0.6 / 1.0 per verified lift (41 lifts per device-year [dataset]); basic inbound ticket upload free |
| 6 | **Tender-as-a-service** (verified volume packs, EUR/t benchmarks) | 10 | EUR 1.5k / 3k / 5k per tender cluster |
| 7 | **Materials marketplace** for weighed bales (cardboard, plastics) | 10 | Commission EUR 2 / 4 / 6 per tonne; Cirplus-type commission models exist, rates unpublished [fact] |
| 8 | **Tonne-based full service**, Europress in the middle | 6 | Margin 1.5 / 3 / 5 % of spend, about EUR 29 per device-month at 3 % [dataset] |

| # | Customer benefit | Required capability | Operator conflict and neutrality | Legal and trust |
|---|---|---|---|---|
| 1 | Euro-denominated, human-approved actions each month | Calibrated weight, invoice parser, rules + ML | Medium. Show tolerance bands and causes (drift, side waste, stale tare, combined load); never rank on raw gaps | Verification-grade only; contract data is the customer's, confidentiality clause with the operator must allow sharing |
| 2 | No upfront cost; weight arrives with the machine | Factory option, lease product, install at planned service visits | Low | Hardware warranty; no trade claims |
| 3 | Reporting without manual work | Audit trail, exports, SSO, API | Low | Assurance needs documented method; CSRD pull is narrow (section 6) |
| 4 | No upfront risk | Evidence ledger per saving, counterfactual rules | Medium-high: success fee tied to disputes. Cap, disclose, and take no fee from operators | Define "verified" in contract; reversal path |
| 5 | Fewer disputes, payload planning | Two-sided evidence pack, right of reply | Operator carrot; keep customer data customer-controlled | Data Act contract basis (section 6) |
| 6 | Better tariffs | Anonymised benchmark, pooling | High; keep fixed fee, no success fee from winners | Benchmarks need customer consent; no competitive insight leakage |
| 7 | Better credit per tonne | Buyer network, grading | Medium; logistics stay with operators | Weighed lots need independent check |
| 8 | One price per tonne | Balance sheet, operator contracts | Very high; contradicts "no waste business" | Counterparty and billing-grade metrology |

## 4. Product tiering, retrofit versus new-build, payback

**4.1 Mapping** [assumption: tier definitions inferred from Tommi and the Kaari case, no public definitions found].

| SMART tier | Weight feature | Price |
|---|---|---|
| Intro | "Ballpark weight" per lift (about +-10 %), no verification claim; collects calibration data and educates | Free or EUR 0-3 |
| Insights | **Verified Weight**: calibrated mass, weight-checked invoices, EUR/t, anomaly and contamination flags, monthly action list with approval | EUR 15 per device-month |
| Integrated | Weight API, ERP and ESG exports, signed weight statements, operator handshake | Per-chain licence + device fee |

Use a few reference scales (Scaletipper, weighbridge tickets) as ground truth to recalibrate the whole fleet; sell billing-grade only at sites that buy a scale.

**4.2 Attach to leases and the installed base.** New machines: weight in the standard option list, uplift inside the lease. Installed base: offer at lease renewal and during planned service or predictive-maintenance visits, which cut retrofit cost from ~EUR 600 standalone toward ~EUR 400 [assumption].

**4.3 Payback per device** (script output; upfront = customer pays hardware cash).

| | Low (EUR 10) | Base (EUR 15) | High (EUR 25) |
|---|---|---|---|
| Realisable value, EUR per device-year | 242 | 576 | 978 |
| Integrated: benefit/cost under lease, payback if paid upfront | 1.2x, 38 months | **2.6x, 5.9 months** | 3.0x, 2.1 months |
| Retrofit: benefit/cost, payback upfront | **0.7x, never in 6 years** | 1.75x, 22.7 months | 2.5x, 8.9 months |

Rule: retrofit pays where realisable value is at least EUR 330 per device-year (25 of 52 customers, 64 % of devices in the base case); integrated at EUR 220 (37 of 52, 83 % of devices) [dataset]. Europress side: onboarding is ~EUR 110 per device (EUR 600 per 8.6-device customer plus EUR 40); contribution is EUR 10.2 per device-month (68 %) after EUR 2.5 operations and EUR 2.3 support. Integrated payback is 6.4 months including a EUR 45 hardware margin; retrofit covers onboarding on day one.

**4.4 Break-even adoption.** Fixed team cost EUR 135k per year (1.5 FTE at EUR 90k loaded) [assumption] needs 1,106 paying devices at EUR 15, which is 33 % of the year-3 SMART base (low scenario: 123 %; high scenario at EUR 25: 9 %). Base case reaches 563. The base-case 3-year direct contribution is EUR 227k against EUR 405k of team cost, a EUR 178k gap, or about 30 extra machine lifecycles at EUR 6k gross profit each [assumption, ask Tommi] (about 1 % of an assumed ~3,300 machines sold in 3 years).

## 5. Three-year Europress revenue scenarios (EUR thousand)

Inputs [assumption unless marked]: paid SMART devices today 1,500 / 2,400 / 4,000 (assumed ~12k installed devices x 12-33 %, unverified; **biggest unknown**), new SMART machines 150 / 300 / 600 per year, eligible share 19 / 35 / 37 % [dataset], adoption of eligible by year 3: 20 / 35 / 50 %, factory take-rate 15 / 30 / 50 %, chains cumulative 2 / 4 / 9 by year 3. Hardware revenue is gross; contribution counts margin only.

| | Y1 low | Y1 base | Y1 high | Y2 low | Y2 base | Y2 high | Y3 low | **Y3 base** | Y3 high |
|---|---|---|---|---|---|---|---|---|---|
| Weight devices (end) | 36 | 157 | 477 | 78 | 348 | 1,043 | 123 | **563** | 1,638 |
| SaaS | 2 | 14 | 72 | 7 | 45 | 228 | 12 | **82** | 402 |
| Hardware revenue | 23 | 64 | 117 | 29 | 87 | 158 | 32 | **105** | 171 |
| Chain licences | 0 | 20 | 80 | 10 | 40 | 200 | 20 | **80** | 360 |
| **Revenue** | 26 | 98 | 268 | 46 | 173 | 586 | 64 | **267** | 934 |
| Contribution (after serving, onboarding) | 2 | 26 | 111 | 15 | 68 | 359 | 27 | **134** | 663 |
| ARR at year end | 4 | 48 | 223 | 19 | 103 | 513 | 35 | **181** | 851 |

**Confidence: low.** Revenue scales linearly with the paid-SMART base, the 3x value test, and adoption, none of which is observed. The high case is about 1.3 % of Europress's ~EUR 70M revenue. Options 5-8 are excluded from these numbers.

## 6. Strategic risks and regulatory hooks

| Risk | Mitigation |
|---|---|
| **Operator pushback**: fuller containers cut transports; an unwanted referee | Two-sided evidence pack, right of reply, no success fees from operators, handshake benefits (payload planning, fewer disputes), publish methodology |
| **Data ownership** | Customer owns device and contract data; Europress processes under contract; cross-customer benchmarks only anonymised and consented |
| **Accuracy disputes** (+-3.3 % typical, faults larger [dataset]) | Advice only, tolerance clause (e.g. +-5-10 %), calibration log, weighbridge stays billing reference |
| **Value is not all weight** | Price on the weight-attributable share; report low case |
| **Concentration**: 54 % of value in 5 customers | Chain track plus bundled small-site track |
| **Dataset flatters value** (injected errors) | Realise 5 % not 22.8 % of spend |
| **Poland** | Fixed schedules and different price levels; untested, no data |

**Sourced hooks (secondary sources unless stated):**
- **EU Data Act, Reg. 2023/2854**, applicable since 2025-09-12. EUR-Lex recitals: the manufacturer's use of non-personal data needs a **contract with the user** (rec. 25); data holders must not derive insights that undermine the user's commercial position (rec. 27); users may share data with third parties, who may not build a competing connected product (rec. 39). This legitimises customer-controlled weight data and sets rules for our "what we do with the data" list. Check Article text with counsel.
- **CSRD, Omnibus I, Directive (EU) 2026/470** (published 2026-02-26, in force 2026-03-18, per PwC and other secondary summaries): scope is now above 1,000 employees and above EUR 450M turnover, with a value-chain cap for smaller suppliers. ESG reporting demand therefore sits with the largest chains only. Final waste data points in the simplified ESRS not verified.
- **PPWR, Reg. (EU) 2025/40**: applies mostly from 2026-08-12, EPR registration and reporting; Finnish producer organisations carry reporting (Tamro note). **We found no rule that requires weighing waste at the compactor** and WFD Art. 35 record-keeping is mandatory only for hazardous waste (Member States may extend). The pull is money, not compliance.
- **Legal metrology**: trade use of weighing instruments falls under the NAWI Directive 2014/31/EU (EN 45501, OIML R76). Finnish applicability to compactor-integrated devices not verified. Stay verification-grade; GDPR is not the issue, contract confidentiality is.

## 7. Value proposition, pitch, data uses

**Value proposition.** Europress SMART Verified Weight puts an independent witness inside the machine. It gives every customer a ballpark-accurate weight for each lift at near-zero hardware cost, checks it against contracts and invoices, and returns a short monthly list of euro-valued actions (invoice lines to question, contracts to renegotiate, contamination to fix, tenders worth running) that a person approves. Customers stop paying per tonne for weights they cannot see; operators get fewer disputes and a neutral reference; Europress becomes the trusted measurement layer without touching a truck.

**60-second hook.** "Every month a retailer gets an invoice per tonne, weighed on a scale it cannot see, graded by the party paid per tonne. Our compactors already know how full they are; now they also know how heavy. In our synthetic test of 52 customers, about 5 % of spend, EUR 258k a year, was realisable [simulated, hypothetical prices]. We don't pick up your waste or take sides: the machine keeps the receipt, an AI drafts the dispute, and you press approve."

**What we would do with the data** (Tommi's question):
1. Weight-checked invoice review and dispute packs (C2 actions, human approval).
2. EUR/t and material-value transparency per device, site, customer.
3. Anomaly and contamination detection from kg-per-fill density drift.
4. Fleet self-calibration: every weighbridge ticket recalibrates similar devices.
5. Neutral operator scorecard with explained causes.
6. Tender packs and anonymised EUR/t benchmarks (consented).
7. Weighed-bale lots for a materials marketplace.
8. ESG and EPR exports with an audit trail.
9. Predictive maintenance: load history and overload events against wear and warranty.
10. Product design: bulk density by material informs machine sizing. Anonymised regional volumes could later be licensed to operators for capacity planning.
Never: sell raw customer or contract data, or publish operator rankings without causes.

## 8. Open questions and licences

- **Ask Tommi:** number of devices on paid SMART tiers, SMART ARPU and churn; gross profit per machine over a 6-year lease plus service; whether Scaletipper X1 pricing conflicts with this tier; whether operators influence equipment purchase.
- **Third parties used:** pandas, numpy (BSD-3), PyYAML (MIT), Since AI dataset v1.0.1 (synthetic; no licence text found in the files we read, confirm with organisers). Prices are not Europress prices.
- **Untested:** willingness to pay, any operator acceptance, retrofit install cost, Finnish metrology rules, US patent scope.

## Sources (accessed 2026-11-06)

Enevo: recyclingproductnews.com/article/18538 ; news.cision.com/abax/r/the-abax-venture-company-reen-acquires-enevo-group,c3363064 · Sensoneo: iot-shop.de/en/shop/snn-ss3-sensoneo-smart-waste-single-sensor-v3-0-4787 ; sfpublicworks.org Resolution 2026-0059 (read) · Nordsense: dealroom.co/companies/nordsense · Compology: nextcity.org/urbanist-news/dumpsters-sensors-efficient-trash-pickup (search excerpt; fetch 403) · Sensor prices: smartends-os1.vercel.app/pricing ; committeeadmin.lancaster.gov.uk/documents/s87029/ICMD18%20REPORT.pdf (excerpt; fetch failed) · OEMs: marathonequipment.com/ismart ; 3rdeyecam.com/industry/retail-box-stores ; harmony1.com/insite-equipment-monitoring-faqs/ ; bramidan.com/bra-in-monitoring-system/ ; global-recycling.info/?p=5200 · Auditors: costanalysts.com/waste-management-auditing ; cassinfo.com/waste-expense-management · Truck scales: ricelake.com/products/rigid-underbody-load-cell-kits · Patent: patents.google.com/patent/US11162834 · Market: lt.fi/en/investors/lt-as-an-investment/market-position · Europress: epsmart.fi ; europressgroup.com ; recyclinginside.com/customer-case-finnish-shopping-mall-now-manages-waste-the-smart-way/ · Law: eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R2854 ; mofo.com/resources/insights/251222-top-10-questions-about-the-eu-data-act ; pwc.lu/en/sustainability/sustainable-finance/eu-finalises-agreement-on-omnibus.html ; williamfry.com Omnibus-1 PDF (Mar 2026) ; tamro.fi PPWR news ; legislation.gov.uk/eudr/2008/98/article/35 ; oiml.org r076-1-e06.pdf · Marketplace: newsletter.mcj.vc/p/our-investment-in-cirplus
