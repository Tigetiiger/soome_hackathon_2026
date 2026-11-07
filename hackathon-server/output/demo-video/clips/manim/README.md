# Manim clips for the demo video

| Clip | Length | Scene | Data tag |
|---|---|---|---|
| `problem.mp4` | 15.0 s, 450 frames | `src/problem.py` → `Problem` | practice data |
| `solution.mp4` | 13.0 s, 390 frames | `src/solution.py` → `Solution` | simulated |
| `impact.mp4` | 25.0 s, 750 frames | `src/impact.py` → `Impact` (v2) | practice data · estimate |

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

### impact.mp4 (v2, 7 Nov 2026 — the v1 table is in impact_v1.mp4's era, see timeline_v1.json)
All values come from `src/data/impact_v2.json`, written by `src/export_impact_v2.py` from the dashboard data that business.html quotes.

| On screen | Value | Source |
|---|---|---|
| €140,574 waste cost | | `ORG-0049.json` → `kpis.total_cost` |
| €52,154 SMART can save (37 %) | 52,154 / 140,574 | `kpis.savings` |
| Levers €39,955 / €6,318 / €5,881 | sum = €52,154 | `levers[].saving_eur` (`early_lifts`, `sorting`, `avoidable_fees`) |
| SMART fee 25 % = €13,038; keeps €39,116 | round(52,154 × 0.25) | demo share, business.html §4 (the live sales brief says the same) |
| €1.25M savings, 52 demo customers | €1,245,163 | Σ `customers/*.json` → `kpis.savings` |
| 3,945 fewer truck trips, 5 demo partners | 676 + 714 + 333 + 745 + 1,477 | Σ `operators/OP-*.json` → `value.trips_saved_year` |
| ≈ €311k SMART fees | 1,245,163 × 0.25 | business.html §0 |
| load cells on 10 machines ≈ €34–63k | €3.4–6.3k per machine installed | business.html §7, Table 4 (estimate) |

The problem clip's v2 labels: "operator weighs / at the weighbridge, after the truck has left" and "SMART compactor" (was "hauler weighs / and is paid per tonne", "compactor with fill sensor").

All data is synthetic: Europress practice data plus our simulator. Prices are hypothetical.
