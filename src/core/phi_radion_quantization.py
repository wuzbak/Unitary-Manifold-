# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/phi_radion_quantization.py
===================================
Local canonical quantization of the radion φ around the FTUM attractor.

This module does not claim the full 5D Dirac/Wheeler-DeWitt programme is
complete.  It closes the local harmonic sector around φ₀ = 1 by providing:

1. a canonical harmonic Hamiltonian for radion fluctuations q = φ − φ₀,
2. analytic oscillator eigenvalues/eigenfunctions,
3. JAX probability-normalization checks on the ground state,
4. 256/512-bit mpmath normalization and moment audits.

The geometric frequency is tied to the braid data through

    ω_φ = √K_CS / (2 πkR) = 1 / √74

using K_CS = 74 and πkR = K_CS / 2 = 37.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence

import numpy as np

try:
    import jax.numpy as jnp

    _JAX_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    _JAX_AVAILABLE = False

try:
    import mpmath

    _MPMATH_AVAILABLE = True
except Exception:  # pragma: no cover - environment dependent
    _MPMATH_AVAILABLE = False

N_W: int = 5
K_CS: int = 74
PI_KR: float = K_CS / 2.0
PHI0_FTUM: float = 1.0
EFFECTIVE_MASS: float = 1.0
OMEGA_RADION: float = math.sqrt(K_CS) / (2.0 * PI_KR)  # = 1/sqrt(74)
ZERO_POINT_ENERGY: float = 0.5 * OMEGA_RADION
DEFAULT_GRID_SPAN: float = 12.0 / math.sqrt(OMEGA_RADION)
DEFAULT_GRID_SIZE: int = 4097

__all__ = [
    "N_W",
    "K_CS",
    "PI_KR",
    "PHI0_FTUM",
    "EFFECTIVE_MASS",
    "OMEGA_RADION",
    "ZERO_POINT_ENERGY",
    "radion_energy_level",
    "radion_energy_spectrum",
    "radion_wavefunction",
    "probability_normalization",
    "expectation_values",
    "jax_ground_state_normalization",
    "mpmath_ground_state_audit",
    "canonical_quantization_report",
]


def radion_energy_level(n: int, omega: float = OMEGA_RADION) -> float:
    """Return E_n = (n + 1/2) ω for the local radion oscillator."""
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    return (float(n) + 0.5) * omega


def radion_energy_spectrum(n_max: int = 5, omega: float = OMEGA_RADION) -> Dict[str, object]:
    """Return the first n_max+1 energy levels and spacing audit."""
    if n_max < 0:
        raise ValueError(f"n_max must be non-negative, got {n_max}")
    levels = [radion_energy_level(n, omega) for n in range(n_max + 1)]
    spacings = [levels[i + 1] - levels[i] for i in range(len(levels) - 1)]
    return {
        "omega": omega,
        "levels": levels,
        "spacings": spacings,
        "uniform_spacing": all(abs(s - omega) < 1e-12 for s in spacings),
    }


def _hermite_phys(n: int, x: np.ndarray) -> np.ndarray:
    coeffs = [0.0] * n + [1.0]
    return np.polynomial.hermite.hermval(x, coeffs)


def _default_phi_grid(
    span: float = DEFAULT_GRID_SPAN,
    n_points: int = DEFAULT_GRID_SIZE,
    center: float = PHI0_FTUM,
) -> np.ndarray:
    return np.linspace(center - span, center + span, int(n_points), dtype=float)


def radion_wavefunction(
    phi_values: Sequence[float] | np.ndarray,
    level: int = 0,
    center: float = PHI0_FTUM,
    omega: float = OMEGA_RADION,
) -> np.ndarray:
    """Return ψ_n(φ) for the local harmonic radion sector."""
    if level < 0:
        raise ValueError(f"level must be non-negative, got {level}")
    phi = np.asarray(phi_values, dtype=float)
    xi = np.sqrt(EFFECTIVE_MASS * omega) * (phi - center)
    norm = (
        (EFFECTIVE_MASS * omega / math.pi) ** 0.25
        / math.sqrt((2.0 ** level) * math.factorial(level))
    )
    herm = _hermite_phys(level, xi)
    return norm * herm * np.exp(-0.5 * xi ** 2)


def probability_normalization(
    level: int = 0,
    phi_values: Sequence[float] | np.ndarray | None = None,
    center: float = PHI0_FTUM,
    omega: float = OMEGA_RADION,
) -> Dict[str, float]:
    """Numerically integrate ∫|ψ_n|² dφ on a wide finite grid."""
    grid = _default_phi_grid(center=center) if phi_values is None else np.asarray(phi_values, dtype=float)
    psi = radion_wavefunction(grid, level=level, center=center, omega=omega)
    density = np.abs(psi) ** 2
    integral = float(np.trapezoid(density, grid))
    return {
        "level": level,
        "integral": integral,
        "abs_error": abs(integral - 1.0),
    }


def expectation_values(
    level: int = 0,
    phi_values: Sequence[float] | np.ndarray | None = None,
    center: float = PHI0_FTUM,
    omega: float = OMEGA_RADION,
) -> Dict[str, float]:
    """Return ⟨φ⟩ and variance for ψ_n."""
    grid = _default_phi_grid(center=center) if phi_values is None else np.asarray(phi_values, dtype=float)
    psi = radion_wavefunction(grid, level=level, center=center, omega=omega)
    density = np.abs(psi) ** 2
    norm = float(np.trapezoid(density, grid))
    mean = float(np.trapezoid(grid * density, grid) / norm)
    variance = float(np.trapezoid(((grid - mean) ** 2) * density, grid) / norm)
    return {
        "level": level,
        "mean_phi": mean,
        "variance_phi": variance,
        "expected_variance": (level + 0.5) / omega,
    }


def jax_ground_state_normalization(
    center: float = PHI0_FTUM,
    omega: float = OMEGA_RADION,
    span: float = DEFAULT_GRID_SPAN,
    n_points: int = DEFAULT_GRID_SIZE,
) -> Dict[str, object]:
    """Return a JAX-based normalization audit for ψ₀."""
    if not _JAX_AVAILABLE:
        return {
            "jax_available": False,
            "integral": None,
            "abs_error": None,
            "passed": False,
        }
    phi = jnp.linspace(center - span, center + span, int(n_points))
    xi = jnp.sqrt(EFFECTIVE_MASS * omega) * (phi - center)
    norm = (EFFECTIVE_MASS * omega / math.pi) ** 0.25
    psi0 = norm * jnp.exp(-0.5 * xi ** 2)
    integral = float(jnp.trapezoid(psi0 ** 2, phi))
    error = abs(integral - 1.0)
    return {
        "jax_available": True,
        "integral": integral,
        "abs_error": error,
        "passed": error < 1e-5,
    }


def mpmath_ground_state_audit(
    dps: int = 80,
    center: float = PHI0_FTUM,
    omega: float = OMEGA_RADION,
) -> Dict[str, object]:
    """High-precision normalization and variance audit for ψ₀."""
    if not _MPMATH_AVAILABLE:
        return {
            "mpmath_available": False,
            "passed": False,
            "dps": dps,
        }

    with mpmath.workdps(dps):
        mp_omega = mpmath.mpf(omega)
        mp_center = mpmath.mpf(center)
        pref = (mp_omega / mpmath.pi) ** mpmath.mpf("0.25")

        def psi_sq(phi: "mpmath.mpf") -> "mpmath.mpf":
            xi = mpmath.sqrt(mp_omega) * (phi - mp_center)
            psi = pref * mpmath.exp(-xi ** 2 / 2)
            return psi ** 2

        normalization = mpmath.quad(psi_sq, [-mpmath.inf, mpmath.inf])

        def centered_second(phi: "mpmath.mpf") -> "mpmath.mpf":
            return (phi - mp_center) ** 2 * psi_sq(phi)

        variance = mpmath.quad(centered_second, [-mpmath.inf, mpmath.inf])
        expected_variance = mpmath.mpf("0.5") / mp_omega

        norm_err = abs(normalization - 1)
        var_err = abs(variance - expected_variance)
        return {
            "mpmath_available": True,
            "dps": dps,
            "normalization": float(normalization),
            "variance": float(variance),
            "expected_variance": float(expected_variance),
            "normalization_error": float(norm_err),
            "variance_error": float(var_err),
            "passed": (norm_err < mpmath.mpf("1e-30")) and (var_err < mpmath.mpf("1e-30")),
        }


def canonical_quantization_report(levels: Iterable[int] = (0, 1, 2)) -> Dict[str, object]:
    """Return the consolidated local radion quantization report."""
    level_list: List[int] = [int(n) for n in levels]
    normalization_checks = [probability_normalization(level=n) for n in level_list]
    expectation_checks = [expectation_values(level=n) for n in level_list]
    jax_audit = jax_ground_state_normalization()
    audit_256 = mpmath_ground_state_audit(80)
    audit_512 = mpmath_ground_state_audit(155)
    spectrum = radion_energy_spectrum(max(level_list) if level_list else 0)

    local_norm_ok = all(item["abs_error"] < 5e-4 for item in normalization_checks)
    jax_ok = (not jax_audit["jax_available"]) or bool(jax_audit["passed"])
    precision_ok = all(
        (not audit["mpmath_available"]) or bool(audit["passed"])
        for audit in (audit_256, audit_512)
    )

    return {
        "status": "LOCAL_CANONICAL_CLOSURE" if (local_norm_ok and jax_ok and precision_ok) else "OPEN",
        "phi0_ftum": PHI0_FTUM,
        "omega_radion": OMEGA_RADION,
        "zero_point_energy": ZERO_POINT_ENERGY,
        "spectrum": spectrum,
        "normalization_checks": normalization_checks,
        "expectation_checks": expectation_checks,
        "jax_ground_state": jax_audit,
        "precision_256bit": audit_256,
        "precision_512bit": audit_512,
        "residual_open_item": (
            "Full 5D Wheeler-DeWitt constraint algebra and operator-ordering closure remain open; "
            "this module closes the local harmonic radion sector around the FTUM attractor."
        ),
    }
