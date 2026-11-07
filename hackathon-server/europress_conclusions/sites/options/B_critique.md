# B critiques A and C

## A: conclusions-first feed

**Strongest points**
1. **It gives one sentence, a € figure and a next step.** That is Tommi's "beef", and it is the fastest of the three to read in a 3-minute demo.
2. **It shows the engine saying no.** "Checked and dismissed" (335 kg, €0) plus the rules/back-test page are the most credible honesty devices on offer.

**Biggest flaws**
1. **The ranking undermines trust.** The #1 card is a **SIMULATED** €3,750, while the only fully OBSERVED invoice error (€121) ranks 5th. The "€8,469 (mixed units)" headline adds up incompatible units.
2. **The denominator is hidden.** 2,250 gaps, 25 R1 lines and 18 vehicles become 7 cards, and "Open evidence" shows 3 rows. That is weak on traceability (20%) and on "data displayed".
3. **It is a separate destination, not an addition to SMART.**

## C: embedded additions

**Strongest points**
1. **Best fit for "an addition to SMART".** The NEW-tag toggle (today vs with the add-on) is the best demo device for integration (15%) and productisation (10%).
2. **Conclusions sit on the object they concern.** The device strip combines a kg ± band, an agreement badge, a chart and one linked sentence. It is literally "a panel" of data plus conclusion.

**Biggest flaws**
1. **No cross-device view.** Vehicle OP-E-V16's stored tare affects 83 lifts on 56 devices, and a device page cannot show that.
2. **It breaks the neutrality rule.** "Ticket outside band" is drawn in **red**, which implies the hauler is to blame.
3. **It guesses SMART's real screens and scatters the value.** There is no "what to do this week" view.

## What I'd steal

- **From A:** the conclusion cards with p10–p90 and a recipient, the "says no" section, and the rules page.
- **From C:** the NEW toggle, the device weight strip, the "Weighed" history columns, and the operator receipt API.
- **From B (honest view):** it should be the drill-down, not the landing page. The full grid at rest is too dense for a pitch.

## Final recommendation: a hybrid "Verified Weight panel"

1. **Entry points:** C's device strip and history columns. The demo opens on "SMART today", then flips the toggle.
2. **Panel top:** 4–6 A-style cards, ranked by "actionable now, OBSERVED first", with € in one unit (per year). SIMULATED cards are separated out.
3. **Every card shows its count** and opens the B grid pre-filtered (saved views: R1, stored tare, not needed, says no). The lift drawer shows the math and the document chain.
4. **One action path:** single or bulk approve → proposals grouped by counterpart → `approval.decided` event in the outbox. The operator is told first.
5. **Neutral series colours and provenance chips everywhere:** device blue, ticket navy, invoice purple, never red. Keep A's rules and negative-results page for clarity.
