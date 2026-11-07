# Creative strategist: 28 new ideas beyond C1–C14

Lens: divergent ideas that sit on top of the **"Verified Weight"** spine (red-team portfolio A). Ideas C1–C14 in `red-team-judge.md` §2 and options a–e in `weighing-engineer.md` §1 are **not** repeated here. Where an idea sits next to one of them, I say so. Tags: **[F]** fact with a source (listed at the end), **[E]** estimate, **[A]** assumption.

**Scoring (1–5).** Fit = fit with Tommi's red lines: no trucks, no waste trading, cheapest wins, operator-neutral, human approval. Judge = expected pull on the official criteria. Demo = can we show it in 48 h on the synthetic dataset. Orig = originality. Rev = revenue potential for Europress. Σ is the plain sum, out of 25.

---

## 1. Idea bank

### (a) Weighing hacks at near-zero BOM

| ID | Idea | Fit | Judge | Demo | Orig | Rev | Σ |
|---|---|---|---|---|---|---|---|
| **W1** | **"Watt-scale": a second physical channel.** Energy per stroke from the motor supply: an existing soft-starter or VFD readout, or a ~€10 CT clamp [E]. Motor power is a known proxy for pump hydraulic load [F1]. Fusing it with pressure gives two semi-independent views of compaction work, which cuts unit-gain error and flags a drifting pressure transducer. | 5 | 4 | 3 | 4 | 2 | 18 |
| **W2** | **Stroke-timing features.** Time to reach relief pressure, ram return time, and dwell all come from the PLC timestamps the controller already has. No BOM, firmware only. Denser material gives a faster pressure rise. Stroke timing is also a predictive-maintenance signal (pump wear), so one feature serves both products. | 5 | 4 | 2 | 3 | 2 | 16 |
| **W3** | **Hook-lift handshake.** An NFC/QR tag on the COMBI unit (€0.50 [E]) lets the operator's own hook-lift weigher tag each lift to the right device. Hiab MULTILIFT claims ±2% integrated weighing with history on HiConnect [F2]. Operator-owned truth per lift, no weighbridge. Adjacent to option c, but the new part is the zero-hardware pairing protocol. Needs operator buy-in. | 4 | 3 | 3 | 4 | 2 | 16 |
| **W4** | **Scaletipper bridge.** Where bins are tipped into the compactor, Europress's own Scaletipper "scale solution" sums bin weights bottom-up. This is truth for bio-waste, where the pressure model fails. Uses an existing in-house product line. | 5 | 4 | 2 | 4 | 3 | 18 |
| **W5** | **Shared service-visit weigh kit.** The technician carries portable wheel-load pads on the paid service visit and logs one anchor via QR scan. One €2–3k kit across ~150 machines is ≈€15–20 per machine [E]. Removes the "no tickets" gap (OP-D shares 0%). | 5 | 4 | 4 | 3 | 2 | 18 |
| **W6** | **Inbound-packaging mass balance.** Retail chains know their goods received, and under PPWR they must report packaging types and quantities [F3]. Σ(cases × SKU packaging kg) gives an expected cardboard mass: an independent anchor that needs no hardware. | 4 | 4 | 2 | **5** | 3 | 18 |
| **W7** | **Acoustic contamination tap.** A ~€2 MEMS microphone in the IoT box [E] listens for glass or metal crunch inside cardboard strokes. Detection only, not weight. Feasibility is unproven, so present it as a research hypothesis. | 4 | 2 | 1 | 4 | 2 | 13 |
| **W8** | **Dry-tonne normalisation.** Precipitation from an open weather API, combined with lid state, separates water from fibre in cardboard mass. Tommi's "+100 kg over a weekend" becomes a quantity you can bill-check and act on. Dataset hook: 69 `MOISTURE_HEAVY_LOAD` labels. | 5 | 5 | 4 | 4 | 3 | **21** |

### (b) Customer-facing value

| ID | Idea | Fit | Judge | Demo | Orig | Rev | Σ |
|---|---|---|---|---|---|---|---|
| **V1** | **"Water you paid for" lid nudge** (built on W8). A push to the store manager: "Weekend rain added ~140 kg ≈ €X on the mixed bill [A, hypothetical price]. Keep the lid closed." It is a behavioural nudge with an € figure, aimed at the price-sensitive small customer. | 5 | 5 | 5 | 4 | 3 | **22** |
| **V2** | **Shift-level contamination coach.** Density anomalies are bucketed by shift and fed back to the team, never to an individual (GDPR and works councils) [A]. A breakroom card reads "Tuesday evening: 3 suspicious loads". | 4 | 4 | 4 | 3 | 2 | 17 |
| **V3** | **Chain "Recycling Cup".** A store-vs-store league inside one chain covering €/t, contamination and moisture share. Big chains want more SMART [Tommi]. Peers make it competitive without blaming any operator. | 5 | 4 | 5 | 3 | 3 | 20 |
| **V4** | **Supplier packaging scorecard** (built on W6). Shows the retailer kg of cardboard per supplier. That is leverage for PPWR packaging-minimisation talks [F3], and value for the chain's buyers rather than only its facility managers. | 4 | 4 | 2 | **5** | 3 | 18 |
| **V5** | **Intro-tier "one-line savings" SMS.** The free or Intro customer gets one sentence a month: "Save ~€X by Y". It serves the 85% non-SMART base and acts as an upsell funnel. | 5 | 4 | 4 | 2 | 4 | 19 |
| **V6** | **Insurance risk signal.** Fill, oil temperature and fault patterns feed a fire and damage-risk score, which the customer could take to its insurer [A]. Never claim an insurer accepts it. | 4 | 2 | 2 | 4 | 2 | 14 |
| **V7** | **QR "value at the door".** A sticker on the machine. Staff scan it and see in plain Finnish or Polish: "Each kg here earns X; each kg of cardboard in the mixed bin costs Y". This answers "customers not educated enough". | 5 | 4 | 5 | 3 | 2 | 19 |

### (c) Business models and ecosystem

| ID | Idea | Fit | Judge | Demo | Orig | Rev | Σ |
|---|---|---|---|---|---|---|---|
| **B1** | **Nordic Material Flow Index.** Monthly cardboard tonnage generated at source, used as a retail-activity nowcast. A free headline plus a paid feed. Unlike C10's €/t price index, this is a **volume** index, which avoids competition-law risk on price exchange [A]. | 4 | 4 | 4 | 4 | 3 | 19 |
| **B2** | **Recycler supply forecast feed.** Sells mills and plastics recyclers a 2–8 week OCC/plastic supply forecast by region and grade. Europress sells the forecast, not the material, so it is not waste trading. | 4 | 4 | 3 | 4 | 4 | 19 |
| **B3** | **Lease-risk data for the financier.** Utilisation and health history lowers the leasing partner's residual-value risk, so the customer gets a cheaper lease. "Cheapest wins" is met by the financing line, not the BOM [A]. | 5 | 3 | 2 | 4 | 3 | 17 |
| **B4** | **Gain-share SMART.** The fee is a share of verified savings, so a small customer pays nothing up front. Adjacent to C11, but the base is outcome, not throughput. Attribution disputes are the risk. | 4 | 4 | 3 | 3 | 4 | 18 |
| **B5** | **White-label "Verified Service" portal for operators.** Sells the reconciliation engine to haulers as their own customer-transparency portal. This turns the adversary into a channel and keeps Europress neutral. | 5 | 4 | 3 | 4 | 4 | 20 |
| **B6** | **PRO and municipality feed.** Verified source-separated tonnes from commercial sites go to producer-responsibility organisations (Rinki is already a customer [brief]) for EPR reconciliation. | 4 | 3 | 2 | 4 | 3 | 16 |
| **B7** | **Poland BDO autofill.** Polish waste producers must issue electronic waste-transfer cards (KPO) in BDO, with mass in Mg to four decimals and penalties up to PLN 1M [F4]. SMART pre-fills the KPO mass from the device and the operator confirms it. A compliance hook in the key growth market, where fixed schedules still dominate. | 5 | 5 | 3 | **5** | 4 | **22** |
| **B8** | **Machine passport and second life.** Lifetime tonnes, strokes and health certify the residual value of ex-lease machines for refurbishment and resale (for example in Poland). It is circular economy applied to Europress's own product. | 5 | 3 | 3 | 4 | 3 | 18 |

### (d) AI-native

| ID | Idea | Fit | Judge | Demo | Orig | Rev | Σ |
|---|---|---|---|---|---|---|---|
| **A1** | **Trolley-photo pre-sort.** Staff snap the trolley via the QR page. A vision LLM says "remove 2 plastic wraps → mixed bin" before the drop. Greyparrot-style vision works on MRF conveyors [F5]; we move it to the **source**. Advice only, with no automatic action. | 5 | 4 | 5 | 4 | 2 | 20 |
| **A2** | **Voice "Ask your compactor"** in FI, PL and SV, grounded only on SMART rows. The red team cut a *fake* assistant, so only show it if it is real and cites row IDs. | 4 | 3 | 3 | 2 | 2 | 14 |
| **A3** | **Contract reader.** An LLM extracts tariffs from customer PDF contracts into the `contract_versions` schema with a human diff-approve step. Onboarding takes minutes, and €/t works even for customers who do not know their own tariffs. | 5 | 4 | 4 | 3 | 3 | 19 |
| **A4** | **Synthetic-fleet pricing simulator.** An agent-based model of ~10k customers with price elasticity per segment picks SMART tier prices. This gives Task D's "team-chosen price + adoption" a traceable sensitivity analysis. | 5 | 4 | 4 | 3 | 3 | 19 |
| **A5** | **Value-of-information anchor scheduler.** A Bayesian model ranks devices by (posterior σ × € at stake) and says which machines need an anchor weigh (W5, a ticket request, or Scaletipper) next. It spends the calibration budget where it pays most. | 5 | **5** | 4 | **5** | 3 | **22** |

---

## 2. Top 5 "wow but credible" add-ons for the Verified Weight spine

**1. A5 Anchor scheduler, "calibrate 15% of the fleet, get most of the accuracy" (Part 1 + K3).** On the dataset, start every device with a fleet prior from weighing-engineer §e. Each quality-gated ticket or simulated W5 visit then updates a per-device posterior. In the demo, a slider sets the anchor budget (0–100 visits). A curve shows fleet-median interval width falling, and the next-visit list is ranked by expected € error removed. The claim is an [E] that we compute live on synthetic data and never present as field accuracy. It turns the weighing concept from a static table into an operating policy, the "cheapest wins" answer judges can see.

**2. W8 + V1 Dry tonnes and the "water you paid for" nudge (K2 + K6).** Join the `MOISTURE_HEAVY_LOAD` events with a synthetic precipitation series (a real open weather API in production; list its licence). The demo shows one lift card: device kg 3,240 = fibre ~3,100 + water ~140, with a band [illustrative]. Below it sits a draft push to the store manager that a human must approve before it is sent. It is Tommi's own anecdote turned into a product feature and a measured behaviour change. The validation idea is a lid-closed vs lid-open A/B across a chain.

**3. W1 + W2 Two-channel virtual scale (Part 1 slide).** The weighing slide adds one row: "motor energy per stroke and time-to-pressure, from signals the controller already has or a ~€10 CT clamp" [E]. It also shows a fusion diagram (pressure ⊕ energy ⊕ timing → mass with σ). Narrative: two independent physical views let the system say whose fault a discrepancy is, the sensor's or the load's, which extends C4 to the device side. We have no pressure or power data, so the slide must say "untested; validation = golden cohort (option e) with both channels logged". It answers "a justified alternative" in the brief cheaply and originally.

**4. A1 Trolley-photo pre-sort (live demo moment, creative AI).** On stage, a teammate scans the QR sticker (V7) on a printed compactor photo and photographs a trolley of cardboard with a plastic wrap. Within ~5 s the page shows "Remove: 1 plastic film (est.) → mixed bin. Avoids ~€X contamination penalty risk [hypothetical]" plus a confidence level. The page logs the event to SMART as an *advisory*, never as a grade. It is the most memorable 20 seconds of the pitch, and it attacks Tommi's problem 2 before the waste enters the machine. List the model and API licence, and note that vision accuracy on real trolleys is untested.

**5. B7 + B6 Regulatory autofill (business-plan slide, productisation).** Slide: "In Poland every waste handover needs an e-KPO with mass in Mg [F4]. SMART pre-fills it from the device weight, and the operator confirms in BDO." Add a small mock of a KPO field populated from one dataset lift, with uncertainty and an "operator-confirmed: pending" status. The Nordic version of the same pipe feeds Rinki-style PRO reconciliation (B6). Weight then becomes a compliance utility, which is a reason to buy SMART in the market Tommi called key. Caveat: device weight is not legal-for-trade, so it pre-fills and the weighbridge or operator remains the record of truth.

**Honourable mentions.** W6/V4 is the most original idea, but its data is fictional, so give it one vision-slide sentence. B5 is the best neutrality story for the Q&A.

---

## 3. Industry-changing vision statements

1. "**Every kilo known at the source.** From the machine, not the truck, so the value of waste stays with whoever made it."
2. "**From weighbridge to waste-bridge.** Europress makes the compactor the neutral, trusted ledger the whole recycling chain settles on."
3. "**The cheapest scale is the one you already own.** SMART turns 15 years of installed machines into a calibrated, self-improving weighing network."

---

## 4. Limits

- Nothing was tested on real pressure, power or acoustic data, because the dataset has none. Each Part 1 add-on is a hypothesis paired with a validation design.
- B7 needs a legal check: who issues the KPO, and whether an estimate may pre-fill it [F4].
- CSRD now covers only companies with >1,000 employees and >€450M turnover [F6], so ESG value applies to the big chains only.
- B1 and B2 need data-licence consent and k-anonymity. The view that volume indices carry lower competition-law risk is [A].

## Sources

- [F1] ORNL, motor as transducer for pump load: https://www.osti.gov/biblio/236262 (accessed 2026-11-06)
- [F2] Hiab MULTILIFT Ultima integrated weighing ±2%, HiConnect history: https://hiab.com/en-us/products/hooklifts-and-roll-off-hoists/ultima-series
- [F3] PPWR (EU 2025/40), obligations from 12 Aug 2026, producer reporting of packaging quantities (secondary sources; verify in the Official Journal): https://www.gtlaw.com/pl/insights/2026/6/countdown-to-the-new-eu-packaging-and-packaging-waste-regulation-compliance-considerations ; https://verkkolehti.rinkiin.fi/the-ppwr-in-brief?lang=en
- [F4] Poland BDO and e-KPO with mass in Mg, penalties: https://www.dudkowiak.com/environmental-law-in-poland/bdo-register-in-poland/ ; https://www.igwp.org.pl/wp-content/uploads/2020/01/images_pliki_szkolenia_bdo_200123_Rejestr_BDO_szkolenie.pdf
- [F5] Greyparrot conveyor-level waste vision (vendor claims): https://letsdatascience.com/news/greyparrot-raises-27-million-to-scale-ai-waste-intelligence-53666feb
- [F6] CSRD Omnibus I thresholds: https://www.pwc.lu/en/sustainability/sustainable-finance/eu-finalises-agreement-on-omnibus.html
