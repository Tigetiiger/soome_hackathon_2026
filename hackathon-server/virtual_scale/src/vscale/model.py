"""Mass prediction from sensor features, trained on scale weighings.

* Training labels: clean shared weighbridge tickets + golden-cohort platform weighings (never the hidden truth).
* Validation: GroupKFold by device, so every score is for machines the model has never seen.
* Per-device anchor calibration: after k clean tickets of a machine, a shrunk multiplicative gain
  (robust median of log(label / prediction)) corrects that machine. Only anchors dated before a lift are used.
* Intervals: quantile gradient boosting (10 % / 90 %) on log mass.
* Scoring: against the hidden true collected mass, and the pre-registered acceptance criteria of the
  business plan (>= 80 % of >= 1 t lifts within +/-10 %; device-month bias <= 5 % for >= 80 % of
  device-months; 80 % interval covers 75-85 %).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold

from vscale.features import tier_columns

N_FOLDS = 5
ANCHOR_SHRINK_K0 = 2.0
MIN_KG = 50.0


def _gbm(loss: str = "squared_error", quantile: float | None = None) -> HistGradientBoostingRegressor:
    kw = {"quantile": quantile} if quantile is not None else {}
    return HistGradientBoostingRegressor(loss=loss, max_iter=400, learning_rate=0.05, max_leaf_nodes=31,
                                         min_samples_leaf=30, l2_regularization=1.0,
                                         categorical_features="from_dtype", random_state=0, **kw)


@dataclass(frozen=True)
class OofResult:
    pred: np.ndarray
    lo: np.ndarray
    hi: np.ndarray


def oof_predict(df: pd.DataFrame, tier: str, with_intervals: bool = False) -> OofResult:
    """Out-of-fold predictions for every lift; models see labelled lifts of other devices only."""
    cols = tier_columns(tier)
    X = df[cols]
    y = np.log(np.maximum(df.label_kg.to_numpy(), MIN_KG))
    has_label = df.label_kg.notna().to_numpy()
    pred = np.full(len(df), np.nan)
    lo = np.full(len(df), np.nan)
    hi = np.full(len(df), np.nan)
    for train_idx, test_idx in GroupKFold(n_splits=N_FOLDS).split(X, groups=df.device_id):
        tr = train_idx[has_label[train_idx]]
        pred[test_idx] = np.exp(_gbm().fit(X.iloc[tr], y[tr]).predict(X.iloc[test_idx]))
        if with_intervals:
            lo[test_idx] = np.exp(_gbm("quantile", 0.10).fit(X.iloc[tr], y[tr]).predict(X.iloc[test_idx]))
            hi[test_idx] = np.exp(_gbm("quantile", 0.90).fit(X.iloc[tr], y[tr]).predict(X.iloc[test_idx]))
    return OofResult(pred=pred, lo=lo, hi=hi)


def anchor_calibrate(df: pd.DataFrame, pred: np.ndarray, max_anchors: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Per-device gain from earlier clean anchors. Returns (calibrated prediction, anchors used)."""
    out = pred.copy()
    used = np.zeros(len(df), dtype=int)
    order = df.assign(row_idx=np.arange(len(df)), base_pred=pred).sort_values(["device_id", "lift_at"])
    for _, g in order.groupby("device_id", sort=False):
        logs: list[float] = []
        for row in g.itertuples():
            k = len(logs) if max_anchors is None else min(len(logs), max_anchors)
            if k:
                w = k / (k + ANCHOR_SHRINK_K0)
                out[row.row_idx] = row.base_pred * np.exp(w * np.median(logs[:k]))
                used[row.row_idx] = k
            if not np.isnan(row.label_kg) and row.label_kg > MIN_KG:
                logs.append(float(np.log(row.label_kg / row.base_pred)))
    return out, used


def lift_metrics(true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    ape = np.abs(pred / true - 1)
    big = true >= 1000
    band = (true >= 2500) & (true <= 3500)
    return {
        "lifts": int(len(true)),
        "median_ape_pct": 100 * float(np.median(ape)),
        "p90_ape_pct": 100 * float(np.quantile(ape, 0.9)),
        "within_10pct_ge1t": float(np.mean(ape[big] <= 0.10)) if big.any() else np.nan,
        "within_100kg_2.5-3.5t": float(np.mean(np.abs(pred[band] - true[band]) <= 100)) if band.any() else np.nan,
    }


def device_month_bias(df: pd.DataFrame, pred: np.ndarray) -> pd.DataFrame:
    d = df[["device_id", "lift_at", "true_collected_kg"]].assign(pred=pred)
    d["month"] = pd.to_datetime(d.lift_at).dt.strftime("%Y-%m")
    m = d.groupby(["device_id", "month"]).agg(true=("true_collected_kg", "sum"), pred=("pred", "sum"), lifts=("pred", "size"))
    m["bias_pct"] = 100 * (m.pred / m.true - 1)
    return m.reset_index()


def acceptance(df: pd.DataFrame, pred: np.ndarray, lo: np.ndarray | None = None, hi: np.ndarray | None = None) -> dict:
    true = df.true_collected_kg.to_numpy()
    lm = lift_metrics(true, pred)
    dm = device_month_bias(df, pred)
    res = {
        "A1_ge1t_within_10pct": lm["within_10pct_ge1t"],
        "A1_pass": lm["within_10pct_ge1t"] >= 0.80,
        "A2_devmonth_within_5pct": float((dm.bias_pct.abs() <= 5).mean()),
        "A2_pass": float((dm.bias_pct.abs() <= 5).mean()) >= 0.80,
    }
    if lo is not None and hi is not None and not np.isnan(lo).all():
        cov = float(np.mean((true >= lo) & (true <= hi)))
        res.update({"A3_80pct_interval_coverage": cov, "A3_pass": 0.75 <= cov <= 0.85})
    return res


def calibrated_interval(df: pd.DataFrame, cal_pred: np.ndarray, used: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Interval for calibrated predictions from leave-device-out log residual quantiles vs labels,
    by material and by 'calibrated or not'. Labels carry weighbridge noise, so it is slightly conservative."""
    lo = np.full(len(df), np.nan)
    hi = np.full(len(df), np.nan)
    lab = df.label_kg.to_numpy()
    resid = np.log(np.maximum(lab, MIN_KG) / cal_pred)
    ok = ~np.isnan(lab)
    for train_idx, test_idx in GroupKFold(n_splits=N_FOLDS).split(df, groups=df.device_id):
        tr = train_idx[ok[train_idx]]
        for mat in df.material.cat.categories:
            for cal in (False, True):
                sel_tr = tr[(df.material.to_numpy()[tr] == mat) & ((used[tr] > 0) == cal)]
                sel_te = test_idx[(df.material.to_numpy()[test_idx] == mat) & ((used[test_idx] > 0) == cal)]
                if len(sel_tr) < 20 or not len(sel_te):
                    sel_tr = tr
                q10, q90 = np.quantile(resid[sel_tr], [0.10, 0.90])
                lo[sel_te] = cal_pred[sel_te] * np.exp(q10)
                hi[sel_te] = cal_pred[sel_te] * np.exp(q90)
    return lo, hi
