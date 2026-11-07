"""Fill-only weight baseline on the ORIGINAL Europress pack (no simulated sensors).

Estimate of collected mass per lift:  (fill_before - fill_after) / 100 * container_volume * density
Reference: clean shared weighbridge tickets (single load, WEIGHED tare, no side waste reported).

Density variants
  A  pack table      : typical compacted density per material (reference/material_classes)
  B  fleet-learned   : median(ticket / volume-collected) per material x machine class, learned on
                       OTHER devices (5-fold group split by device) -> what a new machine gets
  C  per-machine     : B, then a shrunk gain from that machine's EARLIER clean tickets (k = 1, 3, 5, 10)
Upper reference: the pack's simulated integrated scale (device_estimated_collected_kg).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vscale.config import DEFAULT_PACK, PROJECT_ROOT  # noqa: E402

OUT = PROJECT_ROOT / "reports" / "pack_baseline"
K0 = 2.0
ANCHORS = [0, 1, 3, 5, 10]


def load(pack: Path) -> pd.DataFrame:
    ce = pd.read_parquet(pack / "operations/collection_events.parquet")
    wb = pd.read_parquet(pack / "operations/weighbridge_tickets.parquet")
    dev = pd.read_parquet(pack / "reference/devices.parquet")[["device_id", "container_volume_m3", "material_stream", "equipment_class"]]
    dens = pd.read_parquet(pack / "reference/material_classes.parquet")[["material_stream", "typical_compacted_density_kg_m3"]]
    c = ce[ce.status == "COMPLETED"].merge(dev, on="device_id").merge(dens, on="material_stream")
    d = c.merge(wb[["operator_job_ref", "allocated_net_kg", "tare_method", "loads_on_vehicle"]], on="operator_job_ref", how="left")
    d["shared_ticket"] = d.allocated_net_kg.notna()
    d["clean"] = (d.shared_ticket & (d.loads_on_vehicle == 1) & (d.tare_method == "WEIGHED")
                  & ~d.driver_reported_side_waste.fillna(False).astype(bool) & (d.allocated_net_kg > 100))
    d = d.dropna(subset=["device_fill_pct_before"])
    d["vol_collected_m3"] = (d.device_fill_pct_before - d.device_fill_pct_after.fillna(0)).clip(lower=0) / 100 * d.container_volume_m3
    return d.sort_values(["device_id", "actual_at"]).reset_index(drop=True)


def fleet_density(d: pd.DataFrame) -> np.ndarray:
    """Per material x class density learned on other devices only (clean tickets)."""
    out = np.full(len(d), np.nan)
    key = d.material_stream + "|" + d.equipment_class
    for tr, te in GroupKFold(5).split(d, groups=d.device_id):
        t = d.iloc[tr]
        t = t[t.clean & (t.vol_collected_m3 > 0.5)]
        rho = (t.allocated_net_kg / t.vol_collected_m3).groupby(key.loc[t.index]).median()
        out[te] = key.iloc[te].map(rho).fillna(d.typical_compacted_density_kg_m3.iloc[te]).to_numpy()
    return out


def per_machine(d: pd.DataFrame, pred: np.ndarray, max_k: int | None) -> np.ndarray:
    out = pred.copy()
    clean = d.clean.to_numpy()
    ref = d.allocated_net_kg.to_numpy()
    for _, g in d.groupby("device_id", sort=False):
        logs: list[float] = []
        for i in g.index:
            k = len(logs) if max_k is None else min(len(logs), max_k)
            if k:
                out[i] = pred[i] * np.exp(k / (k + K0) * np.median(logs[:k]))
            if clean[i] and pred[i] > 50:
                logs.append(float(np.log(ref[i] / pred[i])))
    return out


def metrics(ref: np.ndarray, est: np.ndarray) -> dict:
    ok = np.isfinite(est) & (est > 0)
    ref, est = ref[ok], est[ok]
    ape = np.abs(est / ref - 1)
    big, band = ref >= 1000, (ref >= 2500) & (ref <= 3500)
    return {"lifts": int(ok.sum()), "median_ape_pct": round(100 * np.median(ape), 1),
            "p90_ape_pct": round(100 * np.quantile(ape, 0.9), 1),
            "ge1t_within_10pct": round(float(np.mean(ape[big] <= 0.10)), 3),
            "within_100kg_2.5-3.5t": round(float(np.mean(np.abs(est[band] - ref[band]) <= 100)), 3),
            "median_bias_pct": round(100 * np.median(est / ref - 1), 1)}


def devmonth(d: pd.DataFrame, est: np.ndarray, mask: np.ndarray) -> float:
    x = d[mask].assign(est=est[mask], m=d.actual_at[mask].dt.strftime("%Y-%m"))
    g = x.groupby(["device_id", "m"]).agg(r=("allocated_net_kg", "sum"), e=("est", "sum"))
    return round(float(((g.e / g.r - 1).abs() <= 0.05).mean()), 3)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d = load(DEFAULT_PACK)
    clean = d.clean.to_numpy()
    ref = d.allocated_net_kg.to_numpy()
    est = {
        "A pack density table": (d.vol_collected_m3 * d.typical_compacted_density_kg_m3).to_numpy(),
        "B fleet-learned density (new machine)": d.vol_collected_m3.to_numpy() * fleet_density(d),
    }
    for k in ANCHORS[1:]:
        est[f"C per-machine, {k} earlier tickets"] = per_machine(d, est["B fleet-learned density (new machine)"], k)
    est["REF pack integrated scale (simulated)"] = d.device_estimated_collected_kg.to_numpy()

    # C variants compared on the same lifts: those with >= 10 earlier clean tickets on their machine
    n_prev = d.groupby("device_id").clean.cumsum().to_numpy() - clean
    same = clean & (n_prev >= 10)
    rows = []
    for name, e in est.items():
        rows.append({"estimate": name, "set": "all clean tickets", **metrics(ref[clean], e[clean]),
                     "devmonth_within_5pct": devmonth(d, e, clean & np.isfinite(e))})
        rows.append({"estimate": name, "set": "machines with >=10 prior tickets", **metrics(ref[same], e[same])})
    res = pd.DataFrame(rows)

    best = est["C per-machine, 5 earlier tickets"]
    by = []
    for (mat, cls), g in d[clean].groupby(["material_stream", "equipment_class"]):
        idx = g.index.to_numpy()
        by.append({"material": mat, "class": cls, **metrics(ref[idx], est["B fleet-learned density (new machine)"][idx]),
                   "median_ape_pct_after_5_tickets": metrics(ref[idx], best[idx])["median_ape_pct"]})
    by = pd.DataFrame(by)

    coverage = pd.DataFrame({
        "completed_lifts": [len(d)], "with_shared_ticket": [int(d.shared_ticket.sum())],
        "clean_tickets": [int(clean.sum())], "machines_with_any_clean_ticket": [int(d[clean].device_id.nunique())],
        "machines_total": [int(d.device_id.nunique())],
        "lifts_on_machines_never_calibratable_pct": [round(100 * (~d.device_id.isin(d[clean].device_id)).mean(), 1)],
    })
    res.to_csv(OUT / "fill_baseline.csv", index=False)
    by.to_csv(OUT / "fill_baseline_by_material.csv", index=False)
    coverage.to_csv(OUT / "coverage.csv", index=False)
    pd.set_option("display.width", 220)
    print(coverage.to_string(index=False), "\n")
    print(res.to_string(index=False), "\n")
    print(by.to_string(index=False))


if __name__ == "__main__":
    main()
