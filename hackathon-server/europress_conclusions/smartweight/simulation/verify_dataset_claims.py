"""Check the dataset documentation's claims against the raw synthetic data.

The Europress v1.0.1 pack documents (ASSUMPTIONS_AND_LIMITATIONS, ECONOMIC_MODEL,
assumptions.yaml, ...) are treated as CLAIMS. This script measures each one on the
raw parquet tables and writes results/dataset_checks.json plus a few CSVs.

Everything measured here is measured on SYNTHETIC data. It says what the simulator
does, never what a real compactor or sensor does.

Usage:
    python verify_dataset_claims.py [--data PATH_TO/data/competition/public]
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
DEFAULT_DATA = Path(
    "/home/hackathon/input-files/Europress_SinceAI2026_FINAL/"
    "Europress_SMART_Material_Value_Engine_v1.0.1_PARTICIPANTS (3)/"
    "Europress_SMART_Material_Value_Engine_v1.0.1/data/competition/public"
)

# Claimed compacted densities, configs/assumptions.yaml -> materials.compacted_density
CLAIMED_DENSITY = {
    "cardboard": 190, "paper": 330, "plastic_film": 140,
    "mixed_plastic": 115, "mixed_waste": 380, "biowaste": 620,
}
CREDIT_STREAMS = {"cardboard", "plastic_film", "mixed_plastic"}


def pct(x, q):
    return float(np.nanpercentile(x, q)) if len(x) else float("nan")


def load(data: Path):
    return {
        "dev": pd.read_parquet(data / "reference/devices.parquet"),
        "col": pd.read_parquet(data / "operations/collection_events.parquet"),
        "wb": pd.read_parquet(data / "operations/weighbridge_tickets.parquet"),
        "cv": pd.read_parquet(data / "reference/contract_versions.parquet"),
        "idx": pd.read_parquet(data / "reference/price_index_monthly.parquet"),
    }


def check_weighing_share(t):
    dev = t["dev"]
    share = dev["has_weight_measurement"].mean()
    return {
        "claim": "about 91% of devices have integrated (simulated) weighing",
        "measured_share": round(float(share), 4),
        "weight_measurement_values": dev["weight_measurement"].value_counts().to_dict(),
        "held_up": bool(abs(share - 0.91) < 0.03),
    }


def completed_pickups(t):
    col = t["col"].merge(
        t["dev"][["device_id", "material_stream", "equipment_class", "container_volume_m3"]],
        on="device_id",
    )
    return col[col["status"] == "COMPLETED"].copy()


def check_load_mass(t):
    col = completed_pickups(t)
    out = {}
    for mat, g in col.groupby("material_stream"):
        m = g["device_estimated_collected_kg"].dropna()
        out[mat] = {
            "n": int(len(m)), "p10": pct(m, 10), "median": pct(m, 50),
            "p90": pct(m, 90), "max": float(m.max()),
            "share_ge_2500kg": round(float((m >= 2500).mean()), 4),
        }
    allm = col["device_estimated_collected_kg"].dropna()
    return {
        "claim": "the +-100 kg target refers to a ~3,000 kg cardboard load",
        "by_material": out,
        "overall_median_kg": pct(allm, 50),
        "overall_share_ge_2500kg": round(float((allm >= 2500).mean()), 4),
    }


def check_density(t):
    col = completed_pickups(t)
    g = col[(col["device_fill_pct_before"] >= 60) & col["device_mass_kg_before"].notna()].copy()
    g["rho"] = g["device_mass_kg_before"] / (g["device_fill_pct_before"] / 100 * g["container_volume_m3"])
    rows, out = [], {}
    for mat, d in g.groupby("material_stream"):
        dev_med = d.groupby("device_id")["rho"].median()
        within = d.groupby("device_id")["rho"].agg(lambda x: x.std() / x.mean() if len(x) > 3 else np.nan)
        med = float(d["rho"].median())
        out[mat] = {
            "n": int(len(d)), "median_kg_m3": round(med, 1),
            "claimed_kg_m3": CLAIMED_DENSITY.get(mat),
            "between_device_cv": round(float(dev_med.std() / dev_med.mean()), 4),
            "median_within_device_cv": round(float(within.median()), 4),
            "held_up_within_15pct": bool(abs(med / CLAIMED_DENSITY[mat] - 1) < 0.15),
        }
        rows.append({"material": mat, **out[mat]})
    pd.DataFrame(rows).to_csv(RESULTS / "dataset_density_check.csv", index=False)
    return {"claim": "compacted densities as in assumptions.yaml", "by_material": out}


def paired_device_ticket(t):
    col = completed_pickups(t)
    j = col.merge(t["wb"], on="operator_job_ref", how="inner", suffixes=("", "_wb"))
    clean = j[
        (j["allocation_method"] == "SINGLE_LOAD")
        & (j["tare_method"] == "WEIGHED")
        & (j["driver_reported_side_waste"] != True)  # noqa: E712
        & j["device_estimated_collected_kg"].notna()
    ].copy()
    clean["err_kg"] = clean["device_estimated_collected_kg"] - clean["net_kg"]
    clean["err_rel"] = clean["err_kg"] / clean["net_kg"].clip(lower=1)
    return j, clean


def check_device_vs_ticket(t):
    j, clean = paired_device_ticket(t)
    big = clean[(clean["material_stream"] == "cardboard") & clean["net_kg"].between(2500, 3500)]
    ge1t = clean[clean["net_kg"] >= 1000]
    stored = j[(j["allocation_method"] == "SINGLE_LOAD") & (j["tare_method"] == "STORED")
               & j["device_estimated_collected_kg"].notna() & (j["net_kg"] >= 1000)]
    stored_rel = (stored["device_estimated_collected_kg"] - stored["net_kg"]) / stored["net_kg"]
    res = {
        "claim": "integrated weighing within ~100 kg on a 3 t cardboard load for ~95% of normal readings",
        "note": "ticket net is itself noisy (sigma 12 kg, 20 kg resolution, two weighings); "
                "difference includes ticket error and all injected sensor faults",
        "n_clean_pairs": int(len(clean)),
        "cardboard_2.5_3.5t": {
            "n": int(len(big)),
            "share_within_100kg": round(float((big["err_kg"].abs() <= 100).mean()), 4),
            "median_abs_err_kg": pct(big["err_kg"].abs(), 50),
            "p95_abs_err_kg": pct(big["err_kg"].abs(), 95),
        },
        "all_ge_1t": {
            "n": int(len(ge1t)),
            "share_within_3.3pct": round(float((ge1t["err_rel"].abs() <= 0.033).mean()), 4),
            "share_within_5pct": round(float((ge1t["err_rel"].abs() <= 0.05).mean()), 4),
            "median_rel_err": round(pct(ge1t["err_rel"], 50), 4),
        },
        "stored_tare_ge1t_median_abs_rel": round(pct(stored_rel.abs(), 50), 4),
        "weighed_tare_ge1t_median_abs_rel": round(pct(ge1t["err_rel"].abs(), 50), 4),
    }
    res["held_up"] = bool(res["cardboard_2.5_3.5t"]["share_within_100kg"] >= 0.90)
    return res


def check_tickets(t):
    wb = t["wb"]
    return {
        "claim": "weighbridge resolution 20 kg; 45% stored tare",
        "share_net_multiple_of_20": round(float((wb["net_kg"] % 20 == 0).mean()), 4),
        "share_gross_multiple_of_20": round(float((wb["gross_kg"] % 20 == 0).mean()), 4),
        "tare_method_share": wb["tare_method"].value_counts(normalize=True).round(4).to_dict(),
        "allocation_method_share": wb["allocation_method"].value_counts(normalize=True).round(4).to_dict(),
    }


def check_press_index(data: Path):
    files = sorted(glob.glob(str(data / "telemetry/telemetry_hourly/month=2026-0[1-3]/*.parquet")))
    df = pd.concat([pd.read_parquet(f, columns=["device_id", "fill_pct", "press_load_index", "mass_kg"])
                    for f in files])
    d = df.dropna(subset=["fill_pct", "press_load_index"])
    r_fill = float(np.corrcoef(d["fill_pct"], d["press_load_index"])[0, 1])
    dm = d.dropna(subset=["mass_kg"])
    dm = dm[dm["fill_pct"] > 20]
    r_mass = float(np.corrcoef(dm["mass_kg"], dm["press_load_index"])[0, 1])
    X = np.column_stack([np.ones(len(dm)), dm["fill_pct"], dm["press_load_index"]])
    beta, *_ = np.linalg.lstsq(X, dm["mass_kg"], rcond=None)
    bf, *_ = np.linalg.lstsq(X[:, :2], dm["mass_kg"], rcond=None)
    r2_full = 1 - np.var(dm["mass_kg"] - X @ beta) / np.var(dm["mass_kg"])
    r2_fill = 1 - np.var(dm["mass_kg"] - X[:, :2] @ bf) / np.var(dm["mass_kg"])
    return {
        "claim": "press_load_index is derived from the fill estimate (no independent pressure info)",
        "n_rows": int(len(d)),
        "corr_fill_vs_press_index": round(r_fill, 4),
        "corr_mass_vs_press_index_fill_gt20": round(r_mass, 4),
        "pooled_r2_mass_from_fill": round(float(r2_fill), 4),
        "pooled_r2_mass_from_fill_plus_press": round(float(r2_full), 4),
        "held_up": bool(r_fill > 0.95),
    }


def check_fill_baseline(t):
    """Fill x density baseline (Model D) on the synthetic pack, scored against clean tickets."""
    _, clean = paired_device_ticket(t)
    c = clean[clean["net_kg"] >= 500].sort_values("actual_at").copy()
    c["vol_m3"] = c["device_fill_pct_before"] / 100 * c["container_volume_m3"]
    c["pred_table"] = c["vol_m3"] * c["material_stream"].map(CLAIMED_DENSITY)
    e = (c["pred_table"] - c["net_kg"]) / c["net_kg"]
    out = {"table_density_no_calibration": {
        "n_eval": int(len(e)),
        "median_abs_rel": round(pct(e.abs(), 50), 4),
        "share_within_5pct": round(float((e.abs() <= 0.05).mean()), 4),
        "share_within_10pct": round(float((e.abs() <= 0.10).mean()), 4),
    }}
    for k in (3, 8):
        errs = []
        for _, g in c.groupby("device_id"):
            if len(g) <= k + 2:
                continue
            cal, ev = g.iloc[:k], g.iloc[k:]
            rho = np.median(cal["net_kg"] / cal["vol_m3"].clip(lower=0.1))
            errs.append(((ev["vol_m3"] * rho) - ev["net_kg"]) / ev["net_kg"])
        e = pd.concat(errs)
        out[f"device_calibrated_k{k}"] = {
            "n_eval": int(len(e)),
            "median_abs_rel": round(pct(e.abs(), 50), 4),
            "p95_abs_rel": round(pct(e.abs(), 95), 4),
            "share_within_5pct": round(float((e.abs() <= 0.05).mean()), 4),
            "share_within_10pct": round(float((e.abs() <= 0.10).mean()), 4),
        }
    out["note"] = ("measures the SIMULATOR's density variability, not real waste. "
                   "It is the synthetic world's bar for fill-only estimation.")
    return out


def check_economics(t):
    """EUR per tonne that depends on mass: haul + processing fees and material credits."""
    cv = t["cv"].sort_values("effective_from").groupby("contract_id").tail(1)
    dev = t["dev"][["device_id", "contract_id", "material_stream"]]
    m = dev.merge(cv, on="contract_id", how="left")
    m["mass_fee_eur_per_t"] = (m["haul_fee_cents_per_t"] + m["processing_fee_cents_per_t"]) / 100
    idx = t["idx"].groupby("material")["price_eur_per_t"].mean().to_dict()
    m["credit_eur_per_t"] = [
        (idx.get(s, 0.0) * bp / 10000) if s in CREDIT_STREAMS else 0.0
        for s, bp in zip(m["material_stream"], m["credit_share_bp"])
    ]
    m["mass_sensitive_eur_per_t"] = m["mass_fee_eur_per_t"] + m["credit_eur_per_t"]
    col = completed_pickups(t)
    tonnes = col.groupby("device_id")["device_estimated_collected_kg"].sum() / 1000
    lifts = col.groupby("device_id").size()
    m = m.merge(tonnes.rename("t_per_year"), on="device_id").merge(
        lifts.rename("lifts_per_year"), on="device_id")
    m["eur_mass_sensitive_per_year"] = m["t_per_year"] * m["mass_sensitive_eur_per_t"]
    summ = m.groupby("material_stream").agg(
        devices=("device_id", "count"),
        median_t_per_year=("t_per_year", "median"),
        median_lifts_per_year=("lifts_per_year", "median"),
        median_mass_fee_eur_per_t=("mass_fee_eur_per_t", "median"),
        median_credit_eur_per_t=("credit_eur_per_t", "median"),
        median_eur_mass_sensitive_per_year=("eur_mass_sensitive_per_year", "median"),
        mean_eur_mass_sensitive_per_year=("eur_mass_sensitive_per_year", "mean"),
    ).round(2)
    summ.to_csv(RESULTS / "dataset_economics_by_material.csv")
    m[["device_id", "material_stream", "pricing_model", "t_per_year", "lifts_per_year",
       "mass_fee_eur_per_t", "credit_eur_per_t", "eur_mass_sensitive_per_year"]].to_csv(
        RESULTS / "dataset_economics_by_device.csv", index=False)
    return {
        "note": "hypothetical synthetic tariffs; EUR whose amount scales with billed mass; "
                "the window is ~1 year, so totals are per device-year",
        "share_devices_with_any_mass_sensitive_tariff": round(float((m["mass_sensitive_eur_per_t"] > 0).mean()), 4),
        "pricing_model_share": m["pricing_model"].value_counts(normalize=True).round(4).to_dict(),
        "fleet_median_eur_mass_sensitive_per_device_year": round(float(m["eur_mass_sensitive_per_year"].median()), 2),
        "fleet_mean_eur_mass_sensitive_per_device_year": round(float(m["eur_mass_sensitive_per_year"].mean()), 2),
        "fleet_median_t_per_device_year": round(float(m["t_per_year"].median()), 2),
        "by_material": summ.reset_index().to_dict(orient="records"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA)
    a = ap.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    t = load(a.data)
    out = {
        "C1_weighing_share": check_weighing_share(t),
        "C2_load_mass": check_load_mass(t),
        "C3_density": check_density(t),
        "C4_device_vs_ticket": check_device_vs_ticket(t),
        "C5_tickets": check_tickets(t),
        "C6_press_load_index": check_press_index(a.data),
        "C7_fill_baseline": check_fill_baseline(t),
        "C8_economics": check_economics(t),
    }
    (RESULTS / "dataset_checks.json").write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
