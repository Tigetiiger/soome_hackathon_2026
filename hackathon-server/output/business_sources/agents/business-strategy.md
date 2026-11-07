# Business strategy backbone: "Verified Weight" inside SMART

Author: business-strategy agent, 2026-11-06. Tags: **[fact/URL]** sourced (web access 2026-11-06), **[data]** computed on the synthetic dataset (hypothetical prices), **[estimate]** my judgement, **[assumption]** a parameter to confirm with Tommi. Every price in this document is a hypothesis. None is a Europress price. Calculation script: `/tmp/claude-1001/-home-hackathon/a8a54bb4-1721-4b20-9e32-771541f26109/scratchpad/pl.py`.

## 0. Recommendation in one paragraph

Sell **Verified Weight** as an add-on to SMART that gives the customer an independent second opinion on every lift: device kg vs ticket kg vs invoice kg, with an uncertainty band, a neutral cause label, and human-approved actions. It is not a billing basis. Price it at about **€12/device/month in Insights** and **€25/device/month in Integrated** (ESG/BDO evidence pack, operator data API, audit trail). Offer the load-cell **Scale platform** as a premium lease line at about **€39/device/month**. Intro customers get a free monthly ballpark €/t figure as the upsell hook. Bundle the fee into new 6-year leases. Offer gain-share only to large chains. The standalone P&L reaches run-rate break-even at about **3,100 active devices** [estimate]. The real prize is strategic: more SMART attach (today about 15% [fact: Tommi]) and stickier service contracts, plus becoming the industry's neutral weight-data layer.

## 1. Market and competitor research

### 1.1 Competitors and adjacent players

| Player | What it measures | Business model / price (public) | Independent at-source weight? |
|---|---|---|---|
| Compology (RoadRunner since 2022) | In-container camera: fullness, contamination | Sensor purchase plus subscription per container per month. Price not public. [fact: nextcity.org/urbanist-news/dumpsters-sensors-efficient-trash-pickup] | **No.** RoadRunner "tracks waste and recycling by volume" [fact: roadrunnerwm.com/technology/waste-metering] |
| Sensoneo, Enevo, Nordsense, Waste Vision | Ultrasonic/radar fill-level | Subscription per container; prices quote-only [fact: sensoneo.com/faq; recyclingproductnews.com/article/18538; dealroom.co/companies/nordsense] | No |
| Greyparrot (UK) | AI cameras on MRF sorting belts | Hardware plus analytics to operators. Deepnest data product for brands. $27M Series B Jul 2026. UK EA accepted its AI composition data for statutory reporting in Q1 2026 [fact: wastedive.com/news/greyparrot-27m-funding-round-scales-ai-recycling-analytics/826339] | No, but it proves that **waste data can be sold to third parties and accepted by regulators** |
| Bramidan BRA-IN (Orwak/Presona group) | Fill, bales ready, errors. BRA-IN Link works on third-party compactors | Claims up to 25% fewer collections [fact: bramidan.com/bra-in] | No weight found |
| Waste Harmonics iWaste | Fullness plus "audit of invoices", hauler accountability | Managed service [fact: wasteharmonics.com/technology/iwaste-for-dumpsters] | Invoice audit, but **no weight**: it uses timestamps and fullness |
| Generic US compactor monitors | Ultrasonic or pressure fullness | **$25–60 per unit per month**, or $600 licence + $900/yr [fact: consultant pages in search results, low quality; treat as indicative] | No. One page notes they suit customers billed per pull, not per weight |
| On-truck weighing (Hyva Titan, RDS body weighing, Rice Lake) | Truck or body load cells | Hardware on the **operator's** vehicle. ≤1% claimed [fact: weighing-engineer.md; rds.eu/en/product/calibrated-body-weighing-system] | Weight yes, independent **no** (the operator owns it) |
| BACE IntelliBACE (US) | Patent US11162834 "Weight-measurement retrofitting for waste compactors" [fact: patents.google.com/patent/US11162834] | Equipment OEM | Closest prior art: an **OEM-side weight** product. Freedom to operate is not analysed |

**Finding** [estimate, based on the searches above]: every fill-level vendor sells volume. Every weight source sits with the operator, either at the weighbridge or on the truck. I found no vendor that offers customer-side, operator-neutral, per-lift weight verification as a service in the Nordics. Europress already has the hardware pieces (Scale platform, Scaletipper X1, waste volume calculator [fact: europressgroup.com/scale-solutions]) and the SMART channel. Its gap is a verification product, not a sensor.

### 1.2 Europress public figures

- Europress Group Oy (business ID 0889611-2) reported revenue of **€35.6M in 2024** (2023: €39.2M) and net profit of €0.57M [fact: scoris.eu/company/FI/0889611-2]. Tommi's "~€70M" is probably group-level, with sister companies in SE/NO/PL [assumption: ask Tommi which figure to use].
- SMART claims are vendor-reported averages: -40% total waste cost, -40% CO₂, -37% emptyings, +58% fill rate, -50% maintenance visits [fact: epsmart.fi]. The public site does not show the tier names or prices.
- The Scale platform has one weighing sensor per corner and sends monthly user reports by email. No accuracy figure or price is published [fact: europressgroup.com/scale-solutions].

### 1.3 Regulatory tailwinds (what weight data must be reported)

| Rule | What it demands | Relevance |
|---|---|---|
| CSRD / ESRS E5-5 | Total waste generated (mass), hazardous/non-hazardous, by treatment, % non-recycled [fact: knowledgehub.efrag.org ESRS E5]; Omnibus narrowed scope to ~>1,000 employees and >€450M turnover (sources conflict) [fact: evotix.com/resources/blog/understanding-the-csrd-reporting-timeline] | Big chains stay in scope; small shops drop out [estimate] |
| WFD revision, Dir. (EU) 2025/1892 | Binding −30% per-capita food waste in retail/restaurants/households, −10% processing, by 2030; transpose by 17 Jun 2027 [fact: circulareconomy.europa.eu/platform/fr/node/9265] | Grocery biowaste needs a kg baseline and trend |
| PPWR, Reg. (EU) 2025/40 | Applies 12 Aug 2026; 40% reusable transport packaging by 2030; cardboard excluded from reuse targets [fact: slrconsulting.com/insights/eu-packaging-and-packaging-waste-regulation] | Cardboard stays the core compactor stream |
| Finnish Waste Act 646/2011 (am. 714/2021) | Business separate-collection duty from 1 Jul 2022 [fact: valtioneuvosto.fi/-/1410903]; electronic transfer documents kept 3 yrs for some streams | Proof of separate collection; holder record-keeping (§118) not verified [assumption] |
| Poland BDO | Registration, records, electronic transfer cards (KPO), annual report by 15 March; non-filing is an offence [fact: roedl.pl/en/good-to-know/good-to-know/law-and-tax-news/the-bdo-register-all-about-obligations-and-penalties] | Mandatory mass per waste code: a concrete pre-fill/check product [estimate] |
| NAWI 2014/31/EU / MID | Trade weighing needs approved instruments [fact: weighing-engineer.md] | Verification, not billing |

### 1.4 Market size indicators

- Global refuse compactor market ~**USD 280M (2024)**, Europe largest region [fact: custommarketinsights.com/press-releases/refuse-compactor-market-size/, low-transparency publisher]; no reliable Nordic/EU installed-base count found.
- Working assumption: **15,000 connected Europress machines** [assumption: ~2,000 units/yr × ~8-yr life; must be confirmed by Tommi]. At 15% on SMART, about 2,250 devices are on a subscription today.
- Dataset proxy: 52 customers, 150 sites, 447 devices, 3.0 devices per site. Grocery retail holds 35% of devices, non-food retail 19%, manufacturing 12% [data].

## 2. Segments and value proposition

| Segment | Job to be done | Value driver | WTP reasoning | Tier |
|---|---|---|---|---|
| **Big retail chains** (S-Group, Kesko-type; in data 35%+19% of devices) | "Prove my waste cost and recycling KPIs across 100+ sites, defend my ESRS E5 and food-waste numbers." | €/t per site benchmarked, invoice second opinion, CSRD/WFD evidence pack | Highest. They have a finance and sustainability team. Value is about 8% of waste spend [data] | Integrated |
| **Logistics and industry** (manufacturing 12%, logistics 4%) | "Turn cardboard and film into money and catch contamination before it costs me." | Material credit transparency (only cardboard and plastics earn credits [fact: ECONOMIC_MODEL]), grade C/R alerts | Medium-high. Credits are visible. Fewer sites, larger tonnage | Insights → Integrated |
| **Small shops** (the "small fries", 80% of the count) | "Just make it cheaper." | Ballpark €/t once a month, "you are paying more than peers" nudge | Very low. Tommi: "cheapest wins" | Intro (free hook) |
| **Property managers / shopping centres** (9% of devices) | "Allocate waste cost fairly to tenants." | Weight per tenant (already built: RFID + Scaletipper [fact: europressgroup.com/scale-solutions]) | Medium. It is a recharge, so the cost passes to tenants | Integrated + RFID |
| **Waste operators** | "Fewer disputes, less admin, a better load factor." | Auto-reconciled invoices, tare-hygiene alerts on their vehicles, pre-notified load weight | Not a payer at first. **Give-to-get**: they share tickets and get reconciliation free | Partner API |

## 3. Revenue model options and recommendation

### 3.1 Price derivation from customer value

The team figure is a dev best-set action value of **€1,064 per contract-year on €13.5k annual contract cost (7.9%)**, with 1 contract = 1 device [data, hypothetical prices]. Two caveats. About 99% of it comes from tariff actions (RENEGOTIATE, TENDER) that weight only enables through €/t normalisation, and weight-basis disputes alone are small (€729 over 77 lines) [data: red-team-judge.md §0]. So realisation is well below 100%.

**Rule:** fee ≤ realisable value ÷ 3. The 3× multiple is a purchase-condition assumption, stricter than the 2× in the dataset example [assumption]. In the grid below, the value multiple = €1,064 × realisation ÷ (12 × monthly fee):

| Fee €/device/month | 25% realised | 50% realised | 75% realised |
|---|---|---|---|
| 5 | 4.4× | 8.9× | 13.3× |
| 10 | 2.2× | 4.4× | 6.7× |
| **12 (Insights)** | 1.8× | **3.7×** | 5.5× |
| 15 | 1.5× | 3.0× | 4.4× |
| **25 (Integrated)** | 0.9× | 1.8× | 2.7× |
| 40 | 0.6× | 1.1× | 1.7× |

Reading the grid [estimate]: €12 is safe at about 50% realisation. €25 only clears 3× at more than 80% realisation on transactional value, so Integrated must also earn on **compliance value**: ESRS E5, the WFD baseline, Polish BDO filing, and tenant recharge. That value is not in the dataset. The reference points are US monitoring at $25–60 per unit per month [fact, low-quality sources], which is fullness only. Our €12 sits below that, which fits "cheapest wins".

### 3.2 Options mapped to tiers

| Option | Tier | Price [assumption] | Verdict |
|---|---|---|---|
| Ballpark monthly €/t + "peer gap" teaser | Intro | Free | **Yes**: the funnel into Insights |
| Verified Weight add-on: lift-level second opinion, cause labels, dispute/data-request drafts (human-approved) | Insights | €12/device/month | **Yes: core** |
| ESG/CSRD + WFD food-waste + BDO evidence pack; signed lift passport; operator data API | Integrated | €25/device/month (includes the add-on) | **Yes** |
| Premium Scale platform (4 load cells) | Integrated option | €39/device/month on a 72-month lease. BOM €1.0–1.9k plus install of about €480 means cost of €21–33/month [estimate: weighing-engineer.md] | **Yes**, for the few who need ±1.4%, plus a golden cohort for calibration |
| Bundle into new leases | All new machines | +€12/month baked in, €864 over 6 years [estimate] | **Yes**: the default for new sales, invisible to price-shoppers |
| Gain-share | Large chains only | 20% of documented, approved recoveries (credit notes, renegotiated tariffs), capped at 2× the Integrated fee | Optional. It needs audit-grade attribution and slows sales cycles |
| Operator data exchange (give-to-get) | Partner | Free for ticket-sharing operators. Paid API later | **Yes, as a strategy**. It is not revenue in Years 1–3 |
| Anonymised €/t benchmark index | Year 3+ | Licence to chains and associations | **Later.** Competition law: no current or future price exchange between competitors. Use historical data only (e.g. older than 3 months), aggregated (k ≥ 5 contracts, no operator identifiable), and get legal review (EU Horizontal Guidelines 2023, information exchange) [assumption: legal check required] |
| Billing on device weight / weight-linked lease | No | n/a | Legal metrology and dispute liability. A vision item only |

## 4. Illustrative 3-year P&L for the service

**Assumptions** [all assumption/estimate]:
- Mix: 70% Insights at €12, 27% Integrated at €25, 3% Integrated + platform at €64. Blended ARPU **€17.07/device/month**.
- Cost to serve per device per month: cloud/data €1.00, LLM drafting and summaries €0.20 (about 40 lifts per device per year [data], few exceptions, cached), support €1.50. Platform hardware is €26.8/month on 3% of devices.
- Onboarding €102.5 per new device: €50 setup and anchor calibration, plus a €175 weigh trip on the 30% of devices without tickets.
- Incremental fixed cost (product, data science, customer success on top of the existing SMART platform): €350k / €450k / €500k.
- Recurring gross margin is **~79%**. Contribution is €13.5/device/month.

| Scenario | Year | Devices (end) | ARR end (€k) | Revenue (€k) | GM incl. onboarding | EBIT (€k) | Cumulative (€k) |
|---|---|---|---|---|---|---|---|
| Low | 1 / 2 / 3 | 250 / 700 / 1,500 | 51 / 143 / 307 | 26 / 97 / 225 | -21% / 32% / 43% | -355 / -419 / -404 | -1,179 |
| **Base** | 1 / 2 / 3 | 400 / 1,500 / 3,000 | 82 / 307 / **615** | 41 / 195 / 461 | -21% / 21% / 46% | -359 / -409 / -290 | **-1,058** |
| High | 1 / 2 / 3 | 700 / 2,800 / 6,000 | 143 / 574 / **1,229** | 72 / 358 / 901 | -21% / 19% / 43% | -365 / -382 / -116 | -864 |

- **Break-even:** about **3,100 active devices** at €500k fixed cost (500,000 ÷ (13.48 × 12)). That is about 21% of the assumed fleet, or 1.4× today's SMART base. Base reaches it early in Year 4. High reaches run-rate break-even during Year 3.
- **Honest read** [estimate]: standalone it is small (~1–2% of revenue). The case rests on effects **not in this P&L**: SMART attach above 15%, retention of 6-year leases and service contracts ("the real profit"), and Scale platform pull-through.
- Illustration with hypothetical figures: if Verified Weight saves 100 service contracts per year from churn at €X margin each, the line pays for itself when X ≥ €3–4k [estimate, from €290–400k annual losses ÷ 100].

**KPIs:**
- Commercial: attach rate of Verified Weight on SMART; Intro → Insights conversion; ARPU; gross revenue retention.
- Data: share of lifts with an operator ticket; device-vs-ticket agreement within tolerance (target ≥80% at ±10%, monthly totals ±5%); calibration anchors per device.
- Operations: time-to-resolve disputes; share of flags the operator confirms or fixes (e.g. tare corrections).
- Customer and compliance: realised € per device per year (approved actions); ESG packs delivered.
- Cost: cost to serve per device.

## 5. Go-to-market

### 5.1 Pilot (Phase 0, 6 months, Finland)

- **Who:** 2 large grocery and non-food chains, 1 logistics/industry site, and 1 shopping centre. Use **one operator that agrees to share WEIGHED-tare tickets**, and invite it as co-pilot.
- **Size:** 40–60 devices (about 15–20 sites at 3 per site [data]), of which 4–6 are on the Scale platform as the golden cohort (~€6–11k hardware [estimate]).
- **Success metrics, set in advance:**
  - Monthly device total within ±5% of tickets on ≥80% of device-months.
  - ≥1 neutral root cause confirmed by the operator (e.g. stored tare).
  - Customer-approved actions worth ≥3× the hypothetical fee.
  - Operator NPS not lower than baseline.
  - ≥50% of pilot customers sign a paid conversion intent.

### 5.2 Sequencing

| When | Market | Wedge |
|---|---|---|
| 2027 H1 | **Finland** pilot | On-call SMART fleet, chains, CSRD/WFD |
| 2027 H2 | Finland/Nordic rollout, add Verified Weight to every new lease | Insights upsell |
| 2028 | **Poland** | Fixed schedules mean weight proves over-servicing (lifts at low fill). **BDO/KPO pre-fill** is a must-have compliance product. The Polish factory supports local presence [fact: Tommi] |
| 2029 | Benchmark index, operator API monetisation | Data network effects |

### 5.3 Operator partnership (respecting Tommi's sensitivity)

1. **Operator-first disclosure.** Any discrepancy goes to the operator first, with evidence, and gets a 10-working-day window before it appears on the customer dashboard as "under review" [assumption on window].
2. **Neutral cause taxonomy:** sensor drift, stored tare, side waste, combined load, moisture. The vehicle stored-tare finding gives operators a fix, not an accusation [data: red-team-judge.md].
3. **Give-to-get.** Operators that share tickets via API get free auto-reconciliation, fewer disputes and pre-notified load weights for routing.
4. **No tender or switching push in the product's default view.** RENEGOTIATE/TENDER stay as customer-initiated, human-approved actions.
5. Europress stays a technology provider. It **never operates trucks, trades waste, or takes a margin on transport** [fact: Tommi].

### 5.4 Risks and mitigations

| Risk | Sev. | Mitigation |
|---|---|---|
| Accuracy (virtual ±7% vs ~±3% for per-lift verification [fact: weighing-engineer.md]) | High | Verify monthly/contract totals; intervals; platform where per-lift is needed |
| Legal metrology (NAWI) | High | "Verification, not billing" in T&C; weighbridge stays billing basis; consult Tukes [assumption] |
| Operator backlash | High | §5.3; co-pilot operator |
| Price sensitivity | High | Intro free; lease bundle; fee ≤ value/3 |
| Competition law (index) | Med | Historical, aggregated, k ≥ 5, legal review |
| Value overstatement | Med | Report only realised, approved €; show grid |
| IP (US11162834) / CSRD scope shrink | Med | FTO check; lead with WFD, BDO and cost |
| GDPR | Low | B2B machine data; DPA for RFID per-user data |

## 6. "Change the industry" vision (3–5 years)

**From "the operator's scale decides" to "the weight is known at source, shared and neutral."**

1. **Y1–2 Weight at source:** virtual scale on every SMART unit, golden-cohort platforms; customers see €/t per site.
2. **Y2–3 Neutral reconciliation layer:** device, ticket and invoice kg auto-matched for operators and customers; Europress as the trusted clearing record, not a party to transport [estimate].
3. **Y3–4 Compliance by default:** one-click ESRS E5, WFD food-waste baseline and Polish BDO/KPO filings with audit trail.
4. **Y4–5 Data products:** anonymised €/t and quality index for chains, recyclers, EPR schemes (precedent: Greyparrot Deepnest sells waste data to brands [fact: wastedive.com/.../826339]); value-based selling of weighed, graded bales as a future hypothesis.

Outcome: Europress moves from machine maker to the asset-light **weight-data infrastructure of commercial recycling**.

## 7. Open questions for Tommi

1. What is the real connected installed base and what is the group revenue figure (€35.6M Oy vs ~€70M group)?
2. What are today's prices for Intro, Insights and Integrated, and the service-contract margin and churn? These decide whether the strategic case (attach and retention) carries the P&L.
3. What are the price, accuracy and install time of the existing Scale platform?
4. Do operators buy Europress machines, and which operator would co-pilot with WEIGHED-tare tickets?
5. Poland: do customers struggle with BDO reporting today, and would they pay for pre-filled KPO data?
6. May anonymised cross-customer €/t data be used under current customer T&C?

