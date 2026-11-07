"""Reproducible mock data shared by every demo.

All values are synthetic and only loosely inspired by the Europress
"virtual scale" idea (estimating the mass inside a waste compactor from
fill level and hydraulic pressure). They are NOT measurements.

Run directly to (re)write the JSON files consumed by the Three.js demo:
    python shared/mockdata.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

SEED = 2026
ROOT = Path(__file__).resolve().parent
STYLE = json.loads((ROOT / "style.json").read_text())

# Container: 20 m3 roll-off compactor, illustrative capacity.
CAPACITY_KG = 4200.0


# ---------------------------------------------------------------- surface ---
def mass_surface(fill: np.ndarray, pressure: np.ndarray, density: float) -> np.ndarray:
    """Estimated payload mass (tonnes) as a function of fill fraction and
    normalised ram pressure. `density` in [0, 1] morphs between a light,
    springy stream (plastic film) and a dense one (wet cardboard).

    Shape: mass grows with fill; pressure compacts the material, with a
    saturating response, plus a small smooth calibration residual so the
    surface has some character instead of being a plain ramp.
    """
    compaction = 0.35 + 0.65 * (1.0 - np.exp(-(2.0 + 3.0 * density) * pressure))
    base = (0.8 + 2.6 * density) * fill**1.25 * compaction
    residual = 0.12 * np.sin(3.2 * fill * np.pi) * np.cos(2.4 * pressure * np.pi) * fill
    return base + residual


# ----------------------------------------------------------------- lifts ----
@dataclass(frozen=True)
class Lifts:
    fill_pct: np.ndarray      # 0..100
    pressure_bar: np.ndarray  # peak hydraulic pressure at last compaction
    mass_kg: np.ndarray       # weighbridge-ticket mass
    stream: np.ndarray        # 0,1,2 index into STYLE["streams"]
    anomaly: np.ndarray       # bool


def lifts(n_per_stream: int = 180, n_anomalies: int = 14, seed: int = SEED) -> Lifts:
    rng = np.random.default_rng(seed)
    # (fill mean, pressure mean, kg per % fill, noise)
    params = [
        (82.0, 165.0, 34.0, 120.0),  # cardboard: dense, high pressure
        (70.0, 125.0, 27.0, 160.0),  # mixed waste
        (88.0, 95.0, 13.0, 80.0),    # plastic film: bulky, light
    ]
    cols = {k: [] for k in ("f", "p", "m", "s", "a")}
    for s, (fm, pm, kpf, noise) in enumerate(params):
        f = np.clip(rng.normal(fm, 8.0, n_per_stream), 35, 100)
        p = np.clip(rng.normal(pm, 14.0, n_per_stream) + 0.4 * (f - fm), 50, 220)
        m = kpf * f * (0.75 + 0.25 * p / pm) + rng.normal(0, noise, n_per_stream)
        cols["f"].append(f); cols["p"].append(p); cols["m"].append(m)
        cols["s"].append(np.full(n_per_stream, s)); cols["a"].append(np.zeros(n_per_stream, bool))
    # Anomalies: heavy-for-volume lifts (e.g. contamination / water)
    s = rng.integers(0, 3, n_anomalies)
    f = rng.uniform(55, 90, n_anomalies)
    p = rng.uniform(90, 180, n_anomalies)
    m = rng.uniform(3300, 4100, n_anomalies)
    cols["f"].append(f); cols["p"].append(p); cols["m"].append(m)
    cols["s"].append(s); cols["a"].append(np.ones(n_anomalies, bool))
    cat = {k: np.concatenate(v) for k, v in cols.items()}
    return Lifts(cat["f"], cat["p"], np.clip(cat["m"], 300, 4200), cat["s"], cat["a"])


# ------------------------------------------------------------ time series ---
def timeseries(n_compactors: int = 6, days: int = 14, seed: int = SEED) -> dict:
    """Hourly estimated mass inside each compactor (sawtooth: fills, then is
    emptied at pickup). Also returns the weighbridge ticket mass at each
    pickup and the virtual-scale estimate with its uncertainty."""
    rng = np.random.default_rng(seed + 1)
    hours = days * 24
    t = np.arange(hours)
    series = []
    for c in range(n_compactors):
        rate = rng.uniform(9.0, 22.0)            # kg per operating hour
        threshold = rng.uniform(2600, 3600)      # pickup trigger
        stream = int(rng.integers(0, 3))
        mass = np.zeros(hours)
        est = np.zeros(hours)
        sigma = np.zeros(hours)
        pickups = []
        cur = rng.uniform(0, 1500)
        for h in t:
            hour_of_day = h % 24
            weekday = (h // 24) % 7 < 5
            active = 6 <= hour_of_day <= 20
            inflow = rate * (1.6 if active else 0.15) * (1.0 if weekday else 0.45)
            cur += max(0.0, rng.normal(inflow, inflow * 0.35))
            if cur >= threshold:
                ticket = cur
                estimate = ticket * (1 + rng.normal(0, 0.025))
                pickups.append({"hour": int(h), "ticket_kg": round(float(ticket), 1),
                                "estimate_kg": round(float(estimate), 1)})
                cur = rng.uniform(0, 60)
            mass[h] = cur
            sigma[h] = 40 + 0.03 * cur
            est[h] = cur + rng.normal(0, sigma[h] * 0.5)
        series.append({
            "id": f"C-{101 + c}",
            "stream": stream,
            "mass_kg": np.round(mass, 1).tolist(),
            "estimate_kg": np.round(est, 1).tolist(),
            "sigma_kg": np.round(sigma, 1).tolist(),
            "pickups": pickups,
        })
    return {"hours": hours, "days": days, "capacity_kg": CAPACITY_KG, "compactors": series}


def export_json(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "timeseries.json").write_text(json.dumps(timeseries()))
    lf = lifts()
    (out_dir / "lifts.json").write_text(json.dumps({
        "fill_pct": np.round(lf.fill_pct, 2).tolist(),
        "pressure_bar": np.round(lf.pressure_bar, 2).tolist(),
        "mass_kg": np.round(lf.mass_kg, 1).tolist(),
        "stream": lf.stream.astype(int).tolist(),
        "anomaly": lf.anomaly.astype(int).tolist(),
    }))


if __name__ == "__main__":
    export_json(ROOT.parent / "data")
    print("wrote", ROOT.parent / "data")
