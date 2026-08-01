# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 639 — CMB Z_φ Boltzmann solver Phase 1."""
from __future__ import annotations

import math

from src.core.pillar639_cmb_zphi_boltzmann_phase1 import (
    AS_BARE,
    AS_PLANCK,
    AS_ZPH_CORRECTED,
    COVERAGE_FRACTION,
    DELTA_Z,
    K_CS,
    PHI0,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RESIDUAL_FACTOR,
    VERSION,
    Z_PHI,
    amplitude_correction,
    phase2_scope,
    pillar_report,
    primordial_power_spectrum_corrected,
    three_term_decomposition_check,
    what_is_NOT_claimed,
    what_is_claimed,
    z_phi_from_first_principles,
)

REPORT = pillar_report()
Z = z_phi_from_first_principles()
PS = primordial_power_spectrum_corrected()
AMP = amplitude_correction()
DECOMP = three_term_decomposition_check()
PHASE2 = phase2_scope()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 639

    def test_status(self):
        assert "PHASE1_EXECUTABLE" in PILLAR_STATUS

    def test_z_phi_formula(self):
        expected = 1.0 + math.sqrt(K_CS) / (2.0 * PHI0 ** 2)
        assert abs(Z_PHI - expected) < 1e-12

    def test_delta_z_positive(self):
        assert DELTA_Z > 0.0

    def test_z_phi_greater_than_one(self):
        assert Z_PHI > 1.0

    def test_z_phi_approx_5(self):
        assert 4.0 < Z_PHI < 10.0

    def test_coverage_fraction_positive(self):
        assert 0.0 < COVERAGE_FRACTION < 1.0

    def test_residual_factor_gt_one(self):
        assert RESIDUAL_FACTOR > 1.0


class TestZPhiFromFirstPrinciples:
    def test_formula_string(self):
        assert "Z_φ" in Z["formula"]

    def test_physical_origin(self):
        assert "radion" in Z["physical_origin"]

    def test_k_cs(self):
        assert Z["k_cs"] == K_CS

    def test_pillar_355(self):
        assert Z["pillar_reference"] == 355


class TestPrimordialPowerSpectrum:
    def test_z_phi_applied(self):
        assert abs(PS["a_s_corrected"] - Z_PHI * AS_BARE) < 1e-30

    def test_n_s_unchanged(self):
        assert PS["n_s_unchanged"] is True

    def test_a_s_planck(self):
        assert abs(PS["a_s_planck"] - AS_PLANCK) < 1e-20


class TestAmplitudeCorrection:
    def test_residual_gt_one(self):
        assert AMP["residual_factor_after"] > 1.0

    def test_coverage_percent_positive(self):
        assert AMP["coverage_percent"] > 0.0

    def test_improvement_ratio_gt_one(self):
        assert AMP["improvement_ratio"] > 1.0


class TestThreeTermDecomposition:
    def test_log_identity(self):
        assert DECOMP["log_identity_passes"] is True

    def test_s_5d_cap_label(self):
        assert "5D_CAP" in DECOMP["5d_irreducible_floor_label"]


class TestPhase2Scope:
    def test_status_open(self):
        assert PHASE2["status"] == "OPEN_FRONTIER"

    def test_deliverables(self):
        assert len(PHASE2["deliverables"]) >= 2


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
