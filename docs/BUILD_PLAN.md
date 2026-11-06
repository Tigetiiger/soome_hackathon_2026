# Build plan — SMART Verified Weight (48 h)

_Companion to `BUSINESS_PLAN.md`. Draft 1, 2026-11-06. H+0 = start of build; the real submission time is **unknown, please confirm** (all hours below are relative)._

**Goal:** a working, honest demo on the Since AI synthetic pack that shows (1) a weighing concept with an accuracy ladder and a validation protocol (Part 1), (2) traceable value from weight (Part 2), (3) a SMART integration path. Scored on: 25% weighing concept · 25% customer value · 20% data-driven value · 15% working demo + SMART path · 10% productisation · 5% clarity/limits.

**Principles:** advice only, human approves · every number tagged observed / estimated / simulated / hypothetical · neutral towards operators · no tuning on the test period · never impute a missing mass (EUR/t stays NULL with a reason).

---

## 1. Scope

| Must (MVP, demo-critical) | Should (if on schedule at H+24) | Stretch (only if on schedule at H+30) | Cut |
|---|---|---|---|
| M1 virtual-scale estimator T0/T1 with intervals and drift guard | M6 cause-adjusted neutral scorecard | signed "lift passport" evidence-pack export (hash chain) | pickup optimisation / routing |
| M2 lift reconciliation + cause attribution (rules) | M7 value-vs-σ sensitivity page | LLM-worded evidence summary (Claude API, templated fallback) | map, CO₂ flights hero |
| M3 EUR/t with mass provenance | GBM ranker for cause (after rules) | monthly PDF report | fake chat assistant |
| M4 S40 fill-vs-mass order guard | | | marketplace, full service |
| M5 action recommender (dispute / request data / renegotiate / tender) + evidence pack + approval queue | | | moisture/contamination detection |
| M8 dashboard (4 screens) · M9 mock SMART API | | | any "TrueLoad" naming |

## 2. Architecture

```
Since AI pack (parquet/CSV, read-only)
   │  DuckDB views, telemetry dedup, as_of masking
   ▼
vw/ (Python package)
   io → anchors → scale (T0/T1, intervals, drift)
                 → reconcile (pairing, rules, cause) → scorecard
                 → eurt (wraps europress_data.economics)
                 → guard (S40)
                 → actions (wraps baselines B6 + evidence packs)
                 → sensitivity (σ sweep)
   │  export.py → precomputed JSON (seeded, versioned)
   ▼
web/ (Vite + React + TS + Tailwind + shadcn/ui + Recharts)   ← reads JSON, no backend needed for the demo
api/ (FastAPI) = thin mock of the SMART integration (/estimate, /evidence-pack, /actions) over the same JSON
```

**Why precomputed JSON:** demo reliability offline (product-designer's recommendation); keep a static build and a screen recording as backup. FastAPI exists to *show the integration pathway*, not to carry the demo.

Repo layout (new repo or folder `verified-weight/`): `vw/`, `web/`, `api/`, `tests/`, `analysis/` (already exists: scripts 01–10 with seed 20261106), `docs/`, `requirements.txt`, `Makefile` (`make data`, `make test`, `make web`, `make demo`). Dataset stays outside the repo (`/home/hackathon/europress_data/...`), referenced by an env var `VW_DATA`.

## 3. Modules, acceptance tests and owners

Suggested roles for four people (adjust once we know the team): **A Data/ML**, **B Backend/pipeline**, **C Frontend**, **D Business/pitch/docs**.

| ID | Module | Owner | What it does | Acceptance test (regression numbers from our analysis) |
|---|---|---|---|---|
| M0 | Setup | B | durable venv, `requirements.txt`, load pack with `europress_data.sdk.open_dataset`, run `analysis/run_all.sh` | reproduces baseline scores below |
| M1 | Virtual scale | A | T0: fill×volume×density table. T1: per-device gain from filtered anchors (SINGLE_LOAD, WEIGHED tare, no side waste), Student-t update, CUSUM drift flag, conformal/quantile interval. `pressure_sim.py`: synthetic stroke generator **only to unit-test the fitting code**, labelled everywhere | fill-only with 3 anchors: median abs. error ≈ 9.4% and ≈ 52% of lifts within ±10% (weighing agent's numbers); 80% interval covers 75–85% of lifts; never worse than T0 |
| M2 | Reconciliation | A | pair device mass with ticket via `operator_job_ref`; rule R1 `|diff|>100 kg and >10%`, single load, no side-waste flag; cause attribution: side waste / stale stored tare (per vehicle) / combined load / device drift | rule F1 ≈ 0.887 on actionable weight discrepancies (train <1 Jun, validate Jun–Jul); stored-tare concentration: 10 of 70 vehicles ≈ 79% of tare errors |
| M3 | EUR/t | B | call `economics.py`; mass source order ticket → invoice → device; flag `observed`/`estimated`; NULL with reason otherwise | A-task scores match B1 (net exact 0.964, EUR/t coverage 0.997); device fills ≈ 95.5% of today's NULL lifts |
| M4 | Order guard S40 | A | `kg-per-fill-pp` per device from first 120 d; alert at order time if `fill≥80 & mass-implied fill<50` | precision ≈ 0.96, recall ≈ 0.51 at order time; fires on ≈ 2.2% of fill-triggered orders |
| M5 | Actions + evidence | B | wrap B6 valuation with mass sources; build an evidence pack per lift/contract (device record, ticket, invoice line, rule fired, interval, caveats); approval queue writes an append-only action log; **no external sending** | C2 regret reproduces B6 (€240.1, captured 0.774) with all mass sources; with device-only mass ≈ 0.73; at σ=10% ≈ 0.743 |
| M6 | Neutral scorecard | A/B | cause-adjusted weight bias per operator-region-month beside punctuality, missed, sharing, billing accuracy | bias MAE 1.2–1.6 pp vs 5.5 pp naive; false flag rate ≈ 0.9% vs 74% |
| M7 | Sensitivity | A | σ sweep 0.5–10%: EUR/t within ±10%, overbilling detection, tare/drift recall, S40 recall, C2 captured | reproduces the analyst's σ table (e.g. +10% overbilling detected 85.1% at σ=3%, 15.3% at σ=10%) |
| M8 | Dashboard | C | screens below, design tokens from `docs/agents/product-designer.md`, reference `docs/agents/mock_dashboard.html` | no console errors; works offline; every figure shows a provenance badge and unit; WCAG AA contrast |
| M9 | Mock SMART API | B | `/estimate`, `/evidence-pack/{lift}`, `/actions` (+ approve), OpenAPI schema | schema validates; same JSON as UI |
| M10 | Part 1 concept pack | D (+A) | 2–3 page illustrated weighing concept: COMBI/DUO sketch with sensor placement, ladder, BOM table, error budget, calibration flow, validation protocol with pre-registered acceptance (A1–A6) and falsification gates | covers all items in submission format (1) |
| M11 | Business case | D | re-run strategist's model at €8/device-month (and low/base/high), sensitivity grid, tags | numbers in slides = numbers in `BUSINESS_PLAN.md` |
| M12 | Compliance | D | third-party/licence table, assumptions register, "what remains untested" | complete, versions pinned at freeze |

### Dashboard screens (MVP = 1–4)
1. **Invoice check (hero):** lift list; device weight vs ticket vs invoice with an interval band; cause chips; recommended action with value and an Approve / Reject; audit log. Opener case: synthetic CTR-00038, 24 Aug, two phantom lifts, four lines, €1,215.20 (device status, not weight), then a 335 kg gap with "no action, €0".
2. **Weight & EUR/t:** tonnes per stream, EUR/t with mass-source badge, share of lifts with no verifiable mass today (26%) and what the device fills.
3. **Fleet & sensor trust:** per-device drift/calibration status, machine health, S40 order-guard alerts.
4. **Operator scorecard (neutral language):** cause-adjusted bias, punctuality, sharing, billing accuracy; evidence, not blame.
5. _(should)_ **Accuracy ↔ value:** σ-sweep chart linking Part 1 to Part 2. 6. _(stretch)_ Monthly report. 7. _(stretch)_ Lift passport export.

SMART look (from the live epsmart.fi theme, per the designer): navy `#000d61`, pink-red `#ff2962` as accent only (white on it fails AA, use navy text or a darker crimson), mint `#54dea9` pill primary button, tints `#fff0f4` `#e0f1f5` `#ddf8ee`; Open Sans / Source Sans 3 / Montserrat (free substitute for Loos Wide); text wordmark placeholder, no copied logos or photos; a visible **SYNTHETIC DATA** banner.

## 4. Data handling rules (from the pack's docs)
- `telemetry_hourly` is an ingest log: dedupe by `message_id`, order by `measured_at`, respect `quality_flag` and `sensor_status`; `mass_kg` can be NULL, negative, drifted or spiked.
- Join collection → ticket only through `operator_job_ref`; invoice lines may have job-ref typos (fall back to contract + service date).
- Use `as_of` views for any decision case; use only dev/validation labels; test labels are hidden.
- Local date logic is Europe/Helsinki; tariffs come from the contract version valid on the local service date.
- Never treat a difference as the operator's fault by default: side waste, combined loads, stale tare and sensor drift cause differences.

## 5. Timeline (relative hours)

| Window | A Data/ML | B Backend | C Frontend | D Business |
|---|---|---|---|---|
| **H0–2** | read pack docs, run baselines | M0 env, loaders, repo, Makefile | scaffold Vite/shadcn, tokens | confirm questions to Tommi, outline M10, licence list started |
| **H2–8** | M1 T0 + anchors; M2 rule R1 | M3 EUR/t with provenance; export v0 | shell + screen 1 on sample JSON | M10 draft, M11 params |
| **H8–16** | M1 T1 gain/CUSUM/intervals; cause attribution | M5 evidence pack + queue; M9 mock API | screens 2–3 | M10 diagrams, BOM table |
| **H16–24** | M4 guard; M7 sweep | M6 scorecard; JSON v1 frozen shape | screen 4; provenance badges | M11 numbers, pitch storyline v1 |
| **H24–30** | GBM ranker (should); tests | integration, regression suite green | polish, offline build | slides + 3-min script |
| **H30–36** | tune only on validation; write limits | stretch (lift passport) _only if green_ | screen 5; recorded walkthrough | freeze numbers |
| **H36 FREEZE** | no new features | | | |
| **H36–44** | bug fixes, final reproducibility run | README, setup notes, pinned requirements | fixes, a11y pass | submission pack: concept PDF, demo link/recording, business case, licence table |
| **H44–48** | buffer: full rehearsal ×3 on the demo machine, backup recording uploaded | | | |

## 6. Test and quality plan
- **Regression suite** pins the numbers in the acceptance column above (tolerance ±1 pp) with seed 20261106; `make test` must pass before any numbers go on a slide.
- **Unit tests:** anchor filter, Student-t update, CUSUM, interval coverage, tag/provenance presence (a lint fails if a displayed figure lacks a tag).
- **Leakage check:** no label column enters features; time-split train/validate; hold the test period untouched.
- **Honesty checks:** UI never says "validated accuracy"; Part 1 numbers are labelled [est]; the synthetic pressure generator is flagged "unit-test only".
- **Accessibility:** contrast checked per token table; keyboard operable approve flow.

## 7. AI approach (what Tommi asked to see)
- **Rules vs ML, measured:** rules F1 0.887, GBM 0.926 with vehicle/device history, isolation forest 0.098. Position: rules flag and explain, GBM ranks cause later, an LLM only words the evidence pack, a human approves.
- **Uncertainty first-class:** conformal intervals on every mass; "estimated" vs "observed" badges.
- **AI used in the build:** agentic research and analysis (this repo's `docs/agents/`), documented in the submission as process, not as a feature.
- **Optional LLM:** Claude API for wording only, behind one `summarise(evidence_pack)` interface with a deterministic template fallback; never decides, never sends.

## 8. Third-party components (confirm versions at freeze)
| Component | Licence | Commercial use |
|---|---|---|
| pandas, NumPy, SciPy, scikit-learn | BSD-3-Clause | yes |
| LightGBM, DuckDB, PyYAML | MIT | yes |
| pyarrow | Apache-2.0 | yes |
| matplotlib | PSF/BSD-style | yes |
| FastAPI | MIT; Uvicorn BSD-3 | yes |
| React, Vite, Tailwind CSS, shadcn/ui (Radix), Recharts | MIT | yes |
| lucide-react | ISC | yes |
| Montserrat, Open Sans, Source Sans 3 | SIL OFL 1.1 | yes (Loos Wide is commercial: **not embedded**) |
| Since AI synthetic dataset v1.0.1 | START_HERE: "You can use it freely"; **no licence file in the pack — confirm terms** | confirm |
| `europress_data` code in the pack | no licence file — confirm before redistributing | confirm |
| Papers (Mansouri 2025, Werner 2025, Savia & Koivo 2002 ...) | cited only, nothing reused | n/a |
| Claude API (optional) | Anthropic commercial terms | key required; disabled by default |

## 9. Risks and fallbacks
| Risk | Fallback |
|---|---|
| Live demo fails | static build + recorded walkthrough, both tested on the demo machine |
| T1 does not beat T0 on the data | report it: the synthetic data cannot test pressure; show the fill-only + anchors result and the protocol; do not hide it |
| Anchors too noisy | stricter filter (WEIGHED tare only); report coverage loss |
| Scope creep | hard freeze H+36; stretch only if regression suite is green |
| Number drift between slides and code | single `export.py` source; slides read JSON; business model re-run from one params file |
| Dataset licence unclear | ask Since AI/Tommi; keep derived tables out of public repos until answered |

## 10. Day-one commands
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # pandas numpy scipy scikit-learn lightgbm duckdb pyarrow pyyaml matplotlib fastapi uvicorn
pip install -e "$VW_DATA/.."               # the pack's europress_data package (read-only source)
bash analysis/run_all.sh                    # reproduces the analyst's tables, seed 20261106
python baselines/run_all.py competition     # inside the pack: B1–B6 validation scores to match
```

## 11. Open decisions for you
1. Team size, skills, and who owns A–D. 2. Submission time and live vs recorded judging. 3. Repo location and whether the code may be public (dataset terms unclear). 4. Whether to include the optional Claude-API wording step. 5. Whether Tommi has sent pressure-curve examples on Discord (it changes M1 from "fill-only + anchors" to a real pressure model).
