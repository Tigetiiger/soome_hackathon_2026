"""AI vs transparent rules for device-vs-weighbridge weight-difference anomalies (Task B family WEIGHT_DISCREPANCY).
Time split: train = lifts evaluated before 2026-06-01, validation = 2026-06-01..2026-07-31 (public dev labels).  Seed fixed."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
lab = labels(); df = lifts()
wd = lab[lab.label_family == "WEIGHT_DISCREPANCY"].set_index("entity_id")
D = df[df.status.isin(LIFT) & df.ticket_id.notna() & df.device_estimated_collected_kg.notna() & (df.allocated_net_kg > 0)].copy()
D = D.sort_values("actual_at").reset_index(drop=True)
D["rel"] = (D.device_estimated_collected_kg - D.allocated_net_kg) / D.allocated_net_kg
D["diff"] = D.device_estimated_collected_kg - D.allocated_net_kg
D["side"] = (D.driver_reported_side_waste == True).astype(int)
D["stored"] = (D.tare_method == "STORED").astype(int)
D["multi"] = (D.loads_on_vehicle > 1).astype(int)
D["cause"] = D.collection_id.map(wd.explanation_code)
D["T1"] = D.cause.notna()
D["T2"] = D.cause.isin(["WEIGHBRIDGE_TARE_ERROR", "DEVICE_SENSOR_DRIFT", "DEVICE_SENSOR_DEGRADED", "DEVICE_SENSOR_CALIBRATION_GAIN"])
D["cause_g"] = D.cause.map({"WEIGHBRIDGE_TARE_ERROR": "tare", "DEVICE_SENSOR_DRIFT": "device", "DEVICE_SENSOR_DEGRADED": "device", "DEVICE_SENSOR_CALIBRATION_GAIN": "device",
                            "SIDE_WASTE_ON_SAME_TRUCK": "side_waste", "COMBINED_LOAD_ALLOCATION": "combined", "MEASUREMENT_NOISE_OR_TIMING": "noise"}).fillna("none")
# ---- as-of history features (strictly earlier lifts only)
def prior_median(key, col, win, minp, mask=None):
    s = D[col].where(mask) if mask is not None else D[col]
    return s.groupby(D[key]).transform(lambda x: x.shift(1).rolling(win, min_periods=minp).median())
clean_mask = (D.multi == 0) & (D.side == 0)
D["veh_bias_prior"] = prior_median("vehicle_id", "rel", 12, 3, clean_mask & (D.stored == 1))
D["dev_bias_prior"] = prior_median("device_id", "rel", 8, 3, clean_mask)
D["dev_bias_prior_clipped"] = D.dev_bias_prior
D["veh_abs_dev_prior"] = D.groupby("vehicle_id").rel.transform(lambda x: x.abs().shift(1).rolling(12, min_periods=3).median())
split_date = pd.Timestamp("2026-06-01")
D = D[D.eval_at.notna()].copy()
tr = D[D.eval_at.dt.tz_convert(TZ).dt.tz_localize(None) < split_date]; va = D[(D.eval_at.dt.tz_convert(TZ).dt.tz_localize(None) >= split_date) & (D.eval_at.dt.tz_convert(TZ).dt.tz_localize(None) < pd.Timestamp("2026-08-01"))]
print("train pairs %d (T1 %d, T2 %d) | validation pairs %d (T1 %d, T2 %d)" % (len(tr), tr.T1.sum(), tr.T2.sum(), len(va), va.T1.sum(), va.T2.sum()))

def prf(pred, y):
    tp = int((pred & y).sum()); fp = int((pred & ~y).sum()); fn = int((~pred & y).sum())
    p = tp / max(1, tp + fp); r = tp / max(1, tp + fn); return round(p, 3), round(r, 3), round(2 * p * r / max(1e-9, p + r), 3), tp, fp, fn
res = []
def add(name, pred, kind):
    for tgt in ("T1", "T2"):
        p, r, f, tp, fp, fn = prf(pred, va[tgt])
        res.append({"detector": name, "type": kind, "target": {"T1": "any label (incl. explained)", "T2": "actionable (tare+device)"}[tgt], "precision": p, "recall": r, "f1": f, "tp": tp, "fp": fp, "fn": fn})
# R1: baseline B2 rule
r1 = (va["diff"].abs() > 100) & (va.rel.abs() > .10) & (va.multi == 0) & (va.side == 0)
add("R1 B2 rule: |diff|>100kg & |rel|>10% & single load & no side-waste flag", r1, "transparent rule")
# R2: rule + attribution; flagged iff size test passes; explained causes removed by evidence
size = (va["diff"].abs() > 100) & (va.rel.abs() > .10)
veh_biased = (va.stored == 1) & (va.veh_bias_prior.abs() > .05)
dev_biased = (va.dev_bias_prior.abs() > .05)
cause_r2 = np.select([va.multi == 1, va.side == 1, veh_biased & (np.sign(va.veh_bias_prior) == np.sign(va.rel)), dev_biased & (np.sign(va.dev_bias_prior) == np.sign(va.rel))],
                     ["combined", "side_waste", "tare", "device"], default="unexplained")
r2_actionable = size & np.isin(cause_r2, ["tare", "device", "unexplained"])
add("R2 rule + as-of vehicle/device history attribution (size test, explained causes removed)", r2_actionable, "transparent rule")
# R2c: evidence-first rule. Side-waste flag excludes a lift only when history gives no evidence of a biased tare/device
tare_ev = veh_biased & (np.sign(va.veh_bias_prior) == np.sign(va.rel)); dev_ev = dev_biased & (np.sign(va.dev_bias_prior) == np.sign(va.rel))
r2c = size & (va.multi == 0) & ((va.side == 0) | tare_ev | dev_ev)
add("R2c evidence-first rule: size test & single load & (no side-waste flag OR biased vehicle/device history)", r2c, "transparent rule")
# R2d: two tiers - ACT (history evidence of a biased tare/device) vs REVIEW (size test only, no evidence)
act_tier = size & (va.multi == 0) & (tare_ev | dev_ev)
add("R2d tier ACT only: size test & single load & vehicle/device history evidence", act_tier, "transparent rule")
r2_any = size
add("R2b size test only: |diff|>100 & |rel|>10% (no exclusions)", r2_any, "transparent rule")
# ML1: GBM, basic features only (what B4 sees about weights)
basic = ["rel", "diff", "allocated_net_kg", "device_estimated_collected_kg", "side", "stored", "multi", "container_volume_m3", "device_fill_pct_before"]
def X(d, cols): return d[cols].astype(float)
for name, cols in [("ML1 gradient boosting, basic features", basic), ("ML2 gradient boosting, basic + as-of vehicle/device history", basic + ["veh_bias_prior", "dev_bias_prior", "veh_abs_dev_prior"])]:
    for tgt in ("T1", "T2"):
        m = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, random_state=SEED).fit(X(tr, cols), tr[tgt])
        p = m.predict_proba(X(va, cols))[:, 1] >= 0.5
        pr, rc, f, tp, fp, fn = prf(pd.Series(p, index=va.index), va[tgt])
        res.append({"detector": name, "type": "supervised ML", "target": {"T1": "any label (incl. explained)", "T2": "actionable (tare+device)"}[tgt], "precision": pr, "recall": rc, "f1": f, "tp": tp, "fp": fp, "fn": fn})
# IF: unsupervised isolation forest on size features, contamination = training share of T1
cols_if = ["rel", "diff", "allocated_net_kg", "side", "multi"]
for tgt in ("T1", "T2"):
    cont = float(tr[tgt].mean())
    iso = IsolationForest(n_estimators=300, contamination=cont, random_state=SEED).fit(X(tr, cols_if))
    p = iso.predict(X(va, cols_if)) == -1
    pr, rc, f, tp, fp, fn = prf(pd.Series(p, index=va.index), va[tgt])
    res.append({"detector": "ML3 isolation forest (unsupervised, contamination=train anomaly share)", "type": "unsupervised ML", "target": {"T1": "any label (incl. explained)", "T2": "actionable (tare+device)"}[tgt],
                "precision": pr, "recall": rc, "f1": f, "tp": tp, "fp": fp, "fn": fn})
R = pd.DataFrame(res)
print(R.to_string(index=False)); R.to_csv(OUT / "08_rules_vs_ml.csv", index=False)

# ---- explainability: cause attribution (multi-class) rule vs GBM, restricted to labelled anomalies in validation
lv = va[va.T1].copy(); lv["rule_cause"] = pd.Series(cause_r2, index=va.index)[lv.index]
gm = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, random_state=SEED).fit(X(tr[tr.T1], basic + ["veh_bias_prior", "dev_bias_prior", "veh_abs_dev_prior"]), tr[tr.T1].cause_g)
lv["ml_cause"] = gm.predict(X(lv, basic + ["veh_bias_prior", "dev_bias_prior", "veh_abs_dev_prior"]))
lv["rule_cause2"] = lv.rule_cause.replace({"unexplained": "noise"})
print("\ncause attribution accuracy on labelled validation anomalies (n=%d): rule %.3f | GBM %.3f" % (len(lv), (lv.rule_cause2 == lv.cause_g).mean(), (lv.ml_cause == lv.cause_g).mean()))
print("rule confusion (rows=true, cols=rule):"); print(pd.crosstab(lv.cause_g, lv.rule_cause))
print("GBM confusion (rows=true, cols=ML):"); print(pd.crosstab(lv.cause_g, lv.ml_cause))
# value-weighted: EUR of actionable anomalies caught, using 01_pairs_eur (device-basis delta)
pe = pd.read_parquet(OUT / "01_pairs_eur.parquet")[["collection_id", "delta_eur"]]
vv = va.merge(pe, on="collection_id", how="left")
vv["r1"] = r1.values; vv["r2"] = r2_actionable.values
for nm in ("r1", "r2"):
    tp_eur = vv.loc[vv[nm] & vv.T2, "delta_eur"].abs().sum(); fp_n = int((vv[nm] & ~vv.T2).sum()); tot = vv.loc[vv.T2, "delta_eur"].abs().sum()
    print(f"{nm}: |EUR basis effect| of actionable anomalies caught {tp_eur:,.0f} of {tot:,.0f}; false flags {fp_n}")
# first-flag timeliness: vehicle-level tare error — how many tickets does the as-of vehicle rule need before it attributes?
print("\nshare of validation tare-error lifts with enough vehicle history (>=3 prior stored lifts):", float(va[va.cause_g == "tare"].veh_bias_prior.notna().mean()))
va[["collection_id", "cause_g", "T1", "T2"]].assign(rule_cause=cause_r2, r1=r1.values, r2=r2_actionable.values).to_parquet(OUT / "08_validation_predictions.parquet")

# ---- paired bootstrap on the validation set (actionable target): is the GBM advantage real?
rngb = np.random.default_rng(SEED)
y = va.T2.to_numpy()
m2 = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, random_state=SEED).fit(X(tr, basic + ["veh_bias_prior", "dev_bias_prior", "veh_abs_dev_prior"]), tr.T2)
p_ml = m2.predict_proba(X(va, basic + ["veh_bias_prior", "dev_bias_prior", "veh_abs_dev_prior"]))[:, 1] >= .5
preds = {"R1": r1.to_numpy(), "R2c": r2c.to_numpy(), "ML2": p_ml}
def f1(pr, yy):
    tp = (pr & yy).sum(); fp = (pr & ~yy).sum(); fn = (~pr & yy).sum(); return 2 * tp / max(1, 2 * tp + fp + fn)
boots = {k: [] for k in preds}
for _ in range(1000):
    i = rngb.integers(0, len(y), len(y))
    for k, pr in preds.items():
        boots[k].append(f1(pr[i], y[i]))
for k in preds:
    b = np.array(boots[k]); print(f"bootstrap F1 {k}: {b.mean():.3f}  95% CI [{np.quantile(b, .025):.3f}, {np.quantile(b, .975):.3f}]")
d = np.array(boots["ML2"]) - np.array(boots["R1"]); print("ML2 - R1 F1 diff: mean %.3f, 95%% CI [%.3f, %.3f], P(ML2>R1)=%.2f" % (d.mean(), np.quantile(d, .025), np.quantile(d, .975), (d > 0).mean()))
# label-free reality check: share of anomalies the ML would see in practice if labels (T2) were NOT available -> unsupervised only
print("\nNote: T2 labels come from simulator truth; in production they do not exist, so only R1/R2c/ML3 are deployable on day 1; ML1/ML2 need confirmed cases from human review.")
