"""UC5 Sensor drift / calibration fault detection lead time. Detector T (ticket-based): per device, ordered clean pairs (single load, weighed
tare, ticket net > 500 kg, no driver-reported side waste); alarm when the median of the last 3 ratios device/ticket-1 exceeds +-TH.
Detector F (ticket-free): device mass/fill per lift vs device's own trailing baseline (median of lifts 4..11 back); alarm when median of last 3
log-ratios exceeds +-TH. Labels SENSOR_DRIFT (15) + CALIBRATION_ERROR (4) used only for evaluation. Synthetic data."""
import json
from ec_common import *
lab = labels(); df = lifts(); dv = device_segments(); res = {}
ep = lab[lab.label_family.isin(["SENSOR_DRIFT", "CALIBRATION_ERROR"])][["device_id", "label_family", "event_at", "end_at", "parameter"]].reset_index(drop=True)
other = lab[lab.label_family.isin(["SENSOR_FAULT", "SENSOR_DEGRADED", "SENSOR_REPLACEMENT"])][["device_id", "event_at", "end_at"]]
L = df[df.status.isin(LIFT)].sort_values(["device_id", "actual_at"]).copy()
# ticket-based series
T = L[(L.loads_on_vehicle == 1) & (L.tare_method == "WEIGHED") & (L.allocated_net_kg > 500) & ~L.driver_reported_side_waste.fillna(False).astype(bool) & L.device_estimated_collected_kg.notna()].copy()
T["s"] = T.device_estimated_collected_kg / T.allocated_net_kg - 1
T["stat"] = T.groupby("device_id").s.transform(lambda x: x.rolling(3, min_periods=3).median())
# ticket-free series (as-of: baseline uses lifts 4..11 back so a slow drift is not absorbed instantly)
F = L[L.device_mass_kg_before.notna() & (L.device_fill_pct_before >= 30)].copy()
F["k"] = np.log(F.device_mass_kg_before / F.device_fill_pct_before)
F["base"] = F.groupby("device_id").k.transform(lambda x: x.shift(3).rolling(8, min_periods=5).median())
F["s"] = F.k - F.base
F["stat"] = F.groupby("device_id").s.transform(lambda x: x.rolling(3, min_periods=3).median())
w0, w1 = [pd.Timestamp(t, tz="UTC") for t in WINDOW]
def evaluate(S, th, name):
    S = S[(S.actual_at >= w0) & (S.actual_at < w1)]
    al = S[S.stat.abs() > th][["device_id", "actual_at", "stat"]]
    rows = []
    for e in ep.itertuples():
        a = al[(al.device_id == e.device_id) & (al.actual_at >= e.event_at) & (al.actual_at <= e.end_at + pd.Timedelta(days=7))]
        nobs = int(((S.device_id == e.device_id) & (S.actual_at >= e.event_at) & (S.actual_at <= e.end_at)).sum())
        rows.append({"device_id": e.device_id, "family": e.label_family, "start": e.event_at, "end": e.end_at, "episode_days": (e.end_at - e.event_at).days,
                     "obs_in_episode": nobs, "detected": len(a) > 0, "lead_days_after_start": (a.actual_at.min() - e.event_at).days if len(a) else None,
                     "days_before_fix": (e.end_at - a.actual_at.min()).days if len(a) else None})
    r = pd.DataFrame(rows)
    # false alarms: alarms not inside any episode (+7 d) nor inside sensor fault/degraded/replacement periods
    bad = pd.concat([ep[["device_id", "event_at", "end_at"]], other])
    fa = al.copy(); fa["inside"] = False
    for b in bad.itertuples():
        fa.loc[(fa.device_id == b.device_id) & (fa.actual_at >= b.event_at - pd.Timedelta(days=1)) & (fa.actual_at <= b.end_at + pd.Timedelta(days=7)), "inside"] = True
    fa = fa[~fa.inside].sort_values(["device_id", "actual_at"])
    # count distinct false-alarm episodes (gap > 14 d)
    fa["new"] = fa.groupby("device_id").actual_at.diff().dt.days.fillna(999) > 14
    n_fa = int(fa.new.sum()); dy = dv[dv.device_id.isin(S.device_id.unique())].dev_years.sum()
    summ = {"detector": name, "th": th, "episodes": len(r), "episodes_with_obs": int((r.obs_in_episode > 0).sum()), "detected": int(r.detected.sum()),
            "median_lead_days": float(r.lead_days_after_start.median()) if r.detected.any() else None, "median_days_before_fix": float(r.days_before_fix.median()) if r.detected.any() else None,
            "false_alarm_episodes_per_device_year": round(n_fa / dy, 3)}
    return summ, r
out = []; det = {}
for name, S in [("T_ticket", T), ("F_ticketfree", F)]:
    for th in (.04, .06, .08, .10):
        s, r = evaluate(S, th, name); out.append(s); det[(name, th)] = r
o = pd.DataFrame(out); print(o.to_string(index=False)); o.to_csv(OUT2 / "50_drift_detectors.csv", index=False)
det[("T_ticket", .06)].to_csv(OUT2 / "50_drift_episodes_T06.csv", index=False); print(det[("T_ticket", .06)].to_string(index=False))
det[("F_ticketfree", .06)].to_csv(OUT2 / "50_drift_episodes_F06.csv", index=False)
wo = rd("operations/maintenance_work_orders.parquet")
print(wo.work_order_type.value_counts())
res["recalibration_work_orders"] = int((wo.work_order_type == "SENSOR_RECALIBRATION").sum())
res["episode_days_median"] = float((ep.end_at - ep.event_at).dt.days.median())
json.dump(res, open(OUT2 / "50_summary.json", "w"), indent=1, default=str); print(res)
