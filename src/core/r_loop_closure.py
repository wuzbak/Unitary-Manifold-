# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
WINDING_NUMBER: int = 5
K_CS: int = 74                      # = 5² + 7²
BRAIDED_SOUND_SPEED: float = 12 / 37
R_TREE: float = 0.0315              # tree-level braided r
R_BICEP_KECK_BOUND: float = 0.036   # 95 % CL upper limit

# ---------------------------------------------------------------------------
# Pillar 102 — r-loop closure
# ---------------------------------------------------------------------------

def r_tree_level() -> float:
    return R_TREE


def r_one_loop_correction(n_w: int = WINDING_NUMBER, k_cs: int = K_CS) -> float:
    loop_factor = k_cs / (4.0 * math.pi) ** 2
    return float(R_TREE * loop_factor)


def r_corrected(n_w: int = WINDING_NUMBER, k_cs: int = K_CS) -> float:
    return float(R_TREE - r_one_loop_correction(n_w, k_cs))


def r_loop_convergence_check(n_w: int = WINDING_NUMBER, k_cs: int = K_CS) -> dict:
    # Loop expansion parameter: k_cs/(4π)² is the one-loop suppression factor
    loop_param = float(k_cs) / (4.0 * math.pi) ** 2
    converges = loop_param < 1.0
    return {
        "loop_param": loop_param,
        "converges": converges,
        "criterion": "k_cs/(4pi)^2 < 1 required for loop expansion validity",
    }


def r_prediction_summary(n_w: int = WINDING_NUMBER, k_cs: int = K_CS) -> dict:
    tree = r_tree_level()
    corr = r_one_loop_correction(n_w, k_cs)
    corrected = tree - corr
    within_bound = corrected < R_BICEP_KECK_BOUND
    status = "WITHIN_BOUND" if within_bound else "EXCEEDS_BOUND"
    return {
        "tree": tree,
        "correction": corr,
        "corrected": corrected,
        "observational_bound": R_BICEP_KECK_BOUND,
        "status": status,
    }
