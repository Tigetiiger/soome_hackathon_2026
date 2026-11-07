"""Physical world: machines, materials and pickup events (ground truth).

All distributions come from params.yaml and are SYNTHETIC sensitivity assumptions.
One row of the returned DataFrame = one pickup (emptying) of one machine.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent


def load_params(path: Path | None = None) -> dict:
    return yaml.safe_load((path or HERE / "params.yaml").read_text())


def rho_law(sigma, rho_loose, rho_inf, sigma_c):
    """Compaction law rho(sigma) [kg/m3]; sigma and sigma_c in Pa."""
    return rho_loose + (rho_inf - rho_loose) * (1.0 - np.exp(-sigma / sigma_c))


def sigma_c_for(rho_loose, rho_ref, rho_inf, sigma_ref):
    """Solve rho(sigma_ref) = rho_ref for sigma_c."""
    frac = (rho_ref - rho_loose) / (rho_inf - rho_loose)
    return -sigma_ref / np.log(1.0 - frac)


def relief_face_stress(press: dict) -> float:
    return press["relief_bar"] * 1e5 * press["a_cyl_m2"] / press["a_face_m2"]


def make_machines(p: dict, rng: np.random.Generator, n: int | None = None) -> pd.DataFrame:
    n = n or p["n_machines"]
    mp = p["machines"]
    cls = rng.choice(list(mp["class_share"]), size=n, p=list(mp["class_share"].values()))
    mats = rng.choice(list(mp["material_share"]), size=n, p=list(mp["material_share"].values()))
    vol = np.array([rng.choice(mp["volumes_m3"][c]) for c in cls], dtype=float)
    area = rng.uniform(*mp["cross_section_m2"], size=n)
    tare = np.array([
        (mp["tare_kg"][c]["base"] + mp["tare_kg"][c]["per_m3"] * v)
        * rng.lognormal(0, mp["tare_kg"][c]["cv"]) for c, v in zip(cls, vol)
    ])
    pr = p["press"]
    return pd.DataFrame({
        "machine_id": np.arange(n),
        "eq_class": cls,
        "material": mats,
        "volume_m3": vol,
        "length_m": vol / area,
        "tare_kg": tare,
        "site_rho_factor": rng.lognormal(0, mp["site_density_cv"], size=n),
        "area_err": rng.normal(0, pr["area_tol_cv"], size=n),           # cylinder/face area tolerance
        "friction_factor": rng.lognormal(0, pr["friction_cv"], size=n),  # wall friction of this machine
        "motor_eff": pr["motor_eff_mean"] * rng.lognormal(0, pr["motor_eff_device_cv"], size=n),
        "fill_gain": rng.normal(0, p["fill_sensor"]["gain_sd"], size=n),
        "fill_bias_pp": rng.normal(0, p["fill_sensor"]["bias_sd_pp"], size=n),
        # tare centre of mass from the rear support, fraction of length (COMBI: press unit at the front)
        "tare_com_frac": np.where(cls == "COMBI", rng.uniform(0.6, 0.7, n), rng.uniform(0.45, 0.55, n)),
    })


def make_events(p: dict, machines: pd.DataFrame, rng: np.random.Generator,
                events_per_machine: int | None = None) -> pd.DataFrame:
    k = events_per_machine or p["events_per_machine"]
    ev = machines.loc[machines.index.repeat(k)].reset_index(drop=True)
    n = len(ev)
    ev["event_no"] = np.tile(np.arange(k), len(machines))
    env = p["environment"]

    # fill at pickup: mostly on-call near full, some early pickups [assumed]
    early = rng.random(n) < 0.3
    ev["fill_true"] = np.where(early, rng.uniform(0.2, 0.75, n), rng.uniform(0.75, 1.0, n))

    # temperatures, time since emptying, snow change on the container
    season = rng.uniform(0, 1, n)
    ev["t_amb"] = env["t_amb_range_c"][0] + (env["t_amb_range_c"][1] - env["t_amb_range_c"][0]) * \
        (0.5 - 0.5 * np.cos(2 * np.pi * season))
    ev["dt_tare"] = rng.normal(0, env["t_tare_shift_sd_c"], n)
    ev["days"] = rng.uniform(*env["days_between"], n)
    snow = (ev["t_amb"] < 0) & (rng.random(n) < env["snow_prob_below_0c"])
    ev["snow_kg"] = np.where(snow, rng.exponential(env["snow_mean_kg"], n), 0.0)
    ev["t_oil"] = ev["t_amb"] + rng.uniform(*env["oil_warmup_c"], n)

    # material state and mass
    rho_dry = np.empty(n)
    wet = np.empty(n)
    sig_eff = np.empty(n)
    sig_c_true = np.empty(n)
    rho_inf_true = np.empty(n)
    for mat, mpar in p["materials"].items():
        i = (ev["material"] == mat).to_numpy()
        m = int(i.sum())
        if m == 0:
            continue
        cls = ev.loc[i, "eq_class"].to_numpy()
        s_rel = np.array([relief_face_stress(p["press"][c]) for c in cls])
        s_ref = p["press"]["reference_stress_frac"] * s_rel
        rho_inf = mpar["inf_factor"] * mpar["rho_ref"] * ev.loc[i, "site_rho_factor"].to_numpy() \
            * rng.lognormal(0, mpar["event_cv"], m)
        sc = sigma_c_for(mpar["rho_loose"], mpar["rho_ref"], mpar["inf_factor"] * mpar["rho_ref"], s_ref) \
            * rng.lognormal(0, mpar["sigma_c_cv"], m)
        # effective (mean) pack stress grows with fill [assumed]
        f = ev.loc[i, "fill_true"].to_numpy()
        s_eff = s_ref * (0.5 + 0.5 * f) * rng.lognormal(0, 0.10, m)
        is_wet = rng.random(m) < mpar["wet_prob"]
        w = np.where(is_wet, rng.uniform(*mpar["wet_gain"], m), rng.uniform(*mpar["dry_gain"], m))
        soft = 1.0 + mpar["wet_softening"] * w           # wet fibres pack denser at the same stress
        rho_dry[i] = rho_law(s_eff, mpar["rho_loose"], rho_inf, sc) * soft
        wet[i] = w
        sig_eff[i] = s_eff
        sig_c_true[i] = sc
        rho_inf_true[i] = rho_inf
    ev["sigma_eff_pa"] = sig_eff
    ev["sigma_c_true"] = sig_c_true
    ev["rho_inf_true"] = rho_inf_true
    ev["water_frac"] = wet
    ev["rho_dry"] = rho_dry
    ev["m_true"] = rho_dry * (1.0 + wet) * ev["fill_true"] * ev["volume_m3"]

    # content centre of mass from the rear wall (pack grows from the rear door forward) [assumed]
    L = ev["length_m"]
    ev["x_content"] = (ev["fill_true"] * L / 2 * rng.normal(1.0, 0.15, n)).clip(0.05 * L, 0.95 * L)
    ev["y_content"] = rng.normal(0, 0.10, n)  # lateral offset [m]
    return ev


def build_world(p: dict, seed: int | None = None, n_machines: int | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(seed if seed is not None else p["seed"])
    machines = make_machines(p, rng, n_machines)
    return make_events(p, machines, rng)
