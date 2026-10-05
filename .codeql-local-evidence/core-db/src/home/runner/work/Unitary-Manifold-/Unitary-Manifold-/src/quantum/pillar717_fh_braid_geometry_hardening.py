# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/pillar717_fh_braid_geometry_hardening.py
====================================================
Pillar 717 — Fermi-Hubbard Braid Geometry Hardening

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

PILLAR_NUMBER = 717
N_W = 5
K_CS = 74
T_KK = 12.0 / 37.0
U_KK = 74.0 / 5.0
T_PRIME_KK = T_KK**2
U_OVER_T_KK = U_KK / T_KK
C_S = T_KK
HAMILTONIAN_LABEL = "H = -t NN - t' NNN + U n_up n_dn"

_COSINE_SQUARED = math.cos(2.0 * math.pi / N_W) ** 2
_BANDWIDTH = 4.0 * T_KK
_BANDWIDTH_NNN = _BANDWIDTH * (1.0 + 4.0 * (T_PRIME_KK / T_KK) * _COSINE_SQUARED)
_MOTT_GAP = U_KK - _BANDWIDTH_NNN
IS_MOTT_INSULATOR = _MOTT_GAP > 0.0

__all__ = [
    "PILLAR_NUMBER",
    "N_W",
    "K_CS",
    "T_KK",
    "U_KK",
    "T_PRIME_KK",
    "U_OVER_T_KK",
    "C_S",
    "IS_MOTT_INSULATOR",
    "fh_braid_hamiltonian_params",
    "mott_gap_estimate",
    "braid_bandwidth",
    "mott_insulator_verdict",
]


def fh_braid_hamiltonian_params() -> Dict[str, object]:
    """Return the hardened braid-geometry Hamiltonian parameters."""
    return {
        "pillar": PILLAR_NUMBER,
        "n_w": N_W,
        "k_cs": K_CS,
        "t_kk": T_KK,
        "u_kk": U_KK,
        "t_prime_kk": T_PRIME_KK,
        "u_over_t_kk": U_OVER_T_KK,
        "hamiltonian": HAMILTONIAN_LABEL,
        "nnn_origin": "t_prime = c_s^2",
        "epistemic_status": "ANALYTICAL_ESTIMATE",
    }


def braid_bandwidth() -> Dict[str, object]:
    """Return the nearest-neighbour and NNN-enhanced bandwidths."""
    enhancement = _BANDWIDTH_NNN / _BANDWIDTH
    return {
        "pillar": PILLAR_NUMBER,
        "bandwidth_w": _BANDWIDTH,
        "bandwidth_w_nnn": _BANDWIDTH_NNN,
        "cosine_squared_factor": _COSINE_SQUARED,
        "enhancement_factor": enhancement,
        "nnn_fraction": T_PRIME_KK / T_KK,
        "epistemic_status": "ANALYTICAL_ESTIMATE",
    }


def mott_gap_estimate() -> Dict[str, object]:
    """Return the strong-coupling Mott gap estimate with NNN hopping."""
    bandwidth = braid_bandwidth()
    return {
        "pillar": PILLAR_NUMBER,
        "u_kk": U_KK,
        "bandwidth_w_nnn": bandwidth["bandwidth_w_nnn"],
        "delta_mott": U_KK - bandwidth["bandwidth_w_nnn"],
        "criterion": "Delta_Mott = U - W_NNN",
        "epistemic_status": "ANALYTICAL_ESTIMATE",
    }


def mott_insulator_verdict() -> Dict[str, object]:
    """Return the hardened Mott-insulator verdict."""
    gap = mott_gap_estimate()
    return {
        "pillar": PILLAR_NUMBER,
        "u_over_t_kk": U_OVER_T_KK,
        "delta_mott": gap["delta_mott"],
        "is_mott_insulator": gap["delta_mott"] > 0.0,
        "regime": "STRONG_COUPLING_MOTT" if gap["delta_mott"] > 0.0 else "METALLIC_OR_CROSSOVER",
        "epistemic_status": "ANALYTICAL_ESTIMATE",
    }
