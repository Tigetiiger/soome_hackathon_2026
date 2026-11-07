"""Sensor observation models: what each sensor configuration would read for each pickup.

Every function takes the ground-truth event table (world.py) and returns new columns.
Noise models are [assumed] and parameterised in params.yaml.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from world import relief_face_stress  # noqa: F401  (re-exported for estimators)


def _per_machine(ev: pd.DataFrame, rng, sd: float, size: int = 1):
    """Draw a per-machine random effect and broadcast to events."""
    n_m = ev["machine_id"].max() + 1
    draw = rng.normal(0, sd, size=(n_m, size))
    out = draw[ev["machine_id"].to_numpy()]
    return out[:, 0] if size == 1 else out


def fill_obs(ev, p, rng):
    fs = p["fill_sensor"]
    f = ev["fill_true"] * 100 * (1 + ev["fill_gain"]) + ev["fill_bias_pp"] + rng.normal(0, fs["sigma_pp"], len(ev))
    return (f.clip(0, 105) / 100).to_numpy()


def support_shares(ev):
    """Content load share on 4 supports: rear-left, rear-right, front-left, front-right."""
    L = ev["length_m"].to_numpy()
    x = ev["x_content"].to_numpy()
    y = ev["y_content"].to_numpy()
    rear = (L - x) / L
    half_w = 1.1
    left = 0.5 + y / (2 * half_w)
    return np.column_stack([rear * left, rear * (1 - left), (1 - rear) * left, (1 - rear) * (1 - left)])


def load_cells_4(ev, p, rng, grade: str, failed_cell: bool = False):
    """Four load cells under all supports. Net = full reading - empty (auto-tare) reading."""
    c = p["load_cells"][grade]
    n = len(ev)
    gains = _per_machine(ev, rng, c["cell_gain_sd"], 4)
    span = _per_machine(ev, rng, c["cell_gain_sd"] / 2)
    sh = support_shares(ev)
    m = ev["m_true"].to_numpy()
    if failed_cell:
        gains = gains.copy()
        gains[:, 0] = -1.0  # cell 0 reads zero
    content = (sh * (1 + gains)).sum(axis=1) * (1 + span) * m
    eps = _per_machine(ev, rng, 1.0)
    eps = np.abs(eps) * c["parasitic_max"] / 2
    eps = np.where(ev["eq_class"] == "DUO", eps, eps * 0.3)  # DUO: docking interface to the press
    parasitic = -eps * (1 - sh[:, :2].sum(axis=1)) * m * 2
    zero_t = c["tc_zero_kg_per_c"] * ev["dt_tare"].to_numpy()
    hyst = rng.normal(0, c["hysteresis_rel"], n) * m
    noise = rng.normal(0, np.sqrt(2) * c["noise_kg"], n) + rng.normal(0, p["load_cells"]["wind_noise_kg"], n)
    return content + parasitic + zero_t + hyst + noise + ev["snow_kg"].to_numpy()


def load_cells_2_rear(ev, p, rng, f_obs):
    """Two load cells/pins at the rear supports only; front support unmeasured (pivot).
    Content mass is reconstructed with a centre-of-mass estimate from the fill level."""
    c = p["load_cells"]["cheap"]
    n = len(ev)
    sh = support_shares(ev)
    m = ev["m_true"].to_numpy()
    L = ev["length_m"].to_numpy()
    rear = sh[:, :2].sum(axis=1) * m * (1 + _per_machine(ev, rng, c["cell_gain_sd"]))
    rear = rear + rng.normal(0, np.sqrt(2) * c["noise_kg"], n) + c["tc_zero_kg_per_c"] / 2 * ev["dt_tare"].to_numpy()
    x_hat = np.clip(f_obs, 0.05, 1.0) * L / 2
    return rear * L / (L - x_hat)


def strain(ev, p, rng, variant: str):
    s = p["strain"][variant]
    n = len(ev)
    m = ev["m_true"].to_numpy()
    cal = _per_machine(ev, rng, s["cal_gain_sd"])
    share_err = rng.normal(0, s["share_cv"], n)
    reading = m * (1 + cal) * (1 + share_err)
    reading += s["tc_kg_per_c"] * ev["dt_tare"].to_numpy()
    reading += rng.normal(0, s["zero_walk_kg_sqrt_day"], n) * np.sqrt(ev["days"].to_numpy())
    reading += rng.normal(0, np.sqrt(2) * s["noise_kg"], n)
    return reading + ev["snow_kg"].to_numpy()


def hooklift_pressure(ev, p, rng, f_obs):
    """Model B on the hauler's hooklift: cylinder force during the lift carries the moment of the load
    about the truck's rear roller. Reconstruct mass with a fill-based centre-of-mass estimate."""
    h = p["hooklift_truck"]
    n = len(ev)
    truck = rng.integers(0, h["n_trucks"], n)
    t_gain = np.random.default_rng(p["seed"] + 7).normal(0, h["cal_gain_sd"], h["n_trucks"])[truck]
    L = ev["length_m"].to_numpy()
    m = ev["m_true"].to_numpy()
    tare = ev["tare_kg"].to_numpy()
    xt = ev["tare_com_frac"].to_numpy() * L
    xc = ev["x_content"].to_numpy()
    friction = rng.normal(0, h["friction_rel_sd"], n)  # residual after mean friction calibration
    moment = (tare * xt + (m + ev["snow_kg"].to_numpy()) * xc) / L
    meas = moment * (1 + t_gain) * (1 + friction) + rng.normal(0, h["dyn_noise_rel"], n) * (tare + m) * 0.5
    x_hat = np.clip(f_obs, 0.05, 1.0) * L / 2
    return (meas - tare * xt / L) * L / x_hat


def weighbridge_ticket(ev, p, rng, weighed_only: bool = True):
    """Net ticket at the operator's weighbridge (gross - tare, two weighings, 20 kg division)."""
    w = p["weighbridge"]
    n = len(ev)
    m = ev["m_true"].to_numpy()
    truck_tare = rng.uniform(11000, 16000, n)
    res = w["resolution_kg"]
    gross = np.round((truck_tare + m + rng.normal(0, w["sigma_kg"], n)) / res) * res
    tare_w = np.round((truck_tare + rng.normal(0, w["sigma_kg"], n)) / res) * res
    if weighed_only:
        return gross - tare_w
    stored = rng.random(n) < w["stored_tare_prob"]
    stale = rng.random(n) < w["stale_vehicle_share"]
    tare_s = truck_tare + rng.normal(0, w["stored_tare_sd_kg"], n) + np.where(stale, rng.normal(0, w["stale_bias_sd_kg"], n), 0)
    return gross - np.where(stored, np.round(tare_s / res) * res, tare_w)


def compaction_pressure(ev, p, rng, sensor_drift_bar: float = 0.0):
    """Mid-stroke plateau pressure [bar] of the last compaction series (Model C/D input)."""
    pr = p["press"]
    n = len(ev)
    a_cyl = np.where(ev["eq_class"] == "COMBI", pr["COMBI"]["a_cyl_m2"], pr["DUO"]["a_cyl_m2"])
    a_face = np.where(ev["eq_class"] == "COMBI", pr["COMBI"]["a_face_m2"], pr["DUO"]["a_face_m2"])
    fric = 1 + 0.25 * (ev["friction_factor"].to_numpy() - 1)
    force = ev["sigma_eff_pa"].to_numpy() * a_face * fric
    p_load = force / (a_cyl * (1 + ev["area_err"].to_numpy())) / 1e5
    loss = pr["loss_bar_40c"] * np.exp(pr["loss_temp_coeff"] * (40 - ev["t_oil"].to_numpy()))
    p_true = (p_load + loss) * rng.lognormal(0, pr["plateau_noise_rel"], n)
    gain = _per_machine(ev, rng, 0.01)
    offset = _per_machine(ev, rng, 1.0)
    return p_true * (1 + gain) + offset + sensor_drift_bar


def pressure_from_current(ev, p, rng, p_bar):
    """Hydraulic pressure inferred from motor current/power: p ~ eta * P_el / Q. Adds efficiency and CT error."""
    pr = p["press"]
    eff_ratio = ev["motor_eff"].to_numpy() / pr["motor_eff_mean"]
    return p_bar * eff_ratio * rng.lognormal(0, pr["ct_noise_rel"], len(ev))
