# Option B: Reconciliation workbench

**Thesis.** Tommi said customers don't trust the operator's figures. More claims won't fix distrust; showing the evidence will. In B the data is the product: one row per lift, with every conclusion auditable. Like invoice-audit tools; buyers already work in tables.

## Users and top tasks
- **Customer finance and procurement:** check invoice lines against two independent masses, dispute with evidence, and benchmark €/t.
- **Facility and ESG managers:** export verified kg per fraction and check that scheduled lifts were needed.
- **SMART Center:** triage sensor suspects and share vehicle-tare findings with the hauler first, in neutral terms.
- **Hauler (Integrated tier):** see their own vehicles' tare offsets before a customer escalates.

## IA (one screen, three layers)
1. **Pinned conclusions.** Four cards, each of which is also a filter:
   - R1, invoice ≠ both masses: 25 lines, precision 1.0.
   - 77% of large gaps are weighbridge-side; only 3.9% are the device.
   - 18 vehicles have a stored tare at least 200 kg off.
   - CMP-00430: 45 of 78 scheduled lifts were not needed.
2. **Saved views, filters and facets.**
   - Saved views: Breaches this month, R1, Stored-tare vehicles, Fixed-schedule not needed, Big gap / €0 ("says no"), Sensor suspects, Approved.
   - Filters: hauler, cause, status and tare.
   - Facet counts and € at stake recompute for the current filter.
3. **Lift grid.** Columns: device kg ±band, ticket kg, invoiced kg, gap kg (%), z, cause, € Δ, status. All columns sort.
   - **Drawer:** a three-mass band chart in neutral colours, a numbered "show the math" with an OBSERVED/ESTIMATED/HYPOTHETICAL chip per step, the document chain (ticket gross/tare, contract, invoice lines), the recommended action and "what could make this wrong".
   - **Bulk actions:** select rows → one proposal per action and counterpart → a human approves → an `approval.decided` CloudEvent goes to the SMART outbox.

## How conclusions are derived (deterministic)
- **Band:** σ is the robust SD of the gap per tare method × load type (stored, single load: 7.7%, n=3,876). Band = ±2σ. z = gap% / σ.
- **R1 rule:** the invoiced kg is outside the band against *both* the ticket and the device.
- **Cause:** taken from the engine's attribution.
- **Action:** a lookup on status × cause × contract model. A €0 gap on a per-lift contract gives NO_ACTION, which is the "says no" view.
- **LLM (P1):** only drafts dispute text, citing row IDs. The rules decide.

## Scoring vs A (insight feed) and C (embedded widgets)
| Criterion | B | Why |
|---|---|---|
| Weighing 25% | = | The ±band on every row shows what T0/T1 accuracy is good for. |
| Customer value 25% | ++ | Bulk disputes, tare fixes and schedule changes, with a € total. In A you act on one insight at a time. C has no cross-device view to act in |
| Traceable 20% | +++ | Every headline number opens to its rows and its math. A asserts first and links later. C shows numbers without the population behind them |
| Demo + SMART 15% | + | Live approve → outbox. C is hard to demo off-portal |
| Productisation 10% | + | One schema for the grid, export and API, and saved views scale |
| Clarity 5% | − | Dense. The card sentences and chips partly mitigate this |

**Against A.** A feed hides the denominator. "77% weighbridge-side" means little until you can open the 2,250 rows behind it.

**Against C.** A device widget answers "how is this machine?", but the money cuts across machines. In the sample, vehicle OP-E-V16's stored tare (−400 kg) affects 83 lifts on 56 devices. Only a cross-device grid at lift level shows that.

## Admitted weaknesses
- **It looks like work, not "wow".** The pitch needs a scripted path: card → R1 view → hero `COL-00392-0032` drawer → approve.
- **Weaker readability for end customers.** Fix: borrow A's sentences for the cards, and use C's widgets as deep links into the grid.
- **Ugly rows.** Tiny loads include negative device kg. The default sort pushes them down.
- **Sample, not full data.** The prototype loads 4.6k of 9,062 pairs:. Production needs server-side paging.

## SMART tier fit
| Tier | What it gets |
|---|---|
| Intro | Cards only (monthly kg band) |
| Insights | Grid with device vs ticket, causes and Proof of Fullness |
| Integrated | Invoiced-kg column, bulk approval, operator ticket API, shared hauler view, outbox events |

**Recommendation:** B as the spine, with A's sentences as the pinned cards and C's widgets as entry points.
