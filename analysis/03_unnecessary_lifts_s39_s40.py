"""(4) What does weight add BEYOND fill for unnecessary lifts?  Labels: PREMATURE_UNJUSTIFIED (OVER_SERVICING S01, PRECAUTIONARY_ORDER S39,
FILL_SENSOR_FALSE_HIGH S40).  Compare fill-only detectors with mass-aware detectors (no labels used for calibration)."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)
lab = labels(); df = lifts(); dy = device_years(); dyw = device_years(only_weighted=True)
tel = pd.read_parquet(OUT / "telemetry_dedup.parquet")
dev = rd("reference/devices.parquet").set_index("device_id")

# ---- per-device calibration of 'kg per fill-%' on the first 120 days of the window, VALID readings with fill in 50..95
t0 = tel.measured_at.min()
cal = tel[(tel.measured_at < t0 + pd.Timedelta(days=120)) & (tel.quality_flag == "VALID") & tel.fill_pct.between(50, 95) & (tel.mass_kg > 0)]
kgpp = (cal.mass_kg / cal.fill_pct).groupby(cal.device_id).median()
n_cal = cal.groupby("device_id").size()
kgpp = kgpp[n_cal.reindex(kgpp.index) >= 20]
print("devices calibrated:", len(kgpp), "of", dev.has_weight_measurement.sum(), "with weight")
eval_start = t0 + pd.Timedelta(days=120)

L = df[df.status.isin(LIFT)].copy()
pl = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & lab.is_actionable][["entity_id", "explanation_code", "value_at_stake_eur", "severity"]].rename(columns={"entity_id": "collection_id"})
L = L.merge(pl, on="collection_id", how="left")
L["cat"] = L.explanation_code.fillna("OTHER")
L["kgpp"] = L.device_id.map(kgpp)
L["mass_fill"] = L.device_mass_kg_before / L.kgpp                    # mass-implied fill % (kg / kg-per-fill-pp)
L["fill"] = L.device_fill_pct_before
L["gap"] = L.fill - L.mass_fill
L = L[L.eval_at.notna() & (L.actual_at >= eval_start)]              # label window, after calibration period
has = L.device_mass_kg_before.notna() & L.fill.notna() & L.kgpp.notna()
print("lifts in eval window:", len(L), " with fill+mass+calibration:", int(has.sum()))
print(L.groupby("cat").agg(n=("collection_id", "size"), eur=("value_at_stake_eur", "sum"), fill_med=("fill", "median"), massfill_med=("mass_fill", "median"), gap_med=("gap", "median"),
                           has=("mass_fill", lambda s: s.notna().mean())).round(2))
tot_eur = L.groupby("cat").value_at_stake_eur.sum()
H = L[has].copy()
H["y_any"] = H.cat.isin(["OVER_SERVICING", "PRECAUTIONARY_ORDER", "FILL_SENSOR_FALSE_HIGH"])

def prf(mask, y):
    tp = int((mask & y).sum()); fp = int((mask & ~y).sum()); fn = int((~mask & y).sum())
    p = tp / max(1, tp + fp); r = tp / max(1, tp + fn)
    return tp, fp, fn, p, r, 2 * p * r / max(1e-9, p + r)

rows = []
def evalrule(name, mask, targets):
    for tname, y in targets.items():
        tp, fp, fn, p, r, f = prf(mask, y)
        rows.append({"rule": name, "target": tname, "tp": tp, "fp": fp, "fn": fn, "precision": round(p, 3), "recall": round(r, 3), "f1": round(f, 3)})
targets = {"S40 false-high": H.cat == "FILL_SENSOR_FALSE_HIGH", "S39 precautionary": H.cat == "PRECAUTIONARY_ORDER", "S01 over-servicing": H.cat == "OVER_SERVICING", "ANY unjustified": H.y_any}
# justified-early lifts (explained) must not be flagged
for thr in (30, 40, 50):
    evalrule(f"FILL-ONLY: fill_before<{thr}%", H.fill < thr, targets)
for thr in (30, 40, 50):
    evalrule(f"MASS-ONLY: mass-implied fill<{thr}%", H.mass_fill < thr, targets)
for thr in (40, 50, 60):
    evalrule(f"MASS-vs-FILL: mass-fill<{thr}% (any fill)", H.mass_fill < thr, targets)
evalrule("MASS-vs-FILL gap: fill>=80 & mass-fill<50 (S40 signature)", (H.fill >= 80) & (H.mass_fill < 50), targets)
evalrule("COMBINED: fill<40 OR (fill>=80 & mass-fill<50)", (H.fill < 40) | ((H.fill >= 80) & (H.mass_fill < 50)), targets)
evalrule("COMBINED2: fill<40 OR mass-fill<40", (H.fill < 40) | (H.mass_fill < 40), targets)
res = pd.DataFrame(rows)
print("\n== rule performance on lift level (eval window)"); print(res.to_string(index=False))
res.to_csv(OUT / "04_lift_rules.csv", index=False)

# what fill-only sees on S40 lifts
s40 = H[H.cat == "FILL_SENSOR_FALSE_HIGH"]
print("\nS40 lifts: fill_before median %.1f (p10 %.1f), mass-implied fill median %.1f (p90 %.1f)" % (s40.fill.median(), s40.fill.quantile(.1), s40.mass_fill.median(), s40.mass_fill.quantile(.9)))
print("normal 'OTHER' lifts: fill median %.1f, mass-fill median %.1f" % (H[H.cat == "OTHER"].fill.median(), H[H.cat == "OTHER"].mass_fill.median()))

# ---- value of what mass uniquely catches: S40 lifts that FILL-ONLY (fill<40) misses but mass-vs-fill gap catches
fill_flag = H.fill < 40
gap_flag = (H.fill >= 80) & (H.mass_fill < 50)
mass_flag = H.mass_fill < 40
for cat in ["FILL_SENSOR_FALSE_HIGH", "PRECAUTIONARY_ORDER", "OVER_SERVICING"]:
    s = H[H.cat == cat]
    fl = fill_flag[s.index]; ml = (mass_flag | gap_flag)[s.index]
    print(f"{cat}: n={len(s)} EUR={s.value_at_stake_eur.sum():,.0f} | caught by fill<40: {fl.mean():.2f} (EUR {s.value_at_stake_eur[fl].sum():,.0f}) | caught by mass-aware: {ml.mean():.2f} (EUR {s.value_at_stake_eur[ml].sum():,.0f}) | mass-only-extra EUR {s.value_at_stake_eur[ml & ~fl].sum():,.0f}")
# false positives (explained early lifts flagged?)
expl = lab[(lab.label_family == "EARLY_JUSTIFIED")].entity_id
H["justified"] = H.collection_id.isin(expl)
print("explained-justified lifts flagged: fill<40: %.3f | mass-aware: %.3f (n=%d)" % (fill_flag[H.justified].mean(), (mass_flag | gap_flag)[H.justified].mean(), H.justified.sum()))

# ---- S40 episode-level early warning from telemetry: hours of (fill>=80 & mass-fill<50) inside labelled episodes vs elsewhere
ep = lab[lab.label_family == "FILL_SENSOR_FALSE_HIGH"][["device_id", "event_at", "end_at", "parameter"]].copy()
ep = ep[ep.device_id.isin(kgpp.index) & (ep.event_at >= eval_start)]
print("\nS40 episodes in eval window:", len(ep), " duration h median:", ((ep.end_at - ep.event_at).dt.total_seconds() / 3600).median())
tv = tel[tel.quality_flag.isin(["VALID", "LOW_CONFIDENCE"]) & tel.device_id.isin(kgpp.index) & (tel.measured_at >= eval_start) & (tel.measured_at < pd.Timestamp("2026-08-01", tz="UTC"))].copy()   # labels only exist before Aug-2026
tv["mass_fill"] = tv.mass_kg / tv.device_id.map(kgpp)
tv["sig"] = (tv.fill_pct >= 80) & (tv.mass_fill < 50)
# mark episode hours
tv["in_ep"] = False; tv["in_ep_pad"] = False
for d, g in ep.groupby("device_id"):
    m = tv.device_id == d
    for r in g.itertuples():
        tv.loc[m & (tv.measured_at >= r.event_at) & (tv.measured_at < r.end_at), "in_ep"] = True
        tv.loc[m & (tv.measured_at >= r.event_at) & (tv.measured_at < r.end_at + pd.Timedelta(hours=6)), "in_ep_pad"] = True
print("hour-level: P(sig | in S40 episode)=%.3f  P(sig | not in episode)=%.4f ; hours in episode %d" % (tv[tv.in_ep].sig.mean(), tv[~tv.in_ep].sig.mean(), tv.in_ep.sum()))
# persistence rule: >=3 signature hours in 6 -> alert; time to alert since episode start; false alert per device-year
tv = tv.sort_values(["device_id", "measured_at"])
tv["sig3"] = tv.groupby("device_id").sig.transform(lambda s: s.rolling(6, min_periods=3).sum() >= 3)
alert_h = []
for r in ep.itertuples():
    g = tv[(tv.device_id == r.device_id) & (tv.measured_at >= r.event_at) & (tv.measured_at < r.end_at) & tv.sig3]
    alert_h.append((g.measured_at.min() - r.event_at).total_seconds() / 3600 if len(g) else np.nan)
alert_h = pd.Series(alert_h)
print("episodes alerted by persistence rule: %.3f; median hours to alert %.1f" % (alert_h.notna().mean(), alert_h.median()))
fa = tv[~tv.in_ep_pad & tv.sig3]
ydays = tv.groupby("device_id").measured_at.agg(lambda s: (s.max() - s.min()).days).sum()
# count distinct false alert episodes (gap > 24h)
fa_ep = 0
for d, g in fa.groupby("device_id"):
    fa_ep += int((g.measured_at.diff().dt.total_seconds().fillna(1e9) > 24 * 3600).sum())
print("false alert episodes: %d over %.1f device-years -> %.3f per device-year; devices involved: %d of %d" % (fa_ep, ydays / 365, fa_ep / (ydays / 365), fa.device_id.nunique(), tv.device_id.nunique()))
json.dump({"s40_episodes_eval": int(len(ep)), "s40_alerted": float(alert_h.notna().mean()), "s40_median_h_to_alert": float(alert_h.median()),
           "false_alerts_per_device_year": fa_ep / (ydays / 365)}, open(OUT / "04_s40_summary.json", "w"))

# ---- fleet EUR pool (whole label window, labels only) and per weighted device-year
pool = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & lab.is_actionable].groupby("explanation_code").agg(n=("entity_id", "size"), eur=("value_at_stake_eur", "sum"))
pool["eur_per_device_year(weighted devices)"] = pool.eur / dyw
pool["eur_per_device_year(all devices)"] = pool.eur / dy
print("\n== label-window pool (304 d), device-years all=%.1f weighted=%.1f" % (dy, dyw)); print(pool.round(1))
pool.round(2).to_csv(OUT / "04_premature_pool.csv")
# on-call vs fixed split of each category (who has the problem)
pp = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & lab.is_actionable].merge(dev[["collection_policy", "has_weight_measurement"]], left_on="device_id", right_index=True)
print(pp.groupby(["explanation_code", "collection_policy"]).size().unstack(fill_value=0))
print(pp.groupby(["explanation_code", "has_weight_measurement"]).size().unstack(fill_value=0))

# ======================================================================== additions: S39 needs weight?  S40 alert sweep and lead time
print("\n== S39: trigger-type + fill rule (no weight)")
H["cr"] = H.trigger_type == "CUSTOMER_REQUEST"
rows2 = []
for thr in (40, 50, 60):
    m_ = H.cr & (H.fill < thr)
    tp, fp, fn, p, r, f = prf(m_, H.cat == "PRECAUTIONARY_ORDER"); rows2.append(("CUSTOMER_REQUEST & fill<%d" % thr, "S39", tp, fp, fn, round(p, 3), round(r, 3), round(f, 3)))
    m2 = H.cr & (H.mass_fill < thr)
    tp, fp, fn, p, r, f = prf(m2, H.cat == "PRECAUTIONARY_ORDER"); rows2.append(("CUSTOMER_REQUEST & mass-fill<%d" % thr, "S39", tp, fp, fn, round(p, 3), round(r, 3), round(f, 3)))
print(pd.DataFrame(rows2, columns=["rule", "target", "tp", "fp", "fn", "precision", "recall", "f1"]).to_string(index=False))
print("trigger types among S39:", H[H.cat == "PRECAUTIONARY_ORDER"].trigger_type.value_counts().to_dict())

print("\n== S40 hourly alert sweep (persistence k of 6 h, mass-implied fill threshold)")
tv = tv.sort_values(["device_id", "measured_at"])
rows3 = []
ep_by_dev = {d: g for d, g in ep.groupby("device_id")}
for mf_thr in (40, 50):
    for k in (3, 4, 5):
        sig = (tv.fill_pct >= 80) & (tv.mass_fill < mf_thr)
        s3 = sig.groupby(tv.device_id).transform(lambda s: s.rolling(6, min_periods=k).sum() >= k)
        alerted, hrs = [], []
        for r in ep.itertuples():
            m_ = (tv.device_id == r.device_id) & (tv.measured_at >= r.event_at) & (tv.measured_at < r.end_at) & s3
            if m_.any():
                alerted.append(True); hrs.append((tv.measured_at[m_].min() - r.event_at).total_seconds() / 3600)
            else:
                alerted.append(False)
        fa_h = tv[~tv.in_ep_pad & s3]
        n_fa = sum(int((g.measured_at.diff().dt.total_seconds().fillna(1e9) > 24 * 3600).sum()) for _, g in fa_h.groupby("device_id"))
        rows3.append({"mass_fill_thr": mf_thr, "k_of_6": k, "episode_recall": round(float(np.mean(alerted)), 3), "median_h_to_alert": round(float(np.median(hrs)), 1),
                      "false_alert_episodes_per_device_year": round(n_fa / (ydays / 365), 3)})
sw = pd.DataFrame(rows3); print(sw.to_string(index=False)); sw.to_csv(OUT / "04_s40_alert_sweep.csv", index=False)

# lead time of the alert vs the order that caused the unnecessary lift (S40 lifts whose order was placed inside/after an episode)
lab40 = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & (lab.explanation_code == "FILL_SENSOR_FALSE_HIGH")][["entity_id"]].rename(columns={"entity_id": "collection_id"})
s40l = L.merge(lab40, on="collection_id")[["collection_id", "device_id", "order_placed_at", "actual_at"]].dropna(subset=["order_placed_at"])
sig = (tv.fill_pct >= 80) & (tv.mass_fill < 50)
tv["s3"] = sig.groupby(tv.device_id).transform(lambda s: s.rolling(6, min_periods=3).sum() >= 3)
lead = []
for r in s40l.itertuples():
    g = tv[(tv.device_id == r.device_id) & tv.s3 & (tv.measured_at <= r.order_placed_at) & (tv.measured_at >= r.order_placed_at - pd.Timedelta(hours=96))]
    lead.append((r.order_placed_at - g.measured_at.min()).total_seconds() / 3600 if len(g) else np.nan)
lead = pd.Series(lead)
print("S40 lifts with an order time: %d; alert (3-of-6 rule) fires BEFORE the order in %.1f%% of them; median lead %.1f h" % (len(lead), 100 * lead.notna().mean(), lead.median()))
json.dump({"s40_lifts_with_order": int(len(lead)), "alert_before_order_share": float(lead.notna().mean()), "median_lead_h": float(lead.median())}, open(OUT / "04_s40_lead.json", "w"))

# ======================================================================== order-time guard: block/confirm an order when fill says full but mass says not
ords = df[df.status.isin(LIFT) & df.order_placed_at.notna() & df.eval_at.notna() & df.has_weight_measurement].merge(pl, on="collection_id", how="left")
ords = ords[ords.order_placed_at >= eval_start].copy()
ords["cat"] = ords.explanation_code.fillna("OTHER")
tvs = tel[tel.quality_flag.isin(["VALID", "LOW_CONFIDENCE"]) & tel.device_id.isin(kgpp.index)][["device_id", "measured_at", "fill_pct", "mass_kg"]].sort_values("measured_at")
tvs["mass_fill"] = tvs.mass_kg / tvs.device_id.map(kgpp)
ords["order_placed_at"] = ords.order_placed_at.astype("datetime64[us, UTC]"); tvs["measured_at"] = tvs.measured_at.astype("datetime64[us, UTC]")
o2 = pd.merge_asof(ords.sort_values("order_placed_at"), tvs.rename(columns={"fill_pct": "fill_at_order", "mass_fill": "mf_at_order"}), left_on="order_placed_at", right_on="measured_at",
                   by="device_id", direction="backward", tolerance=pd.Timedelta(hours=3))
o2 = o2[o2.mf_at_order.notna()]
guard = (o2.fill_at_order >= 80) & (o2.mf_at_order < 50)
print("\n== order-time guard (fill>=80 & mass-implied fill<50 at the hour before the order), orders with telemetry: %d" % len(o2))
for c in ["FILL_SENSOR_FALSE_HIGH", "PRECAUTIONARY_ORDER", "OVER_SERVICING", "OTHER"]:
    m_ = o2.cat == c
    print(f"  {c}: n={m_.sum()}, guard fires on {guard[m_].mean():.3f}" + (f", EUR at stake caught {o2.value_at_stake_eur[m_ & guard].sum():,.0f} of {o2.value_at_stake_eur[m_].sum():,.0f}" if c != "OTHER" else ""))
ont = o2[o2.trigger_type.isin(["ON_CALL_ORDER"])]
g2 = (ont.fill_at_order >= 80) & (ont.mf_at_order < 50)
print("  on-call fill-triggered orders: n=%d, guard fires %.3f; of firing orders %.1f%% are S40 (precision)" % (len(ont), g2.mean(), 100 * (ont.cat[g2] == "FILL_SENSOR_FALSE_HIGH").mean()))
tpg = (o2.cat == "FILL_SENSOR_FALSE_HIGH") & guard
print("  S40 orders caught at order time: %.1f%% (EUR %.0f of %.0f)" % (100 * tpg.sum() / (o2.cat == "FILL_SENSOR_FALSE_HIGH").sum(), o2.value_at_stake_eur[tpg].sum(), o2.value_at_stake_eur[o2.cat == "FILL_SENSOR_FALSE_HIGH"].sum()))
json.dump({"order_guard_s40_recall": float(tpg.sum() / (o2.cat == "FILL_SENSOR_FALSE_HIGH").sum()), "order_guard_precision_on_call": float((ont.cat[g2] == "FILL_SENSOR_FALSE_HIGH").mean()),
           "order_guard_eur_caught": float(o2.value_at_stake_eur[tpg].sum()), "s40_orders_eur": float(o2.value_at_stake_eur[o2.cat == "FILL_SENSOR_FALSE_HIGH"].sum())}, open(OUT / "04_order_guard.json", "w"))
H[["collection_id", "device_id", "cat", "fill", "mass_fill", "value_at_stake_eur", "trigger_type", "device_mass_kg_before"]].to_parquet(OUT / "04_lifts_H.parquet")
o2[["collection_id", "cat", "fill_at_order", "mf_at_order", "value_at_stake_eur", "trigger_type"]].to_parquet(OUT / "04_orders_o2.parquet")
