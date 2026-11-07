"""Section A of the results site: "Simulation in detail" (formulas + parameters from the run's config)."""
from __future__ import annotations

import logging
import re
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from site_common import (ROOT, SITE, Build, copy_plots, dig, figures, load_yaml, note, num, pct_of,
                         pre, raw_table, sci, table)

SHOWN_IN_HYDRAULICS = ("pressure_graph", "pressure_vs_fill")
GEN = Path("generated")            # site-relative folder for images made by this page
LIFT_TARGET_T = {"cardboard": "2–3.5", "paper": "2.5–4", "plastic_film": "1.2–2.2", "mixed_waste": "3–6 (assumed)"}
FILL_BANDS = ((10, 25, "low (10–25 %)", "#2a9d8f"), (45, 60, "medium (45–60 %)", "#c98a00"),
              (85, 100, "high (85–100 %)", "#d62828"))


def v(cfg: dict | None, path: str, nd: int | None = None) -> str:
    """Config value at a dotted path, html-escaped; '–' when absent."""
    val = dig(cfg, *path.split("."))
    if val is None:
        return "–"
    if nd is not None and isinstance(val, (int, float)):
        return escape(num(val, nd))
    if isinstance(val, (list, tuple)):
        return escape("–".join(str(x) for x in val))
    return escape(str(val))


def why(text: str) -> str:
    return f'<p class="muted"><strong>Why:</strong> {escape(text)}</p>'


def h3(anchor: str, title: str) -> str:
    return f'<h3 id="{anchor}" class="sub">{escape(title)}</h3>'


def shares(d: dict | None, pct: bool = True) -> str:
    if not isinstance(d, dict):
        return "–"
    return escape(", ".join(f"{k} {num(x * 100, 0)} %" if pct else f"{k} {x}" for k, x in d.items()))


# ---------------------------------------------------------------- 1 fleet
def fleet(cfg: dict) -> str:
    fc = cfg.get("fleet", {})
    comp = cfg.get("compaction", {})
    rows = []
    for mat, opts in (fc.get("containers") or {}).items():
        sizes = " · ".join(f"{c} {vol} m³ ({num(w * 100, 0)} %)" for c, vol, w in opts)
        rows.append([escape(mat), escape(num(dig(fc, "material_shares", mat) * 100, 0)) + " %",
                     escape(num(dig(comp, "rho_typ_kg_m3", mat), 0)), escape(sizes)])
    models = [[escape(k), escape(str(m.get("force_t"))), escape(str(m.get("cycle_s"))), escape(str(m.get("motor_kw"))),
               escape(" × ".join(str(a) for a in m.get("aperture_m", [])))] for k, m in (fc.get("press_models") or {}).items()]
    sectors = []
    for name, s in (cfg.get("sectors") or {}).items():
        op = s.get("open", {})
        txt = " · ".join(f"{d} {'closed' if h is None else f'{h[0]}–{h[1]}'}" for d, h in op.items())
        sectors.append([escape(name), escape(txt), "closed" if s.get("closed_on_holidays") else "open"])
    sec_mat = [[escape(m)] + [escape(num(x * 100, 0)) + " %" for x in d.values()]
               for m, d in (fc.get("sector_by_material") or {}).items()]
    sec_head = ["material"] + list(next(iter((fc.get("sector_by_material") or {"": {}}).values())).keys())
    return (h3("sim-fleet", "1 · Fleet & sites")
            + f"<p>{v(cfg, 'run.n_bins')} machines, each its own site. Materials are drawn with exact shares (largest "
              "remainder). <strong>mixed_waste</strong> (household waste incl. bio waste, heavy and less condensed) replaced "
              "the brief's mixed plastic after the expert interview.</p>"
            + raw_table(["material", "share", "ρ_typ kg/m³", "containers (class, volume, weight)"], rows, left_cols={0, 3})
            + "<p><strong>COMBI</strong> = press and container are one unit, lifted together (tare "
              f"{v(cfg, 'fleet.tare_kg.COMBI')} kg, assumed); empties fully. <strong>DUO</strong> = stationary press, the "
              f"container is swapped (tare {v(cfg, 'fleet.tare_kg.DUO')} kg) and keeps a residue of "
              f"{v(cfg, 'operations.duo_residue_frac')} of the layers. Press models within each class: "
              f"{shares(dig(fc, 'press_model_shares', 'COMBI'))} (DUO the same).</p>"
            + raw_table(["press model", "force t", "cycle s", "motor kW", "aperture m"], models)
            + f"<p>Infeed: {shares(fc.get('infeed_shares'))}. Drainage on {v(cfg, 'fleet.drainage_share')} of machines; "
              f"{v(cfg, 'fleet.waterproof_share_of_undrained')} of the undrained are sealed (water pools); "
              f"{v(cfg, 'fleet.indoor_installation_share_of_shaft')} of indoor shafts sit in a heated waste room at "
              f"{v(cfg, 'moisture.indoor_installation_temp_c')} °C. Floating roof on {v(cfg, 'fleet.floating_roof.share')} "
              f"of cardboard containers ≥ {v(cfg, 'fleet.floating_roof.min_volume_m3')} m³ (+"
              f"{v(cfg, 'fleet.floating_roof.density_gain')} density). Order threshold "
              f"{shares({f'{k} %': x for k, x in (fc.get('threshold_pct_shares') or {}).items()})}. Regions: "
              f"{shares(fc.get('region_shares'))}. {v(cfg, 'fleet.ref_scale_share')} of machines carry a reference load "
              "cell.</p>"
            + raw_table(["sector", "opening hours (local)", "public holidays"], sectors, left_cols={0, 1})
            + raw_table(sec_head, sec_mat)
            + f"<p>Per-site opening hours shift by {v(cfg, 'fleet.opening_shift_h')} h. Each site's daily input is set so "
              "the container reaches its order threshold in a lognormal number of days (median "
              f"{v(cfg, 'fleet.target_cycle_days.median')}, σ_log {v(cfg, 'fleet.target_cycle_days.sigma_log')}, clipped "
              f"{v(cfg, 'fleet.target_cycle_days.min')}–{v(cfg, 'fleet.target_cycle_days.max')} d).</p>"
            + why("material, container size and site rhythm set the mass range and the cycle length; the soft sensor "
                  "must work across all of them, including container sizes it has not seen often."))


# ---------------------------------------------------------------- 2 weather
def weather(cfg: dict) -> str:
    w = cfg.get("weather", {})
    rows = [[escape(k), escape(r.get("name", "")), escape(str(r.get("jan_c"))), escape(str(r.get("jul_c"))),
             escape(str(r.get("precip_mm_year"))), escape(str(r.get("wet_day_prob"))), escape(str(r.get("rh_mean")))]
            for k, r in (w.get("regions") or {}).items()]
    t, p, h = "weather.temperature", "weather.precipitation", "weather.humidity"
    return (h3("sim-weather", "2 · Weather") + f"<p>Mode <code>{v(cfg, 'weather.mode')}</code>: daily weather per region "
            "(or replayed FMI daily observations), then disaggregated to hours.</p>"
            + raw_table(["region", "name", "Jan °C", "Jul °C", "precip mm/yr", "p(wet day)", "RH mean %"], rows, {0, 1})
            + pre(f"""
T_day(r,d) = (Jan_r + Jul_r)/2 + (Jul_r - Jan_r)/2 * season(d)  + sd(d) * a(r,d)
             season: cosine, coldest on day-of-year {v(cfg, t + '.coldest_doy')}
a(r,d)     = {v(cfg, t + '.anomaly_ar1_phi')} * a(r,d-1) + sqrt(1 - phi^2) * z     (unit-variance AR(1))
             z: {v(cfg, t + '.spatial_corr')} of the variance shared by all regions
sd(d)      = {v(cfg, t + '.anomaly_sd_summer_c')} °C (summer) ... {v(cfg, t + '.anomaly_sd_winter_c')} °C (winter)

wet(d)     = Markov chain: p11 - p01 = {v(cfg, p + '.persistence')}, p(wet) seasonal ±{v(cfg, p + '.seasonal_amp_prob')} (peak doy {v(cfg, p + '.peak_doy')})
amount     ~ Gamma(shape {v(cfg, p + '.gamma_shape')}), mean scaled to the annual total, seasonal ±{v(cfg, p + '.seasonal_amp_amount')}, min {v(cfg, p + '.min_wet_mm')} mm
             spatial correlation {v(cfg, p + '.spatial_corr')} (Gaussian copula)
RH_day     = rh_mean + rh_amp * season(peak doy {v(cfg, h + '.peak_doy')}) + {v(cfg, h + '.wet_day_bump_pct')} % on wet days + AR(1)(phi {v(cfg, h + '.ar1_phi')}, sd {v(cfg, h + '.noise_sd_pct')} %)

hourly T   = interpolated daily mean + diurnal cosine (amp {v(cfg, t + '.diurnal_amp_winter_c')}–{v(cfg, t + '.diurnal_amp_summer_c')} °C, max at {v(cfg, t + '.warmest_hour')}:00)
             + AR(1) noise (sd {v(cfg, t + '.hourly_noise_sd_c')}, phi {v(cfg, t + '.hourly_noise_phi')}), re-centred to the exact daily mean
hourly rain: block of {v(cfg, p + '.hours_base')} + {v(cfg, p + '.hours_per_sqrt_mm')}*sqrt(mm) + Exp(1) hours, Dirichlet({v(cfg, p + '.dirichlet_alpha')}) weights
snow       : precipitation while T < {v(cfg, p + '.snow_below_c')} °C; snowpack melts {v(cfg, 'weather.snowpack.degree_day_mm_per_c_day')} mm per °C-day
yard wet   : store = store * exp(-1/{v(cfg, 'weather.yard.wet_decay_h')} h) + rain + melt;  index = min(1, store / {v(cfg, 'weather.yard.wet_ref_mm')} mm)
indoor RH  : outdoor vapour pressure at {v(cfg, h + '.indoor.temp_c')} °C (Magnus) + {v(cfg, h + '.indoor.moisture_source_pct')} %, clipped {v(cfg, h + '.indoor.clip_pct')} %""")
            + why("weather is the only public input that changes how heavy a load is at the same volume (wet fibre), "
                  "and frost and cold oil change the pressure signal; it has to look like Finnish weather."))


# ---------------------------------------------------------------- 3 inflow
def inflow(cfg: dict) -> str:
    i = "inflow"
    masses = ", ".join(f"{k} {x} kg" for k, x in (dig(cfg, "inflow", "event_mass_mean_kg") or {}).items())
    return (h3("sim-inflow", "3 · Material inflow") + pre(f"""
lambda(h)  = daily_input / mean_event_mass * hour_weight(sector,h) * day_factor * month_factor * open(h)
             * daily_noise(d) * bulk(d)                    (normalised so the year averages to daily_input)
events(h)  ~ Poisson(lambda(h))
mass(h)    ~ Gamma(events * {v(cfg, i + '.event_mass_gamma_shape')}, mean_event_mass / {v(cfg, i + '.event_mass_gamma_shape')})   (sum of gamma event masses)
daily_noise: AR(1) lognormal, phi {v(cfg, i + '.daily_noise.ar1_phi')}, sigma_log {v(cfg, i + '.daily_noise.sigma_log')}
bulk(d)    = x U{v(cfg, i + '.bulk_day.multiplier')} on {v(cfg, i + '.bulk_day.prob_per_open_day')} of open days, else 1
presses(h) ~ Binomial(events, {v(cfg, i + '.press_prob_per_event')}) + Poisson({v(cfg, i + '.test_cycle_rate_per_open_hour')} test cycles per open hour)""")
            + f"<p>Mean event mass: {escape(masses)}. Holidays (Finnish public holidays incl. Easter, Ascension, "
              "Midsummer, All Saints) close every sector except hotels.</p>"
            + why("press counts and timing are real machine signals; tying them to loading events makes "
                  "\"presses since lift\" a genuine proxy for the number of loads."))


# ---------------------------------------------------------------- 4 moisture
def moisture(cfg: dict) -> str:
    m = "moisture"
    return (h3("sim-moisture", "4 · Moisture pathways") + "<p>Each pathway is tracked as its own truth column "
            "(<code>true_water_humidity_kg</code>, <code>true_water_carried_kg</code>, <code>true_water_hopper_kg</code>, "
            "<code>true_free_water_kg</code>, <code>true_ice_kg</code>), so the effect of each can be checked separately.</p>"
            + pre(f"""
humidity  EMC% = {v(cfg, m + '.emc_oswin.A')} * (h/(1-h))^{v(cfg, m + '.emc_oswin.B')}   (Oswin, h = RH/100 <= {v(cfg, m + '.emc_oswin.rh_max')})
          storage air = {v(cfg, m + '.storage_time_constant_h')} h EMA of outdoor / indoor RH, mixed by the site's outdoor-storage share
          extra = hygroscopic * (EMC - {v(cfg, m + '.reference_mc_pct')}) / (100 + {v(cfg, m + '.reference_mc_pct')})     hygroscopic: {shares(dig(cfg, m, 'hygroscopic'), False)}
carry-in  water = mass * carry_in_frac * yard_wetness   (outdoor infeeds only)   carry_in_frac: {shares(dig(cfg, m, 'carry_in_frac'), False)}
          absorbed share {shares(dig(cfg, m, 'carry_absorbed_frac'), False)}; the rest runs off as free water
hopper    rain/snow kg = mm * aperture area * ingress  (open {v(cfg, m + '.hopper_ingress.open_hopper')}, lidded {v(cfg, m + '.hopper_ingress.lidded_hopper')}, shaft {v(cfg, m + '.hopper_ingress.indoor_shaft')}), pressed in with the next stroke
          soaked up by the pack: {shares(dig(cfg, m, 'retained_frac'), False)}
free water: drainage -> drained;  standard container -> seeps out (tau {v(cfg, m + '.seepage_time_constant_h')} h);  sealed -> pools
          free water and ice add mass, not volume
frost     below {v(cfg, m + '.frost.freeze_below_c')} °C (container temp = {v(cfg, m + '.container_temp_time_constant_h')} h EMA of air): free water and hopper snow -> ice,
          melts at {v(cfg, m + '.ice_melt_rate_per_c_h')}/h per °C; wet loads freeze into lumps (+{shares(dig(cfg, m, 'frost', 'penalty'), False)} volume), thaw tau {v(cfg, m + '.frost.thaw_time_constant_h')} h
wet density: rho x (1 + coeff * moisture_extra), coeff {shares(dig(cfg, m, 'wet_density_coeff'), False)}, extra clipped {v(cfg, m + '.moisture_extra_clip')}""")
            + why("moisture is the reason a fill-based estimate drifts with the weather: water adds kilograms "
                  "without adding volume and makes fibre pack denser and softer."))


# ---------------------------------------------------------------- 5 compaction
def compaction(cfg: dict) -> str:
    c = "compaction"
    return (h3("sim-compaction", "5 · Compaction & container state") + pre(f"""
layers   one per loading day since the last lift (max {v(cfg, c + '.n_layers')}); each stores base mass, water by pathway,
         reference volume vref, frost volume and pmax = the highest pack pressure it has seen
density  rho = rho_typ * machine_factor * daily_factor * (1 + a*moisture_extra) * g(pmax)
         g(P) = (1 + c*ln(1 + P/{v(cfg, c + '.p0_bar')})) / (1 + c*ln(1 + {v(cfg, c + '.p_ref_bar')}/{v(cfg, c + '.p0_bar')}))      (log-law, plastic: a layer only gets denser)
         machine_factor: lognormal cv {v(cfg, c + '.machine_factor_cv')} * (force/{v(cfg, c + '.force_ref_t')} t)^{v(cfg, c + '.force_exponent')};  daily_factor cv {v(cfg, c + '.daily_factor_cv')}
         compressibility c: {shares(dig(cfg, c, 'compressibility'), False)}
springback right after a stroke the pack is {shares(dig(cfg, c, 'springback'), False)} denser, relaxes with tau {v(cfg, c + '.springback_time_constant_h')} h
fill     = sum(layer volume) / container volume;  material that does not fit -> side waste (true fill never > 100 %)
chamber  loads in an hour without a stroke wait in the press chamber and go in with the next stroke""")
            + "<p>The mass ledger <code>start + material in + hopper precipitation − drained − seeped − side waste − "
              "lifted = end</code> is checked per machine.</p>"
            + why("the hidden per-machine density factor and the daily scatter are exactly what a fill reading cannot "
                  "see and what the pressure has to reveal."))


# ---------------------------------------------------------------- 6 hydraulics
def hydraulics(cfg: dict, b: Build, run: Path) -> str:
    y, cv = "hydraulics", "hydraulics.curve"
    interview = raw_table(["expert said", "simulator"], [
        ["back pressure is visible from <strong>5–10 % fill</strong>, then it rises until full",
         f"<code>fill_onset {v(cfg, y + '.fill_onset')}</code>, <code>fill_exponent {v(cfg, y + '.fill_exponent')}</code> (linear)"],
        ["the ram enters only <strong>20–30 cm</strong> into the container",
         f"pressure graph rises only in the last part of the stroke (<code>ram_ingress_frac {v(cfg, cv + '.ram_ingress_frac')}</code>)"],
        ["fill tells <strong>volume; weight is a question mark</strong>",
         f"medium density dependence, <code>density_exponent {v(cfg, y + '.density_exponent')}</code>"],
        ["single strokes spike — a <strong>box crushed</strong> on the way in",
         f"spikes +{v(cfg, y + '.spikes.bar')} bar with probability {shares(dig(cfg, y, 'spikes', 'prob_per_stroke'), False)} per stroke"],
        ["the machine can log the <strong>pressure graph</strong>",
         f"{v(cfg, cv + '.n_points')} samples per stroke → per-stroke curve features"],
    ], left_cols={0, 1})
    imgs = [p for p in copy_plots(b, run / "plots") if p.stem in SHOWN_IN_HYDRAULICS]
    extra = pressure_examples(b, run, cfg)
    return (h3("sim-hydraulics", "6 · Hydraulics & the pressure signal (centrepiece)")
            + "<p>The ram pressure is the only signal that sees the pack. Its law follows what a Europress specialist "
              "told us in the expert interview (parameter <em>values</em> are assumed — real ones are unknown):</p>" + interview
            + pre(f"""
f(fill)  = clip((fill - {v(cfg, y + '.fill_onset')}) / (1 - {v(cfg, y + '.fill_onset')}), 0, 1)^{v(cfg, y + '.fill_exponent')}
demand   = k * f(fill) * stiffness * (rho/rho_typ)^{v(cfg, y + '.density_exponent')} * soft(moisture) * (1 + {v(cfg, y + '.frost_stiffening')}*frost_share)
           k = {v(cfg, y + '.k_bar')} bar (machine cv {v(cfg, y + '.k_machine_cv')}), stiffness {shares(dig(cfg, y, 'stiffness'), False)}
           soft = clip(1 - wet_softening*moisture_extra, 0.3, 1.5), wet_softening {shares(dig(cfg, y, 'wet_softening'), False)}
P_stroke = min(relief, visc(T_oil) * (P_idle + demand * resistance_noise)) + crushed-item spike
           P_idle U{v(cfg, y + '.p_idle_bar')} bar, relief {v(cfg, y + '.relief_bar')} bar (cv {v(cfg, y + '.relief_cv')}), resistance cv {v(cfg, y + '.stroke_resistance_cv')}
visc     = 1 + {v(cfg, y + '.viscosity_coeff_per_c')} * max({v(cfg, y + '.viscosity_ref_c')} - T_oil, 0)       (cold oil reads high)
T_oil    : +{v(cfg, y + '.oil.heat_per_stroke_c')} °C per stroke, cools to ambient with tau {v(cfg, y + '.oil.cool_time_constant_h')} h, max {v(cfg, y + '.oil.max_c')} °C
P_pack   = min(demand, relief/visc - P_idle)    -> the layer's pmax; density growth stalls once the valve opens""")
            + "<h4>The pressure graph (per stroke)</h4>" + pre(f"""
x        = ram position, 0 = stroke start, 1 = end; {v(cfg, cv + '.n_points')} samples
x_c      = 1 - {v(cfg, cv + '.ram_ingress_frac')} - {v(cfg, cv + '.contact_span')} * clip((fill - {v(cfg, cv + '.contact_onset')})/(1 - {v(cfg, cv + '.contact_onset')}), 0, 1)  +/- {v(cfg, cv + '.contact_noise')}   (contact point)
P(x)     = min(relief, visc * (P_idle + excess * ramp(x)^q + loose(x))) + spike bump
ramp     = clip((x - x_c)/(1 - x_c), 0, 1);  q = {v(cfg, cv + '.shape_base')} + {v(cfg, cv + '.shape_gain')}*(0.35 - c);  loose material up to {v(cfg, cv + '.loose_bar_max')} bar before contact
device   : contact_pos  = first x where P rises > {v(cfg, cv + '.contact_threshold_bar')} bar above the start   (where the pack face is)
           rise_slope   = (P_end - P_contact) / (1 - contact_pos)                 (stiffer / denser pack rises faster)
           mean_bar     = mean pressure over the stroke                             (proportional to hydraulic work)
           completion   = share of the travel done before the relief valve opened""")
            + "<p>The end-of-stroke value equals the stroke peak, so the curve is consistent with "
              "<code>peak_pressure_bar</code>. Hourly means of the four device features become the <code>curve_*</code> "
              f"columns; raw curves are kept for the first {v(cfg, cv + '.sample_bins')} machines.</p>"
            + figures(imgs + extra)
            + why("pressure is what separates a light from a heavy container at the same fill; making its "
                  "dependence on density only medium keeps the problem honest — as the expert said, weight is a "
                  "question mark."))


def _hourly_cols(run: Path, cols: list[str], bins: list[str] | None = None) -> pd.DataFrame | None:
    path = ROOT / run / "hourly.parquet"
    if not path.exists():
        return None
    filters = [("bin_id", "in", bins)] if bins else None
    return pd.read_parquet(path, columns=cols, filters=filters)


def pressure_examples(b: Build, run: Path, cfg: dict) -> list[Path]:
    """Example pressure graphs at low / medium / high true fill -> site/generated/pressure_examples.png."""
    src = b.check(run / "pressure_curves.parquet")
    if src is None:
        return []
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        curves = pd.read_parquet(src)
        fill = _hourly_cols(run, ["bin_id", "ts", "true_fill_pct"], sorted(curves["bin_id"].unique().tolist()))
        curves = curves.assign(hour=curves["ts"].dt.floor("h")).merge(
            fill.rename(columns={"ts": "hour"}), on=["bin_id", "hour"], how="left")
        thr = float(dig(cfg, "hydraulics", "curve", "contact_threshold_bar") or 15.0)
        rng = np.random.default_rng(7)
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for lo, hi, label, color in FILL_BANDS:
            keys = curves[(curves["true_fill_pct"] >= lo) & (curves["true_fill_pct"] < hi)][
                ["bin_id", "ts", "stroke_in_hour"]].drop_duplicates()
            if keys.empty:
                continue
            pick = keys.iloc[rng.choice(len(keys), min(4, len(keys)), replace=False)]
            for i, key in enumerate(pick.itertuples(index=False)):
                one = curves[(curves["bin_id"] == key.bin_id) & (curves["ts"] == key.ts)
                             & (curves["stroke_in_hour"] == key.stroke_in_hour)].sort_values("ram_position")
                x, p = one["ram_position"].to_numpy(), one["pressure_bar"].to_numpy()
                ax.plot(x, p, color=color, lw=1.4, alpha=0.85, label=label if i == 0 else None)
                rise = np.flatnonzero(p - p[0] > thr)
                if rise.size:
                    ax.plot(x[rise[0]], p[rise[0]], "o", color=color, ms=5, mec="black", mew=0.5)
        ax.set(xlabel="ram position (0 = start, 1 = end of stroke)", ylabel="pressure (bar)",
               title="Example pressure graphs by true fill (dot = detected contact point)")
        ax.legend(title="true fill", loc="upper left")
        ax.grid(alpha=0.3)
        fig.tight_layout()
        (SITE / GEN).mkdir(parents=True, exist_ok=True)
        fig.savefig(SITE / GEN / "pressure_examples.png", dpi=110)
        plt.close(fig)
        return [GEN / "pressure_examples.png"]
    except (OSError, ValueError, KeyError) as exc:
        logging.warning("pressure example plot failed: %s", exc)
        return []


# ---------------------------------------------------------------- 7 sensors
def fill_error(b: Build, run: Path) -> tuple[str, list[Path]]:
    """Mean |fill_pct - true_fill_pct| from the run, plus a hexbin plot."""
    b.check(run / "hourly.parquet")
    try:
        h = _hourly_cols(run, ["fill_pct", "true_fill_pct"])
        if h is None:
            return "", []
        h = h.dropna()
        err = (h["fill_pct"] - h["true_fill_pct"]).abs()
        hi = err[h["true_fill_pct"] >= 30]
        text = (f"<p>Measured on this run ({escape(str(run))}, {num(len(h), 0)} hourly readings): mean |fill_pct − true "
                f"fill| = <strong>{num(err.mean())} pp</strong> overall, {num(hi.mean())} pp at true fill ≥ 30 % "
                "(includes the spurious-high episodes).</p>")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        sample = h.sample(min(len(h), 400_000), random_state=7)
        fig, ax = plt.subplots(figsize=(5.6, 4.5))
        hb = ax.hexbin(sample["true_fill_pct"], sample["fill_pct"], gridsize=50, bins="log", cmap="viridis", mincnt=1)
        ax.plot([0, 100], [0, 100], color="white", lw=1, ls="--")
        fig.colorbar(hb, ax=ax, label="hours (log)")
        ax.set(xlabel="true fill (%)", ylabel="reported fill_pct (%)", title="Firmware fill estimate vs truth")
        fig.tight_layout()
        (SITE / GEN).mkdir(parents=True, exist_ok=True)
        fig.savefig(SITE / GEN / "fill_estimate.png", dpi=110)
        plt.close(fig)
        return text, [GEN / "fill_estimate.png"]
    except (OSError, ValueError, KeyError) as exc:
        logging.warning("fill error stats failed: %s", exc)
        return "", []


def sensors(cfg: dict, b: Build, run: Path) -> str:
    s = "sensors"
    text, imgs = fill_error(b, run)
    return (h3("sim-sensors", "7 · Sensors") + f"<p><strong>The fill level is not measured directly.</strong> With "
            f"<code>fill_mode: {v(cfg, s + '.fill_mode')}</code> the firmware estimates it from the back pressure, like a "
            "real Europress-style machine without a separate level sensor:</p>" + pre(f"""
P_avg   = exponential rolling average over ~{v(cfg, s + '.pressure_fill.rolling_strokes')} strokes (alpha = 2/(n+1) per stroke), reset at a lift
fill %  = 100 * clip((P_avg - P_idle) / P_full, 0, 1)        no oil-temperature correction (compensate_oil_temp: {v(cfg, s + '.pressure_fill.compensate_oil_temp')})
P_full  = {v(cfg, s + '.pressure_fill.full_backpressure_bar')} bar * material stiffness, calibrated {v(cfg, s + '.pressure_fill.calibration')} (machine scale, idle, typical density)
spurious high: {v(cfg, s + '.false_full.rate_per_day')} per day, {v(cfg, s + '.false_full.duration_days')} days at {v(cfg, s + '.false_full.level_pct')} %, only once true fill >= {v(cfg, s + '.false_full.min_true_fill_pct')} %, clears at lift
dropouts: {v(cfg, s + '.dropout_prob')} of hours + outages {v(cfg, s + '.outage.rate_per_day')}/day, duration lognormal(mu, sigma = {escape(', '.join(str(x) for x in dig(cfg, 'sensors', 'outage', 'duration_h_lognormal') or []))}) h (max {v(cfg, s + '.outage.max_h')} h)
pressure transducer: noise {v(cfg, s + '.pressure.noise_sd_bar')} bar, {v(cfg, s + '.pressure.quantum_bar')} bar steps, gain bias sd {v(cfg, s + '.pressure.gain_bias_sd')}, drift sd {v(cfg, s + '.pressure.gain_drift_sd_per_year')}/yr""")
            + "<p>So cold oil reads fuller, day-to-day density scatter and spikes leak into the reading, and the README "
              "documents ≈ 6 pp mean error for this setup (the interview said about 5 %).</p>" + text + figures(imgs)
            + why("the model's main input is itself an estimate derived from pressure; pretending it is a clean level "
                  "sensor would overstate what fill alone can do."))


# ---------------------------------------------------------------- 8 operations
def operations(cfg: dict) -> str:
    o = "operations"
    return (h3("sim-ops", "8 · Operations") + pre(f"""
order    when the observed fill >= threshold (80/85/90 %), or {v(cfg, o + '.scheduled_lead_h')} h before the max interval of {v(cfg, o + '.max_interval_days')} days
truck    arrives {v(cfg, o + '.truck_delay_h')} h after the order, only {v(cfg, o + '.truck_hours')} h local, no Sundays: {v(cfg, o + '.no_sunday')}, no holidays: {v(cfg, o + '.no_holidays')}
lift     COMBI: press + container lifted and emptied fully; DUO: container swapped, residue U{v(cfg, o + '.duo_residue_frac')} of the layers
         the final stroke before the swap also takes the chamber contents
weighbridge  net kg with resolution {v(cfg, o + '.weighbridge.resolution_kg')} kg and noise sd {v(cfg, o + '.weighbridge.noise_sd_kg')} kg""")
            + "<p>The lift happens at the start of the <code>lift_event</code> hour; the row one hour earlier holds the "
              "mass that was lifted — that is the value compared with the weighbridge.</p>"
            + why("false-full readings and truck delays make the container's fill at lift vary widely, which is "
                  "what the soft sensor has to get right."))


# ---------------------------------------------------------------- 9 validation
KEY_LINES = (("mass balance", r"mass-balance max"), ("heaviest lift", r"heaviest net lift"),
             ("days between lifts", r"days between lifts"), ("overflow", r"^overflow"),
             ("peak pressure", r"^peak pressure:"), ("pressure at high fill", r"peak pressure at true fill"),
             ("pressure graph", r"corr\(contact position"), ("weather effect", r"open hopper heavier"),
             ("false full", r"share of lifts triggered"), ("false full", r"mean true fill before lift"))


def validation(b: Build, run: Path, summary: dict | None) -> str:
    parts = [h3("sim-validation", "9 · Validation")]
    if summary:
        lm = summary.get("lift_mass_by_material") or {}
        rows = [[m, num((dig(x, "mean") or float("nan")) / 1000, 2), LIFT_TARGET_T.get(m, "–"), num(dig(x, "count"), 0)]
                for m, x in lm.items()]
        parts.append("<h4>Lift mass by material</h4>"
                     + table(["material", "mean lift (t)", "brief target (t)", "lifts"], rows))
        parts.append(f"<p>False-full-triggered lifts: <strong>{pct_of(summary.get('false_full_lift_share'))} %</strong>"
                     f". Max per-machine mass-balance residual: {sci(summary.get('mass_balance_max_abs_residual_kg'))} kg."
                     "</p>")
        mb = summary.get("mass_balance_kg") or {}
        parts.append("<h4>Mass balance (whole fleet, reported period)</h4>"
                     + table(["term", "kg"], [[k.removesuffix("_kg"), sci(x) if k == "residual_kg" else num(x, 0)]
                                              for k, x in mb.items()]))
    src = b.check(run / "validate_report.txt")
    if src is not None:
        text = src.read_text()
        lines = text.splitlines()
        rows = []
        for label, pat in KEY_LINES:
            hit = next((ln.strip() for ln in lines if re.search(pat, ln.strip())), None)
            if hit:
                rows.append([label, hit])
        corr = [ln.strip() for ln in lines if re.match(r"\s+\w+\s+r = ", ln)]
        if corr:
            rows.append(["corr(pressure, density) at fill 85–100 %", " · ".join(corr)])
        parts.append("<h4>Key checks from validate.py</h4>" + table(["check", "report line"], rows)
                     + f"<details><summary>Full validate.py report ({escape(str(run))})</summary>{pre(text)}</details>")
    else:
        parts.append(note(f"{run}/validate_report.txt not generated yet."))
    rest = [p for p in copy_plots(b, run / "plots") if p.stem not in SHOWN_IN_HYDRAULICS]
    parts.append("<h4>Validation plots</h4><p class=muted>The two pressure plots are shown in section 6.</p>"
                 + figures(rest))
    return "".join(parts)


def simulation_detail(b: Build, run: Path, summary: dict | None, baseline_html: str) -> str:
    cfg = load_yaml(b, run / "config_used.yaml") or load_yaml(b, Path("config.yaml"))
    head = (f'<section id="sim"><h2>Simulation in detail</h2><p><code>compactor_sim</code> generates hourly telemetry '
            f"and ground truth for a fleet of press containers. Everything below is shown for run "
            f"<code>{escape(str(run))}</code>; parameter values are read from its <code>config_used.yaml</code> "
            "(identical to <code>config.yaml</code> apart from run size). Formulas are simplified from the code in "
            "<code>compactor_sim/</code>.</p>")
    if not cfg:
        return head + note("No config available.") + "</section>"
    toc = ("<p>" + " · ".join(f'<a href="#{a}">{escape(t)}</a>' for a, t in (
        ("sim-fleet", "Fleet"), ("sim-weather", "Weather"), ("sim-inflow", "Inflow"), ("sim-moisture", "Moisture"),
        ("sim-compaction", "Compaction"), ("sim-hydraulics", "Hydraulics"), ("sim-sensors", "Sensors"),
        ("sim-ops", "Operations"), ("sim-validation", "Validation"))) + "</p>")
    return (head + toc + fleet(cfg) + weather(cfg) + inflow(cfg) + moisture(cfg) + compaction(cfg)
            + hydraulics(cfg, b, run) + sensors(cfg, b, run) + operations(cfg) + validation(b, run, summary)
            + baseline_html + "</section>")


__all__ = ["simulation_detail"]
