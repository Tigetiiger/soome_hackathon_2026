"""Collects the headline numbers used in docs/agents/data-analyst.md from the saved outputs (no new modelling)."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
dy = device_years(); dyw = device_years(only_weighted=True)
df = lifts(); lab = labels()
L = df[df.status.isin(LIFT) & df.eval_at.notna()]
print("device-years all %.1f, weighted %.1f; label-window lifts %d" % (dy, dyw, len(L)))
ref = rd("labels_dev/reference_economics.parquet")
print("reference total customer cost (all events, label window): EUR %.0f ; collection cost EUR %.0f ; processing EUR %.0f ; credit EUR %.0f" %
      (ref.total_customer_cost_eur.sum(), ref.collection_cost_eur.sum(), ref.processing_cost_eur.sum(), ref.material_credit_eur.sum()))
print("lifts: with ticket %.3f ; with device est %.3f ; with at least one independent measure (ticket or device) %.3f ; neither %.4f" %
      (L.ticket_id.notna().mean(), L.device_estimated_collected_kg.notna().mean(), (L.ticket_id.notna() | L.device_estimated_collected_kg.notna()).mean(),
       (L.ticket_id.isna() & L.device_estimated_collected_kg.isna()).mean()))
inv_only = L[L.observable_mass_source == "INVOICE_TONNAGE"]
print("invoice-tonnage-only lifts %d: device est present %d (%.1f%% of all lifts become verifiable)" % (len(inv_only), inv_only.device_estimated_collected_kg.notna().sum(), 100 * inv_only.device_estimated_collected_kg.notna().sum() / len(L)))
# pricing model mix (weight-exposed share of contracts)
cv = rd("reference/contract_versions.parquet"); last = cv.sort_values("version_no").groupby("contract_id").tail(1)
print("pricing model mix (latest version):", last.pricing_model.value_counts(normalize=True).round(3).to_dict())
# S40/S39/S01 pools
pool = pd.read_csv(OUT / "04_premature_pool.csv", index_col=0); print(pool)
g = json.load(open(OUT / "04_order_guard.json")); print(g)
print("S40 guard EUR per weighted device-year: %.1f" % (g["order_guard_eur_caught"] / (330.9 * (6 / 10)) ))   # eval window is Feb-Jul (6 months) so scale to eval-window device-years
ev_dy = device_years(window=(pd.Timestamp("2026-02-01"), pd.Timestamp("2026-08-01")), only_weighted=True)
print("   eval window (Feb-Jul) weighted device-years %.1f -> EUR per weighted device-year %.1f (order guard, S40 only)" % (ev_dy, g["order_guard_eur_caught"] / ev_dy))
print("   all S40 orders EUR in eval window %.0f -> per weighted device-year %.1f" % (g["s40_orders_eur"], g["s40_orders_eur"] / ev_dy))
# C2 table
c2 = {m: json.load(open(OUT / f"05b_c2_ablation_{m}.json"))["score"] for m in ["none", "no_weight", "no_device", "default", "device_only", "oracle", "sim_0.5", "sim_1", "sim_1.5", "sim_3", "sim_5", "sim_10"]}
best = 220229.33
for m, sc in c2.items():
    print(f"C2 {m:12s} capture {sc['value_capture_share']:.4f} captured EUR {sc['value_captured_eur']:.0f} regret {sc['mean_regret_eur']:.1f}")
print("C2 per-contract-year increments (EUR/contract): device_only - no_weight = %.0f ; default - no_device = %.0f ; device_only - none = %.0f" %
      ((c2["device_only"]["value_captured_eur"] - c2["no_weight"]["value_captured_eur"]) / 207, (c2["default"]["value_captured_eur"] - c2["no_device"]["value_captured_eur"]) / 207,
       (c2["device_only"]["value_captured_eur"] - c2["none"]["value_captured_eur"]) / 207))
# baselines
b = json.load(open("/home/hackathon/soome_hackathon_2026/analysis/baseline_run/reports/baselines_competition.json"))
print(json.dumps({k: b[k] for k in ("task_A",)}, indent=1, default=str)[:900])
fam = b["task_B"]["B2_rules"]["validation"]
print({k: v for k, v in fam.items() if k in ("macro_f1", "macro_f1_detection_only", "value_weighted_recall", "explained_flagged_as_anomaly")})
for mname in ("B4_gradient_boosting", "hybrid_ml_plus_rules"):
    v = b["task_B"][mname]["validation"]; print(mname, {k: v[k] for k in v if k in ("macro_f1", "macro_f1_detection_only", "value_weighted_recall", "explained_flagged_as_anomaly")})
print(list(b["task_B"]["B2_rules"]["validation"].keys())[:30])
