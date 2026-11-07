"""Shared helpers for europress_conclusions value analyses. Reuses (read-only) the team loaders in soome_hackathon_2026/analysis/common.py.
All EUR are the dataset's HYPOTHETICAL customer-operator tariffs on SYNTHETIC data -> tag [data, hypothetical prices]."""
import sys
sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *  # noqa: F401,F403  (rd, lifts, labels, device_years, WINDOW, PUB, LIFT, reprice, lift_pricing_inputs)
from pathlib import Path
import numpy as np, pandas as pd
OUT2 = Path("/home/hackathon/europress_conclusions/analysis/outputs"); OUT2.mkdir(parents=True, exist_ok=True)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 300)
YEAR_FACTOR = 365 / 304          # label window 2025-10-01..2026-08-01 is 304 days


def device_segments():
    dv = rd("reference/devices.parquet")
    cu = rd("reference/customers.parquet")[["customer_id", "primary_sector"]]
    st = rd("reference/sites.parquet")[["site_id", "region_code", "outdoor_material_staging"]]
    dv = dv.merge(cu, on="customer_id", how="left").merge(st, on="site_id", how="left")
    w0, w1 = WINDOW
    a = pd.to_datetime(dv.active_from).fillna(w0).clip(lower=w0)
    b = pd.to_datetime(dv.active_to).fillna(w1).clip(upper=w1)
    dv["dev_years"] = (b - a).dt.days.clip(lower=0) / 365.0
    return dv


SEGS = ["primary_sector", "material_stream", "collection_policy", "operator_id"]


def per_segment(df_val, val_col, dv, segs=SEGS, extra=None):
    """Sum val_col by segment and divide by active device-years of that segment (all devices of that segment)."""
    rows = []
    for s in segs:
        num = df_val.groupby(s)[val_col].sum()
        den = dv.groupby(s).dev_years.sum()
        cnt = df_val.groupby(s).size()
        for k in den.index:
            rows.append({"segment": s, "value": k, "n": int(cnt.get(k, 0)), "eur": round(float(num.get(k, 0)), 2),
                         "device_years": round(float(den[k]), 1), "eur_per_device_year": round(float(num.get(k, 0)) / max(den[k], 1e-9), 2)})
    rows.append({"segment": "ALL", "value": "ALL", "n": len(df_val), "eur": round(float(df_val[val_col].sum()), 2),
                 "device_years": round(float(dv.dev_years.sum()), 1), "eur_per_device_year": round(float(df_val[val_col].sum()) / dv.dev_years.sum(), 2)})
    return pd.DataFrame(rows)


def device_dist(df_val, val_col, dv):
    """Per-device EUR/device-year distribution (p10/p50/p90 across devices, zeros included)."""
    v = df_val.groupby("device_id")[val_col].sum().reindex(dv.device_id).fillna(0).values
    y = dv.dev_years.values
    m = y > 0.1
    r = v[m] / y[m]
    return {"p10": round(float(np.quantile(r, .1)), 1), "p50": round(float(np.median(r)), 1), "p75": round(float(np.quantile(r, .75)), 1),
            "p90": round(float(np.quantile(r, .9)), 1), "mean": round(float(r.mean()), 1), "share_devices_nonzero": round(float((r > 0).mean()), 3)}
