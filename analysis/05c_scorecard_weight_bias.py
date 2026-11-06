"""Operator weight bias (operator allocated net vs TRUE mass): naive device-vs-ticket estimate (as baseline B5) vs cause-adjusted estimate vs truth (labels_dev/operator_scorecard.weight_bias_pct)."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
sc = rd("labels_dev/operator_scorecard.parquet"); sc = sc[sc.n_completed_lifts >= 10]
df = lifts(); sites = rd("reference/sites.parquet")[["site_id", "region_code"]]
d = df[df.status.isin(LIFT) & df.ticket_id.notna() & df.device_estimated_collected_kg.notna() & (df.device_estimated_collected_kg > 50)].merge(sites, on="site_id")
d["month"] = d.scheduled_at.dt.tz_convert(TZ).dt.strftime("%Y-%m")
KEY = ["operator_id", "region_code", "month"]
lab = labels(); wd = lab[lab.label_family == "WEIGHT_DISCREPANCY"].set_index("entity_id").explanation_code
d["cause"] = d.collection_id.map(wd)
def bias(g):
    return 100 * (g.allocated_net_kg.sum() - g.device_estimated_collected_kg.sum()) / g.device_estimated_collected_kg.sum()
naive = d.groupby(KEY).apply(bias).rename("naive")
# transparent cause-adjusted estimate: drop lifts a customer can explain from the TICKET alone (combined load, driver-reported side waste); keep everything else
adj_d = d[(d.loads_on_vehicle == 1) & (d.driver_reported_side_waste != True)]
adj = adj_d.groupby(KEY).apply(bias).rename("adjusted")
# + robust: median ratio instead of ratio of sums (limits the leverage of single big deviations)
adj_med = adj_d.groupby(KEY).apply(lambda g: 100 * float(np.median((g.allocated_net_kg - g.device_estimated_collected_kg) / g.device_estimated_collected_kg))).rename("adjusted_median")
t = sc.set_index(KEY).weight_bias_pct.rename("truth")
x = pd.concat([t, naive, adj, adj_med], axis=1, join="inner").dropna()
print("operator x region x month rows with >=10 lifts:", len(x))
for c in ("naive", "adjusted", "adjusted_median"):
    print(f"{c:16s} MAE vs truth {np.abs(x[c] - x.truth).mean():.2f} pp ; bias {np.mean(x[c] - x.truth):+.2f} pp ; rank corr {x[c].corr(x.truth, method='spearman'):.3f}")
print("truth: mean %.2f pp, sd %.2f pp" % (x.truth.mean(), x.truth.std()))
po = pd.concat([x.groupby(level=0)[["truth", "naive", "adjusted", "adjusted_median"]].mean()], axis=1)
print("\nby operator (mean over months), pp:"); print(po.round(2))
# naive: how many operator-region-months would be flagged 'operator over-weighs by >3.3 %' while truth is within +-3.3 %
fp = ((x.naive.abs() > 3.3) & (x.truth.abs() <= 3.3)).mean(); fp2 = ((x.adjusted_median.abs() > 3.3) & (x.truth.abs() <= 3.3)).mean()
print("share of rows wrongly flagged (|bias|>3.3%% while truth within 3.3%%): naive %.3f ; adjusted %.3f ; truth beyond 3.3%%: %.3f" % (fp, fp2, (x.truth.abs() > 3.3).mean()))
x.round(3).to_csv(OUT / "06_weight_bias_naive_vs_adjusted.csv")
