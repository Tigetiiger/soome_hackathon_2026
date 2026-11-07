"""Break-even sensitivity of the 4-cell system (Model A, 'cheap' grade): how much worse can each error term get
before P95 |error| on loads >= 1 t exceeds 2 % and 5 %?  SIMULATED. Writes results/sensitivity_lc4.csv + png.
"""
from __future__ import annotations

import copy
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import sensors as S  # noqa: E402
from world import build_world, load_params  # noqa: E402

RES = Path(__file__).resolve().parent.parent / "results"
FACTORS = [0.5, 1, 2, 4, 8, 16, 32]
TERMS = {
    "parasitic_max": ("load_cells", "cheap", "parasitic_max"),
    "tc_zero_kg_per_c": ("load_cells", "cheap", "tc_zero_kg_per_c"),
    "cell_gain_sd": ("load_cells", "cheap", "cell_gain_sd"),
    "hysteresis_rel": ("load_cells", "cheap", "hysteresis_rel"),
    "snow_mean_kg": ("environment", None, "snow_mean_kg"),
}


def p95(p, ev):
    est = S.load_cells_4(ev, p, np.random.default_rng(7), "cheap")
    t = ev["m_true"].to_numpy()
    big = t >= 1000
    return float(np.percentile(np.abs(est[big] - t[big]) / t[big], 95))


def main():
    base = load_params()
    base["n_machines"] = 200
    rows = []
    for term, (sec, sub, key) in TERMS.items():
        for f in FACTORS:
            p = copy.deepcopy(base)
            node = p[sec][sub] if sub else p[sec]
            node[key] = node[key] * f
            ev = build_world(p)
            rows.append({"term": term, "factor": f, "value": node[key], "P95_rel_ge1t": p95(p, ev)})
    df = pd.DataFrame(rows)
    df.to_csv(RES / "sensitivity_lc4.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    for term, g in df.groupby("term"):
        ax.plot(g["factor"], g["P95_rel_ge1t"] * 100, marker="o", label=term)
    ax.set_xscale("log", base=2); ax.axhline(5, ls="--", c="grey"); ax.axhline(2, ls=":", c="grey")
    ax.set_xlabel("multiplier on the assumed error term (1 = params.yaml)")
    ax.set_ylabel("P95 |error|, loads >= 1 t, %")
    ax.set_title("SIMULATED sensitivity of the 4-cell system to each error term")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RES / "sensitivity_lc4.png", dpi=130)
    print(df.pivot(index="factor", columns="term", values="P95_rel_ge1t").round(4).to_string())


if __name__ == "__main__":
    main()
