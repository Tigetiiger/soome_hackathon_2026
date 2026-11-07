"""Measurement models of real scales: the operator weighbridge (labels the fleet sees in practice).

Error sources follow the Europress pack and the business-plan findings:
weighbridge noise ~12 kg at 20 kg resolution, stored (stale) vehicle tares concentrated on a few
vehicles, combined loads allocated pro rata, side waste thrown on the truck, and operators that
share tickets only some of the time (Hauler Delta never).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Vehicle:
    vehicle_id: str
    stale_tare_bias_kg: float  # error of the stored tare when it is used (0 for well-kept vehicles)


def make_fleet_vehicles(rng: np.random.Generator, cfg: dict, operator_ids: list[str]) -> dict[str, list[Vehicle]]:
    sc = cfg["scales"]
    fleet: dict[str, list[Vehicle]] = {}
    for op in operator_ids:
        vs = []
        for j in range(sc["n_vehicles_per_operator"]):
            stale = rng.random() < sc["stale_vehicle_share"]
            bias = float(rng.normal(0, sc["stale_vehicle_bias_sd_kg"])) if stale else float(rng.normal(0, 8))
            vs.append(Vehicle(vehicle_id=f"{op}-V{j + 1:02d}", stale_tare_bias_kg=bias))
        fleet[op] = vs
    return fleet


def round_to(x: float, res: float) -> float:
    return float(np.round(x / res) * res)


def weigh_lift(rng: np.random.Generator, cfg: dict, collected_kg: float, vehicles: list[Vehicle],
               share_prob: float) -> dict:
    """One weighbridge ticket for one lift. Returns ticket fields plus the hidden error parts.

    net = collected + side_waste + scale_noise - tare_error   (then allocation for combined loads)
    A tare error > 0 means the stored tare is too heavy, so the net reads light.
    """
    sc = cfg["scales"]
    veh = vehicles[int(rng.integers(len(vehicles)))]
    stored = rng.random() < sc["stored_tare_prob"]
    tare_err = (veh.stale_tare_bias_kg + rng.normal(0, sc["stored_tare_sd_kg"])) if stored else 0.0
    side = float(rng.uniform(*sc["side_waste_kg"])) if rng.random() < sc["side_waste_prob"] else 0.0
    side_reported = bool(side > 0 and rng.random() < 0.7)
    combined = rng.random() < sc["combined_load_prob"]
    gross_err = rng.normal(0, sc["weighbridge_sigma_kg"])
    net = collected_kg + side + gross_err - tare_err
    if combined:
        net *= float(np.clip(rng.normal(1.0, sc["combined_alloc_error_cv"]), 0.4, 1.8))
    net = max(round_to(net, sc["weighbridge_resolution_kg"]), 0.0)
    shared = bool(rng.random() < share_prob)
    clean = shared and not stored and not combined and not side_reported
    return {
        "wb_vehicle_id": veh.vehicle_id,
        "wb_tare_method": "STORED" if stored else "WEIGHED",
        "wb_loads_on_vehicle": 2 if combined else 1,
        "wb_side_waste_reported": side_reported,
        "wb_allocated_net_kg": net,
        "wb_shared": shared,
        "wb_clean_anchor": clean,
        "err_tare_kg": float(tare_err),
        "err_side_waste_kg": side,
    }
