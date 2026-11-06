"""(7) Value-vs-accuracy curve linking Part 1 (sigma of the weighing concept) to Part 2 (EUR / detection quality).
sigma = relative 1-sd of a lift's device mass (% of load) with an absolute floor of 15 kg, as in examples/weighing_accuracy_value.py.
Fixed seed.  Run after 03 (needs 04_lifts_H.parquet) and the 05b sim runs (for the C2 column)."""
import sys, json; sys.path.insert(0, "/home/hackathon/soome_hackathon_2026/analysis")
from common import *
from scipy.stats import norm
rng = np.random.default_rng(SEED)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
SIG = [0.5, 1, 1.5, 3, 5, 10]
WB = 12.0              # weighbridge sigma kg (assumptions.yaml)
FLOOR = 15.0
lab = labels(); df = lifts()
wd = lab[lab.label_family == "WEIGHT_DISCREPANCY"].set_index("entity_id")
L = df[df.status.isin(LIFT) & df.ticket_id.notna() & df.eval_at.notna()].copy()
L["wd"] = L.collection_id.map(wd.explanation_code)
clean = L[L.wd.isna() & (L.loads_on_vehicle == 1) & (L.driver_reported_side_waste != True) & (L.allocated_net_kg > 100)]
m = clean.allocated_net_kg.to_numpy(float)
print("reference loads (clean single-load tickets, unlabelled):", len(m), " median load kg:", np.median(m))

# ---- (a) EUR/t error and +100 kg target, as in the example script, plus within-5/10 %
rows = []
for s in SIG:
    sd = np.maximum(FLOOR, s / 100 * m)
    dev = m + rng.normal(0, 1, len(m)) * sd
    err = np.abs(m / np.clip(dev, 1, None) - 1)
    band = (m >= 2500) & (m <= 3500)
    rows.append({"sigma_pct": s, "within_100kg_2.5-3.5t": float((np.abs(dev - m)[band] <= 100).mean()), "eurt_median_err_pct": 100 * float(np.median(err)),
                 "eurt_p95_err_pct": 100 * float(np.quantile(err, .95)), "eurt_within_5pct": float((err <= .05).mean()), "eurt_within_10pct": float((err <= .10).mean())})
A = pd.DataFrame(rows).set_index("sigma_pct"); print("\n(a) EUR/t reporting accuracy"); print(A.round(3))

# ---- (b) tonnage-overbilling detection on the OBSERVED mismatch lines (8-25 %, mean +16 %) and generic +5/+10/+16/+25 %
wbm = pd.read_csv(OUT / "02_weight_basis_mismatch_lines.csv")
wbm = wbm[wbm.ref_qty.notna()]
mref = (wbm.ref_qty * 1000).to_numpy(float); minv = (wbm.quantity * 1000).to_numpy(float); val = wbm.value_at_stake_eur.to_numpy(float)
K = 2.0
rows = []
for s in SIG:
    sd = np.maximum(FLOOR, s / 100 * mref); sdt = np.sqrt(sd ** 2 + WB ** 2)
    p = norm.cdf(((minv - mref) - K * sdt) / sd)                    # P(invoice - device > K * sigma_tot)
    sdm = np.maximum(FLOOR, s / 100 * m); sdtm = np.sqrt(sdm ** 2 + WB ** 2)
    fa = norm.cdf(-K * sdtm / sdm)                                  # false alarm on a correct invoice
    out = {"sigma_pct": s, "false_alarm_rate": float(fa.mean()), "observed_lines_detected_share": float(p.mean()),
           "observed_overcharge_eur_detected(of %.0f)" % val[val > 0].sum(): float((p * np.clip(val, 0, None)).sum())}
    for x in (5, 10, 16, 25):
        sdx = np.maximum(FLOOR, s / 100 * m); sdtx = np.sqrt(sdx ** 2 + WB ** 2)
        out[f"detect_+{x}pct"] = float(norm.cdf((x / 100 * m - K * sdtx) / sdx).mean())
    rows.append(out)
B = pd.DataFrame(rows).set_index("sigma_pct"); print("\n(b) tonnage-overbilling detection with device weight (flag if invoice - device > 2 sigma_tot)"); print(B.round(3))

# ---- (c) device-vs-ticket anomaly detection (tare error + sensor drift = actionable) with extra device noise on the observed gap
pairs = L[L.device_estimated_collected_kg.notna()].copy()
pairs["rel"] = (pairs.device_estimated_collected_kg - pairs.allocated_net_kg) / pairs.allocated_net_kg.where(pairs.allocated_net_kg > 0)
pairs["diff"] = pairs.device_estimated_collected_kg - pairs.allocated_net_kg
act = pairs.wd.isin(["WEIGHBRIDGE_TARE_ERROR", "DEVICE_SENSOR_DRIFT", "DEVICE_SENSOR_DEGRADED", "DEVICE_SENSOR_CALIBRATION_GAIN"])
expl = pairs.wd.isin(["SIDE_WASTE_ON_SAME_TRUCK", "COMBINED_LOAD_ALLOCATION", "MEASUREMENT_NOISE_OR_TIMING"])
single = (pairs.loads_on_vehicle == 1) & (pairs.driver_reported_side_waste != True)
cl = pairs[pairs.wd.isna() & single & (pairs.allocated_net_kg >= 1500)]
s0 = 1.4826 * float((cl.rel - cl.rel.median()).abs().median())     # observed device-vs-ticket relative noise on clean mid/large loads
print("\nobserved relative noise of (device - ticket)/ticket on clean loads >=1.5 t: robust sd = %.2f %% (current device concept ~1.5 %% per reading)" % (100 * s0))
rows = []
for s in SIG:
    extra = np.sqrt(max(0.0, (s / 100) ** 2 - 0.015 ** 2 * 1.0)) if s > 1.5 else 0.0
    # extra noise relative to the load, on top of what is already in the data (sigma>1.5 %); sigma<=1.5 % cannot be emulated from the observed gaps -> uses observed
    rel_new = pairs.rel + rng.normal(0, 1, len(pairs)) * extra
    diff_new = pairs["diff"] + rng.normal(0, 1, len(pairs)) * extra * pairs.allocated_net_kg
    flag = (rel_new.abs() > .10) & (diff_new.abs() > 100) & single
    rows.append({"sigma_pct": s, "emulated": "observed" if s <= 1.5 else "observed+noise", "recall_actionable(tare+drift)": float((flag & act).sum() / act.sum()),
                 "precision_actionable": float((flag & act).sum() / max(1, flag.sum())), "flags_per_1000_clean_lifts": float(1000 * (flag & pairs.wd.isna()).sum() / (pairs.wd.isna().sum())),
                 "flag_share_of_explained(side waste/combined)": float((flag & expl).sum() / max(1, expl.sum()))})
C = pd.DataFrame(rows).set_index("sigma_pct"); print("\n(c) device-vs-ticket anomaly flag (|rel|>10% & |diff|>100 kg, single load) vs sigma"); print(C.round(3))

# ---- (d) S40 false-high fill detection (fill>=80 & mass-implied fill<50) vs mass noise
H = pd.read_parquet(OUT / "04_lifts_H.parquet")
rows = []
for s in SIG + [20, 30]:
    # mass_fill is already measured with ~1.5 % noise; add relative noise sqrt(s^2 - 1.5^2)
    extra = np.sqrt(max(0.0, (s / 100) ** 2 - 0.015 ** 2))
    mf = H.mass_fill * (1 + rng.normal(0, 1, len(H)) * extra)
    sig = (H.fill >= 80) & (mf < 50)
    y = H.cat == "FILL_SENSOR_FALSE_HIGH"
    rows.append({"sigma_pct": s, "S40_recall": float((sig & y).sum() / y.sum()), "S40_precision": float((sig & y).sum() / max(1, sig.sum())), "false_flags_per_1000_other_lifts": float(1000 * (sig & ~y).sum() / (~y).sum())})
D = pd.DataFrame(rows).set_index("sigma_pct"); print("\n(d) S40 (fill sensor false-high) lift-level signature vs mass accuracy"); print(D.round(3))
# order-time guard
o2 = pd.read_parquet(OUT / "04_orders_o2.parquet")
rows = []
for s in SIG + [20, 30]:
    extra = np.sqrt(max(0.0, (s / 100) ** 2 - 0.015 ** 2))
    mf = o2.mf_at_order * (1 + rng.normal(0, 1, len(o2)) * extra)
    g = (o2.fill_at_order >= 80) & (mf < 50)
    y = o2.cat == "FILL_SENSOR_FALSE_HIGH"
    rows.append({"sigma_pct": s, "orders_S40_recall": float((g & y).sum() / y.sum()), "eur_caught": float(o2.value_at_stake_eur[g & y].sum()), "false_blocks_per_1000_normal_orders": float(1000 * (g & ~y).sum() / (~y).sum())})
D2 = pd.DataFrame(rows).set_index("sigma_pct"); print("\n(d2) order-time guard vs sigma"); print(D2.round(3))

# ---- (e) C2 value captured (from 05b sim runs) 
rows = []
def cap(mode, key=None):
    f = OUT / f"05b_c2_ablation_{mode}.json"
    if not f.exists():
        return None
    sc = json.load(open(f))["score"]
    return {"mean_regret_eur": sc["mean_regret_eur"], "value_capture_share": sc["value_capture_share"]}
for name, mode in [("no mass source at all", "none"), ("invoice tonnage only (no tickets, no device)", "no_weight"), ("tickets+invoice, no device", "no_device"), ("default B1 chain (ticket>invoice>device)", "default"),
                   ("device (real, as simulated), nothing else", "device_only")] + [(f"hypothetical device sigma={s}%", f"sim_{s}") for s in SIG] + [("oracle billing mass", "oracle")]:
    c = cap(mode)
    if c:
        rows.append({"mass source": name, **c})
E = pd.DataFrame(rows); print("\n(e) Task C2 (dev, 207 contracts): value captured vs mass source"); print(E.round(4).to_string(index=False))
A.round(4).to_csv(OUT / "07_a_eurt.csv"); B.round(4).to_csv(OUT / "07_b_overbilling.csv"); C.round(4).to_csv(OUT / "07_c_anomaly.csv"); D.round(4).to_csv(OUT / "07_d_s40.csv"); D2.round(4).to_csv(OUT / "07_d2_guard.csv"); E.round(4).to_csv(OUT / "07_e_c2.csv", index=False)
