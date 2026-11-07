# Submission pack: how we are graded and where each piece is

**Source of the grading rules:** `input-files/Europress_SinceAI2026_FINAL/Europress_SinceAI_2026_Challenge_Brief_BUILDER_FINAL (1).pdf` (copies in `europress_zip/` and `europress_final_extract/`). Sections **06 Evaluation Criteria** and **07 Submission Format**.

Challenge: **SMART Material Value Engine: Weigh at Source, Create Value** (Europress Group Oy, Since AI Hackathon 2026, Turku, 6–8 Nov 2026). Submit via Since AI.

## 1. Evaluation criteria (§06) → our evidence

| Weight | Criterion | Our evidence | Status |
|---|---|---|---|
| **25 %** | Weighing concept: technical feasibility, accuracy reasoning, cost, retrofit potential | `europress_conclusions/smartweight/`: EXECUTIVE_SUMMARY, HARDWARE_PROPOSAL, BILL_OF_MATERIALS (3 tiers: €60–130 / €3.4–6.3k / €5.4–10k), MATHEMATICAL_MODELS (identifiability proof), SENSOR_RESEARCH + SENSOR_COMPARISON.csv, simulation `results/` (Pareto cost vs accuracy, error vs mass). Soft sensor: `simulator-weather-and-stuff/` (LightGBM hydraulic estimate, p10–p90 band) and `virtual_scale/` (density rig, anchor curve) | Strong in content. **Gap:** a single *illustrated* concept doc (see §3) |
| **25 %** | Customer / business value | `output/04_business_findings_and_decisions.md`, `04_business_findings_explained.md`, `05_business_plan_addon.md/.html`, `06_problems_solutions_why.md` (8 customer problems → solution → test), `business_sources/BUSINESS_CASE.md` | Done |
| **20 %** | Data-driven value concept + analytical reasoning (traceable calculations) | `output/02_dashboard.md` §3 (every formula), `soome_hackathon_2026/analysis/` (rules vs ML, operator scorecard, weight bias), `europress_conclusions/smartweight/results/` (dataset economics by device/material, verification power, audit cohort) | Done. Check that the headline numbers match across docs (see memory note on number conflicts) |
| **15 %** | Demonstrated software workflow + SMART integration pathway | `europress-dashboard/` (live demo, FI/EN, AI advisor, weight soft-sensor tab), `output/03_deployment.md`, `europress-dashboard/softsensor/README.md` (API), `output/screenshots/`, `05_business_plan_addon` module→file→API table | Demo works. **Gap:** recorded walkthrough video (in progress, `output/animation-comparison/`) |
| **10 %** | Commercial productisation potential | `05_business_plan_addon` (pricing, financials, Phase 0 budget, partners, roadmap with gates), `business_sources/BUSINESS_PLAN_merged.md` | Done |
| **5 %** | Clarity, uncertainty, practical limitations | Evidence tags `[measured]/[derived]/[simulated]/[assumed]` in smartweight; `virtual_scale/ASSUMPTIONS_AND_EXCEPTIONS.md`; `smartweight/ISSUES.md` (20 issues); `02_dashboard.md` §7 Limits; [`ASSUMPTIONS_AND_UNTESTED.md`](ASSUMPTIONS_AND_UNTESTED.md) | Done |

## 2. Required deliverables (§07) checklist

| # | Required item | Where | Status |
|---|---|---|---|
| 1 | **Short illustrated weighing concept**: sensor/measurement principle | smartweight/EXECUTIVE_SUMMARY §1, MATHEMATICAL_MODELS §2 | ✅ |
|   | placement | HARDWARE_PROPOSAL "Where it mounts", EXECUTIVE_SUMMARY §1 "Where" | ✅ |
|   | indicative bill of materials and cost | BILL_OF_MATERIALS.md (3 tiers + rejected options) | ✅ |
|   | installation | HARDWARE_PROPOSAL, BILL_OF_MATERIALS (labour) | ✅ |
|   | calibration | MATHEMATICAL_MODELS §2.3, virtual_scale anchor curve | ✅ |
|   | error sources | MATHEMATICAL_MODELS, results/uncertainty_budget.csv, ISSUES #16 (snow), virtual_scale §1 (frozen/wet) | ✅ |
|   | validation plan | EXPERIMENT_PLAN.md (Phase 0–2, pre-registered pass/fail) | ✅ |
|   | *illustrated, short* | figures exist (`results/*.png`, `virtual_scale/reports/fig*.png`), but no single short doc with a placement drawing | ⚠️ **TODO**: 2–4 page PDF/HTML with a placement diagram |
| 2 | **Working software demo or recorded walkthrough** using synthetic weight data | `europress-dashboard/` (live on the tailnet) | ✅ demo / ⚠️ video in progress |
|   | code/setup notes | `simulator-weather-and-stuff/README.md`, `europress-dashboard/softsensor/README.md`, `output/03_deployment.md`, requirements.txt files | ✅ |
|   | traceable economics | `output/02_dashboard.md` §3, `smartweight/results/dataset_economics_*.csv` | ✅ |
|   | proposed SMART integration | `05_business_plan_addon` (modules → files → APIs; operator feed JSON/CSV/webhook), `softsensor/README.md` architecture | ✅ |
| 3 | **Concise customer value + business case**: use case/service | `06_problems_solutions_why.md`, `05_business_plan_addon` | ✅ |
|   | measurable customer benefit | `04_business_findings…`, `06` (test per problem) | ✅ |
|   | commercial model for Europress | `05` pricing + financials | ✅ |
|   | productisation as part of SMART | `05` modules M1–M7, roadmap | ✅ |
|   | *concise* | material is spread over several long docs | ⚠️ **TODO**: 1–2 page summary |
| — | **Every third-party library, model, dataset, service + licence + commercial restrictions** | [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md), [`third_party_inventory.csv`](third_party_inventory.csv) | ✅ new (one row marked CONFIRM) |
| — | **Assumptions and what remains untested** | [`ASSUMPTIONS_AND_UNTESTED.md`](ASSUMPTIONS_AND_UNTESTED.md) | ✅ new (consolidated) |
| — | No physical prototype required | — | n/a |

## 3. Open items before submitting

1. **Illustrated weighing concept (25 % criterion).** Build one short document from `smartweight/`: a placement diagram (4 shear beams under DUO docking frame / COMBI feet), the tier table, the calibration steps, the error budget and the validation phases.
2. **Recorded walkthrough** of the dashboard (the brief accepts a demo *or* a recording; a recording protects against a failed live demo).
3. **One-page business case** distilled from 04/05/06.
4. **One consistent weighing story.** smartweight says indirect/hydraulic sensing gives P95 25–49 % and cannot reach ±2–5 %. The soft sensor (`simulator-weather-and-stuff`, `virtual_scale`) is a hydraulic estimate. Present them as one ladder: a free soft-sensor estimate on every machine (T1, labelled with its band) plus a load-cell **audit cohort** (T2) per operator as the reference. `05` already uses this "weight ladder T0–T3".
5. Confirm the **ChatGPT/Codex** row in the licence inventory, and ask the organisers about the **dataset licence**.
6. Check that the headline numbers agree across 02/04/05/06 and the video (see `~/.claude/projects/-home-hackathon/memory/demo-video-plan.md`).
