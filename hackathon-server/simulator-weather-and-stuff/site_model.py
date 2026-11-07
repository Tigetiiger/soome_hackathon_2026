"""Section B of the results site: "What goes into the model" (inputs, exclusions, features, ladder, importance, example)."""
from __future__ import annotations

import logging
import re
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from site_common import ROOT, SPLIT_LABEL, Build, copy_plots, dig, figures, note, num, raw_table, table
from weight_train.columns import CURVE_COLUMNS, DEVICE_COLUMNS, FORBIDDEN_COLUMNS, FORBIDDEN_PREFIXES, OPTIONAL_DEVICE_COLUMNS
from weight_train.features import (CALENDAR, CYCLE, FEATURE_SETS, FILL, GRAPH, MACHINE, PRESSES, PRESSURE, STROKES,
                                   WEATHER)
from weight_train.settings import NOMINAL_DENSITY

FAMILIES = (("machine", MACHINE), ("calendar", CALENDAR), ("cycle", CYCLE), ("fill", FILL), ("presses", PRESSES),
            ("peak pressure", PRESSURE), ("strokes", STROKES), ("pressure graph", GRAPH), ("weather", WEATHER))
TEL, SMART, WX, CONF = "machine telemetry", "SMART service", "public weather", "machine configuration"
RAW = {
    "bin_id": ("machine id", SMART), "ts": ("local hour start", SMART),
    "material": ("material the container is assigned to", CONF), "equipment_class": ("COMBI or DUO", CONF),
    "container_volume_m3": ("container volume", CONF), "region": ("region (weather station)", CONF),
    "infeed": ("open hopper / lidded hopper / indoor shaft", CONF), "drainage": ("has a drainage system", CONF),
    "temp_c": ("air temperature this hour", WX),
    "precip_mm_day": ("day total precipitation — only completed days are used", WX),
    "rh_pct": ("day mean relative humidity — only completed days are used", WX),
    "fill_pct": ("firmware fill estimate (derived from back pressure, not a level sensor)", TEL),
    "presses": ("ram strokes this hour", TEL), "peak_pressure_bar": ("max stroke peak pressure this hour", TEL),
    "lift_event": ("container emptied at the start of this hour (defines the cycle)", SMART),
    "oil_temp_c": ("hydraulic oil temperature", TEL), "energy_kwh": ("motor energy this hour", TEL),
    "precip_mm": ("hourly precipitation (past hours only)", WX),
    "curve_contact_pos": ("pressure graph: ram position where the pressure starts rising", TEL),
    "curve_rise_slope_bar": ("pressure graph: slope from contact to peak", TEL),
    "curve_mean_bar": ("pressure graph: mean pressure over the stroke", TEL),
    "curve_completion": ("pressure graph: share of travel before the relief valve opened", TEL),
    "strokes.parquet": ("per-stroke peak pressure and duration (optional, hourly means)", TEL),
}
FORBIDDEN_WHY = {
    "lifted_mass_kg": "mass removed by the lift (the answer)", "side_waste_kg": "overflow left outside (truth)",
    "ref_scale_kg": "load-cell reading on ~5 % of machines (a scale — the thing we replace)",
    "density_factor": "hidden per-machine density multiplier", "daily_input_kg": "hidden site input rate",
    "target_cycle_days": "hidden site cycle length", "p_idle_bar": "true idle pressure of the machine",
    "k_machine": "true hydraulic scale of the machine", "relief_bar": "true relief-valve setting",
    "fill_gain_bias": "fill sensor bias", "pressure_gain_bias": "pressure transducer bias",
    "pressure_gain_drift_per_year": "pressure transducer drift", "storage_outdoor_share": "hidden storage habit",
    "threshold_pct": "order threshold of the site",
}
LADDER = (("naive_fill_x_density", "formula: fill × nominal density (not a model)"),
          ("fill_presses", "fill_presses (shared model)"), ("pressure", "pressure (shared model)"),
          ("pressure_graph", "pressure_graph (shared model)"), ("full_shared", "full (shared model)"),
          ("full_per_material", "full (one model per material)"),
          ("full_selected", "full, setup chosen per material on validation (deployed)"))
EXAMPLE_HOURS = 8


def feature_docs() -> dict[str, str]:
    """feature -> meaning, parsed from the features table in weight_train/README.md."""
    path = ROOT / "weight_train" / "README.md"
    docs: dict[str, str] = {}
    if not path.exists():
        return docs
    for line in path.read_text().splitlines():
        m = re.match(r"\|\s*(`[^|]+)\|\s*(.+?)\s*\|\s*$", line)
        if not m:
            continue
        names = re.findall(r"`([^`]+)`", m.group(1))
        if "…" in m.group(1) and len(names) == 2:   # rain_mm_d1 … rain_mm_d7
            stem = names[0].rstrip("0123456789")
            names = [f"{stem}{k}" for k in range(int(names[0][len(stem):]), int(names[1][len(stem):]) + 1)]
        for n in names:
            docs[n] = m.group(2).replace("`", "")
    dens = "/".join(num(x, 0) for x in NOMINAL_DENSITY.values())   # keep in sync with settings.py
    return {k: re.sub(r"\(\d+(?:/\d+)+ kg/m³\)", f"({dens} kg/m³)", d) for k, d in docs.items()}


# ---------------------------------------------------------------- 1 flow
def flow() -> str:
    boxes = [
        ("Raw device signals per hour", ["fill estimate, presses, peak pressure, oil temp, energy",
                                         "pressure-graph features", "machine configuration", "public weather"]),
        ("Feature engineering", ["per machine, backward-looking only", "cycle = since the last emptying",
                                 "completed days for daily weather", f"{len(FEATURE_SETS['full'])} features (full set)"]),
        ("LightGBM", ["target = kg per m³ of container", "shared vs per-material model, chosen on validation",
                      "p10 / p90 quantile models", "conformal calibration → 80 % interval"]),
        ("Output per hour", ["mass_pred_kg = kg/m³ × volume", "mass_p10_kg, mass_p90_kg",
                             "value before a lift ↔ weighbridge"]),
    ]
    html = []
    for i, (title, items) in enumerate(boxes):
        if i:
            html.append('<div class="arrow" aria-hidden="true">→</div>')
        html.append(f'<div class="box"><b>{escape(title)}</b><ul>'
                    + "".join(f"<li>{escape(t)}</li>" for t in items) + "</ul></div>")
    return '<div class="flow" role="img" aria-label="model pipeline">' + "".join(html) + "</div>"


# ---------------------------------------------------------------- 2/3 inputs
def raw_inputs() -> str:
    rows = []
    for col in list(DEVICE_COLUMNS) + list(OPTIONAL_DEVICE_COLUMNS) + ["strokes.parquet"]:
        meaning, origin = RAW.get(col, ("–", "–"))
        kind = "required" if col in DEVICE_COLUMNS else "optional"
        rows.append([f"<code>{escape(col)}</code>", escape(meaning), escape(origin), kind])
    return ("<p>Only these columns are read (whitelist <code>DEVICE_COLUMNS</code> + <code>OPTIONAL_DEVICE_COLUMNS</code> "
            "in <code>weight_train/columns.py</code>); everything else in the data file is dropped before any feature "
            f"is computed. The pressure-graph columns ({escape(', '.join(CURVE_COLUMNS))}) are optional.</p>"
            + raw_table(["column", "meaning", "origin", "status"], rows, left_cols={0, 1, 2, 3})
            + "<p><strong>Today's daily precipitation and RH are not used for the current day</strong>: a daily total or "
              "mean would contain hours that have not happened yet. Daily weather enters only as completed days "
              "(yesterday and earlier); the hourly <code>precip_mm</code> is used only up to the current hour.</p>")


def excluded(data_run: Path) -> str:
    true_cols: list[str] = []
    try:
        import pyarrow.parquet as pq
        true_cols = [c for c in pq.read_schema(ROOT / data_run / "hourly.parquet").names
                     if c.startswith(FORBIDDEN_PREFIXES)]
    except (OSError, ValueError) as exc:
        logging.warning("cannot read hourly schema: %s", exc)
    rows = [[f"<code>{escape(c)}</code>", escape(FORBIDDEN_WHY.get(c, "hidden truth"))] for c in sorted(FORBIDDEN_COLUMNS)]
    return ("<p>The simulator also writes the truth. None of it may reach the model, or the test numbers would be "
            "meaningless (leakage). Excluded are every column starting with <code>true_</code> — in "
            f"<code>{escape(str(data_run))}</code>: " + ", ".join(f"<code>{escape(c)}</code>" for c in true_cols)
            + " — and the <code>FORBIDDEN_COLUMNS</code>:</p>" + raw_table(["column", "what it is"], rows, {0, 1})
            + "<p><code>assert_no_leakage</code> rejects any such column at feature-build and fit time, and the tests in "
              "<code>tests/test_weight_train.py</code> enforce it: no <code>true_</code> column reaches the feature matrix, "
              "planted truth columns are rejected, scrambling truth changes nothing, cutting or scrambling the future "
              "leaves earlier features identical, and daily weather lags use completed days only.</p>")


# ---------------------------------------------------------------- 4/5 features + ladder
def feature_table(docs: dict[str, str]) -> str:
    sets = list(FEATURE_SETS)
    rows, classes = [], []
    for fam, cols in FAMILIES:
        rows.append([f"{escape(fam)} ({len(cols)})"] + [""] * (len(sets) + 1))
        classes.append("fam")
        for c in cols:
            rows.append([f"<code>{escape(c)}</code>", escape(docs.get(c, "–"))]
                        + ["✓" if c in FEATURE_SETS[s] else "" for s in sets])
            classes.append("")
    rows.append(["<code>material</code>", escape(docs.get("material", "material (shared model only)"))]
                + ["shared"] * len(sets))
    classes.append("")
    head = ["feature", "meaning"] + [f"<code>{escape(s)}</code>" for s in sets]
    nominal = ", ".join(f"{k} {num(x, 0)}" for k, x in NOMINAL_DENSITY.items())
    return (f"<p>All features are computed per machine and hour from rows ≤ the current hour. Nominal densities used by "
            f"<code>naive_kg_m3</code> and <code>graph_kg_m3</code> (public, kg/m³): {escape(nominal)}. Ticks show "
            "which comparison-ladder feature set contains the feature.</p>"
            + raw_table(head, rows, left_cols={0, 1}, row_class=classes))


def ladder(metrics: dict | None) -> str:
    out = []
    for split, sp in (dig(metrics, "splits") or {}).items():
        lad = sp.get("ladder") or {}
        mats = sorted({m for st in lad.values() for m in (st.get("by_material") or {})})
        rows = []
        for step, desc in LADDER:
            if step not in lad:
                continue
            bym = lad[step].get("by_material") or {}
            rows.append([step, desc, num(dig(lad[step], "overall", "mean_pct"))]
                        + [num(dig(bym, m, "mean_pct")) for m in mats])
        out.append(f"<h4>{escape(split)} — {escape(SPLIT_LABEL.get(split, ''))}</h4>"
                   + table(["step", "what it is", "all"] + mats, rows, good_cols=set(range(2, len(mats) + 3))))
    return ("<p>Mean % error at lift on the same test lifts, adding one signal family at a time. "
            "<code>naive_fill_x_density</code> is a formula (fill × nominal density × volume), not a trained model. "
            "Cells under 5 % are highlighted.</p>" + ("".join(out) or note("No ladder in metrics.json.")))


# ---------------------------------------------------------------- 6 importance
def importance(metrics: dict | None, b: Build, model_run: Path) -> str:
    parts = []
    for split, sp in (dig(metrics, "splits") or {}).items():
        groups: dict[tuple, list[str]] = {}
        for mat, gains in (sp.get("feature_importance_gain") or {}).items():
            key = (dig(sp, "selection", mat) or "?", tuple(sorted(gains.items())))
            groups.setdefault(key, []).append(mat)
        cards = []
        for (setup, items), mats in groups.items():
            gains = dict(items)
            total = sum(gains.values()) or 1.0
            top = sorted(gains.items(), key=lambda kv: -kv[1])[:10]
            bars = "".join(f'<div class="bar"><code title="{escape(f)}">{escape(f)}</code><div class="track">'
                           f'<div class="fill" style="width:{100 * g / top[0][1]:.1f}%"></div></div>'
                           f"<span>{100 * g / total:.1f} %</span></div>" for f, g in top)
            cards.append(f'<div class="bar-card"><h5>{escape(" · ".join(mats))} <span class="muted">({escape(setup)} '
                         f"model)</span></h5>{bars}</div>")
        if cards:
            parts.append(f"<h4>{escape(split)} — {escape(SPLIT_LABEL.get(split, ''))}</h4>"
                         f'<div class="bars">{"".join(cards)}</div>')
    shap = [p for p in copy_plots(b, model_run / "plots") if p.stem.startswith("shap")]
    return ("<p>Share of total LightGBM split gain of the model each material actually uses (top 10). Materials "
            "served by the same shared model share one chart.</p>" + ("".join(parts) or note("No importance yet."))
            + ("<h4>SHAP at lift</h4>" + figures(shap) if shap else ""))


# ---------------------------------------------------------------- 7 example
def _pick_lift(h: pd.DataFrame, test_start: pd.Timestamp | None) -> tuple[str, pd.Timestamp] | None:
    busy = h.groupby("bin_id", sort=False)["presses"].transform(lambda x: x.shift(1).rolling(EXAMPLE_HOURS - 1).sum())
    lifts = h[(h["lift_event"] == 1) & (h["true_mass_kg"].shift(1) > 0) & (busy >= 3) & (h["ts"].dt.hour >= 12)]
    if test_start is not None:
        lifts = lifts[lifts["ts"] >= test_start]
    for mat in ("cardboard", "paper", "plastic_film", "mixed_waste"):
        cand = lifts[lifts["material"] == mat]
        if len(cand) > 2:
            row = cand.iloc[len(cand) // 2]
            return str(row["bin_id"]), row["ts"]
    return None


def example(model_run: Path, data_run: Path, metrics: dict | None) -> str:
    from weight_train.bundle import SoftSensor
    from weight_train.features import build_features
    split = next((s for s in ("time", "bins") if (ROOT / model_run / s / "bundle.json").exists()), None)
    hpath = ROOT / data_run / "hourly.parquet"
    if split is None or not hpath.exists():
        return note("No trained bundle or matching hourly data for the example.")
    try:
        sensor = SoftSensor.load(ROOT / model_run / split)
        h = pd.read_parquet(hpath)
        ts0 = dig(metrics, "splits", split, "test_start")
        pick = _pick_lift(h, pd.Timestamp(ts0) if ts0 else None)
        if pick is None:
            return note("No suitable lift found for the example.")
        bin_id, lift_ts = pick
        one = h[h["bin_id"] == bin_id].reset_index(drop=True)
        spath = ROOT / data_run / "strokes.parquet"
        strokes = (pd.read_parquet(spath, columns=["bin_id", "ts", "peak_pressure_bar", "duration_s"],
                                   filters=[("bin_id", "==", bin_id)]) if spath.exists() else None)
        feats = build_features(one, sensor.inverter, strokes)
        pred = sensor.predict_frame(feats)
    except (OSError, ValueError, KeyError) as exc:
        logging.warning("example failed: %s", exc)
        return note(f"Example could not be built: {exc}")
    pos = int(np.flatnonzero((feats.meta["ts"] == lift_ts).to_numpy())[0])
    rows_idx = list(range(pos - EXAMPLE_HOURS + 1, pos + 1))
    X = feats.X.iloc[rows_idx]
    truth = one.set_index("ts").loc[feats.meta["ts"].iloc[rows_idx], "true_mass_kg"].to_numpy()
    hours = [t.strftime("%a %H:%M") for t in feats.meta["ts"].iloc[rows_idx]]
    head = ["feature"] + [escape(x) for x in hours]
    hc = [""] + ["lift" if i >= EXAMPLE_HOURS - 2 else "" for i in range(EXAMPLE_HOURS)]
    rows, classes = [], []

    def add(label: str, vals, cls: str = "", nd: int = 2) -> None:
        nums = [float(x) for x in vals if isinstance(x, (int, float, np.floating, np.integer)) and not pd.isna(x)]
        if nums and all(x.is_integer() for x in nums):
            nd = 0
        cells = [escape(str(x)) if not isinstance(x, (int, float, np.floating, np.integer))
                 else ("–" if pd.isna(x) else escape(num(x, nd))) for x in vals]
        rows.append([label] + cells)
        classes.append(cls)

    p = pred.iloc[rows_idx]
    add("<strong>true_mass_kg</strong> (truth, not an input)", truth, "key", 0)
    add("<strong>mass_pred_kg</strong>", p["mass_pred_kg"].to_numpy(), "key", 0)
    add("mass_p10_kg … mass_p90_kg", [f"{num(a, 0)} … {num(c, 0)}" for a, c in zip(p["mass_p10_kg"], p["mass_p90_kg"])])
    for fam, cols in FAMILIES:
        rows.append([escape(fam)] + [""] * EXAMPLE_HOURS)
        classes.append("fam")
        for c in cols:
            if c in X:
                add(f"<code>{escape(c)}</code>", X[c].tolist())
    mat = str(feats.meta["material"].iloc[pos])
    vol = num(feats.meta["container_volume_m3"].iloc[pos], 0)
    return (f"<p>Machine <code>{escape(bin_id)}</code> ({escape(mat)}, {escape(vol)} m³) from "
            f"<code>{escape(str(data_run))}</code>, the {EXAMPLE_HOURS} hours up to the lift at "
            f"{escape(lift_ts.strftime('%Y-%m-%d %H:%M'))} (test period of the <code>{escape(split)}</code> split, so "
            f"these hours were not trained on). Features from <code>build_features</code>, prediction from the "
            f"<code>{escape(str(model_run / split))}</code> bundle. The highlighted last two columns are the pre-lift hour "
            "(the value compared with the weighbridge) and the lift hour (container emptied at its start, so the true "
            "mass is that hour's new material only).</p>"
            + raw_table(head, rows, left_cols={0}, row_class=classes, col_class=hc))


def model_inputs(b: Build, metrics: dict | None, model_run: Path, data_run: Path) -> str:
    docs = feature_docs()
    b.check(Path("weight_train/README.md"))
    return (f'<section id="inputs"><h2>What goes into the model <span class="muted">({escape(str(model_run))})</span>'
            "</h2>" + flow()
            + "<h3>Raw inputs</h3>" + raw_inputs()
            + "<h3>Explicitly excluded inputs</h3>" + excluded(data_run)
            + "<h3>Engineered features</h3>" + feature_table(docs)
            + "<h3>Comparison ladder: which features each step uses</h3>" + ladder(metrics)
            + "<h3>Feature importance</h3>" + importance(metrics, b, model_run)
            + "<h3>Example: one machine before a lift</h3>" + example(model_run, data_run, metrics) + "</section>")
