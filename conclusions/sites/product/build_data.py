"""Build compact JSON for the SMART Verified Weight product page (single-file HTML demo).

Read-only on the competition dataset. Reuses ec_common (europress_conclusions/analysis) which in turn
reuses soome_hackathon_2026/analysis/common.py and its 01_pairs_eur.parquet / telemetry_dedup.parquet.
All EUR are the dataset's HYPOTHETICAL tariffs on SYNTHETIC data.

Run:  /home/hackathon/.claude/jobs/717fee2a/tmp/v/bin/python build_data.py
Writes: data.json next to this file, then inlines it into index.html between the DATA markers.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/hackathon/europress_conclusions/analysis")
from ec_common import *  # noqa: F401,F403,E402

HERE = Path(__file__).resolve().parent
A_OUT = Path("/home/hackathon/europress_conclusions/analysis/outputs")
RNG = np.random.default_rng(20261106)
HAULER = {"OP-A": "Hauler Alpha", "OP-B": "Hauler Beta", "OP-C": "Hauler Gamma", "OP-D": "Hauler Delta", "OP-E": "Hauler Epsilon"}
CAUSES = ["no label (agree or small diff)", "side waste on same truck", "stale/wrong tare (operator side)",
          "combined load (50/50 split)", "noise/timing (small loads)", "device sensor fault/drift/calibration"]
CAUSE_KEY = ["agree", "side_waste", "stored_tare", "combined_load", "small_load", "device"]
MASS_LINES = ["PROCESSING", "HAUL_PER_TONNE", "MATERIAL_CREDIT"]
SIGMA_DEV_REL, SIGMA_DEV_KG = 0.014, 15.0      # sensor_registry: GENERIC_INTEGRATED_WEIGHT (simulated)
D0 = pd.Timestamp("2025-10-01")


def r(x, n=0):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    v = round(float(x), n)
    return int(v) if n == 0 else v


def robust_sd(s):
    return float((s.quantile(.75) - s.quantile(.25)) / 1.349)


# ---------------------------------------------------------------- base tables
dv = device_segments()
ce = rd("operations/collection_events.parquet")
wb = rd("operations/weighbridge_tickets.parquet")
il = rd("finance/invoice_lines.parquet")
inv = rd("finance/invoices.parquet")
cv = rd("reference/contract_versions.parquet").set_index("contract_version_id")
ref = rd("labels_dev/reference_economics.parquet")
lab = labels()
pairs = pd.read_parquet(OUT / "01_pairs_eur.parquet")
s10 = json.load(open(A_OUT / "10_summary.json"))
s20 = json.load(open(A_OUT / "20_summary.json"))
s30 = json.load(open(A_OUT / "30_summary.json"))
notes = []          # numbers that disagree with the docs

w0, w1 = WINDOW
L = ce[ce.status.isin(LIFT)].copy()
L["t"] = pd.to_datetime(L.actual_at).dt.tz_localize(None)
L = L.merge(wb.drop_duplicates("operator_job_ref")[["operator_job_ref", "ticket_id", "vehicle_id", "tare_kg", "tare_method",
                                                    "net_kg", "allocated_net_kg", "loads_on_vehicle"]].rename(columns={"vehicle_id": "wb_vehicle"}),
            on="operator_job_ref", how="left")
LW = L[(L.t >= w0) & (L.t < w1)]

# ---------------------------------------------------------------- bands (from data)
pairs = pairs.merge(ce[["collection_id", "operator_job_ref", "vehicle_id", "driver_reported_side_waste"]], on="collection_id", how="left")
pairs["comb"] = pairs.loads_on_vehicle > 1
bands = {}
for (tm, cb), g in pairs.groupby(["tare_method", "comb"]):
    bands[f"{tm}|{'COMBINED' if cb else 'SINGLE'}"] = {"robust_sd_rel": round(robust_sd(g.rel), 4), "n": int(len(g))}
pairs["sd_tk_rel"] = [bands[f"{tm}|{'COMBINED' if cb else 'SINGLE'}"]["robust_sd_rel"] for tm, cb in zip(pairs.tare_method, pairs.comb)]
pairs["sd_dev_kg"] = np.sqrt((SIGMA_DEV_REL * pairs.dev_kg) ** 2 + 2 * SIGMA_DEV_KG ** 2)
pairs["band_kg"] = 2 * np.sqrt(pairs.sd_dev_kg ** 2 + (pairs.sd_tk_rel * pairs.wb_kg) ** 2)
pairs["within"] = (pairs.dev_kg - pairs.wb_kg).abs() <= pairs.band_kg

# invoiced mass per job (mass-priced lines, tonnes -> kg)
ilm = il[il.line_type.isin(MASS_LINES) & (il.unit == "t")]
inv_mass = ilm.groupby("operator_job_ref").agg(inv_kg=("quantity", lambda q: float(q.abs().max()) * 1000),
                                               inv_line=("invoice_line_id", "first"),
                                               unit_price=("unit_price_eur", "first"))
pairs = pairs.merge(inv_mass, left_on="operator_job_ref", right_index=True, how="left")

# ---------------------------------------------------------------- devices
dev_ids = sorted(dv.device_id)
DIX = {d: i for i, d in enumerate(dev_ids)}
prem = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & lab.is_actionable]
BILL = ["DUPLICATE_LINE", "MISSING_LINE", "OUTDATED_TARIFF", "UNINVOICED_COLLECTION", "UNMATCHED_LINE", "WEIGHT_BASIS_MISMATCH", "WRONG_SURCHARGE"]
over = lab[lab.label_family.isin(BILL)].assign(o=lambda x: x.value_at_stake_eur.fillna(0).clip(lower=0)).groupby("device_id").o.sum()
dev_rows = []
pg = pairs.groupby("device_id")
lg = LW.groupby("device_id")
for d in dev_ids:
    x = dv.set_index("device_id").loc[d]
    lifts_d = lg.get_group(d) if d in lg.groups else LW.iloc[:0]
    p = pg.get_group(d) if d in pg.groups else pairs.iloc[:0]
    pu = prem[prem.device_id == d]
    dev_rows.append([
        d, x.material_stream, x.collection_policy, x.operator_id, bool(x.has_weight_measurement), x.equipment_class,
        r(x.container_volume_m3, 1), len(lifts_d), r(lifts_d.device_estimated_collected_kg.sum() / 1000, 1),
        r(lifts_d.ticket_id.notna().mean() if len(lifts_d) else np.nan, 3), len(p),
        r(p.rel.median() * 100 if len(p) else np.nan, 1), int((~p.within).sum()) if len(p) else 0,
        len(pu), r(pu.value_at_stake_eur.sum()), r(over.get(d, 0)), r(x.dev_years, 2), x.primary_sector])
DEV_COLS = ["id", "stream", "policy", "op", "weight", "cls", "m3", "lifts", "t_dev", "tk_share", "pairs", "gap_med_pct",
            "outside", "unjust", "unjust_eur", "overcharge_eur", "dy", "sector"]

# ---------------------------------------------------------------- lifts (pairs) columnar
pairs["date"] = pd.to_datetime(pairs.service_date)
pairs = pairs.sort_values(["device_id", "date"]).reset_index(drop=True)
vehicles = sorted(pairs.vehicle_id.dropna().unique())
VIX = {v: i for i, v in enumerate(vehicles)}
TM = {"WEIGHED": 0, "STORED": 1}
PM = ["FIXED_PER_LIFT", "HYBRID", "HYBRID_MIN", "PER_TONNE"]
lifts_col = {
    "dev": [DIX[d] for d in pairs.device_id],
    "seq": [int(c.split("-")[-1]) for c in pairs.collection_id],
    "day": [(dt - D0).days for dt in pairs.date],
    "dev_kg": [r(v) for v in pairs.dev_kg],
    "wb_kg": [r(v) for v in pairs.wb_kg],
    "inv_kg": [r(v) for v in pairs.inv_kg],
    "tare": [TM.get(t, -1) for t in pairs.tare_method],
    "loads": [r(v) for v in pairs.loads_on_vehicle],
    "veh": [VIX.get(v, -1) if isinstance(v, str) else -1 for v in pairs.vehicle_id],
    "cause": [CAUSES.index(c) for c in pairs.cause_g],
    "pm": [PM.index(p) for p in pairs.pricing_model],
    "d_eur": [r(v, 2) for v in pairs.delta_eur],
    "sw": [1 if v is True else 0 for v in pairs.driver_reported_side_waste],
}

# ---------------------------------------------------------------- fleet KPIs
lw_dev = LW[LW.device_estimated_collected_kg.notna()]
mon = lw_dev.assign(m=lw_dev.t.dt.to_period("M")).groupby(["device_id", "m"]).device_estimated_collected_kg.agg(["sum", "size"])
fleet = {
    "devices": len(dv), "devices_weight": int(dv.has_weight_measurement.sum()), "device_years": round(device_years(), 1),
    "lifts_window": int(len(LW)), "lifts_with_device_kg": int(len(lw_dev)),
    "lifts_with_ticket": int(LW.ticket_id.notna().sum()), "ticket_share": round(float(LW.ticket_id.notna().mean()), 3),
    "tk_share_by_op": {o: round(float(g.ticket_id.notna().mean()), 3) for o, g in LW.groupby("operator_id")},
    "lifts_by_op": {o: int(len(g)) for o, g in LW.groupby("operator_id")},
    "t_device": round(float(lw_dev.device_estimated_collected_kg.sum() / 1000), 1),
    "pairs": int(len(pairs)), "pairs_within": int(pairs.within.sum()), "pairs_gt10": int((pairs.rel.abs() > .10).sum()),
    "bands": bands,
    "overcharge_window_eur": round(s10["overcharge_total_window"], 0), "undercharge_window_eur": round(s10["undercharge_total_window"], 0),
    "overcharge_dist": {k: round(v, 1) for k, v in s10["overcharge_per_device_year_dist"].items()},
    "overcharge_needs_weight_share": round(s10["overcharge_needs_weight_share"], 3),
    "mass_billing_eur": round(s10["mass_billing_abs_eur_window"], 0),
    "mass_billing_device_only_eur": round(s10["mass_billing_device_only_eur_window"], 0),
    "mass_billing_noindep_eur": round(s10["mass_billing_noindep_eur_window"], 0),
    "fixed_hybrid_dist": {k: round(v, 1) for k, v in s20["fixed_hybrid_device_dist_eur_per_dy"].items()},
    "c2": {"cases": s30["c2_cases"], "best_mean": round(s30["c2_best_set_value_per_case_mean"], 0),
           "pos_by_action": s30["c2_pos_value_by_action"], "pos_device_only": s30["c2_pos_value_device_only_mass"]},
    "month_rel_sd_note": "device-month totals vs ticket totals",
}
# T-tier mapping of the fleet (illustrative: which tier each device could run at today)
tier = []
for row in dev_rows:
    if not row[4]:
        tier.append("none")
    elif (row[9] or 0) >= 0.5:
        tier.append("T1")
    else:
        tier.append("T0")
fleet["tier_counts"] = {k: tier.count(k) for k in ["T0", "T1", "none"]}
# gap histogram (device vs ticket, %), clipped to +-60
h, edges = np.histogram((pairs.rel * 100).clip(-60, 60), bins=np.arange(-60, 62.5, 2.5))
fleet["gap_hist"] = {"edges": [float(e) for e in edges], "counts": [int(c) for c in h]}
fleet["gap_hist_by_tare"] = {tm: [int(c) for c in np.histogram((g.rel * 100).clip(-60, 60), bins=edges)[0]]
                             for tm, g in pairs[~pairs.comb].groupby("tare_method")}

# ---------------------------------------------------------------- cause attribution
gt = pairs[pairs.rel.abs() > .10]
causes = {
    "n_gt10": int(len(gt)), "n_pairs": int(len(pairs)),
    "share": {CAUSE_KEY[i]: round(float((gt.cause_g == c).mean()), 4) for i, c in enumerate(CAUSES)},
    "by_op": {o: {CAUSE_KEY[i]: int((g.cause_g == c).sum()) for i, c in enumerate(CAUSES)} for o, g in gt.groupby("operator_id")},
    "by_stream": {s: {CAUSE_KEY[i]: int((g.cause_g == c).sum()) for i, c in enumerate(CAUSES)} for s, g in gt.groupby("material_stream")},
}
chk = s10["gt10_share_by_cause"]
if abs(causes["share"]["device"] - chk["device sensor fault/drift/calibration"]) > 1e-3:
    notes.append("device-fault share differs from 10_summary")
causes["weighbridge_side"] = round(causes["share"]["side_waste"] + causes["share"]["stored_tare"] + causes["share"]["combined_load"], 4)

# vehicle stored tare vs weighed tare (+ split-half stability)
wbt = wb.copy()
wbt["t"] = pd.to_datetime(wbt.arrival_at).dt.tz_localize(None)
mid = w0 + (w1 - w0) / 2
veh = []
for v, g in wbt.groupby("vehicle_id"):
    st, we = g[g.tare_method == "STORED"], g[g.tare_method == "WEIGHED"]
    if len(st) < 10 or len(we) < 20:
        continue
    stored = float(st.tare_kg.median())
    wm = float(we.tare_kg.median())
    h1, h2 = we[we.t < mid].tare_kg, we[we.t >= mid].tare_kg
    pv = pairs[(pairs.vehicle_id == v) & (pairs.tare_method == "STORED") & ~pairs.comb & (pairs.wb_kg > 1000)]
    se = 1.2533 * robust_sd(we.tare_kg) / np.sqrt(len(we))
    veh.append({"v": v, "op": v[:4], "stored": r(stored), "weighed_med": r(wm), "off": r(stored - wm), "off_se": r(se, 1),
                "n_st": int(len(st)), "n_we": int(len(we)), "st_values": int(st.tare_kg.nunique()),
                "off_h1": r(stored - h1.median()) if len(h1) >= 10 else None, "off_h2": r(stored - h2.median()) if len(h2) >= 10 else None,
                "n_pairs_st": int(len(pv)), "rel_med_st": r(pv.rel.median() * 100, 1) if len(pv) >= 5 else None})
veh.sort(key=lambda x: x["off"])
causes["vehicles"] = veh
causes["vehicles_abs_ge200"] = sum(1 for x in veh if abs(x["off"]) >= 200)

# ---------------------------------------------------------------- hero H1: full chain
def chain(job):
    Lr = L[L.operator_job_ref == job].iloc[0]
    rr = ref.set_index("collection_id").loc[Lr.collection_id]
    ver = cv.loc[rr.contract_version_id]
    t = wb[wb.operator_job_ref == job]
    t = t.iloc[0] if len(t) else None
    lines = il[il.operator_job_ref == job].merge(inv[["invoice_id", "billing_period", "issued_at"]], on="invoice_id")
    rcl = rd("labels_dev/reference_charge_lines.parquet")
    rcl = rcl[rcl.collection_id == Lr.collection_id]
    labs = lab[lab.entity_id.isin([Lr.collection_id] + lines.invoice_line_id.tolist())]
    return {
        "job": job, "collection_id": Lr.collection_id, "device": Lr.device_id, "date": str(Lr.t.date()), "time": Lr.t.strftime("%H:%M"),
        "op": Lr.operator_id, "stream": dv.set_index("device_id").loc[Lr.device_id, "material_stream"],
        "policy": dv.set_index("device_id").loc[Lr.device_id, "collection_policy"],
        "fill_before": r(Lr.device_fill_pct_before, 1), "mass_before": r(Lr.device_mass_kg_before), "mass_after": r(Lr.device_mass_kg_after),
        "dev_kg": r(Lr.device_estimated_collected_kg),
        "ticket": None if t is None else {"id": t.ticket_id, "vehicle": t.vehicle_id, "gross": r(t.gross_kg), "tare": r(t.tare_kg),
                                          "tare_method": t.tare_method, "net": r(t.net_kg), "alloc": r(t.allocated_net_kg),
                                          "loads": r(t.loads_on_vehicle), "facility": t.facility_id, "published": str(t.published_at)[:10]},
        "contract_version": rr.contract_version_id,
        "contract": {k: (r(ver[k]) if k != "pricing_model" else ver[k]) for k in
                     ["pricing_model", "lift_fee_cents", "processing_fee_cents_per_t", "haul_fee_cents_per_t", "min_charge_cents", "credit_share_bp", "default_weight_kg", "fuel_surcharge_bp"]},
        "ref_billing_kg": r(rr.billing_mass_kg), "ref_basis": rr.billing_mass_basis, "ref_invoice_eur": r(rr.expected_invoice_amount_eur, 2),
        "ref_eur_t": r(rr.total_cost_eur_per_t, 2), "obs_mass_source": rr.observable_mass_source,
        "lines": [{"id": x.invoice_line_id, "type": x.line_type, "qty": r(x.quantity, 3), "unit": x.unit, "price": r(x.unit_price_eur, 2),
                   "eur": r(x.amount_eur, 2), "invoice": x.invoice_id} for x in lines.itertuples()],
        "ref_lines": [{"type": x.line_type, "qty": r(x.quantity, 3), "eur": r(x.amount_eur, 2)} for x in rcl.itertuples()],
        "labels": [{"entity": x.entity_id, "family": x.label_family, "code": x.explanation_code, "eur": r(x.value_at_stake_eur, 2), "sev": x.severity} for x in labs.itertuples()],
    }


tel = pd.read_parquet(OUT / "telemetry_dedup.parquet", columns=["device_id", "measured_at", "fill_pct", "mass_kg", "mass_uncertainty_kg", "sensor_status"])
tel["t"] = pd.to_datetime(tel.measured_at).dt.tz_localize(None) if tel.measured_at.dt.tz is not None else tel.measured_at


def mass_trace(device, t_center, hours=72):
    g = tel[(tel.device_id == device) & (tel.t >= t_center - pd.Timedelta(hours=hours)) & (tel.t <= t_center + pd.Timedelta(hours=hours))].sort_values("t")
    return [[r((x.t - t_center).total_seconds() / 3600, 1), r(x.mass_kg), r(x.mass_uncertainty_kg), r(x.fill_pct, 1)] for x in g.itertuples()]


heroes = {}
h1 = chain("OP-E-003920032")
h1t = L[L.operator_job_ref == "OP-E-003920032"].t.iloc[0]
h1["trace"] = mass_trace("CMP-00392", h1t)
inv_line = [x for x in h1["lines"] if x["id"] == "INV-00392-202512-L045"][0]
assert abs(inv_line["qty"] - 5.08) < 1e-6 and h1["ticket"]["net"] == 4200 and h1["dev_kg"] == 4125, "H1 numbers changed"
heroes["H1"] = h1
heroes["H1b"] = chain("OP-B-000100042")

# vehicle hero lifts (same picks as 61_hero_traces)
heroes["V06"] = chain("OP-E-000700009")
heroes["V12"] = chain("OP-A-001950014")

# "says no": single load, stored tare, FIXED_PER_LIFT, gap well outside band, EUR 0 on the invoice
sn = pairs[(pairs.pricing_model == "FIXED_PER_LIFT") & ~pairs.comb & (pairs.tare_method == "STORED") & ~pairs.within
           & (pairs.delta_eur.abs() < .005) & (pairs.cause_g == "stale/wrong tare (operator side)")].copy()
sn["k"] = (sn["diff"].abs() - 335).abs()
pick = sn.sort_values("k").iloc[0]
heroes["NO"] = chain(pick.operator_job_ref)
heroes["NO"]["band_kg"] = r(pick.band_kg)

# ---------------------------------------------------------------- invoice-vs-masses rule over all lifts (R1)
pp = pairs[pairs.inv_kg.notna()].copy()
pp["best_kg"] = (pp.dev_kg / pp.sd_dev_kg ** 2 + pp.wb_kg / (pp.sd_tk_rel * pp.wb_kg) ** 2) / (1 / pp.sd_dev_kg ** 2 + 1 / (pp.sd_tk_rel * pp.wb_kg) ** 2)
pp["best_sd"] = 1 / np.sqrt(1 / pp.sd_dev_kg ** 2 + 1 / (pp.sd_tk_rel * pp.wb_kg) ** 2)
pp["agree"] = pp.within
pp["inv_gap"] = pp.inv_kg - pp.wb_kg
pp["flag"] = pp.agree & (pp.inv_gap.abs() > np.maximum(3 * pp.best_sd, 100))
fl = pp[pp.flag]
wbm = lab[lab.label_family == "WEIGHT_BASIS_MISMATCH"]
tp = fl.inv_line.isin(wbm.entity_id).sum()
rule_r1 = {"flagged": int(len(fl)), "true_wbm": int(tp), "labels_wbm": int(len(wbm)), "precision": round(tp / max(1, len(fl)), 3),
           "recall_on_paired": round(tp / max(1, wbm.entity_id.isin(pp.inv_line).sum()), 3),
           "wbm_on_paired": int(wbm.entity_id.isin(pp.inv_line).sum()),
           "over_eur": round(float(((fl.inv_kg - fl.best_kg) / 1000 * fl.unit_price.abs()).clip(lower=0).sum()), 0)}

# ---------------------------------------------------------------- Proof of fullness: CMP-00430
D = "CMP-00430"
x430 = dv.set_index("device_id").loc[D]
L430 = LW[(LW.device_id == D) & LW.collection_id.isin(ref[ref.eval_at.notna()].collection_id)].sort_values("t")  # labelled lifts, as in 61_hero_traces
pl430 = prem[prem.device_id == D].set_index("entity_id")
ref_i = ref.set_index("collection_id")
pof_lifts = [[(x.t - D0).days, r(x.t.hour + x.t.minute / 60, 1), r(x.device_fill_pct_before, 1), r(x.device_estimated_collected_kg),
              1 if x.collection_id in pl430.index else 0, r(pl430.value_at_stake_eur.get(x.collection_id, 0), 2),
              r(ref_i.total_customer_cost_eur.get(x.collection_id, np.nan), 2), int(x.collection_id.split("-")[-1])] for x in L430.itertuples()]
day = rd("telemetry/telemetry_daily_summary.parquet")
day = day[day.device_id == D].copy()
day["d"] = (pd.to_datetime(day.date) - D0).dt.days
day = day[(day.d >= 0) & (day.d < 304)].sort_values("d")
pof_daily = [[int(x.d), r(x.fill_pct_max, 1), r(x.mass_kg_max_valid)] for x in day.itertuples()]
dc = rd("benchmark/decision_cases.parquet"); dt = rd("labels_dev/decision_truth.parquet"); do = rd("labels_dev/decision_outcomes.parquet")
c430 = dc[dc.device_id == D].merge(dt, on=["case_id", "split"]).sort_values("decision_at")
cases430 = []
for c in c430.itertuples():
    o = do[do.case_id == c.case_id]
    cases430.append({"case": c.case_id, "at": str(c.decision_at)[:10], "h": int(c.horizon_days), "best": c.best_action, "best_eur": r(c.best_benefit_cents / 100),
                     "acceptable": list(c.acceptable_actions) if not isinstance(c.acceptable_actions, str) else c.acceptable_actions,
                     "opts": [{"a": y.action, "eur": r(y.benefit_vs_no_action_cents / 100), "se": r(y.benefit_se_cents / 100), "ok": bool(y.permissible),
                               "lifts": r(y.n_completed_lifts, 1), "overflow_h": r(y.overflow_open_hours, 1), "trap": bool(y.hidden_cost_trap)} for y in o.itertuples()]})
g30 = pd.read_csv(A_OUT / "30a_contract_eurt_vs_peer.csv")
gx = g30[g30.contract_id == "CTR-00430"].iloc[0]
pof = {
    "device": D, "customer": x430.customer_id, "policy": x430.collection_policy, "per_week": r(x430.fixed_schedule_per_week, 1),
    "stream": x430.material_stream, "m3": r(x430.container_volume_m3, 1), "op": x430.operator_id, "contract": x430.contract_id,
    "lifts": pof_lifts, "daily": pof_daily, "cases": cases430,
    "n_lifts": len(pof_lifts), "n_unjust": int(sum(p[4] for p in pof_lifts)), "eur_unjust": round(float(pl430.value_at_stake_eur.sum()), 2),
    "fill_med": r(L430.device_fill_pct_before.median(), 1), "kg_med": r(L430.device_estimated_collected_kg.median()),
    "eur_t": r(gx.net_cost_eur_t, 1), "peer_eur_t": r(gx.peer_med_eur_t, 1), "tk_share": r(L430.ticket_id.notna().mean(), 3),
    "policy_table": pd.read_csv(A_OUT / "20a_share_unjustified_by_policy.csv").to_dict("records"),
    "detect": pd.read_csv(A_OUT / "20b_detection_by_policy.csv").to_dict("records"),
    "value_by_policy": pd.read_csv(A_OUT / "20c_decision_value_by_policy.csv").round(0).to_dict("records"),
}
seg = pd.read_csv(A_OUT / "20a_premature_by_segment.csv")
pof["eur_dy_by_policy"] = seg[seg.segment == "collection_policy"][["value", "eur_per_device_year", "lifts_per_device_year"]].to_dict("records")
if pof["n_unjust"] != 45 or pof["n_lifts"] != 78:
    notes.append(f"CMP-00430: {pof['n_unjust']} of {pof['n_lifts']} lifts unjustified (docs: 45 of 78)")

# ---------------------------------------------------------------- CTR-00142 contract hero
oa = rd("labels_dev/operator_action_values.parquet")
o142 = oa[oa.case_id == "OC-00142"]
g142 = g30[g30.contract_id == "CTR-00142"].iloc[0]
L142 = LW[LW.device_id == "CMP-00142"]
ctr142 = {"contract": "CTR-00142", "device": "CMP-00142", "op": "OP-D", "stream": "cardboard", "pricing": "HYBRID_MIN",
          "t": r(L142.device_estimated_collected_kg.sum() / 1000, 1), "lifts": int(len(L142)), "tk_share": r(L142.ticket_id.notna().mean(), 3),
          "eur_t": r(g142.net_cost_eur_t, 1), "peer_eur_t": r(g142.peer_med_eur_t, 1), "gap_pct": r(g142.gap_pct, 1),
          "annual_cost": r(o142.annual_contract_cost_eur.iloc[0], 2),
          "actions": {y.action: {"eur": r(y.value_eur, 2), "pos": bool(y.positive)} for y in o142.itertuples()},
          "renegotiated_annual": r(o142[o142.action == "RENEGOTIATE_CONTRACT"].renegotiated_annual_cost_eur.iloc[0], 2),
          "alt_op": o142[o142.action == "TENDER_OR_SWITCH_OPERATOR"].best_alternative_operator.iloc[0]}
if ctr142["gap_pct"] < 0:
    notes.append(f"CTR-00142 device-weight EUR/t {ctr142['eur_t']} is {ctr142['gap_pct']}% vs peer median {ctr142['peer_eur_t']} (below peer); "
                 "the C2 renegotiate/tender value is tariff-driven, not an above-peer price")

# ---------------------------------------------------------------- recommendations (rules decide)
def marginal_eur_per_t(cid):
    rr = ref_i.loc[cid]
    rc = RCL[RCL.collection_id == cid]
    m = rc[rc.unit == "t"].amount_eur.sum()
    return float(m / (rr.billing_mass_kg / 1000)) if rr.billing_mass_kg and rr.billing_mass_kg > 0 else 0.0


RCL = rd("labels_dev/reference_charge_lines.parquet")
props = []
# R1 dispute (H1)
row = pp[pp.inv_line == "INV-00392-202512-L045"].iloc[0]
over_kg = row.inv_kg - row.best_kg
z = 1.2816
props.append({"id": "P-001", "rule": "R1 INVOICE_MASS_VS_TWO_MASSES", "action": "DISPUTE_INVOICE", "sev": "warning",
              "to": "Customer finance (then Hauler Epsilon)", "subject": "INV-00392-202512-L045", "device": "CMP-00392", "op": "OP-E",
              "title": "Invoice bills 0.88 t more processing than both independent masses",
              "why": [f"Invoice line INV-00392-202512-L045 bills PROCESSING 5.080 t at €126.82/t = €644.25.",
                      f"Weighbridge ticket WB-OP-E-00392-0032: net 4,200 kg (stored tare, single load).",
                      f"Compactor: 4,200 kg before, 75 kg after, so 4,125 kg collected (−1.8% vs ticket, inside the ±{r(row.band_kg)} kg band).",
                      f"Combined mass estimate {r(row.best_kg)} ± {r(row.best_sd)} kg (1σ). The invoice is {r((row.inv_kg-row.best_kg)/row.best_sd)}σ above it."],
              "evidence": [["collection_events", "COL-00392-0032", "OBSERVED"], ["weighbridge_tickets", "WB-OP-E-00392-0032", "OBSERVED"],
                           ["invoice_lines", "INV-00392-202512-L045", "OBSERVED"], ["contract_versions", "CTR-00392-V1", "OBSERVED"]],
              "value": {"p10": r((over_kg - z * row.best_sd) / 1000 * 126.82, 2), "p50": r(over_kg / 1000 * 126.82, 2),
                        "p90": r((over_kg + z * row.best_sd) / 1000 * 126.82, 2), "label_eur": 111.61, "unit": "one-off", "tag": "ESTIMATED"},
              "reverse": "Withdraw the query before the hauler replies; nothing is credited until the hauler issues a credit note.",
              "limits": "A late contract amendment or a re-weigh we have not seen would explain it. The ticket uses a stored tare; the device agrees with it, so a tare error does not explain 0.88 t.",
              "conf": "High"})
# R2 vehicle tare (operator first)
for vid, pid in [("OP-E-V06", "P-002"), ("OP-A-V12", "P-003")]:
    vv = [x for x in veh if x["v"] == vid][0]
    st = L[(L.wb_vehicle == vid) & (L.tare_method == "STORED") & (L.t >= w0) & (L.t < w1)]
    st = st[st.collection_id.isin(ref_i.index)]
    mt = np.array([marginal_eur_per_t(c) for c in st.collection_id])
    eur = -vv["off"] / 1000 * mt          # stored tare too low -> net too high -> customer pays more (positive = customer overpays)
    tot = float(eur.sum())
    se = vv["off_se"] / 1000 * float(np.abs(mt).sum())
    props.append({"id": pid, "rule": "R2 STORED_TARE_OFFSET", "action": "FIX_VEHICLE_TARE", "sev": "notice",
                  "to": f"{HAULER[vid[:4]]} weighbridge team (operator first)", "subject": vid, "device": None, "op": vid[:4],
                  "title": f"Vehicle {vid}: stored tare is {abs(vv['off'])} kg {'below' if vv['off'] < 0 else 'above'} its weighed tare",
                  "why": [f"Stored tare {vv['stored']:,} kg on {vv['n_st']} tickets; weighed tare median {vv['weighed_med']:,} kg on {vv['n_we']} tickets.",
                          f"So every stored-tare net is about {abs(vv['off'])} kg too {'high' if vv['off'] < 0 else 'low'}.",
                          f"Split-half check: offset {vv['off_h1']} kg (first half) vs {vv['off_h2']} kg (second half), so it is stable, not a one-off.",
                          f"Device vs ticket on its stored-tare single loads: median {vv['rel_med_st']}% (n={vv['n_pairs_st']})."],
                  "evidence": [["weighbridge_tickets", f"{vid} STORED ×{vv['n_st']}", "OBSERVED"], ["weighbridge_tickets", f"{vid} WEIGHED ×{vv['n_we']}", "OBSERVED"],
                               ["collection_events", f"{vv['n_pairs_st']} paired lifts", "OBSERVED"]],
                  "value": {"p10": r(tot - z * se, 0), "p50": r(tot, 0), "p90": r(tot + z * se, 0), "unit": f"in window, {len(st)} stored-tare lifts (+ = customers overpaid)", "tag": "ESTIMATED"},
                  "reverse": "Share privately with the operator first. If the operator re-weighs and the offset disappears, close the item; no customer-facing claim is made.",
                  "limits": "The weighed tare varies with fuel, crew and equipment. A vehicle fitted with heavier equipment after its tare was stored would also look like this. This is a weighbridge-hygiene finding, not intent.",
                  "conf": "High" if vv["n_we"] >= 50 else "Medium"})
# R3 Proof of fullness
c0 = cases430[0]
rf = [o for o in c0["opts"] if o["a"] == "REDUCE_FREQUENCY"][0]
props.append({"id": "P-004", "rule": "R3 PROOF_OF_FULLNESS", "action": "REDUCE_FREQUENCY", "sev": "notice",
              "to": "Site manager ORG-0049 (then Hauler Delta schedule change)", "subject": "CMP-00430", "device": "CMP-00430", "op": "OP-D",
              "title": f"Fixed schedule: {pof['n_unjust']} of {pof['n_lifts']} lifts were not needed",
              "why": [f"Fixed schedule 2 lifts/week, 8 m³ mixed waste. Median fill at lift {pof['fill_med']}%, median {pof['kg_med']:,} kg collected.",
                      f"{pof['n_unjust']} lifts labelled unjustified, €{pof['eur_unjust']:,.0f} in the window (hypothetical tariff).",
                      "Hauler Delta shares no tickets, so the compactor's weight is the only tonnage evidence for the schedule change.",
                      f"Simulated 56-day horizon: reduce frequency €{rf['eur']:,} benefit; switching to on-call or a mass trigger is not permissible (overflow {[o['overflow_h'] for o in c0['opts'] if o['a']=='SWITCH_TO_ON_CALL'][0]} h)."],
              "evidence": [["collection_events", f"{pof['n_lifts']} lifts CMP-00430", "OBSERVED"], ["telemetry_daily_summary", "CMP-00430 fill/mass", "OBSERVED"],
                           ["decision_outcomes", c0["case"], "SIMULATED"]],
              "value": {"p10": r(rf["eur"] - z * rf["se"], 0), "p50": rf["eur"], "p90": r(rf["eur"] + z * rf["se"], 0), "unit": "per 56 days (simulated)", "tag": "SIMULATED"},
              "reverse": "Schedule change is reversible at the next schedule review; SMART watches fill daily and raises an overflow alarm if the new schedule is too thin.",
              "limits": "The benefit is a simulated counterfactual, not a measured saving. Seasonal peaks could need the old frequency; 2 of 9 later cases say no action.",
              "conf": "Medium"})
# R4 contract (CTR-00142)
props.append({"id": "P-005", "rule": "R4 CONTRACT_VALUE_DEVICE_ONLY_MASS", "action": "RENEGOTIATE_CONTRACT", "sev": "info",
              "to": "Customer procurement (discussion with Hauler Delta)", "subject": "CTR-00142", "device": "CMP-00142", "op": "OP-D",
              "title": "Contract review: the only tonnage evidence is the compactor's",
              "why": [f"{ctr142['t']} t over {ctr142['lifts']} lifts, ticket share {int((ctr142['tk_share'] or 0)*100)}%: device weight is the only mass.",
                      f"Device-weight net cost €{ctr142['eur_t']}/t vs stream peer median €{ctr142['peer_eur_t']}/t ({ctr142['gap_pct']}%).",
                      f"Dataset valuation rules price RENEGOTIATE at €{ctr142['actions']['RENEGOTIATE_CONTRACT']['eur']:,.0f} and TENDER at €{ctr142['actions']['TENDER_OR_SWITCH_OPERATOR']['eur']:,.0f} on €{ctr142['annual_cost']:,.0f} annual cost.",
                      "Tendering is the last step and is gated: it needs procurement sign-off and the 'talk to the operator first' step."],
              "evidence": [["contracts", "CTR-00142", "OBSERVED"], ["collection_events", f"{ctr142['lifts']} lifts CMP-00142", "OBSERVED"],
                           ["operator_action_values", "OC-00142", "SIMULATED"]],
              "value": {"p10": None, "p50": ctr142["actions"]["RENEGOTIATE_CONTRACT"]["eur"], "p90": None, "unit": "per year (valuation rules, point value)", "tag": "HYPOTHETICAL"},
              "reverse": "A discussion request commits to nothing; it can be closed without contacting the operator.",
              "limits": "Value comes from the dataset's hypothetical tariff rules. The contract is already below the peer median €/t, so the case rests on contract terms, not on a high price.",
              "conf": "Medium"})
# R5 drift watch + ticket confirmation
ep = pd.read_csv(A_OUT / "50_drift_episodes_T06.csv")
ep = ep[ep.detected].sort_values("days_before_fix", ascending=False).iloc[0]
props.append({"id": "P-006", "rule": "R5 DRIFT_WATCH_CONFIRMED", "action": "VERIFY_WEIGHT_SENSOR", "sev": "warning",
              "to": "SMART Center service planning", "subject": ep.device_id, "device": ep.device_id, "op": None,
              "title": f"{ep.device_id}: weight sensor drift confirmed by tickets",
              "why": [f"Ticket-free watch (kg per fill vs the device's own baseline) raised a watch; clean ticket pairs confirmed a shift above 6%.",
                      f"Confirmed {int(ep.lead_days_after_start)} days after the episode started, {int(ep.days_before_fix)} days before today's fix.",
                      "Fleet-wide: ticket-confirmed alarm caught 7 of 10 episodes that had clean pairs, 0.30 false-alarm episodes per device-year."],
              "evidence": [["telemetry_hourly", f"{ep.device_id} mass/fill", "OBSERVED"], ["weighbridge_tickets", "clean pairs", "OBSERVED"],
                           ["maintenance_work_orders", "SENSOR_RECALIBRATION", "OBSERVED"]],
              "value": {"p10": None, "p50": None, "p90": None, "unit": "no € claimed (visit cost is an assumption)", "tag": "HYPOTHETICAL"},
              "reverse": "Cancel the work order before the visit; the device keeps its current calibration.",
              "limits": "Drift and a real change in material density look alike for weeks. That is why the watch needs ticket confirmation before a visit.",
              "conf": "Medium"})
# R6 says no
no = heroes["NO"]
props.append({"id": "P-007", "rule": "R6 GAP_WITHOUT_MONEY", "action": "NO_ACTION", "sev": "info",
              "to": "Nobody (logged only)", "subject": no["collection_id"], "device": no["device"], "op": no["op"],
              "title": f"{abs(int(pick['diff']))} kg gap on {no['collection_id']}: real, but worth €0",
              "why": [f"Device {r(pick.dev_kg):,} kg vs ticket {r(pick.wb_kg):,} kg (stored tare): outside the ±{r(pick.band_kg)} kg band.",
                      "The contract is fixed price per lift. No invoice line depends on mass, so re-pricing on the device weight changes €0.00.",
                      "Logged for the vehicle-tare report; no dispute, no letter."],
              "evidence": [["collection_events", no["collection_id"], "OBSERVED"], ["weighbridge_tickets", no["ticket"]["id"] if no["ticket"] else "-", "OBSERVED"],
                           ["contract_versions", no["contract_version"], "OBSERVED"]],
              "value": {"p10": 0, "p50": 0, "p90": 0, "unit": "on this invoice", "tag": "ESTIMATED"},
              "reverse": "Nothing to reverse.", "limits": "Affects reported €/t only, not the invoice.", "conf": "High"})
# R7 give-to-get data request
props.append({"id": "P-008", "rule": "R7 NO_TICKETS_SHARED", "action": "REQUEST_WEIGHBRIDGE_DATA", "sev": "info",
              "to": "Hauler Delta (operator API invitation)", "subject": "OP-D", "device": None, "op": "OP-D",
              "title": "Hauler Delta shares 0% of tickets: invite to the ticket feed",
              "why": [f"{fleet['lifts_by_op'].get('OP-D', 0):,} lifts in the window, {int(fleet['tk_share_by_op'].get('OP-D', 0)*100)}% with a ticket.",
                      "Give-to-get: shared tickets return a reconciliation receipt and a private tare-hygiene report to the operator.",
                      "The dataset's valuation rules give this request −€20 (admin cost) per contract, so it is offered as a service, not as savings."],
              "evidence": [["operators", "OP-D weighbridge_data_shared=false", "OBSERVED"], ["collection_events", "OP-D lifts", "OBSERVED"]],
              "value": {"p10": None, "p50": -20, "p90": None, "unit": "per contract (admin cost, valuation rules)", "tag": "HYPOTHETICAL"},
              "reverse": "Invitation can be withdrawn; no data flows until the operator opts in.", "limits": "Operators may decline; nothing in this product depends on it.", "conf": "High"})

# ---------------------------------------------------------------- simulated calibration (Monte Carlo check of closed form)
def mc(sig_e, sig_b, sig_t, n_month, ks, n=4000):
    out = []
    for k in ks:
        b = RNG.normal(0, sig_b, n)
        # Kalman / conjugate update of the machine gain from k anchors (ticket noise + lift noise)
        obs = b[:, None] + RNG.normal(0, np.sqrt(sig_e ** 2 + sig_t ** 2), (n, k)) if k else np.zeros((n, 0))
        prec = 1 / sig_b ** 2 + k / (sig_e ** 2 + sig_t ** 2)
        bhat = (obs.sum(1) / (sig_e ** 2 + sig_t ** 2)) / prec if k else np.zeros(n)
        res = b - bhat
        lift = res + RNG.normal(0, sig_e, n)
        month = res + RNG.normal(0, sig_e / np.sqrt(n_month), n)
        out.append([k, round(float(np.sqrt(np.mean(lift ** 2)) * 100), 2), round(float(np.sqrt(np.mean(month ** 2)) * 100), 2)])
    return out


sim = {"params": {"sig_e": 0.12, "sig_b_fleet": 0.034, "sig_b_none": 0.09, "sig_t": 0.04, "n_month": 8},
       "mc_fleet": mc(.12, .034, .04, 8, [0, 1, 2, 3, 5, 10, 20, 40]),
       "mc_none": mc(.12, .09, .04, 8, [0, 1, 2, 3, 5, 10, 20, 40])}

# ---------------------------------------------------------------- detection / drift / density
det = pd.read_csv(A_OUT / "11_detection_robust_median.csv").to_dict("records")
drift = pd.read_csv(A_OUT / "50_drift_detectors.csv")
drift = drift[drift.th == 0.06].to_dict("records")
dens = pd.read_csv(A_OUT / "40_density_pr.csv")
dens = dens[dens.thr == 0.1].to_dict("records")

# ---------------------------------------------------------------- write
data = {
    "meta": {"dataset": "Europress SMART Material Value Engine v1.0.1 (competition/public, synthetic)", "window": ["2025-10-01", "2026-08-01"],
             "built": pd.Timestamp.now().strftime("%Y-%m-%d"), "d0": "2025-10-01", "sigma_dev_rel": SIGMA_DEV_REL, "sigma_dev_kg": SIGMA_DEV_KG,
             "hauler": HAULER, "causes": CAUSE_KEY, "pm": PM, "notes": notes},
    "fleet": fleet, "devcols": DEV_COLS, "devices": dev_rows, "vehicles": vehicles, "lifts": lifts_col,
    "causes": causes, "heroes": heroes, "rule_r1": rule_r1, "pof": pof, "ctr142": ctr142, "props": props, "sim": sim,
    "detect": det, "drift": drift, "density": dens,
}
txt = json.dumps(data, separators=(",", ":"), ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))
(HERE / "data.json").write_text(txt)
print(f"data.json {len(txt)/1024:.0f} KB; notes: {notes}")
print("fleet within band", fleet["pairs_within"], "/", fleet["pairs"], "| R1", rule_r1, "| tiers", fleet["tier_counts"])
print("vehicles", len(veh), "abs>=200", causes["vehicles_abs_ge200"], "| says-no", heroes["NO"]["collection_id"], pick["diff"], pick.band_kg)
for p in props:
    print(p["id"], p["action"], p["value"])

idx = HERE / "index.html"
if idx.exists():
    html = idx.read_text()
    new = re.sub(r'(<script id="data" type="application/json">)(.*?)(</script>)', lambda m: m.group(1) + txt.replace("</", "<\\/") + m.group(3), html, count=1, flags=re.S)
    idx.write_text(new)
    print("inlined into index.html", len(new) // 1024, "KB")
