# Comparison: Set S (Sonnet, `soome_hackathon_2026/docs/agents`) vs Set O (ours, `europress_conclusions/agents`)

2026-11-06. Checks were run read-only on `data/competition/public` (scripts in the session scratchpad). [D] = computed here.

## 1. Topic by topic

| Topic | S position | O position | Better / why |
|---|---|---|---|
| Core product | "Verified Weight" Insights add-on (business-strategist §0) | Same spine. Five plan variants: CFO, Poland, ESG, data platform, strategy | **Tie.**Independent convergence is good evidence |
| Price | €15/device-month (10/25), plus a €2/verified-tonne variant | €10, €12, €15, €25 and 25 % gain-share, depending on the file | **S.** O contradicts itself and must pick one: CFO €15 = S €15 |
| Realisable value | €576/device-yr (242/978), 5 % of spend | €532 (50 % of €1,064) CFO; €545 ESG | **Tie.** They agree within 10 %. Both miss that the **median is €0** (below) |
| Fixed cost / break-even | 1.5 FTE, €135k/yr; 1,106 devices | €200–500k/yr; ~3,100 devices (strategy) | **O CFO** (2–3 FTE, €200–380k) is more realistic. |
| Weight accuracy | Per lift 12–15 % 1σ with fill + tickets; 5–6 % monthly. Calls ±6.6 % "optimistic" (science §0.4, §2) | Repeats ±6.6–7 % per lift and "87–93 % inside ±10–12 %" | **S.** It is better argued: a literature-anchored error budget. O should quote per-lift ~±10–15 % and monthly ±5–6 % |
| Contamination / moisture | Density-drift flags are a data use; contamination is 11 % of value; mock shows a density "HINT" | **Negative result**: density proxy precision 0.6–0.7 % (data-value §4) | **O.** Its result is computed on labels. S oversells it |
| Pickup / over-servicing | 9 % of value, "already SMART's job" | Poland plan makes avoided lifts the core (€2,347/dy) | **S** is more Tommi-compliant. O's number is real but needs reframing (§4) |
| Literature / physics | 45 cited sources, Kawakita/Kalman/conformal model, validation protocol | None beyond the weighing-engineer | **S, by far** |
| Dashboard | A working single-file HTML mock, 7 screens of IA, demo script | Wireframes, tokens, microcopy; **no HTML** | **S** has the artefact. O has better brand semantics (see §3) |
| Regulation | Data Act recitals, CSRD Omnibus, PPWR, NAWI/OIML R76 | Same, plus ESRS E5-5 §16, WFD 2025/1892, Polish BDO/KPO, Art. 101 | **O** is broader. S is deeper on metrology |
| Creative ideas, integration | 10 data uses; extends `smve.recommendation.v0` | 28 scored ideas; CloudEvents + firmware spec | **O** |

## 2. Take from S

1. **Error budget and honest accuracy claim** (science-researcher §2). The table runs from ~20 % RSS uncalibrated to 13–16 % with tickets, or 9–12 % with curve features. Gaussian shares inside ±10 % / ±12 % are 56 % / 64 % at σ = 13 %. The monthly figure is √(12²/n + 3.4²) ≈ 5.4–6 %. [Literature-derived estimate, not data.] Use it instead of the bare "±6.6 %".
2. **Fleet-learning precedent** (§0.3, [8] Mansouri 2025). A model built on 25,000 bales from 25 scale-equipped machines reached 4.96 % MRE on machines without scales. Cites our golden cohort.
3. **Negative literature result** (§0.1). No peer-reviewed mass-from-pressure study exists for compactors. Novelty and limitation.
4. **Model structure** (§3). Kawakita density prior, log-space GBM correction, partial pooling of per-machine gain, a Kalman update per clean ticket, Mondrian conformal intervals with ACI, and a CUSUM/ADWIN anomaly layer.
5. **Validation protocol** (§4). Leave-one-machine-out testing, Bland-Altman on the log-ratio, baselines B0–B3, and an ablation over k = 0/3/5/10/20 tickets. Acceptance: median lift error ≤ 10 % and 80 % interval coverage of 75–85 %. Pilot: ~10 machines × 20–30 tickets.
6. **Ground truth is fuzzy** (§0.5, OIML R76 [11]). Weighbridge net can be off by ±40 kg at initial verification and ±80 kg in service. Deconvolve with σ_model² = σ_obs² − σ_ticket².
7. **Quotable facts** (§7). EN 643/CEPI allows 10 % moisture in recovered paper, and buyers claim back the excess. Puts money on Tommi's rain story. Trade-grade bin weighing is certified only up to ≤600 kg.
8. **IP flag** (§1.3 [22]). US8794135B1 (One Plus, active to ~2028) covers pressure-based diagnostics and needs a freedom-to-operate check. O only flags US11162834.
9. **Mock dashboard** (`mock_dashboard.html`). Adopt it as the HTML fallback and template (product-designer §6 option C). Elements to reuse:
   - a persistent, non-dismissible **SYNTHETIC banner**;
   - provenance badges [M]/[R]/[~]/[?] that use shape as well as colour;
   - findings list, then detail with "Why we think so" and a **"What could make this wrong"** section;
   - a mass trace with invoice markers;
   - a three-source band chart (device, ticket, invoice);
   - an approve panel: evidence checkbox → "Approve and prepare draft" → audit log, with `aria-live`.
10. **"A tool that says no earns the yes"** (product-designer §3.2 F2, §4 rule 6). A real 335 kg gap is worth €0 on a per-lift contract, so the tool says "no action". Value is computed through contract mechanics.
11. **UX rules** (product-designer §4).
    - Combined band = 2√(σ_dev² + σ_ticket²), with σ_ticket set by `tare_method`. Competition-set check [D], single loads: WEIGHED robust SD 3.8 % (16.5 % of pairs differ by more than 10 %); STORED 7.5 % (34.7 %); EQUAL_SPLIT ~33 %.
    - Explicit green/amber/red **sensor-trust thresholds** (§3.4).
    - Confidence tiers High/Medium/Low.
    - Hauler scorecard shows n, and "insufficient data" below n = 20.
12. **Data-source palette** (product-designer §1.1). Device `#4b5ac3`, weighbridge `#009a98`, invoice `#b07400`; CVD-validated, with pink reserved for alerts. O colours the invoice series `#d1003f`, which is also its Critical severity colour. A red invoice line implies the operator is at fault and breaks neutrality. Keep O's autumn-for-error rule and adopt S's series palette.
13. **Pricing ideas O lacks** (business-strategist §3):
    - per-verified-tonne price (€2/t ≈ €14/month);
    - chain licence €10–40k/yr on top of device fees;
    - operator "weight handshake" at €0.3–1.0 per verified lift;
    - tender pack €1.5–5k;
    - payback rule: retrofit pays only above €330/device-yr of value (48 % of customers), factory-fit above €220.
14. **3-minute demo script** (product-designer §5): wow, then honesty case, then approval.

## 3. Contradictions and which to trust

| Item | S | O | Verdict |
|---|---|---|---|
| Value per device-yr | €576 mean | €1,064 identified / €532 realisable, mean | **Both incomplete.** [D] Dev cases: n = 207, mean €1,064, **median €0** (52 % of contracts have no positive best set). Top 5 of 20 dev customers hold **75 %** of the value. In the full fleet, the top 5 customers hold 40.5 % of devices. State the median and the concentration. S's "top 5 hold 54 %" is directionally right |
| Per-lift accuracy | 12–15 % | 6.6–7 % | **Trust S** for the pitch: O's figure is an untested engineering RSS |
| Density-based contamination and moisture | Works as a hint | Does not work on this data | **Trust O.** O's own creative-ideas W8/V1 "dry tonnes" also conflicts with data-value §4. Demo it only as a weather-covariate *hypothesis* |
| Phantom-lift wow attributed to weight | S frames it as weight evidence | O: only 3 % of billing errors need weight | **O is more honest.** Phantom lines are caught by the collection log plus fill. Say "your compactor's record", not "weight" |
| Installed base | ~12k devices | 15,000 (strategy) vs 12,000 (CFO) | Unknown. Use one parameter and ask Tommi |
| Ticket coverage | Quickstart: 45–94 % | Competition: A 96, B 88, C 51, D 0, E 94 % | Different packs; [D] confirms O (73.5 % overall) |
| Hardware add-on | €150 factory sensor / €600 retrofit | Zero BOM; load cells €1.0–1.9k | O matches "no new sensors". S's €150 sensor is undefined |
| Brand semantics | Pink = alert | Pink = accent, never "bad"; errors use autumn | **O** is closer to the theme's `--color-error` |

## 4. Conflicts with Tommi's statements

- **O Poland plan (bizplan-cheapest-poland).** Its core is avoided lifts, which is pickup optimisation. It also concedes fill alone catches 92.7 % of the value. Reframe it as "proof-of-fullness that moves fixed-schedule customers onto existing SMART on-call": an add-on that sells SMART and leases, not a new optimiser.
- **S business-strategist.** "Weight-included lease" with a €150–300 integrated sensor and a €600 retrofit adds BOM ("cheapest wins"). Materials marketplace (#7) and tonne-based full service (#8) edge into the waste business. S scores #8 lowest; drop both.
- **S uses Tommi's €70M** for scale. O shows the Oy's revenue is €35.6M. Ask which figure applies.
- **Contamination or moisture from density** (S strategist §7.3, product-designer §3.3). This promises a "second problem" solution that the data does not support. Offer O's A1 trolley photo or the acoustic hypothesis plus S's literature (ContamiNet AUC 0.86) as the roadmap.
- **Pricing spread in O** (€10 to €25 plus 25 % gain-share). Fix it as: Intro free ballpark, Insights +€15, Integrated per-chain licence plus device fee, load cells only inside the lease (CFO §4).
- **Operator neutrality.** O's red invoice series (§3) breaks it.
- **Both comply** on no trucks, service-provider role, human approval, 80/20 and service-contract profit (O CFO's retention credit expresses it best).
