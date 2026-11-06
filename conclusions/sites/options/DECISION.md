# Panel design decision (after the A/B/C debate)

All three debaters converged on a hybrid. Their inputs are in `A_*`, `B_*` and `C_*` (proposal, critique, prototype).

## The hybrid "H"

1. **Frame: a thin SMART portal shell** (from C).
   - Generic nav of our own drawing: Fleet · Devices · Reports · SMART Center · **Verified Weight (NEW)**.
   - Marked "concept mock, not the real SMART UI".
   - Do *not* redraw Europress's whole UI. Two hooks show the add-on lives inside SMART:
     - the weight strip on the device card;
     - the "Weighed" columns in pickup history.
2. **Landing: the Verified Weight panel = conclusions feed** (from A), with these fixes:
   - Rank **observed** findings first, then estimated, then simulated. Never put a simulated € at the top.
   - Put every € on one unit (€/year, annualised, with the basis shown), so no headline mixes units.
   - Each card shows the conclusion, the number ± band, an evidence chip, "show the math", the suggested action, and a "how many rows" count.
   - Keep the "checked and dismissed" card (the 335 kg gap worth €0).
3. **Drill-down: every card opens the reconciliation grid pre-filtered to its rows** (from B).
   - Grid columns: device ± band | ticket | invoiced | gap | z | cause | status.
   - Each row opens a lift drawer with the full document chain (hero COL-00392-0032 / INV-00392-202512-L045).
   - Cross-device views (vehicle OP-E-V16 / OP-E-V06 stored tare across many devices) live here.
4. **Single exit: approval in a SMART Center lane** (C + A).
   - Approve / hold / reject, with a reason.
   - Approving emits a `fi.europress.smart.approval.decided.v1` event to the outbox. The operator API receipt is shown.
5. **Method & limits page:** the Part 1 weighing concept, the reference-data note, licences and what is untested.

## Cross-cutting rules

- Device, ticket and invoice series use **neutral colours**. Never red for the ticket or operator.
- Engine rules (R1…R7) and thresholds come from **one source**. B's R1 currently differs from the engine's: reconcile them.
- SYNTHETIC DATA banner. Plain-language tooltips for jargon.
- Visual theme from the Fable designer (`../design/theme.css`).

## Open choice for the team

Is the default landing page the **Verified Weight panel** (recommended), or the **device card with the strip**, where the user discovers the panel from a familiar screen?
