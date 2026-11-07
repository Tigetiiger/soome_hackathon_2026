"""Build a temporary static results site into site/ (index.html + copied plots).

Re-runnable: only includes inputs that exist at build time.
Serve with: .venv/bin/python -m http.server 8765 -d site
"""
from __future__ import annotations

import json
import logging
import math
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
SIM_RUN = Path("runs/full400")
MODEL_RUNS = (Path("models/full400"), Path("models/bins25"))
SPLIT_LABEL = {"bins": "unseen machines", "time": "same machines, later months"}
LADDER_STEPS = ["naive_fill_x_density", "fill_presses", "pressure", "pressure_graph", "full_shared", "full_per_material", "full_selected"]
GOOD_PCT = 5.0
LIFT_TARGET_T = {"cardboard": "2–3.5", "paper": "2.5–4", "plastic_film": "1.2–2.2", "mixed_waste": "3–6 (assumed)"}
CAPTIONS = {
    "lifts": "Lifted mass per material and days between lifts.",
    "temperature": "Monthly mean temperature per region (synthetic weather).",
    "weather_effect": "Cardboard lift mass in wet vs dry weeks, by infeed type.",
    "pressure_vs_fill": "Hourly peak ram pressure vs true fill, coloured by true density.",
    "ladder": "Comparison ladder: what each signal adds.",
    "learning_curve": "Error at lift vs number of training machines.",
    "lift_error_by_material": "Error at lift by material.",
    "coverage_by_material": "80 % interval coverage by material.",
    "pred_vs_true": "Predicted vs true mass at lift",
    "mass_curves": "Hourly mass estimate with interval over the test period",
    "feature_importance": "Feature importance (gain)",
    "shap": "SHAP summary at lift",
}

CSS = """
:root{--bg:#f7f8fa;--fg:#1d2330;--muted:#5d6676;--card:#fff;--line:#dde1e8;--accent:#1f6feb;
--good:#d8f3dc;--good-fg:#14532d;--code:#eef1f5;--nav:rgba(255,255,255,.92)}
@media (prefers-color-scheme:dark){:root{--bg:#0f1318;--fg:#e4e8ee;--muted:#9aa4b2;--card:#181e26;
--line:#2c3440;--accent:#6ea8fe;--good:#173b26;--good-fg:#9be3b0;--code:#212a35;--nav:rgba(15,19,24,.92)}}
*{box-sizing:border-box}html{scroll-padding-top:4rem}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
nav{position:sticky;top:0;z-index:10;background:var(--nav);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
nav ul{display:flex;gap:1.2rem;margin:0 auto;padding:.7rem 16px;list-style:none;max-width:1100px;overflow-x:auto;white-space:nowrap}
nav a{color:var(--fg);text-decoration:none;font-weight:600;font-size:.95rem}nav a:hover{color:var(--accent)}
main{max-width:1100px;margin:0 auto;padding:0 16px 3rem}section{padding-top:2.2rem}
h1{font-size:clamp(1.6rem,4vw,2.4rem);line-height:1.2;margin:.4rem 0}h2{border-bottom:1px solid var(--line);padding-bottom:.3rem}
a{color:var(--accent)}p,li{max-width:75ch}.muted{color:var(--muted)}
.disclaimer{display:inline-block;background:var(--code);border-left:4px solid var(--accent);padding:.4rem .8rem;border-radius:4px}
.note{color:var(--muted);font-style:italic;border:1px dashed var(--line);padding:.5rem .8rem;border-radius:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));gap:.8rem;margin:1.2rem 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.9rem 1rem}
.kpi b{display:block;font-size:1.7rem;line-height:1.2}.kpi span{color:var(--muted);font-size:.88rem}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,460px),1fr));gap:1rem}
figure{margin:0;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.6rem}
img{max-width:100%;height:auto;display:block;margin:0 auto;background:#fff;border-radius:4px}
figcaption{font-size:.88rem;color:var(--muted);margin-top:.4rem}.tbl{overflow-x:auto;margin:.8rem 0}
table{border-collapse:collapse;font-size:.9rem;background:var(--card);min-width:50%}
th,td{border:1px solid var(--line);padding:.35rem .6rem;text-align:right}th{background:var(--code)}
td:first-child,th:first-child{text-align:left}td.good{background:var(--good);color:var(--good-fg);font-weight:600}
code{background:var(--code);padding:.1rem .3rem;border-radius:4px;font-size:.9em}
pre{background:var(--code);padding:.8rem;border-radius:6px;overflow-x:auto}pre code{padding:0}
.md{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.2rem 1.2rem;overflow-wrap:anywhere}
blockquote{margin:1rem 0;padding:.4rem 1rem;border-left:4px solid var(--accent);background:var(--code)}
footer{border-top:1px solid var(--line);margin-top:2rem;padding-top:1rem;font-size:.85rem;color:var(--muted)}
"""


@dataclass
class Build:
    """Tracks which inputs were used or missing during the build."""
    used: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    def check(self, rel: Path) -> Path | None:
        path = ROOT / rel
        (self.used if path.exists() else self.missing).append(str(rel))
        return path if path.exists() else None


# ---------------------------------------------------------------- formatting
def num(v: Any, nd: int = 1) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "–"
    return "–" if math.isnan(f) else f"{f:,.{nd}f}"


def sci(v: Any) -> str:
    return "–" if num(v) == "–" else f"{float(v):.1e}"


def pct_of(frac: Any, nd: int = 1) -> str:
    return "–" if num(frac) == "–" else num(float(frac) * 100, nd)


def dig(d: Any, *keys: str) -> Any:
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def note(text: str) -> str:
    return f'<p class="note">{escape(text)}</p>'


def table(header: list[str], rows: list[list[str]], good_cols: set[int] | None = None) -> str:
    """Cells are pre-formatted strings; numeric cells in good_cols < GOOD_PCT are highlighted."""
    head = "".join(f"<th>{escape(h)}</th>" for h in header)
    body = []
    for row in rows:
        cells = []
        for i, c in enumerate(row):
            hit = good_cols and i in good_cols and _below(c, GOOD_PCT)
            cells.append(f'<td{" class=good" if hit else ""}>{escape(c)}</td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def _below(cell: str, limit: float) -> bool:
    try:
        return float(cell.replace(",", "")) < limit
    except ValueError:
        return False


def _read(b: Build, rel: Path, reader: Any) -> Any:
    path = b.check(rel)
    try:
        return None if path is None else reader(path)
    except (OSError, ValueError) as exc:  # JSONDecodeError is a ValueError
        logging.warning("cannot read %s: %s", rel, exc)
        return None


def load_json(b: Build, rel: Path) -> dict | None:
    return _read(b, rel, lambda p: json.loads(p.read_text()))


def load_csv(b: Build, rel: Path) -> pd.DataFrame | None:
    return _read(b, rel, pd.read_csv)


# ---------------------------------------------------------------- tiny markdown
def md_inline(text: str) -> str:
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append(f"<code>{m.group(1)}</code>")
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", stash, escape(text))
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1" loading="lazy">', s)
    s = re.sub(r"\[([^\]]+)\]\(((?:https?://|#)[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\[([^\]]+)\]\([^)\s]+\)", r"\1", s)  # local file links: keep text only
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)


def md_to_html(md: str) -> str:
    """Headings, fenced code, tables, flat lists, paragraphs, inline bold/em/code/links/images."""
    out: list[str] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif line.startswith(">"):
            j = i
            while j < len(lines) and lines[j].startswith(">"):
                j += 1
            out.append("<blockquote>" + md_inline(" ".join(x.lstrip("> ") for x in lines[i:j])) + "</blockquote>")
            i = j
        elif m := re.match(r"(#{1,6})\s+(.*)", line):
            out.append(f"<h{len(m.group(1))}>{md_inline(m.group(2))}</h{len(m.group(1))}>")
            i += 1
        elif line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            i = _md_table(lines, i, out)
        elif re.match(r"\s*([*-]|\d+\.)\s+", line):
            i = _md_list(lines, i, out)
        elif not line.strip():
            i += 1
        else:
            j = i
            while j < len(lines) and lines[j].strip() and not re.match(r"(#|>|```|\s*\||\s*([*-]|\d+\.)\s)", lines[j]):
                j += 1
            j = max(j, i + 1)
            out.append("<p>" + md_inline(" ".join(lines[i:j])) + "</p>")
            i = j
    return "\n".join(out)


def _md_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _md_table(lines: list[str], i: int, out: list[str]) -> int:
    head = "".join(f"<th>{md_inline(c)}</th>" for c in _md_cells(lines[i]))
    j, rows = i + 2, []
    while j < len(lines) and lines[j].lstrip().startswith("|"):
        rows.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in _md_cells(lines[j])) + "</tr>")
        j += 1
    out.append(f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    return j


def _md_list(lines: list[str], i: int, out: list[str]) -> int:
    tag = "ol" if re.match(r"\s*\d+\.", lines[i]) else "ul"
    items: list[str] = []
    j = i
    while j < len(lines) and lines[j].strip():
        m = re.match(r"\s*(?:[*-]|\d+\.)\s+(.*)", lines[j])
        if m:
            items.append(m.group(1))
        elif items and lines[j].startswith((" ", "\t")):
            items[-1] += " " + lines[j].strip()
        else:
            break
        j += 1
    out.append(f"<{tag}>" + "".join(f"<li>{md_inline(t)}</li>" for t in items) + f"</{tag}>")
    return j


# ---------------------------------------------------------------- images
def copy_plots(b: Build, rel_dir: Path) -> list[Path]:
    """Copy rel_dir/*.png into site/rel_dir; return site-relative paths."""
    src = b.check(rel_dir)
    if src is None:
        return []
    dest = SITE / rel_dir
    dest.mkdir(parents=True, exist_ok=True)
    pngs = sorted(src.glob("*.png"))
    for p in pngs:
        shutil.copy2(p, dest / p.name)
    return [rel_dir / p.name for p in pngs]


def caption(stem: str) -> str:
    base, _, split = stem.rpartition("_")
    if base in CAPTIONS and split in SPLIT_LABEL:
        return f"{CAPTIONS[base]} — {SPLIT_LABEL[split]} ({split} split)."
    return CAPTIONS.get(stem, stem.replace("_", " "))


def figures(paths: list[Path]) -> str:
    if not paths:
        return note("Plots not generated yet.")
    figs = [
        f'<figure><a href="{escape(p.as_posix())}"><img src="{escape(p.as_posix())}" alt="{escape(p.stem)}" '
        f'loading="lazy"></a><figcaption>{escape(caption(p.stem))}</figcaption></figure>'
        for p in paths
    ]
    return f'<div class="figs">{"".join(figs)}</div>'


# ---------------------------------------------------------------- sections
def hero(metrics: dict | None, model_run: Path, summary: dict | None) -> str:
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
    shown = f"Soft-sensor numbers from <code>{escape(str(model_run))}</code>" if metrics else ""
    return f"""<section id="top"><h1>Compactor weight without a scale</h1>
<p>Waste compactors already know their fill level, how often they press and how hard the ram pushes. We
simulate a fleet of press containers hour by hour and train a <strong>hydraulic soft sensor</strong> that
turns those signals (plus public weather) into an estimate of the mass inside, every hour. The value just before
emptying lets a customer check the transporter's weighbridge figure without installing a load cell.</p>
<p class="disclaimer">All data is synthetic. Nothing here represents real Europress data or pressure settings.</p>
<div class="kpis">{kpis or note("No metrics available yet.")}</div><p class="muted">{shown}</p></section>"""


def simulator(b: Build, summary: dict | None) -> str:
    parts = ["""<section id="sim"><h2>Simulator</h2>
<p><code>compactor_sim</code> generates hourly telemetry and ground truth for a fleet of press containers (cardboard,
paper, plastic film, mixed plastic) across five Finnish regions. Weather (temperature, rain/snow, humidity, snowpack)
drives moisture: fibre absorbs humidity and rain carried in or falling through the hopper, which makes loads heavier and
softer. Inside each container the waste is tracked in daily layers whose density grows plastically with the highest
pack pressure it has seen; the ram pressure follows fill, density, moisture, frost and oil temperature, capped by the
relief valve. Sensors add noise, drift, dropouts and "false full" bridging; trucks are ordered when the fill reading
crosses a threshold and arrive hours later.</p>
<p>The ledger <em>start + material in + hopper precipitation − drained − seeped − side waste − lifted = end</em> is
checked per machine and closes to about 1e-9 kg.</p>"""]
    if summary is None:
        parts.append(note("runs/full400/summary.json not generated yet."))
    else:
        lm = summary.get("lift_mass_by_material") or {}
        rows = [[m, num(dig(v, "mean") / 1000 if isinstance(dig(v, "mean"), (int, float)) else None, 2),
                 LIFT_TARGET_T.get(m, "–"), num(dig(v, "count"), 0)] for m, v in lm.items()]
        parts.append("<h3>Lift mass by material</h3>" + table(["material", "mean lift (t)", "brief target (t)", "lifts"], rows))
        parts.append(f"<p>False-full-triggered lifts: <strong>{pct_of(summary.get('false_full_lift_share'))} %</strong> "
                     "of all lifts (the fill sensor read full because of bridging).</p>")
        mb = summary.get("mass_balance_kg") or {}
        parts.append("<h3>Mass balance (whole fleet, reported period)</h3>" +
                     table(["term", "kg"], [[k.removesuffix("_kg"), sci(v) if k == "residual_kg" else num(v, 0)]
                                            for k, v in mb.items()]))
    parts.append(baseline(b))
    parts.append("<h3>Validation plots</h3>" + figures(copy_plots(b, SIM_RUN / "plots")) + "</section>")
    return "".join(parts)


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


def ladder_tables(df: pd.DataFrame | None) -> str:
    if df is None or not {"split", "step", "material", "mean_pct"} <= set(df.columns):
        return note("comparison.csv not generated yet.")
    out = []
    for split, g in df.groupby("split", sort=False):
        piv = g.pivot_table(index="step", columns="material", values="mean_pct", aggfunc="first")
        order = [s for s in LADDER_STEPS if s in piv.index] + [s for s in piv.index if s not in LADDER_STEPS]
        cols = (["all"] if "all" in piv.columns else []) + [c for c in piv.columns if c != "all"]
        rows = [[s] + [num(piv.at[s, c]) for c in cols] for s in order]
        out.append(f"<h4>{escape(str(split))} — {escape(SPLIT_LABEL.get(str(split), ''))}</h4>"
                   + table(["step (mean % error at lift)"] + cols, rows, good_cols=set(range(1, len(cols) + 1))))
    return "".join(out)


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
    parts.append("<h3>Comparison ladder</h3><p>Same test lifts, adding one signal group at a time.</p>"
                 + ladder_tables(load_csv(b, model_run / "comparison.csv")))
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


def page(title: str, body: str, nav: str = "") -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title>'
            f"<style>{CSS}</style></head><body>{nav}{body}</body></html>")


def pick_model_run(b: Build) -> tuple[Path, dict | None]:
    for run in MODEL_RUNS:
        metrics = load_json(b, run / "metrics.json")
        if metrics:
            return run, metrics
    return MODEL_RUNS[0], None


def build() -> Build:
    b = Build()
    SITE.mkdir(exist_ok=True)
    model_run, metrics = pick_model_run(b)
    logging.info("model run shown: %s", model_run)
    summary = load_json(b, SIM_RUN / "summary.json")
    b.check(Path("README.md"))
    nav = ('<nav><ul><li><a href="#top">Overview</a></li><li><a href="#sim">Simulator</a></li>'
           '<li><a href="#model">Soft sensor</a></li><li><a href="#ai">How the AI built it</a></li></ul></nav>')
    body = ("<main>" + hero(metrics, model_run, summary) + simulator(b, summary)
            + soft_sensor(b, metrics, model_run) + ai_section(b) + footer(b) + "</main>")
    (SITE / "index.html").write_text(page("Compactor Soft Sensor", body, nav))
    return b


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    b = build()
    logging.info("wrote %s", SITE / "index.html")
    for m in dict.fromkeys(b.missing):
        logging.info("missing at build time: %s", m)


if __name__ == "__main__":
    main()
