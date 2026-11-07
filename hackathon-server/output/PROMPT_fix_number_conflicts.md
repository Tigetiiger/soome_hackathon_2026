# Prompt: fix the number conflicts before the demo video

You are working in `/home/hackathon`, on the Europress × Since AI 2026 hackathon project. All data is synthetic: practice data from Europress, plus our own simulator. Today is 7 Nov 2026, and the demo video is due on the final day.

Several published documents and app screens disagree about key numbers. Judges will see these numbers in a 2-minute video, so every figure must be consistent, sourced and labelled. Fix the five issues below.

**Do not make any videos or animations.** Do not change the models or rerun the simulator. This is a consistency and wording pass only.

## Where things live

| Path | What it is |
|---|---|
| `output/04_business_findings_explained.md`, `output/04_business_findings_and_decisions.md` | Earlier findings (source of the "96 %") |
| `output/05_business_plan_addon.md` + `.html` | Business plan. The `.html` is also published at https://claude.ai/artifact/MeVR2iDqkQvdfK25AYEpMp |
| `output/06_problems_solutions_why.md` | Problems → solutions, plain-language |
| `europress-dashboard/` | The app: Node server on port 8080, data built by `pipeline/build_data.py` into `public/data/`, UI in `public/js/` |
| `europress-dashboard/public/data/customers/ORG-0049.json` | Hero customer "Hospitality Customer 0049" |
| `europress-dashboard/public/data/softsensor/evaluation.json` | Soft-sensor metrics the app shows |
| `simulator-weather-and-stuff/` | Simulator and model. The `models/full400/metrics.json` and `REPORT.md` are the source of truth for accuracy |
| `simulator-weather-and-stuff/make_site.py` | Builds the site served at http://100.87.158.27:8765, from `site/` |
| `simulator-weather-and-stuff/AI_WORK_SUMMARY.md` | Rendered on that site as "How the AI built it" |

Leave historical drafts as they are, but list any stale figures you find in them: `output/business_sources/**`, plus anything under `node_modules`.

## Issues to fix

### 1. Soft-sensor accuracy: 4.7 % vs 5.3 %

- **Old figure.** `05` and `06` say the simulator soft sensor reaches **4.7 %** mean error on unseen machines, with "61 % within ±5 %".
- **Current figure.** The deployed model (`models/full400`, shown on the site and in the app) has these results:

  | Split | Mean error at lift | Within 5 % | Coverage of 80 % interval |
  |---|---|---|---|
  | Unseen machines (`bins`) | **5.3 %** | 55.4 % | 77.1 % |
  | Same machines, later months (`time`) | **3.7 %** | 72.7 % | 78.4 % |

**Task:**
1. Confirm these values in `models/full400/metrics.json` and `europress-dashboard/public/data/softsensor/evaluation.json`.
2. Find where 4.7 % came from (an earlier run? the plastic-film row?), and say so in your report.
3. Replace 4.7 % and its companion figures everywhere in `05` (md and html) and `06` with the full400 numbers. Name the split each time: "5.3 % on machines the model never saw".
4. Check the weight-ladder table in `05` §4 ("≈ 4–7 % mean per pickup", "≈ 3.5 % after 5 tickets") and keep it consistent with the new figures.

### 2. "9 % → 96 %" compares two different things

- The **9 %** is pickups with a weighing ticket the customer can see: 37 of 395 (`weight.verified_within_10pct` in `ORG-0049.json`; the trace value is 9.4 %).
- The **96 %** comes from `04`, where it is the share of **weight-based billing** the customer can check: "77 % today, 96 % with machine weight".
- `05` and `06` present them as one before/after pair ("check 96 % of its pickups instead of 9 %"). That is wrong.

**Task:**
1. Find how `04` computed 77 % and 96 %. Search `soome_hackathon_2026/analysis/` and `output/business_sources/`.
2. Decide on one consistent before/after pair with the same denominator, and say which you chose and why. Choose one of:
   - **(a) Pickups.** Compute the "with machine weight" share of the 395 pickups from the hero's data, defining "checkable" explicitly.
   - **(b) Billing.** Use 77 % → 96 % of weight-based billing.

   Prefer (a) if it can be computed honestly from the data. It matches the 37-of-395 story the video opens with.
3. Update every place that states the pair: `05` md and html (including the `9 % → 96 %` stat tile), `06` Problem 1, and the §2 table in `05` ("Checkable pickups 9 % → 90 %+").

### 3. The notice date reads as already missed

- The hero's contract card says Hauler Delta's notice is due by **17 Oct 2026**. Today is 7 Nov 2026.
- The data runs to 30 Sep 2026, and `europress-dashboard/pipeline/build_data.py` uses `TODAY = pd.Timestamp("2026-10-01")`, so the app is internally consistent. The problem is that nothing tells the viewer the date the data stands at.

**Task:**
1. Make the as-of date visible wherever a date-relative claim appears:
   - the contract or service card;
   - the `tender_window` insight;
   - the Account page;
   - the operators table.
   For example: "Data as of 30 Sep 2026" in the header, or "(as of 30 Sep 2026)" on the card. Use the existing i18n strings in `public/js/i18n.js` and add both EN and FI.
2. Remove the hardcoded `new Date("2027-04-01")` "soon" cut-offs in `public/js/app.js:231` and `public/js/account.js:54`. Derive them from the data's as-of date, which the pipeline should export into the JSON (for example in `period`), not from the browser clock.
3. In `05` and `06`, phrase the date as "notice due 17 Oct 2026 (data as of 30 Sep 2026)".

### 4. State the accuracy conflict honestly, and consistently

`05` §4 and `06` Problem 1 already say that the hardware study finds pressure-only estimates off by about 29 % at the 95th percentile, which conflicts with the simulator.

**Task:**
1. Make sure the conflict appears in one consistent sentence in `05`, `06` and the app's soft-sensor "How" page (`public/js/sensor/how.js` and `strings.js`). Use the corrected 5.3 % figure.
2. Include the resolution: "a €0 test on archived pressure data from 10–30 machines against their tickets decides it".
3. Do not soften either number.

### 5. The "How the AI built it" section on the simulator site is out of date

`AI_WORK_SUMMARY.md` contradicts the current simulator documented on the same page:

| Topic | `AI_WORK_SUMMARY.md` says | Current page and config say |
|---|---|---|
| Pressure onset | Pressure starts at 30 % fill, exponent 1.6 | Starts at 7 % fill (`fill_onset 0.07`), linear |
| Density exponent | 1.5 | 1.0 |
| Waste stream | "mixed plastic", c = 0.30 | `mixed_waste`, c = 0.12 |
| False-full lifts | 6 % | 10.2 % |
| Pipeline status | "in progress" | Finished: 5.3 % / 3.7 % |

**Task:**
1. Update `AI_WORK_SUMMARY.md` against `runs/full400/config_used.yaml`, `validate_report.txt` and `models/full400/metrics.json`. Label superseded early results as "before recalibration", or remove them.
2. Rebuild the site with `make_site.py`.
3. Check that the page served on port 8765 shows no contradiction.

## Rules

- **Every figure needs a source.** Each number you write must trace to a file you read. Quote the file and key in your report.
- **Keep the evidence tags** used in `05`: [P] practice data, [S] simulator, [E] estimate, [A] assumption, [R] real public data. Tag any number you add.
- **Keep both languages in step.** EN and FI strings must stay in sync in the app.
- **Regenerate and verify the app.** After changing the pipeline:
  1. Regenerate the data with the project's own build command (check `europress-dashboard/README` or `bin/`).
  2. Load the app at http://localhost:8080 and screenshot the Answers home, the Contract card and the soft-sensor page.
  3. Confirm that the console shows no errors.
- **Do not republish the artifact.** Do not republish https://claude.ai/artifact/MeVR2iDqkQvdfK25AYEpMp or push or commit anything without asking me first. Update the local `05_business_plan_addon.html` only.
- **Do not edit the historical drafts.** Leave `output/business_sources/**` unchanged.

## Report back with

1. A table with these columns:
   - issue
   - old text
   - new text
   - file:line
   - source of the new number
2. Your choice for issue 2, and why.
3. Where 4.7 % came from.
4. Stale figures left in the historical drafts, listed but not edited.
5. Screenshots or check results for the app and the site.
6. Anything you could not resolve, stated plainly.
