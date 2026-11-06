"""Pick hero-story candidates with full traces (job ref -> ticket -> contract version -> invoice lines -> EUR/t)."""
from ec_common import *
lab = labels(); df = lifts(); dv = device_segments()
il = rd("finance/invoice_lines.parquet"); inv = rd("finance/invoices.parquet"); cv = rd("reference/contract_versions.parquet")
ref = rd("labels_dev/reference_economics.parquet"); rcl = rd("labels_dev/reference_charge_lines.parquet")
# H1 weight basis mismatch with device & ticket agreeing
w = pd.read_csv(OUT / "02_weight_basis_mismatch_lines.csv")
w = w[w.device_estimated_collected_kg.notna() & w.allocated_net_kg.notna()]
w["dev_vs_tk"] = w.device_estimated_collected_kg / w.allocated_net_kg - 1
print(w.sort_values("value_at_stake_eur", ascending=False)[["invoice_line_id", "operator_job_ref", "line_type", "quantity", "allocated_net_kg", "device_estimated_collected_kg", "dev_vs_tk", "value_at_stake_eur", "contract_id", "operator_id"]].head(8).to_string())
# H2 stale tare lifts on per-tonne contracts
p = pd.read_parquet(OUT / "01_pairs_eur.parquet")
p = p.merge(df[["collection_id", "vehicle_id", "gross_kg", "tare_kg", "tare_method", "operator_job_ref", "ticket_id"]], on="collection_id", how="left", suffixes=("", "_x"))
t = p[(p.cause_g == "stale/wrong tare (operator side)")]
print(t.groupby("vehicle_id").agg(n=("collection_id", "size"), med_rel=("rel", "median"), eur=("delta_eur", "sum")).sort_values("eur").head(5))
print(t.groupby("vehicle_id").agg(n=("collection_id", "size"), med_rel=("rel", "median"), eur=("delta_eur", "sum")).sort_values("eur").tail(5))
print(t.sort_values("delta_eur", key=abs, ascending=False)[["collection_id", "device_id", "vehicle_id", "operator_job_ref", "ticket_id", "gross_kg", "tare_kg", "wb_kg", "dev_kg", "rel", "delta_eur", "pricing_model"]].head(8).to_string())
# vehicle-level stored tare profile
wb = rd("operations/weighbridge_tickets.parquet")
print(wb[wb.vehicle_id.isin(["OP-E-V06", "OP-A-V12"])].groupby(["vehicle_id", "tare_method"]).tare_kg.describe())
# H3 FIXED device with most over-servicing EUR
pl = lab[(lab.label_family == "PREMATURE_UNJUSTIFIED") & lab.is_actionable]
top = pl.groupby("device_id").agg(n=("entity_id", "size"), eur=("value_at_stake_eur", "sum")).join(dv.set_index("device_id")[["collection_policy", "material_stream", "fixed_schedule_per_week", "operator_id", "customer_id", "container_volume_m3", "contract_id", "dev_years"]])
print(top[top.collection_policy != "ON_CALL"].sort_values("eur", ascending=False).head(8))
