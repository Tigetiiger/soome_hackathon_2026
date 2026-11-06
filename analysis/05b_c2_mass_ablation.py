"""Task C2 mass-source ablation: how much of the C2 score (value captured / regret) depends on knowing the billing mass?
Re-runs baseline B1 -> B2 invoice flags -> B6 with different mass sources, and scores on the public dev labels.
Usage: python 05b_c2_mass_ablation.py MODE   with MODE in default|oracle|device_only|no_weight|no_device"""
import sys, json, zlib
from pathlib import Path
BR = Path("/home/hackathon/soome_hackathon_2026/analysis/baseline_run")
sys.path.insert(0, str(BR / "src")); sys.path.insert(0, str(BR / "baselines"))
import numpy as np, pandas as pd
import b1_economic_calculator as b1m
from b1_economic_calculator import load_inputs
from europress_data.economics import price_event, summarize
from b2_rules_anomaly import detect_invoices
from b6_operator_actions import decide as decide_c2
from europress_data.evaluate import score_c2

MODE = sys.argv[1]
SEED = 20261106
PUB = BR / "data" / "competition" / "public"


def compute(root, mode):
    con, ce, cv, wb, qa, il, pi = load_inputs(root)
    ref = pd.read_parquet(PUB / "labels_dev" / "reference_economics.parquet").set_index("collection_id").billing_mass_kg
    vers = {k: g.to_dict("records") for k, g in cv.groupby("contract_id")}
    wbm = wb.merge(qa, on="ticket_id", how="left").drop_duplicates("operator_job_ref").set_index("operator_job_ref")
    inv_t = il[il.unit == "t"].groupby("operator_job_ref").quantity.max()
    inv_types = il.groupby("operator_job_ref").line_type.apply(set)
    idx = {(r.index_id, r.month): int(round(r.price_eur_per_t * 100)) for r in pi.itertuples()}
    rows, lines = [], []
    for r in ce.itertuples():
        vl = vers[r.contract_id]; v = vl[0]
        for vv in vl:
            if vv["effective_from"] <= r.service_date:
                v = vv
        kg, basis, grade = None, "NOT_A_LIFT", None
        if r.status in ("COMPLETED", "PARTIAL"):
            have_ticket = r.operator_job_ref in wbm.index
            dev_ok = pd.notna(r.device_estimated_collected_kg)
            if mode == "oracle" and r.collection_id in ref.index and pd.notna(ref[r.collection_id]):
                kg, basis = int(ref[r.collection_id]), "ORACLE"
            elif mode == "none":                # no mass source at all
                kg, basis = None, "UNKNOWN"
            elif mode.startswith("sim:"):       # hypothetical device of relative accuracy sigma (1 sd, % of load, floor 15 kg) replaces all mass sources
                sig = float(mode.split(":")[1]) / 100
                m0 = ref.get(r.collection_id, np.nan)
                if pd.notna(m0):
                    rng = np.random.default_rng(SEED + (zlib.crc32(r.collection_id.encode()) % 1000003) + int(sig * 10000))
                    kg, basis = max(0, int(round(m0 + rng.normal(0, max(15.0, sig * m0))))), "SIM_DEVICE"
                elif dev_ok:
                    kg, basis = max(0, int(round(r.device_estimated_collected_kg))), "DEVICE_ESTIMATE"
                else:
                    basis = "UNKNOWN"
            elif mode == "device_only":
                kg, basis = (max(0, int(round(r.device_estimated_collected_kg))), "DEVICE_ESTIMATE") if dev_ok else (None, "UNKNOWN")
            elif mode == "no_weight":          # no tickets shared, no device weight: only the operator's invoice tonnage
                kg, basis = (int(round(inv_t[r.operator_job_ref] * 1000)), "INVOICE_QUANTITY") if r.operator_job_ref in inv_t.index else (None, "UNKNOWN")
            elif mode == "no_device":           # tickets + invoice tonnage, no device fallback
                if have_ticket:
                    kg, basis = max(0, int(wbm.loc[r.operator_job_ref, "allocated_net_kg"])), "WEIGHBRIDGE"
                elif r.operator_job_ref in inv_t.index:
                    kg, basis = int(round(inv_t[r.operator_job_ref] * 1000)), "INVOICE_QUANTITY"
                else:
                    basis = "UNKNOWN"
            else:                               # default B1 chain
                if have_ticket:
                    kg, basis = max(0, int(wbm.loc[r.operator_job_ref, "allocated_net_kg"])), "WEIGHBRIDGE"
                elif r.operator_job_ref in inv_t.index:
                    kg, basis = int(round(inv_t[r.operator_job_ref] * 1000)), "INVOICE_QUANTITY"
                elif dev_ok:
                    kg, basis = max(0, int(round(r.device_estimated_collected_kg))), "DEVICE_ESTIMATE"
                else:
                    basis = "UNKNOWN"
            if have_ticket and mode in ("default", "no_device", "oracle"):
                g = wbm.loc[r.operator_job_ref, "grade"]; grade = g if isinstance(g, str) else None
            if r.credit_eligible and grade is None:
                types = inv_types.get(r.operator_job_ref, set())
                grade = "R" if "REJECTION_REPROCESSING" in types else "C" if "CONTAMINATION_PENALTY" in types else "A"
        ix = idx.get((r.price_index_id, str(r.service_date)[:7])) if r.credit_eligible else None
        res = price_event(v, r.status, kg, grade, ix, emergency=r.original_trigger_type == "AD_HOC_CUSTOMER",
                          side_waste=bool(False if pd.isna(r.driver_reported_side_waste) else r.driver_reported_side_waste),
                          notice_hours=None if pd.isna(r.cancellation_notice_hours) else float(r.cancellation_notice_hours), credit_eligible=bool(r.credit_eligible))
        s = summarize(res["lines"], kg)
        rows.append({"collection_id": r.collection_id, "device_id": r.device_id, "contract_id": r.contract_id, "contract_version_id": v["contract_version_id"],
                     "operator_job_ref": r.operator_job_ref, "status": r.status, "service_date": r.service_date, "mass_kg": kg, "mass_basis": basis, "grade": grade,
                     "collection_cost_eur": s["collection_cost_cents"] / 100, "processing_cost_eur": s["processing_cost_cents"] / 100, "penalties_eur": s["penalties_cents"] / 100,
                     "material_credit_eur": s["material_credit_cents"] / 100, "net_material_contribution_eur": s["net_material_contribution_cents"] / 100,
                     "collection_cost_eur_per_t": s["collection_cost_eur_per_t"], "benchmark_eur_per_t": v["target_collection_cost_cents_per_t"] / 100, "mass_known": kg is not None})
        for ln in res["lines"]:
            lines.append({"collection_id": r.collection_id, "operator_job_ref": r.operator_job_ref, "line_type": ln["line_type"], "quantity": float(ln["quantity"]),
                          "unit_price_eur": ln["unit_price_cents"] / 100, "amount_eur": ln["amount_cents"] / 100})
    con.close()
    return pd.DataFrame(rows), pd.DataFrame(lines)


b1, b1l = compute(PUB, MODE)
print(MODE, "mass basis:", b1.mass_basis.value_counts().to_dict(), flush=True)
flags = detect_invoices(PUB, b1, b1l)
pred = decide_c2(PUB, b1, b1l, flags)
sc = score_c2(pred, PUB / "labels_dev", "dev")
out = {"mode": MODE, "mass_basis": b1.mass_basis.value_counts().to_dict(), **{k: sc[k] for k in sc if not isinstance(sc[k], (dict, list))}}
print(json.dumps(out, indent=1, default=str))
json.dump({"mode": MODE, "score": sc}, open(f"/home/hackathon/soome_hackathon_2026/analysis/outputs/05b_c2_ablation_{MODE.replace(':', '_')}.json", "w"), indent=1, default=str)
