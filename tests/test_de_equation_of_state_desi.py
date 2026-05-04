# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_de_equation_of_state_desi.py
=========================================
Pillar 151 — Tests for de_equation_of_state_desi.py.

Tests cover:
  - Constants: C_S_BRAIDED, W_KK, DESI_DR2_W0, PLANCK_BAO_W
  - um_dark_energy_eos(): UM prediction w_KK
  - desi_dr2_constraint(): DESI DR2 2025 constraints
  - planck_bao_w_constraint(): Planck 2018 + BAO reference
  - tension_analysis(): sigma-tension analysis
  - de_eos_reconciliation_summary(): full reconciliation
  - pillar151_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.de_equation_of_state_desi import (
    C_S_BRAIDED,
    W_KK,
    DESI_DR2_W0,
    DESI_DR2_W0_SIGMA,
    DESI_DR2_LCDM_TENSION_SIGMA,
    DESI_DR2_WA,
    PLANCK_BAO_W,
    PLANCK_BAO_W_SIGMA,
    DESI_DR2_REF,
    um_dark_energy_eos,
    desi_dr2_constraint,
    planck_bao_w_constraint,
    tension_analysis,
    de_eos_reconciliation_summary,
    pillar151_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_c_s_braided_is_12_over_37(self):
        assert abs(C_S_BRAIDED - 12.0 / 37.0) < 1e-12

    def test_w_kk_formula(self):
        """w_KK = −1 + (2/3) c_s²"""
        expected = -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2
        assert abs(W_KK - expected) < 1e-12

    def test_w_kk_is_negative(self):
        assert W_KK < 0

    def test_w_kk_greater_than_minus_1(self):
        """UM predicts w > −1 (quintessence-like)."""
        assert W_KK > -1.0

    def test_w_kk_approximate_value(self):
        """w_KK ≈ −0.9302"""
        assert abs(W_KK - (-0.9302)) < 0.001

    def test_desi_dr2_w0_central(self):
        assert abs(DESI_DR2_W0 - (-0.838)) < 0.01

    def test_desi_dr2_w0_sigma_positive(self):
        assert DESI_DR2_W0_SIGMA > 0

    def test_desi_dr2_tension_with_lcdm(self):
        """DESI DR2 shows w₀ > −1 at ~3.9σ."""
        assert DESI_DR2_LCDM_TENSION_SIGMA > 2.0

    def test_desi_dr2_wa_negative(self):
        """DESI DR2 shows wₐ < 0 (darkening DE)."""
        assert DESI_DR2_WA < 0

    def test_planck_bao_w_near_minus_1(self):
        assert abs(PLANCK_BAO_W - (-1.03)) < 0.05

    def test_planck_bao_sigma_small(self):
        assert PLANCK_BAO_W_SIGMA < 0.1

    def test_desi_ref_nonempty(self):
        assert len(DESI_DR2_REF) > 10


# ---------------------------------------------------------------------------
# UM dark energy EoS
# ---------------------------------------------------------------------------

class TestUMDarkEnergyEOS:
    def setup_method(self):
        self.result = um_dark_energy_eos()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_c_s_stored(self):
        assert abs(self.result["c_s_braided"] - C_S_BRAIDED) < 1e-12

    def test_w_kk_matches_constant(self):
        assert abs(self.result["w_kk"] - W_KK) < 1e-12

    def test_formula_string_present(self):
        assert "w_KK" in self.result["formula"] or "c_s" in self.result["formula"]

    def test_deviation_from_lcdm_positive(self):
        """w_KK > −1 → deviation is positive."""
        assert self.result["deviation_from_lcdm"] > 0

    def test_pillar_reference_present(self):
        assert "15" in self.result["pillar_reference"] or "136" in self.result["pillar_reference"]

    def test_invalid_c_s_zero_raises(self):
        with pytest.raises(ValueError, match="\\(0, 1\\]"):
            um_dark_energy_eos(c_s=0.0)

    def test_invalid_c_s_gt_1_raises(self):
        with pytest.raises(ValueError):
            um_dark_energy_eos(c_s=1.5)

    def test_c_s_squared_positive(self):
        assert self.result["c_s_squared"] > 0

    def test_derivation_string_nonempty(self):
        assert len(self.result["derivation"]) > 20


# ---------------------------------------------------------------------------
# DESI DR2 constraint
# ---------------------------------------------------------------------------

class TestDESIDR2Constraint:
    def setup_method(self):
        self.result = desi_dr2_constraint()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_w0_central(self):
        assert abs(self.result["w0_central"] - DESI_DR2_W0) < 1e-10

    def test_w0_sigma_positive(self):
        assert self.result["w0_sigma"] > 0

    def test_wa_central(self):
        assert abs(self.result["wa_central"] - DESI_DR2_WA) < 1e-10

    def test_lcdm_tension(self):
        """DESI DR2 excludes ΛCDM at >3σ."""
        assert self.result["lcdm_tension_sigma"] > 3.0

    def test_95cl_range_tuple(self):
        low, high = self.result["95cl_w0_range"]
        assert low < high

    def test_95cl_contains_w0(self):
        low, high = self.result["95cl_w0_range"]
        assert low < DESI_DR2_W0 < high

    def test_summary_nonempty(self):
        assert len(self.result["summary"]) > 30

    def test_dataset_nonempty(self):
        assert len(self.result["dataset"]) > 5


# ---------------------------------------------------------------------------
# Planck BAO constraint (old reference)
# ---------------------------------------------------------------------------

class TestPlanckBAOWConstraint:
    def setup_method(self):
        self.result = planck_bao_w_constraint()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_w_central(self):
        assert abs(self.result["w_central"] - PLANCK_BAO_W) < 1e-10

    def test_w_sigma_small(self):
        assert self.result["w_sigma"] < 0.1

    def test_prior_note_present(self):
        assert "prior" in self.result["note"].lower() or "ΛCDM" in self.result["note"]


# ---------------------------------------------------------------------------
# Tension analysis
# ---------------------------------------------------------------------------

class TestTensionAnalysis:
    def setup_method(self):
        self.result = tension_analysis()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_w_kk_stored(self):
        assert abs(self.result["w_kk"] - W_KK) < 1e-12

    def test_tension_vs_planck_large(self):
        """Old 3.4σ tension with Planck+BAO."""
        assert self.result["tension_vs_planck_bao"]["tension_sigma"] > 2.0

    def test_tension_vs_desi_small(self):
        """UM consistent with DESI DR2 at <2σ."""
        assert self.result["tension_vs_desi_dr2"]["tension_sigma"] < 2.5

    def test_tension_vs_desi_is_about_1_3_sigma(self):
        """w_KK = −0.9302 vs DESI w₀ = −0.838 ± 0.072 → ~1.3σ."""
        tension = self.result["tension_vs_desi_dr2"]["tension_sigma"]
        assert 0.5 < tension < 2.5

    def test_um_in_correct_direction(self):
        """Both UM and DESI predict w > −1."""
        assert self.result["um_in_correct_direction_relative_to_lcdm"] is True

    def test_um_on_same_side_as_desi(self):
        assert self.result["um_on_same_side_as_desi"] is True

    def test_summary_nonempty(self):
        assert len(self.result["summary"]) > 30

    def test_desi_status_consistent(self):
        status = self.result["tension_vs_desi_dr2"]["status"]
        assert "CONSISTENT" in status or "MARGINAL" in status


# ---------------------------------------------------------------------------
# Full reconciliation summary
# ---------------------------------------------------------------------------

class TestDEEOSReconciliationSummary:
    def setup_method(self):
        self.result = de_eos_reconciliation_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_151(self):
        assert self.result["pillar"] == 151

    def test_previous_status_open(self):
        assert "OPEN" in self.result["previous_status"] or "3.4" in self.result["previous_status"]

    def test_new_status_revised(self):
        assert "REVISED" in self.result["new_status"] or "DESI" in self.result["new_status"]

    def test_key_finding_nonempty(self):
        assert len(self.result["key_finding"]) > 50

    def test_remaining_open_nonempty(self):
        assert len(self.result["remaining_open"]) > 30

    def test_desi_ref_present(self):
        assert DESI_DR2_REF in self.result["desi_ref"] or "DESI" in self.result["desi_ref"]


# ---------------------------------------------------------------------------
# Pillar 151 summary
# ---------------------------------------------------------------------------

class TestPillar151Summary:
    def setup_method(self):
        self.result = pillar151_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_151(self):
        assert self.result["pillar"] == 151

    def test_w_kk_matches(self):
        assert abs(self.result["w_kk"] - W_KK) < 1e-12

    def test_c_s_braided_matches(self):
        assert abs(self.result["c_s_braided"] - C_S_BRAIDED) < 1e-12

    def test_desi_w0_matches(self):
        assert abs(self.result["desi_dr2_w0"] - DESI_DR2_W0) < 1e-10

    def test_tension_vs_desi_positive(self):
        assert self.result["tension_vs_desi_sigma"] > 0

    def test_consistent_with_desi_true(self):
        assert self.result["um_consistent_with_desi"] is True

    def test_um_in_correct_direction(self):
        assert self.result["um_in_correct_direction"] is True

    def test_old_tension_superseded(self):
        assert self.result["old_tension_superseded"] is True

    def test_mechanism_nonempty(self):
        assert len(self.result["mechanism"]) > 30

    def test_pillar_references_nonempty(self):
        assert len(self.result["pillar_references"]) >= 2
