# Build plan: "Verified Weight" (working title)

Author: build-architect agent, Fri 6 Nov 2026, 19:40 (H0). Inputs: `docs/00_shared_brief.md`, `docs/agents/red-team-judge.md` (spine C2+C3+C4+C6+C7, C8 as one action, light C14), `docs/agents/weighing-engineer.md`, `analysis/`.

The submission deadline is assumed to be **Sun ~12:00 (H+40)**. Please confirm it; the whole schedule shifts with it.

## 0. Machine facts (probed)

| Tool | State |
|---|---|
| Python | 3.13.5 venv `/home/hackathon/.claude/jobs/717fee2a/tmp/v`. It has duckdb 2.0, pandas 3.1, pyarrow, sklearn 1.9, scipy 1.18, numpy, matplotlib, PyYAML. **No** fastapi, uvicorn, anthropic, pytest or statsmodels. |
| Node | v26.13.0 and npm 11.20. **No pnpm, no uv, no docker.** |
| Network | PyPI, the npm registry and api.anthropic.com are reachable. |
| Make | GNU Make 4.4 |
| Hardware | 4 cores, 7 GB RAM. The competition data is 116 MB. |
| Claude API | `ANTHROPIC_API_KEY` is **not set**. The team must supply a key. |

**Decision:** own `.venv` with pinned `requirements.txt` (not the shared job venv); **npm** + `package-lock.json` (no pnpm).

## 1. Architecture

```
competition parquet (read-only) --open_dataset(as_of)--> build_marts.py --> marts/vw.duckdb (+ parquet exports)
                                                               |
       engine/: reconcile · attribution · drift · density · invoice · actions · bench
                                                               |
                     FastAPI (reads marts, writes decisions/events to state.duckdb)
                     /api/*   +  serves web/dist (static SPA)   -> one process, port 8000
                                                               |
             llm/: drafter (Claude) + guard + cache/llm/*.json (fallback = template)
```

**Principle: precompute everything, serve read-only.** Model results are batch outputs in the marts; the only write path is approvals (appended to `state.duckdb` + event outbox). Demo is fast and deterministic. A `DEMO_AS_OF` parameter in `params.yaml` (e.g. `2026-07-01`) drives `open_dataset(..., as_of=)` so decisions are leak-free.

### 1.1 Data layer (owner: Data/ML)

`engine/build_marts.py` puts the dataset's `src/` on `sys.path`, calls `open_dataset`, and writes these tables:

| Mart | Grain | Key columns |
|---|---|---|
| `lift_pair` | collection_id | device, ticket_id, vehicle_id, tare_method, loads_on_vehicle, side_waste, dev_kg, ticket_kg, σ_dev, σ_ticket, z, tier, `clean_anchor` flag |
| `lift_trace` | collection_id | telemetry before/after → event → ticket → grade → contract_version → invoice_line_ids → €/t (the end-to-end audit row) |
| `vehicle_effect` | vehicle_id | shrunk bias %, CI, n, share stored-tare |
| `device_state` | device × day | device bias, CUSUM S+/S-, drift alarm, density z |
| `invoice_check` | invoice_line_id | expected €, billed €, rule hit, weight-basis note |
| `operator_score` | operator × region × month | B2 metrics, plus a cause-adjusted weight bias |
| `proposal` | proposal_id | see §1.3 |
| `bench` | task × method | official `europress_data.evaluate` scores (A, B, B2, C2) and our own metrics |

Port the existing `analysis/common.py::lifts()` and the `01_*` logic rather than rewriting them.

### 1.2 Engine (owner: Data/ML; pure functions, unit-tested)

**`reconcile.py`**
- Device uncertainty: σ_dev = max(`mass_uncertainty_kg`, 15 kg, 1.4%·m).
- Ticket uncertainty depends on the tare method. Weighed tare: σ_ticket = √(20² + (1%·m)²). Stored tare: add the vehicle-effect uncertainty.
- Agreement score: z = (dev − ticket − vehicle_bias) / √(σ_dev² + σ_ticket²).
- Tiers: AGREE (|z| < 2), REVIEW (2–3), BREACH (> 3).
- Monthly roll-up: the random part shrinks as σ/√n and the systematic part does not, so we report both.

**`attribution.py`**: r = ln(dev/ticket) = b_device + b_vehicle·[stored tare] + b_stream + ε, fitted by alternating robust backfitting with shrinkage n/(n+k), k = 10 (~40 lines numpy; equivalent to crossed random effects, explainable). Outputs variance share per cause, per-lift decomposition ("of −340 kg: tare −290, device −20, residual −30"), and leave-month-out stability of vehicle effects (guards against a simulator artefact).

**`drift.py`**: tabular CUSUM (k = 0.5σ, h = 4σ, reset at service work orders) on clean-anchor residuals (weighed tare, single load, no side waste) after removing vehicle effects. Scored vs `SENSOR_DRIFT`/`CALIBRATION_ERROR` labels (n = 19): detection rate, median lead days, false alarms/device-year.

**`density.py`**: ρ̂ = mass_before/(V·fill), robust z vs the stream's fleet band. High z at an outdoor site → `MOISTURE_SUSPECT`; with grade C/R → `CONTAMINATION_SUSPECT`. Precision/recall vs `MOISTURE_HEAVY_LOAD` / `CONTAMINATION_INCIDENT` labels, reported whatever they are.

**`invoice.py`** re-implements the Task B rules in our own code. The baselines' licence is unstated, so we do not import them (see §6). It also adds the lift-level device/ticket/invoice triangle.

**`actions.py`** creates proposals, each with type, target, evidence, an expected-value range, confidence, a reversal path and a neutral-tone flag. Types, in order of display precedence:

1. VERIFY_SENSOR
2. FIX_VEHICLE_TARE (sent to the operator first)
3. REQUEST_WEIGHBRIDGE_DATA
4. DISPUTE_INVOICE
5. RENEGOTIATE
6. TENDER_OR_SWITCH (shown last and gated)

The EV p10/p50/p90 comes from a bootstrap over lifts, using the hypothetical prices in `params.yaml`.

**`bench.py`** runs `python -m europress_data.evaluate` on the validation/dev splits for our method and the baselines, and writes the results to `bench`.

### 1.3 API (owner: Backend; FastAPI with Pydantic v2 models, which are the contract)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health`, `/api/meta` | as_of, dataset version, evidence-tag legend |
| GET | `/api/fleet/summary` | agreement distribution, tier counts, € at stake (hypothetical) |
| GET | `/api/devices?stream=&tier=` · `/api/devices/{id}` | device list; series with bands and the CUSUM |
| GET | `/api/lifts/{collection_id}/trace` | **the hero end-to-end trace** |
| GET | `/api/attribution` · `/api/vehicles/{id}` | cause decomposition, vehicle-tare effects |
| GET | `/api/operators/scorecard?month=` | operator-neutral scorecard |
| GET | `/api/proposals?status=&type=` · `/api/proposals/{id}` | approval inbox |
| POST | `/api/proposals/{id}/draft?mode=cached\|live` | LLM draft with citations |
| POST | `/api/proposals/{id}/decision` | `{decision: APPROVE\|REJECT\|DEFER, reviewer, note}` → `approval.decided` event |
| POST | `/api/ingest/tickets` | operator give-to-get ingest; returns a reconciliation receipt |
| GET | `/api/events?since=` | outbox (demonstrates the SMART integration) |
| GET | `/api/bench` · `/api/sim/virtual-scale` | AI-vs-rules scores; Part 1 simulation results |

Example proposal (all values illustrative):

```json
{
  "schema": "vw.proposal.v1", "synthetic": true,
  "proposal_id": "P-2026-07-000143", "type": "FIX_VEHICLE_TARE",
  "audience": "OPERATOR_FIRST", "target": {"operator_id": "OP-E", "vehicle_id": "OP-E-V06"},
  "finding": "Stored-tare tickets for this vehicle read 21% (CI 17–25%) above device and weighed-tare peers",
  "evidence": {"observed": {"lifts": 115, "median_gap_pct": -21.0},
               "row_ids": ["COL-…0412", "TKT-…8810", "…"], "method": "attribution.py v1, k=10"},
  "uncertainty": {"tier": "BREACH", "z_median": 4.1, "alt_causes": ["side_waste", "combined_load"]},
  "expected_value_eur": {"p10": 310, "p50": 640, "p90": 980, "basis": "hypothetical tariffs, params.yaml"},
  "requires_human_approval": true, "auto_execute": false,
  "reversal_path": "Withdraw the request; no invoice is changed until the operator re-weighs tare",
  "status": "PENDING"
}
```

### 1.4 Frontend (owner: Frontend)

**Choice: Vite + React + TypeScript + Tailwind + shadcn/ui (Radix) + Recharts + TanStack Query + React Router.**
- Fonts: Montserrat (the stand-in for Loos Wide) and Open Sans, self-hosted via `@fontsource`. No CDN.
- Types are generated from FastAPI's `openapi.json` with `openapi-typescript`.

**Why not Next.js?** No SSR/RSC benefit, hydration/boundary bugs are a time sink, two processes. A Vite build is static files served by FastAPI: one process, offline, nothing to deploy. **Why not Streamlit?** Reliable but generic; approval drawer and citation hovers are clumsy. Plan B only: if screen ① is not rendering by H+18, B builds a Streamlit page over the same API.

Brand tokens: navy `#000d61`, signal `#ff2962`, ice `#e0f1f5`, mint `#ddf8ee`, pink wash `#fff0f4`. There is **no map**; regions are shown as a bar chart. Every number carries an evidence chip: observed / estimated / simulated / hypothetical.

| Prio | Screen |
|---|---|
| P0 | ① Fleet overview · ② Lift trace (one number, end to end) · ③ Cause attribution (vehicle-tare showcase, waterfall) · ⑤ Proposals inbox + approval drawer (draft, cited rows, EV range, reversal) |
| P1 | ④ Device drift (CUSUM) · ⑥ Operator scorecard ("shared with operator first") · ⑧ Bench: AI vs rules |
| P2 | ⑦ Part 1 virtual-scale simulator page. It can live in the deck only. |

### 1.5 LLM layer (owner: Backend; Python `anthropic` SDK)

**What the LLM does and does not do.** The deterministic engine **decides**. Claude only **drafts**: dispute letters, data requests, operator notes and a plain-language "why" for each proposal.

**Input** is the proposal JSON plus 30 or fewer evidence rows, and nothing else.

**Output** uses structured outputs (`output_config.format`, JSON schema `{subject, body, claims:[{sentence, row_ids[], numbers[]}]}`).

**Guard** (`llm/guard.py`) rejects a draft citing a `row_id` outside the evidence set, a number not in the evidence (±0.5%), or blame wording (lexicon). One retry, then the deterministic template, labelled "template".

**Models:**
- `claude-haiku-5-5` for bulk drafts ($0.10 / $0.50 per MTok).
- `claude-sonnet-5-5` for the 5 hero drafts and the optional "ask about this proposal" ($2 / $10 per MTok). Use `fallbacks: "default"` on Sonnet per the current API guidance.

**Cache.** The static system prompt and schema come first (prompt caching). Drafts for the top ~60 proposals are pre-generated into `cache/llm/{sha256(model+prompt)}.json` and committed, so the demo never needs the network. Estimated total spend is under €2.

**Honest bake-off** (for `/api/bench`; numbers are filled in at H+28):

| Method | Task B / C2 decision quality | Draft groundedness (% claims cited correctly) | Numeric fidelity | Blind human rating (2 raters × 20 drafts) | Cost per 1k proposals |
|---|---|---|---|---|---|
| Rules only (ours) | official score | n/a (template) | 100% | — | €0 |
| LLM-as-classifier (Haiku given the same features) | official score | — | — | — | — |
| Hybrid: rules decide, LLM explains | = rules | — | — | — | — |

Expected result: rules win on detection (the BENCHMARK shows GBM 0.35 vs rules 0.73 macro-F1) and the LLM wins on readability. **Report it either way.**

## 2. SMART integration pathway

**Events** use a CloudEvents 1.0 envelope (`specversion, id, source, type, time, subject, datacontenttype, data`) on SMART's existing message bus or webhooks:

| type | Emitted when | Key `data` |
|---|---|---|
| `fi.europress.smart.weight.estimated.v1` | each emptying (edge/cloud) | device_id, mass_kg, interval_p10/p90, model_id, tier T0/T1/T2 |
| `…weight.reconciled.v1` | a ticket is matched | collection_id, ticket_id, z, tier, attribution {device, vehicle, residual} |
| `…device.drift_suspected.v1` | CUSUM alarm | device_id, S+, since, evidence ids |
| `…recommendation.created.v1` | proposal | the full proposal object (§1.3) |
| `…approval.decided.v1` | human decision | proposal_id, decision, reviewer_role, note, reversal_path |
| `…ticket.ingested.v1` | operator API push | operator_id, ticket count, schema version, rejects |

```json
{"specversion":"1.0","type":"fi.europress.smart.weight.reconciled.v1","source":"/smart/vw-engine",
 "id":"evt-01J…","time":"2026-07-01T06:12:00+03:00","subject":"COL-…0412",
 "data":{"device_id":"DEV-0231","dev_kg":2950,"ticket_kg":3600,"z":-4.3,"tier":"BREACH",
         "attribution":{"vehicle_tare_kg":-590,"device_kg":-25,"residual_kg":-35},"synthetic":true}}
```

**Tier mapping:**

| Tier | What it includes |
|---|---|
| **Intro** | T0 estimated kg with an interval per emptying, plus monthly kg and €/t. Software only. |
| **Insights** | Reconciliation, drift and density alerts, the scorecard and the proposals inbox with approval. This is the core offer. |
| **Integrated** | Ticket-ingest API and webhooks, export of approved disputes to ERP/accounts payable, an operator portal, and T2 load-cell hardware for customers who need verification-grade weight. |

**Operator ticket ingest (give-to-get).** `POST /api/ingest/tickets` takes JSON or CSV with this schema: ticket_id, operator_job_ref, vehicle_id, gross/tare/net, tare_method, loads_on_vehicle, published_at. It is authenticated with a per-operator API key (in a real deployment) and idempotent on ticket_id.

The operator gets back a reconciliation receipt, a private stored-tare hygiene report on its own vehicles, and fewer disputes. This is how C3/C4 get their labels.

**Edge and firmware changes for Part 1** (with the weighing engineer's input):
1. Log P(t) at 10–20 Hz during each stroke from the existing 0–200 bar transducer, plus stroke time and an oil-temperature proxy.
2. Extract features on the edge: P_peak, P_hold, ∫P dt, dP/dt, hold decay and stroke time. Each feature record is about 64 B, so 200 strokes/day ≈ 13 kB/day. The raw curve (about 400 B/stroke) is uploaded only for golden-cohort machines or for 1 in 50 sampled strokes.
3. Upload the daily batch over the existing modem. Stamp each estimate with `model_id` and firmware version.
4. Roll out OTA in stages (1% → 10% → 100%) with automatic rollback if the estimate-vs-ticket MAE regresses.
5. Optionally, sign readings with a per-device Ed25519 key (for a later evidence pack).

## 3. Part 1 simulator (owner: Data/ML, ~5 h; `sim/virtual_scale_sim.py`, CLI and notebook-free)

Every chart is watermarked **"SIMULATED — illustrates method, not accuracy"**.

**Generator.**
- Charges Δm are lognormal per stream.
- Compaction follows ρ(σ) = ρ0 + β·ln(σ/σ0).
- Stress per stroke comes from the target density, with F = P·A − F_fric(T_oil).
- The curve P(t) is a rise to P_peak, then a hold with exponential springback decay τ_mat, plus 0.5% FS noise.
- Per-device gain g ~ N(1, 0.10).
- Moisture adds mass without adding pressure.
- Emptying resets the integral.

**Estimator.** A physics baseline m = g·Σ W_i/w_mat, calibrated with k = 0, 1, 3, 5 anchors at 3% noise (including a stored-tare bias), with a Student-t robust gain update and CUSUM.

**Outputs:** error-vs-k curves; error-budget reproduction (RSS ~14% → 6.6%); Monte Carlo power of the validation protocol (A1–A6 at n = 150/240 lifts); JSON served at `/api/sim/virtual-scale`.

**Test:** with no moisture, the estimator recovers a planted gain within ±2%.

## 4. Repo, start, tests, licences

```
verified-weight/
├─ Makefile  README.md  params.yaml  requirements.txt  LICENSES.md
├─ engine/  build_marts.py reconcile.py attribution.py drift.py density.py invoice.py actions.py bench.py
├─ api/     main.py models.py routes/{fleet,lifts,proposals,ingest,events,bench}.py state.py
├─ llm/     drafter.py guard.py prompts/system.md templates/*.j2
├─ sim/     virtual_scale_sim.py
├─ web/     package.json vite.config.ts src/{pages,components,api/types.gen.ts,theme}
├─ marts/   (generated, gitignored)    cache/llm/*.json (committed)
├─ tests/   test_reconcile.py test_attribution.py test_drift.py test_proposals.py test_api_contract.py test_llm_guard.py test_sim.py
├─ docs/    part1_weighing_concept.md business_case.md assumptions_untested.md integration.md
└─ demo/    script.md walkthrough.mp4
```

**Make targets:** `make setup` (venv + `pip install -r requirements.txt` + `npm ci --prefix web`) · `make marts` (build_marts → bench → actions, ~2–4 min, idempotent) · **`make demo`** (marts if missing, build `web/dist`, `uvicorn api.main:app --port 8000` → http://localhost:8000) · `make dev` (uvicorn --reload + vite :5173 proxying `/api`) · `make test` (pytest + `tsc`) · `make drafts` (refresh `cache/llm`, needs key) · `make licences`.

**Tests (light, `make test` before each milestone):** reconciliation z/tier boundaries, σ/√n roll-up, stored-tare σ inflation; attribution recovers a planted ±20% vehicle bias; CUSUM catches a planted 5% step within 10 anchors with <0.2 false alarms/device-year; proposal invariants (approval required, no auto-execute, row_ids exist, p10 ≤ p50 ≤ p90); API contract via TestClient + `openapi.json` snapshot; LLM guard rejects invented rows/numbers.

**Licence commands (run at H+34):**

```
.venv/bin/pip install pip-licenses && .venv/bin/pip-licenses --format=markdown --with-urls --order=license > docs/py_licences.md
npx --yes license-checker-rseidelsohn --start web --production --summary \
  --onlyAllow "MIT;ISC;Apache-2.0;BSD-2-Clause;BSD-3-Clause;0BSD;OFL-1.1;CC0-1.0;BlueOak-1.0.0;Python-2.0"
```

## 5. Schedule (H0 = Fri 19:40; owners D = Data/ML, B = Backend, F = Frontend, P = Business/Pitch)

| Window | D | B | F | P |
|---|---|---|---|---|
| **H0–2** Fri 19:40–21:40 | Repo, `make setup`, port `lifts()` | Pydantic models, proposal and event schema (**contract freeze v0**), fixtures | Vite + shadcn scaffold, theme, layout shell | Submission checklist, deck skeleton, list of questions for Tommi |
| **H2–6** →Sat 01:40 | `lift_pair`, `lift_trace`, `vehicle_effect` marts | Routes fleet, lifts and trace on the marts; `make demo` | Screens ① and ② on fixtures, then live | Part 1 concept draft from weighing-engineer.md (BOM, error budget, validation) |
| **M1 H+6** | **`make demo` shows the fleet overview and one real traced lift** | | | |
| H6–12 | Sleep (stagger: D and B 02:00–08:00, F and P 02:30–08:30) | | | |
| **H12–18** →Sat 13:40 | reconcile, attribution, CUSUM, plus evaluation against labels | `actions.py` integration, decision POST, events outbox, ingest | Screens ③ and ⑤ (approval drawer) | `params.yaml` prices + sensitivity grid, business model, SMART tier map; ask Tommi at the mentor slot |
| **M2 H+18** | **Full loop: proposal → approve → event in the outbox; official scores in `bench`** | | | |
| **H18–28** →Sat 23:40 | density flags, simulator (§3), bench numbers | LLM drafter, guard, cache, bake-off harness, `make drafts` | Screens ④, ⑥, ⑧ and the evidence chips; polish | Deck v1, licence table, assumptions/untested, demo script |
| **M3 H+28** | **Feature complete; cached drafts committed; rehearsal #1 and draft recording** | | | |
| H28–34 →Sun 05:40 | Bug fixes, tests green, numbers frozen into `bench.json` | Hardening, offline test (Wi-Fi off) | Polish, ⑦ only if green | Deck v2 with frozen numbers; 4 h sleep in pairs |
| **M4 H+34 FREEZE** | **Tag v1.0, licence scan, final walkthrough recording (screen capture + voice-over)** | | | |
| H34–40 →Sun ~11:40 | Fixes only | README and setup notes | Rehearsal ×3 | Package submission (concept PDF, demo/recording, business case, licences); submit by H+39 |

**Demo script (3:00):**

| Time | Beat |
|---|---|
| 0:00–0:20 | The pain: "The operator holds the weight; customers can't check invoices." SMART already handles pickups, so we don't. |
| 0:20–0:50 | Part 1 in one slide: T0 virtual scale (€0 BOM), T1 ticket-calibrated, T2 platform. Error budget, then the "SIMULATED" error-vs-anchors chart. |
| 0:50–1:30 | Screen ①, then ②: one lift traced from telemetry to ticket to contract version to invoice line to €/t, with the interval and evidence chips. |
| 1:30–2:05 | Screen ③: "Most of the big gaps are a stored tare on one vehicle, not the sensor and not intent." The proposal FIX_VEHICLE_TARE goes to the operator first. |
| 2:05–2:40 | Screen ⑤: open the proposal, show the Claude draft with clickable row citations, and approve it. The `approval.decided` event appears in the outbox (the SMART integration). Screen ⑧: rules vs AI, honestly. |
| 2:40–3:00 | Business: Insights tier, value-based fee band from `params.yaml`. Limits: synthetic data, no pressure data, prices hypothetical. |

The backup is the recorded walkthrough in `demo/walkthrough.mp4`, plus screenshots in the deck.

**Risks → mitigation:** LLM/Wi-Fi down → cached drafts default, live is a toggle · slow mart build → build once, commit parquet, DuckDB 3 GB limit · vehicle effect fails leave-month-out (check by H+18) → demote to "hypothesis" · drift n = 19 → CIs, "indicative" · frontend slips → P0 only, Streamlit Plan B, hard cut H+28 · scope creep → extras only after green M3 · leakage → all decisions via `as_of`, tune on dev only · licence surprise → scan at H+34, no baseline code imported · over-claiming → P runs a deck claims audit against evidence tags at H+30.

## 6. Third-party licences (confirm versions with the scan at freeze)

| Component | Licence | Commercial-use note |
|---|---|---|
| FastAPI, Pydantic, DuckDB, PyYAML, pytest, anthropic SDK (Python) | MIT | OK |
| Starlette, Uvicorn, httpx, pandas, NumPy, SciPy, scikit-learn | BSD-3-Clause | OK |
| pyarrow | Apache-2.0 | OK |
| matplotlib | Matplotlib licence (PSF-style) | OK |
| React, Vite, Tailwind CSS, shadcn/ui (copied source), Radix UI, Recharts, TanStack Query, React Router, openapi-typescript | MIT | OK |
| lucide-react | ISC | OK |
| @fontsource Montserrat and Open Sans | OFL-1.1 fonts, MIT packaging | OK to embed. State that Montserrat stands in for Loos Wide (commercial; not shipped). |
| CloudEvents spec | Apache-2.0 (specification only) | OK |
| Claude API (`claude-haiku-5-5`, `claude-sonnet-5-5`) | Anthropic Commercial Terms | It is a paid service, and only synthetic data is sent. |
| Since AI / Europress dataset v1.0.1 and the `europress_data` SDK, used as a read-only dependency | No licence file; "Since AI Hackathon 2026 rules" | Confirm commercial and IP use with the organisers. The baselines are **not** copied into our code. |
| pip-licenses, license-checker-rseidelsohn (dev tools only) | MIT, BSD-3-Clause | Not shipped |
| Excluded | Next.js/Vercel hosting, map tiles, Mapbox, Highcharts, AGPL/GPL packages | — |

## 7. Open questions

1. Exact submission deadline and format (live or recorded judging)?
2. Will someone fund the Claude API key, or do we run cached-only?
3. Can Tommi confirm the SMART event bus and API surface, and whether per-stroke pressure is archived?
4. Dataset licence and IP terms for code that calls the `europress_data` SDK.
