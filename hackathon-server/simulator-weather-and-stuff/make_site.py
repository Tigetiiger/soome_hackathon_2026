"""Build the static results site into site/ (index.html + copied and generated plots).

Re-runnable: only includes inputs that exist at build time. Helpers live in site_common.py, the
"Simulation in detail" section in site_sections.py and "What goes into the model" in site_model.py.

    .venv/bin/python make_site.py [--model-run models/bins25]

Serve with: .venv/bin/python -m http.server 8765 -d site
"""
from __future__ import annotations

import argparse
import logging
import re
import shutil
from datetime import datetime
from html import escape
from pathlib import Path

import pandas as pd

from site_common import (GOOD_PCT, ROOT, SITE, SPLIT_LABEL, Build, copy_plots, dig, figures, load_csv, load_json,
                         md_to_html, note, num, page, pct_of, sci, table)
from site_model import model_inputs
from site_sections import simulation_detail

SIM_RUN = Path("runs/full400")
PREFERRED_MODEL, FALLBACK_MODEL = Path("models/full400"), Path("models/bins25")
NAV = (("top", "Overview"), ("sim", "Simulation"), ("inputs", "Model inputs"), ("model", "Soft sensor"),
       ("ai", "How the AI built it"))


# ---------------------------------------------------------------- sections
def hero(metrics: dict | None, model_run: Path, summary: dict | None, choice: str) -> str:
    cards = []
    for split, sp in (dig(metrics, "splits") or {}).items():
        lift = dig(sp, "final", "lift", "overall") or {}
        cards.append((f"{num(lift.get('mean_pct'))} %", f"mean error at lift — {SPLIT_LABEL.get(split, split)} "
                      f"({pct_of(lift.get('coverage'), 0)} % inside 80 % interval)"))
    naive = dig(metrics, "splits", "bins", "ladder", "naive_fill_x_density", "overall", "mean_pct")
    if naive is not None:
        cards.append((f"{num(naive)} %", "naive fill × density error (what pressure fixes)"))
    if summary:
        cards.append((f"{sci(summary.get('mass_balance_max_abs_residual_kg'))} kg",
                      "simulator mass-balance residual (max, per bin)"))
        cards.append((f"{summary.get('n_bins', '–')} machines",
                      f"{num(summary.get('hourly_rows'), 0)} hourly rows · {num(summary.get('n_lifts'), 0)} lifts · "
                      f"{summary.get('days', '–')} days (simulator run {SIM_RUN})"))
    kpis = "".join(f'<div class="kpi"><b>{escape(v)}</b><span>{escape(t)}</span></div>' for v, t in cards)
    data = dig(metrics, "data") or "?"
    shown = (f'<p class="banner"><strong>Model run shown:</strong> <code>{escape(str(model_run))}</code> (trained on '
             f"<code>{escape(str(data))}</code>, {dig(metrics, 'compute', 'machines') or '–'} machines). "
             f"{escape(choice)} Simulator sections show <code>{escape(str(SIM_RUN))}</code>.</p>")
    return f"""<section id="top"><h1>Compactor weight without a scale</h1>
<p>Waste compactors already know their fill level, how often they press and how hard the ram pushes. We
simulate a fleet of press containers hour by hour and train a <strong>hydraulic soft sensor</strong> that
turns those signals (plus public weather) into an estimate of the mass inside, every hour. The value just before
emptying lets a customer check the transporter's weighbridge figure without installing a load cell.</p>
<p class="disclaimer">All data is synthetic. Nothing here represents real Europress data or pressure settings.</p>
{shown}<div class="kpis">{kpis or note("No metrics available yet.")}</div></section>"""


def baseline(b: Build) -> str:
    data = load_json(b, SIM_RUN / "baseline_results.json")
    if not data:
        return ""
    rows = [[k, num(v.get("mean_ape_pct")), num(v.get("median_ape_pct")), num(v.get("p90_ape_pct")), num(v.get("mae_kg"), 0)]
            for k, v in data.items() if isinstance(v, dict) and "mean_ape_pct" in v]
    return ("<h3>First baseline (5-fold CV grouped by machine)</h3><p>What each feature group adds to a plain LightGBM "
            "model of lift mass. Pressure is the big win.</p>"
            + table(["features", "mean %", "median %", "p90 %", "MAE kg"], rows, good_cols={1}))


def split_table(sp: dict) -> str:
    lift = dig(sp, "final", "lift") or {}
    groups = {"all": lift.get("overall") or {}, **(lift.get("by_material") or {})}
    rows = [[m, num(g.get("n"), 0), num(g.get("mae_kg"), 0), num(g.get("mean_pct")), num(g.get("median_pct")),
             pct_of(g.get("within_5pct")), num(g.get("bias_kg"), 0), pct_of(g.get("coverage")), num(g.get("width_kg"), 0)]
            for m, g in groups.items()]
    head = ["material", "lifts", "MAE kg", "mean %", "median %", "within 5 % (%)", "bias kg", "coverage %", "width kg"]
    return table(head, rows, good_cols={3, 4})


def learning_table(df: pd.DataFrame | None) -> str:
    if df is None or not {"n_machines", "material", "mean_pct"} <= set(df.columns):
        return note("learning_curve.csv not generated yet.")
    piv = df.pivot_table(index="n_machines", columns="material", values="mean_pct", aggfunc="first")
    cols = (["all"] if "all" in piv.columns else []) + [c for c in piv.columns if c != "all"]
    rows = [[str(n)] + [num(piv.at[n, c]) for c in cols] for n in piv.index]
    return table(["training machines (mean % at lift)"] + cols, rows, good_cols=set(range(1, len(cols) + 1)))


def report_page(b: Build, model_run: Path) -> str:
    src = b.check(model_run / "REPORT.md")
    if src is None:
        return note(f"{model_run}/REPORT.md not generated yet.")
    dest = SITE / model_run
    dest.mkdir(parents=True, exist_ok=True)
    text = src.read_text()
    shutil.copy2(src, dest / "REPORT.md")
    body = f'<main><p><a href="../../index.html#model">← back</a></p><div class="md">{md_to_html(text)}</div></main>'
    (dest / "REPORT.html").write_text(page(f"Report {model_run.name}", body))
    rel = (model_run / "REPORT.html").as_posix()
    return f'<p>Full generated report: <a href="{rel}">REPORT ({escape(model_run.name)})</a> · ' \
           f'<a href="{(model_run / "REPORT.md").as_posix()}">raw markdown</a></p>'


def soft_sensor(b: Build, metrics: dict | None, model_run: Path) -> str:
    parts = [f"""<section id="model"><h2>Soft sensor results <span class="muted">({escape(str(model_run))})</span></h2>
<p><code>weight_train</code> trains LightGBM models on kg per m³ of container from fill, press counts, ram pressure, oil
temperature and weather, with p10/p90 quantile models widened by conformal calibration into an 80 % interval. The
number that matters is the estimate just before a lift, compared with the weighbridge. Cells under {GOOD_PCT:.0f} %
are highlighted.</p>"""]
    if metrics is None:
        parts.append(note("No metrics.json found for any model run yet."))
    for split, sp in (dig(metrics, "splits") or {}).items():
        desc = sp.get("description", "")
        parts.append(f"<h3>Split <code>{escape(split)}</code> — {escape(SPLIT_LABEL.get(split, split))}</h3>"
                     f"<p class=muted>{escape(desc)}; {sp.get('n_train_machines', '–')} train / "
                     f"{sp.get('n_test_machines', '–')} test machines.</p>" + split_table(sp))
    if b.check(model_run / "comparison.csv"):
        parts.append('<h3>Comparison ladder</h3><p>See <a href="#inputs">What goes into the model</a> for the ladder '
                     f'with the feature set of each step; raw numbers: <a href="{(model_run / "comparison.csv").as_posix()}">'
                     "comparison.csv</a>.</p>")
        dest = SITE / model_run
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "comparison.csv").write_bytes((ROOT / model_run / "comparison.csv").read_bytes())
    parts.append("<h3>Learning curve</h3>" + learning_table(load_csv(b, model_run / "learning_curve.csv")))
    parts.append("<h3>Report</h3>" + report_page(b, model_run))
    parts.append("<h3>Plots</h3>" + figures(copy_plots(b, model_run / "plots")) + "</section>")
    return "".join(parts)


def ai_section(b: Build) -> str:
    head = """<section id="ai"><h2>How the AI built this</h2>
<p>The simulator, the training pipeline and this page were written by an AI coding assistant working from the
hackathon brief. Below is its own account of the work.</p>"""
    src = b.check(Path("AI_WORK_SUMMARY.md"))
    if src is None:
        return head + note("AI_WORK_SUMMARY.md not generated yet.") + "</section>"
    text = src.read_text()
    topics = [re.sub(r"[*`]", "", h) for h in re.findall(r"^##\s+(.+)$", text, flags=re.M)]
    toc = ("<p><strong>Covers:</strong> " + escape(" · ".join(topics)) + "</p>") if topics else ""
    return f'{head}{toc}<div class="md">{md_to_html(text)}</div></section>'


def footer(b: Build) -> str:
    used = "".join(f"<li><code>{escape(s)}</code></li>" for s in dict.fromkeys(b.used))
    missing = "".join(f"<li><code>{escape(s)}</code></li>" for s in dict.fromkeys(b.missing))
    return (f"<footer><p>Built {escape(datetime.now().strftime('%Y-%m-%d %H:%M'))} by <code>make_site.py</code>. "
            "Synthetic data only.</p><details><summary>Source files used</summary><ul>" + used + "</ul></details>"
            + (f"<details><summary>Not available at build time</summary><ul>{missing}</ul></details>" if missing else "")
            + "</footer>")


def newer(a: Path, b: Path) -> bool:
    try:
        return a.stat().st_mtime > b.stat().st_mtime
    except OSError:
        return False


def default_model_run() -> tuple[Path, str]:
    """models/full400 only if its metrics.json is newer than the simulator data it was trained on."""
    pref, data = ROOT / PREFERRED_MODEL / "metrics.json", ROOT / SIM_RUN / "hourly.parquet"
    if newer(pref, data):
        return PREFERRED_MODEL, f"Chosen by default: {PREFERRED_MODEL}/metrics.json is newer than {SIM_RUN} data."
    why = "is older than" if pref.exists() else "is missing vs"
    return FALLBACK_MODEL, (f"Chosen by default: {PREFERRED_MODEL}/metrics.json {why} {SIM_RUN}/hourly.parquet "
                            "(stale or still training), so the freshly trained bins25 model is shown.")


def build(model_run: Path | None = None) -> Build:
    b = Build()
    SITE.mkdir(exist_ok=True)
    if model_run is None:
        model_run, choice = default_model_run()
    else:
        choice = "Chosen with --model-run."
    metrics = load_json(b, model_run / "metrics.json")
    data_run = Path(dig(metrics, "data") or "runs/bins25")
    logging.info("model run shown: %s (data %s)", model_run, data_run)
    summary = load_json(b, SIM_RUN / "summary.json")
    b.check(Path("README.md"))
    nav = "<nav><ul>" + "".join(f'<li><a href="#{a}">{escape(t)}</a></li>' for a, t in NAV) + "</ul></nav>"
    body = ("<main>" + hero(metrics, model_run, summary, choice)
            + simulation_detail(b, SIM_RUN, summary, baseline(b))
            + model_inputs(b, metrics, model_run, data_run)
            + soft_sensor(b, metrics, model_run) + ai_section(b) + footer(b) + "</main>")
    (SITE / "index.html").write_text(page("Compactor Soft Sensor", body, nav))
    return b


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-run", type=Path, default=None,
                    help=f"trained model folder to show (default: {PREFERRED_MODEL} if its metrics.json is newer "
                         f"than {SIM_RUN}/hourly.parquet, else {FALLBACK_MODEL})")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    run = args.model_run
    if run is not None and run.is_absolute():
        run = run.relative_to(ROOT)
    b = build(run)
    logging.info("wrote %s", SITE / "index.html")
    for m in dict.fromkeys(b.missing):
        logging.info("missing at build time: %s", m)


if __name__ == "__main__":
    main()
