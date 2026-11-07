"""Operator-level audit cohort, SIMULATED.

Pool (ticket - LC4)/LC4 over a cohort of Tier-2 machines (n machines x N pickups) served by one operator and
detect a constant operator-level tonnage bias with a 5 % false-alarm threshold (bootstrap of the pooled median).
Writes results/audit_cohort_power.txt.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

import sensors as S
from world import build_world, load_params

OUT = Path(__file__).resolve().parent.parent / "results" / "audit_cohort_power.txt"


def main() -> None:
    p = load_params()
    p["n_machines"] = 200
    ev = build_world(p)
    rng = np.random.default_rng(9)
    lc = S.load_cells_4(ev, p, rng, "cheap")
    tk = S.weighbridge_ticket(ev, p, rng, weighed_only=False)
    ok = (ev["m_true"] > 500).to_numpy()
    rel = ((tk - lc) / lc)[ok]
    lines = ["per-pickup sd of (ticket-LC4)/LC4: %.4f  (MAD-sd %.4f)"
             % (rel.std(), 1.4826 * np.median(np.abs(rel - np.median(rel)))),
             "pooled_pickups  bias  detection_rate"]
    for npick in (10, 30, 60, 120, 240):
        for b in (0.005, 0.01, 0.02, 0.03):
            null = np.array([np.median(rng.choice(rel, npick)) for _ in range(4000)])
            thr = np.percentile(null, 95)
            alt = np.array([np.median(rng.choice(rel, npick) + b) for _ in range(4000)])
            lines.append("%5d %6.3f %6.2f" % (npick, b, float(np.mean(alt > thr))))
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
