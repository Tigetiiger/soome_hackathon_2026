"""Pilot sizing: how many instrumented machines, for how long, before the pressure model generalises?

Train the T1a (fill + pressure) model only on labelled lifts from N pilot machines during the first
M months, then score it on a fixed set of held-out machines (never seen), uncalibrated and after
5 of their own clean tickets. Synthetic data: the pressure physics is a hypothesis [hyp].
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vscale.config import PROJECT_ROOT  # noqa: E402
from vscale.features import tier_columns  # noqa: E402
from vscale.model import MIN_KG, _gbm, anchor_calibrate, lift_metrics  # noqa: E402

PILOT_SIZES = [6, 10, 20, 30, 60, 120]
MONTHS = [3, 6]
SEEDS = [0, 1, 2]
N_TEST_DEVICES = 120
TIERS = ["T0_fill_only", "T1a_pressure"]


def run() -> pd.DataFrame:
    df = pd.read_parquet(PROJECT_ROOT / "data" / "lift_features.parquet")
    for c in ("material", "equipment_class"):
        df[c] = df[c].astype("category")
    df["lift_at"] = pd.to_datetime(df.lift_at)
    start = df.lift_at.min()
    devices = df.device_id.unique()
    rows = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        test_dev = rng.choice(devices, N_TEST_DEVICES, replace=False)
        pool = np.setdiff1d(devices, test_dev)
        test = df[df.device_id.isin(test_dev)].reset_index(drop=True)
        for n in PILOT_SIZES:
            pilot = rng.choice(pool, n, replace=False)
            for months in MONTHS:
                tr = df[df.device_id.isin(pilot) & df.label_kg.notna()
                        & (df.lift_at < start + pd.DateOffset(months=months))]
                for tier in TIERS:
                    cols = tier_columns(tier)
                    model = _gbm().set_params(min_samples_leaf=min(30, max(5, len(tr) // 20)))
                    model.fit(tr[cols], np.log(np.maximum(tr.label_kg, MIN_KG)))
                    pred = np.exp(model.predict(test[cols]))
                    cal, _ = anchor_calibrate(test, pred, max_anchors=5)
                    true = test.true_collected_kg.to_numpy()
                    rows.append({"seed": seed, "pilot_machines": n, "months": months, "tier": tier,
                                 "training_lifts": len(tr), "materials_covered": tr.material.nunique(),
                                 "new_machine_median_ape": lift_metrics(true, pred)["median_ape_pct"],
                                 "after_5_tickets_median_ape": lift_metrics(true, cal)["median_ape_pct"],
                                 "after_5_tickets_ge1t_within_10pct": lift_metrics(true, cal)["within_10pct_ge1t"]})
    return pd.DataFrame(rows)


def main() -> None:
    res = run()
    res.to_csv(PROJECT_ROOT / "reports" / "pilot_learning_curve.csv", index=False)
    agg = res.groupby(["tier", "months", "pilot_machines"]).mean(numeric_only=True).drop(columns="seed").round(2)
    pd.set_option("display.width", 200)
    print(agg.to_string())


if __name__ == "__main__":
    main()
