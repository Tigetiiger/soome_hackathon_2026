"""Fleet simulator: what cheap sensors and real scales would record for every lift in the pack.

Grounding in the Europress pack: device roster (class, volume, material, operator), site
(region, opening hours, outdoor staging) and the completed lift timeline with the mass in
the container before/after each lift (`device_mass_kg_before/after`). That mass is taken as
the TRUE mass of this synthetic world. Between two lifts the intake is split into compaction
cycles; each cycle produces the signals in CYCLE_COLUMNS. At each lift the operator's
weighbridge and (for the golden cohort) a platform scale produce weighings.
"""
from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from vscale import physics as ph
from vscale.config import DEFAULT_OUT, DEFAULT_PACK, Paths, load_config
from vscale.scales import make_fleet_vehicles, weigh_lift

log = logging.getLogger(__name__)

HEL_UTC_OFFSET_H = 2
MAX_CYCLES_PER_LIFT = 400
MIN_INTAKE_KG = 30.0
CYCLE_SIZE_DEVICE_CV = 0.35    # site habit: kg loaded per press [hyp]
CYCLE_SIZE_INTERVAL_CV = 0.25  # drift of that habit between emptyings [hyp]
SIM_START = pd.Timestamp("2025-10-01", tz="UTC")


@dataclass(frozen=True)
class DeviceParams:
    """Hidden per-device truth (kept for diagnostics, never used as a model feature)."""
    device_id: str
    sigma_c_scale: float
    mu: float
    a_cyl: float
    a_face: float
    p_gain: float
    p_offset: float
    p_drift_bar_per_day: float
    fill_gain: float
    fill_bias: float
    strain_share: float
    golden: bool


def sample_device(rng: np.random.Generator, cfg: dict, dev: pd.Series, golden: bool) -> DeviceParams:
    mat = cfg["materials"][dev.material_stream]
    press = cfg["press"]
    geo = press[dev.equipment_class]
    pt = cfg["sensors"]["pressure_transducer"]
    fl = cfg["sensors"]["fill"]
    drift = rng.normal(0, pt["drift_bar_per_year_sd"]) / 365 if rng.random() < pt["drift_prob"] else 0.0
    return DeviceParams(
        device_id=dev.device_id,
        sigma_c_scale=float(rng.lognormal(0, mat["sigma_c_cv"])),
        mu=float(mat["mu"] * rng.lognormal(0, press["mu_device_cv"])),
        a_cyl=float(geo["a_cyl_m2"] * rng.lognormal(0, press["area_tolerance_cv"])),
        a_face=float(geo["a_face_m2"] * rng.lognormal(0, press["area_tolerance_cv"])),
        p_gain=float(rng.normal(1, pt["gain_cv"])),
        p_offset=float(rng.normal(0, pt["offset_sd_bar"])),
        p_drift_bar_per_day=float(drift),
        fill_gain=float(rng.normal(1, fl["gain_sd"])),
        fill_bias=float(rng.normal(0, fl["bias_sd_pp"])),
        strain_share=float(cfg["sensors"]["frame_strain"]["load_share"] * rng.lognormal(0, 0.10)),
        golden=golden,
    )


# ----------------------------------------------------------------------------- weather
def daily_weather(rng: np.random.Generator, cfg: dict, region: str, days: pd.DatetimeIndex) -> pd.DataFrame:
    """Daily mean temperature (AR(1) anomaly around Finnish normals) and rain flag."""
    cl = cfg["climate"]
    normals = np.asarray(cl[region], dtype=float)  # Oct..Sep
    month_idx = (days.month.to_numpy() - 10) % 12
    anomaly = np.zeros(len(days))
    for i in range(1, len(days)):
        anomaly[i] = 0.75 * anomaly[i - 1] + rng.normal(0, cl["daily_sd_c"] * np.sqrt(1 - 0.75 ** 2))
    temp = normals[month_idx] + anomaly
    rain = rng.random(len(days)) < cl["rain_day_prob"] * np.where(temp < -1, 0.3, 1.0)  # snow stays drier
    return pd.DataFrame({"temp_c": temp, "rain": rain}, index=days.normalize())


# ----------------------------------------------------------------------------- cycle timing
def parse_hours(spec: str) -> tuple[int, int]:
    a, b = spec.split("-")
    return int(a), int(b)


def sample_cycle_times(rng, start, end, n, open_days: str, hours: tuple[int, int]) -> pd.DatetimeIndex:
    """n timestamps in [start, end) during site opening hours (local time), sorted."""
    span = (end - start).total_seconds()
    if span <= 0:
        return pd.DatetimeIndex([end - pd.Timedelta(minutes=1)] * n)
    out: list[np.ndarray] = []
    got = 0
    mask = np.array([c == "1" for c in open_days])
    for _ in range(20):
        cand = start + pd.to_timedelta(rng.random(max(4 * n, 16)) * span, unit="s")
        local = cand + pd.Timedelta(hours=HEL_UTC_OFFSET_H)
        ok = mask[local.day_of_week] & (local.hour >= hours[0]) & (local.hour < hours[1])
        keep = cand[ok].tz_convert(None).to_numpy()
        out.append(keep)
        got += keep.size
        if got >= n:
            break
    pool = np.concatenate(out) if out else np.array([], dtype="datetime64[ns]")
    if pool.size < n:  # site closed for the whole window: fall back to any time
        extra = start + pd.to_timedelta(rng.random(n - pool.size) * span, unit="s")
        pool = np.concatenate([pool, extra.tz_convert(None).to_numpy()]) if pool.size else extra.tz_convert(None).to_numpy()
    return pd.DatetimeIndex(np.sort(pool[:n])).tz_localize("UTC")  # numpy datetimes are naive UTC


# ----------------------------------------------------------------------------- truth from the pack
def lift_truth(ce: pd.DataFrame, dev: pd.Series, mat_cfg: dict) -> pd.DataFrame:
    """True mass before/after each lift. Pack device mass is used as truth; if it is missing or
    implausible versus fill, fall back to fill x volume x typical density."""
    lifts = ce[(ce.device_id == dev.device_id) & ce.status.isin(["COMPLETED", "PARTIAL"])].sort_values("actual_at")
    if lifts.empty:
        return lifts.assign(true_before_kg=[], true_after_kg=[])
    fill_based = lifts.device_fill_pct_before.fillna(75.0) / 100 * dev.container_volume_m3 * mat_cfg["rho_ref"]
    before = lifts.device_mass_kg_before
    ratio = before / fill_based.clip(lower=1)
    use_pack = before.notna() & ratio.between(0.3, 3.0)
    true_before = np.where(use_pack, before, fill_based)
    after = lifts.device_mass_kg_after.clip(lower=0).fillna(0.0)
    after = np.minimum(after.to_numpy(), 0.6 * true_before)
    return lifts.assign(true_before_kg=np.maximum(true_before, 50.0), true_after_kg=after,
                        truth_source=np.where(use_pack, "PACK_DEVICE_MASS", "FILL_X_DENSITY"))


# ----------------------------------------------------------------------------- one device
def simulate_device(rng, cfg, dev, site, ce, operator_vehicles, op_share_prob, golden):
    mat = cfg["materials"][dev.material_stream]
    press = cfg["press"]
    geo = press[dev.equipment_class]
    hyd = cfg["hydraulics"]
    sens = cfg["sensors"]
    p = sample_device(rng, cfg, dev, golden)
    V = float(dev.container_volume_m3)
    sigma_relief = ph.relief_stress_kpa(geo["relief_bar"], p.a_cyl, p.a_face)
    law = ph.material_law(mat["rho_loose"], mat["rho_ref"], mat["inf_factor"],
                          press["reference_stress_frac"] * sigma_relief)
    k_conf = press["confinement_k_frac"] * sigma_relief

    lifts = lift_truth(ce, dev, mat)
    if lifts.empty:
        return None, None, p
    days = pd.date_range(SIM_START - pd.Timedelta(days=60), lifts.actual_at.max().normalize() + pd.Timedelta(days=1), freq="D")
    wx = daily_weather(rng, cfg, site.region_code, days)
    day_factor = pd.Series(rng.lognormal(0, mat["daily_cv"], len(days)), index=wx.index)
    hours = parse_hours(site.opening_hours_local)
    outdoor = bool(site.outdoor_material_staging) and mat["moisture_sensitive"]
    strain_zero_walk = 0.0
    oil_temp = None
    prev_end = None
    residual = 0.0
    median_gap = lifts.actual_at.diff().median()
    median_gap = median_gap if pd.notna(median_gap) else pd.Timedelta(days=7)
    cyc_rows, lift_rows = [], []
    habit = rng.lognormal(0, CYCLE_SIZE_DEVICE_CV)

    for lift in lifts.itertuples():
        start = prev_end if prev_end is not None else lift.actual_at - median_gap
        intake = max(lift.true_before_kg - residual, MIN_INTAKE_KG)
        # how much waste users load per press varies by site habit and over time, so the cycle
        # count is only a loose proxy of mass (otherwise it would leak the answer)
        kg_per_cycle = mat["event_kg"] * habit * rng.lognormal(0, CYCLE_SIZE_INTERVAL_CV)
        n = int(np.clip(rng.poisson(intake / kg_per_cycle), 1, MAX_CYCLES_PER_LIFT))
        charges = rng.lognormal(0, 0.5, n)
        charges = charges / charges.sum() * intake
        mass = residual + np.cumsum(charges)
        ts = sample_cycle_times(rng, start, lift.actual_at, n, site.opening_days_mon_sun, hours)
        dkey = ts.normalize()
        wday = wx.reindex(dkey, method="nearest")
        hour_local = (ts.hour + HEL_UTC_OFFSET_H) % 24
        ambient = wday.temp_c.to_numpy() + cfg["climate"]["diurnal_amp_c"] * np.sin((hour_local - 9) / 24 * 2 * np.pi)

        # material state of the pack = mass-weighted mean of the daily properties of its layers
        wet = np.where(outdoor & wday.rain.to_numpy(), rng.uniform(0.3, 1.0, n), 0.0)
        cold = mat["cold_stiffening"] * np.clip(-ambient / 20.0, 0, 1)
        layer_scale = day_factor.reindex(dkey, method="nearest").to_numpy() * (1 + cold) * (1 - cfg["climate"]["rain_softening"] * wet)
        w = np.concatenate([[residual], charges])
        s = np.concatenate([[1.0], layer_scale])
        pack_scale = p.sigma_c_scale * (np.cumsum(w * s)[1:] / np.cumsum(w)[1:])
        frozen = ambient < -2
        mu = p.mu * np.where(wet > 0, press["mu_wet_factor"], 1.0) * np.where(frozen, press["mu_frozen_factor"], 1.0)

        st = ph.solve_press_state(mass, V, law, pack_scale, mu, p.a_face, k_conf, press["confinement_exp"],
                                  press["lock_mid"], press["lock_width"], cfg["gravity"],
                                  gradient_a=press.get("density_gradient_a", 0.0))
        completion = ph.stroke_completion(st.sigma_end, sigma_relief)
        sigma_end_seen = np.minimum(st.sigma_end, sigma_relief)
        sigma_plateau = st.sigma_slide + 0.25 * st.sigma_conf

        # oil temperature: warms with use, relaxes toward ambient between cycles
        dt_h = np.diff(ts.asi8, prepend=ts.asi8[0]) / 3.6e12
        oil = np.empty(n)
        cur = ambient[0] + 5 if oil_temp is None else oil_temp
        for i in range(n):
            cur = ambient[i] + (cur - ambient[i]) * np.exp(-dt_h[i] / hyd["oil_cooling_tau_h"]) + hyd["oil_warmup_per_cycle_c"]
            oil[i] = cur
        oil_temp = cur
        loss = ph.hydraulic_loss_bar(oil, hyd["loss_bar_at_40c"], hyd["loss_temp_coeff"])

        # pressure transducer (bar): gain, offset, drift, noise
        days_in = (ts - SIM_START).total_seconds().to_numpy() / 86400
        pt = sens["pressure_transducer"]
        def meas_bar(true_bar, rel_noise):
            noise = rng.normal(0, 1, n) * np.sqrt((pt["noise_fs"] * pt["full_scale_bar"]) ** 2 + (rel_noise * true_bar) ** 2)
            return p.p_gain * true_bar + p.p_offset + p.p_drift_bar_per_day * days_in + noise
        p_end_true = ph.face_kpa_to_bar(sigma_end_seen, p.a_cyl, p.a_face) + loss
        p_plat_true = ph.face_kpa_to_bar(sigma_plateau, p.a_cyl, p.a_face) + loss
        p_end = meas_bar(p_end_true, 0.01)
        p_plat = meas_bar(p_plat_true, pt["plateau_noise_rel"])

        work = ph.cycle_work_kj(sigma_plateau, sigma_end_seen, p.a_face, geo["stroke_m"], completion)
        idle_kj = loss * ph.KPA_PER_BAR * p.a_cyl * geo["stroke_m"] * 2.0
        motor_wh = (work + idle_kj) / press["motor_efficiency"] / 3.6
        motor_wh_meas = motor_wh * (1 + rng.normal(0, sens["motor_current_ct"]["noise_rel"], n))

        fl = sens["fill"]
        fill = np.clip(p.fill_gain * 100 * np.minimum(st.phi, 1.05) + p.fill_bias + rng.normal(0, fl["sigma_pp"], n), 0, 100)

        fs = sens["frame_strain"]
        strain_zero_walk += rng.normal(0, fs["zero_walk_kg_per_sqrt_day"] * np.sqrt(max((lift.actual_at - start).days, 1)))
        position = 1 + 0.15 * (st.phi - 0.6)
        strain = (p.strain_share * rng.lognormal(0, 0.05) * position * mass + fs["temp_drift_kg_per_c"] * (ambient - 10)
                  + strain_zero_walk + rng.normal(0, fs["noise_kg"], n))
        pl = sens["platform_scale"]
        platform = mass + rng.normal(0, 1, n) * np.maximum(pl["sigma_abs_kg"], pl["sigma_rel"] * mass)

        cyc_rows.append(pd.DataFrame({
            "device_id": dev.device_id, "collection_id": lift.collection_id, "cycle_at": ts,
            "fill_pct": fill.astype("float32"), "p_plateau_bar": p_plat.astype("float32"), "p_end_bar": p_end.astype("float32"),
            "stroke_completion": completion.astype("float32"), "motor_wh": motor_wh_meas.astype("float32"),
            "oil_temp_c": (oil + rng.normal(0, sens["oil_temp_probe"]["noise_c"], n)).astype("float32"),
            "ambient_temp_c": ambient.astype("float32"), "frame_strain_kg": strain.astype("float32"),
            "platform_kg": platform.astype("float32"),
            "true_mass_kg": mass.astype("float32"), "true_volume_frac": st.phi.astype("float32"),
            "true_density_kg_m3": st.density.astype("float32"), "true_face_stress_kpa": st.sigma_end.astype("float32"),
            "true_wetness": wet.astype("float32"),
        }))

        residual_meas_fill = float(np.clip(p.fill_gain * 100 * lift.true_after_kg / (law.density(5.0, pack_scale[-1]) * V)
                                           + p.fill_bias + rng.normal(0, fl["sigma_pp"]), 0, 100))
        collected = lift.true_before_kg - lift.true_after_kg
        wb = weigh_lift(rng, cfg, collected, operator_vehicles, op_share_prob)
        lift_rows.append({
            "collection_id": lift.collection_id, "device_id": dev.device_id, "lift_at": lift.actual_at,
            "lift_status": lift.status, "operator_id": dev.operator_id, "material": dev.material_stream,
            "equipment_class": dev.equipment_class, "container_volume_m3": V, "region_code": site.region_code,
            "outdoor_staging": bool(site.outdoor_material_staging), "golden_cohort": golden,
            "fill_after_pct": residual_meas_fill,
            "platform_after_kg": float(lift.true_after_kg + rng.normal(0, max(pl["sigma_abs_kg"], pl["sigma_rel"] * lift.true_after_kg))),
            "true_before_kg": lift.true_before_kg, "true_after_kg": lift.true_after_kg, "true_collected_kg": collected,
            "truth_source": lift.truth_source, **wb,
        })
        residual = lift.true_after_kg
        prev_end = lift.actual_at

    return pd.concat(cyc_rows, ignore_index=True), pd.DataFrame(lift_rows), p


def run(paths: Paths, cfg: dict, max_devices: int | None = None) -> dict[str, pd.DataFrame]:
    paths.validate()
    rng = np.random.default_rng(cfg["seed"])
    devices = pd.read_parquet(paths.pack / "reference" / "devices.parquet")
    sites = pd.read_parquet(paths.pack / "reference" / "sites.parquet").set_index("site_id")
    ce = pd.read_parquet(paths.pack / "operations" / "collection_events.parquet")
    share = load_operator_share(paths)
    vehicles = make_fleet_vehicles(rng, cfg, sorted(devices.operator_id.unique()))
    if max_devices:
        devices = devices.head(max_devices)
    if cfg.get("extra_fleet", {}).get("enabled"):
        x_dev, x_ce = extra_fleet(np.random.default_rng(cfg["seed"] + 1), cfg, sites)
        devices = pd.concat([devices, x_dev], ignore_index=True)
        ce = pd.concat([ce, x_ce], ignore_index=True)
    golden_ids = set(devices.sample(frac=cfg["scales"]["golden_cohort_share"], random_state=cfg["seed"]).device_id)
    cycles, lifts, params = [], [], []
    for i, dev in enumerate(devices.itertuples()):
        c, l, prm = simulate_device(rng, cfg, dev, sites.loc[dev.site_id], ce, vehicles[dev.operator_id],
                                    share.get(dev.operator_id, 0.0), dev.device_id in golden_ids)
        params.append(prm.__dict__)
        if c is not None:
            cycles.append(c)
            lifts.append(l)
        if (i + 1) % 50 == 0:
            log.info("simulated %d / %d devices", i + 1, len(devices))
    return {"cycles": pd.concat(cycles, ignore_index=True), "lifts": pd.concat(lifts, ignore_index=True),
            "device_truth": pd.DataFrame(params)}


def extra_fleet(rng: np.random.Generator, cfg: dict, sites: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Synthetic devices + lift timeline for streams the pack does not contain (glass, cans).

    Intake per day is drawn per device; the container is emptied when it reaches a random share of
    its capacity at the stream's typical compacted density. The mass before a lift is the truth.
    """
    xf = cfg["extra_fleet"]
    dev_rows, ce_rows = [], []
    site_ids = sites.index.to_numpy()
    for mat, spec in xf["streams"].items():
        rho_ref = cfg["materials"][mat]["rho_ref"]
        for j in range(xf["devices_per_material"]):
            did = f"X-{mat[:3].upper()}-{j + 1:03d}"
            vol = float(rng.choice(spec["volumes"]))
            op = str(rng.choice(xf["operators"]))
            dev_rows.append({"device_id": did, "site_id": str(rng.choice(site_ids)), "equipment_class": str(rng.choice(spec["equipment"])),
                             "container_volume_m3": vol, "material_stream": mat, "operator_id": op})
            daily = rng.uniform(*spec["daily_kg"])
            t = SIM_START + pd.Timedelta(days=float(rng.uniform(0, 10)))
            k = 0
            while t < SIM_START + pd.Timedelta(days=xf["days"]):
                target = rng.uniform(*xf["lift_fill_frac"]) * vol * rho_ref
                t = t + pd.Timedelta(days=float(target / (daily * rng.lognormal(0, 0.2))))
                k += 1
                after = float(rng.uniform(0, 0.03) * target)
                ce_rows.append({"collection_id": f"{did}-L{k:03d}", "device_id": did, "status": "COMPLETED",
                                "actual_at": t.floor("min"), "device_mass_kg_before": target,
                                "device_mass_kg_after": after, "device_fill_pct_before": 100 * target / (vol * rho_ref)})
    ce = pd.DataFrame(ce_rows)
    ce["actual_at"] = pd.to_datetime(ce.actual_at, utc=True)
    return pd.DataFrame(dev_rows), ce


def load_operator_share(paths: Paths) -> dict[str, float]:
    """Weighbridge sharing probability per operator, from the pack's assumptions.yaml."""
    import yaml
    a = paths.pack.parents[2] / "configs" / "assumptions.yaml"
    if not a.exists():
        return {}
    ops = yaml.safe_load(a.read_text(encoding="utf-8"))["operators"]
    return {k: float(v["weighbridge_share_prob"]) for k, v in ops.items()}


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pack", default=str(DEFAULT_PACK))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--max-devices", type=int, default=None)
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    from pathlib import Path
    paths = Paths(pack=Path(a.pack), out=Path(a.out))
    tables = run(paths, load_config(), a.max_devices)
    paths.out.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_parquet(paths.out / f"{name}.parquet", index=False)
        log.info("wrote %s: %d rows", name, len(df))


if __name__ == "__main__":
    main()
