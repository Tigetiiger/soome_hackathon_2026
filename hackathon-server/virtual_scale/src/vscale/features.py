"""Lift-level features: what the controller would summarise from the cycles before an emptying.

Only MEASURED columns and NOMINAL engineering constants are used here (catalogue press areas,
nominal material laws, nominal hydraulic loss curve). Hidden per-device truth is never used.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from vscale import physics as ph

LAST_N = 3
STATIC_CATS = ["material", "equipment_class"]

TIER_FEATURES: dict[str, list[str]] = {
    "T0_fill_only": ["fill_last", "fill_max", "fill_after_pct", "n_cycles", "hours_since_empty",
                     "ambient_mean_c", "container_volume_m3", "month", "m_table_kg"],
    "T1a_pressure": ["p_end_last", "p_plat_last", "completion_min", "m_phys_amb_kg", "m_slide_amb_kg"],
    "T1b_pressure_plus": ["p_end_last", "p_plat_last", "completion_min", "oil_last_c", "motor_wh_sum",
                          "m_phys_oil_kg", "m_slide_oil_kg"],
    "T1s_frame_strain": ["strain_last", "strain_rise", "m_strain_kg"],
}
TIER_FEATURES["T1c_all_cheap"] = sorted(set(TIER_FEATURES["T1b_pressure_plus"]) | set(TIER_FEATURES["T1s_frame_strain"]))


def tier_columns(tier: str) -> list[str]:
    """Features available to a hardware tier. Every tier includes the existing SMART (T0) features."""
    if tier == "T0_fill_only":
        return TIER_FEATURES["T0_fill_only"] + STATIC_CATS
    return TIER_FEATURES["T0_fill_only"] + TIER_FEATURES[tier] + STATIC_CATS


def _last_n_median(g: pd.core.groupby.DataFrameGroupBy, col: str) -> pd.Series:
    return g[col].apply(lambda s: float(np.median(s.to_numpy()[-LAST_N:])))


def summarise_cycles(cycles: pd.DataFrame) -> pd.DataFrame:
    c = cycles.sort_values(["collection_id", "cycle_at"])
    g = c.groupby("collection_id", sort=False)
    out = pd.DataFrame({
        "fill_last": _last_n_median(g, "fill_pct"),
        "fill_max": g.fill_pct.max(),
        "p_end_last": _last_n_median(g, "p_end_bar"),
        "p_plat_last": _last_n_median(g, "p_plateau_bar"),
        "completion_min": g.stroke_completion.apply(lambda s: float(s.to_numpy()[-LAST_N:].min())),
        "oil_last_c": _last_n_median(g, "oil_temp_c"),
        "ambient_last_c": _last_n_median(g, "ambient_temp_c"),
        "ambient_mean_c": g.ambient_temp_c.mean(),
        "motor_wh_sum": g.motor_wh.sum(),
        "n_cycles": g.size(),
        "hours_since_empty": (g.cycle_at.max() - g.cycle_at.min()).dt.total_seconds() / 3600,
        "strain_last": _last_n_median(g, "frame_strain_kg"),
        "strain_first": g.frame_strain_kg.first(),
        "platform_last": _last_n_median(g, "platform_kg"),
    })
    out["strain_rise"] = out.strain_last - out.strain_first
    return out.reset_index()


def nominal_laws(cfg: dict) -> dict[tuple[str, str], tuple[ph.MaterialLaw, float, float]]:
    """(material, class) -> (nominal law, nominal a_cyl, nominal a_face)."""
    laws = {}
    for cls in ("COMBI", "DUO"):
        geo = cfg["press"][cls]
        srel = ph.relief_stress_kpa(geo["relief_bar"], geo["a_cyl_m2"], geo["a_face_m2"])
        for mat, m in cfg["materials"].items():
            law = ph.material_law(m["rho_loose"], m["rho_ref"], m["inf_factor"], cfg["press"]["reference_stress_frac"] * srel)
            laws[(mat, cls)] = (law, geo["a_cyl_m2"], geo["a_face_m2"])
    return laws


def physics_estimates(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Engineering estimates of collected mass with nominal constants (inputs to the ML models)."""
    laws = nominal_laws(cfg)
    hyd = cfg["hydraulics"]
    out = df.copy()
    rho_ref = out.material.map({k: v["rho_ref"] for k, v in cfg["materials"].items()})
    mu = out.material.map({k: v["mu"] for k, v in cfg["materials"].items()})
    V = out.container_volume_m3
    resid_table = out.fill_after_pct / 100 * V * rho_ref * 0.5
    out["m_table_kg"] = (out.fill_last / 100 * V * rho_ref - resid_table).clip(lower=0)
    for tag, temp in (("amb", out.ambient_last_c + 5.0), ("oil", out.oil_last_c)):
        loss = pd.Series(ph.hydraulic_loss_bar(temp, hyd["loss_bar_at_40c"], hyd["loss_temp_coeff"]), index=out.index)
        m_phys = np.full(len(out), np.nan)
        m_slide = np.full(len(out), np.nan)
        for (mat, cls), (law, a_cyl, a_face) in laws.items():
            sel = ((out.material == mat) & (out.equipment_class == cls)).to_numpy()
            if not sel.any():
                continue
            sig_end = ph.bar_to_face_kpa(np.maximum(out.p_end_last.to_numpy()[sel] - loss.to_numpy()[sel], 0), a_cyl, a_face)
            rho = law.density(sig_end)
            m_phys[sel] = out.fill_last.to_numpy()[sel] / 100 * V.to_numpy()[sel] * rho
            sig_pl = ph.bar_to_face_kpa(np.maximum(out.p_plat_last.to_numpy()[sel] - loss.to_numpy()[sel], 0), a_cyl, a_face)
            m_slide[sel] = sig_pl * 1000 * a_face / (mu.to_numpy()[sel] * cfg["gravity"])
        out[f"m_phys_{tag}_kg"] = np.maximum(m_phys - resid_table.to_numpy(), 0)
        out[f"m_slide_{tag}_kg"] = m_slide
    out["m_strain_kg"] = out.strain_rise / cfg["sensors"]["frame_strain"]["load_share"]
    out["m_platform_kg"] = out.platform_last - out.platform_after_kg
    return out


def build_lift_table(cycles: pd.DataFrame, lifts: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    s = summarise_cycles(cycles)
    df = lifts.merge(s, on="collection_id", how="inner")
    df["month"] = pd.to_datetime(df.lift_at).dt.month
    df = physics_estimates(df, cfg)
    # labels the fleet would actually have: golden-cohort platform delta, else a clean shared ticket
    df["label_kg"] = np.where(df.golden_cohort, df.m_platform_kg,
                              np.where(df.wb_clean_anchor, df.wb_allocated_net_kg, np.nan))
    df["label_source"] = np.where(df.golden_cohort, "PLATFORM", np.where(df.wb_clean_anchor, "WEIGHBRIDGE_CLEAN", "NONE"))
    for col in STATIC_CATS:
        df[col] = df[col].astype("category")
    return df
