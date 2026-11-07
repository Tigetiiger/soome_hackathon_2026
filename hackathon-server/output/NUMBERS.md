# NUMBERS: the one agreed set of figures

**Europress × Since AI 2026 · checked 7 Nov 2026, 18:30.** Every figure below was re-read from the file named in its "Source" column. Nothing here is new modelling. Where two figures measure different things, both are kept and the basis is named. Where a figure had no source, it was removed rather than replaced.

Evidence tags (same as the business case):

| Tag | Meaning |
|---|---|
| **[D]** | Computed on the synthetic competition dataset (Europress practice data, hypothetical prices) |
| **[S]** | Our own simulator (`simulator-weather-and-stuff`, `smartweight/simulation`, `virtual_scale`) |
| **[E]** | Our estimate (error budget, budget, price arithmetic) |
| **[L]** | Listed supplier price, with URL in `smartweight/_research/hardware_prices.md` |
| **[T]** | Said by Europress at the briefings |
| **[A]** | Our assumption |

> **Read this caveat first.** The dataset simulates its own device weight with noise of **max(15 kg, 1.4 %)** (`europress_data/.../configs/assumptions.yaml:172`). Every [D] result that uses device weight (the €-share 77 % → 96 %, overbilling detection, the drift alarm) therefore assumes a sensor much more precise than our pressure soft sensor. Say so when you quote them.

---

## 1. Weight accuracy

| Figure | **Use this** | Basis | Source |
|---|---|---|---|
| Soft sensor, unseen machines | **5.3 % mean error per pickup** (median 4.3 %, 55 % within ±5 %, 88 % within ±10 %) [S] | 100 held-out machines, last 25 % of the year, n = 1,221 pickups | `simulator-weather-and-stuff/models/full400/REPORT.md:3`; `europress-dashboard/public/data/softsensor/evaluation.json` → `splits.bins.lift.overall` |
| Soft sensor, known machines | **3.7 % mean** (median 3.0 %, 73 % within ±5 %) [S] | Same 400 machines, later months, n = 4,876 | same files, `splits.time` |
| Naive fill × nominal density (simulator) | **32.1 %** unseen / 28.3 % known [S] | same runs | `full400/REPORT.md:3` |
| 80 % range (p10–p90) coverage | **77 %** unseen, 78 % known [S]. **Mixed waste on unseen machines: 31 %** | target 80 % | `full400/REPORT.md` §coverage, line 141 |
| Worst-case error of the soft sensor | **Not reported.** 88 % of unseen-machine pickups are within ±10 %, so more than 5 % miss by more than 10 % [S] | — | `evaluation.json` `within_10pct` = 0.8755 |
| Pressure-based mass, hardware study | **P95 29 %** (physics model anchored on tickets, with oil-temperature probe); 31.7 % without the probe; ML on unseen machines P95 34 % with anchors, 49 % without [S] | SmartWeight simulator | `europress_conclusions/smartweight/SENSOR_RESEARCH.md:133–141` |
| Strain gauges on the frame | **P95 ≈ 25 %** [S]. *This is not the pressure figure* | same | `SENSOR_RESEARCH.md:90` |
| Tier 2 load cells (4 × IP68 C3 shear beams) | **P95 2.3 %** [S] | loads ≥ 1 t | `smartweight/results/core_comparison.csv`, row `LC4_CHEAP`, `P95_rel_ge1t` |
| Tier 3 certified load cells | **P95 1.4 %** [S] | loads ≥ 1 t | same file, row `REF_CERT_LC4` |
| Software-only estimate, literature error budget | **±12–15 % per pickup (1σ), ±5–6 % on monthly totals after ~20 clean tickets** [E] | RSS error budget, not data | `soome_hackathon_2026/docs/agents/science-researcher.md` §2 (error-budget table) |
| Dashboard weight model on the practice data | v1 fill × density table **15.4 %** median → v3 with per-machine ticket calibration **7.0 %** [D] | trained Oct–Mar, tested Apr–Sep, 3,522 lifts | `output/02_dashboard.md:191–193` |

**How to say it in one line:** "On our simulator the soft sensor is 5.3 % off on average on machines it never saw. A separate hardware study says pressure alone can be off by 29 % in the worst 5 % of cases. A €0 test on archived SMART pressure data against tickets decides who is right. Load cells reach 2.3 % (P95) and are the reference."

**Wrong values seen:** 4.7 % (= the plastic-film row on unseen machines, not the overall figure), 61 % within ±5 % (not in the current report), 3.4 % (early test fit), "fill-only 7 %" (7 % is v3, which uses tickets), "±1.4 %" for Tier 2 (that is Tier 3), "P95 25–49 % for pressure" (25 % is strain gauges).

## 2. Hardware cost

| Figure | **Use this** | Source |
|---|---|---|
| Tier 2 load cells per machine | **€3.4–6.3k installed, mid €4.85k** [L/E] | `smartweight/BILL_OF_MATERIALS.md`; `EXECUTIVE_SUMMARY.md:22` |
| Tier 3 certified | **€5.4–10k** plus €150–400 a year [L/E] | `BILL_OF_MATERIALS.md` |
| Soft sensor on SMART machines | **€0** extra hardware (the pressure sensor already exists) [T] | briefing; `tommi_1600.txt` |
| Pressure transducer for other makers' machines | **€264** (cheapest verified); £156–198 in the UK [L]. The €30 figure could not be verified | `smartweight/SENSOR_RESEARCH.md:104`; `ISSUES.md:19` |
| Load cells in a 72-month lease | **≈ €47–88 a month, hardware only** [E] = €3.4–6.3k ÷ 72, no interest or margin | arithmetic on the BOM |
| Measured tier price | **Europress's current platform price**, on the lease; outside the add-on economics [T] | Europress already sells the Scale Solutions platform |

**Wrong values seen:** €1.0–1.9k and ~€1,500 for load cells (rejected in `smartweight/ISSUES.md:10`), €14–26 / €14–33 / €21–33 a month lease cost, a +€39–49 a month measured-tier price (below the hardware cost above).

## 3. Pilot and Phase 0 budget

| Figure | **Use this** | Source |
|---|---|---|
| 10 reference machines with load cells | **€34–63k** (10 × €3.4–6.3k) [E] | `05_business_plan_addon.md` §6 |
| Kerava rig test (Phase 1 of the experiment) | **€15–30k**, 4–6 weeks [E] | `smartweight/EXECUTIVE_SUMMARY.md:133` |
| Rig + 10-machine field pilot | **≈ €50–100k** [E] | `smartweight/EXPERIMENT_PLAN.md:92` |
| Phase 0 total (software 15 person-months €150k, rig, 10 load-cell machines, sensor kits, camera pilot, cloud) | **≈ €211–267k** [E] | `05_business_plan_addon.md` §6 table |
| Maximum loss | **the Phase 0 budget, ≈ €211–267k**, because of the stop gate [E] | same |

**Wrong values seen:** €10–19k for the reference scales, and "downside ≈ €150k". Both came from the early CFO plan, which assumed 6 platforms at €11k in total (`europress_conclusions/agents/bizplan-cfo.md:125`). Also "about €270k", which is a rounded figure.

## 4. What a customer can check

| Figure | **Use this** | Basis | Source |
|---|---|---|---|
| Fleet, pickups | **74 % → 97 %**: pickups with a ticket today → with at least one independent weight (ticket or device) [D]. Device estimate alone: 88 % | all lifts | `soome_hackathon_2026/analysis/outputs/09_summary.log:3` |
| Fleet, euros | **77 % → 96 %** of mass-billed euros have an independent weight [D] | €2.76M billed by weight; tickets cover €2.11M, device-only €0.53M, neither €0.12M | `europress_conclusions/analysis/outputs/10_summary.json` (`mass_billing_*`) |
| Hotel group (ORG-0049) | **48 of 395 pickups (12 %) had a ticket.** 37 agree with the machine within 10 %, 11 differ by more, and 347 have only the machine weight [D] | demo customer | `europress-dashboard/public/data/customers/ORG-0049.json` → `weight` |

**Rule:** never pair a pickup share with a euro share. **Wrong values seen:** "37 of 395 (9 %) had a ticket" (37 is the number that *agree*), "9 % → 96 %", "95–97 % of lifts".

## 5. Hotel group "Hospitality Customer 0049" (practice data, prices invented)

| Figure | **Use this** | Source (`ORG-0049.json`) |
|---|---|---|
| Annual cost | **€140,574**, 496.6 t, €283/t [D] | `kpis.total_cost`, `tonnes`, `eur_per_t` |
| Savings potential | **€60,471 a year (43 % of cost)**, of which "empty when full" is **€39,955** [D] | `kpis.savings`, `levers[early_lifts]` |
| ⚠️ Concentration | One machine, **CMP-00430, supplies €29,074** of the €39,955, at €484.56 per pickup (contract lift fee €427.37) [D] | `levers[0].trace.rows` |
| Pickups / fill | **395 pickups**, 49 % average fill at emptying [D] | `kpis.lifts`, `kpis.avg_fill` |
| Mixed waste and recycling | **56 % → 60 % mixed; recycling 44 % → 40 %**, Oct–Dec 2025 vs Jul–Sep 2026 [D] | `trend_findings` (mixed, recycling) |
| Recycling, full year | **43 %** [D] | `kpis.recycling_rate` |
| Operators | Hauler Delta 57 % on time, 0 % tickets shared, 6 wasted trips, 37 h order to truck; second operator 62 % on time, 89 % shared [D] | `operators[]` |
| Notice date | **17 Oct 2026, data as of 30 Sep 2026** [D] | `insights[tender_window]`, `period.as_of` |
| Sorting lever | **€6,318 a year** [D] | `problems[recycling_down].eur` |

**One trend, three bases in the app.** The Trends tab uses the quarter comparison above. The insight card compares half-years (55.2 % → 58.5 % mixed). The Problems list and the quarter-compare panel use Apr–Jun vs Jul–Sep (56.7 % → 60.3 % mixed, 43.3 % → 39.7 % recycling). Each is correct for its own basis. In text, use the quarter comparison and never mix bases. **Wrong values seen:** "55 % → 58.5 % mixed with 44 % → 40 % recycling" (two bases in one sentence).

## 6. Value, prices and the business model

| Figure | **Use this** | Source |
|---|---|---|
| Unnecessary pickups on fixed and hybrid schedules | **30–32 %** (fixed 31.7 %, hybrid 29.7 %; on-call 6.5 %) [D] | `europress_conclusions/analysis/outputs/20a_share_unjustified_by_policy.csv` |
| Value of those pickups | **≈ €2.6k per device-year** mean (€2,597; median €759) [D]. "€2.5–2.7k" is fine | `20_summary.json` → `fixed_hybrid_device_dist_eur_per_dy` |
| Billing errors recovered | **≈ €150 per device-year** mean (€149; median €12) [D] | `10_summary.json` → `overcharge_per_device_year_dist` |
| Contract leverage from device weight | **+€190 per contract-year** where tickets are not shared [D] | `09_summary.log:27` |
| C2 value captured | no weight 50 % → 55 % (tickets) → **77 %** (tickets + device) [D] | `09_summary.log:15–18` |
| Value per contract | mean **€1,064** a year, **median €0**; 52 % of contracts have no positive value [D] | `30_summary.json`; `agents/comparison-sonnet-vs-ours.md:57` |
| Concentration | **Top 5 of all 52 customers hold 54 %** of realisable value; **among the 20 customers with contract-action cases, the top 5 hold 75 %** [D] | `soome_hackathon_2026/docs/agents/business-strategist.md:10`; `comparison-sonnet-vs-ours.md:57` |
| Weighbridge-side share of large gaps | **77 %** (side waste 34 %, stale tare 30 %, combined loads 12 %); device faults **3.9 %** [D] | `10_summary.json` → `gt10_*` |
| Overbilling detection at σ ≈ 10 % | **62 %** of +10 % overbilling caught per quarter [D] | `10d_detection_sigma_sweep.csv` |
| Verified Weight price | **€15 per device per month list, €12 bundled into a new lease** [A]. The dashboard's revenue tile uses €12 (bundled) | `BUSINESS_CASE.md` §3; `public/js/i18n.js:101` |
| +1 pp SMART attach | **≈ 120 machines ≈ €21,600 a year** at the €15 list price (120 × €15 × 12) on an assumed ~12k fleet [A] | `BUSINESS_PLAN.md:103`; `06:93` |
| NPV, 6 years at 10 % | **+€0.01M** subscription alone (break-even); **+€0.58M** base with retention uplift (low −€0.64M, high +€2.84M), payback year 5 [E]. The measured tier (Europress's existing platform) is sold at its own price and is outside these figures | `europress_conclusions/analysis/npv_option_a.py` (reruns `agents/bizplan-cfo_model.py` with `prem_share = 0`) |
| Why the NPV changed | The published −€0.33M / +€0.23M included a measured tier at €49 a month on €1,900 of hardware. At the verified €3.4–6.3k it pays back in 76–140 months, longer than the 72-month lease, and turns the base NPV negative (−€0.29M to −€1.28M) [E] | same script; `smartweight/BILL_OF_MATERIALS.md` |
| Add-on revenue | ⚠️ **two models, see open decision 1** | — |

## 7. AI vs rules (the brief asks for this comparison)

| Test | Rules | ML | Source |
|---|---|---|---|
| Full anomaly benchmark (all families, macro-F1) | **0.73** | gradient boosting **0.35**; **rules + ML hybrid 0.78** | `soome_hackathon_2026/analysis/outputs/09_summary.log:52–54` |
| Weight gaps worth acting on (stale tare + device fault, F1) | **0.89** | gradient boosting **0.91–0.93**; isolation forest **0.10** | `08_rules_vs_ml.csv` |

**How to say it:** "Across all anomaly types, transparent rules beat ML (0.73 vs 0.35), and a hybrid does best (0.78). On weight gaps alone, ML is slightly better (0.93 vs 0.89), so rules decide and ML can rank." **Wrong:** "rules beat ML" with no test named.

---

## 8. Open decisions (need a person, not a fix)

1. **Revenue and value don't come from the same model.** `05` §6 shows €0.15M / €0.50M / **€0.91M** expected for 2027–29. The NPV above comes from the CFO model, whose base year-3 add-on revenue is **€0.6–0.75M** (`BUSINESS_PLAN.md:86`). Either rerun `europress_conclusions/agents/bizplan-cfo_model.py` with the `05` revenue lines, or label them as two scopes.
2. ✅ **Measured-tier price (decided 7 Nov):** sold at Europress's current platform price and kept outside the add-on economics. NPV updated to match (§6).
5. ⚠️ **Not edited, because the correct figure looks worse; waiting for a decision:**
   - `europress_conclusions/BUSINESS_CASE.md:119`: "€10–19k for the scale-platform pilot machines … downside about €150k". The evidence says €34–63k and ≈ €211–267k (§3). `BUSINESS_PLAN.md` and both `04` files already use the correct figures, so the business case currently disagrees with them.
   - `europress_conclusions/analysis/pl_model.py` (annual revenue table, "~€0.6–0.75M in year 3", break-even ~3,100 devices): it still includes the measured tier at 3 % of devices. Taking it out, as in the NPV, lowers base year-3 revenue from €615k to €558–572k and raises break-even to 3,157–3,253 devices.
3. **€25 a month is used for two products**: the Integrated contract benchmark (`BUSINESS_CASE.md` §3) and the camera tier (`05` §6). Rename or reprice one.
4. **The app's trend widgets use three bases** (§5). Optional pipeline change: put all of them on one basis.

## 9. Where things stand, by file

| File | Status |
|---|---|
| `europress_conclusions/BUSINESS_PLAN.md` | ✅ fixed in this pass: load-cell cost and accuracy, lease cost, measured-tier price, pilot €34–63k, Phase 0 €211–267k, concentration bases, [D] → [E] on error-budget figures, [F] → [D] on rules vs ML. "≈ 11 % off uncalibrated" removed (no source found) |
| `output/04_business_findings_and_decisions.md` | ✅ fixed in this pass: 97 % of lifts, concentration bases, rules-vs-ML scopes, hotel trends and as-of date, tier accuracy and cost, measured tier, pilot and Phase 0 |
| `output/04_business_findings_explained.md` | ✅ fixed in this pass: same set |
| `output/05_business_plan_addon.md` / `.html`, `output/06_problems_solutions_why.md`, dashboard, simulator site | Being fixed by the session running `output/PROMPT_fix_number_conflicts.md` (already shows 5.3 %, 48 of 395 = 12 %, as-of date). **Still to do in `06`:** line 33 "fill-only 7 %" → 15.4 % fill-only vs 7.0 % with ticket calibration (§1); line 135 mixes trend bases (§5); line 172 "€270k" → €211–267k (§3) |
| `input-files/CHEAT_SHEET.md` §3–§5 | ⚠️ other session's video sheet. Differs from this file on: "37 have a ticket" (→ 48, §4), Tier 2 "P95 1.4–2.3 %" (→ 2.3 %; 1.4 % is Tier 3, §1), pressure "25–49 % P95" (→ 29–49 %; 25 % is strain gauges, §1) |
| `europress_conclusions/BUSINESS_CASE.md` | ✅ fixed: concentration basis, measured tier, NPV, error-budget tag + 5.3 %, hybrid 0.78. ⚠️ Line 119 (pilot €10–19k, downside €150k) left as is: see open decision 5 |
| NPV in `BUSINESS_PLAN.md`, both `04` files, `05` md + html, `06` | ✅ updated to +€0.01M / +€0.58M (low −€0.64M, high +€2.84M). ⚠️ `input-files/CHEAT_SHEET.md` §6 still shows −€0.33M / +€0.23M |
| `europress_conclusions/BUILD_PLAN.md:79` | ⚠️ "±12–15 % per lift" needs the [E] tag and the 5.3 % [S] figure next to it |
| `virtual_scale/ASSUMPTIONS_AND_EXCEPTIONS.md:147, 152` | ⚠️ transducer €60–150 and platform ~€1,500 / €1.0–1.9k are simulator inputs. Add a note pointing to §2 |
| `europress_conclusions/sites/*` | ⚠️ ≈ 33 stale figures. Recommendation: don't submit these sites |
| `output/business_sources/**` | Historical drafts, deliberately not edited |
