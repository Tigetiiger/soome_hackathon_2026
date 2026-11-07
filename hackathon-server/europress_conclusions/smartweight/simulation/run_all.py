"""Run every SmartWeight experiment and write results/ (CSV, JSON, PNG).

    python run_all.py            # full run (~1-2 min)
    python run_all.py --quick    # fewer machines for a smoke test

All numbers produced here are SIMULATED under the assumptions in params.yaml.
They are not validated real-world performance.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

import estimators as E  # noqa: E402
import sensors as S  # noqa: E402
from metrics import breakdown, summarize  # noqa: E402
from world import build_world, load_params  # noqa: E402

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results"
MASS_SENSITIVE_EUR = 2765.0  # median EUR/device-year scaling with billed mass [measured: dataset_checks.json C8, synthetic, hypothetical tariffs]

COST_KEY = {
    "WB_TICKET_WEIGHED": "WEIGHBRIDGE", "WB_TICKET_MIXED_TARE": "WEIGHBRIDGE",
    "REF_CERT_LC4": "REF_CERT_LC4", "LC4_CHEAP": "LC4_CHEAP", "LC2_REAR_PINS": "LC2_REAR_PINS",
    "SG_BEND2": "SG_BEND2", "SG_BEND2_A5": "SG_BEND2", "SG_SHEAR4": "SG_SHEAR4",
    "HYD_LIFT_TRUCK": "HYD_LIFT_TRUCK", "FILL_D": "FILL_D", "FILL_D_A5": "FILL_D",
    "HYD_COMP_FW": "HYD_COMP_FW", "HYD_COMP_FW_A5": "HYD_COMP_FW",
    "HYD_COMP_OILT_A5": "HYD_COMP_FW_OILT", "CT_POWER_A5": "CT_POWER",
    "ML_GBM": "HYD_COMP_FW_OILT", "ML_GBM_A5": "HYD_COMP_FW_OILT",
    "HYBRID_A5": "HYD_COMP_FW_OILT",
}
# Is the estimator calibrated independently of the operator whose bill it checks?
INDEPENDENT = {k: not (k.endswith("_A5") or k.startswith("WB_")) for k in COST_KEY}


def compute(ev: pd.DataFrame, p: dict, seed: int, golden: np.ndarray, k: int, perturb: str | None = None) -> dict:
    rng = np.random.default_rng(seed)
    after = (ev["event_no"] >= k).to_numpy()
    f_obs = S.fill_obs(ev, p, rng)
    ticket = S.weighbridge_ticket(ev, p, rng, weighed_only=True)
    t_oil_obs = ev["t_oil"].to_numpy() + rng.normal(0, 0.5, len(ev))
    out = {"WB_TICKET_WEIGHED": ticket,
           "WB_TICKET_MIXED_TARE": S.weighbridge_ticket(ev, p, rng, weighed_only=False)}

    # A: direct gravitational sensing
    out["REF_CERT_LC4"] = S.load_cells_4(ev, p, rng, "cert")
    lc = S.load_cells_4(ev, p, rng, "cheap")
    if perturb == "cell_fail":
        dead = S.load_cells_4(ev, p, np.random.default_rng(seed + 1), "cheap", failed_cell=True)
        lc = np.where(after, dead, lc)
    if perturb == "cell_drift":
        lc = np.where(after, lc * (1 + 0.02 * S.support_shares(ev)[:, 0]), lc)
    out["LC4_CHEAP"] = lc
    out["LC2_REAR_PINS"] = S.load_cells_2_rear(ev, p, rng, f_obs)
    sg = S.strain(ev, p, rng, "bending_2")
    out["SG_BEND2"] = sg
    out["SG_BEND2_A5"], _ = E.anchor_calibrate(ev, sg, ticket, k)
    out["SG_SHEAR4"] = S.strain(ev, p, rng, "shear_4")
    # B: hooklift lift pressure (hauler's truck)
    out["HYD_LIFT_TRUCK"] = S.hooklift_pressure(ev, p, rng, f_obs)

    # C/D: indirect
    drift = np.where(after, 6.0, 0.0) if perturb == "pressure_drift" else 0.0
    p_bar = S.compaction_pressure(ev, p, rng, sensor_drift_bar=drift)
    out["FILL_D"] = E.fill_density(ev, p, f_obs)
    out["FILL_D_A5"], _ = E.anchor_calibrate(ev, out["FILL_D"], ticket, k)
    hc = E.compaction_inverse(ev, p, f_obs, p_bar, None)
    out["HYD_COMP_FW"] = hc
    out["HYD_COMP_FW_A5"], _ = E.anchor_calibrate(ev, hc, ticket, k)
    hct = E.compaction_inverse(ev, p, f_obs, p_bar, t_oil_obs)
    out["HYD_COMP_OILT_A5"], _ = E.anchor_calibrate(ev, hct, ticket, k)
    p_ct = S.pressure_from_current(ev, p, rng, p_bar)
    out["CT_POWER_A5"], _ = E.anchor_calibrate(ev, E.compaction_inverse(ev, p, f_obs, p_ct, t_oil_obs), ticket, k)

    # ML: trained on golden-cohort machines with true (reference-scale) mass, evaluated elsewhere
    X = E.ml_features(ev, f_obs, p_bar, t_oil_obs)
    ml = np.full(len(ev), np.nan)
    ml[~golden] = E.ml_fit_predict(X[golden], ev["m_true"].to_numpy()[golden], X[~golden], seed)
    ml[golden] = ev["m_true"].to_numpy()[golden]  # not evaluated
    out["ML_GBM"] = ml
    out["ML_GBM_A5"], _ = E.anchor_calibrate(ev, ml, ticket, k)

    # E: hybrid, inverse-variance fusion of the two anchored indirect estimators (sds from golden cohort)
    m_true = ev["m_true"].to_numpy()
    eval_g = golden & after
    sd_h = float(np.std(np.log(out["HYD_COMP_OILT_A5"][eval_g] / m_true[eval_g])))
    sd_f = float(np.std(np.log(out["FILL_D_A5"][eval_g] / m_true[eval_g])))
    out["HYBRID_A5"] = E.fuse([out["HYD_COMP_OILT_A5"], out["FILL_D_A5"]], [sd_h, sd_f])
    out["_ticket"] = ticket
    out["_hybrid_sd"] = (sd_h, sd_f)
    return out


def eval_mask(ev, golden, k):
    return (~golden) & (ev["event_no"] >= k).to_numpy() & (ev["m_true"] > 100).to_numpy()


def cost_table(costs: dict) -> pd.DataFrame:
    rows = []
    for key, c in costs["configs"].items():
        parts = ["hardware", "structure", "install", "calibration", "type_approval_amortised"]
        lo = sum(c[x][0] for x in parts)
        hi = sum(c[x][1] for x in parts)
        share = c.get("per_truck_shared_by", 1)
        rows.append({"cost_key": key, "label": c["label"], "capex_low": lo / share, "capex_high": hi / share,
                     "capex_mid": (lo + hi) / 2 / share, "annual_mid": sum(c["annual"]) / 2 / share,
                     "billing_grade_possible": c["billing_grade_possible"], "owner": c["owner"]})
    return pd.DataFrame(rows)


def core(ev, p, golden, k):
    est = compute(ev, p, p["seed"] + 11, golden, k)
    mask = eval_mask(ev, golden, k)
    truth = ev["m_true"].to_numpy()[mask]
    rows, by_mat, by_bin = [], [], []
    for name, e in est.items():
        if name.startswith("_"):
            continue
        s = summarize(e[mask], truth)
        rows.append({"config": name, **s})
        bm = breakdown(e[mask], ev[mask], "material"); bm.insert(0, "config", name); by_mat.append(bm)
        bb = breakdown(e[mask], ev[mask], "mass_bin"); bb.insert(0, "config", name); by_bin.append(bb)
        bc = breakdown(e[mask], ev[mask], "eq_class"); bc.insert(0, "config", name); by_mat.append(bc)
    return est, mask, pd.DataFrame(rows), pd.concat(by_mat), pd.concat(by_bin)


def stress(p, golden_fn, k):
    """Sensor failure / drift / changed material / changed machines."""
    rows = []
    base_w = build_world(p)
    golden = golden_fn(base_w)
    scen = {"baseline": (base_w, None), "pressure_drift_+6bar": (base_w, "pressure_drift"),
            "load_cell_failed_undetected": (base_w, "cell_fail"), "one_cell_gain_drift_2pct": (base_w, "cell_drift")}
    # material composition shift after calibration: site density +20 %
    p2 = copy.deepcopy(p)
    w_shift = build_world(p2)
    w_shift = w_shift.copy()
    later = w_shift["event_no"] >= k
    p_hi = copy.deepcopy(p)
    for m in p_hi["materials"].values():
        m["inf_factor"] *= 1.2
    w_hi = build_world(p_hi)
    w_shift.loc[later] = w_hi.loc[later]
    scen["material_mix_shift_+20pct_density"] = (w_shift, None)
    # wet season after calibration: every cardboard pickup wet
    p_wet = copy.deepcopy(p)
    p_wet["materials"]["cardboard"]["wet_prob"] = 1.0
    w_wet = build_world(p_wet)
    w2 = base_w.copy()
    w2.loc[later] = w_wet.loc[later]
    scen["wet_season_after_calibration"] = (w2, None)
    # unseen machine population: different press/friction (new seed + wider tolerances)
    p_new = copy.deepcopy(p)
    p_new["press"]["area_tol_cv"] = 0.05
    p_new["press"]["friction_cv"] = 0.30
    p_new["machines"]["site_density_cv"] = 0.25
    w_new = build_world(p_new, seed=p["seed"] + 99)
    scen["unseen_machine_population"] = (w_new, None)
    for sname, (w, pert) in scen.items():
        g = golden_fn(w)
        est = compute(w, p, p["seed"] + 11, g, k, pert)
        mask = eval_mask(w, g, k)
        truth = w["m_true"].to_numpy()[mask]
        for name, e in est.items():
            if name.startswith("_") or name.startswith("WB_"):
                continue
            s = summarize(e[mask], truth)
            rows.append({"scenario": sname, "config": name, "median_rel_ge1t": s["median_rel_ge1t"],
                         "P95_rel_ge1t": s["P95_rel_ge1t"], "within_5pct_ge1t": s["within_5pct_ge1t"],
                         "bias_kg": s["bias_kg"], "MAE_kg": s["MAE_kg"]})
    return pd.DataFrame(rows)


def heldout_material(ev, p, golden, k):
    """ML trained without plastics, evaluated on plastics; physics needs only the nominal plastic table."""
    rng = np.random.default_rng(p["seed"] + 5)
    f_obs = S.fill_obs(ev, p, rng)
    p_bar = S.compaction_pressure(ev, p, rng)
    t_oil = ev["t_oil"].to_numpy()
    X = E.ml_features(ev, f_obs, p_bar, t_oil)
    train = golden & (ev["material"] != "plastic").to_numpy()
    test = (~golden) & (ev["material"] == "plastic").to_numpy() & (ev["m_true"] > 100).to_numpy()
    X_noplastic = X.drop(columns=["mat_plastic"])
    ml = E.ml_fit_predict(X_noplastic[train], ev["m_true"].to_numpy()[train], X_noplastic[test])
    phys = E.compaction_inverse(ev, p, f_obs, p_bar, t_oil)[test]
    truth = ev["m_true"].to_numpy()[test]
    return pd.DataFrame([{"config": "ML_GBM_no_plastic_in_training", **summarize(ml, truth)},
                         {"config": "HYD_COMP_OILT_physics_uncalibrated", **summarize(phys, truth)}])


def ablation(ev, p, golden):
    """Effect of anchors k, oil-temperature probe, fill accuracy and pressure on the hybrid."""
    rows = []
    for k in (0, 1, 3, 5, 10):
        est = compute(ev, p, p["seed"] + 11, golden, k)
        mask = eval_mask(ev, golden, max(k, 10))  # same evaluation set for every k
        t = ev["m_true"].to_numpy()[mask]
        for name in ("FILL_D_A5", "HYD_COMP_FW_A5", "HYD_COMP_OILT_A5", "HYBRID_A5", "ML_GBM_A5", "SG_BEND2_A5"):
            s = summarize(est[name][mask], t)
            rows.append({"study": "anchors_k", "k": k, "config": name, "median_rel_ge1t": s["median_rel_ge1t"],
                         "P95_rel_ge1t": s["P95_rel_ge1t"], "within_5pct_ge1t": s["within_5pct_ge1t"]})
    # perfect fill sensor / perfect pressure: how much does each input limit the hybrid?
    for label, mod in (("fill_sensor_perfect", {"fill_sensor": {"sigma_pp": 0.0, "bias_sd_pp": 0.0, "gain_sd": 0.0}}),
                       ("pressure_noise_zero", {"press": {"plateau_noise_rel": 0.0}}),
                       ("no_moisture_variation", "dry")):
        p2 = copy.deepcopy(p)
        if mod == "dry":
            for m in p2["materials"].values():
                m["wet_prob"] = 0.0
                m["dry_gain"] = [0.0, 0.0]
        else:
            for sec, kv in mod.items():
                p2[sec].update(kv)
        w = build_world(p2)
        est = compute(w, p2, p["seed"] + 11, golden, 5)
        mask = eval_mask(w, golden, 5)
        t = w["m_true"].to_numpy()[mask]
        for name in ("FILL_D_A5", "HYD_COMP_OILT_A5", "HYBRID_A5"):
            s = summarize(est[name][mask], t)
            rows.append({"study": label, "k": 5, "config": name, "median_rel_ge1t": s["median_rel_ge1t"],
                         "P95_rel_ge1t": s["P95_rel_ge1t"], "within_5pct_ge1t": s["within_5pct_ge1t"]})
    return pd.DataFrame(rows)


def verification_power(ev, p, golden, k, est):
    """User goal (2026-11-07): verify the client is billed accurately.

    The operator's invoiced mass = its weighbridge ticket (mixed stored/weighed tare) x (1 + delta).
    Rule per machine: flag if the median of (invoiced - estimate)/estimate over the next N pickups exceeds a
    threshold set so that honest billing is flagged in <= 5 % of machine-windows.
    Mode 'from_start': the overbilling is already present in the anchor tickets (absorbed by ticket calibration).
    Mode 'step': overbilling starts after calibration.
    """
    rng = np.random.default_rng(p["seed"] + 21)
    honest = S.weighbridge_ticket(ev, p, rng, weighed_only=False)
    rows = []
    mid = ev["machine_id"].to_numpy()
    for name in ("REF_CERT_LC4", "LC4_CHEAP", "SG_SHEAR4", "SG_BEND2_A5", "HYD_COMP_OILT_A5", "HYBRID_A5",
                 "FILL_D_A5", "FILL_D", "LC2_REAR_PINS"):
        e = est[name]
        for N in (1, 6, 12):
            for mode in ("step", "from_start"):
                for delta in (0.0, 0.02, 0.03, 0.05, 0.10):
                    inv = honest * (1 + delta)
                    e_used = e
                    if mode == "from_start" and not INDEPENDENT.get(name, True) and delta > 0:
                        e_used = e * (1 + delta)  # calibration on biased tickets absorbs the bias
                    rel = (inv - e_used) / np.clip(e_used, 50, None)
                    df = pd.DataFrame({"m": mid, "n": ev["event_no"].to_numpy(), "rel": rel,
                                       "ok": (~golden) & (ev["event_no"] >= k).to_numpy() & (ev["m_true"] > 500).to_numpy()})
                    df = df[df["ok"]]
                    df["win"] = (df["n"] - k) // N
                    stat = df.groupby(["m", "win"])["rel"].median()
                    rows.append({"config": name, "N_lifts": N, "mode": mode, "delta": delta, "stat": stat.to_numpy()})
    out = []
    thr = {}
    for r in rows:
        if r["delta"] == 0.0:
            thr[(r["config"], r["N_lifts"], r["mode"])] = np.percentile(r["stat"], 95)
    for r in rows:
        t = thr[(r["config"], r["N_lifts"], r["mode"])]
        out.append({"config": r["config"], "N_lifts": r["N_lifts"], "mode": r["mode"], "overbilling": r["delta"],
                    "threshold": round(float(t), 4), "detection_rate": round(float((r["stat"] > t).mean()), 4)})
    return pd.DataFrame(out)


def plots(core_df, pareto_df, by_bin, ver, est, ev, mask):
    RES.mkdir(exist_ok=True, parents=True)
    # 1. cost vs accuracy (Pareto)
    fig, ax = plt.subplots(figsize=(9, 6))
    d = pareto_df[~pareto_df["config"].str.startswith("WB_")]
    ax.scatter(d["capex_mid"] + 1, d["P95_rel_ge1t"] * 100, c=np.where(d["pareto"], "C3", "C0"))
    for _, r in d.iterrows():
        ax.annotate(r["config"], (r["capex_mid"] + 1, r["P95_rel_ge1t"] * 100), fontsize=7, xytext=(3, 3),
                    textcoords="offset points")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.axhline(5, ls="--", c="grey"); ax.axhline(2, ls=":", c="grey")
    ax.set_xlabel("Installed cost per machine, EUR (mid estimate, +1, log)")
    ax.set_ylabel("95th percentile |error| on loads >= 1 t, % (log)")
    ax.set_title("SIMULATED cost vs accuracy (red = Pareto frontier)")
    fig.tight_layout(); fig.savefig(RES / "pareto_cost_vs_accuracy.png", dpi=130); plt.close(fig)
    # 2. error vs true mass for key configs
    fig, axs = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    t = ev["m_true"].to_numpy()[mask]
    for ax, name in zip(axs.ravel(), ["REF_CERT_LC4", "LC4_CHEAP", "SG_BEND2_A5", "HYD_COMP_OILT_A5", "HYBRID_A5", "FILL_D_A5"]):
        e = est[name][mask] - t
        ax.scatter(t, e, s=2, alpha=0.3)
        ax.axhline(100, c="r", lw=0.8); ax.axhline(-100, c="r", lw=0.8)
        ax.plot([0, 8000], [0, 400], "g:", lw=0.8); ax.plot([0, 8000], [0, -400], "g:", lw=0.8)
        ax.set_ylim(-1500, 1500); ax.set_title(name, fontsize=9)
    for ax in axs[1]:
        ax.set_xlabel("true load mass, kg")
    axs[0, 0].set_ylabel("error, kg"); axs[1, 0].set_ylabel("error, kg")
    fig.suptitle("SIMULATED error vs load (red: +-100 kg, green: +-5 %)")
    fig.tight_layout(); fig.savefig(RES / "error_vs_mass.png", dpi=130); plt.close(fig)
    # 3. verification detection power, step mode, 6 lifts
    fig, ax = plt.subplots(figsize=(8, 5))
    v = ver[(ver["mode"] == "step") & (ver["N_lifts"] == 6)]
    for name, g in v.groupby("config"):
        ax.plot(g["overbilling"] * 100, g["detection_rate"] * 100, marker="o", label=name)
    ax.set_xlabel("systematic overbilling of tonnage, %"); ax.set_ylabel("machine-windows flagged, %")
    ax.set_title("SIMULATED detection power, median of 6 pickups, 5 % false-alarm rate")
    ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(RES / "verification_detection_power.png", dpi=130); plt.close(fig)


def pareto_frontier(df):
    """Cost vs P95 frontier over the options Europress could install (operator weighbridge rows excluded)."""
    d = df.sort_values(["capex_mid", "P95_rel_ge1t"]).reset_index(drop=True)
    best = np.inf
    flags = []
    for _, r in d.iterrows():
        if str(r["config"]).startswith("WB_"):
            flags.append(False)
            continue
        flags.append(bool(r["P95_rel_ge1t"] < best))
        best = min(best, r["P95_rel_ge1t"])
    d["pareto"] = flags
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    p = load_params()
    if a.quick:
        p["n_machines"] = 80
    RES.mkdir(parents=True, exist_ok=True)
    k = p["anchors"]["k_default"]
    golden_fn = lambda w: (w["machine_id"] % 5 == 0).to_numpy()  # noqa: E731  20 % golden cohort

    ev = build_world(p)
    golden = golden_fn(ev)
    est, mask, core_df, by_mat, by_bin = core(ev, p, golden, k)
    costs = cost_table(yaml.safe_load((HERE / "costs.yaml").read_text()))
    core_df["cost_key"] = core_df["config"].map(COST_KEY)
    core_df["independent_of_operator"] = core_df["config"].map(INDEPENDENT)
    pdf = core_df.merge(costs, on="cost_key", how="left")
    pdf["eur_misstatement_per_device_year"] = pdf["median_rel_ge1t"] * MASS_SENSITIVE_EUR
    pdf = pareto_frontier(pdf)
    pdf.to_csv(RES / "core_comparison.csv", index=False)
    by_mat.to_csv(RES / "error_by_material_and_class.csv", index=False)
    by_bin.to_csv(RES / "error_by_mass_bin.csv", index=False)
    st = stress(p, golden_fn, k); st.to_csv(RES / "stress_tests.csv", index=False)
    hm = heldout_material(ev, p, golden, k); hm.to_csv(RES / "heldout_material.csv", index=False)
    ab = ablation(ev, p, golden); ab.to_csv(RES / "ablation.csv", index=False)
    ver = verification_power(ev, p, golden, k, est); ver.to_csv(RES / "verification_power.csv", index=False)
    plots(core_df, pdf, by_bin, ver, est, ev, mask)
    gt = ev["m_true"]
    meta = {"n_events": int(len(ev)), "n_eval_events": int(mask.sum()), "anchors_k": k,
            "true_mass_kg_p10_p50_p90": [float(gt.quantile(q)) for q in (0.1, 0.5, 0.9)],
            "hybrid_component_log_sd": est["_hybrid_sd"], "note": "SIMULATED, see params.yaml"}
    (RES / "run_meta.json").write_text(json.dumps(meta, indent=2))
    cols = ["config", "capex_mid", "MAE_kg", "bias_kg", "P95_abs_kg", "within_100kg_at_2.5-3.5t",
            "median_rel_ge1t", "P95_rel_ge1t", "within_2pct_ge1t", "within_5pct_ge1t", "pareto"]
    pd.set_option("display.width", 250)
    print(pdf[cols].round(3).to_string(index=False))
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
