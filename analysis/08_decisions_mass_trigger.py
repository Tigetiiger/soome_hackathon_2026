"""Task C (context): what does a MASS_TARGET_TRIGGER option add beyond the fill-based actions?  Simulated counterfactuals (labels_dev/decision_outcomes) -- not causal evidence."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
dc = rd("benchmark/decision_cases.parquet"); do = rd("labels_dev/decision_outcomes.parquet"); dt = rd("labels_dev/decision_truth.parquet")
dv = rd("reference/devices.parquet")[["device_id", "has_weight_measurement", "material_stream", "collection_policy"]]
dc = dc.merge(dv, on="device_id")
cases_m = dc[dc.candidate_actions.str.contains("MASS_TARGET_TRIGGER")].case_id
o = do[do.case_id.isin(cases_m)]
perm = o[o.permissible]
best_all = perm.groupby("case_id").benefit_vs_no_action_cents.max().clip(lower=0)
best_nomass = perm[perm.action != "MASS_TARGET_TRIGGER"].groupby("case_id").benefit_vs_no_action_cents.max().reindex(best_all.index).fillna(0).clip(lower=0)
inc = (best_all - best_nomass) / 100
n = len(best_all)
print("cases with a MASS_TARGET_TRIGGER option (devices with weight): %d of %d" % (n, len(dc)))
print("mean best-permissible benefit per 56-day case: EUR %.1f | without mass option: EUR %.1f | increment from mass option: EUR %.1f (%.0f%% of the best)" %
      (best_all.mean() / 100, best_nomass.mean() / 100, inc.mean(), 100 * inc.mean() / (best_all.mean() / 100)))
print("share of cases where the mass option adds > EUR 25: %.3f ; > EUR 100: %.3f" % ((inc > 25).mean(), (inc > 100).mean()))
t = dt[dt.case_id.isin(cases_m)].copy()
t["best_is_mass"] = t.best_action == "MASS_TARGET_TRIGGER"
t["acc_nomass"] = t.acceptable_actions.fillna("").apply(lambda s: [a for a in s.split(",") if a and a != "MASS_TARGET_TRIGGER"])
t["mass_needed"] = t.best_is_mass & t.acc_nomass.apply(lambda l: len([a for a in l if a != "NO_ACTION"]) == 0) & ~t.no_action_acceptable
print("cases where MASS_TARGET_TRIGGER is the best action: %.3f ; and no fill-based action and not NO_ACTION is within tolerance ('mass needed'): %.3f" % (t.best_is_mass.mean(), t.mass_needed.mean()))
mt = o[o.action == "MASS_TARGET_TRIGGER"]
print("MASS_TARGET_TRIGGER: permissible %.3f ; mean benefit (permissible) EUR %.1f ; hidden-cost traps %.3f ; mean benefit if best EUR %.1f" %
      (mt.permissible.mean(), mt[mt.permissible].benefit_vs_no_action_cents.mean() / 100, mt.hidden_cost_trap.mean(), mt[mt.case_id.isin(t[t.best_is_mass].case_id)].benefit_vs_no_action_cents.mean() / 100))
x = t.merge(dc[["case_id", "collection_policy", "material_stream"]], on="case_id")
print("\nshare mass-best by policy:"); print(x.groupby("collection_policy").best_is_mass.mean().round(3).to_dict())
print("share mass-best by stream:"); print(x.groupby("material_stream").best_is_mass.mean().round(3).to_dict())
si = inc.groupby(inc.index.map(dc.set_index("case_id").material_stream)).mean().round(1)
print("mean increment EUR/case by stream:", si.to_dict())
# annualisation (indicative): one 56-day horizon benefit -> x 365/56 per weighted device-year if policy persists; cases are 28 days apart, so do not sum cases
ann = inc.mean() * 365 / 56
print("indicative per weighted device-year (policy persists, benefits per 56-day horizon scaled to 365 d): EUR %.0f" % ann)
# decision-case diagnostics that need weight: VERIFY_WEIGHT_SENSOR
sens = dt[dt.case_id.isin(cases_m)].truth_sensor_issue_active.notna()
print("cases with an active hidden weight-sensor issue at decision time: %.3f (n=%d)" % (sens.mean(), sens.sum()))
json.dump({"cases": int(n), "inc_eur_per_case": float(inc.mean()), "best_all_eur": float(best_all.mean() / 100), "mass_best_share": float(t.best_is_mass.mean()),
           "mass_needed_share": float(t.mass_needed.mean()), "annualised_eur": float(ann)}, open(OUT / "09_mass_trigger.json", "w"), indent=1)
