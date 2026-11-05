# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1134 rare-decay evidence and comparison helpers."""

import math

import pytest

from src.core.pillar1134_rare_decay_probes import (
    ADJACENT_TRACK_LABEL,
    EVIDENCE_THRESHOLD_SIGMA,
    LHCB_COMBINED_BD_TO_MUMU_SIGMA,
    LHCB_RUN3_BD_TO_MUMU_SIGMA,
    OBSERVATION_THRESHOLD_SIGMA,
    PILLAR_NUMBER,
    classify_significance,
    compare_prediction_to_measurement,
)


def test_pillar_identity_and_label():
    assert PILLAR_NUMBER == 1134
    assert ADJACENT_TRACK_LABEL == (
        "🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM"
    )


@pytest.mark.parametrize(
    ("sigma", "expected"),
    [
        (0.0, "below_evidence_threshold"),
        (2.999, "below_evidence_threshold"),
        (3.0, "evidence"),
        (3.2, "evidence"),
        (4.999, "evidence"),
        (5.0, "observation"),
        (7.0, "observation"),
    ],
)
def test_conventional_significance_boundaries(sigma, expected):
    assessment = classify_significance(sigma)
    assert assessment.classification == expected
    assert assessment.evidence_threshold_sigma == EVIDENCE_THRESHOLD_SIGMA
    assert assessment.observation_threshold_sigma == OBSERVATION_THRESHOLD_SIGMA
    assert "conventional" in assessment.threshold_note


def test_published_lhcb_values_classify_as_evidence_not_observation():
    assert LHCB_RUN3_BD_TO_MUMU_SIGMA == 3.0
    assert LHCB_COMBINED_BD_TO_MUMU_SIGMA == 3.2
    assert classify_significance(LHCB_RUN3_BD_TO_MUMU_SIGMA).classification == "evidence"
    assert classify_significance(LHCB_COMBINED_BD_TO_MUMU_SIGMA).classification == "evidence"


@pytest.mark.parametrize(
    "value",
    [-0.01, math.inf, -math.inf, math.nan, pytest.param(10**400, id="huge-integer")],
)
def test_significance_rejects_negative_or_nonfinite_values(value):
    with pytest.raises(ValueError):
        classify_significance(value)


def test_significance_rejects_boolean_and_non_numeric_values():
    with pytest.raises(TypeError):
        classify_significance(True)
    with pytest.raises(TypeError):
        classify_significance("3")


def test_prediction_comparison_uses_combined_uncertainty_and_signed_residual():
    result = compare_prediction_to_measurement(10, 13, 4, 3)
    assert result.combined_uncertainty == 5
    assert result.normalized_residual == pytest.approx(0.6)
    assert "no model prediction" in result.interpretation_note


def test_prediction_comparison_handles_zero_uncertainties():
    exact = compare_prediction_to_measurement(1, 1, 0, 0)
    discrepant = compare_prediction_to_measurement(1, 2, 0, 0)
    assert exact.normalized_residual == 0
    assert discrepant.normalized_residual == math.inf


@pytest.mark.parametrize(
    "inputs",
    [
        (0, 0, -1, 0),
        (0, 0, 0, -1),
        (math.inf, 0, 1, 1),
        (0, math.nan, 1, 1),
    ],
)
def test_prediction_comparison_rejects_invalid_inputs(inputs):
    with pytest.raises(ValueError):
        compare_prediction_to_measurement(*inputs)


def test_prediction_comparison_rejects_boolean():
    with pytest.raises(TypeError):
        compare_prediction_to_measurement(True, 1, 1, 1)
