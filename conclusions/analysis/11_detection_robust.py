"""UC1(d) robust aggregation: per device-month/quarter MEDIAN of per-lift ratios ticket/device (observable filters only: single load,
weighed tare, ticket net > 500 kg, no driver-reported side waste). No labels used. Synthetic data."""
import json
from ec_common import *
p = pd.read_parquet(OUT / "01_pairs_eur.parquet")
ce = rd("operations/collection_events.parquet")[["collection_id", "driver_reported_side_waste"]]
p = p.merge(ce, on="collection_id", how="left")
c = p[(p.loads_on_vehicle == 1) & (p.tare_method == "WEIGHED") & (p.wb_kg > 500) & ~p.driver_reported_side_waste.fillna(False).astype(bool)].copy()
c["r"] = c.wb_kg / c.dev_kg - 1
c["month"] = pd.to_datetime(c.service_date).dt.to_period("M"); c["q"] = pd.to_datetime(c.service_date).dt.to_period("Q")
c = c.replace([np.inf, -np.inf], np.nan).dropna(subset=["r"])
rows = []
for lvl, key in [("per_lift", None), ("device_month", "month"), ("device_quarter", "q"), ("device_window_10m", "all")]:
    if key is None:
        g = c[["r"]].assign(n=1)
    elif key == "all":
        g = c.groupby("device_id").agg(r=("r", "median"), n=("r", "size"))
    else:
        g = c.groupby(["device_id", key]).agg(r=("r", "median"), n=("r", "size"))
    tau = g.r.quantile(.975)
    row = {"level": lvl, "units": len(g), "median_lifts": float(g.n.median()), "robust_sd_pct": round(100 * (g.r.quantile(.75) - g.r.quantile(.25)) / 1.349, 2),
           "tau_pct(2.5%FA)": round(100 * tau, 2)}
    for X in (.03, .05, .10):
        row[f"detect_+{int(X*100)}pct"] = round(float((((1 + X) * (1 + g.r) - 1) > tau).mean()), 3)
    rows.append(row)
out = pd.DataFrame(rows); print(out.to_string(index=False)); out.to_csv(OUT2 / "11_detection_robust_median.csv", index=False)
print("pairs used", len(c), "devices", c.device_id.nunique())
