"""Explainable compaction physics used to generate synthetic press signals.

Model (all quantities per compaction cycle, vectorised with numpy):

* Material law      rho(sigma) = rho_loose + (rho_inf - rho_loose) * (1 - exp(-sigma / sigma_c))
* Volume fraction   phi = M / (rho(sigma) * V)
* Sliding friction  sigma_slide = mu * g * M * (1 - lock(phi)) / A_face      (pack pushed along the floor)
* Confinement       sigma_conf  = K * phi ** n                                (pack squeezed against back wall)
* End-of-stroke stress solves  sigma = sigma_slide(sigma) + sigma_conf(sigma)  (unique root, bisection).

Two independent mass signals follow: the mid-stroke plateau carries mu*g*M (friction),
and end pressure + fill carry density * volume. Both are hypotheses [hyp] to be falsified
on real pressure curves; nothing here is measured Europress data.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

KPA_PER_BAR = 100.0


@dataclass(frozen=True)
class MaterialLaw:
    rho_loose: float
    rho_inf: float
    sigma_c: float  # kPa

    def density(self, sigma_kpa: np.ndarray, sigma_c_scale: np.ndarray | float = 1.0) -> np.ndarray:
        sc = self.sigma_c * np.asarray(sigma_c_scale)
        s = np.maximum(np.asarray(sigma_kpa, dtype=float), 0.0)
        return self.rho_loose + (self.rho_inf - self.rho_loose) * (1.0 - np.exp(-s / sc))

    def stress_for_density(self, rho: np.ndarray, sigma_c_scale: np.ndarray | float = 1.0) -> np.ndarray:
        """Inverse law; densities at or above rho_inf map to +inf."""
        sc = self.sigma_c * np.asarray(sigma_c_scale)
        frac = (np.asarray(rho, dtype=float) - self.rho_loose) / (self.rho_inf - self.rho_loose)
        frac = np.clip(frac, 0.0, 1.0)
        with np.errstate(divide="ignore"):
            return -sc * np.log1p(-frac)


def material_law(rho_loose: float, rho_ref: float, inf_factor: float, sigma_ref_kpa: float) -> MaterialLaw:
    """Build a law that reaches the pack's typical compacted density rho_ref at sigma_ref."""
    rho_inf = rho_ref * inf_factor
    if not rho_loose < rho_ref < rho_inf:
        raise ValueError("need rho_loose < rho_ref < rho_inf")
    frac = (rho_ref - rho_loose) / (rho_inf - rho_loose)
    sigma_c = -sigma_ref_kpa / np.log1p(-frac)
    return MaterialLaw(rho_loose=rho_loose, rho_inf=rho_inf, sigma_c=float(sigma_c))


def relief_stress_kpa(relief_bar: float, a_cyl_m2: float, a_face_m2: float) -> float:
    return relief_bar * KPA_PER_BAR * a_cyl_m2 / a_face_m2


def bar_to_face_kpa(p_bar: np.ndarray, a_cyl_m2: float | np.ndarray, a_face_m2: float | np.ndarray) -> np.ndarray:
    return np.asarray(p_bar) * KPA_PER_BAR * np.asarray(a_cyl_m2) / np.asarray(a_face_m2)


def face_kpa_to_bar(sigma_kpa: np.ndarray, a_cyl_m2: float | np.ndarray, a_face_m2: float | np.ndarray) -> np.ndarray:
    return np.asarray(sigma_kpa) * np.asarray(a_face_m2) / (np.asarray(a_cyl_m2) * KPA_PER_BAR)


def lock_fraction(phi: np.ndarray, mid: float, width: float) -> np.ndarray:
    """Share of the pack that rests against the back wall and no longer slides."""
    return 1.0 / (1.0 + np.exp(-(np.asarray(phi) - mid) / width))


@dataclass(frozen=True)
class PressState:
    sigma_end: np.ndarray        # required end-of-stroke face stress, kPa (may exceed relief)
    sigma_slide: np.ndarray      # friction component, kPa
    sigma_conf: np.ndarray       # confinement component, kPa
    phi: np.ndarray              # true volume fraction of the container
    density: np.ndarray          # pack density kg/m3


def solve_press_state(
    mass_kg: np.ndarray,
    volume_m3: float,
    law: MaterialLaw,
    sigma_c_scale: np.ndarray,
    mu: np.ndarray,
    a_face_m2: float,
    k_conf_kpa: float,
    conf_exp: float,
    lock_mid: float,
    lock_width: float,
    gravity: float = 9.81,
    iters: int = 50,
    gradient_a: float = 0.0,
) -> PressState:
    """Solve sigma = sigma_slide(phi(sigma)) + sigma_conf(phi(sigma)) for every cycle.

    The right-hand side falls as sigma rises (a denser pack occupies less volume), so the
    root is unique and bisection on [0, hi] converges.

    gradient_a: field-only density gradient. In a long pack, wall friction means layers far
    from the ram see less stress than the face, so the AVERAGE density is rho(sigma) * (1 - a*phi).
    A short lab sample has a = 0. This is the deliberate lab-vs-field mismatch [hyp].
    """
    m = np.maximum(np.asarray(mass_kg, dtype=float), 0.0)
    mu = np.broadcast_to(np.asarray(mu, dtype=float), m.shape)
    scale = np.broadcast_to(np.asarray(sigma_c_scale, dtype=float), m.shape)

    def components(sig: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        rho_face = law.density(sig, scale)
        c = m / (rho_face * volume_m3)
        if gradient_a > 0:
            # phi * (1 - a*phi) = c  ->  smaller root
            phi = (1.0 - np.sqrt(np.maximum(1.0 - 4.0 * gradient_a * c, 0.0))) / (2.0 * gradient_a)
        else:
            phi = c
        rho = m / np.maximum(phi * volume_m3, 1e-9)
        slide = mu * gravity * m * (1.0 - lock_fraction(phi, lock_mid, lock_width)) / a_face_m2 / 1000.0
        conf = k_conf_kpa * phi ** conf_exp
        return slide, conf, phi, rho

    lo = np.zeros_like(m)
    hi = np.full_like(m, 50.0 * k_conf_kpa)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        slide, conf, _, _ = components(mid)
        too_low = (slide + conf) > mid
        lo = np.where(too_low, mid, lo)
        hi = np.where(too_low, hi, mid)
    sig = 0.5 * (lo + hi)
    slide, conf, phi, rho = components(sig)
    return PressState(sigma_end=sig, sigma_slide=slide, sigma_conf=conf, phi=phi, density=rho)


def hydraulic_loss_bar(oil_temp_c: np.ndarray, loss_at_40: float, coeff: float) -> np.ndarray:
    """Flow losses: cold oil is more viscous, so the same load reads as a higher pressure."""
    return loss_at_40 * np.exp(coeff * (40.0 - np.asarray(oil_temp_c, dtype=float)))


def stroke_completion(sigma_required: np.ndarray, sigma_relief: float) -> np.ndarray:
    """Share of the stroke completed. Above relief pressure the ram stalls early."""
    over = np.maximum(np.asarray(sigma_required) / sigma_relief - 1.0, 0.0)
    return np.clip(1.0 - 1.5 * over, 0.25, 1.0)


def cycle_work_kj(
    sigma_plateau: np.ndarray, sigma_end: np.ndarray, a_face_m2: float, stroke_m: float, completion: np.ndarray
) -> np.ndarray:
    """Mechanical work of one forward stroke (kPa * m3 = kJ), trapezoid between plateau and end stress."""
    return a_face_m2 * stroke_m * completion * 0.5 * (np.asarray(sigma_plateau) + np.asarray(sigma_end))


def pressure_trace(
    p_idle: float, p_plateau: float, p_end: float, completion: float, relief: float, hz: int = 20, stroke_s: float = 18.0
) -> tuple[np.ndarray, np.ndarray]:
    """Illustrative 1-cycle pressure curve (forward stroke + return) for plots and edge-feature demos."""
    n_fwd = int(hz * stroke_s * completion)
    x = np.linspace(0.0, 1.0, max(n_fwd, 2))
    contact = 0.25
    rise = np.clip((x - contact) / (1 - contact), 0, 1)
    fwd = np.where(x < contact, p_idle, p_plateau + (p_end - p_plateau) * rise ** 3)
    if completion < 1.0:
        hold = np.full(int(hz * 2), min(relief, p_end))
        fwd = np.concatenate([fwd, hold])
    ret = np.full(int(hz * stroke_s * 0.6), p_idle * 1.1)
    p = np.concatenate([fwd, ret])
    t = np.arange(p.size) / hz
    return t, p
