"""Analytical uncertainty propagation (sigma_m^2 = J Sigma J^T), Monte Carlo cross-check,
identifiability counterexamples and required sensor accuracy.

Reference point: 3,000 kg cardboard load in a 20 m3 DUO container [assumed geometry, params.yaml].
Writes results/uncertainty_*.csv and results/identifiability.json. All values are [derived]/[simulated].
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from estimators import nominal_material
from world import load_params, relief_face_stress, rho_law

RES = Path(__file__).resolve().parent.parent / "results"
M0 = 3000.0


def jac_numeric(f, x0: dict, keys, h=1e-4):
    base = f(x0)
    J = []
    for k in keys:
        x = dict(x0)
        step = h * (abs(x[k]) if x[k] != 0 else 1.0)
        x[k] = x[k] + step
        J.append((f(x) - base) / step)
    return np.array(J)


# ---------------- Model A: four load cells ----------------
def model_a(x):
    # m_hat = sum_i (1+g_i) s_i m - eps*s_front*m + tc*dT + n + snow
    s = np.array([x["s1"], x["s2"], x["s3"], 1 - x["s1"] - x["s2"] - x["s3"]])
    g = np.array([x["g1"], x["g2"], x["g3"], x["g4"]])
    front = s[2] + s[3]
    return ((1 + g) * s).sum() * x["m"] - x["eps"] * front * x["m"] + x["tc"] * x["dT"] + x["noise"] + x["snow"]


def budget_a(p, grade):
    c = p["load_cells"][grade]
    x0 = {"m": M0, "s1": 0.3, "s2": 0.3, "s3": 0.2, "g1": 0, "g2": 0, "g3": 0, "g4": 0,
          "eps": c["parasitic_max"] / 2, "tc": c["tc_zero_kg_per_c"], "dT": 0.0, "noise": 0.0, "snow": 0.0}
    sd = {"g1": c["cell_gain_sd"], "g2": c["cell_gain_sd"], "g3": c["cell_gain_sd"], "g4": c["cell_gain_sd"],
          "s1": 0.05, "s2": 0.05, "s3": 0.05,  # load distribution changes between pickups (COM)
          "eps": c["parasitic_max"] / 2, "dT": p["environment"]["t_tare_shift_sd_c"],
          "noise": np.sqrt(2 * c["noise_kg"]**2 + p["load_cells"]["wind_noise_kg"]**2),
          "snow": p["environment"]["snow_mean_kg"] * 0.55}  # ~30 % of winter events x exp(40): sd approx
    keys = list(sd)
    J = jac_numeric(model_a, x0, keys)
    var = (J**2) * np.array([sd[k]**2 for k in keys])
    rows = [{"model": f"A_LC4_{grade}", "input": k, "sd": sd[k], "dm_dinput": J[i], "var_share": var[i] / var.sum(),
             "sigma_contrib_kg": np.sqrt(var[i])} for i, k in enumerate(keys)]
    # MC cross-check
    rng = np.random.default_rng(1)
    n = 20000
    sims = []
    for _ in range(n):
        x = dict(x0)
        for k in keys:
            x[k] = x0[k] + rng.normal(0, sd[k])
        sims.append(model_a(x) - M0)
    sims = np.array(sims)
    return rows, float(np.sqrt(var.sum())), float(np.std(sims)), float(np.percentile(np.abs(sims), 95))


# ---------------- Model C/D: pressure + fill -> density -> mass ----------------
def model_cd_truth(p, x):
    """True mass from the latent state; estimator assumes nominal parameters."""
    rl, ri, sc, _ = nominal_material(p, "cardboard", "DUO")
    rho = rho_law(x["sigma"], rl, ri * x["k_inf"], sc * x["k_c"])
    return rho * (1 + x["w"]) * x["f"] * 20.0


def model_cd_estimate(p, x):
    rl, ri, sc, _ = nominal_material(p, "cardboard", "DUO")
    sigma_hat = x["sigma"] * x["p_gain"] * (1 + x["area"]) + x["loss_err"]
    rho = rho_law(sigma_hat, rl, ri, sc)
    return rho * x["f_obs"] * 20.0


def budget_cd(p, anchored: bool):
    rl, ri, sc, rho_ref = nominal_material(p, "cardboard", "DUO")
    s_ref = p["press"]["reference_stress_frac"] * relief_face_stress(p["press"]["DUO"])
    f0 = M0 / (rho_ref * 20.0)
    mp = p["materials"]["cardboard"]
    # unknowns that the estimator cannot see -> error = estimate(nominal) - truth(perturbed)
    sd = {
        "k_inf": np.sqrt(p["machines"]["site_density_cv"]**2 * (0.25 if anchored else 1) + mp["event_cv"]**2),
        "k_c": mp["sigma_c_cv"],
        "w": 0.07,  # sd of water fraction, from the wet/dry mixture in params [derived approx]
        "f_obs": np.sqrt((p["fill_sensor"]["sigma_pp"] / 100)**2
                         + ((p["fill_sensor"]["bias_sd_pp"] / 100)**2 + (p["fill_sensor"]["gain_sd"] * f0)**2) * (0.25 if anchored else 1)),
        "p_gain": p["press"]["plateau_noise_rel"],
        "area": p["press"]["area_tol_cv"] * (0.5 if anchored else 1),
        "loss_err": 0.5 * 1e5 * 0.018 / 2.0,  # 0.5 bar residual loss error -> Pa face stress
    }
    x0 = {"sigma": s_ref, "k_inf": 1.0, "k_c": 1.0, "w": 0.0, "f": f0, "f_obs": f0, "p_gain": 1.0, "area": 0.0, "loss_err": 0.0}
    m_true0 = model_cd_truth(p, x0)

    def err(x):
        return model_cd_estimate(p, x) - model_cd_truth(p, x) * (M0 / m_true0)

    keys = list(sd)
    J = jac_numeric(err, x0, keys, h=1e-3)
    var = (J**2) * np.array([sd[k]**2 for k in keys])
    tag = "CD_anchored" if anchored else "CD_uncalibrated"
    rows = [{"model": tag, "input": k, "sd": sd[k], "dm_dinput": J[i], "var_share": var[i] / var.sum(),
             "sigma_contrib_kg": np.sqrt(var[i])} for i, k in enumerate(keys)]
    rng = np.random.default_rng(2)
    sims = []
    for _ in range(20000):
        x = dict(x0)
        for k in keys:
            x[k] = x0[k] + rng.normal(0, sd[k])
        sims.append(err(x))
    sims = np.array(sims)
    return rows, float(np.sqrt(var.sum())), float(np.std(sims)), float(np.percentile(np.abs(sims), 95))


def identifiability(p):
    rl, ri, sc, rho_ref = nominal_material(p, "cardboard", "DUO")
    s_ref = p["press"]["reference_stress_frac"] * relief_face_stress(p["press"]["DUO"])
    V, f = 20.0, 0.75
    rho = rho_law(s_ref, rl, ri, sc)
    dry = rho * f * V
    wet = dry * 1.20
    # material counterexample: stiffer material (sigma_c +30 %) at higher fill gives the same pressure & mass?
    rho_stiff = rho_law(s_ref, rl, ri, sc * 1.3)
    f_same_mass = dry / (rho_stiff * V)
    # observation Jacobian rank: observations y = (p, f) ; unknowns theta = (m, rho_inf, sigma_c, w)
    # p depends on sigma only; f on volume only; m = rho(sigma; rho_inf, sigma_c)(1+w) f V
    # => d(p,f)/d(rho_inf, w) = 0 at fixed (sigma, f): mass direction not observable
    return {
        "reference": {"V_m3": V, "fill": f, "face_stress_kPa": s_ref / 1e3, "rho_kg_m3": rho},
        "counterexample_moisture": {
            "load_A_dry_kg": dry, "load_B_wet_kg": wet,
            "same_pressure_curve": True, "same_fill": True,
            "explanation": "water adds mass but the fibre skeleton sets the stress-strain response; "
                           "pressure and fill are identical while mass differs by 20 %",
        },
        "counterexample_material_stiffness": {
            "load_A": {"fill": f, "sigma_c_factor": 1.0, "mass_kg": dry},
            "load_C": {"fill": f, "sigma_c_factor": 1.3, "mass_kg": rho_stiff * f * V,
                       "mass_diff_pct": 100 * (rho_stiff / rho - 1)},
            "fill_needed_for_equal_mass": f_same_mass,
            "explanation": "a stiffer batch at the same face stress and fill is lighter; pressure alone cannot tell "
                           "softer-heavier from stiffer-lighter without the material law of that batch",
        },
        "observation_rank": {"observations": ["plateau_pressure", "fill_level"],
                             "unknowns": ["mass", "rho_inf", "sigma_c", "water_fraction"],
                             "rank": 2, "identifiable": False,
                             "what_resolves_it": "a direct gravitational measurement (load cells/strain at ALL supports) "
                                                 "or per-batch density reference (ticket anchors only fix the machine mean)"},
        "hooklift_com": {"formula": "m_hat/m = x_c / x_c_hat  (single force about one pivot)",
                         "sd_x_rel_0.15_gives_mass_sd_rel": 0.15,
                         "explanation": "one force about one pivot measures W*x_c, not W; a second reaction is needed"},
        "two_rear_cells": {"formula": "dm/m = dx_c/(L - x_c)", "x_c_over_L": 0.4, "sd_x_over_L": 0.08,
                           "mass_sd_rel": 0.08 / 0.6},
    }


def required_accuracy(p):
    """What each model needs to hit P95 <= 2 % and <= 5 % at 3 t (Gaussian: P95 = 1.96 sigma)."""
    out = []
    for target in (0.02, 0.05):
        sig = target / 1.96
        out.append({"target_P95": target, "model": "A_LC4",
                    "max_cell_gain_sd_if_alone": sig / np.sqrt(4 * 0.25**2 + 4 * 0.05**2),
                    "max_parasitic_share": sig * 2, "max_zero_drift_kg": sig * M0})
        out.append({"target_P95": target, "model": "CD_pressure_fill",
                    "max_total_density_law_cv": sig, "max_fill_sd_pp_at_75pct": sig * 75,
                    "note": "moisture alone (sd ~7 %) already exceeds the 2 % and 5 % targets"})
    return out


def main():
    p = load_params()
    RES.mkdir(parents=True, exist_ok=True)
    rows, summ = [], []
    for grade in ("cert", "cheap"):
        r, lin, mc, p95 = budget_a(p, grade)
        rows += r
        summ.append({"model": f"A_LC4_{grade}", "sigma_linear_kg": lin, "sigma_mc_kg": mc, "P95_abs_mc_kg": p95})
    for anch in (False, True):
        r, lin, mc, p95 = budget_cd(p, anch)
        rows += r
        summ.append({"model": "CD_anchored" if anch else "CD_uncalibrated", "sigma_linear_kg": lin,
                     "sigma_mc_kg": mc, "P95_abs_mc_kg": p95})
    pd.DataFrame(rows).round(5).to_csv(RES / "uncertainty_budget.csv", index=False)
    pd.DataFrame(summ).round(2).to_csv(RES / "uncertainty_summary.csv", index=False)
    pd.DataFrame(required_accuracy(p)).round(5).to_csv(RES / "required_accuracy.csv", index=False)
    (RES / "identifiability.json").write_text(json.dumps(identifiability(p), indent=2, default=float))
    print(pd.DataFrame(summ).round(1).to_string(index=False))
    print(pd.DataFrame(rows)[["model", "input", "var_share", "sigma_contrib_kg"]].round(3).to_string(index=False))
    print(json.dumps(identifiability(p), indent=1, default=float)[:1500])


if __name__ == "__main__":
    main()
