"""Virtual compaction test rig: measure density vs pressure for every material, then fit a law.

Procedure per sample (what a real lab/test-hall run would do):
  1. Weigh a loose batch on a bench platform scale (0.2 %).
  2. Load it into a 0.7 x 0.7 m press box; press at stepped hydraulic pressures.
  3. At each step read pressure (transducer) and ram position (draw-wire, +/-3 mm) -> volume -> density.
  Conditions: cold / mild / warm, and wet vs dry for fibre materials. Each batch is a different
  "real" material sample (stiffness and dense-limit vary batch to batch).

Fit per material:  rho(sigma, T, wet) = rho_L + (rho_inf - rho_L) * (1 - exp(-sigma / sc))
                   sc = sigma_c * (1 + b_cold * cold(T)) * (1 - b_wet * wet)
The fitted law is the "density table" the field estimator uses: pressure -> density.
"""
from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from vscale import physics as ph
from vscale.config import DEFAULT_OUT, PROJECT_ROOT, load_config

log = logging.getLogger(__name__)


def cold_index(temp_c: np.ndarray) -> np.ndarray:
    return np.clip(-np.asarray(temp_c, dtype=float) / 20.0, 0.0, 1.0)


@dataclass(frozen=True)
class FittedLaw:
    material: str
    rho_loose: float
    rho_inf: float
    sigma_c: float
    b_cold: float
    b_wet: float
    log_resid_sd: float     # batch-to-batch scatter in log density (the material's own variability)
    n_points: int

    def density(self, sigma_kpa: np.ndarray, temp_c: np.ndarray | float = 10.0, wet: np.ndarray | float = 0.0) -> np.ndarray:
        sig = np.asarray(sigma_kpa, dtype=float)
        return _law(sig, np.broadcast_to(cold_index(temp_c), sig.shape),
                    np.broadcast_to(np.asarray(wet, dtype=float), sig.shape),
                    self.rho_loose, self.rho_inf, self.sigma_c, self.b_cold, self.b_wet)


def _law(sig, cold, wet, rho_l, rho_inf, sigma_c, b_cold, b_wet):
    sc = sigma_c * (1 + b_cold * cold) * (1 - b_wet * wet)
    return rho_l + (rho_inf - rho_l) * (1 - np.exp(-np.maximum(sig, 0) / sc))


def true_law(cfg: dict, material: str) -> ph.MaterialLaw:
    """Ground-truth law of the synthetic world at the DUO reference stress (same as the field sim)."""
    g = cfg["press"]["DUO"]
    srel = ph.relief_stress_kpa(g["relief_bar"], g["a_cyl_m2"], g["a_face_m2"])
    m = cfg["materials"][material]
    return ph.material_law(m["rho_loose"], m["rho_ref"], m["inf_factor"], cfg["press"]["reference_stress_frac"] * srel)


def run_experiment(cfg: dict, rng: np.random.Generator) -> pd.DataFrame:
    rig = cfg["rig"]
    pt = cfg["sensors"]["pressure_transducer"]
    rows = []
    for mat, m in cfg["materials"].items():
        law = true_law(cfg, mat)
        wets = [0.0, 1.0] if m["moisture_sensitive"] else [0.0]
        sid = 0
        for temp in rig["temperatures_c"]:
            for wet in wets:
                for _ in range(rig["samples_per_condition"]):
                    sid += 1
                    # this batch's real behaviour
                    scale = (rng.lognormal(0, m["sigma_c_cv"]) * rng.lognormal(0, m["daily_cv"])
                             * (1 + m["cold_stiffening"] * cold_index(temp))
                             * (1 - cfg["climate"]["rain_softening"] * wet * rng.uniform(0.6, 1.0)))
                    batch = ph.MaterialLaw(law.rho_loose * rng.lognormal(0, 0.05),
                                           law.rho_inf * rng.lognormal(0, rig["rho_inf_sample_cv"]), law.sigma_c)
                    mass_true = rig["loose_fill_m3"] * batch.rho_loose * (1 + 0.1 * wet)
                    mass_meas = mass_true * (1 + rng.normal(0, rig["scale_sigma_rel"]))
                    sig = np.asarray(rig["stress_steps_kpa"], dtype=float)
                    rho = batch.density(sig, scale)
                    vol_true = mass_true / rho
                    pos_mm = vol_true / rig["a_face_m2"] * 1000 + rng.normal(0, rig["position_sd_mm"], sig.size)
                    vol_meas = np.maximum(pos_mm, 1.0) / 1000 * rig["a_face_m2"]
                    p_bar = (ph.face_kpa_to_bar(sig, rig["a_cyl_m2"], rig["a_face_m2"])
                             + rng.normal(0, pt["noise_fs"] * pt["full_scale_bar"], sig.size))
                    for k in range(sig.size):
                        rows.append({"material": mat, "sample_id": f"{mat}-{sid:03d}", "temp_c": temp, "wet": wet,
                                     "mass_kg": mass_meas, "p_bar": p_bar[k], "position_mm": pos_mm[k],
                                     "face_stress_kpa": ph.bar_to_face_kpa(p_bar[k], rig["a_cyl_m2"], rig["a_face_m2"]),
                                     "density_kg_m3": mass_meas / vol_meas[k], "true_density_kg_m3": rho[k]})
    return pd.DataFrame(rows)


def fit_material(d: pd.DataFrame, moisture: bool) -> FittedLaw:
    sig = d.face_stress_kpa.to_numpy()
    cold = cold_index(d.temp_c.to_numpy())
    wet = d.wet.to_numpy()
    rho = d.density_kg_m3.to_numpy()

    def f(x, rho_l, rho_inf, sigma_c, b_cold, b_wet):
        return np.log(_law(x[0], x[1], x[2], rho_l, rho_inf, sigma_c, b_cold, b_wet if moisture else 0.0))

    p0 = [rho.min(), rho.max() * 1.2, 80.0, 0.0, 0.0]
    lo = [1.0, rho.min(), 1.0, -0.5, -0.5]
    hi = [rho.max(), rho.max() * 5, 2000.0, 2.0, 0.9]
    popt, _ = curve_fit(f, np.vstack([sig, cold, wet]), np.log(rho), p0=p0, bounds=(lo, hi), maxfev=20000)
    resid = np.log(rho) - f(np.vstack([sig, cold, wet]), *popt)
    return FittedLaw(material=str(d.material.iloc[0]), rho_loose=popt[0], rho_inf=popt[1], sigma_c=popt[2],
                     b_cold=popt[3], b_wet=popt[4] if moisture else 0.0,
                     log_resid_sd=float(np.std(resid)), n_points=len(d))


def fit_all(cfg: dict, meas: pd.DataFrame) -> dict[str, FittedLaw]:
    return {mat: fit_material(g, cfg["materials"][mat]["moisture_sensitive"]) for mat, g in meas.groupby("material")}


def laws_table(cfg: dict, laws: dict[str, FittedLaw]) -> pd.DataFrame:
    """Fitted parameters + the density 'lookup' at round field pressures (DUO end pressure)."""
    rows = []
    for mat, L in laws.items():
        row = {"material": mat, "rho_loose": L.rho_loose, "rho_inf": L.rho_inf, "sigma_c_kpa": L.sigma_c,
               "b_cold": L.b_cold, "b_wet": L.b_wet, "batch_scatter_pct": 100 * L.log_resid_sd, "points": L.n_points,
               "pack_typical_density": cfg["materials"][mat]["rho_ref"]}
        geo = cfg["press"]["DUO"]
        for bar in (25, 50, 100, 150):
            s = ph.bar_to_face_kpa(bar, geo["a_cyl_m2"], geo["a_face_m2"])
            row[f"rho_at_DUO_{bar}bar"] = float(L.density(np.array([s]))[0])
        rows.append(row)
    return pd.DataFrame(rows).round(3)


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cfg = load_config()
    meas = run_experiment(cfg, np.random.default_rng(cfg["seed"] + 7))
    Path(a.out).mkdir(parents=True, exist_ok=True)
    meas.to_parquet(Path(a.out) / "rig_measurements.parquet", index=False)
    table = laws_table(cfg, fit_all(cfg, meas))
    rep = PROJECT_ROOT / "reports"
    rep.mkdir(exist_ok=True)
    table.to_csv(rep / "rig_density_laws.csv", index=False)
    log.info("rig: %d measurements, %d samples\n%s", len(meas), meas.sample_id.nunique(), table.to_string(index=False))


if __name__ == "__main__":
    main()
