"""DuckDB SQL cross-checks of the headline numbers (same figures as the pandas scripts)."""
import duckdb
P = "/home/hackathon/europress_data/Europress_SMART_Material_Value_Engine_v1.0.1/data/competition/public"
con = duckdb.connect()
for t, p in {"ce": "operations/collection_events.parquet", "wb": "operations/weighbridge_tickets.parquet", "lab": "labels_dev/anomaly_labels.parquet",
             "ref": "labels_dev/reference_economics.parquet", "dev": "reference/devices.parquet"}.items():
    con.execute(f"CREATE VIEW {t} AS SELECT * FROM read_parquet('{P}/{p}')")
print("-- (1) device vs weighbridge disagreement, label window (lifts with reference economics), shares of paired lifts")
print(con.sql("""
WITH w AS (SELECT DISTINCT ON (operator_job_ref) operator_job_ref, allocated_net_kg FROM wb ORDER BY operator_job_ref, ticket_id),
p AS (SELECT c.collection_id, c.device_estimated_collected_kg d, w.allocated_net_kg n,
             (c.device_estimated_collected_kg - w.allocated_net_kg) / w.allocated_net_kg AS rel
      FROM ce c JOIN ref r USING (collection_id) JOIN w USING (operator_job_ref)
      WHERE c.status IN ('COMPLETED','PARTIAL') AND c.device_estimated_collected_kg IS NOT NULL AND w.allocated_net_kg > 0)
SELECT count(*) pairs, round(avg((abs(rel) > 0.033)::INT),4) gt_3_3pct, round(avg((abs(rel) > 0.10)::INT),4) gt_10pct,
       round(avg((abs(d - n) > 100)::INT),4) gt_100kg FROM p""").df().to_string(index=False))
print("\n-- (1b) cause split of WEIGHT_DISCREPANCY labels (|diff|>100 kg and >10 %)")
print(con.sql("""SELECT explanation_code, is_actionable, count(*) n FROM lab WHERE label_family='WEIGHT_DISCREPANCY' GROUP BY 1,2 ORDER BY n DESC""").df().to_string(index=False))
print("\n-- (3) EUR/t mass source at extraction (lifts in label window)")
print(con.sql("""SELECT observable_mass_source, count(*) lifts, round(count(*)*1.0/sum(count(*)) OVER (),4) share, round(sum(collection_cost_eur),0) collection_cost_eur
FROM ref WHERE status IN ('COMPLETED','PARTIAL') GROUP BY 1 ORDER BY 2 DESC""").df().to_string(index=False))
print("\n-- (3b) by operator: share of lifts with a published ticket / invoice-tonnage only / device-only")
print(con.sql("""SELECT c.operator_id, count(*) lifts, round(avg((r.observable_mass_source='WEIGHBRIDGE_PUBLISHED')::INT),3) ticket,
 round(avg((r.observable_mass_source='INVOICE_TONNAGE')::INT),3) invoice_only, round(avg((r.observable_mass_source IN ('DEVICE_ESTIMATE_ONLY','NONE'))::INT),3) eurt_null
FROM ref r JOIN ce c USING (collection_id) WHERE r.status IN ('COMPLETED','PARTIAL') GROUP BY 1 ORDER BY 1""").df().to_string(index=False))
print("\n-- (2) invoice-line discrepancy EUR by family (value_at_stake_eur = billed - expected, + = overcharge)")
print(con.sql("""SELECT label_family, count(*) n, round(sum(value_at_stake_eur),0) net_eur, round(sum(greatest(value_at_stake_eur,0)),0) overcharge_eur
FROM lab WHERE label_family IN ('DUPLICATE_LINE','UNMATCHED_LINE','OUTDATED_TARIFF','WRONG_SURCHARGE','WEIGHT_BASIS_MISMATCH','MISSING_LINE','UNINVOICED_COLLECTION') GROUP BY 1 ORDER BY 3 DESC""").df().to_string(index=False))
print("\n-- (4) unnecessary-lift pools (illustrative avoidable logistics cost)")
print(con.sql("""SELECT explanation_code, count(*) lifts, round(sum(value_at_stake_eur),0) eur FROM lab WHERE label_family='PREMATURE_UNJUSTIFIED' AND is_actionable GROUP BY 1 ORDER BY 3 DESC""").df().to_string(index=False))
print("\n-- mass-linked share of the correct charges")
print(con.sql(f"""SELECT sum(abs(amount_eur)) FILTER (WHERE line_type IN ('HAUL_PER_TONNE','PROCESSING','REJECTION_REPROCESSING','MIN_CHARGE_TOPUP','MATERIAL_CREDIT')) / sum(abs(amount_eur)) AS mass_linked_share,
 sum(abs(amount_eur)) FILTER (WHERE line_type IN ('HAUL_PER_TONNE','PROCESSING','REJECTION_REPROCESSING','MIN_CHARGE_TOPUP','MATERIAL_CREDIT')) mass_linked_gross_eur
 FROM read_parquet('{P}/labels_dev/reference_charge_lines.parquet')""").df().to_string(index=False))
