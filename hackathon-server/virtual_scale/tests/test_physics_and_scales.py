import numpy as np
import pandas as pd
import pytest

from vscale import physics as ph
from vscale.config import load_config
from vscale.model import anchor_calibrate, lift_metrics
from vscale.scales import make_fleet_vehicles, round_to, weigh_lift


@pytest.fixture(scope="module")
def cfg():
    return load_config()


def _law(cfg, mat="cardboard", cls="DUO"):
    g = cfg["press"][cls]
    srel = ph.relief_stress_kpa(g["relief_bar"], g["a_cyl_m2"], g["a_face_m2"])
    m = cfg["materials"][mat]
    return ph.material_law(m["rho_loose"], m["rho_ref"], m["inf_factor"], cfg["press"]["reference_stress_frac"] * srel), srel


def test_material_law_hits_reference_density(cfg):
    law, srel = _law(cfg)
    rho = law.density(np.array([cfg["press"]["reference_stress_frac"] * srel]))
    assert rho[0] == pytest.approx(cfg["materials"]["cardboard"]["rho_ref"], rel=1e-9)


def test_material_law_inverse_roundtrip(cfg):
    law, _ = _law(cfg, "mixed_waste")
    sig = np.array([1.0, 20.0, 80.0, 150.0])
    assert np.allclose(law.stress_for_density(law.density(sig)), sig, rtol=1e-6)


def test_material_law_rejects_bad_order():
    with pytest.raises(ValueError):
        ph.material_law(200, 190, 1.4, 100)


def test_press_state_solves_balance_and_is_monotone(cfg):
    law, srel = _law(cfg)
    m = np.linspace(200, 4500, 30)
    st = ph.solve_press_state(m, 20.0, law, 1.0, 0.45, 1.45, 0.85 * srel, 3.0, 0.45, 0.10)
    assert np.allclose(st.sigma_end, st.sigma_slide + st.sigma_conf, rtol=1e-6, atol=1e-6)
    assert np.all(np.diff(st.sigma_end) > 0), "more mass must need more pressure"
    assert np.all(np.diff(st.phi) > 0), "more mass must fill more volume"
    assert np.allclose(st.phi * st.density * 20.0, m, rtol=1e-6)


def test_softer_material_packs_denser(cfg):
    law, srel = _law(cfg)
    m = np.array([3000.0])
    stiff = ph.solve_press_state(m, 20.0, law, 1.2, 0.45, 1.45, 0.85 * srel, 3.0, 0.45, 0.10)
    soft = ph.solve_press_state(m, 20.0, law, 0.8, 0.45, 1.45, 0.85 * srel, 3.0, 0.45, 0.10)
    assert soft.phi[0] < stiff.phi[0]


def test_hydraulic_loss_grows_when_cold():
    assert ph.hydraulic_loss_bar(-10, 6, 0.035) > ph.hydraulic_loss_bar(40, 6, 0.035) == pytest.approx(6)


def test_stroke_stalls_above_relief():
    c = ph.stroke_completion(np.array([50.0, 100.0, 120.0, 400.0]), 100.0)
    assert c[0] == c[1] == 1.0 and 0.25 <= c[3] < c[2] < 1.0


def test_bar_face_conversion_roundtrip():
    s = ph.bar_to_face_kpa(120.0, 0.0126, 1.45)
    assert ph.face_kpa_to_bar(s, 0.0126, 1.45) == pytest.approx(120.0)


def test_pressure_trace_shape():
    t, p = ph.pressure_trace(6, 20, 120, 1.0, 200)
    assert t.shape == p.shape and p.max() == pytest.approx(120, rel=0.01)


def test_weighbridge_clean_ticket_close_to_truth(cfg):
    rng = np.random.default_rng(0)
    veh = make_fleet_vehicles(rng, cfg, ["OP-X"])["OP-X"]
    errs = []
    for _ in range(2000):
        t = weigh_lift(rng, cfg, 3000.0, veh, 1.0)
        if t["wb_clean_anchor"]:
            errs.append(t["wb_allocated_net_kg"] - 3000.0)
    errs = np.array(errs)
    assert len(errs) > 500
    assert abs(np.median(errs)) <= 20 and np.quantile(np.abs(errs), 0.9) < 120


def test_never_sharing_operator_gives_no_anchor(cfg):
    rng = np.random.default_rng(1)
    veh = make_fleet_vehicles(rng, cfg, ["OP-D"])["OP-D"]
    assert not any(weigh_lift(rng, cfg, 2000.0, veh, 0.0)["wb_shared"] for _ in range(200))


def test_round_to_resolution():
    assert round_to(3009.0, 20) == 3000.0 and round_to(3011.0, 20) == 3020.0


def test_anchor_calibration_removes_device_gain():
    n = 30
    df = pd.DataFrame({"device_id": ["D1"] * n, "lift_at": pd.date_range("2026-01-01", periods=n, freq="D"),
                       "label_kg": np.full(n, 2000.0)})
    pred = np.full(n, 2500.0)  # model is 25 % high on this machine
    cal, used = anchor_calibrate(df, pred)
    assert used[0] == 0 and cal[0] == 2500.0, "first lift has no earlier anchor"
    assert abs(cal[-1] / 2000.0 - 1) < 0.08 and used[-1] == n - 1


def test_lift_metrics_perfect():
    t = np.array([1000.0, 3000.0])
    m = lift_metrics(t, t)
    assert m["median_ape_pct"] == 0 and m["within_10pct_ge1t"] == 1.0 and m["within_100kg_2.5-3.5t"] == 1.0
