"""(1) Device mass vs weighbridge net: how often do they disagree (>3.3 %, >10 %) and why (label causes), plus the EUR effect
of billing on the device basis instead of the weighbridge basis (ECONOMIC_MODEL 2b).  seed-free (no randomness)."""
import sys; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)

df = lifts(); lab = labels()
w = lab[lab.label_family == "WEIGHT_DISCREPANCY"][["entity_id", "explanation_code", "is_actionable", "severity"]].rename(columns={"entity_id": "collection_id"})
d = df[df.status.isin(LIFT)].merge(w, on="collection_id", how="left")
d["dev_kg"] = d.device_estimated_collected_kg
d["wb_kg"] = d.allocated_net_kg
d["rel"] = (d.dev_kg - d.wb_kg) / d.wb_kg.where(d.wb_kg > 0)
d["diff"] = d.dev_kg - d.wb_kg
d["in_label_window"] = d.eval_at.notna()                       # reference economics / labels exist
d["cause"] = d.explanation_code.fillna("NO_LABEL")
res = {}

# ---- universe sizes
lifts_all = d
pair_all = d[d.rel.notna()]
pair_dev = pair_all[pair_all.in_label_window]
res["lifts_all"] = len(lifts_all); res["lifts_in_label_window"] = int(d.in_label_window.sum())
res["pairs_all_year"] = len(pair_all); res["pairs_label_window"] = len(pair_dev)
print(res)

def rates(p):
    return pd.Series({"n": len(p), "gt3.3pct": (p.rel.abs() > .033).mean(), "gt10pct": (p.rel.abs() > .10).mean(),
                      "gt100kg": (p["diff"].abs() > 100).mean(), "median_abs_rel": p.rel.abs().median(), "median_rel": p.rel.median()})
print("\n== Overall rates (all pairs, whole year, no labels)"); print(rates(pair_all).round(4))
print("\n== Overall rates (label window)"); print(rates(pair_dev).round(4))
# ---- noise floor: 'clean' lifts = single load, no side-waste flag, no label, WEIGHED tare, device ok
clean = pair_dev[(pair_dev.cause == "NO_LABEL") & (pair_dev.loads_on_vehicle == 1) & (pair_dev.driver_reported_side_waste != True)]
print("\n== 'Clean' lifts (no label, single load, no side waste) rates"); print(rates(clean).round(4))
print("by tare_method"); print(clean.groupby("tare_method").apply(rates).round(4))
big = clean[clean.rel.abs() > .10]
print("clean lifts with |rel|>10% (unlabelled, probably small loads where abs<threshold):", len(big), " of which |diff|<=100kg:", (big['diff'].abs() <= 100).sum())

# ---- cause split in label window
def cause_group(c):
    return {"SIDE_WASTE_ON_SAME_TRUCK": "side waste on same truck", "COMBINED_LOAD_ALLOCATION": "combined load (50/50 split)",
            "WEIGHBRIDGE_TARE_ERROR": "stale/wrong tare (operator side)", "DEVICE_SENSOR_DRIFT": "device sensor fault/drift/calibration",
            "DEVICE_SENSOR_DEGRADED": "device sensor fault/drift/calibration", "DEVICE_SENSOR_CALIBRATION_GAIN": "device sensor fault/drift/calibration",
            "MEASUREMENT_NOISE_OR_TIMING": "noise/timing (small loads)", "NO_LABEL": "no label (agree or small diff)"}[c]
pair_dev = pair_dev.assign(cause_g=pair_dev.cause.map(cause_group))
tab = pair_dev.groupby("cause_g").apply(lambda p: pd.Series({
    "lifts": len(p), "share_of_pairs": len(p) / len(pair_dev), "gt3.3pct": int((p.rel.abs() > .033).sum()), "gt10pct": int((p.rel.abs() > .10).sum()),
    "median_diff_kg": p["diff"].median(), "median_rel_pct": 100 * p.rel.median(), "actionable_label": bool(p.is_actionable.fillna(False).any())}))
tab["share_of_gt10"] = tab["gt10pct"] / tab["gt10pct"].sum()
tab["share_of_gt3.3"] = tab["gt3.3pct"] / tab["gt3.3pct"].sum()
print("\n== Cause split (label window)"); print(tab.round(3))
tab.round(4).to_csv(OUT / "01_cause_split.csv")
# severity / total disagreements >10 % where label missing in window
print("unlabelled >10% in label window:", int(((pair_dev.cause == "NO_LABEL") & (pair_dev.rel.abs() > .10)).sum()))

# ---- by operator (who has the data to check)
sh = d[d.in_label_window].groupby("operator_id").apply(lambda p: pd.Series({
    "lifts": len(p), "ticket_share": p.ticket_id.notna().mean(), "device_est_share": p.dev_kg.notna().mean(),
    "pairs": int(p.rel.notna().sum()), "gt10_of_pairs": (p.rel.abs() > .10).sum() / max(1, p.rel.notna().sum())}))
print("\n== operator sharing"); print(sh.round(3)); sh.round(4).to_csv(OUT / "01_operator_sharing.csv")

# ---- EUR effect of billing on device basis vs weighbridge basis (ECONOMIC_MODEL 2b)
ref, cv = lift_pricing_inputs()
m = ref.merge(pair_dev[["collection_id", "dev_kg", "wb_kg", "rel", "diff", "cause_g", "loads_on_vehicle", "tare_method", "operator_id"]], on="collection_id")
m["dev_kg_c"] = m.dev_kg.clip(lower=0)
m["inv_wb"] = reprice(m, cv, "billing_mass_kg")
m["inv_dev"] = reprice(m, cv, "dev_kg_c")
m["delta_eur"] = m.inv_wb - m.inv_dev            # + : weighbridge basis costs the customer more
# sanity: reproduces reference
print("\nreprice check vs reference expected_invoice_amount: max abs diff =", float((m.inv_wb - m.expected_invoice_amount_eur).abs().max()))
pricing = pd.read_parquet(PUB / "reference/contract_versions.parquet").set_index("contract_version_id").pricing_model
m["pricing_model"] = m.contract_version_id.map(pricing)
print(m.groupby("pricing_model").agg(n=("delta_eur", "size"), mean_abs=("delta_eur", lambda s: s.abs().mean()), nz=("delta_eur", lambda s: (s.abs() > .005).mean())))
dy = device_years()
g = m.groupby("cause_g").agg(n=("delta_eur", "size"), net=("delta_eur", "sum"), pos=("delta_eur", lambda s: s[s > 0].sum()), neg=("delta_eur", lambda s: s[s < 0].sum()),
                              gross=("delta_eur", lambda s: s.abs().sum()))
g["pos_per_device_year"] = g.pos / dy
print("\n== EUR effect by cause (device basis vs weighbridge basis), label window; device-years =", round(dy, 1)); print(g.round(1))
g.round(2).to_csv(OUT / "01_eur_basis_effect_by_cause.csv")
tot = m.delta_eur
print("TOTAL: net", round(tot.sum(), 1), "pos", round(tot[tot > 0].sum(), 1), "neg", round(tot[tot < 0].sum(), 1), "gross", round(tot.abs().sum(), 1),
      "| total billed (expected invoice) in pairs", round(m.inv_wb.sum(), 1))
# only lifts flagged by tolerance rule (|rel|>3.3%) -> what share of gross effect is above tolerance?
for tol in (.033, .10):
    f = m[m.rel.abs() > tol]
    print(f"flag |rel|>{tol:.3f}: n={len(f)}, gross share captured={f.delta_eur.abs().sum() / tot.abs().sum():.3f}, pos share={f.delta_eur.clip(lower=0).sum() / tot.clip(lower=0).sum():.3f}")
m.to_parquet(OUT / "01_pairs_eur.parquet")
res["device_years"] = dy
import json; json.dump({k: (float(v) if not isinstance(v, str) else v) for k, v in res.items()}, open(OUT / "01_summary.json", "w"), indent=1)

# ---- reconciliation reality on 2.5-3.5 t loads: share within +-100 kg (the challenge target is ~95 % for a single reading)
band = pair_dev[(pair_dev.wb_kg >= 2500) & (pair_dev.wb_kg <= 3500)]
cl_band = band[(band.cause == "NO_LABEL") & (band.loads_on_vehicle == 1) & (band.driver_reported_side_waste != True)]
print("\n2.5-3.5 t loads: all pairs n=%d within 100 kg %.3f | clean (no label, single load, no side-waste flag) n=%d within 100 kg %.3f | clean median |diff| %.1f kg"
      % (len(band), (band["diff"].abs() <= 100).mean(), len(cl_band), (cl_band["diff"].abs() <= 100).mean(), cl_band["diff"].abs().median()))
print("clean 2.5-3.5t: signed median diff %.1f kg (device lower than ticket => material added between last reading and pickup / resolution)" % cl_band["diff"].median())
