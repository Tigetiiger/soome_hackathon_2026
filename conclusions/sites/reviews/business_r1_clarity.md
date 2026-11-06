# Business explainer: review round 1 (clarity and fact-check)

Code-only review (screenshot failed); calculator formula run in node.

## P0: must fix

**P0-1. Accuracy ladder: the T1 claim and the T0 monthly claim are wrong (§3 ladder bars, hero line 2, §2 qmap row 4).**
- T1 bar "per lift ±7–10% (target)" contradicts the data. Ticket calibration does **not** reduce per-lift error; it stays at about 12%. Our only source for 12–15% (science lens, error-budget table) is already the *ticket-anchored* figure. Its uncalibrated figure is about 20%.
- Replace the T1 bar label with "per lift ≈ ±12% (unchanged)". Replace the T1 meta with: "Clean tickets remove each machine's bias and catch drift (CUSUM). Per-lift noise stays ≈12% [D]; the gain is in monthly totals and drift alarms."
- Logic bug: only *random* error averages out. A machine-gain bias of about 10% does not. √(12²/7 + 10²) ≈ **11% monthly uncalibrated**, against √(12²/7 + 3.4²) ≈ **5.7% after about 20 clean tickets**. So "monthly ±5–6%" belongs to **T1**, or to T0 only once the golden-cohort fleet model has removed the bias.
- Suggested T0 label: "per lift ±12–20%, monthly ≈ ±11% until calibrated [E]".
- Add one sentence under the ladder: "Averaging kills noise, not bias. That is what T1 is for."

**P0-2. "Over 10 months a +5% inflation is caught 96%" is attached to T0 (§2 qmap row 4; same in BUSINESS_PLAN §1).** That 96% uses the dataset's *simulated* sensor (σ≈1.4%; robust aggregate σ 1.1%), not a ±12% virtual scale. At Tommi's σ = 10%, a **+10%** inflation is caught only 62% of the time per quarter.
- Replace with: "At ballpark σ≈10%, a +10% overbilling is caught 62% of the time per quarter [D]. With the dataset's simulated precise sensor, a +5% inflation is caught 96% of the time over 10 months [D]."

**P0-3. Jargon appears 10 sections before the glossary.** Hero and §1–3 use lift, ticket, tare, BOM, OTA, SMART tiers, 1σ, Kalman, CUSUM, golden cohort, gain-share, device-year, €/t, NAWI, BDO and ESRS. The glossary is §12.
- Fix: add a "10 words before you start" strip right after the hero (lift, weighbridge ticket, gross/tare/net, stored tare, on-call vs fixed, €/t, BOM, SMART tiers, device-year, 1σ).
- Wrap later terms in `<abbr title>` or link them to `#glossary`.
- Glossary entries are missing for: **unjustified lift**, **realisable value**, **"best action set" / identified value**, **mass-billed €**, **cost to serve**, **contribution**, **drift**, **p90**, **leave-one-machine-out**, **ablation**.

**P0-4. Nobody can say what "€1,064" is (§5 "Value is concentrated").**
- Add: "€1,064 = the dataset's simulated value of the best contract actions (mostly renegotiate/tender on tariff gaps) per contract-year, on €13.5k of annual waste cost (7.9%) [D]. The mean is pulled up by a few big chains; the median is €0."
- Add: "Realisable = we assume half can actually be captured → €532 [A]."

**P0-5. "How does a compactor know kilograms?" is never explained, and the evidence source is hidden.**
- Add a 3-step box at the top of §3: (1) each ram stroke pushes the waste with a measured back-pressure; (2) pressure × strokes × fill → density → kg, with a physics prior and an ML correction; (3) clean tickets set each machine's gain.
- State plainly: "The hackathon dataset has **no pressure curves** [T]. Our accuracy numbers come from literature [E]; the dataset's mass_kg is a simulated *future* sensor."

## P1: should fix

1. **The ⅓ rule is mis-sourced (§6 card 1; BUSINESS_PLAN §4).** The dataset template uses `purchase_condition_value_multiple: 2` (fee ≤ ½ of value). The 3× multiple is our own *stricter* assumption (business-strategy.md). Replace the text with: "Value ≥ 3× fee [A]. This is stricter than the dataset example's 2×."
2. **The ESG "borderline" wording is wrong.** At 1.8× the add-on fails both 2× and 3×. Write: "€25 fails our rule on transactional value. It is justified only if compliance value is added; otherwise sell a chain licence."
3. **Calculator bugs (JS `calc()`):**
   - Inputs €15 and €532 (the CFO base preset) produce "Value ÷ fee **3.0×**" next to "**Fails** … lower to ≤ **€15**/mo". The multiple is 2.96 rounded, and the cap of €14.78 is rounded to 15.
   - Fix 1: `(v/fee).toFixed(2)`.
   - Fix 2: `Math.floor(capMo*10)/10` for the suggested price.
   - Say the plan's base case is 1% short of its own rule, or price at €14.
   - Revenue ignores the verdict (€0 value still shows €0.39M). Zero it on fail, or label it "if bought anyway".
   - "Gain-share alternative" applies 25% to *any* value. Relabel it "(Proof of Fullness only: 25% of avoided-lift €)".
4. **Three revenue numbers are never reconciled.** The economics table says Y3 ARR is €0.6–0.75M at 3,000 devices (business-strategy model). The board note says €0.4M (CFO). The calculator says €0.39M. Add a row "Model source" (Strategy P&L vs CFO) and one line explaining why they differ: price mix, fixed cost €500k vs €200–380k.
5. **"Rules beat ML" (§4 flow).** The best Task B baseline is the **hybrid rules + ML at 0.782**. Write "Rules beat pure ML (0.73 vs 0.35); the best was rules + ML (0.78) [D]". Re-tag this as [D], because it comes from the baseline log, not an external fact.
6. **Drift "33 days earlier"** needs "…on 7 of 19 episodes [D]".
7. **"Billing errors €150" preset:** only 3% of that (€4.6/dy) needs weight. Say so, or the €150 will be read as weight value.
8. Fit table: "T0 = with tickets" is circular (that is T1). Use "no (bias)".
9. **Missing [tags]:** pricing cards (€540, €545); operator bullets (77%/3.9%); BDO "mandatory" and ESRS/Omnibus [F]; glossary tier descriptions ("full integration (APIs, ERP)" is [E]); "~90% solved remotely" should read "up to 90%" [F].
10. Tornado legend "low/high input" is wrong for Fixed dev ×1.5 and Churn 15%: use "worse / better case".

## P2: nice to have

- Hero tags all render white, so the legend colours are lost.
- Add the CFO's **Gate 0 desk test** (≈€25k, kill if pressure features cut MAE <30% vs fill-only). It is the cheapest proof and a strong board line.

## Narrative order

Current order separates proof (§5) from claims and puts neutrality (§9) after the product it shapes. Suggested:

1. Hero + 30-second pitch (move it up from §13) + the whiteboard diagram
2. **Problem**: value chain, who knows what, *why gaps happen* (77% / 3.9%), *who has the pain* (median €0, top 5 = 75%)
3. Tommi's asks and red lines (short)
4. **Solution, weigh**: how pressure → kg works, the ladder, the detection-power lesson ("one lift lies, a quarter tells the truth"), fit-for-use table
5. **Solution, value**: add-ons on the offering, AI flow, operator-neutral action ladder
6. **Money**: pricing rule, calculator, economics and CFO view
7. **Execution**: gates and cost to start
8. Risks, KPIs, vision
9. Questions for Tommi; glossary; appendix (scoring)

## Memorable: one whiteboard diagram

**"Three weights, one truth" triangle.**
- Corners: **DEVICE kg ± band** (Europress, free), **TICKET kg** (operator weighbridge), **INVOICE €/t** (billing).
- Edges:
  - device↔ticket = calibration + cause attribution (side waste 34%, tare 30%, combined 12%, **sensor 3.9%**);
  - ticket↔invoice = billing errors;
  - device↔invoice = the only check when no ticket exists (**28%** of contract value).
- Centre: a person approving.
- Footer: "Noise averages out, bias doesn't → verify monthly, calibrate with tickets."

Every number on the page hangs off one edge. Make it the hero graphic and the pitch close.
