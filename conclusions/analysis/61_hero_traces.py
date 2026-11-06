"""End-to-end traces for the hero stories (printed + saved as CSV)."""
from ec_common import *
lab = labels(); df = lifts(); dv = device_segments().set_index("device_id")
il = rd("finance/invoice_lines.parquet"); inv = rd("finance/invoices.parquet"); cv = rd("reference/contract_versions.parquet").set_index("contract_version_id")
ref = rd("labels_dev/reference_economics.parquet").set_index("collection_id"); rcl = rd("labels_dev/reference_charge_lines.parquet")
FEES = ["pricing_model", "lift_fee_cents", "haul_fee_cents_per_t", "processing_fee_cents_per_t", "min_charge_cents", "credit_share_bp", "default_weight_kg"]
def trace(job):
    L = df[df.operator_job_ref == job].iloc[0]
    print(f"\n#### job {job} | {L.collection_id} | device {L.device_id} ({dv.loc[L.device_id, 'material_stream']}, {dv.loc[L.device_id, 'collection_policy']}, {L.operator_id}) | date {L.service_date}")
    print(f" device mass before/after {L.device_mass_kg_before}/{L.device_mass_kg_after} -> est {L.device_estimated_collected_kg} kg; fill before {L.device_fill_pct_before}")
    print(f" ticket {L.ticket_id} vehicle {L.vehicle_id} gross {L.gross_kg} tare {L.tare_kg} ({L.tare_method}) net {L.net_kg} alloc {L.allocated_net_kg} loads {L.loads_on_vehicle}; grade {L.grade}")
    r = ref.loc[L.collection_id]; print(f" contract version {r.contract_version_id}: " + ", ".join(f"{k}={cv.loc[r.contract_version_id, k]}" for k in FEES))
    print(f" reference: billing mass {r.billing_mass_kg} ({r.billing_mass_basis}) expected invoice EUR {r.expected_invoice_amount_eur} total cost EUR/t {r.total_cost_eur_per_t}")
    x = il[il.operator_job_ref == job].merge(inv[["invoice_id", "contract_id", "issued_at"]], on="invoice_id")
    print(x[["invoice_line_id", "line_type", "quantity", "unit", "unit_price_eur", "amount_eur"]].to_string(index=False))
    print(" invoice total for job EUR", round(x.amount_eur.sum(), 2), "| reference lines:", rcl[rcl.collection_id == L.collection_id][["line_type", "quantity", "amount_eur"]].values.tolist())
    print(" labels:", lab[lab.entity_id.isin([L.collection_id] + x.invoice_line_id.tolist())][["entity_id", "label_family", "explanation_code", "value_at_stake_eur", "severity"]].values.tolist())
# H1 invoice tonnage inflated vs ticket + device that agree
for j in ["OP-E-003920032", "OP-B-000100042"]:
    trace(j)
# H2 vehicle stored tare: OP-E-V06 (stored tare too low) vs OP-A-V12 (stored tare too high)
for veh in ["OP-E-V06", "OP-A-V12"]:
    v = df[(df.vehicle_id == veh) & (df.tare_method == "STORED") & df.device_estimated_collected_kg.notna() & (df.loads_on_vehicle == 1) & (df.allocated_net_kg > 1000)].copy()
    v["rel"] = v.device_estimated_collected_kg / v.allocated_net_kg - 1
    v["pm"] = v.collection_id.map(ref.contract_version_id).map(cv.pricing_model)
    print(f"\n{veh}: stored-tare single loads n={len(v)}, median device/ticket-1 {v.rel.median():.3f}; pricing mix {v.pm.value_counts().to_dict()}")
    pick = v[v.pm.isin(["PER_TONNE", "HYBRID"]) & ~v.driver_reported_side_waste.fillna(False).astype(bool)].sort_values("allocated_net_kg").iloc[len(v) // 4 if len(v) > 8 else 0]
    trace(pick.operator_job_ref)
# H3 Poland-like fixed schedule, operator does not share tickets
d = "CMP-00430"; print("\n####", d, dv.loc[d, ["customer_id", "collection_policy", "fixed_schedule_per_week", "material_stream", "container_volume_m3", "operator_id", "contract_id", "has_weight_measurement"]].to_dict())
Lx = df[(df.device_id == d) & df.status.isin(LIFT) & df.eval_at.notna()]
pl = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & (lab.device_id == d)]
print(" lifts in window", len(Lx), "unjustified", len(pl), "EUR", round(pl.value_at_stake_eur.sum(), 2), "| median fill before", Lx.device_fill_pct_before.median(), "median device kg", Lx.device_estimated_collected_kg.median(),
      "| ticket share", Lx.ticket_id.notna().mean(), "| obs mass source", ref.loc[Lx.collection_id].observable_mass_source.value_counts().to_dict())
print(" median cost per lift EUR", ref.loc[Lx.collection_id].total_customer_cost_eur.median(), "| EUR/t median", ref.loc[Lx.collection_id].total_cost_eur_per_t.median())
dc = rd("benchmark/decision_cases.parquet"); dt = rd("labels_dev/decision_truth.parquet"); do = rd("labels_dev/decision_outcomes.parquet")
c = dc[dc.device_id == d].merge(dt, on=["case_id", "split"])
print(c[["case_id", "decision_at", "horizon_days", "best_action", "best_benefit_cents", "acceptable_actions"]].to_string(index=False))
print(do[do.case_id == c.case_id.iloc[0]][["action", "benefit_vs_no_action_cents", "permissible", "n_completed_lifts", "overflow_open_hours", "hidden_cost_trap"]].to_string(index=False))
ex = pl.sort_values("value_at_stake_eur").iloc[len(pl) // 2]
trace(df[df.collection_id == ex.entity_id].operator_job_ref.iloc[0])
# H4 contract action where device weight is the only mass
g = pd.read_csv(OUT2 / "30a_contract_eurt_vs_peer.csv")
oa = rd("labels_dev/operator_action_values.parquet").merge(rd("benchmark/operator_action_cases.parquet")[["case_id", "contract_id"]], on="case_id")
o = oa[oa.positive].merge(g, on="contract_id")
print(o[o.weight_needed == "device weight is the only mass"][["case_id", "contract_id", "device_id", "operator_id", "material_stream", "pricing_model", "action", "value_eur", "annual_contract_cost_eur", "best_alternative_operator", "net_cost_eur_t", "peer_med_eur_t", "gap_pct", "t", "lifts"]].sort_values("value_eur", ascending=False).head(8).to_string(index=False))
