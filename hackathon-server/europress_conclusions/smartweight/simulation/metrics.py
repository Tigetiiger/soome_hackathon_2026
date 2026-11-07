"""Error metrics for mass estimators (all in kg unless named *_rel)."""
from __future__ import annotations

import numpy as np
import pandas as pd

MASS_BINS = [0, 500, 1000, 2000, 3000, 20000]
MASS_LABELS = ["<0.5t", "0.5-1t", "1-2t", "2-3t", ">=3t"]


def summarize(est: np.ndarray, truth: np.ndarray) -> dict:
    e = est - truth
    ae = np.abs(e)
    big = truth >= 1000
    rel = np.abs(e[big]) / truth[big]
    near3 = (truth >= 2500) & (truth <= 3500)
    return {
        "n": int(len(e)),
        "MAE_kg": float(ae.mean()),
        "RMSE_kg": float(np.sqrt((e**2).mean())),
        "bias_kg": float(e.mean()),
        "P90_abs_kg": float(np.percentile(ae, 90)),
        "P95_abs_kg": float(np.percentile(ae, 95)),
        "within_100kg": float((ae <= 100).mean()),
        "within_100kg_at_2.5-3.5t": float((ae[near3] <= 100).mean()) if near3.any() else np.nan,
        "median_rel_ge1t": float(np.median(rel)) if big.any() else np.nan,
        "P95_rel_ge1t": float(np.percentile(rel, 95)) if big.any() else np.nan,
        "within_2pct_ge1t": float((rel <= 0.02).mean()) if big.any() else np.nan,
        "within_5pct_ge1t": float((rel <= 0.05).mean()) if big.any() else np.nan,
    }


def breakdown(est: np.ndarray, ev: pd.DataFrame, by: str) -> pd.DataFrame:
    truth = ev["m_true"].to_numpy()
    if by == "mass_bin":
        key = pd.cut(truth, MASS_BINS, labels=MASS_LABELS, right=False)
    else:
        key = ev[by].to_numpy()
    rows = []
    for k in pd.unique(key):
        i = np.asarray(key == k)
        if i.sum() < 20:
            continue
        s = summarize(est[i], truth[i])
        rows.append({by: k, "n": s["n"], "MAE_kg": s["MAE_kg"], "bias_kg": s["bias_kg"],
                     "P95_abs_kg": s["P95_abs_kg"], "within_100kg": s["within_100kg"],
                     "median_rel": float(np.median(np.abs(est[i] - truth[i]) / np.clip(truth[i], 50, None)))})
    return pd.DataFrame(rows)
