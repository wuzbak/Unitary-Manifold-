# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 259 — Residual Geometry Operator (adjacent research track).

Deterministic residual-vector, coupling-matrix, and principal-mode analysis for
current open or monitoring lanes. This is an adjacent mathematical hardening
surface: it does not alter any hardgate claim labels.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from src.core.adm_bssn_closure import t3_closure_assessment
from src.core.as_transfer_normalization_audit import as_transfer_chain_audit
from src.core.higgs_naturalness_extended import higgs_naturalness_extended_report
from src.core.flux_landscape_extended_scan import SC4_PASS_RESIDUAL_THRESHOLD, residual_log10_ratio, sc4_closure_summary
from src.core.pillar255_open_gap_residual_dashboard import closure_priority_ranking, monitoring_g3_desi_status, monitoring_juno_status

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "LANE_ORDER",
    "normalized_lane_residuals",
    "residual_coupling_matrix",
    "residual_geometry_operator",
    "principal_residual_modes",
    "closure_leverage_ranking",
    "pillar259_residual_geometry_report",
]

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"
LANE_ORDER: tuple[str, ...] = ("T3", "A3", "SC2", "SC4", "G3", "JUNO")
MONITORING_WEIGHT: float = 0.50


def _bounded_ratio(value: float, scale: float) -> float:
    if scale <= 0.0:
        raise ValueError("scale must be positive")
    return max(0.0, float(value) / float(scale))


def normalized_lane_residuals() -> Dict[str, float]:
    """Return deterministic normalized residual magnitudes for all active lanes."""
    t3 = t3_closure_assessment()
    a3 = higgs_naturalness_extended_report()
    sc2 = as_transfer_chain_audit()
    sc4 = sc4_closure_summary()
    g3 = monitoring_g3_desi_status()
    juno = monitoring_juno_status()

    t3_metric = float(t3["hamiltonian_proxy"]) + float(t3["momentum_proxy"])
    a3_metric = float(a3["canonical_k_point"]["delta_renormalized"]) + float(a3["scheme_spread"])
    sc2_metrics = (
        float(sc2["step1_mkk_transfer_uncertainty"]["metric"]) / float(sc2["step1_mkk_transfer_uncertainty"]["pass_threshold"]),
        float(sc2["step3_as_consistency"]["relative_residual"]) / 0.12,
        float(sc2["step5_robustness_overlap"]["required_minimum"]) / max(float(sc2["step5_robustness_overlap"]["overlap_fraction"]), 1e-12),
    )
    sc4_pass_n_flux = int(sc4["first_pass_n_flux"] or sc4["required_n_flux_min"])
    sc4_metric = residual_log10_ratio(sc4_pass_n_flux)

    return {
        "T3": _bounded_ratio(t3_metric, 0.01),
        "A3": _bounded_ratio(a3_metric, 1.0),
        "SC2": float(sum(sc2_metrics) / len(sc2_metrics)),
        "SC4": _bounded_ratio(sc4_metric, SC4_PASS_RESIDUAL_THRESHOLD),
        "G3": _bounded_ratio(float(g3["desi_tension_sigma"]), float(g3["falsification_threshold_sigma"])),
        "JUNO": _bounded_ratio(float(juno["tension_sigma_if_confirmed"]), 3.0),
    }


def _lane_weights() -> Dict[str, float]:
    ranking = closure_priority_ranking()
    weights: Dict[str, float] = {}
    for idx, rid in enumerate(ranking):
        weights[rid] = 1.0 - 0.15 * idx
    weights["G3"] = MONITORING_WEIGHT
    weights["JUNO"] = MONITORING_WEIGHT
    return weights


def residual_coupling_matrix() -> np.ndarray:
    """Return the deterministic symmetric residual-coupling matrix."""
    matrix = np.array(
        [
            [1.00, 0.30, 0.15, 0.10, 0.05, 0.05],
            [0.30, 1.00, 0.25, 0.35, 0.10, 0.10],
            [0.15, 0.25, 1.00, 0.60, 0.20, 0.05],
            [0.10, 0.35, 0.60, 1.00, 0.25, 0.05],
            [0.05, 0.10, 0.20, 0.25, 1.00, 0.10],
            [0.05, 0.10, 0.05, 0.05, 0.10, 1.00],
        ],
        dtype=float,
    )
    return matrix


def residual_geometry_operator() -> Dict[str, object]:
    """Return the weighted residual operator matrix and aligned vectors."""
    residuals = normalized_lane_residuals()
    weights = _lane_weights()
    vector = np.array([residuals[lane] for lane in LANE_ORDER], dtype=float)
    weight_vector = np.array([weights[lane] for lane in LANE_ORDER], dtype=float)
    coupling = residual_coupling_matrix()
    weighted = vector * weight_vector
    operator = np.diag(weighted) @ coupling @ np.diag(weighted)

    return {
        "lane_order": list(LANE_ORDER),
        "residual_vector": vector.tolist(),
        "weight_vector": weight_vector.tolist(),
        "coupling_matrix": coupling.tolist(),
        "operator_matrix": operator.tolist(),
        "frobenius_norm": float(np.linalg.norm(operator, ord="fro")),
        "trace": float(np.trace(operator)),
    }


def principal_residual_modes() -> List[Dict[str, object]]:
    """Return operator eigenmodes sorted by descending eigenvalue."""
    packet = residual_geometry_operator()
    operator = np.array(packet["operator_matrix"], dtype=float)
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    order = np.argsort(eigenvalues)[::-1]

    rows: List[Dict[str, object]] = []
    for idx in order:
        value = float(eigenvalues[idx])
        vector = eigenvectors[:, idx]
        contributions = {
            lane: float(abs(component))
            for lane, component in zip(LANE_ORDER, vector, strict=True)
        }
        dominant_lane = max(contributions, key=contributions.get)
        rows.append(
            {
                "eigenvalue": value,
                "dominant_lane": dominant_lane,
                "contributions": contributions,
            }
        )
    return rows


def closure_leverage_ranking() -> List[Dict[str, object]]:
    """Rank lanes by residual magnitude weighted by coupling reach."""
    residuals = normalized_lane_residuals()
    weights = _lane_weights()
    coupling = residual_coupling_matrix()
    coupling_reach = coupling.sum(axis=1)

    rows = []
    for idx, lane in enumerate(LANE_ORDER):
        score = residuals[lane] * weights[lane] * float(coupling_reach[idx])
        rows.append(
            {
                "lane": lane,
                "normalized_residual": residuals[lane],
                "weight": weights[lane],
                "coupling_reach": float(coupling_reach[idx]),
                "leverage_score": float(score),
            }
        )
    rows.sort(key=lambda row: row["leverage_score"], reverse=True)
    return rows


def pillar259_residual_geometry_report() -> Dict[str, object]:
    """Return the integrated Pillar 259 report."""
    operator = residual_geometry_operator()
    modes = principal_residual_modes()
    leverage = closure_leverage_ranking()
    residuals = normalized_lane_residuals()

    return {
        "pillar": 259,
        "title": "Residual Geometry Operator",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "lane_order": list(LANE_ORDER),
        "normalized_residuals": residuals,
        "operator": operator,
        "principal_modes": modes,
        "closure_leverage": leverage,
        "dominant_mode": modes[0]["dominant_lane"],
        "highest_leverage_lane": leverage[0]["lane"],
        "status": "RESIDUAL_OPERATOR_EXECUTED",
        "separation_guard": True,
    }
