# BUILD PLAN: "SMART Verified Weight" (working title)

Europress × Since AI Hackathon 2026 · team of 4 · **hard deadline Sun 8 Nov 10:00 (local)**.

This plan merges the agent lenses in `agents/`: build-architecture, data-value, brand-dashboard and creative-ideas. It also draws on the red-team and weighing-engineer docs in `../soome_hackathon_2026/docs/agents/`. Detailed engine maths, the API table, event schemas and the licence table are in `agents/build-architecture.md`. This file holds the decisions, scope, schedule and who does what.

---

## 0. Transcript anchors: what Tommi said, and how the build obeys it

| Tommi said (kick-off) | Build consequence |
|---|---|
| "The second part … is the beef: what would be the business possibilities?" | Most screens are Part 2 value. Part 1 is one concept PDF plus one simulator chart. |
| "Cheapest wins"; customers "not willing to pay almost anything extra"; no new sensors on the BOM | T0 virtual scale with €0 BOM is the default. Hardware (T2 load cells) appears only as a premium tier. |
| "Doesn't need to be by the kilo … ballpark is enough" | Every weight shows a ± band. We show *what each accuracy level is good enough for*. |
| SMART already makes sure containers are as full as possible | **No pickup-timing optimiser.** The only pickup screen is *Proof of Fullness*, which gives tonnage evidence for fixed schedules (Poland). |
| The waste operator owns the weight; customers distrust the figures; "who owns the data is the holy grail" | Hero flow: device vs ticket vs invoice reconciliation, with an operator-neutral cause attribution. |
| Europress won't operate trucks; it wants to be a technology and service company | Everything is SMART software events, an API and recommendations. No logistics. |
| "Recognise material that doesn't fit" (stated second problem) | We show it honestly. The density proxy fails on this data (~1% precision), so the screen says *needs pressure-curve shape: future firmware*. That gives a roadmap slide, not a fake feature. |
| "Real-time visibility" and readability for the end customer | Plain-language hero sentence on each screen, FI/EN microcopy. |
| "Use AI … superpowers" and show how you used it | Rules decide, Claude drafts the explanations. There is an honest AI-vs-rules bench page, and the pitch has a slide on how we used AI to build the product. |
| Poland is a key future market and still on fixed schedules | Proof of Fullness hero device `CMP-00430`, plus a P2 Polish BDO waste-card mass export. |

## 1. What we are building

**One sentence:** a SMART add-on that gives every compactor an **independent weight estimate with an uncertainty band**. It reconciles each lift against the weighbridge ticket and the invoice, explains *why* they differ in operator-neutral terms, and turns that into **human-approved recommended actions**. On fixed schedules it also proves which pickups were not needed ("Proof of Fullness").

| Criterion | Weight | Where we score |
|---|---|---|
| Weighing concept | 25% | Part 1 PDF: tiered T0 virtual scale (€0 BOM) → T1 ticket-calibrated → T2 load-cell platform (an existing Europress product). Error budget, calibration, validation protocol, simulator chart |
| Customer/business value | 25% | Invoice assurance, Proof of Fullness (largest € in the data), €/t contract benchmark, reporting pack |
| Data-driven value + traceable calcs | 20% | Every number traced: lift → ticket → contract version → invoice line → €/t. Cause attribution. Official benchmark scores |
| Demo + SMART integration | 15% | One-command local app, CloudEvents outbox, operator ticket-ingest API, Intro/Insights/Integrated tier map |
| Productisation | 10% | Add-on pricing per SMART tier (BUSINESS_PLAN.md) |
| Clarity/uncertainty | 5% | Evidence chip on every number (OBSERVED / ESTIMATED / SIMULATED / HYPOTHETICAL), negative results shown |

## 2. Scope (decided)

**P0, must ship**
1. **Fleet overview:** agreement distribution, € at stake (labelled hypothetical), tier counts.
2. **Lift trace:** one number traced end to end. Hero `INV-00392-202512-L045`: invoiced 5.08 t vs ticket 4.20 t vs device 4.125 t, €111.61.
3. **Cause attribution:** device vs vehicle stored tare vs side waste vs combined load.
   - Of the large gaps, only 3.9% are sensor faults. Weighbridge-side causes account for 77%.
   - Hero vehicles `OP-E-V06` / `OP-A-V12` have stored tares about 360 kg and 285 kg off, in opposite directions.
4. **Proof of Fullness** (fixed and hybrid schedules): 30–32% of lifts are unjustified, worth about €2.5–2.7k per device-year [synthetic data, hypothetical prices]. Hero `CMP-00430`: 45 of 78 lifts unjustified.
5. **Recommendations inbox + approval drawer.** Each proposal has cited evidence rows, an expected value at p10/p50/p90, and a reversal path. Approving it emits an `approval.decided` event into the outbox.
6. **Part 1 simulator chart:** error vs number of calibration anchors, watermarked SIMULATED.

**P1, if green at M2**
- Drift (CUSUM) device page
- Operator-neutral scorecard ("shared with operator first")
- AI-vs-rules bench page
- LLM drafts with row citations (cached)

**P2, only after M3**
- Anchor-scheduler slider (where calibration visits pay most)
- Polish BDO mass export
- FI/EN toggle

**OUT, do not claim**
- Pickup routing or timing
- Map tiles
- Real brand names
- "Validated accuracy"
- CO₂ flight equivalents
- Contamination detection as a working feature

## 2b. Taken from the parallel Sonnet session (`agents/comparison-sonnet-vs-ours.md`)

- **`../soome_hackathon_2026/docs/agents/mock_dashboard.html`**: the frontend's visual template and day-one fallback. Reuse these parts of it:
  - the permanent **SYNTHETIC DATA** banner
  - the provenance badges
  - a **"What could make this wrong"** panel on every screen
  - the three-source band chart (device, ticket, invoice)
  - the approve → draft → audit-log flow
- **Neutral colours for the device, ticket and invoice series.** Do *not* draw the invoice or operator line in red, because that implies blame.
- **A "says no" case.** Show one real 335 kg gap that is worth €0 on a per-lift contract. That proves the engine doesn't cry wolf.
- **Honest accuracy copy:**
  - T0 virtual scale: ±12–15% per lift (1σ) and ±5–6% on monthly totals.
  - Weighbridge reference itself: only ±40–80 kg (OIML R76).
  - Validation design: Kalman recalibration, conformal intervals, leave-one-machine-out testing, Bland-Altman, and a "how many tickets" ablation. All from the Sonnet `science-researcher.md` §3–4.

## 3. Stack (architect's decision, chosen for demo reliability)

| Layer | Choice | Why |
|---|---|---|
| Data | DuckDB marts built once from the competition parquet via `open_dataset(as_of=…)` | Fast, leak-free, read-only serving |
| Engine | Pure Python (numpy, pandas, scipy) | Deterministic, unit-testable, explainable |
| API | FastAPI + Pydantic v2, which also serves the built SPA | **One process on port 8000, works offline** |
| Frontend | **Vite + React + TS + Tailwind + shadcn/ui + Recharts + TanStack Query** | Polished, no SSR hydration pitfalls. Streamlit is Plan B if screen ① isn't up by M2 |
| LLM (optional) | `claude-haiku-5-5` for bulk drafts, `claude-sonnet-5-5` for the 5 hero drafts | See below |
| Env | Our own `.venv` + `requirements.txt`; npm + lockfile | The machine has no pnpm, uv or docker. Probed: Node 26, Python 3.13, Make 4.4 |

Engine modules: reconcile · attribution · drift · proof_of_fullness · invoice · actions · bench.

LLM details:
- Drafts use structured output and pass a guard that rejects uncited rows, unsupported numbers and blame wording.
- Drafts are cached and committed, with a template fallback.
- Rules **decide**; AI only **drafts**.

**API key: undecided.** Build with `LLM_MODE=cached|template` from hour one. If a key appears, run `make drafts` once and commit the result. The demo never needs the network.

## 4. Brand (verified from the epsmart.fi theme.css)

- Navy `#000d61`, ice `#e0f1f5`, mint wash `#ddf8ee`, greys `#f7f9fc / #ecf0f6 / #c9d1de / #323d4e`.
- **Primary CTA = mint `#54dea9` pill with navy text.** Pink `#ff2962` is an accent only. For pink text use `#d1003f` (AA).
- Severity colour is autumn `#b95041`. Reject buttons are neutral, never red.
- Sentence-case headings, as on epsmart. Caps only on buttons and tags.
- Fonts:
  - **Archivo** for titles. It is a free stand-in for the commercial Loos Wide; do not ship Loos.
  - Open Sans for body text.
  - Source Sans 3 for UI.
  - All are OFL, loaded via `@fontsource`.
- Radius 1rem for cards, 1.5rem for blocks, pill buttons.
- Every screen has **one hero sentence**. Every number gets a ± band and an evidence chip.
- Tokens, the Tailwind snippet, the contrast table, 6 wireframes and microcopy are in `agents/brand-dashboard.md`.

## 5. Repo and commands

```
verified-weight/
├─ Makefile  README.md  params.yaml  requirements.txt  LICENSES.md
├─ engine/  build_marts.py reconcile.py attribution.py drift.py proof_of_fullness.py invoice.py actions.py bench.py
├─ api/     main.py models.py routes/{fleet,lifts,attribution,pof,proposals,ingest,events,bench}.py
├─ llm/     drafter.py guard.py prompts/ templates/        cache/llm/*.json (committed)
├─ sim/     virtual_scale_sim.py        (Part 1, SIMULATED)
├─ web/     Vite app (pages, components, theme, api/types.gen.ts)
├─ tests/   reconcile, attribution, drift, proposals, api_contract, llm_guard, sim
├─ docs/    part1_weighing_concept.md business_case.md assumptions_untested.md integration.md
└─ demo/    script.md walkthrough.mp4
```

Commands: `make setup` · `make marts` · **`make demo`** (http://localhost:8000) · `make dev` · `make test` · `make drafts` (needs a key) · `make licences`

**Reuse, don't rewrite:**
- `../soome_hackathon_2026/analysis/common.py::lifts()` and the `01_*` scripts.
- The data-value scripts in `analysis/` (10–61), which already compute the hero traces.

**Do not import** the dataset's `baselines/`. Their licence is unstated, so re-implement the logic.

## 6. Schedule (local time; H0 = Fri ~22:00; submit by **Sun 09:30**, leaving a 30-minute buffer)

Owners: **D** = Data/ML · **B** = Backend/LLM · **F** = Frontend · **P** = Business/Pitch, who also owns the Part 1 PDF.

| Window | D | B | F | P |
|---|---|---|---|---|
| **Fri 22:00–02:00** | Repo, `make setup`, port `lifts()`; marts `lift_pair`, `lift_trace`, `vehicle_effect` | Pydantic models + proposal/event schema (**contract freeze v0 at 23:00**), fixtures, fleet + trace routes | Vite + shadcn scaffold, brand theme, shell, screens ① ② on fixtures | Submission checklist, deck skeleton, Part 1 concept draft from weighing-engineer.md |
| **M1 02:00** | **`make demo` shows the fleet overview and one real traced lift** | | | |
| 02:00–08:00 | Sleep, staggered so someone is up by 07:30 | | | |
| **Sat 08:00–14:00** | reconcile, attribution (+ leave-month-out stability), PoF mart, CUSUM, eval vs labels | actions.py, decision POST, events outbox, ingest endpoint | Screens ③ attribution, ④ PoF, ⑤ inbox + drawer | BUSINESS_PLAN → deck, params.yaml prices + sensitivity, **ask Tommi the open questions** |
| **M2 14:00** | **Full loop: proposal → approve → event in the outbox; official scores in bench. Go/no-go on Streamlit Plan B** | | | |
| Sat 14:00–22:00 | Simulator, bench numbers, AI-vs-rules bake-off | LLM drafter + guard + cache (or templates) | Drift page, scorecard, bench page, evidence chips, polish | Deck v1, licence table, assumptions/untested, demo script, Part 1 PDF v1 |
| **M3 22:00** | **Feature complete; rehearsal #1; first recording** | | | |
| Sat 22:00–02:00 | Freeze numbers into `bench.json`, tests green | Offline test (Wi-Fi off), README and setup notes | Polish; P2 only if green | Deck v2 with frozen numbers; **claims audit against the evidence tags** |
| **M4 FREEZE 02:00** | **Tag v1.0, run the licence scan, record the final walkthrough** | | | |
| 02:00–06:30 | Sleep in pairs | | | |
| **Sun 06:30–09:30** | Fixes only | Package repo + setup notes | Rehearse ×3 | Package and **submit by 09:30**: (1) Part 1 PDF (2) demo + recording (3) business case (4) licences (5) assumptions |

## 7. Demo script (3 min)

| Time | Beat |
|---|---|
| 0:00–0:20 | "The operator holds the weight, and customers can't check their invoices. SMART already gets containers full; we add the missing number." |
| 0:20–0:50 | Part 1: the T0/T1/T2 ladder, the error budget and the SIMULATED error-vs-anchors chart. "Start free, add accuracy only where it pays." |
| 0:50–1:20 | ② One lift traced end to end: invoice 5.08 t vs ticket 4.20 t vs device 4.125 t. |
| 1:20–1:50 | ③ "Most big gaps come from the weighbridge's stored vehicle tare, not the sensor and not intent." The FIX_VEHICLE_TARE proposal goes **to the operator first**. |
| 1:50–2:15 | ④ Proof of Fullness: a fixed-schedule site where 45 of 78 lifts weren't needed. This is the Poland pitch. |
| 2:15–2:40 | ⑤ Open a proposal → cited draft → **Approve** → the `approval.decided` event appears (SMART integration). |
| 2:40–3:00 | Business: add-ons on the existing SMART tiers, priced from value. Limits stated: synthetic data, no pressure curves, hypothetical prices. |

Backup: the recorded walkthrough plus screenshots in the deck.

## 8. Claude Code skills to use (all installed)

| Who / when | Skill | Use for |
|---|---|---|
| All, at kick-off | `ecc:orch-build-mvp` or `ecc:prp-plan` | Turn this plan into tracked tasks per owner |
| D | `ecc:python-testing`, `ecc:tdd-workflow` | Engine unit tests (planted vehicle bias, CUSUM step, z-tier boundaries) |
| D, F | `dataviz` | Read before any chart (bands, waterfalls, error-vs-anchors) |
| B | `ecc:fastapi-patterns`, `ecc:api-design` | Routes, the Pydantic contract, the ingest endpoint |
| B | `claude-api` | LLM drafter: model IDs, structured output, prompt caching |
| F | `ecc:frontend-design-direction`, `impeccable:impeccable`, `ecc:design-system` | Apply the Europress tokens, polish the screens |
| F | `ecc:react-patterns`, `ecc:vite-patterns`, `ecc:react-build` (if the build breaks) | Frontend implementation |
| F, B | `run`, `ecc:browser-qa` / `ecc:e2e-testing` | Drive the app, click-through check before each milestone |
| Anyone, after code | `code-review`, `simplify`, `ecc:python-review` / `ecc:react-review` | Review before M2, M3 and M4 |
| P | `anthropic-skills:pdf` / `anthropic-skills:docx` | Part 1 illustrated concept PDF |
| P | `anthropic-skills:pptx` or `ecc:frontend-slides` | Pitch deck |
| P | `ecc:ui-demo` / `ecc:video-editing` | Recorded walkthrough |
| P | `ecc:market-research`, `product-management:competitive-brief` | Business-plan gaps |
| Freeze | `ecc:verification-loop` | Final checks |

## 9. Risks and mitigation

| Risk | Mitigation |
|---|---|
| No API key | Template mode is first-class. Label it "template" and never fake an LLM |
| The vehicle-tare effect is a simulator artefact | Leave-month-out stability check by M2. If it is unstable, call it a hypothesis |
| Frontend slips | P0 only, with the Streamlit Plan B decision at M2 |
| Over-claiming | P runs a claims audit at 01:00 on Sunday; every number carries an evidence chip |
| Licence surprise | Scan at freeze; no baseline code copied; ask the organisers about the dataset licence |
| Wi-Fi or demo failure | Offline single process, plus the recording |

## 10. Open questions (ask Tommi or the organisers on Saturday morning)

1. Is per-stroke pressure archived, and at what sampling rate (Hz)? Can we see one or two example curves (he offered on Discord)?
2. What does SMART's real event/API surface look like? Can we use portal screenshots?
3. What are the licence and IP terms for the dataset and SDK in submitted code?
4. Is judging live or recorded, and how long is the slot?
5. Who funds the Claude API key?
