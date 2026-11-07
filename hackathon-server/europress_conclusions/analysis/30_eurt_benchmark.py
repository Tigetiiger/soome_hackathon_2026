"""UC3 EUR/t transparency and contract benchmarking. (a) net cost EUR/t per contract (label window) vs peer median (same stream, region if
>=5 peers else stream only); EUR above peer median, annualised. (b) C2 RENEGOTIATE/TENDER value split by how the contract's tonnage is observable
without Europress weight (ticket / invoice tonnage / device only). Synthetic data, hypothetical prices."""
import json
from ec_common import *
dv = device_segments(); res = {}
ref = rd("labels_dev/reference_economics.parquet")
ref = ref[ref.status.isin(LIFT)]
cv = rd("reference/contract_versions.parquet")
pm = cv.sort_values("version_no").groupby("contract_id").pricing_model.last()
g = ref.groupby(["contract_id", "device_id"]).agg(t=("billing_mass_kg", lambda s: s.sum() / 1000), cost=("total_customer_cost_eur", "sum"),
                                                  credit=("material_credit_eur", "sum"), net=("net_material_contribution_eur", "sum"), lifts=("collection_id", "size"),
                                                  dev_only=("observable_mass_source", lambda s: s.isin(["DEVICE_ESTIMATE_ONLY", "NONE"]).mean()),
                                                  ticket=("observable_mass_source", lambda s: (s == "WEIGHBRIDGE_PUBLISHED").mean()),
                                                  inv_t=("observable_mass_source", lambda s: (s == "INVOICE_TONNAGE").mean())).reset_index()
g = g.merge(dv[["device_id", "material_stream", "region_code", "operator_id", "collection_policy", "primary_sector", "dev_years"]], on="device_id")
g["pricing_model"] = g.contract_id.map(pm)
g = g[(g.t > 1) & (g.lifts >= 5)].copy()
g["net_cost_eur_t"] = -g.net / g.t
def peer_med(r):
    pr = g[(g.material_stream == r.material_stream) & (g.region_code == r.region_code) & (g.contract_id != r.contract_id)]
    if len(pr) < 5:
        pr = g[(g.material_stream == r.material_stream) & (g.contract_id != r.contract_id)]; lvl = "stream"
    else:
        lvl = "stream+region"
    return pd.Series({"peer_med_eur_t": pr.net_cost_eur_t.median(), "peer_level": lvl, "peer_n": len(pr)})
g = g.join(g.apply(peer_med, axis=1))
g["gap_pct"] = 100 * (g.net_cost_eur_t / g.peer_med_eur_t - 1)
g["excess_eur_y"] = ((g.net_cost_eur_t - g.peer_med_eur_t).clip(lower=0) * g.t) * YEAR_FACTOR
g["weight_needed"] = np.select([g.ticket >= .5, g.inv_t >= .5], ["ticket shared (weight not needed)", "invoice tonnage (operator-reported)"], "device weight is the only mass")
g.to_csv(OUT2 / "30a_contract_eurt_vs_peer.csv", index=False)
print(g.groupby("material_stream").agg(n=("contract_id", "size"), med_eurt=("net_cost_eur_t", "median"), p10=("net_cost_eur_t", lambda s: s.quantile(.1)), p90=("net_cost_eur_t", lambda s: s.quantile(.9)),
                                       above25=("gap_pct", lambda s: (s >= 25).mean()), excess_eur_y=("excess_eur_y", "sum")).round(1))
seg = g.groupby("weight_needed").agg(n=("contract_id", "size"), excess_eur_y=("excess_eur_y", "sum"), above12=("gap_pct", lambda s: (s >= 12).sum())).round(0); print(seg); seg.to_csv(OUT2 / "30a_excess_by_weight_need.csv")
for s in ["operator_id", "collection_policy", "primary_sector", "pricing_model"]:
    print(g.groupby(s).agg(n=("contract_id", "size"), med_gap=("gap_pct", "median"), excess_eur_y=("excess_eur_y", "sum"), excess_per_contract_y=("excess_eur_y", "mean")).round(1))
res["contracts"] = len(g); res["excess_total_eur_y"] = float(g.excess_eur_y.sum()); res["excess_per_contract_y_mean"] = float(g.excess_eur_y.mean())
res["excess_per_contract_y_p50_of_positive"] = float(g.excess_eur_y[g.excess_eur_y > 0].median())
res["share_contracts_gap_ge_12"] = float((g.gap_pct >= 12).mean()); res["share_contracts_gap_ge_25"] = float((g.gap_pct >= 25).mean())
# (b) C2 action values (dev labels) by tonnage observability
oa = rd("labels_dev/operator_action_values.parquet"); oc = rd("benchmark/operator_action_cases.parquet")[["case_id", "contract_id", "device_id", "operator_id"]]
o = oa.merge(oc, on="case_id").merge(g[["contract_id", "weight_needed", "pricing_model", "material_stream", "collection_policy", "ticket", "dev_only"]], on="contract_id", how="left")
o["pos_value"] = o.value_eur.where(o.positive, 0)
tb = o.pivot_table(index="weight_needed", columns="action", values="pos_value", aggfunc="sum", fill_value=0).round(0); tb["cases"] = o.groupby("weight_needed").case_id.nunique()
print(tb); tb.to_csv(OUT2 / "30b_c2_value_by_weight_need.csv")
tb2 = o.pivot_table(index="pricing_model", columns="action", values="pos_value", aggfunc="sum", fill_value=0).round(0); print(tb2); tb2.to_csv(OUT2 / "30b_c2_value_by_pricing.csv")
cases = o.case_id.nunique(); best = o.drop_duplicates("case_id")
res["c2_cases"] = int(cases); res["c2_best_set_value_total"] = float(best.best_set_value_eur.sum()); res["c2_best_set_value_per_case_mean"] = float(best.best_set_value_eur.mean())
res["c2_annual_contract_cost_mean"] = float(best.annual_contract_cost_eur.mean())
pv = o.groupby("action").pos_value.sum(); res["c2_pos_value_by_action"] = pv.round(0).to_dict()
w = o[o.weight_needed == "device weight is the only mass"].groupby("action").pos_value.sum(); res["c2_pos_value_device_only_mass"] = w.round(0).to_dict()
json.dump(res, open(OUT2 / "30_summary.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
