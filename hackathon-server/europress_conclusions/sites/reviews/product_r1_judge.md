# Product site review, round 1: Tommi plus a sceptical juror

Scope: `sites/product/index.html` (HTML and JS, read in full) and `data.json`, spot-checked against the raw parquet. **No screenshot:** the bundled Chrome is missing `libnss3.so`, so this review is from the code only.

## Score now: about 66/100

| Criterion | Max | Now | Why |
|---|---|---|---|
| K1 Weighing concept | 25 | **13** | The T0/T1/T2 ladder, €0 BOM, calibration simulator and pilot acceptance criteria are good. Missing: the physics (why ram pressure tells you mass), **sensor placement**, **installation and retrofit**, an **error-budget table** and an **option comparison** (load cells, strain, hydraulic, truck/hook weighing). There is also a T1 inconsistency (P0-1). |
| K2 Customer/business value | 25 | **17** | Operator-first handling, the "says no" lift, Proof of Fullness, and an honest value concentration (median €0). Weak points: fleet tile 4 leads with €45.6k of billing errors when only 3.1% of that needs weight. The renegotiate hero is a contract that is already 37% *below* the peer median. No per-buyer value statement. |
| K3 Data and traceability | 20 | **15** | Very strong: row-level chain, bands derived from data, R1 precision 100% / recall 66% without labels, negative density result. A few counts don't line up (P1-4). |
| K4 Demo + SMART path | 15 | **10** | Five working screens, CloudEvents outbox, ingest API, tier map. Missing: an architecture flow showing what exists today vs what is new, where T0 runs (edge or cloud), and how to run or reproduce it. No guided path for someone watching without narration. |
| K5 Productisation | 10 | **7** | Tier mapping, ⅓-of-value rule, gain-share and the "stickier service contract" NPV are good. "Scale platform +€39–49/month" next to "€14–26/month" reads as a contradiction without a "cost vs price" label. |
| K6 Clarity and limits | 5 | **4** | Evidence chips, "what could make this wrong" panels and the limits list are good. The hero card has no chip, even though the page says every number carries one. |

## Tommi's anchors

- Cheapest wins (T0 is €0): **respected.**
- Ballpark is OK (± bands everywhere): **respected.**
- No pickup optimiser: **respected.** It is stated twice, and the PoF draft refuses on-call because of overflow risk.
- Operator-neutral: **respected.** Hauler table is alphabetical, tare findings go to the operator first, colours are neutral.
- No trucks: **respected.**
- Part 2 is "the beef": **mostly.** But the page has no explicit "what the customer gets" block, so the value has to be read out of the demo.
- Creative AI use: **weak.** The page says "no LLM runs" (honest) and gives one paragraph on Claude Code. Tommi asked to *see* AI used. There is no sample draft, no description of the guard, and no AI-vs-rules number of our own.
- Wrong material handled honestly: **yes.** ~1% precision is shown and it is placed on the roadmap.
- Ticket calibration does not reduce per-lift error: **mostly honest**, apart from the trace toggle (P0-1).

## Hardest questions the page does not answer

The numbers refer to the 15 hardest questions in red-team-judge.md §5.

- **Q2** Honest accuracy. The empirical fact is missing: in the data, a rolling ticket calibration leaves median |error| unchanged (2.8% → 2.8%).
- **Q3** Cost per machine, including install labour and T2 retrofit.
- **Q6** Who owns the data.
- **Q8** Wet or bio-waste bands. 78% of bio-waste lifts are within 10%, vs 88% for cardboard; this is not on the page.
- **Q11** Our own AI bake-off.
- **Q12** Europress margin and break-even (~3,100 devices).
- **Q13** Real SMART surface: what exists vs what is new.
- **Q15** Polish ticket and BDO formats are untested.

---

## P0: fix before anything else

**P0-1. T1 toggle contradicts the T1 card and the simulator.**
- Where: trace screen, `<button data-tier="T1">T1 ±8%</button>` and JS `TIER = {T0:.13, T1:.08, …}`.
- Problem: the T1 card itself says "Per-lift error stays near ±12%". The simulator at defaults gives 12.5% → 12.3% per lift and 5.4% → 5.0% monthly after 10 tickets.
- Fix: remove the T1 button, or set it to `.12` and label it **"T1 ±12% per lift (bias removed)"**.
- Also change the T1 card headline from "±3–5% monthly" to **"≈ ±5% monthly (target ±3–5%, untested)"**, and add one line: *"Measured on the dataset: a rolling per-device ticket correction leaves median error unchanged (2.8% → 2.8%). Tickets fix drift and bias, not noise."*

**P0-2. Part 1 needs a real concept block (worth up to about 8 K1 points).**
- Where: `#how`, a new card under the tier grid titled "How the virtual scale works".
- What to add:
  - **Principle:** mass ≈ compacted volume (ram stroke × chamber area, from the fill model) × density, where density is inferred from the back-pressure-vs-stroke curve (0–200 bar transducer already on the hydraulic circuit) and the stream's density prior.
  - **Placement:** the existing pressure transducer and PLC; no new sensor. T2 adds 4 load cells under the container platform.
  - **Installation:** T0 is an OTA firmware update (10–20 Hz logging) plus a cloud model, with no site visit. T2 retrofit needs a technician (~½ day, cost [E]) at a service visit that already happens.
  - **Error budget table, 1σ [E]:**

    | Error source | Estimated 1σ |
    |---|---|
    | Density/material mix | 8–10% |
    | Fill-estimate error | 4–6% |
    | Springback (cardboard) | 3–5% |
    | Oil temperature/viscosity | 1–2% |
    | Moisture (bio) | 3–8% |
    | Ram/seal wear (drift) | slow |
    | **Combined** | **≈ 12–15%** |

  - **Option comparison** (BOM, accuracy, retrofit, verdict):

    | Option | BOM | Accuracy | Retrofit | Verdict |
    |---|---|---|---|---|
    | Load cells | €1.0–1.9k | ±1–2% | Technician | T2 |
    | Chassis strain gauges | Low | ±5–10% | Harsh environment | Rejected |
    | Hydraulic pressure | €0 | ±12–15% | OTA | Default |
    | Truck/hook-lift scale | €0 to Europress | n/a | n/a | Operator-owned, which is the problem we solve |

  - Keep the [E] tags.

**P0-3. The PoF hero over-claims.**
- Where: JS `renderPof`, `"The compactor's weight is the only proof."`
- Problem: the same panel says fill alone catches 92% of the €, and the chart shows fill, not weight.
- Replace with: *"On a fixed twice-weekly schedule, 45 of 78 labelled lifts at CMP-00430 were not needed. Fill shows it; the compactor's kg is the only tonnage to put in front of the hauler, which shares no tickets."*

**P0-4. Renegotiate hero P-005 (CTR-00142) undermines credibility.**
- Problem: the contract is €33.8/t against a €53.8/t peer median, so it is already cheap, yet we show €9,953 of renegotiation value. A juror will ask "why renegotiate a cheap contract?"
- Fix, either:
  - pick a device-weight-only contract that is *above* the peer median, or
  - retitle it **"Contract review (valuation rules, not a price gap)"** and put the −37% first in "why".

---

## P1: high value

**P1-1. Lead with the weight-attributable euros.**
- Where: fleet tile 4.
- Change it to **"Mass-billed € only the compactor can verify: €1,730/device-yr (77% → 96% coverage)"**.
- Move the €45.6k figure into the note: "all billing errors €45.6k, only 3.1% weight-related".

**P1-2. A "What the customer gets" block** at the top of `#demo` or `#pricing`. One row per buyer, each with a chip:
- Chain finance: verify 96% of mass-billed €.
- Fixed-schedule site (PL): ~18–20 avoidable lifts/yr, €759 p50 / €2,597 mean.
- Procurement: €/t with no operator ticket, covering 28% of contract value.
- Operator: private tare report. 18 of 70 vehicles are off by ≥200 kg.

**P1-3. Make AI visible and honest.**
- Where: `#limits`, "How we used AI". Expand it into its own card.
- Concrete build log: which agents did what (data-value analysis, red team, build), and what humans verified (claims audit, spot checks).
- One labelled **sample Claude draft**, cached and flagged "LLM draft, not live", next to the template, with the guard rules: rejects uncited rows, unsupported numbers and blame words.
- Our own number: "rule R1: 25 flagged, 25 correct, 66% recall, no labels used".

**P1-4. Align the counts.**
- PoF: "45 of 78" are the *labelled* lifts; the device had 86 completed lifts in the window. Say "45 of 78 labelled lifts".
- The €14,702 sums all 45 labels. The tile says "fixed €409/lift", but the mean value per avoidable lift is €327. Write "€327 avg per avoidable lift (lift fee €409)".
- The V06 hero sentence hard-codes "174 stored-tare tickets", while P-002 says "137 stored-tare lifts" and the chart says n=102 pairs. Explain each: tickets vs window lifts vs clean pairs.

**P1-5. Integration flow diagram.**
- Where: `#integration`.
- Show the flow: compactor PLC (pressure, fill; **exists**) → SMART cloud telemetry (**exists**) → weight model + reconcile engine (**new**) → SMART portal screens (**new**) → CloudEvents → customer ERP / operator API.
- Add one line on consent and data ownership: "customer owns device and contract data; operator owns tickets; Europress processes under contract".
- Add a 3-step pilot timeline (Q1–Q2 2027) with gates.

**P1-6. A 3-minute self-guided path.**
- Add a "Next: Cause attribution →" button at the bottom of each panel.
- Add a one-line "Start here" above the tabs.
- Make the default trace tier **T0**, with a note: *"Even at T0 the invoice flag holds: 3.2σ, because the ticket carries the verdict."* At T0 the H1 lift gives z ≈ 3.25.

**P1-7. Fill the licence table gaps.**
- Add Claude Code / Anthropic models (used to build; commercial terms).
- Add Google Fonts privacy: it loads from `fonts.googleapis.com`, so self-host or note GDPR.
- Mark Playwright/Chromium as test-only if used.
- Add a patent row: "found by title, no FTO".

---

## P2: polish

1. The hero card has no evidence chip. Add Observed for the masses and Hypothetical for the €.
2. The PoF p10–p90 (€3,651–3,849) is simulation SE, not outcome uncertainty. Show the range across the 9 cases (€0–3,951), noting 2 of them are no-action. Fix "2 of 9 later cases" to "2 of 9 cases".
3. "No weight: 43 devices" is a dataset artefact. Add "in a real fleet every SMART machine can run T0".
4. Pricing: label the T2 figures "cost to Europress €14–26/mo vs lease price +€39–49/mo".
5. Add Q8 to the limits: bio-waste is within 10% on 78% of lifts vs 88% for cardboard, so bands are widened.
6. Add a Poland line to the limits: BDO and ticket formats are untested.
7. Fleet hero "7,540 of 9,062 agree" is at the T2-grade dataset scale. Add "(at dataset ±1.4%)".

**After P0 and P1, the expected score is about 76–80.**
