# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 104 extension — NLO CKM mixing from non-universal 5D Yukawa couplings.

This module provides a compact NLO lane around the leading rank-1 RS overlap
texture by promoting g5_ij = δ_ij + ε_ij with small off-diagonal ε terms.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

import numpy as np

__all__ = [
    "default_epsilon_matrices",
    "nlo_yukawa_from_epsilon",
    "extract_mixing_angles",
    "ckm_nlo_from_yukawa_and_epsilon",
]


def _as_three_vector(values: Iterable[float], name: str) -> np.ndarray:
    arr = np.asarray(tuple(values), dtype=float)
    if arr.shape != (3,):
        raise ValueError(f"{name} must contain exactly 3 entries.")
    return arr


def _validate_epsilon(epsilon: np.ndarray, name: str) -> np.ndarray:
    eps = np.asarray(epsilon, dtype=float)
    if eps.shape != (3, 3):
        raise ValueError(f"{name} must be a 3x3 matrix.")
    return eps


def default_epsilon_matrices(
    c_l: Iterable[float],
    lambda_target: float = 0.22650,
) -> Tuple[np.ndarray, np.ndarray]:
    """Build default up/down epsilon matrices with λ, λ², λ³ hierarchy."""
    c_l_arr = _as_three_vector(c_l, "c_l")
    if lambda_target <= 0.0 or lambda_target >= 1.0:
        raise ValueError("lambda_target must satisfy 0 < lambda_target < 1.")

    # Small asymmetry from the LH profile spacing; keeps up/down sectors distinct.
    profile_asym = float(np.clip(np.mean(np.abs(np.diff(c_l_arr))), 0.02, 0.2))
    lam = lambda_target
    lam2 = lam * lam
    lam3 = lam2 * lam

    eps_up = np.array(
        [
            [0.0, +0.35 * lam, +0.08 * lam3],
            [-0.28 * lam, 0.0, +0.22 * lam2],
            [+0.05 * lam3, -0.18 * lam2, 0.0],
        ],
        dtype=float,
    )
    eps_down = np.array(
        [
            [0.0, -0.65 * lam * (1.0 + profile_asym), +0.18 * lam3],
            [+0.72 * lam * (1.0 + profile_asym), 0.0, -0.40 * lam2],
            [-0.14 * lam3, +0.46 * lam2, 0.0],
        ],
        dtype=float,
    )
    return eps_up, eps_down


def nlo_yukawa_from_epsilon(mass_matrix: np.ndarray, epsilon: np.ndarray) -> np.ndarray:
    """Promote a leading-order Yukawa mass matrix with right-acting ε texture."""
    m = np.asarray(mass_matrix, dtype=float)
    if m.shape != (3, 3):
        raise ValueError("mass_matrix must be 3x3.")
    eps = _validate_epsilon(epsilon, "epsilon")
    return m @ (np.eye(3, dtype=float) + eps)


def extract_mixing_angles(v_matrix: np.ndarray) -> Dict[str, float]:
    """Extract θ12, θ13, θ23 (degrees) from a CKM-like unitary matrix."""
    v = np.asarray(v_matrix)
    if v.shape != (3, 3):
        raise ValueError("v_matrix must be 3x3.")
    t12 = float(np.degrees(np.arcsin(np.clip(abs(v[0, 1]), 0.0, 1.0))))
    t13 = float(np.degrees(np.arcsin(np.clip(abs(v[0, 2]), 0.0, 1.0))))
    cos13 = max(float(np.cos(np.radians(t13))), 1e-12)
    t23 = float(np.degrees(np.arcsin(np.clip(abs(v[1, 2]) / cos13, 0.0, 1.0))))
    return {"theta_12_deg": t12, "theta_13_deg": t13, "theta_23_deg": t23}


def ckm_nlo_from_yukawa_and_epsilon(
    m_u_leading: np.ndarray,
    m_d_leading: np.ndarray,
    epsilon_up: np.ndarray,
    epsilon_down: np.ndarray,
) -> Dict[str, object]:
    """Compute CKM_NLO from leading Yukawas plus non-universal ε textures."""
    m_u_nlo = nlo_yukawa_from_epsilon(m_u_leading, epsilon_up)
    m_d_nlo = nlo_yukawa_from_epsilon(m_d_leading, epsilon_down)

    u_u, _, _ = np.linalg.svd(m_u_nlo)
    u_d, _, _ = np.linalg.svd(m_d_nlo)
    v_ckm = u_u.conj().T @ u_d
    angles = extract_mixing_angles(v_ckm)

    s12 = np.sin(np.radians(angles["theta_12_deg"]))
    s13 = np.sin(np.radians(angles["theta_13_deg"]))
    s23 = np.sin(np.radians(angles["theta_23_deg"]))

    hierarchy = {
        "s12": float(s12),
        "s23": float(s23),
        "s13": float(s13),
        "s23_over_s12_sq": float(s23 / max(s12 * s12, 1e-12)),
        "s13_over_s12_cu": float(s13 / max(s12 * s12 * s12, 1e-12)),
    }
    return {
        "M_u_nlo": m_u_nlo,
        "M_d_nlo": m_d_nlo,
        "V_ckm_nlo": v_ckm,
        **angles,
        "wolfenstein_hierarchy": hierarchy,
        "note": (
            "NLO non-universal g5 texture (δ+ε) generates CKM mixing at O(ε) "
            "with λ, λ², λ³ hierarchy diagnostics."
        ),
    }
