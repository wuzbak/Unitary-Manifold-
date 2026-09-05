# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Unit audit and explicit unsupported boundary for the former 5D solver.

The old oscillator mixed m_phi^2 in Planck units with k^2 in Mpc^-2.
exp(-37) times even the *reduced* Planck mass is about 208 GeV, not a
massless CMB field. In conformal time the term is a^2 m_phi^2, with both
mass and comoving k expressed in inverse Mpc. Correcting units alone does
not supply a normalized radion action, background, source or photon
hierarchy. Consequently no backreaction spectrum or closure is returned.

Use pillar814_zph_camb_bridge for a real GR CAMB control calculation.
That calculation does not supply the missing 5D perturbation theory.
"""
from __future__ import annotations

import math
from typing import NamedTuple

import numpy as np

PILLAR_NUMBER = 818
PILLAR_GATE = "FULL_5D_BOLTZMANN_UNSUPPORTED"
FULL_5D_BOLTZMANN_CLOSED = False
LEAN4_THEOREM_COUNT = 25  # Historical inventory, not a solver certificate.
LEAN4_TOTAL_BEFORE = 1386
LEAN4_TOTAL_AFTER = 1411
N_W, K_CS = 5, 74
PI_KR = 37.0
REDUCED_PLANCK_MASS_GEV = 2.435e18
HBAR_C_GEV_M = 1.973269804e-16
MPC_IN_METRES = 3.085677581491367e22
M_PHI_SQ = math.exp(-2 * PI_KR)  # In reduced Planck mass squared, NOT Mpc^-2.
M_PHI_GEV = math.exp(-PI_KR) * REDUCED_PLANCK_MASS_GEV
M_PHI_MPC_INV = M_PHI_GEV * MPC_IN_METRES / HBAR_C_GEV_M
A_REC = 1 / 1090.0

OPEN_ITEMS = [
    "NORMALIZED_ACTION_OPEN: radion kinetic normalization and matter coupling not derived",
    "BACKGROUND_OPEN: no dimensionally calibrated 5D background evolution",
    "SOURCE_OPEN: density contrast alone is not a normalized radion source",
    "HIERARCHY_OPEN: photon, baryon, metric constraints and line-of-sight projection missing",
    "MASS_AUDIT: exp(-37) Mbar_Pl is massive on CMB scales, not massless",
    "PROJECTION_RETRACTED: eta_rec is not the observer-to-last-scattering distance",
    "NO_ZERO_FILL: absent k support cannot be counted as zero spectrum residual",
]


class BackreactedBoltzmannResult(NamedTuple):
    gate: str
    converged: bool
    a_br_median: float | None
    a_br_max: float | None
    delta_cl_median: float | None
    n_modes: int
    n_iter_max: int
    open_items: list[str]
    mode_results: list


def radion_mass_audit(k_mpc_inv=0.05, scale_factor=A_REC):
    """Conditional RS mass conversion, not a derivation of its UM origin."""
    if (not math.isfinite(k_mpc_inv) or k_mpc_inv <= 0
            or not math.isfinite(scale_factor) or not 0 < scale_factor <= 1):
        raise ValueError("Require positive k [Mpc^-1] and 0 < a <= 1")
    conformal_mass = scale_factor * M_PHI_MPC_INV
    return {
        "assumption": "m_phi = exp(-37) reduced Planck mass",
        "mass_gev": M_PHI_GEV,
        "mass_mpc_inv": M_PHI_MPC_INV,
        "k_mpc_inv": k_mpc_inv,
        "scale_factor": scale_factor,
        "conformal_mass_squared_mpc_inv2": conformal_mass**2,
        "conformal_mass_to_k": conformal_mass / k_mpc_inv,
        "massless_at_cmb_scales": False,
        "backreaction_prediction": None,
    }


def run_full_backreacted_boltzmann(
    n_k=24, n_eta=300, n_ell=20, max_iter=20, tol=1e-6,
) -> BackreactedBoltzmannResult:
    """Return unsupported, without fake convergence or numerical zero residuals."""
    if any(not isinstance(x, int) or x < 1 for x in (n_k, n_eta, n_ell, max_iter)):
        raise ValueError("Requested grid sizes and iteration count must be positive integers")
    if not math.isfinite(tol) or tol <= 0:
        raise ValueError("Tolerance must be finite and positive")
    return BackreactedBoltzmannResult(
        PILLAR_GATE, False, None, None, None, 0, 0, list(OPEN_ITEMS), [],
    )


def delta_cl_from_backreaction(cl_gr, cl_br):
    """Relative magnitude only for valid positive control spectra; no zero fill."""
    reference, candidate = np.asarray(cl_gr, dtype=float), np.asarray(cl_br, dtype=float)
    if (reference.ndim != 1 or not reference.size or reference.shape != candidate.shape
            or not np.all(np.isfinite(reference)) or not np.all(np.isfinite(candidate))
            or np.any(reference <= 0) or np.any(candidate < 0)):
        raise ValueError("Require matching finite nonnegative TT arrays and positive reference")
    return np.abs(candidate - reference) / reference


def _unsupported_solver(*args, **kwargs):
    raise NotImplementedError(
        "5D Boltzmann calculation unsupported: normalized action, source, "
        "background and hierarchy missing; Planck mass cannot be added to Mpc^-2"
    )


# Fail explicitly for historical callers rather than continuing the mixed-unit toy.
radion_source_term = _unsupported_solver
solve_radion_mode = _unsupported_solver
boltzmann_br_mode = _unsupported_solver
boltzmann_gr_mode = _unsupported_solver
backreaction_amplitude = _unsupported_solver
run_backreaction_loop = _unsupported_solver
compute_transfer_functions = _unsupported_solver
compute_cl_tt = _unsupported_solver
A_BR_CANONICAL = None
DELTA_CL_CANONICAL = None
