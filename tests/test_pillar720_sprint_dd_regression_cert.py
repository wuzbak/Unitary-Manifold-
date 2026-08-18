# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 720 — Sprint DD regression certificate."""
from __future__ import annotations

from src.quantum.pillar720_sprint_dd_regression_cert import (
    PILLAR_NUMBER,
    sprint_dd_regression_cert,
)


CERT = sprint_dd_regression_cert()


class TestRegressionCertificate:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 720

    def test_returns_dict(self) -> None:
        assert isinstance(CERT, dict)

    def test_checked_function_count(self) -> None:
        assert CERT["n_checked_functions"] == 13
        assert len(CERT["checked_functions"]) == 13

    def test_payloads_are_dicts(self) -> None:
        assert CERT["all_payloads_are_dicts"] is True

    def test_epistemic_status_present(self) -> None:
        assert CERT["all_payloads_have_epistemic_status"] is True

    def test_stub_validated(self) -> None:
        assert CERT["stub_validated"] is True

    def test_mott_verdict_true(self) -> None:
        assert CERT["mott_verdict"] is True

    def test_vqe_hardening_pass(self) -> None:
        assert CERT["vqe_hardening_pass"] is True

    def test_phase3_synthesized(self) -> None:
        assert CERT["phase3_synthesized"] is True

    def test_all_regressions_pass(self) -> None:
        assert CERT["all_regressions_pass"] is True

    def test_contains_expected_function_names(self) -> None:
        assert "p716_mock_xdiag_solve" in CERT["checked_functions"]
        assert "p719_quantum_lane_full_status" in CERT["checked_functions"]

    def test_certificate_status(self) -> None:
        assert CERT["epistemic_status"] == "SCAFFOLD"
