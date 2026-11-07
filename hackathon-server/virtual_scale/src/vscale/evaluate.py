"""Train and score the virtual scale per hardware tier; write tables, figures and REPORT.md."""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from vscale import physics as ph  # noqa: E402
from vscale.config import DEFAULT_OUT, PROJECT_ROOT, load_config  # noqa: E402
from vscale.features import TIER_FEATURES, build_lift_table  # noqa: E402
from vscale.model import (acceptance, anchor_calibrate, calibrated_interval, lift_metrics,  # noqa: E402
                          oof_predict)

log = logging.getLogger(__name__)
ANCHOR_CURVE = [0, 1, 2, 3, 5, 10]
INTERVAL_TIERS = ("T1b_pressure_plus", "T1c_all_cheap")


def score_tiers(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, dict[str, dict]]:
    true = df.true_collected_kg.to_numpy()
    rows, preds = [], {}
    direct = {"T0_table (no ML)": df.m_table_kg.to_numpy(),
              "T1b_physics (no ML)": df.m_phys_oil_kg.to_numpy(),
              "T2_platform (direct)": df.m_platform_kg.to_numpy()}
    for name, p in direct.items():
        p = np.maximum(np.nan_to_num(p, nan=MIN_PRED), MIN_PRED)
        cal, used = anchor_calibrate(df, p)
        rows.append({"model": name, "cost_eur": _cost(cfg, name),
                     **_pref("raw", lift_metrics(true, p)), **_pref("cal", lift_metrics(true, cal))})
        preds[name] = {"raw": p, "cal": cal, "used": used}
    for tier in TIER_FEATURES:
        log.info("training tier %s", tier)
        res = oof_predict(df, tier, with_intervals=tier in INTERVAL_TIERS)
        cal, used = anchor_calibrate(df, res.pred)
        rows.append({"model": f"{tier} (ML)", "cost_eur": cfg["tiers"][tier]["cost_eur"],
                     **_pref("raw", lift_metrics(true, res.pred)), **_pref("cal", lift_metrics(true, cal))})
        preds[tier] = {"raw": res.pred, "cal": cal, "used": used, "lo": res.lo, "hi": res.hi}
    return pd.DataFrame(rows), preds


MIN_PRED = 50.0


def _cost(cfg: dict, name: str) -> int:
    key = {"T0_table (no ML)": "T0_fill_only", "T1b_physics (no ML)": "T1b_pressure_plus",
           "T2_platform (direct)": "T2_platform"}[name]
    return cfg["tiers"][key]["cost_eur"]


def _pref(prefix: str, d: dict) -> dict:
    return {f"{prefix}_{k}": v for k, v in d.items() if k != "lifts"}


def anchor_curve(df: pd.DataFrame, preds: dict, tiers: list[str]) -> pd.DataFrame:
    """Median APE after k anchors, on the same lifts (those with >= 10 earlier anchors)."""
    _, used_all = anchor_calibrate(df, preds[tiers[0]]["raw"])
    subset = used_all >= max(ANCHOR_CURVE)
    rows = []
    for tier in tiers:
        for k in ANCHOR_CURVE:
            cal, _ = anchor_calibrate(df, preds[tier]["raw"], max_anchors=k)
            m = lift_metrics(df.true_collected_kg.to_numpy()[subset], cal[subset])
            rows.append({"tier": tier, "anchors": k, "median_ape_pct": m["median_ape_pct"],
                         "p90_ape_pct": m["p90_ape_pct"], "within_10pct_ge1t": m["within_10pct_ge1t"], "lifts": m["lifts"]})
    return pd.DataFrame(rows)


def acceptance_table(df: pd.DataFrame, preds: dict) -> pd.DataFrame:
    rows = []
    for tier in INTERVAL_TIERS:
        p = preds[tier]
        rows.append({"tier": tier, "stage": "uncalibrated (new machine)", **acceptance(df, p["raw"], p["lo"], p["hi"])})
        lo, hi = calibrated_interval(df, p["cal"], p["used"])
        rows.append({"tier": tier, "stage": "anchor-calibrated", **acceptance(df, p["cal"], lo, hi)})
    rows.append({"tier": "T2_platform", "stage": "direct", **acceptance(df, preds["T2_platform (direct)"]["raw"])})
    return pd.DataFrame(rows)


def by_material(df: pd.DataFrame, pred: np.ndarray) -> pd.DataFrame:
    rows = []
    for mat, g in df.groupby("material", observed=True):
        m = lift_metrics(g.true_collected_kg.to_numpy(), pred[g.index.to_numpy()])
        rows.append({"material": mat, **m})
    return pd.DataFrame(rows)


def field_view(df: pd.DataFrame, pred: np.ndarray) -> pd.DataFrame:
    """What Europress would SEE: device estimate vs shared ticket, flag rule |diff| > 100 kg and > 10 %."""
    s = df[df.wb_shared].copy()
    s["pred"] = pred[s.index.to_numpy()]
    diff = s.pred - s.wb_allocated_net_kg
    s["flag"] = (diff.abs() > 100) & (diff.abs() > 0.10 * s.wb_allocated_net_kg.clip(lower=1))
    s["ticket_issue"] = np.select(
        [s.wb_loads_on_vehicle > 1, s.err_side_waste_kg > 0, s.err_tare_kg.abs() > 60],
        ["combined load", "side waste", "stale stored tare"], "clean ticket")
    t = s.groupby("ticket_issue").agg(tickets=("flag", "size"), flagged=("flag", "sum"), flag_rate=("flag", "mean"))
    t["share_of_all_flags"] = t.flagged / t.flagged.sum()
    return t.reset_index()


# ----------------------------------------------------------------------------- figures
def fig_traces(cycles: pd.DataFrame, cfg: dict, out: Path) -> None:
    dev = cycles[cycles.device_id == cycles.device_id.iloc[0]]
    lift = dev.collection_id.unique()[min(3, dev.collection_id.nunique() - 1)]
    c = dev[dev.collection_id == lift].reset_index(drop=True)
    picks = np.unique(np.linspace(0, len(c) - 1, 5).astype(int))
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    for i in picks:
        r = c.iloc[i]
        t, p = ph.pressure_trace(6.0, float(r.p_plateau_bar), float(r.p_end_bar), float(r.stroke_completion), 180.0)
        ax[0].plot(t, p, label=f"{r.true_mass_kg:,.0f} kg in container")
    ax[0].set(xlabel="seconds", ylabel="hydraulic pressure (bar)", title="Illustrative stroke curves as the container fills")
    ax[0].legend(fontsize=8)
    ax[1].scatter(c.true_mass_kg, c.p_end_bar, s=6, label="end-of-stroke")
    ax[1].scatter(c.true_mass_kg, c.p_plateau_bar, s=6, label="mid-stroke plateau")
    ax[1].scatter(c.true_mass_kg, c.fill_pct, s=6, label="fill % (SMART)")
    ax[1].set(xlabel="true mass in container (kg)", ylabel="bar / %", title=f"One emptying cycle, {dev.device_id.iloc[0]}")
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "fig1_pressure_signals.png", dpi=130)
    plt.close(fig)


def fig_tiers(scores: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for _, r in scores.iterrows():
        ax.scatter(r.cost_eur, r.raw_median_ape_pct, marker="o", color="tab:blue")
        ax.scatter(r.cost_eur, r.cal_median_ape_pct, marker="^", color="tab:orange")
        ax.annotate(r.model, (r.cost_eur, r.raw_median_ape_pct), fontsize=7, xytext=(4, 3), textcoords="offset points")
    ax.scatter([], [], marker="o", color="tab:blue", label="new machine (no anchors)")
    ax.scatter([], [], marker="^", color="tab:orange", label="after per-device anchor calibration")
    ax.set(xlabel="extra hardware per machine, EUR [est]", ylabel="median abs. error per lift (%)",
           title="Accuracy vs hardware cost (synthetic, unseen devices)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "fig2_accuracy_vs_cost.png", dpi=130)
    plt.close(fig)


def fig_anchor(curve: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for tier, g in curve.groupby("tier"):
        ax.plot(g.anchors, g.median_ape_pct, marker="o", label=tier)
    ax.set(xlabel="clean weighbridge tickets used for this machine", ylabel="median abs. error (%)",
           title="Per-device calibration with anchor tickets")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "fig3_anchor_curve.png", dpi=130)
    plt.close(fig)


def fig_scatter(df: pd.DataFrame, pred: np.ndarray, out: Path, tier: str) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    for mat, g in df.groupby("material", observed=True):
        ax.scatter(g.true_collected_kg, pred[g.index.to_numpy()], s=3, alpha=0.4, label=mat)
    lim = float(np.quantile(df.true_collected_kg, 0.995))
    ax.plot([0, lim], [0, lim], "k--", lw=1)
    ax.plot([0, lim], [0, 1.1 * lim], "k:", lw=0.8)
    ax.plot([0, lim], [0, 0.9 * lim], "k:", lw=0.8)
    ax.set(xlim=(0, lim), ylim=(0, lim), xlabel="true collected mass (kg)", ylabel="predicted (kg)",
           title=f"{tier}, calibrated, +/-10 % lines")
    ax.legend(fontsize=7, markerscale=3)
    fig.tight_layout()
    fig.savefig(out / "fig4_pred_vs_true.png", dpi=130)
    plt.close(fig)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default=str(DEFAULT_OUT))
    ap.add_argument("--reports", default=str(PROJECT_ROOT / "reports"))
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cfg = load_config()
    data, rep = Path(a.data), Path(a.reports)
    rep.mkdir(parents=True, exist_ok=True)
    cycles = pd.read_parquet(data / "cycles.parquet")
    lifts = pd.read_parquet(data / "lifts.parquet")
    df = build_lift_table(cycles, lifts, cfg).reset_index(drop=True)
    df.to_parquet(data / "lift_features.parquet", index=False)

    scores, preds = score_tiers(df, cfg)
    curve = anchor_curve(df, preds, ["T0_fill_only", "T1a_pressure", "T1b_pressure_plus", "T1s_frame_strain", "T1c_all_cheap"])
    acc = acceptance_table(df, preds)
    best = "T1c_all_cheap"
    mat = by_material(df, preds[best]["cal"])
    field = field_view(df, preds["T1b_pressure_plus"]["cal"])
    df.assign(**{f"pred_{k}": v["cal"] for k, v in preds.items() if k in TIER_FEATURES}).to_parquet(data / "lift_predictions.parquet", index=False)

    fig_traces(cycles, cfg, rep)
    fig_tiers(scores, rep)
    fig_anchor(curve, rep)
    fig_scatter(df, preds[best]["cal"], rep, best)
    summary = {
        "devices": int(df.device_id.nunique()), "lifts": int(len(df)), "cycles": int(len(cycles)),
        "labelled_lifts": int(df.label_kg.notna().sum()),
        "label_sources": df.label_source.value_counts().to_dict(),
        "lifts_without_any_label_by_operator": df[df.label_kg.isna()].operator_id.value_counts().to_dict(),
    }
    tables = {"scores": scores, "anchor_curve": curve, "acceptance": acc, "by_material": mat, "field_view": field}
    for k, t in tables.items():
        t.to_csv(rep / f"{k}.csv", index=False)
    (rep / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    for k, t in tables.items():
        log.info("\n## %s\n%s", k, t.round(3).to_string(index=False))
    log.info("summary %s", summary)


if __name__ == "__main__":
    main()
