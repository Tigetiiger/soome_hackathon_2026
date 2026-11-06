# Option A: Conclusions-first insight feed

Prototype: `A.html` (`#feed`, `#f/P-001`, `#rules`). Data is SYNTHETIC and tariffs are hypothetical.

## Who uses it, and for what
- **Users:**
  - **Primary:** a facility or sustainability manager at a chain or property owner, who gives this about 3 minutes a week.
  - **Secondary:** customer finance (receives drafts), SMART Center (reviews them), the operator (gets hygiene findings privately, first).
- **Top tasks:**
  1. "Is anything wrong with my bills or schedule?" Answered by the ranked feed.
  2. "Do I believe it?" Answered by inline **Show the math**, evidence rows, the band and the limits.
  3. "Act." **Approve, edit or dismiss** a drafted action, which emits `approval.decided` to the outbox.
  4. "Prove it." Trace lift → ticket → contract → invoice line → €.

## IA
One new SMART nav entry, **Verified Weight**, next to Devices, Fill levels, Emptying calls and Reports.

- **Feed (landing):**
  - Ranked cards: conclusion, € p10–p90, provenance chips, confidence, recipient, CTA.
  - A **"Checked and dismissed"** section with the 335 kg gap worth €0, which proves the engine doesn't cry wolf.
- **Detail:**
  - Visual proof, the math, evidence rows, "what could make this wrong", and an action drawer with reversal path and event JSON.
- **Rules & thresholds:** every rule with its trigger, threshold and back-test.
- **Links to existing SMART pages:** device pages deep-link into the feed, filtered to that device. That is C's strength, used as an entry point.

## How conclusions are generated
Rules decide. The LLM only words the drafts, with row citations.

| Rule | Fires when |
|---|---|
| **R1** | Device and ticket agree, and \|invoice − ticket\| > max(3σ, 100 kg). Precision 25/25, recall 66%. |
| **R2** | Stored-tare offset ≥ 200 kg, stable in both halves of the window (18 of 70 vehicles). |
| **R3** | Proof-of-Fullness mass rule. Fixed schedules: precision 71%, recall 96%. |
| **R4** | €/t above the peer median. |
| **R5** | CUSUM ±6%. It catches 7 of 10 episodes, a median 33 days before today's fix. |
| **R6** | A gap with €0 impact. Logged only. |
| **R7** | An operator shares < 10% of tickets. |

- **Rank:** |p50 €| × confidence. Confidence is 1.0 when two independent masses agree, 0.7 when an input is simulated or a benchmark.
- **Provenance:** every number carries a chip: OBSERVED, ESTIMATED, SIMULATED or HYPOTHETICAL.
- **Negative result:** density-based contamination detection has 0.7% precision, so it generates no finding.

## Scoring
| Criterion | A | Why |
|---|---|---|
| Weighing concept 25% | Medium | ± bands on every card, and the rules page shows what accuracy each rule needs. The concept itself still lives in the Part 1 PDF. |
| Customer value 25% | **Strongest** | "So what?" in one sentence, plus € and an action. Tommi's "the beef". |
| Traceable analysis 20% | Strong | Show the math, evidence rows, back-tests and the negative result. One click deeper than B. |
| Demo + SMART 15% | Strong | A 3-click story: feed → P-001 proof → approve → event. Reuses SMART nav and approval flow. |
| Productisation 10% | Strong | The finding is the unit sold. Locked cards are the upsell. |
| Clarity 5% | Strong | One sentence, a ± band and a chip per card. |

## Weaknesses I admit
1. **The rank mixes units.** One-off, 56-day and annual values sit in one list. The hero invoice error (€121) ranks 5th behind a simulated €3,750. Fix: annualise, or put "actionable now" first.
2. **It hides the long tail.** 2,250 large gaps become 8 cards, and auditors want B's table. Mitigation: each card links to a filtered lift table, so B becomes the drill-down.
3. **It is only as good as the rules.** Guardrails: back-tests, dismiss-with-reason.
4. **It is less in-context than C.** It needs C-style badges on device pages.
5. **With 8 cards it can look curated.** Show the counts behind each rule, for example 25 R1 flags and 18 R2 vehicles.

## SMART tiers
| Tier | What the feed shows |
|---|---|
| **Intro** | One teaser finding and a count of the locked ones. |
| **Insights** (+€15/device/month) | R2–R6 and Proof of Fullness. |
| **Integrated** (+€25) | R1 invoice reconciliation, approvals and the operator API. |
| **T2 load cells** | Shown as a "measured" confidence upgrade on cards, not as a new screen. |

Prices are hypothetical (see BUSINESS_PLAN.md).

**Verdict:** A is the landing page, B is its drill-down and C provides the entry points.
