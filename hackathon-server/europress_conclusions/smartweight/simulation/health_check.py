"""Sensor-health detection for the 4-cell system (Model A), SIMULATED.

Rules tested on every evaluation pickup:
  R1 centre-of-mass plausibility: the COM implied by the 4 cell readings of the content (full - empty)
     must lie inside the footprint with margin, and its longitudinal position must agree with the
     fill-based expectation within 0.35 L.
  R2 cross-check with the free indirect estimate (fill x calibrated density): flag if LC/indirect < 0.6 or > 1.6.
  R3 per-cell share: flag if any cell carries < 3 % or > 60 % of the content load (dead / shorted / jammed cell).
  Small gain drifts (2-10 %) are NOT visible per pickup; they are caught by the periodic test-weight check and
  by the long-run median ratio to weighed-tare tickets (see verification_power.csv for the statistical power).
Writes results/health_check.csv.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import estimators as E
import sensors as S
from world import build_world, load_params

RES = Path(__file__).resolve().parent.parent / "results"


def cell_readings(ev, p, rng, dead: bool, drift: float = 0.0):
    c = p["load_cells"]["cheap"]
    sh = S.support_shares(ev)
    m = ev["m_true"].to_numpy()[:, None]
    gains = rng.normal(0, c["cell_gain_sd"], size=sh.shape)
    r = sh * m * (1 + gains) + rng.normal(0, c["noise_kg"], size=sh.shape)
    if dead:
        r[:, 0] = rng.normal(0, c["noise_kg"], len(ev))
    if drift:
        r[:, 0] *= 1 + drift
    return r


def com_rule(r, f_obs):
    tot = r.sum(axis=1)
    rear = (r[:, 0] + r[:, 1]) / np.clip(tot, 1, None)
    left = (r[:, 0] + r[:, 2]) / np.clip(tot, 1, None)
    x_frac = 1 - rear  # content COM / L from the rear
    expected = np.clip(f_obs, 0.05, 1) / 2
    return (np.abs(x_frac - expected) > 0.35) | (np.abs(left - 0.5) > 0.25) | (rear < 0) | (rear > 1)


def main():
    p = load_params()
    p["n_machines"] = 200
    ev = build_world(p)
    rng = np.random.default_rng(3)
    f_obs = S.fill_obs(ev, p, rng)
    ticket = S.weighbridge_ticket(ev, p, rng)
    ind, _ = E.anchor_calibrate(ev, E.fill_density(ev, p, f_obs), ticket, 5)
    mask = (ev["event_no"] >= 5).to_numpy() & (ev["m_true"] > 500).to_numpy()
    truth = ev["m_true"].to_numpy()
    rows = []
    for label, dead, drift in (("healthy", False, 0.0), ("one_cell_dead", True, 0.0),
                               ("one_cell_gain_+2pct", False, 0.02), ("one_cell_gain_+10pct", False, 0.10)):
        r = cell_readings(ev, p, np.random.default_rng(4), dead, drift)
        lc = r.sum(axis=1)
        r1 = com_rule(r, f_obs)
        ratio = lc / np.clip(ind, 1, None)
        r2 = (ratio < 0.6) | (ratio > 1.6)
        share = r / np.clip(lc, 1, None)[:, None]
        r3 = (share.min(axis=1) < 0.03) | (share.max(axis=1) > 0.60)
        ok = mask & ~(r1 | r2 | r3)
        rows.append({"condition": label,
                     "flag_rate_R1_com": float(r1[mask].mean()),
                     "flag_rate_R2_crosscheck": float(r2[mask].mean()),
                     "flag_rate_R1_or_R2": float((r1 | r2)[mask].mean()),
                     "flag_rate_R3_cell_share": float(r3[mask].mean()),
                     "flag_rate_any": float((r1 | r2 | r3)[mask].mean()),
                     "median_abs_rel_error_unflagged": (float(np.median(np.abs(lc - truth)[ok] / truth[ok]))
                                                        if ok.any() else float("nan"))})
    df = pd.DataFrame(rows).round(4)
    df.to_csv(RES / "health_check.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
