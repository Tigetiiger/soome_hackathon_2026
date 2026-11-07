"""Build ../SENSOR_COMPARISON.csv from results/core_comparison.csv + qualitative engineering columns.

Qualitative columns are engineering judgement [assumed]; accuracy columns are [simulated]; costs from costs.yaml.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results"

QUAL = {
    # config: (measured quantity, mounting, mass identifiable?, main error sources, retrofit difficulty 1-5, robustness 1-5, extra info)
    "REF_CERT_LC4": ("vertical support reactions, N", "C3 cells under all 4 container/unit supports in a docking frame",
                     "yes (direct, all load paths measured)", "snow/ice on roof, temperature, parasitic docking contact, level",
                     4, 4, "tare drift (wear/corrosion), overload, tamper, fill-by-weight"),
    "LC4_CHEAP": ("vertical support reactions, N", "IP68 C3 shear beams under all supports, non-approved transmitter",
                  "yes (direct)", "temperature drift of low-cost electronics, snow, parasitic contact",
                  4, 3, "same as REF"),
    "LC2_REAR_PINS": ("rear roller-axle loads, N", "2 load pins in rear roller axles; front unmeasured",
                      "no: needs centre of mass; total = R_rear*L/(L-x_c)", "centre-of-mass uncertainty dominates",
                      3, 3, "COM shift (uneven packing)"),
    "SG_BEND2": ("bending strain in runner rails", "2 weldable gauges on longitudinal runners",
                 "partial: load share depends on distribution", "load-distribution share, thermal stress, zero walk",
                 2, 2, "fatigue/crack monitoring of runners"),
    "SG_BEND2_A5": ("as SG_BEND2", "as SG_BEND2 + ticket anchors", "partial", "as SG_BEND2", 2, 2, "as SG_BEND2"),
    "SG_SHEAR4": ("shear strain at each support web", "compensated full bridges on shear webs at all 4 supports",
                  "yes if every support has a shear section", "in-situ calibration, temperature, zero creep",
                  3, 3, "load-path health"),
    "HYD_LIFT_TRUCK": ("hooklift cylinder pressure + arm angle", "on the hauler's truck",
                       "no: one force about one pivot gives W*x_c", "centre of mass, friction, dynamics",
                       2, 4, "truck overload; owner is the hauler"),
    "HYD_COMP_FW": ("ram plateau pressure, bar", "existing SMART pressure sensor, firmware logging",
                    "no: mass not identifiable (moisture, material law)", "density law, moisture, fill error",
                    1, 5, "compaction efficiency, blockage, hydraulic wear, overfill"),
    "HYD_COMP_FW_A5": ("as above + ticket anchors", "firmware only", "no (machine mean only)", "as above", 1, 5, "as above"),
    "HYD_COMP_OILT_A5": ("pressure + oil temperature + anchors", "firmware + EUR 20-40 probe", "no (machine mean only)",
                         "as above; removes cold-oil loss bias", 1, 5, "oil condition, cold-start behaviour"),
    "CT_POWER_A5": ("motor active power, W", "DIN-rail meter in the control cabinet (qualified electrician)",
                    "no", "motor/pump efficiency, idle power", 2, 5, "energy use, motor faults"),
    "FILL_D": ("fill level x density table", "existing SMART fill", "no", "density spread", 1, 5, "fill only"),
    "FILL_D_A5": ("fill + ticket-calibrated density", "existing SMART fill + tickets", "no (machine mean only)",
                  "per-load density spread, moisture", 1, 5, "effective density trend"),
    "ML_GBM": ("pressure, fill, oil T, class, material", "firmware; trained on golden cohort",
               "no (learns correlations only)", "extrapolation to unseen machines", 1, 5, "-"),
    "ML_GBM_A5": ("as ML + anchors", "firmware", "no", "as ML", 1, 5, "-"),
    "HYBRID_A5": ("pressure + oil T + fill + anchors, fused", "firmware + probe", "no (machine mean only)",
                  "per-load density/moisture", 1, 5, "all of the above"),
    "WB_TICKET_WEIGHED": ("truck gross-tare at waste centre", "operator weighbridge", "yes (certified)",
                          "20 kg division, two weighings", 0, 5, "-"),
    "WB_TICKET_MIXED_TARE": ("as above, 45 % stored tare", "operator weighbridge", "yes but stored tares drift",
                             "stale stored tare", 0, 5, "-"),
}


def main():
    d = pd.read_csv(RES / "core_comparison.csv")
    q = pd.DataFrame.from_dict(QUAL, orient="index",
                               columns=["measured_quantity", "mounting", "mass_identifiable", "main_error_sources",
                                        "retrofit_difficulty_1to5", "industrial_robustness_1to5", "extra_information"])
    q.index.name = "config"
    d = d.merge(q.reset_index(), on="config", how="left")
    d["verification_grade_P95le5pct"] = d["P95_rel_ge1t"] <= 0.05
    d["meets_2pct_P95"] = d["P95_rel_ge1t"] <= 0.02
    d = d.sort_values(["P95_rel_ge1t", "capex_mid"])
    d["rank_accuracy"] = range(1, len(d) + 1)
    cols = ["rank_accuracy", "config", "label", "measured_quantity", "mounting", "mass_identifiable",
            "capex_low", "capex_mid", "capex_high", "annual_mid", "owner", "billing_grade_possible",
            "independent_of_operator", "MAE_kg", "RMSE_kg", "bias_kg", "P90_abs_kg", "P95_abs_kg",
            "within_100kg", "within_100kg_at_2.5-3.5t", "median_rel_ge1t", "P95_rel_ge1t",
            "within_2pct_ge1t", "within_5pct_ge1t", "verification_grade_P95le5pct", "meets_2pct_P95",
            "eur_misstatement_per_device_year", "pareto", "main_error_sources",
            "retrofit_difficulty_1to5", "industrial_robustness_1to5", "extra_information"]
    d[cols].round(4).to_csv(HERE.parent / "SENSOR_COMPARISON.csv", index=False)
    print(d[["config", "capex_mid", "P95_rel_ge1t", "pareto"]].to_string(index=False))


if __name__ == "__main__":
    main()
