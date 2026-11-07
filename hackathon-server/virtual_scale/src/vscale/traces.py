"""Full per-stroke pressure curves (what a transducer logs at 50 Hz) and the edge feature extraction.

A forward stroke: pump start spike -> free travel at loss pressure -> contact with the charge ->
plateau while the pack slides -> rise to end pressure (or hold at relief if the ram stalls) ->
reversal. Noise: transducer noise + pump ripple. The controller would keep only the extracted
features, so the 4G link carries a few numbers per stroke, not the curve.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

HZ = 50
RIPPLE_HZ = 9.0          # gear-pump pulsation seen through the line [est]
RIPPLE_FRAC = 0.012
FWD_S = 16.0
RET_S = 9.0


@dataclass(frozen=True)
class StrokeFeatures:
    p_idle_bar: float
    p_plateau_bar: float
    p_end_bar: float
    completion: float
    forward_s: float


def generate_trace(rng: np.random.Generator, p_loss: float, p_plateau: float, p_end: float, completion: float,
                   relief_bar: float, noise_bar: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """One forward + return stroke. p_* are TRUE hydraulic pressures in bar (incl. losses)."""
    fwd_s = FWD_S * completion
    n_f = max(int(HZ * fwd_s), 10)
    x = np.linspace(0, completion, n_f)                       # ram position as share of full stroke
    contact = 0.20 + rng.uniform(-0.05, 0.05)
    plateau_end = contact + 0.45 * (1 - contact)
    rise = np.clip((x - plateau_end) / max(completion - plateau_end, 1e-3), 0, 1)
    p = np.where(x < contact, p_loss,
                 np.where(x < plateau_end, p_plateau, p_plateau + (min(p_end, relief_bar) - p_plateau) * rise ** 2.5))
    p[: int(0.3 * HZ)] += np.linspace(p_loss * 1.5, 0, int(0.3 * HZ))   # start spike
    if completion < 1.0:                                                   # stalled: hold at relief
        p = np.concatenate([p, np.full(int(1.5 * HZ), relief_bar)])
    ret = np.full(int(RET_S * HZ), p_loss * 1.1)
    p = np.concatenate([p, ret])
    t = np.arange(p.size) / HZ
    p = p * (1 + RIPPLE_FRAC * np.sin(2 * np.pi * RIPPLE_HZ * t)) + rng.normal(0, noise_bar, p.size)
    return t, p


def extract_features(t: np.ndarray, p: np.ndarray, relief_bar: float) -> StrokeFeatures:
    """Edge algorithm: find the reversal, then take robust statistics of stroke segments."""
    k = 5
    smooth = np.convolve(p, np.ones(k) / k, mode="same")
    # reversal: a real controller knows it from the valve command; here estimated from the curve
    ret_level = float(np.median(smooth[-int(3 * HZ):]))
    rev = max(len(p) - int(RET_S * HZ) - 1, 10)
    tail = smooth[: rev + int(0.5 * HZ)]
    above = np.where(tail > ret_level + max(3.0, 0.1 * (tail.max() - ret_level)))[0]
    if above.size:
        rev = int(above.max())
    fwd = smooth[: rev + 1]
    n = fwd.size
    idle = float(np.median(fwd[int(0.06 * n): max(int(0.12 * n), int(0.06 * n) + 1)]))
    plateau = float(np.median(fwd[int(0.35 * n): int(0.50 * n)]))
    end = float(np.max(fwd[int(0.95 * n):]))
    held = np.mean(fwd[int(0.85 * n):] > 0.97 * relief_bar) > 0.3
    fwd_s = float(t[rev])
    completion = 1.0 if not held else float(np.clip((fwd_s - 1.5) / FWD_S, 0.25, 1.0))
    return StrokeFeatures(idle, plateau, end, completion, fwd_s)
