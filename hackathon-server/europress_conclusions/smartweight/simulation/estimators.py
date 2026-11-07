"""Mass estimators: physical inversions, anchor calibration, ML comparison and fusion."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from world import relief_face_stress, rho_law, sigma_c_for


def nominal_material(p: dict, mat: str, eq_class: str):
    mp = p["materials"][mat]
    s_ref = p["press"]["reference_stress_frac"] * relief_face_stress(p["press"][eq_class])
    rho_inf = mp["inf_factor"] * mp["rho_ref"]
    return mp["rho_loose"], rho_inf, sigma_c_for(mp["rho_loose"], mp["rho_ref"], rho_inf, s_ref), mp["rho_ref"]


def fill_density(ev: pd.DataFrame, p: dict, f_obs: np.ndarray) -> np.ndarray:
    """Model D baseline: m = f * V * rho_table(material)."""
    rho = np.array([p["materials"][m]["rho_ref"] for m in ev["material"]])
    return f_obs * ev["volume_m3"].to_numpy() * rho


def compaction_inverse(ev: pd.DataFrame, p: dict, f_obs: np.ndarray, p_bar: np.ndarray,
                       t_oil_obs: np.ndarray | None) -> np.ndarray:
    """Model C/D: pressure -> face stress -> density via the nominal compaction law -> m = rho * f * V."""
    pr = p["press"]
    is_combi = (ev["eq_class"] == "COMBI").to_numpy()
    a_cyl = np.where(is_combi, pr["COMBI"]["a_cyl_m2"], pr["DUO"]["a_cyl_m2"])
    a_face = np.where(is_combi, pr["COMBI"]["a_face_m2"], pr["DUO"]["a_face_m2"])
    t_oil = t_oil_obs if t_oil_obs is not None else np.full(len(ev), 15.0)  # no probe: assume 15 C
    loss = pr["loss_bar_40c"] * np.exp(pr["loss_temp_coeff"] * (40 - t_oil))
    sigma_hat = np.clip(p_bar - loss, 1.0, None) * 1e5 * a_cyl / a_face
    out = np.empty(len(ev))
    for (mat, cls), idx in ev.groupby(["material", "eq_class"]).indices.items():
        rl, ri, sc, _ = nominal_material(p, mat, cls)
        out[idx] = rho_law(sigma_hat[idx], rl, ri, sc)
    return out * f_obs * ev["volume_m3"].to_numpy()


def anchor_calibrate(ev: pd.DataFrame, raw: np.ndarray, ticket: np.ndarray, k: int,
                     prior_sd: float = 0.15, resid_sd: float | None = None):
    """Per-machine multiplicative gain from the first k pickups' tickets (log-space Bayesian shrinkage).

    Returns (calibrated estimate, is_anchor mask). Anchor events must be excluded from evaluation.
    """
    out = raw.astype(float).copy()
    is_anchor = (ev["event_no"] < k).to_numpy()
    if k == 0:
        return out, is_anchor
    ok = (raw > 50) & (ticket > 200)
    lr = np.where(ok, np.log(np.clip(ticket, 1, None) / np.clip(raw, 1, None)), np.nan)
    if resid_sd is None:
        resid_sd = float(np.nanstd(lr[is_anchor]))  # pooled scatter
    df = pd.DataFrame({"m": ev["machine_id"].to_numpy(), "lr": lr, "a": is_anchor})
    stats = df[df["a"]].groupby("m")["lr"].agg(["sum", "count"])
    prec = stats["count"] / resid_sd**2 + 1 / prior_sd**2
    gain = np.exp((stats["sum"] / resid_sd**2) / prec)
    g = ev["machine_id"].map(gain).fillna(1.0).to_numpy()
    return out * g, is_anchor


def fuse(estimates: list[np.ndarray], sds: list[float]) -> np.ndarray:
    """Inverse-variance fusion in log space (sds = relative 1-sigma of each estimator)."""
    w = np.array([1 / s**2 for s in sds])
    logs = np.vstack([np.log(np.clip(e, 1, None)) for e in estimates])
    return np.exp((w[:, None] * logs).sum(axis=0) / w.sum())


def ml_features(ev: pd.DataFrame, f_obs, p_bar, t_oil_obs) -> pd.DataFrame:
    X = pd.DataFrame({
        "fill": f_obs, "p_bar": p_bar, "t_oil": t_oil_obs, "volume": ev["volume_m3"].to_numpy(),
        "is_combi": (ev["eq_class"] == "COMBI").astype(int).to_numpy(),
    })
    for m in ("cardboard", "plastic", "mixed"):
        X[f"mat_{m}"] = (ev["material"] == m).astype(int).to_numpy()
    X["fill_x_vol"] = X["fill"] * X["volume"]
    return X


def ml_fit_predict(X_train, y_train, X_test, seed: int = 0) -> np.ndarray:
    """Gradient-boosted trees on log mass; trained on calibration (golden-cohort) machines only."""
    mdl = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, random_state=seed)
    ok = y_train > 20
    mdl.fit(X_train[ok], np.log(y_train[ok]))
    return np.exp(mdl.predict(X_test))
