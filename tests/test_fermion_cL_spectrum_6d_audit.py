# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-A: src/core/fermion_cL_spectrum_6d_audit.py"""

from __future__ import annotations

import math
import pytest

from src.core.fermion_cL_spectrum_6d_audit import (
    N_W, K_CS, PI_KR,
    CL_6D, YUKAWA_6D,
    MASS_RATIO_01, MASS_RATIO_02, MASS_RATIO_12,
    GATE_PASSED, WS_A_STATUS,
    cl_spectrum_6d,
    yukawa_6d,
    mass_ratios_6d,
    pdg_ratio_comparison,
    residual_table,
    anchor_elimination_proof,
    wsa_gate_report,
    pillar_wsa_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_cl_6d_length(self):
        assert len(CL_6D) == 3

    def test_cl_6d_gen0(self):
        assert CL_6D[0] == pytest.approx(0.5)

    def test_cl_6d_gen1(self):
        assert CL_6D[1] == pytest.approx(0.5 + 5.0 / 74.0)

    def test_cl_6d_gen2(self):
        assert CL_6D[2] == pytest.approx(0.5 + 10.0 / 74.0)

    def test_cl_6d_monotone_increasing(self):
        assert CL_6D[0] < CL_6D[1] < CL_6D[2]

    def test_yukawa_6d_length(self):
        assert len(YUKAWA_6D) == 3

    def test_yukawa_gen0_is_one(self):
        assert YUKAWA_6D[0] == pytest.approx(1.0)

    def test_yukawa_decreasing(self):
        assert YUKAWA_6D[0] > YUKAWA_6D[1] > YUKAWA_6D[2]

    def test_mass_ratio_01_positive(self):
        assert MASS_RATIO_01 > 1.0

    def test_mass_ratio_02_gt_01(self):
        assert MASS_RATIO_02 > MASS_RATIO_01

    def test_mass_ratio_12_equals_01(self):
        # Equal spacing → ratio_01 == ratio_12
        assert MASS_RATIO_12 == pytest.approx(MASS_RATIO_01, rel=1e-8)

    def test_mass_ratio_analytic(self):
        # exp(5/74 × 37) = exp(2.5)
        assert MASS_RATIO_01 == pytest.approx(math.exp(2.5), rel=1e-6)

    def test_mass_ratio_02_analytic(self):
        assert MASS_RATIO_02 == pytest.approx(math.exp(5.0), rel=1e-6)

    def test_gate_not_passed(self):
        assert GATE_PASSED is False

    def test_status_string_nonempty(self):
        assert len(WS_A_STATUS) > 10


class TestClSpectrum6d:
    def test_returns_dict(self):
        r = cl_spectrum_6d()
        assert isinstance(r, dict)

    def test_spacing(self):
        r = cl_spectrum_6d()
        assert r["spacing"] == pytest.approx(5.0 / 74.0)

    def test_cl_gen0_is_half(self):
        r = cl_spectrum_6d()
        assert r["c_L_gen0"] == pytest.approx(0.5)

    def test_cl_gen1_formula(self):
        r = cl_spectrum_6d()
        assert r["c_L_gen1"] == pytest.approx(0.5 + 5.0 / 74.0)

    def test_cl_gen2_formula(self):
        r = cl_spectrum_6d()
        assert r["c_L_gen2"] == pytest.approx(0.5 + 10.0 / 74.0)

    def test_axiomzero_compliant(self):
        r = cl_spectrum_6d()
        assert r["axiomzero_compliant"] is True

    def test_custom_params(self):
        r = cl_spectrum_6d(n_w=7, k_cs=100)
        assert r["spacing"] == pytest.approx(0.07)
        assert r["c_L_gen1"] == pytest.approx(0.5 + 0.07)


class TestYukawa6d:
    def test_returns_dict(self):
        assert isinstance(yukawa_6d(), dict)

    def test_yukawa_gen0_is_one(self):
        r = yukawa_6d()
        assert r["yukawa_gen0"] == pytest.approx(1.0)

    def test_yukawa_gen1_analytic(self):
        r = yukawa_6d()
        assert r["yukawa_gen1"] == pytest.approx(math.exp(-2.5), rel=1e-6)

    def test_yukawa_gen2_analytic(self):
        r = yukawa_6d()
        assert r["yukawa_gen2"] == pytest.approx(math.exp(-5.0), rel=1e-6)

    def test_mass_ratio_01(self):
        r = yukawa_6d()
        assert r["mass_ratio_01"] == pytest.approx(math.exp(2.5), rel=1e-6)


class TestMassRatios:
    def test_returns_dict(self):
        assert isinstance(mass_ratios_6d(), dict)

    def test_ratio_01(self):
        r = mass_ratios_6d()
        assert r["ratio_gen0_gen1"] == pytest.approx(math.exp(2.5), rel=1e-6)

    def test_ratio_02(self):
        r = mass_ratios_6d()
        assert r["ratio_gen0_gen2"] == pytest.approx(math.exp(5.0), rel=1e-6)


class TestPdgComparison:
    def test_returns_list(self):
        rows = pdg_ratio_comparison()
        assert isinstance(rows, list)

    def test_six_rows(self):
        rows = pdg_ratio_comparison()
        assert len(rows) == 6

    def test_each_row_has_pct_err(self):
        for row in pdg_ratio_comparison():
            assert "pct_err" in row

    def test_all_errors_positive(self):
        for row in pdg_ratio_comparison():
            assert row["pct_err"] >= 0.0

    def test_large_errors_honest(self):
        # The 6D c_L spectrum does NOT match at <5% — verify honesty
        rows = pdg_ratio_comparison()
        max_err = max(r["pct_err"] for r in rows)
        assert max_err > 50.0  # should be large


class TestResidualTable:
    def test_returns_dict(self):
        assert isinstance(residual_table(), dict)

    def test_gate_not_passed(self):
        r = residual_table()
        assert r["gate_passed"] is False

    def test_has_rows(self):
        r = residual_table()
        assert len(r["rows"]) > 0

    def test_verdict_string(self):
        r = residual_table()
        assert len(r["verdict"]) > 10

    def test_what_achieved_list(self):
        r = residual_table()
        assert len(r["what_is_newly_achieved"]) >= 4


class TestAnchorElimination:
    def test_returns_dict(self):
        assert isinstance(anchor_elimination_proof(), dict)

    def test_free_params_reduced(self):
        r = anchor_elimination_proof()
        assert r["before_6d"]["free_params"] == 9
        assert r["after_6d"]["free_params"] == 2
        assert r["reduction"] == 7

    def test_gate_verdict_string(self):
        r = anchor_elimination_proof()
        assert len(r["gate_verdict"]) > 10


class TestGateReport:
    def test_returns_dict(self):
        assert isinstance(wsa_gate_report(), dict)

    def test_gate_not_passed(self):
        r = wsa_gate_report()
        assert r["gate_passed"] is False

    def test_workstream_is_wsa(self):
        r = wsa_gate_report()
        assert r["workstream"] == "WS-A"

    def test_has_all_deliverables(self):
        r = wsa_gate_report()
        assert "deliverable_A1_cl_spectrum" in r
        assert "deliverable_A2_anchor_elimination" in r
        assert "deliverable_A3_residual_table" in r


class TestPillarSummary:
    def test_returns_dict(self):
        assert isinstance(pillar_wsa_summary(), dict)

    def test_c_l_spectrum_derived(self):
        r = pillar_wsa_summary()
        assert r["c_L_spectrum_derived"] is True

    def test_yukawa_scale_not_derived(self):
        r = pillar_wsa_summary()
        assert r["yukawa_scale_derived"] is False
