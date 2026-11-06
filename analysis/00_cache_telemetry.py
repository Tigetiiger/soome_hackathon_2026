"""Deduplicate hourly telemetry (by message_id, first received) and cache the columns the analyses need."""
import sys; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
import duckdb
con = duckdb.connect(); con.execute("SET memory_limit='3GB'")
q = f"""SELECT device_id, measured_at, fill_pct, mass_kg, mass_uncertainty_kg, quality_flag, sensor_status, operational_state, compaction_cycles, press_load_index FROM (
  SELECT *, row_number() OVER (PARTITION BY message_id ORDER BY received_at, delivery_id) rn FROM read_parquet('{PUB}/telemetry/telemetry_hourly/*/*.parquet')) WHERE rn=1"""
t = con.sql(q).df()
t["measured_at"] = pd.to_datetime(t.measured_at, utc=True)
t = t.sort_values(["device_id", "measured_at"]).reset_index(drop=True)
t.to_parquet(OUT / "telemetry_dedup.parquet")
print(t.shape, t.quality_flag.value_counts().to_dict())
