"""(5) Implied density (mass / (volume x fill)) per stream: outliers, moisture (weather-weight), contamination / wrong material.
Device baselines use only telemetry-side data (no labels)."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
from sklearn.metrics import roc_auc_score
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)
lab = labels(); df = lifts(); dy = device_years()
sites = rd("reference/sites.parquet")[["site_id", "outdoor_material_staging", "region_code"]]
L = df[df.status.isin(LIFT)].merge(sites, on="site_id", how="left")
L["vol"] = L.container_volume_m3
L["dens"] = L.device_mass_kg_before / (L.vol * L.device_fill_pct_before / 100)
ok = L.dens.notna() & (L.device_fill_pct_before >= 50) & (L.device_mass_kg_before > 100) & L.has_weight_measurement
L = L[ok].copy()
typ = {"cardboard": 190, "paper": 330, "plastic_film": 140, "mixed_plastic": 115, "mixed_waste": 380, "biowaste": 620}
L["typ"] = L.material_stream.map(typ)
print("lifts with usable fill+mass:", len(L))
print(L.groupby("material_stream").dens.describe()[["count", "mean", "25%", "50%", "75%"]].round(0).assign(typical_assumption=pd.Series(typ)))
# device-level baseline (median over the first 120 days, else all) -> z score
L = L.sort_values(["device_id", "actual_at"])
L["ldens"] = np.log(L.dens)
base = L.groupby("device_id").ldens.transform("median")
mad = L.groupby("device_id").ldens.transform(lambda s: 1.4826 * (s - s.median()).abs().median())
L["z"] = (L.ldens - base) / mad.clip(lower=0.03)
L["rel_to_device_med_pct"] = 100 * (np.exp(L.ldens - base) - 1)
print("between-device spread of median density (CV): ", (L.groupby("device_id").dens.median().groupby(L.drop_duplicates('device_id').set_index('device_id').material_stream).agg(lambda s: s.std() / s.mean())).round(3).to_dict())
print("within-device density MAD (log, %):", round(100 * float(mad.median()), 1))

# ---------------------------------------------------------------- moisture
mo = lab[lab.label_family == "MOISTURE_HEAVY_LOAD"][["entity_id", "true_moisture_extra_pct"]].rename(columns={"entity_id": "collection_id"})
L = L.merge(mo, on="collection_id", how="left")
L["moist"] = L.true_moisture_extra_pct.notna()
elig = L[L.eval_at.notna() & L.material_stream.isin(["cardboard", "paper"])]
print("\n== MOISTURE (S28): eligible lifts (cardboard/paper, labelled window) %d, labelled wet %d" % (len(elig), elig.moist.sum()))
for name, sub in [("all cardboard/paper", elig), ("outdoor-staged only", elig[elig.outdoor_material_staging == True])]:
    if sub.moist.sum() > 5:
        print(f"  {name}: n={len(sub)} wet={int(sub.moist.sum())} AUC(z)={roc_auc_score(sub.moist, sub.z):.3f}  AUC(rel density)={roc_auc_score(sub.moist, sub.rel_to_device_med_pct):.3f}")
out = elig[elig.outdoor_material_staging == True]
rows = []
for thr in (1.5, 2, 2.5, 3, 4):
    f = out.z > thr
    tp = int((f & out.moist).sum()); fp = int((f & ~out.moist).sum()); fn = int((~f & out.moist).sum())
    rows.append({"z_threshold": thr, "flagged": int(f.sum()), "tp": tp, "fp": fp, "fn": fn, "precision": round(tp / max(1, tp + fp), 3), "recall": round(tp / max(1, tp + fn), 3)})
print(pd.DataFrame(rows).to_string(index=False)); pd.DataFrame(rows).to_csv(OUT / "05_moisture_thresholds.csv", index=False)
w = out[out.moist]
print("labelled wet loads: extra water mass %.1f%% median (device-implied density excess median %.1f%%)" % (w.true_moisture_extra_pct.median(), w.rel_to_device_med_pct.median()))
print("normal outdoor loads: density excess median %.1f%%, p95 %.1f%%" % (out[~out.moist].rel_to_device_med_pct.median(), out[~out.moist].rel_to_device_med_pct.quantile(.95)))
# EUR value of water mass: extra kg x (haul+processing) per t on paper/cardboard, + effect on credit (cardboard)
cv = rd("reference/contract_versions.parquet").set_index("contract_version_id")
w2 = w.merge(df[["collection_id", "contract_version_id", "allocated_net_kg", "billing_mass_kg"]].rename(columns={"contract_version_id": "cvid"}), on="collection_id", how="left", suffixes=("", "_y"))
w2["extra_kg"] = w2.billing_mass_kg * (w2.true_moisture_extra_pct / 100) / (1 + w2.true_moisture_extra_pct / 100)
w2["rate_eur_t"] = (w2.cvid.map(cv.haul_fee_cents_per_t) + w2.cvid.map(cv.processing_fee_cents_per_t)) / 100
w2["extra_charge_eur"] = w2.extra_kg / 1000 * w2.rate_eur_t
print("wet loads: extra water kg total %.0f, extra per-tonne fees (haul+processing) EUR %.0f on %d loads; mean EUR %.2f" % (w2.extra_kg.sum(), w2.extra_charge_eur.sum(), len(w2), w2.extra_charge_eur.mean()))
# grade of wet loads
g = elig.merge(rd("operations/quality_assessments.parquet")[["ticket_id", "remark_code"]].rename(columns={"remark_code": "rm"}), on="ticket_id", how="left")
print("wet loads with operator remark WET_MATERIAL: %d of %d with a grade" % ((g[g.moist].rm == "WET_MATERIAL").sum(), g[g.moist].grade.notna().sum()))
# fleet-as-rain-gauge: do wet labels cluster on region-days with high median density excess among outdoor cardboard?
el = L[(L.material_stream.isin(["cardboard", "paper"])) & (L.outdoor_material_staging == True)].copy()
el["day"] = el.actual_at.dt.tz_convert(TZ).dt.date
rg = el.groupby(["region_code", "day"]).agg(n=("z", "size"), med_z=("z", "median"), wet=("moist", "sum"))
rgs = rg[rg.n >= 2]
print("region-days (>=2 outdoor cardboard/paper lifts): %d; with a wet label: %d; AUC(median z -> any wet) = %.3f" % (len(rgs), (rgs.wet > 0).sum(), roc_auc_score(rgs.wet > 0, rgs.med_z)))
# ---------------------------------------------------------------- contamination / grade
q = L[L.grade.notna() & L.material_stream.isin(["cardboard", "plastic_film", "mixed_plastic"])].copy()
print("\n== CONTAMINATION (S07/S38): density vs operator grade (credit-eligible, graded lifts n=%d)" % len(q))
print(q.groupby("grade").agg(n=("z", "size"), z_med=("z", "median"), rel_med=("rel_to_device_med_pct", "median"), contam_med=("contamination_pct_est", "median")).round(2))
for target in ("C", "R"):
    y = q.grade == target
    print(f"  AUC density z -> grade {target}: {roc_auc_score(y, q.z):.3f}; -> grade in (B,C,R): {roc_auc_score(q.grade.isin(['B','C','R']), q.z):.3f}")
ci = lab[lab.label_family == "CONTAMINATION_INCIDENT"][["device_id", "event_at", "end_at", "parameter"]]
q2 = L[L.eval_at.notna() & L.material_stream.isin(["cardboard", "plastic_film", "mixed_plastic"])].copy()
q2["inc"] = False
for r in ci.itertuples():
    q2.loc[(q2.device_id == r.device_id) & (q2.actual_at >= r.event_at) & (q2.actual_at <= r.end_at + pd.Timedelta(days=3)), "inc"] = True
print("  lifts inside/after a CONTAMINATION_INCIDENT episode: %d of %d; AUC(z)=%.3f; median density excess in-incident %.1f%% vs other %.1f%%" %
      (q2.inc.sum(), len(q2), roc_auc_score(q2.inc, q2.z), q2[q2.inc].rel_to_device_med_pct.median(), q2[~q2.inc].rel_to_device_med_pct.median()))
# EUR at stake from grades (operator-assessed) -> not detectable from the device
cv_loss = lab[lab.label_family.isin(["CONTAMINATION_VALUE_LOSS", "REJECTED_LOAD"])].groupby(["label_family", "explanation_code"]).value_at_stake_eur.agg(["count", "sum"])
print(cv_loss.round(0))
# ---------------------------------------------------------------- wrong material / mis-sorted recyclables in mixed waste (S30): unlabelled-in-dev, density outliers
mw = L[L.material_stream == "mixed_waste"]
dmed = mw.groupby("device_id").dens.median()
site_streams = rd("reference/devices.parquet").groupby("site_id").material_stream.agg(lambda s: set(s))
dv = rd("reference/devices.parquet").set_index("device_id")
multi = pd.DataFrame({"dens": dmed, "has_recyclable_stream": [bool(site_streams[dv.site_id[d]] & {"cardboard", "plastic_film", "mixed_plastic"}) for d in dmed.index]})
print("\n== mixed waste devices: median implied density / assumed 380 kg/m3 by whether site also has a recyclable stream")
print(multi.groupby("has_recyclable_stream").dens.describe()[["count", "mean", "25%", "50%", "75%"]].round(0))
# outlier devices: log-density z within stream across devices
dens_dev = L.groupby("device_id").agg(stream=("material_stream", "first"), dens=("dens", "median"), n=("dens", "size"))
dens_dev["dz"] = dens_dev.groupby("stream").dens.transform(lambda s: (np.log(s) - np.log(s).median()) / (1.4826 * (np.log(s) - np.log(s).median()).abs().median()))
print("devices with |across-device z|>3 :", int((dens_dev.dz.abs() > 3).sum()), "of", len(dens_dev))
print("lift-level |z|>3 (device-relative): share %.3f; z>3 share %.3f, z<-3 share %.3f" % ((L.z.abs() > 3).mean(), (L.z > 3).mean(), (L.z < -3).mean()))
L[["collection_id", "device_id", "material_stream", "dens", "z", "rel_to_device_med_pct", "moist", "grade"]].to_parquet(OUT / "05_density_lifts.parquet")

# ---------------------------------------------------------------- alternative moisture signal: device-collected mass per compaction cycle (no fill estimate needed)
tel = pd.read_parquet(OUT / "telemetry_dedup.parquet", columns=["device_id", "measured_at", "compaction_cycles"])
tel["cum"] = tel.groupby("device_id").compaction_cycles.cumsum()
tel["measured_at"] = tel.measured_at.astype("datetime64[us, UTC]")
Lc = df[df.status.isin(LIFT) & df.device_estimated_collected_kg.notna() & df.has_weight_measurement & df.actual_at.notna()].copy()
Lc["actual_at"] = Lc.actual_at.astype("datetime64[us, UTC]")
Lc = Lc.sort_values("actual_at")
m_ = pd.merge_asof(Lc, tel.sort_values("measured_at")[["device_id", "measured_at", "cum"]], left_on="actual_at", right_on="measured_at", by="device_id", direction="backward", tolerance=pd.Timedelta(hours=2))
m_ = m_.sort_values(["device_id", "actual_at"])
m_["cyc"] = m_.groupby("device_id").cum.diff()
m_["kg_per_cycle"] = m_.device_estimated_collected_kg / m_.cyc.where(m_.cyc >= 20)
m_ = m_[(m_.kg_per_cycle > 0) & m_.eval_at.notna()]
m_["lk"] = np.log(m_.kg_per_cycle)
m_["zc"] = (m_.lk - m_.groupby("device_id").lk.transform("median")) / m_.groupby("device_id").lk.transform(lambda s: 1.4826 * (s - s.median()).abs().median()).clip(lower=0.03)
m_ = m_.merge(sites, on="site_id", how="left", suffixes=("", "_s")).merge(mo, on="collection_id", how="left")
m_["moist"] = m_.true_moisture_extra_pct.notna()
e2 = m_[m_.material_stream.isin(["cardboard", "paper"]) & (m_.outdoor_material_staging_s if "outdoor_material_staging_s" in m_ else m_.outdoor_material_staging) == True]
print("\n== moisture via kg per compaction cycle: n=%d wet=%d AUC=%.3f" % (len(e2), e2.moist.sum(), roc_auc_score(e2.moist, e2.zc)))
for thr in (1.5, 2, 3):
    f = e2.zc > thr
    print(f"   z>{thr}: flagged {int(f.sum())}, tp {int((f & e2.moist).sum())}, precision {(f & e2.moist).sum() / max(1, f.sum()):.3f}, recall {(f & e2.moist).sum() / max(1, e2.moist.sum()):.3f}")
