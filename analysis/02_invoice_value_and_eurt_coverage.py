"""(2) EUR of invoice discrepancies by family and what needs independent weight; (3) EUR/t coverage today vs with device weight."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 200)
lab = labels(); dy = device_years()
inv = rd("finance/invoices.parquet"); il = rd("finance/invoice_lines.parquet")
ref = rd("labels_dev/reference_economics.parquet"); rcl = rd("labels_dev/reference_charge_lines.parquet")
df = lifts()

# ------------------------------------------------------------------ (2a) discrepancy EUR by family (public labels, value_at_stake = billed - expected, + = customer overcharged)
il_lab = lab[lab.entity_type == "invoice_line"].copy()
coll_lab = lab[lab.label_family.isin(["MISSING_LINE", "UNINVOICED_COLLECTION"])].copy()
rows = []
for fam, g in pd.concat([il_lab, coll_lab]).groupby("label_family"):
    v = g.value_at_stake_eur.fillna(0)
    rows.append({"family": fam, "n": len(g), "net_eur": v.sum(), "overcharge_eur": v[v > 0].sum(), "undercharge_eur": v[v < 0].sum(), "mean_abs": v.abs().mean()})
fam = pd.DataFrame(rows).set_index("family")
needs = {"DUPLICATE_LINE": "no (same job+line twice)", "UNMATCHED_LINE": "no (phantom job)", "OUTDATED_TARIFF": "no (contract version)",
         "WRONG_SURCHARGE": "no (contract km/fuel)", "WEIGHT_BASIS_MISMATCH": "YES independent mass", "MISSING_LINE": "no to flag; mass to value credit",
         "UNINVOICED_COLLECTION": "no (event without invoice)"}
fam["needs_independent_weight"] = pd.Series(needs)
print("== (2a) invoice discrepancy EUR by family, label window (10 months)"); print(fam.round(1))
fam.round(2).to_csv(OUT / "02_invoice_discrepancy_by_family.csv")
print("total over-charge eur", fam.overcharge_eur.sum().round(1), "total under", fam.undercharge_eur.sum().round(1), "billed total in window",
      inv[inv.billing_period < "2026-08"].total_eur.sum().round(0))

# ------------------------------------------------------------------ (2b) per-tonne-line reconstruction: invoice qty vs ticket qty vs device qty
wbm = il_lab[il_lab.label_family == "WEIGHT_BASIS_MISMATCH"][["entity_id", "value_at_stake_eur", "severity"]].rename(columns={"entity_id": "invoice_line_id"})
x = wbm.merge(il, on="invoice_line_id").merge(inv[["invoice_id", "contract_id", "operator_id", "issued_at"]], on="invoice_id")
r = rcl.rename(columns={"quantity": "ref_qty", "amount_eur": "ref_amount", "unit_price_eur": "ref_price"})
ce = rd("operations/collection_events.parquet")[["collection_id", "operator_job_ref", "device_estimated_collected_kg", "device_id"]]
x = x.merge(ce, on="operator_job_ref", how="left")
x = x.merge(r[["collection_id", "line_type", "ref_qty", "ref_amount"]], on=["collection_id", "line_type"], how="left")
x["inv_qty_over_ref_pct"] = 100 * (x.quantity / x.ref_qty - 1)
tk = df[["collection_id", "ticket_id", "allocated_net_kg", "has_weight_measurement"]]
x = x.merge(tk, on="collection_id", how="left")
x["ticket_shared"] = x.ticket_id.notna()
x["dev_over_inv_pct"] = 100 * (x.device_estimated_collected_kg / 1000 / x.quantity - 1)
print("\n== WEIGHT_BASIS_MISMATCH lines (n=%d): invoice tonnage vs weighbridge reference" % len(x))
print(x[["inv_qty_over_ref_pct", "value_at_stake_eur"]].describe().round(2))
print("ticket shared:", x.ticket_shared.mean().round(3), " device weight on device:", x.has_weight_measurement.mean().round(3), " device est present:", x.device_estimated_collected_kg.notna().mean().round(3))
print("by operator:", x.groupby("operator_id").agg(n=("invoice_line_id", "size"), eur=("value_at_stake_eur", "sum"), shared=("ticket_shared", "mean")).round(2).to_dict("index"))
print("device est vs invoice qty: median %.1f%%, |dev/inv-1|>10%%: %.3f; >3.3%%: %.3f" % (x.dev_over_inv_pct.median(), (x.dev_over_inv_pct.abs() > 10).mean(), (x.dev_over_inv_pct.abs() > 3.3).mean()))
x.to_csv(OUT / "02_weight_basis_mismatch_lines.csv", index=False)

# ------------------------------------------------------------------ (2c) 'weight-exposed' billing: how much of the invoice depends on mass at all?
cv = rd("reference/contract_versions.parquet").set_index("contract_version_id")
rcl2 = rcl.copy()
mass_lines = ["HAUL_PER_TONNE", "PROCESSING", "REJECTION_REPROCESSING", "MIN_CHARGE_TOPUP", "MATERIAL_CREDIT"]
tot_abs = rcl2.groupby(rcl2.line_type.isin(mass_lines)).amount_eur.agg(lambda s: s.abs().sum())
print("\n== share of reference charge lines (gross abs EUR) that depend on mass:", (tot_abs.get(True, 0) / tot_abs.sum()).round(3))
print(rcl2.assign(mass=rcl2.line_type.isin(mass_lines)).groupby("line_type").amount_eur.agg(["count", "sum", lambda s: s.abs().sum()]).round(0))

# ------------------------------------------------------------------ (3) EUR/t coverage today vs with device weight
L = df[df.status.isin(LIFT) & df.eval_at.notna()].copy()
L["src"] = L.observable_mass_source.fillna("NA")
print("\n== (3) observable mass source in label window (lifts n=%d)" % len(L)); print(L.src.value_counts())
cov = L.groupby("operator_id").apply(lambda p: pd.Series({
    "lifts": len(p), "ticket_published": (p.src == "WEIGHBRIDGE_PUBLISHED").mean(), "invoice_tonnage_only": (p.src == "INVOICE_TONNAGE").mean(),
    "device_only": (p.src == "DEVICE_ESTIMATE_ONLY").mean(), "none": (p.src == "NONE").mean()}))
cov.loc["ALL"] = pd.Series({"lifts": len(L), "ticket_published": (L.src == "WEIGHBRIDGE_PUBLISHED").mean(), "invoice_tonnage_only": (L.src == "INVOICE_TONNAGE").mean(),
                            "device_only": (L.src == "DEVICE_ESTIMATE_ONLY").mean(), "none": (L.src == "NONE").mean()})
print(cov.round(3)); cov.round(4).to_csv(OUT / "03_eurt_coverage_by_operator.csv")
# EUR-weighted: share of collection spend on lifts whose EUR/t cannot be verified (no published ticket)
L["spend"] = L.collection_cost_eur
for name, mask in [("no published ticket (EUR/t unverified)", L.src != "WEIGHBRIDGE_PUBLISHED"), ("EUR/t NULL today (device only or none)", L.src.isin(["DEVICE_ESTIMATE_ONLY", "NONE"])),
                   ("invoice tonnage only (unverifiable)", L.src == "INVOICE_TONNAGE")]:
    print(f"{name}: lifts {mask.mean():.3f} spend share {L.spend[mask].sum() / L.spend.sum():.3f} (EUR {L.spend[mask].sum():,.0f})")
# what the device estimate adds: for lifts without a published ticket, how many have a device estimate / device-weight sensor?
nt = L[L.src != "WEIGHBRIDGE_PUBLISHED"]
print("lifts w/o published ticket:", len(nt), " with device est:", int(nt.device_estimated_collected_kg.notna().sum()), "(%.3f)" % nt.device_estimated_collected_kg.notna().mean(),
      " device-sensor devices:", round(nt.has_weight_measurement.mean(), 3))
print(pd.crosstab(nt.src, nt.device_estimated_collected_kg.notna()))
# EUR/t NULL today on lifts that would be recovered by device estimate
nul = L[L.src.isin(["DEVICE_ESTIMATE_ONLY", "NONE"])]
print("EUR/t NULL today: %d lifts (%.2f%% of lifts); recovered by device estimate: %d (%.1f%%)" % (len(nul), 100 * len(nul) / len(L), nul.device_estimated_collected_kg.notna().sum(), 100 * nul.device_estimated_collected_kg.notna().mean()))

# timeliness: days until mass is known (ticket published vs invoice issued vs device = lift time)
tl = L.merge(inv[["invoice_id", "issued_at"]].assign(m=inv.billing_period), left_on=L.service_date.astype(str).str[:7], right_on="m", how="left") if False else None
wb_lag = ((L.published_at - L.arrival_at).dt.total_seconds() / 86400)
print("\nticket sharing lag days (published - weighing): median %.2f, p90 %.2f" % (wb_lag.median(), wb_lag.quantile(.9)))
print(L.assign(lag=wb_lag).groupby("operator_id").lag.describe()[["count", "50%", "mean"]].round(2))
# invoice lag: month end -> issue
inv["svc_month_end"] = pd.to_datetime(inv.billing_period + "-01") + pd.offsets.MonthEnd(0)
inv["issue_lag_from_month_end_d"] = (inv.issued_at.dt.tz_localize(None) - inv.svc_month_end).dt.days
print("invoice issue lag after month end: median %.1f d" % inv.issue_lag_from_month_end_d.median())
# share of lifts with a ticket within 7 / 30 days of the lift  (as-of view, mass knowable 'soon')
act = L.actual_at
for d_ in (2, 7, 30):
    ok = (L.published_at - act).dt.total_seconds() / 86400 <= d_
    print(f"ticket available within {d_} d after lift: {ok.mean():.3f}")
print("device mass available at lift time (device_est present):", L.device_estimated_collected_kg.notna().mean().round(3))

# accuracy of EUR/t from device mass where a ticket exists (EUR/t error vs reference), for lifts with ref EUR/t and mass>=300 kg
ref_l, cv2 = lift_pricing_inputs()
q = ref_l.merge(L[["collection_id", "device_estimated_collected_kg", "allocated_net_kg", "src", "operator_id"]], on="collection_id")
q = q[q.collection_cost_eur_per_t.notna() & q.device_estimated_collected_kg.notna() & (q.billing_mass_kg >= 300) & (q.device_estimated_collected_kg >= 50)].copy()
# re-price collection cost at device mass to get EUR/t error (collection cost depends weakly on mass; per-tonne = cost / t)
q["dev_kg"] = q.device_estimated_collected_kg.clip(lower=1)
q["cc_dev"] = np.nan
vers = cv2.to_dict("index")
from europress_data.economics import price_event, summarize
def cc(r, kg):
    g = None if pd.isna(r.grade_applied) else r.grade_applied
    idx = None if pd.isna(r.index_price_eur_per_t) else int(round(r.index_price_eur_per_t * 100))
    res = price_event(vers[r.contract_version_id], r.status, int(round(kg)), g, idx, emergency=bool(r.emergency), side_waste=bool(r.side_waste), credit_eligible=bool(r.credit_eligible))
    return summarize(res["lines"], int(round(kg)))["collection_cost_eur_per_t"]
q["eurt_dev"] = [cc(r, r.dev_kg) for r in q.itertuples()]
q["err"] = (q.eurt_dev / q.collection_cost_eur_per_t - 1).abs()
print("\nEUR/t from device mass vs reference EUR/t (lifts >=300 kg, n=%d): median err %.1f%%, within 5%%: %.3f, within 10%%: %.3f, within 20%%: %.3f" %
      (len(q), 100 * q.err.median(), (q.err <= .05).mean(), (q.err <= .10).mean(), (q.err <= .20).mean()))
# excluding explained causes (side waste / combined loads): the device is right on these lifts' own mass, but the ticket carries other material
w = lab[lab.label_family == "WEIGHT_DISCREPANCY"].set_index("entity_id").explanation_code
q["cause"] = q.collection_id.map(w).fillna("NO_LABEL")
print(q.groupby("cause").err.agg(["count", "median", lambda s: (s <= .1).mean()]).round(3))
q[["collection_id", "operator_id", "cause", "err"]].to_parquet(OUT / "03_eurt_device_error.parquet")
json.dump({"eurt_null_today_lifts": int(len(nul)), "lifts": int(len(L)), "recovered_by_device": int(nul.device_estimated_collected_kg.notna().sum())}, open(OUT / "03_summary.json", "w"))
