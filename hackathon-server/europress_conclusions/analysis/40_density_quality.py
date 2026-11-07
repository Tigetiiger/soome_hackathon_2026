"""UC4 Material quality: density proxy = device mass before lift / fill % before lift (kg per fill-pp), relative to the device's own
as-of baseline (median of its previous 8 lifts, needs >=4). No labels used to fit. Evaluated vs MOISTURE_HEAVY_LOAD (collection labels) and
CONTAMINATION_INCIDENT (device periods -> lifts inside), with EUR at stake from grade downgrade (CONTAMINATION_VALUE_LOSS / REJECTED_LOAD
value_at_stake: credit x (1 - grade factor A1.0/B0.85/C0.6) + penalties). Synthetic data, hypothetical prices."""
import json
from ec_common import *
dv = device_segments(); lab = labels(); df = lifts(); res = {}
L = df[df.status.isin(LIFT)].copy()
L = L[L.device_mass_kg_before.notna() & (L.device_fill_pct_before >= 30)].sort_values(["device_id", "actual_at"])
L["kgpf"] = L.device_mass_kg_before / L.device_fill_pct_before
L["base"] = L.groupby("device_id").kgpf.transform(lambda s: s.shift(1).rolling(8, min_periods=4).median())
L["z"] = np.log(L.kgpf / L.base)
L = L[L.base.notna() & L.eval_at.notna()]
mo = lab[lab.label_family == "MOISTURE_HEAVY_LOAD"].entity_id
L["y_moist"] = L.collection_id.isin(mo)
ci = lab[lab.label_family == "CONTAMINATION_INCIDENT"][["device_id", "event_at", "end_at"]]
L["y_cont"] = False
for r in ci.itertuples():
    L.loc[(L.device_id == r.device_id) & (L.actual_at >= r.event_at) & (L.actual_at <= r.end_at + pd.Timedelta(days=3)), "y_cont"] = True
cv = lab[lab.label_family.isin(["CONTAMINATION_VALUE_LOSS", "REJECTED_LOAD"])].groupby("entity_id").value_at_stake_eur.sum()
L["grade_loss_eur"] = L.collection_id.map(cv).fillna(0)
L["credit_stream"] = L.material_stream.isin(["cardboard", "plastic_film", "mixed_plastic"])
print("lifts evaluated", len(L), "moist", int(L.y_moist.sum()), "cont-lifts", int(L.y_cont.sum()))
print(L.groupby(["material_stream"]).apply(lambda g: pd.Series({"z_normal_med": g.z[~g.y_moist & ~g.y_cont].median(), "z_moist_med": g.z[g.y_moist].median(), "z_cont_med": g.z[g.y_cont].median(),
                                                                "n_moist": g.y_moist.sum(), "n_cont": g.y_cont.sum()})).round(3))
rows = []
for thr in (.10, .15, .20, .25, .30):
    for name, y, flag in [("moisture (z>+thr)", L.y_moist, L.z > thr), ("contamination (|z|>thr)", L.y_cont, L.z.abs() > thr), ("contamination (z>+thr)", L.y_cont, L.z > thr),
                          ("any density anomaly (|z|>thr) vs moist|cont", L.y_moist | L.y_cont, L.z.abs() > thr)]:
        tp = int((flag & y).sum()); fp = int((flag & ~y).sum()); fn = int((~flag & y).sum())
        rows.append({"target": name, "thr": thr, "tp": tp, "fp": fp, "fn": fn, "precision": round(tp / max(1, tp + fp), 3), "recall": round(tp / max(1, tp + fn), 3),
                     "grade_loss_eur_on_flagged_true": round(float(L.loc[flag & y, "grade_loss_eur"].sum()), 0)})
pr = pd.DataFrame(rows); print(pr.to_string(index=False)); pr.to_csv(OUT2 / "40_density_pr.csv", index=False)
# restricted to outdoor-staging sites for moisture (observable site attribute)
L = L.merge(dv[["device_id", "outdoor_material_staging", "primary_sector"]], on="device_id", how="left")
for thr in (.15, .20):
    f = (L.z > thr) & L.outdoor_material_staging.fillna(False).astype(bool) & L.material_stream.isin(["cardboard", "paper"])
    tp = int((f & L.y_moist).sum()); print(f"moisture rule z>{thr} & outdoor & cardboard/paper: tp {tp} fp {int((f & ~L.y_moist).sum())} recall {tp / max(1, L.y_moist.sum()):.3f} precision {tp / max(1, f.sum()):.3f}")
# EUR context: total grade-loss EUR (all lifts, label window) by stream and share that falls in contamination-incident periods
gl = lab[lab.label_family.isin(["CONTAMINATION_VALUE_LOSS", "REJECTED_LOAD"])].merge(dv[["device_id"] + SEGS], on="device_id", how="left")
seg = per_segment(gl, "value_at_stake_eur", dv); seg["eur_per_device_year"] = (seg.eur_per_device_year * YEAR_FACTOR).round(1)
print(seg.to_string(index=False)); seg.to_csv(OUT2 / "40_grade_loss_by_segment.csv", index=False)
credit_dy = dv[dv.material_stream.isin(["cardboard", "plastic_film", "mixed_plastic"])].dev_years.sum()
res["grade_loss_total_window"] = float(gl.value_at_stake_eur.sum()); res["grade_loss_per_credit_device_year"] = float(gl.value_at_stake_eur.sum() / credit_dy * YEAR_FACTOR)
res["grade_loss_in_incident_lifts_eur"] = float(L.loc[L.y_cont, "grade_loss_eur"].sum())
res["moisture_extra_cost_note"] = "see 40_moisture_eur"
# moisture EUR: extra billed mass x per-tonne components (processing + per-tonne haul) on labelled wet loads
ml = lab[lab.label_family == "MOISTURE_HEAVY_LOAD"][["entity_id", "true_moisture_extra_pct"]].rename(columns={"entity_id": "collection_id"})
ref = rd("labels_dev/reference_economics.parquet").merge(ml, on="collection_id")
ref["extra_share"] = (ref.true_moisture_extra_pct / 100) / (1 + ref.true_moisture_extra_pct / 100)
ref["moist_eur"] = ref.processing_cost_eur * ref.extra_share
res["moisture_lifts"] = len(ref); res["moisture_processing_eur_on_water"] = float(ref.moist_eur.sum())
res["moisture_mean_extra_kg"] = float((ref.billing_mass_kg * ref.extra_share).mean())
json.dump(res, open(OUT2 / "40_summary.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
L[["collection_id", "device_id", "material_stream", "actual_at", "device_mass_kg_before", "device_fill_pct_before", "kgpf", "base", "z", "y_moist", "y_cont", "grade_loss_eur"]].to_parquet(OUT2 / "40_density_lifts.parquet")
