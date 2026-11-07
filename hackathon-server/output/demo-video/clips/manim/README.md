# Manim clips for the demo video

| Clip | Length | Scene | Data tag |
|---|---|---|---|
| `problem.mp4` | 15.0 s, 450 frames | `src/problem.py` → `Problem` | practice data |
| `solution.mp4` | 13.0 s, 390 frames | `src/solution.py` → `Solution` | simulated |
| `impact.mp4` | 25.0 s, 750 frames | `src/impact.py` → `Impact` | practice data · estimate |

All clips are 1920×1080, 30 fps, H.264 yuv420p, no audio. Captions are not rendered; nothing important is placed in the bottom 180 px.

Render: `src/render.sh` (final) or `src/render.sh preview` (480p check). It uses Manim CE 0.22.1 from `output/animation-comparison/.venv` and pads or trims each clip to its exact frame count with ffmpeg. QC stills and contact sheets: `qc/`.

## Where every number on screen comes from

Small JSON files in `src/data/` were exported once from the sources below. The scenes read only those files and assert the key counts.

### problem.mp4
| On screen | Value | Source |
|---|---|---|
| Customer, 3 sites, 9 machines | Hospitality Customer 0049 | `europress-dashboard/public/data/customers/ORG-0049.json` → `customer` (`n_sites`, `n_devices`); also `reference/customers.parquet`, `reference/devices.parquet` |
| 395 dots (date × fill at emptying) | 395 pickups | practice dataset `data/competition/public/operations/collection_events.parquet`, `customer_id == ORG-0049`, `status in {COMPLETED, PARTIAL}` → `src/data/org0049_pickups.json`. Matches `ORG-0049.json` `kpis.lifts` = 395 |
| 48 blue dots / "48 of 395 with a weighing ticket" | 48 | same rows, `weight_reconciliation_status` ≠ `WEIGHBRIDGE_NOT_AVAILABLE` (37 `WITHIN_10PCT` + 11 `DIFFERENCE_GT_10PCT`). Matches `weight.with_ticket` = 48, `verified_within_10pct` = 37, `difference_gt_10pct` = 11, `device_only` = 347 |
| avg fill at emptying 49 % | 49.2 → 49 | mean of `device_fill_pct_before` over the 394 rows with a reading. Matches `kpis.avg_fill` = 49 |

One of the 395 pickups (`COL-00432-0021`, no ticket) has no fill reading. Its dot sits on the 49 % average line.

### solution.mp4
| On screen | Value | Source |
|---|---|---|
| Pressure curves (26 strokes, 16 samples each), fill 8 % → 95 % | — | `simulator-weather-and-stuff/runs/full400/pressure_curves.parquet`, machine `BIN-0001` (cardboard), joined to `hourly.parquet` `true_fill_pct` for the stroke's hour; one stroke picked nearest to each of 26 evenly spaced fill levels → `src/data/pressure_curves_bin0001.json` |
| Error ladder 32.1 / 7.0 / 5.9 / 5.7 / 5.3 % | mean_pct | `simulator-weather-and-stuff/models/full400/comparison.csv`, `split = bins`, `material = all`, steps `naive_fill_x_density`, `fill_presses`, `pressure`, `pressure_graph`, `full_selected` → `src/data/comparison_bins.json` |
| "same machines, later months: 3.7 %" | 3.75 → 3.7 | same file, `split = time`, `full_selected`; `models/full400/REPORT.md:3` |

### impact.mp4
| On screen | Value | Source |
|---|---|---|
| €140,574 a year | | `ORG-0049.json` → `kpis.total_cost` |
| €60,471 saveable (43 %) | 60,471 / 140,574 | `kpis.savings` |
| Levers €39,955 / €6,386 / €6,318 / €5,881 / €1,931 | sum = €60,471 | `levers[].saving_eur` (`early_lifts`, `tender`, `sorting`, `avoidable_fees`, `invoice_check`) |
| 74 % → 97 % pickups with an independent weight | 0.743, 0.971 | `soome_hackathon_2026/analysis/outputs/09_summary.log:3`; NUMBERS.md §4 |
| +1 pp ≈ 120 machines ≈ €21,600 / year | 12,000 / 100 × €15 × 12 | NUMBERS.md §6; `europress_conclusions/BUSINESS_PLAN.md:103` (~12k fleet, +1 pp ≈ 120 devices) [A]; `europress_conclusions/BUSINESS_CASE.md:7,68` (€15 per device per month list) |
| Hardware study: pressure-only P95 error 29 % | 29.0 % | `europress_conclusions/smartweight/SENSOR_RESEARCH.md:138`; NUMBERS.md §1 |
| "archived SMART pressure curves from 10–30 machines" | 10–30 | `output/05_business_plan_addon.md:117` (Phase 0a: "a €0 test on archived pressure data from 10–30 machines against their tickets"); NUMBERS.md §1 one-liner |

All data is synthetic: Europress practice data plus our simulator. Prices are hypothetical.
