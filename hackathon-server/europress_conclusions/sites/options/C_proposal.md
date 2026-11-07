# Option C: Embedded, not separate

**Claim.** Verified Weight is not a module people must remember to open. It is **a set of additions placed where SMART users already look**. `C.html` is our own drawing of a generic SMART portal; nothing is copied from the real UI. Every addition is tagged **NEW · Verified Weight**, and one toggle hides them all, so judges see "SMART today" and "SMART + add-on".

## Users and top tasks

- **Site manager (chain):** "Is my invoice right? Was that pickup needed?" Uses the device card and report.
- **Finance / procurement:** dispute or renegotiate with evidence. Uses the report.
- **SMART Center agent:** triage and approve. Uses the work queue.
- **Operator:** sends tickets, hears about disputes first. Uses the operator API.

## Where each addition lives

1. **Device card → weight strip.** kg ± 2σ band, fill → tonnes, €/t, a badge such as "39/57 lifts agree with ticket", a device-vs-ticket chart, and **one plain-language conclusion** that links into the queue.
2. **Emptying history → "Weighed" columns.** Device kg ± band, ticket kg (tare method, loads), invoice kg, a status (*Agrees / Outside band / Invoice above both*), the likely cause and the € effect. Rows expand to the full trace. Hero row: `COL-00392-0032` (invoiced 5.08 t, ticket 4.20 t, device 4.125 t). On fixed schedules it reads *Needed / Not needed* (Proof of Fullness: `CMP-00430`, 45 of 78 not needed).
3. **Monthly report → page 3 "Verified weight".** Device, ticket and invoice tonnes per month, with an ESG-grade caveat.
4. **SMART Center → a second lane next to the fault tickets.** Eight rule-generated proposals, each with why, evidence chips, limits, reversal and Approve · Hold · Reject. Approval emits an `approval.decided` CloudEvent.
5. **Operator API → one endpoint.** `POST /v1/weight/tickets` returns a reconciliation receipt and a private tare-hygiene report (give-to-get).

## How conclusions surface

Each conclusion is **one sentence on the object it concerns** (device, lift, month or vehicle), with its evidence attached. Anything leaving the company (dispute, tare fix, schedule change) needs human approval in the SMART Center queue. This respects Tommi's point that the operator owns the weight. Weighbridge-side causes explain 77% of large gaps and the device only 3.9%, so the wording stays neutral and the operator hears first.

## Scoring per criterion

- **Demo + SMART integration (15%): strongest.** The integration pathway *is* the UI. Judges see the exact screen, column and API each feature extends, and the toggle contrasts today with tomorrow.
- **Productisation (10%): strong.** Each addition maps to a SKU and a tier (below), so "add on to their existing things" can be seen on screen.
- **Customer value (25%).** Value shows up where the work happens: the invoice line in the history, the schedule proof on the card.
- **Data-driven + traceable (20%).** Every row expands to ticket gross/tare and the invoice lines.
- **Clarity (5%).** ± on every kg, evidence chips, honest "worth €0" cases.
- **Weighing concept (25%).** Neutral. The strip shows the T0 ballpark ±; the concept itself stays in the Part 1 PDF.

## Tier mapping

| Addition | Tier |
|---|---|
| kg ± band on device card (teaser) | **Intro**, free: the hook |
| Weighed columns, report page 3, Proof of Fullness | **Insights** add-on (+€15/device/month, or gain-share in PL) |
| Ticket-calibrated agreement, operator receipt API, SMART Center approval lane, CSRD export | **Integrated** (+€25, or chain licence) |
| Drift watch → service visit | Service contract (bundled) |

## Weaknesses we admit

- **Looks less novel.** A diff on someone else's UI wows less than a dedicated "insight engine" (A).
- **We are guessing SMART's real screens.** The mock says so.
- **Conclusions are scattered.** There is no single "what should I do this week" page. The queue only partly fills that gap; A is better for an executive.
- **Bulk reconciliation is weak.** Working through 2,250 fleet gaps is a workbench job (B); our table works per device.
- **Demo choreography needed.** The value only lands if the presenter clicks device card → history row → queue approve. (~40 s, rehearse it).

**Recommended synthesis:** C as the frame, with A's one-sentence conclusions on every card, and B's workbench as the SMART Center agent's drill-down behind the queue.
