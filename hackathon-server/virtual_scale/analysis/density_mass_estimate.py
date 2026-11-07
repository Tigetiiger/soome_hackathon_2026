"""Mass = volume x density(pressure), with the density law measured on the compaction rig.

Chain per lift:
  stroke curves (50 Hz)  --edge extraction-->  end pressure, oil temperature
  end pressure - hydraulic loss(oil T)  --> face stress  --rig law(material, T)-->  density
  fill % x container volume  --> volume ;  mass = volume x density - residual after the lift
Compared per material with: today's fill x table density, the same + 5 clean tickets per machine,
and the pressure ML model (T1b) for reference. All synthetic; rig law != field truth on purpose
(the field pack is less dense far from the ram).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vscale import physics as ph  # noqa: E402
from vscale.config import PROJECT_ROOT, load_config  # noqa: E402
from vscale.features import build_lift_table  # noqa: E402
from vscale.model import anchor_calibrate, lift_metrics, oof_predict  # noqa: E402
from vscale.rig import fit_all  # noqa: E402
from vscale.traces import extract_features, generate_trace  # noqa: E402

DATA = PROJECT_ROOT / "data"
REP = PROJECT_ROOT / "reports"
N_TRACE_CHECK = 400
N_TRACE_SAVE = 30
RESIDUAL_STRESS_KPA = 5.0
ANCHORS = 5


def trace_check(cycles: pd.DataFrame, cfg: dict, rng: np.random.Generator) -> pd.DataFrame:
    """Generate full curves from sampled cycles, extract features back, measure extraction error."""
    hyd = cfg["hydraulics"]
    s = cycles.sample(N_TRACE_CHECK, random_state=1).reset_index(drop=True)
    rows, saved = [], []
    for i, r in s.iterrows():
        loss = float(ph.hydraulic_loss_bar(r.oil_temp_c, hyd["loss_bar_at_40c"], hyd["loss_temp_coeff"]))
        relief = 200.0
        t, p = generate_trace(rng, loss, float(r.p_plateau_bar), float(r.p_end_bar), float(r.stroke_completion), relief)
        f = extract_features(t, p, relief)
        rows.append({"p_end_logged": r.p_end_bar, "p_end_extracted": f.p_end_bar,
                     "p_plateau_logged": r.p_plateau_bar, "p_plateau_extracted": f.p_plateau_bar})
        if i < N_TRACE_SAVE:
            saved.append(pd.DataFrame({"cycle_uid": f"{r.device_id}|{r.cycle_at}", "device_id": r.device_id,
                                       "true_mass_kg": r.true_mass_kg, "t_s": t.astype("float32"), "p_bar": p.astype("float32")}))
    pd.concat(saved).to_parquet(DATA / "pressure_traces.parquet", index=False)
    d = pd.DataFrame(rows)
    return pd.DataFrame({
        "signal": ["end pressure", "plateau pressure"],
        "bias_bar": [(d.p_end_extracted - d.p_end_logged).mean(), (d.p_plateau_extracted - d.p_plateau_logged).mean()],
        "sd_bar": [(d.p_end_extracted - d.p_end_logged).std(), (d.p_plateau_extracted - d.p_plateau_logged).std()],
    }).round(2)


def rig_estimate(df: pd.DataFrame, cfg: dict, laws: dict) -> np.ndarray:
    hyd = cfg["hydraulics"]
    est = np.full(len(df), np.nan)
    loss = ph.hydraulic_loss_bar(df.oil_last_c.to_numpy(), hyd["loss_bar_at_40c"], hyd["loss_temp_coeff"])
    for (mat, cls), g in df.groupby(["material", "equipment_class"], observed=True):
        idx = g.index.to_numpy()
        geo = cfg["press"][cls]
        sig = ph.bar_to_face_kpa(np.maximum(g.p_end_last.to_numpy() - loss[idx], 0), geo["a_cyl_m2"], geo["a_face_m2"])
        law = laws[mat]
        rho = law.density(sig, g.ambient_last_c.to_numpy())
        V = g.container_volume_m3.to_numpy()
        before = g.fill_last.to_numpy() / 100 * V * rho
        resid = g.fill_after_pct.to_numpy() / 100 * V * law.density(np.full(len(g), RESIDUAL_STRESS_KPA))
        est[idx] = np.maximum(before - resid, 50.0)
    return est


def table_estimate(df: pd.DataFrame, cfg: dict) -> np.ndarray:
    rho = df.material.astype(str).map({k: v["rho_ref"] for k, v in cfg["materials"].items()}).to_numpy()
    V = df.container_volume_m3.to_numpy()
    return np.maximum((df.fill_last.to_numpy() - df.fill_after_pct.to_numpy()) / 100 * V * rho, 50.0)


def fig_rig(meas: pd.DataFrame, laws: dict, out: Path) -> None:
    mats = sorted(laws)
    fig, axes = plt.subplots(3, 3, figsize=(12, 10))
    for ax, mat in zip(axes.flat, mats):
        d = meas[meas.material == mat]
        for (temp, wet), g in d.groupby(["temp_c", "wet"]):
            ax.scatter(g.face_stress_kpa, g.density_kg_m3, s=4, alpha=0.35, label=f"{temp:+.0f} C{' wet' if wet else ''}")
        s = np.linspace(0, 200, 100)
        ax.plot(s, laws[mat].density(s, 10.0), "k-", lw=1.5, label="fitted law (10 C, dry)")
        ax.set_title(mat, fontsize=10)
        ax.set_xlabel("face stress (kPa)", fontsize=8)
        ax.set_ylabel("density (kg/m3)", fontsize=8)
        ax.legend(fontsize=6)
    fig.suptitle("Virtual compaction rig: measured density vs pressure per material (synthetic)")
    fig.tight_layout()
    fig.savefig(out / "fig5_rig_density_laws.png", dpi=120)
    plt.close(fig)


def fig_traces(out: Path) -> None:
    tr = pd.read_parquet(DATA / "pressure_traces.parquet")
    fig, ax = plt.subplots(figsize=(9, 4))
    for _, g in list(tr.groupby("cycle_uid"))[:6]:
        ax.plot(g.t_s, g.p_bar, lw=0.8, label=f"{g.true_mass_kg.iloc[0]:,.0f} kg in container")
    ax.set(xlabel="seconds", ylabel="hydraulic pressure (bar)", title="Synthetic 50 Hz stroke curves (what the transducer logs)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "fig6_stroke_curves.png", dpi=120)
    plt.close(fig)


def fig_by_material(res: pd.DataFrame, out: Path) -> None:
    piv = res.pivot(index="material", columns="method", values="median_ape_pct")
    ax = piv.plot.bar(figsize=(10, 4.5))
    ax.set(ylabel="median abs. error per lift (%)", title="Mass = volume x density(pressure): error by material (synthetic)")
    ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(out / "fig7_error_by_material.png", dpi=120)
    plt.close()


def main() -> None:
    cfg = load_config()
    rng = np.random.default_rng(11)
    cycles = pd.read_parquet(DATA / "cycles.parquet")
    lifts = pd.read_parquet(DATA / "lifts.parquet")
    meas = pd.read_parquet(DATA / "rig_measurements.parquet")
    laws = fit_all(cfg, meas)

    tc = trace_check(cycles, cfg, rng)
    df = build_lift_table(cycles, lifts, cfg).reset_index(drop=True)
    del cycles

    methods = {
        "1 today: fill x table density": table_estimate(df, cfg),
        "2 pressure -> rig density x fill x volume": rig_estimate(df, cfg, laws),
    }
    methods["3 = 2 + 5 clean tickets per machine"] = anchor_calibrate(df, methods["2 pressure -> rig density x fill x volume"], ANCHORS)[0]
    ml = oof_predict(df, "T1b_pressure_plus").pred
    methods["4 ML (T1b) + 5 tickets, reference"] = anchor_calibrate(df, ml, ANCHORS)[0]

    true = df.true_collected_kg.to_numpy()
    rows = []
    for name, est in methods.items():
        rows.append({"material": "ALL", "method": name, **lift_metrics(true, est),
                     "median_bias_pct": 100 * float(np.median(est / true - 1))})
        for mat, g in df.groupby("material", observed=True):
            i = g.index.to_numpy()
            rows.append({"material": mat, "method": name, **lift_metrics(true[i], est[i]),
                         "median_bias_pct": 100 * float(np.median(est[i] / true[i] - 1))})
    res = pd.DataFrame(rows).round(3)
    res.to_csv(REP / "density_estimator_by_material.csv", index=False)
    tc.to_csv(REP / "trace_extraction_check.csv", index=False)
    fig_rig(meas, laws, REP)
    fig_traces(REP)
    fig_by_material(res[res.material != "ALL"], REP)

    pd.set_option("display.width", 220)
    print("trace extraction check\n", tc.to_string(index=False), "\n")
    print(res.pivot(index="material", columns="method", values="median_ape_pct").round(1).to_string(), "\n")
    print(res[res.material == "ALL"].drop(columns="material").to_string(index=False))


if __name__ == "__main__":
    main()
