# Prompt: update the website data

Update the technical-documentation website so that every number, table and figure reflects the
**current** simulator data and trained models. All its content is generated from data files; never
edit numbers in the HTML by hand.

**Where:** project root `/home/hackathon/simulator-weather-and-stuff/` (run everything from there with
`.venv/bin/python`). The site is built into `site/` and is already served live at
`http://100.87.158.27:8765/` by a running `http.server`. Don't start or stop that server; a rebuild
shows up immediately. A clean copy of the project lives in `compactor-soft-sensor/`.

## 1. Decide what changed, then run only the steps needed (in this order)

| what changed | start at step |
|---|---|
| simulator code or `config.yaml` | A |
| model code (`weight_train/`) or training settings | B |
| only plotting code, or a model was retrained elsewhere | D |
| only website code (`make_site.py`, `site_*.py`) | E |

- **A. Simulate** (about 30 s + 8 s): `python -m compactor_sim --bins 400 --days 365 --seed 7 --out runs/full400` and
  `python -m compactor_sim --bins 25 --days 365 --seed 7 --out runs/bins25`, then
  `python validate.py runs/full400 > runs/full400/validate_report.txt` and
  `python baseline.py runs/full400 > runs/full400/baseline_report.txt`.
- **B. Train** (about 15 min + 4 min, about 4.5 GB RAM): `python -m weight_train train --data runs/full400 --out models/full400`
  and `python -m weight_train train --data runs/bins25 --out models/bins25`.
- **C. Predict + curve** (about 1.5 min + 6 min):
  `python -m weight_train predict --models models/full400 --input runs/full400/hourly.parquet --output models/full400/predictions.parquet`,
  then `python -m weight_train report --models models/full400` (so the report includes the prediction timing), then
  `python -m weight_train curve --data runs/full400 --models models/full400 --material cardboard`.
- **D. High-resolution figures** (about 25 s): `python make_hires_plots.py`.
- **E. Build the site** (about 10 s): `python make_site.py`. It shows `models/full400` only if its `metrics.json` is
  newer than `runs/full400/hourly.parquet`; otherwise it falls back to `models/bins25`. If you simulated (A), you must
  also train (B) before building.

Long steps: run them in the background and wait for completion; don't poll with sleep loops.

## 2. Verify

- `make_site.py` logs "19 figures, 19 with a hi-res twin" (or the new count) and the model run `models/full400`.
- `site/index.html` parses with balanced tags. Every `img src`, `data-src`, hi-res link and download exists under `site/`.
- The visible text contains no local paths (`models/`, `runs/`, `/home`, `.py`, `.parquet`) and no interview or expert wording.
- The headline numbers on the page match `models/full400/metrics.json` → `splits.<time|bins>.final.lift.overall.mean_pct`.
- `curl -s -o /dev/null -w '%{http_code}' http://100.87.158.27:8765/` returns 200.
- `python -m pytest -q` passes.

## 3. Sync the clean submission folder

Copy into `compactor-soft-sensor/`:
- changed code (`compactor_sim/`, `weight_train/`, `make_site.py`, `site_*.py`, `make_hires_plots.py`, `validate.py`, `baseline.py`, `config.yaml`, `tests/`),
- `runs/` and `models/`: only the bundle-referenced model `.txt` files, no `predictions.parquet`,
- the built site: `rm -rf compactor-soft-sensor/site && cp -r site compactor-soft-sensor/site` (rsync is not installed).

Then update any numbers quoted in `compactor-soft-sensor/README.md` (headline, results tables, ladder, learning
and machines-needed curves, mixed-waste coverage) from the new `metrics.json` and
`material_curve_cardboard.json`. Run `../.venv/bin/python -m pytest -q` inside the folder.

## 4. Publish (only if asked)

The submission lives on the orphan branch `ai-stuff` of `Tigetiiger/soome_hackathon_2026`, which holds code, docs
and the built `site/`, but no `runs/` or `models/`. To update it:
1. `git worktree add /tmp/ai-stuff-wt ai-stuff`
2. replace the worktree content with `compactor-soft-sensor/` minus `runs/`, `models/` and caches
3. commit with a conventional message ending in `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
4. `git push hackathon ai-stuff`, then remove the worktree

Never touch the `compactor-sim` branch unless asked. Report what was run, the new headline numbers (both
splits, per material) and anything that failed.
