"""Shared loaders for the data-analyst evidence scripts (seed fixed, read-only on the dataset)."""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20261106
ROOT = Path("/home/hackathon/europress_data/Europress_SMART_Material_Value_Engine_v1.0.1")
PUB = ROOT / "data" / "competition" / "public"
OUT = Path("/home/hackathon/soome_hackathon_2026/analysis/outputs")
OUT.mkdir(parents=True, exist_ok=True)
LIFT = ("COMPLETED", "PARTIAL")
TZ = "Europe/Helsinki"


def rd(rel, **kw):
    return pd.read_parquet(PUB / rel, **kw)


def lifts():
    """One row per completed/partial lift with device, ticket, quality, labels and reference economics attached."""
    ce = rd("operations/collection_events.parquet")
    dev = rd("reference/devices.parquet")[["device_id", "material_stream", "equipment_class", "container_volume_m3",
                                           "has_weight_measurement", "collection_policy", "operator_id"]] \
        .rename(columns={"operator_id": "dev_operator_id"})
    wb = rd("operations/weighbridge_tickets.parquet").drop_duplicates("operator_job_ref")
    qa = rd("operations/quality_assessments.parquet")[["ticket_id", "grade", "contamination_pct_est", "remark_code"]]
    ref = rd("labels_dev/reference_economics.parquet")
    df = ce.merge(dev, on="device_id", how="left").merge(
        wb[["operator_job_ref", "ticket_id", "gross_kg", "tare_kg", "tare_method", "net_kg", "allocated_net_kg",
            "allocation_method", "loads_on_vehicle", "published_at", "arrival_at"]], on="operator_job_ref", how="left")
    df = df.merge(qa, on="ticket_id", how="left")
    df = df.merge(ref.drop(columns=["device_id", "contract_id", "status", "event_at"]), on="collection_id", how="left")
    return df


def labels():
    return rd("labels_dev/anomaly_labels.parquet")


# ---------------------------------------------------------------------------------------------------------
# Re-pricing with an alternative billing mass (uses the dataset's own economics engine, copied read-only)
import sys
sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis/baseline_run/src")
from europress_data.economics import price_event, summarize  # noqa: E402


def lift_pricing_inputs():
    """Reference-economics lifts joined to contract version, flags from reference charge lines."""
    ref = rd("labels_dev/reference_economics.parquet")
    rcl = rd("labels_dev/reference_charge_lines.parquet")
    flags = rcl.assign(emergency=rcl.line_type == "EMERGENCY_SURCHARGE", side_waste=rcl.line_type == "SIDE_WASTE_FEE") \
        .groupby("collection_id")[["emergency", "side_waste"]].any()
    cv = rd("reference/contract_versions.parquet").set_index("contract_version_id")
    mat = rd("reference/material_classes.parquet").set_index("material_stream").credit_eligible
    dev = rd("reference/devices.parquet")[["device_id", "material_stream"]].set_index("device_id")
    ref = ref[ref.status.isin(LIFT)].merge(flags, left_on="collection_id", right_index=True, how="left").fillna({"emergency": False, "side_waste": False})
    ref["material_stream"] = ref.device_id.map(dev.material_stream)
    ref["credit_eligible"] = ref.material_stream.map(mat).astype(bool)
    return ref, cv


def reprice(ref, cv, kg_col, grade_col="grade_applied"):
    """Return invoice amount in EUR if every lift were billed on `kg_col` (NaN -> NaN). Same grade/index/tariffs."""
    vers = cv.to_dict("index")
    out = np.full(len(ref), np.nan)
    for i, r in enumerate(ref.itertuples(index=False)):
        kg = getattr(r, kg_col)
        if pd.isna(kg):
            continue
        g = getattr(r, grade_col)
        g = None if (g is None or (isinstance(g, float) and np.isnan(g))) else g
        idx = None if pd.isna(r.index_price_eur_per_t) else int(round(r.index_price_eur_per_t * 100))
        res = price_event(vers[r.contract_version_id], r.status, max(0, int(round(kg))), g, idx,
                          emergency=bool(r.emergency), side_waste=bool(r.side_waste), credit_eligible=bool(r.credit_eligible))
        out[i] = summarize(res["lines"], max(0, int(round(kg))))["invoice_amount_cents"] / 100
    return out


WINDOW = (pd.Timestamp("2025-10-01"), pd.Timestamp("2026-08-01"))   # label window (train+validation), 304 days


def device_years(window=WINDOW, only_weighted=False):
    """Active device-years inside the label window (devices commissioned/decommissioned inside the window count pro rata)."""
    dv = rd("reference/devices.parquet")
    if only_weighted:
        dv = dv[dv.has_weight_measurement]
    a = pd.to_datetime(dv.active_from).fillna(window[0]).clip(lower=window[0])
    b = pd.to_datetime(dv.active_to).fillna(window[1]).clip(upper=window[1])
    return float(((b - a).dt.days.clip(lower=0)).sum() / 365.0)
