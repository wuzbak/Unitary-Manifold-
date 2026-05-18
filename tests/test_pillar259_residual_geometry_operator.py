# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import numpy as np

from src.core.pillar259_residual_geometry_operator import (
    ADJACENCY_TRACK_LABEL,
    LANE_ORDER,
    closure_leverage_ranking,
    normalized_lane_residuals,
    pillar259_residual_geometry_report,
    principal_residual_modes,
    residual_coupling_matrix,
    residual_geometry_operator,
)


def test_normalized_lane_residuals_shape():
    rows = normalized_lane_residuals()
    assert tuple(rows) == LANE_ORDER
    assert all(v >= 0.0 for v in rows.values())


def test_residual_coupling_matrix_symmetric():
    matrix = residual_coupling_matrix()
    assert matrix.shape == (len(LANE_ORDER), len(LANE_ORDER))
    assert np.allclose(matrix, matrix.T)


def test_residual_geometry_operator_shape():
    packet = residual_geometry_operator()
    assert packet["lane_order"] == list(LANE_ORDER)
    assert len(packet["residual_vector"]) == len(LANE_ORDER)
    assert len(packet["operator_matrix"]) == len(LANE_ORDER)
    assert packet["frobenius_norm"] > 0.0


def test_principal_modes_sorted_descending():
    modes = principal_residual_modes()
    eigenvalues = [row["eigenvalue"] for row in modes]
    assert eigenvalues == sorted(eigenvalues, reverse=True)
    assert modes[0]["dominant_lane"] in LANE_ORDER


def test_closure_leverage_sorted_descending():
    rows = closure_leverage_ranking()
    scores = [row["leverage_score"] for row in rows]
    assert scores == sorted(scores, reverse=True)
    assert rows[0]["lane"] in LANE_ORDER


def test_pillar259_report_shape():
    report = pillar259_residual_geometry_report()
    assert report["pillar"] == 259
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["status"] == "RESIDUAL_OPERATOR_EXECUTED"
    assert report["dominant_mode"] in LANE_ORDER
    assert report["highest_leverage_lane"] in LANE_ORDER
