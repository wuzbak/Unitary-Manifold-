# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 490 — α_s full-chain audit v15."""
from __future__ import annotations

import pytest

from src.core.pillar490_alpha_s_audit_v15 import (
    ALPHA_S_5D,
    K_CS,
    N_C,
    PDG_2024_ALPHA_S,
    PILLAR_LABEL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    pdg_2024_reference,
    prediction_chain,
    residual_metrics,
    status_report,
    uv_completion_gap,
)


class TestConstants:
    def test_label(self):
        assert PILLAR_LABEL == 'ALPHA_S_FULL_CHAIN_AUDIT_V15'

    def test_status(self):
        assert PILLAR_STATUS == PILLAR_LABEL

    def test_number(self):
        assert PILLAR_NUMBER == 490

    def test_version(self):
        assert VERSION == 'v15.0'

    def test_nc(self):
        assert N_C == 3

    def test_kcs(self):
        assert K_CS == 74

    def test_alpha_s_value(self):
        assert ALPHA_S_5D == pytest.approx(0.1130)

    def test_pdg_value(self):
        assert PDG_2024_ALPHA_S == pytest.approx(0.1181)


class TestPredictionChain:
    def test_formula(self):
        assert prediction_chain()['formula'] == 'alpha_s^(5D) = (N_c / K_CS) * correction'

    def test_base_ratio(self):
        assert prediction_chain()['base_ratio'] == pytest.approx(3.0 / 74.0)

    def test_correction_factor(self):
        assert prediction_chain()['correction_factor'] == pytest.approx(ALPHA_S_5D / (3.0 / 74.0))

    def test_prediction_status(self):
        assert prediction_chain()['status'] == 'MARGIN_ZONE'

    def test_prediction_reconstructs_value(self):
        chain = prediction_chain()
        assert chain['base_ratio'] * chain['correction_factor'] == pytest.approx(ALPHA_S_5D)


class TestPDGReference:
    def test_sigma(self):
        assert pdg_2024_reference()['sigma'] == pytest.approx(0.0011)

    def test_one_sigma_low(self):
        assert pdg_2024_reference()['one_sigma_low'] == pytest.approx(0.1170)

    def test_one_sigma_high(self):
        assert pdg_2024_reference()['one_sigma_high'] == pytest.approx(0.1192)


class TestResidualMetrics:
    def test_gap(self):
        assert residual_metrics()['gap'] == pytest.approx(0.0051)

    def test_fractional_residual(self):
        assert residual_metrics()['fractional_residual_pct'] == pytest.approx(100.0 * 0.0051 / 0.1181)

    def test_sigma_residual(self):
        assert residual_metrics()['sigma_residual'] == pytest.approx(0.0051 / 0.0011)

    def test_below_pdg(self):
        assert residual_metrics()['below_pdg'] is True

    def test_status(self):
        assert residual_metrics()['status'] == 'MARGIN_ZONE'


class TestUVCompletionGap:
    def test_requires_10d(self):
        assert uv_completion_gap()['requires_10d_completion'] is True

    def test_not_closeable_inside_5d(self):
        assert uv_completion_gap()['closeable_inside_5d'] is False

    def test_honest_label(self):
        assert uv_completion_gap()['honest_label'] == 'IRREDUCIBLE_WITHOUT_10D_COMPLETION'


class TestStatusReport:
    def test_report_pillar(self):
        assert status_report()['pillar'] == 490

    def test_report_label(self):
        assert status_report()['label'] == PILLAR_LABEL

    def test_report_status(self):
        assert status_report()['status'] == PILLAR_STATUS

    def test_report_contains_prediction(self):
        assert status_report()['prediction_chain']['prediction'] == pytest.approx(ALPHA_S_5D)

    def test_report_contains_pdg(self):
        assert status_report()['pdg_2024']['central'] == pytest.approx(PDG_2024_ALPHA_S)

    def test_report_contains_residual(self):
        assert status_report()['residual']['status'] == 'MARGIN_ZONE'
