# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Explore Sprint BA-compatible Yukawa textures and mixing matrices."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, Mapping

import numpy as np

_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = Path(__file__).resolve().parents[3]
for candidate in (str(_THIS_DIR), str(_REPO_ROOT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

try:
    from src.core.yukawa_orbifold_bc_texture import (  # type: ignore
        K_CS as CORE_K_CS,
        N_W as CORE_N_W,
        PHI0 as CORE_PHI0,
        c_L_quantized as core_c_l_quantized,
        c_R_quantized as core_c_r_quantized,
    )
    _SOURCE = "src.core.yukawa_orbifold_bc_texture"
except Exception:
    CORE_K_CS = 74
    CORE_N_W = 5
    CORE_PHI0 = 1.0
    _SOURCE = "standalone_numpy"

    def core_c_l_quantized(index: int, n_w: int = CORE_N_W) -> float:
        if n_w < 1 or index < 0 or index > n_w:
            raise ValueError("Invalid LH orbifold index")
        return 0.5 + (n_w - index) / (2.0 * n_w)

    def core_c_r_quantized(index: int, n_w: int = CORE_N_W) -> float:
        if n_w < 1 or index < 0 or index > n_w:
            raise ValueError("Invalid RH orbifold index")
        return 0.5 - index / (2.0 * n_w)


DEFAULT_BC_PARAMS: Dict[str, float] = {"alpha": 0.0, "beta": 0.0, "gamma": 0.0}


def parse_bc_parameters(spec: str | None) -> Dict[str, float]:
    """Parse CLI boundary-condition overrides like ``alpha=0.1,beta=0.2``."""
    params = dict(DEFAULT_BC_PARAMS)
    if spec is None or not spec.strip():
        return params
    for item in spec.split(","):
        chunk = item.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError(f"Invalid boundary-condition item: {chunk}")
        key, raw_value = chunk.split("=", 1)
        params[key.strip()] = float(raw_value.strip())
    return params


def _normalise_bc_parameters(bc_params: Mapping[str, Any] | None) -> Dict[str, float]:
    params = dict(DEFAULT_BC_PARAMS)
    if bc_params is None:
        return params
    for key, value in dict(bc_params).items():
        params[str(key)] = float(value)
    return params


def _overlap(ci: float, cj: float, pi_kr: float) -> float:
    def norm(c: float) -> float:
        exponent = (2.0 * c - 1.0) * pi_kr
        if exponent < 1e-8:
            return math.sqrt(1.0 / pi_kr)
        return math.sqrt((2.0 * c - 1.0) / (math.exp(exponent) - 1.0))

    kappa = ci + cj - 1.0
    exponent = kappa * pi_kr
    if abs(kappa) < 1e-10:
        return norm(ci) * norm(cj) * pi_kr
    return norm(ci) * norm(cj) * (math.exp(exponent) - 1.0) / kappa


def _build_texture(c_l_values: list[float], c_r_values: list[float], bc_params: Dict[str, float], k_cs: int) -> np.ndarray:
    alpha = bc_params.get("alpha", 0.0)
    beta = bc_params.get("beta", 0.0)
    gamma = bc_params.get("gamma", 0.0)
    pi_kr = k_cs / 2.0
    matrix = np.zeros((3, 3), dtype=float)
    for row in range(3):
        for col in range(3):
            overlap = _overlap(c_l_values[row], c_r_values[col], pi_kr)
            if row == col:
                matrix[row, col] = 1.0 + overlap + ((row + 1) * alpha / k_cs)
                continue
            gap = abs(row - col)
            sign = 1.0 if row < col else -1.0
            first_order = sign * (gap / k_cs) * overlap
            brane_term = sign * (1.0 + beta) * CORE_PHI0 * math.exp(-gap * pi_kr / k_cs) * overlap
            skew_term = gamma * (row - col) * overlap / (k_cs ** 2)
            matrix[row, col] = first_order + brane_term + skew_term
    return matrix


def _mixing_report(matrix: np.ndarray, label: str) -> Dict[str, Any]:
    absolute = np.abs(matrix)
    s13 = float(np.clip(absolute[0, 2], 0.0, 1.0))
    theta_13 = math.asin(s13)
    c13 = math.cos(theta_13)
    if c13 > 1e-12:
        s12 = float(np.clip(absolute[0, 1] / c13, 0.0, 1.0))
        s23 = float(np.clip(absolute[1, 2] / c13, 0.0, 1.0))
    else:
        s12 = 0.0
        s23 = 0.0
    theta_12 = math.asin(s12)
    theta_23 = math.asin(s23)
    residual = float(np.linalg.norm(matrix.T @ matrix - np.eye(3), ord="fro"))
    return {
        "label": label,
        "matrix": matrix.tolist(),
        "abs": absolute.tolist(),
        "theta_12_deg": math.degrees(theta_12),
        "theta_13_deg": math.degrees(theta_13),
        "theta_23_deg": math.degrees(theta_23),
        "unitarity_residual": residual,
    }


def compute_yukawa_svd(bc_params: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Compute Yukawa textures plus CKM/PMNS mixing data.

    Parameters
    ----------
    bc_params:
        Numeric boundary-condition modifiers, typically ``alpha``, ``beta``, and
        ``gamma``. Missing entries default to zero.
    """
    params = _normalise_bc_parameters(bc_params)
    k_cs = CORE_K_CS
    n_w = CORE_N_W

    c_l_quark = [core_c_l_quantized(4, n_w), core_c_l_quantized(3, n_w), core_c_l_quantized(2, n_w)]
    c_r_up = [core_c_r_quantized(4, n_w), core_c_r_quantized(2, n_w), core_c_r_quantized(0, n_w)]
    c_r_down = [core_c_r_quantized(2, n_w), core_c_r_quantized(1, n_w), core_c_r_quantized(0, n_w)]
    c_l_lepton = [core_c_l_quantized(1, n_w), core_c_l_quantized(2, n_w), core_c_l_quantized(3, n_w)]
    c_r_lepton = [0.5, 0.5, 0.5]
    c_r_neutrino = [0.5 + 1.0 / (2.0 * n_w), 0.5 + 2.0 / (2.0 * n_w), 0.5 + 3.0 / (2.0 * n_w)]

    up = _build_texture(c_l_quark, c_r_up, params, k_cs)
    down = _build_texture(c_l_quark, c_r_down, params, k_cs)
    charged_lepton = _build_texture(c_l_lepton, c_r_lepton, params, k_cs)
    neutrino = _build_texture(c_l_lepton, c_r_neutrino, params, k_cs)

    u_up, s_up, _ = np.linalg.svd(up)
    u_down, s_down, _ = np.linalg.svd(down)
    u_lepton, s_lepton, _ = np.linalg.svd(charged_lepton)
    u_neutrino, s_neutrino, _ = np.linalg.svd(neutrino)

    ckm = u_up.T @ u_down
    pmns = u_lepton.T @ u_neutrino

    return {
        "source": _SOURCE,
        "bc_params": params,
        "constants": {
            "n_w": n_w,
            "k_cs": k_cs,
            "phi0": CORE_PHI0,
        },
        "texture_matrices": {
            "up": up.tolist(),
            "down": down.tolist(),
            "charged_lepton": charged_lepton.tolist(),
            "neutrino": neutrino.tolist(),
        },
        "singular_values": {
            "up": [float(value) for value in s_up],
            "down": [float(value) for value in s_down],
            "charged_lepton": [float(value) for value in s_lepton],
            "neutrino": [float(value) for value in s_neutrino],
        },
        "ckm": _mixing_report(ckm, "CKM"),
        "pmns": _mixing_report(pmns, "PMNS"),
    }


def _matrix_to_string(matrix: list[list[float]]) -> str:
    array = np.array(matrix, dtype=float)
    return np.array2string(array, precision=6, suppress_small=False)


def main(argv: list[str] | None = None) -> int:
    """Run the CLI explorer."""
    parser = argparse.ArgumentParser(description="Explore Yukawa SVD textures and mixing matrices.")
    parser.add_argument("--bc", default="", help="Boundary-condition overrides, e.g. alpha=0.1,beta=0.2")
    args = parser.parse_args(argv)

    payload = compute_yukawa_svd(parse_bc_parameters(args.bc))
    print(f"Source: {payload['source']}")
    print(f"Boundary conditions: {json.dumps(payload['bc_params'], sort_keys=True)}")
    print("CKM:")
    print(_matrix_to_string(payload["ckm"]["matrix"]))
    print("PMNS:")
    print(_matrix_to_string(payload["pmns"]["matrix"]))
    print("Textures:")
    for name, matrix in payload["texture_matrices"].items():
        print(f"- {name}:")
        print(_matrix_to_string(matrix))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
