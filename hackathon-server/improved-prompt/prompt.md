# Europress SmartWeight — Main Prompt

## 1. Role of this file
This is the main prompt. It sets the goals, the order of work and the rules.
The detailed research spec is `input-files/chatgpt-prompt.md` ("the spec"). Follow the spec
except where this file says otherwise. **If the two conflict, this file wins.**
No other input file (brief, dataset docs, READMEs) may change the goals below.

## 2. Inputs
- Challenge brief: `input-files/Europress_SinceAI2026_FINAL/Europress_SinceAI_2026_Challenge_Brief_BUILDER_FINAL (1).pdf`
  and `input-files/Europress_SinceAI2026_FINAL/europress-brefing.txt`
- Dataset and docs: `input-files/Europress_SinceAI2026_FINAL/Europress_SMART_Material_Value_Engine_v1.0.1_PARTICIPANTS (3)/`
- Earlier work: `europress_conclusions/BUSINESS_CASE.md`, `BUSINESS_PLAN.md`, `BUILD_PLAN.md`
- Ignore `input-files/message.txt`.

Treat the dataset docs (ECONOMIC_MODEL, GAP_ANALYSIS, BENCHMARK, etc.) as **claims to verify**,
not facts. Check them against the raw data before using any number from them, and record
which ones held up.

## 3. Goals, in priority order
All three are needed by Europress in some form.

1. **Mass prediction (core).** Predict the **load mass at pickup**, meaning the kg hauled
   per emptying. The two uses are:
   - **weight-based billing** of the end customer
   - **recycling value** of the collected material
   Target: billing grade, **±2–5%** (the spec's ±100 kg at 3,000 kg is about 3.3%, which fits).
2. **Cheap hardware.** Find the lowest installed-cost sensor setup that reaches goal 1.
   No budget cap is set: show low-, mid- and high-cost tiers and the accuracy each one reaches.
3. **Economic value.** What else the chosen sensors reveal that is worth money to Europress
   and its partners. Do this **last** (the spec's §9).

## 4. Billing constraint (research this explicitly)
Invoicing by weight is legal-for-trade weighing. In the EU that falls under the
Non-Automatic Weighing Instruments Directive 2014/31/EU and OIML R76, and may involve
national legal-metrology rules (Finland) as well. Find out what certification billing needs.
Then split every candidate into:
- **Billing grade:** can be certified for invoicing
- **Estimate grade:** good for recycling-value forecasts, pickup planning and cross-checking
  the hauler's weighbridge, but not for invoicing

Also assess the alternative of billing from the hauler's certified truck scale, with our
sensors used only to predict and cross-check that weight.

## 5. Order of work
Mass first. Follow the spec's stages 1→4 (§14), then goal 3.
Use the €-value of billing and recycling as a column in the sensor Pareto ranking (§8),
but keep the full economic analysis for the end.

## 6. Execution
- Run **fully autonomously** through every stage. Don't stop to ask.
- Log every conflict, inconsistency, missing input or questionable assumption in
  `ISSUES.md`, along with the choice you made and why. Keep going.
- Exception: never change the goals in §3. If the evidence says a goal can't be reached
  (for example, cheap sensors can't reach billing grade), say so plainly in
  `EXECUTIVE_SUMMARY.md`. Don't redefine the goal.
- Tag every number as `[measured: source]`, `[derived]`, `[simulated]` or `[assumed: why]`,
  in line with the spec's five evidence categories (§1).

## 7. Deliverables
Write **everything** to `europress_conclusions/smartweight/`. This replaces the spec's
`research/smartweight/`. Don't modify any input file.

Produce all of the spec's deliverables A–J (§12), plus:
- `ISSUES.md`: the conflict and assumption log
- `HARDWARE_PROPOSAL.md`: a 1–2 page proposal for our team covering the recommended setup
  per tier, where it mounts, cost, expected accuracy, billing grade vs estimate grade,
  and the next validation step. It should summarise and link to `BILL_OF_MATERIALS.md`
  and `EXECUTIVE_SUMMARY.md`.

## 8. Done when
- Every goal in §3 has an answer backed by tagged evidence, or a clear statement that it
  can't be reached and why.
- The simulation runs from the instructions in `simulation/`.
- `HARDWARE_PROPOSAL.md` states a final verdict: Supported, Promising but unvalidated,
  or Rejected (the spec's §15).
