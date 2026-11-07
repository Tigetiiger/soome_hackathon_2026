"""Website section: one material's error vs number of training machines (weight_train curve)."""
from __future__ import annotations

import shutil
from html import escape
from pathlib import Path

from site_common import SITE, Build, figures, load_json, note, num, pct_of, table

TARGET = 5.0


def _interpretation(res: dict) -> str:
    pts = res["points"]
    unseen = [(p["n_machines"], p["unseen"]["mean_pct"]) for p in pts]
    best_n, best = min(unseen, key=lambda t: t[1])
    first_ok = next((n for n, v in unseen if v < TARGET), None)
    near = next(n for n, v in unseen if v <= best + 0.5)
    parts = [f"With a single training machine the {res['material']} model is off by {num(unseen[0][1])} % on unseen "
             f"machines (naive fill × density: {num(res.get('naive_unseen_mean_pct'))} %).",
             f"The best is {num(best)} % (at {best_n} machines); within 0.5 pp of that already at {near} machines."]
    parts.append(f"The 5 % target on unseen machines is first met at {first_ok} machines." if first_ok
                 else "The 5 % target on unseen machines is not reached with the machines available.")
    parts.append(f"On the machines it was trained on (later months) the error is {num(pts[0]['same']['mean_pct'])} % "
                 f"with {pts[0]['n_machines']} machine(s): a model learns its own installation quickly.")
    return " ".join(parts)


def _copy_png(b: Build, model_run: Path, material: str) -> list[Path]:
    rel = model_run / "plots" / f"material_curve_{material}.png"
    src = b.check(rel)
    if src is None:
        return []
    dest = SITE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return [rel]


def _one_material(b: Build, model_run: Path, res: dict) -> str:
    mat = res["material"]
    ref = res.get("reference_model", {})
    out = [f"<h3>{escape(mat)}</h3>",
           f"<p>A {escape(mat)}-only model is trained on 1, 2, 4, 8, … of the {res['train_pool_machines']} "
           f"{escape(mat)} training machines, using the tuned per-material settings of the 400-machine model "
           f"({escape(str(ref.get('params')))}, {ref.get('best_iter')} trees, {res.get('n_features')} features incl. "
           f"the pressure graph). Everything, including the pressure inversion, is fitted on those machines only. "
           f"<b>Unseen</b>: always the same {res['test_machines']} held-out machines ({res['test_lifts_unseen']} "
           f"lifts from {escape(res['test_start'][:10])}). <b>Same</b>: the training machines themselves in the last "
           f"25 % of the year. Small sizes are repeated with different machine draws; the band and the range show "
           f"how much the result depends on which machines happen to be picked.</p>",
           f"<p>{escape(_interpretation(res))}</p>",
           figures(_copy_png(b, model_run, mat))]
    rows = [[str(p["n_machines"]), str(p["repeats"]), num(p["unseen"]["mean_pct"]),
             f"{num(p['unseen']['min_pct'])}–{num(p['unseen']['max_pct'])}", pct_of(p["unseen"]["within_5pct"], 0),
             num(p["same"]["mean_pct"]), pct_of(p["same"]["within_5pct"], 0)] for p in res["points"]]
    out.append(table(["training machines", "repeats", "unseen: mean % err", "range over repeats",
                      "unseen: within 5 %", "same: mean % err", "same: within 5 %"], rows, good_cols={2, 5}))
    out.append(note(f"Mean % error at lift (hour before emptying). Naive fill × density on the unseen set: "
                    f"{num(res.get('naive_unseen_mean_pct'))} %. Compute: {res.get('wall_s')} s."))
    return "".join(out)


def material_curve_section(b: Build, model_run: Path) -> str:
    files = sorted((Path(__file__).resolve().parent / model_run).glob("material_curve_*.json"))
    head = '<section id="curve"><h2>How many machines does a model need? (one material)</h2>'
    if not files:
        return head + note("Not generated yet: run python -m weight_train curve --data runs/full400 "
                           "--models models/full400 --material cardboard") + "</section>"
    parts = [_one_material(b, model_run, res) for res in (load_json(b, model_run / f.name) for f in files) if res]
    return head + "".join(parts) + "</section>"
