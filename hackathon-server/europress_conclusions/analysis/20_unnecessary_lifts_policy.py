"""UC2 Unnecessary/premature lifts by collection policy (FIXED / HYBRID = 'Poland-like', ON_CALL = Finland-like).
(a) PREMATURE_UNJUSTIFIED EUR + lifts per device-year by policy/stream/operator; (b) what fill-only vs mass-aware rules catch, by policy
(reuses kg-per-fill calibration of soome analysis/03); (c) Task C simulated decision value by policy and action, split by whether the
action needs weight (MASS_TARGET_TRIGGER). Synthetic data, hypothetical prices."""
import json
from ec_common import *
dv = device_segments(); lab = labels(); df = lifts(); res = {}
pl = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & lab.is_actionable].copy()
pl = pl.merge(dv[["device_id"] + SEGS + ["has_weight_measurement", "fixed_schedule_per_week"]], on="device_id", how="left")
pl["one"] = 1.0
seg = per_segment(pl, "value_at_stake_eur", dv); seg["eur_per_device_year"] = (seg.eur_per_device_year * YEAR_FACTOR).round(1)
lifts_dy = per_segment(pl, "one", dv)[["segment", "value", "eur_per_device_year"]].rename(columns={"eur_per_device_year": "lifts_per_device_year"})
lifts_dy["lifts_per_device_year"] = (lifts_dy.lifts_per_device_year * YEAR_FACTOR).round(2)
seg = seg.merge(lifts_dy, on=["segment", "value"]); print(seg.to_string(index=False)); seg.to_csv(OUT2 / "20a_premature_by_segment.csv", index=False)
xt = pl.pivot_table(index="collection_policy", columns="explanation_code", values="value_at_stake_eur", aggfunc="sum", fill_value=0).round(0)
xt["devyears"] = dv.groupby("collection_policy").dev_years.sum().round(1); print(xt); xt.to_csv(OUT2 / "20a_premature_policy_x_code.csv")
# all completed lifts per policy -> share unnecessary
L = df[df.status.isin(LIFT) & df.eval_at.notna()]
sh = L.groupby("collection_policy").size().to_frame("lifts").join(pl.groupby("collection_policy").size().to_frame("unjustified"))
sh["share"] = (sh.unjustified / sh.lifts).round(3); print(sh); sh.to_csv(OUT2 / "20a_share_unjustified_by_policy.csv")
# per-device distribution, FIXED+HYBRID only
fh = dv[dv.collection_policy.isin(["FIXED_SCHEDULE", "HYBRID"])]
res["fixed_hybrid_device_dist_eur_per_dy"] = {k: (v * YEAR_FACTOR if k != "share_devices_nonzero" else v) for k, v in device_dist(pl, "value_at_stake_eur", fh).items()}
res["on_call_device_dist_eur_per_dy"] = {k: (v * YEAR_FACTOR if k != "share_devices_nonzero" else v) for k, v in device_dist(pl, "value_at_stake_eur", dv[dv.collection_policy == "ON_CALL"]).items()}
# median lift cost by policy (for context)
ref = rd("labels_dev/reference_economics.parquet").merge(dv[["device_id", "collection_policy"]], on="device_id")
res["median_lift_cost_by_policy"] = ref[ref.status == "COMPLETED"].groupby("collection_policy").total_customer_cost_eur.median().round(1).to_dict()

# (b) detection by policy: fill-only vs mass-aware (same kg-per-fill calibration as soome 03)
tel = pd.read_parquet(OUT / "telemetry_dedup.parquet", columns=["device_id", "measured_at", "fill_pct", "mass_kg", "quality_flag"])
t0 = tel.measured_at.min()
cal = tel[(tel.measured_at < t0 + pd.Timedelta(days=120)) & (tel.quality_flag == "VALID") & tel.fill_pct.between(50, 95) & (tel.mass_kg > 0)]
kgpp = (cal.mass_kg / cal.fill_pct).groupby(cal.device_id).median(); n_cal = cal.groupby("device_id").size(); kgpp = kgpp[n_cal.reindex(kgpp.index) >= 20]
del tel, cal
H = L[L.actual_at >= t0 + pd.Timedelta(days=120)].merge(pl[["entity_id", "explanation_code", "value_at_stake_eur"]].rename(columns={"entity_id": "collection_id"}), on="collection_id", how="left")
H["kgpp"] = H.device_id.map(kgpp); H["mass_fill"] = H.device_mass_kg_before / H.kgpp; H["fill"] = H.device_fill_pct_before
H = H[H.fill.notna() & H.mass_fill.notna()]
H["y"] = H.explanation_code.notna()
H["fill_rule"] = H.fill < 40
H["mass_rule"] = (H.fill < 40) | (H.mass_fill < 40)
rows = []
for pol, g in H.groupby("collection_policy"):
    for rule in ["fill_rule", "mass_rule"]:
        tp = (g[rule] & g.y).sum(); fp = (g[rule] & ~g.y).sum(); fn = (~g[rule] & g.y).sum()
        rows.append({"policy": pol, "rule": rule, "tp": int(tp), "fp": int(fp), "fn": int(fn), "precision": round(tp / max(1, tp + fp), 3), "recall": round(tp / max(1, tp + fn), 3),
                     "eur_caught": round(float(g.loc[g[rule] & g.y, "value_at_stake_eur"].sum()), 0), "eur_total": round(float(g.loc[g.y, "value_at_stake_eur"].sum()), 0)})
det = pd.DataFrame(rows); print(det.to_string(index=False)); det.to_csv(OUT2 / "20b_detection_by_policy.csv", index=False)

# (c) Task C simulated decision value (train+validation labels): best action per case, annualised per device-year
dc = rd("benchmark/decision_cases.parquet"); dt = rd("labels_dev/decision_truth.parquet"); do = rd("labels_dev/decision_outcomes.parquet")
x = dt.merge(dc[["case_id", "device_id", "horizon_days"]], on="case_id").merge(dv[["device_id", "collection_policy", "material_stream", "operator_id", "has_weight_measurement"]], on="device_id")
x["best_eur_per_year"] = x.best_benefit_cents / 100 * 365 / x.horizon_days
x["needs_weight"] = x.best_action.eq("MASS_TARGET_TRIGGER")
# best permissible non-weight action value per case (what fill-only SMART could reach)
nw = do[(do.action != "MASS_TARGET_TRIGGER") & do.permissible].groupby("case_id").benefit_vs_no_action_cents.max().clip(lower=0)
x["best_nonweight_eur_per_year"] = x.case_id.map(nw).fillna(0) / 100 * 365 / x.horizon_days
x["weight_increment_eur_per_year"] = (x.best_eur_per_year - x.best_nonweight_eur_per_year).clip(lower=0)
tab = x.groupby("collection_policy").agg(cases=("case_id", "size"), mean_best_eur_y=("best_eur_per_year", "mean"), median_best_eur_y=("best_eur_per_year", "median"),
                                        mean_nonweight_eur_y=("best_nonweight_eur_per_year", "mean"), mean_weight_increment_eur_y=("weight_increment_eur_per_year", "mean"),
                                        share_best_is_mass_trigger=("needs_weight", "mean")).round(2)
print(tab); tab.to_csv(OUT2 / "20c_decision_value_by_policy.csv")
ba = pd.crosstab(x.collection_policy, x.best_action, normalize="index").round(3); print(ba); ba.to_csv(OUT2 / "20c_best_action_mix_by_policy.csv")
tab2 = x.groupby(["collection_policy", "material_stream"]).agg(cases=("case_id", "size"), mean_best_eur_y=("best_eur_per_year", "mean"), mean_weight_increment_eur_y=("weight_increment_eur_per_year", "mean")).round(1)
tab2.to_csv(OUT2 / "20c_decision_value_policy_stream.csv")
res["decision_overall_mean_best_eur_y"] = float(x.best_eur_per_year.mean()); res["decision_overall_weight_increment_eur_y"] = float(x.weight_increment_eur_per_year.mean())
res["hidden_cost_trap_share"] = float(x.hidden_cost_trap_present.mean())
json.dump(res, open(OUT2 / "20_summary.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
