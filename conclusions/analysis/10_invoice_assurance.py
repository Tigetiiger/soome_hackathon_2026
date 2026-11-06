"""UC1 Invoice assurance. (a) billing-discrepancy EUR by family x segment, (b) device-vs-ticket cause attribution by segment,
(c) mass-dependent billing that is unverifiable without device weight, (d) detection power per-lift vs monthly vs quarterly.
Synthetic data, hypothetical prices. Seed fixed."""
import json
from ec_common import *
dv = device_segments(); lab = labels(); res = {}
BILL = ["DUPLICATE_LINE", "MISSING_LINE", "OUTDATED_TARIFF", "UNINVOICED_COLLECTION", "UNMATCHED_LINE", "WEIGHT_BASIS_MISMATCH", "WRONG_SURCHARGE"]
b = lab[lab.label_family.isin(BILL)].copy()
b["over"] = b.value_at_stake_eur.fillna(0).clip(lower=0)            # customer over-charged (recoverable by dispute)
b["under"] = (-b.value_at_stake_eur.fillna(0)).clip(lower=0)        # customer under-charged (operator's risk; neutral reporting)
b = b.merge(dv[["device_id"] + SEGS], on="device_id", how="left")
b["needs_weight"] = b.label_family.eq("WEIGHT_BASIS_MISMATCH")
seg = per_segment(b, "over", dv); seg["eur_per_device_year"] *= YEAR_FACTOR; seg["eur_per_device_year"] = seg.eur_per_device_year.round(2)
seg.to_csv(OUT2 / "10a_overcharge_by_segment.csv", index=False); print(seg.to_string(index=False))
dd = device_dist(b, "over", dv); dd = {k: (v * YEAR_FACTOR if k not in ("share_devices_nonzero",) else v) for k, v in dd.items()}
res["overcharge_per_device_year_dist"] = dd
fam = b.groupby("label_family").agg(n=("entity_id", "size"), over=("over", "sum"), under=("under", "sum"))
fam["over_per_dy"] = fam.over / dv.dev_years.sum() * YEAR_FACTOR; print(fam.round(1)); fam.round(2).to_csv(OUT2 / "10a_family.csv")
res["overcharge_total_window"] = float(b.over.sum()); res["undercharge_total_window"] = float(b.under.sum())
res["overcharge_needs_weight_share"] = float(b[b.needs_weight].over.sum() / b.over.sum())

# (b) cause attribution of device-vs-ticket gaps (> 3.3 % and > 10 %) by operator / stream / tare method
p = pd.read_parquet(OUT / "01_pairs_eur.parquet")
p = p.merge(dv[["device_id", "material_stream", "collection_policy", "primary_sector"]], on="device_id", how="left", suffixes=("", "_d"))
p["gt10"] = p.rel.abs() > .10
ca = p[p.gt10].pivot_table(index="operator_id", columns="cause_g", values="collection_id", aggfunc="count", fill_value=0)
ca["total_gt10"] = ca.sum(axis=1); print("\n>10% gaps by operator x cause\n", ca)
ca.to_csv(OUT2 / "10b_gap_cause_by_operator.csv")
cs = p[p.gt10].pivot_table(index="material_stream", columns="cause_g", values="collection_id", aggfunc="count", fill_value=0); cs.to_csv(OUT2 / "10b_gap_cause_by_stream.csv"); print(cs)
gt = p[p.gt10]
res["gt10_n"] = int(len(gt))
res["gt10_share_by_cause"] = (gt.cause_g.value_counts(normalize=True).round(4)).to_dict()
res["gt10_device_caused_share"] = float((gt.cause_g == "device sensor fault/drift/calibration").mean())
res["gt10_weighbridge_side_share"] = float(gt.cause_g.isin(["stale/wrong tare (operator side)", "side waste on same truck", "combined load (50/50 split)"]).mean())

# (c) mass-dependent invoice lines and whether an independent mass exists today
il = rd("finance/invoice_lines.parquet"); inv = rd("finance/invoices.parquet")[["invoice_id", "contract_id", "operator_id", "billing_period"]]
il = il.merge(inv, on="invoice_id")
il = il[il.billing_period < "2026-08"]
MASS = ["HAUL_PER_TONNE", "PROCESSING", "MATERIAL_CREDIT", "REJECTION_REPROCESSING", "MIN_CHARGE_TOPUP"]
ce = rd("operations/collection_events.parquet")[["operator_job_ref", "device_id", "device_estimated_collected_kg"]]
wb = rd("operations/weighbridge_tickets.parquet").drop_duplicates("operator_job_ref")[["operator_job_ref", "ticket_id"]]
m = il[il.line_type.isin(MASS)].merge(ce, on="operator_job_ref", how="left").merge(wb, on="operator_job_ref", how="left")
m["abs_eur"] = m.amount_eur.abs()
m["evidence"] = np.select([m.ticket_id.notna(), m.device_estimated_collected_kg.notna()], ["ticket shared", "device weight only"], "no independent mass")
ev = m.groupby(["operator_id", "evidence"]).abs_eur.sum().unstack(fill_value=0); ev["total"] = ev.sum(axis=1); print("\nmass-dependent billed EUR (abs) by evidence\n", ev.round(0))
ev.round(2).to_csv(OUT2 / "10c_mass_billing_evidence.csv")
res["mass_billing_abs_eur_window"] = float(m.abs_eur.sum())
res["mass_billing_device_only_eur_window"] = float(m[m.evidence == "device weight only"].abs_eur.sum())
res["mass_billing_noindep_eur_window"] = float(m[m.evidence == "no independent mass"].abs_eur.sum())
tot_bill = il.amount_eur.abs().sum(); res["all_billing_abs_eur_window"] = float(tot_bill)

# (d) detection power: empirical (device vs ticket on clean pairs) per lift / month / quarter, then sigma sweep
c = p[(p.loads_on_vehicle == 1) & (p.tare_method == "WEIGHED") & ~p.cause_g.isin(["device sensor fault/drift/calibration"])].copy()
c["month"] = pd.to_datetime(c.service_date).dt.to_period("M"); c["q"] = pd.to_datetime(c.service_date).dt.to_period("Q")
def power(df, key):
    if key is None:
        g = pd.DataFrame({"r": df.wb_kg / df.dev_kg - 1, "n": 1})
    else:
        a = df.groupby(["device_id", key]).agg(wb=("wb_kg", "sum"), dev=("dev_kg", "sum"), n=("wb_kg", "size"))
        g = pd.DataFrame({"r": a.wb / a.dev - 1, "n": a.n})
    g = g.replace([np.inf, -np.inf], np.nan).dropna()
    tau = g.r.quantile(.975)                                    # 2.5 % false-alarm threshold on correct invoices
    out = {"units": len(g), "median_lifts_per_unit": float(g.n.median()), "sd_r_pct": round(100 * g.r.std(), 2), "iqr_sd_pct": round(100 * (g.r.quantile(.75) - g.r.quantile(.25)) / 1.349, 2), "tau_pct": round(100 * tau, 2)}
    for X in (.03, .05, .10):
        out[f"detect_+{int(X*100)}pct"] = round(float((((1 + X) * (1 + g.r) - 1) > tau).mean()), 3)
    return out
emp = {lvl: power(c, k) for lvl, k in [("per_lift", None), ("device_month", "month"), ("device_quarter", "q")]}
print("\nempirical detection power (clean pairs, weighed tare)"); print(pd.DataFrame(emp).T)
pd.DataFrame(emp).T.to_csv(OUT2 / "10d_detection_empirical.csv")
res["detection_empirical"] = emp
# all pairs (incl. stored tare / side waste) -> reality check
emp_all = {lvl: power(p, k) for lvl, k in [("per_lift", None), ("device_month", "month"), ("device_quarter", "q")]} if False else None
p["month"] = pd.to_datetime(p.service_date).dt.to_period("M"); p["q"] = pd.to_datetime(p.service_date).dt.to_period("Q")
emp_all = {lvl: power(p, k) for lvl, k in [("per_lift", None), ("device_month", "month"), ("device_quarter", "q")]}
pd.DataFrame(emp_all).T.to_csv(OUT2 / "10d_detection_empirical_allpairs.csv"); print(pd.DataFrame(emp_all).T)
res["detection_empirical_allpairs"] = emp_all
# sigma sweep with actual lift counts per device-month: sd_month = sqrt(sb^2 + s^2/n) (+ weighbridge 12 kg ignored at month level)
rng = np.random.default_rng(20261106)
n_m = c.groupby(["device_id", "month"]).size().values
rows = []
for s in (.015, .03, .05, .10):
    for sb in (0.0, .01, .02):
        for lvl, n in [("per_lift", np.ones(20000)), ("device_month", rng.choice(n_m, 20000)), ("device_quarter", rng.choice(n_m, 20000) * 3)]:
            sd = np.sqrt(sb ** 2 + s ** 2 / n)
            e = rng.normal(0, 1, len(n)) * sd
            tau = 1.96 * np.sqrt(sb ** 2 + s ** 2 / n)   # per-unit threshold at its own sd
            row = {"sigma_lift_pct": 100 * s, "bias_sd_pct": 100 * sb, "level": lvl}
            for X in (.03, .05, .10):
                row[f"detect_+{int(X*100)}pct"] = round(float(((X - e) > tau).mean()), 3)
            row["false_alarm"] = round(float(((-e) > tau).mean()), 3)
            rows.append(row)
sw = pd.DataFrame(rows); sw.to_csv(OUT2 / "10d_detection_sigma_sweep.csv", index=False); print(sw.to_string(index=False))
res["median_clean_lifts_per_device_month"] = float(np.median(n_m))
json.dump(res, open(OUT2 / "10_summary.json", "w"), indent=1, default=str); print(json.dumps(res, indent=1, default=str))
