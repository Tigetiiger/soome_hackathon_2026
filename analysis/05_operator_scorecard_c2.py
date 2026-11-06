"""(6) Operator scorecard (neutral, cause-attributed) and the C2 action value pool, with the weight-dependent share isolated."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)
sc = rd("labels_dev/operator_scorecard.parquet")
w = sc.n_operator_jobs
def wavg(g, col, wcol="n_completed_lifts"):
    m = g[col].notna(); return float(np.average(g.loc[m, col], weights=g.loc[m, wcol].clip(lower=1))) if m.any() else np.nan
cols = ["on_time_rate", "missed_visit_rate", "weighbridge_shared_7d_rate", "median_share_lag_days", "billing_overcharge_pct", "billing_undercharge_pct", "discrepant_line_rate", "weight_bias_pct", "median_order_to_lift_hours"]
card = pd.DataFrame({op: {c: wavg(g, c) for c in cols} | {"jobs": g.n_operator_jobs.sum(), "billed_eur": g.billed_eur.sum()} for op, g in sc.groupby("operator_id")}).T
print("== operator scorecard (truth, dev months, lift-weighted)"); print(card.round(3)); card.round(4).to_csv(OUT / "06_operator_scorecard.csv")

# --- cause-attributed device-vs-ticket disagreement by operator (what a customer can see + why)
pairs = pd.read_parquet(OUT / "01_pairs_eur.parquet")
pairs["gt10"] = pairs.rel.abs() > .10
tab = pairs.groupby("operator_id").apply(lambda p: pd.Series({
    "pairs": len(p), "gt10_share": p.gt10.mean(),
    "of_gt10: tare(operator)": (p[p.gt10].cause_g == "stale/wrong tare (operator side)").mean(),
    "of_gt10: side waste": (p[p.gt10].cause_g == "side waste on same truck").mean(),
    "of_gt10: combined": (p[p.gt10].cause_g == "combined load (50/50 split)").mean(),
    "of_gt10: device fault": (p[p.gt10].cause_g == "device sensor fault/drift/calibration").mean(),
    "of_gt10: noise/small/no label": (p[p.gt10].cause_g.isin(["noise/timing (small loads)", "no label (agree or small diff)"])).mean(),
    "stored_tare_share": (p.tare_method == "STORED").mean(),
    "tare_error_rate_per_ticket": (p.cause_g == "stale/wrong tare (operator side)").mean()}))
print("\n== cause attribution of >10% device-vs-ticket gaps, by operator (neutral view)"); print(tab.round(3)); tab.round(4).to_csv(OUT / "06_gap_causes_by_operator.csv")
# vehicle concentration of tare errors: do a few vehicles explain most tare errors?
wb = rd("operations/weighbridge_tickets.parquet").drop_duplicates("operator_job_ref")
df = lifts()
lab = labels()
tl = lab[(lab.label_family == "WEIGHT_DISCREPANCY") & (lab.explanation_code == "WEIGHBRIDGE_TARE_ERROR")].entity_id
t = df[df.collection_id.isin(tl)].groupby("vehicle_id").size().sort_values(ascending=False)
allv = df[df.ticket_id.notna() & df.eval_at.notna()].groupby("vehicle_id").size()
print("\nvehicles with tare-error lifts:", len(t), "of", len(allv), " | top-10 vehicles hold %.1f%% of tare-error lifts" % (100 * t.head(10).sum() / t.sum()))
vt = pd.DataFrame({"tickets": allv, "tare_err": t}).fillna(0)
vt["rate"] = vt.tare_err / vt.tickets
print(vt[vt.tickets >= 20].rate.describe().round(3).to_dict())
print("vehicles with tare_err rate >50% among tickets>=20:", int((vt[vt.tickets >= 20].rate > .5).sum()), "of", int((vt.tickets >= 20).sum()))

# --- C2 value pool
v = rd("labels_dev/operator_action_values.parquet"); c = rd("benchmark/operator_action_cases.parquet")
dv = rd("reference/devices.parquet")[["device_id", "has_weight_measurement", "material_stream"]]
c = c.merge(dv, on="device_id")
vv = v.merge(c[["case_id", "operator_id", "has_weight_measurement"]], on="case_id")
act = vv.groupby("action").agg(cases=("case_id", "size"), positive=("positive", "sum"), sum_positive_eur=("value_eur", lambda s: s[s > 0].sum()), mean_positive_eur=("value_eur", lambda s: s[s > 0].mean()))
best = vv.drop_duplicates("case_id")
n_dev = len(best)
print("\n== C2 dev cases:", n_dev, " (40%% of customers, as of 2026-07-01); sum of annual contract cost EUR %.0f" % best.annual_contract_cost_eur.sum())
print(act.round(1))
print("best-set value: total EUR %.0f, mean per contract EUR %.0f (=%.1f%% of annual contract cost)" % (best.best_set_value_eur.sum(), best.best_set_value_eur.mean(), 100 * best.best_set_value_eur.sum() / best.annual_contract_cost_eur.sum()))
# decomposition of best set by action (renegotiate/tender exclusive)
piv = vv.pivot(index="case_id", columns="action", values="value_eur").fillna(0).clip(lower=0)
piv["RT"] = piv[["RENEGOTIATE_CONTRACT", "TENDER_OR_SWITCH_OPERATOR"]].max(axis=1)
piv["is_tender"] = piv.TENDER_OR_SWITCH_OPERATOR >= piv.RENEGOTIATE_CONTRACT
dec = pd.Series({"dispute": piv.DISPUTE_INVOICE.sum(), "request_weighbridge": piv.REQUEST_WEIGHBRIDGE_DATA.sum() if "REQUEST_WEIGHBRIDGE_DATA" in piv else 0,
                 "renegotiate (chosen over tender)": piv.loc[~piv.is_tender & (piv.RT > 0), "RT"].sum(), "tender/switch (chosen)": piv.loc[piv.is_tender & (piv.RT > 0), "RT"].sum()})
print("\nbest-set decomposition EUR:", dec.round(0).to_dict(), " total", round(dec.sum(), 0))
wshare = (dec["dispute"] + dec["request_weighbridge"]) / dec.sum()
print("weight/verification-related actions (dispute + request) share of best-set value: %.1f%%" % (100 * wshare))
# per operator
po = best.merge(c[["case_id", "operator_id"]], on="case_id", suffixes=("", "_c")).groupby("operator_id_c").agg(cases=("case_id", "size"), cost=("annual_contract_cost_eur", "sum"), best=("best_set_value_eur", "sum"))
po["pct_of_cost"] = 100 * po.best / po.cost
print("\nbest-set value by current operator:"); print(po.round(1))
# fleet / per-device-year view (dev cases are annualised forward values, one per contract = device)
ndev_all = 437  # active public contracts = C2 cases
scale = ndev_all / n_dev
print("\nper active device-year: EUR %.0f (dev cases mean); extrapolated to 437 active public devices: EUR %.0f (assumes dev cases are representative: 40%% of customers)" % (best.best_set_value_eur.mean(), best.best_set_value_eur.sum() * scale))
# where the dispute value comes from: recoverable overbilling by case, and share that would need independent weight
rec = vv[vv.action == "DISPUTE_INVOICE"]
print("dispute: recoverable overbilling total EUR %.0f over %d cases, cases >0: %d" % (rec.recoverable_overbilling_eur.sum(), len(rec), (rec.recoverable_overbilling_eur > 0).sum()))
rq = vv[vv.action == "REQUEST_WEIGHBRIDGE_DATA"].merge(c[["case_id", "has_weight_measurement"]], on="case_id", suffixes=("", "_c"))
print("request candidates:", len(rq), " by operator:", rq.groupby("operator_id").size().to_dict(), " positive:", int(rq.positive.sum()), " of which with device weight:", int((rq.positive & rq.has_weight_measurement_c).sum()))
json.dump({"best_total_eur": float(best.best_set_value_eur.sum()), "n_cases": int(n_dev), "annual_cost": float(best.annual_contract_cost_eur.sum()), "decomposition": {k: float(x) for k, x in dec.items()}}, open(OUT / "06_c2_summary.json", "w"), indent=1)
act.round(2).to_csv(OUT / "06_c2_by_action.csv")
