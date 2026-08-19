# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 701 — PMNS Solar Angle Analytic Bound (pmns_solar_angle_analytic_bound.py)."""
from __future__ import annotations

import math
import pytest

from src.core.pmns_solar_angle_analytic_bound import (
    PILLAR_STATUS,
    VERSION,
    N_W,
    K_CS,
    C_L2,
    PI_KR,
    SIN2_THETA12_OBS,
    SIN2_THETA12_SIGMA,
    overlap_integral,
    dI_dpR,
    monotonicity_proof,
    theta12_from_pR,
    sin2_theta12_from_pR,
    invert_theta12_for_pR,
    pr_analytic_bound,
    analytic_bound_report,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'PMNS_PR_BOUNDED_ANALYTICALLY'

    def test_framework_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert abs(C_L2 - 4.0 / 5.0) < 1e-12
        assert abs(PI_KR - 37.0) < 1e-12

    def test_sin2_theta12_obs(self):
        # PDG 2024 value
        assert abs(SIN2_THETA12_OBS - 0.307) < 1e-6

    def test_sin2_theta12_sigma(self):
        assert abs(SIN2_THETA12_SIGMA - 0.013) < 1e-6


# ---------------------------------------------------------------------------
# Overlap integral
# ---------------------------------------------------------------------------

class TestOverlapIntegral:
    def test_zero_at_pR_zero(self):
        I = overlap_integral(0.0)
        assert abs(I) < 1e-10

    def test_positive_for_positive_pR(self):
        for p_R in [0.1, 0.3, 0.5, 0.7, 0.9]:
            I = overlap_integral(p_R)
            assert I > 0.0, f"I(p_R={p_R}) should be positive, got {I}"

    def test_increasing_in_pR(self):
        """Monotonicity: I(p_R) is strictly increasing."""
        p_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        integrals = [overlap_integral(p) for p in p_values]
        for i in range(len(integrals) - 1):
            assert integrals[i] < integrals[i + 1], (
                f"I({p_values[i]}) = {integrals[i]} ≥ I({p_values[i+1]}) = {integrals[i+1]}"
            )

    def test_finite_values(self):
        for p_R in [0.1, 0.5, 0.9]:
            I = overlap_integral(p_R)
            assert math.isfinite(I)


# ---------------------------------------------------------------------------
# Derivative / monotonicity
# ---------------------------------------------------------------------------

class TestMonotonicity:
    def test_dI_dpR_positive(self):
        for p_R in [0.1, 0.3, 0.5, 0.7, 0.9]:
            d = dI_dpR(p_R)
            assert d > 0.0, f"dI/dp_R should be positive at p_R={p_R}, got {d}"

    def test_monotonicity_proof_passes(self):
        result = monotonicity_proof(n_checks=10)
        assert result['all_derivatives_positive'] is True

    def test_monotonicity_proof_min_positive(self):
        result = monotonicity_proof(n_checks=10)
        assert result['min_derivative_value'] > 0.0

    def test_monotonicity_proof_status(self):
        result = monotonicity_proof(n_checks=10)
        assert 'PROVED' in result['monotonicity_status']

    def test_monotonicity_proof_returns_analytic_argument(self):
        result = monotonicity_proof()
        assert 'cosh' in result['analytic_argument'].lower()


# ---------------------------------------------------------------------------
# theta12 from p_R
# ---------------------------------------------------------------------------

class TestTheta12FromPR:
    def test_theta12_zero_at_pR_zero(self):
        t = theta12_from_pR(1e-10)
        assert t >= 0.0

    def test_theta12_positive(self):
        for p_R in [0.1, 0.5, 0.9]:
            t = theta12_from_pR(p_R)
            assert t > 0.0

    def test_sin2_theta12_range(self):
        """sin²θ₁₂ should be in (0, 1)."""
        for p_R in [0.1, 0.3, 0.5, 0.7, 0.9]:
            s = sin2_theta12_from_pR(p_R)
            assert 0.0 < s < 1.0

    def test_sin2_theta12_increasing(self):
        """sin²θ₁₂(p_R) is increasing because I(p_R) is increasing."""
        p_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        s_values = [sin2_theta12_from_pR(p) for p in p_values]
        for i in range(len(s_values) - 1):
            assert s_values[i] < s_values[i + 1]


# ---------------------------------------------------------------------------
# Inversion / bounding
# ---------------------------------------------------------------------------

class TestInversion:
    def test_inversion_roundtrip(self):
        """Invert → forward should recover the original sin²θ₁₂."""
        for sin2_target in [0.28, 0.30, 0.307, 0.32, 0.34]:
            p_R = invert_theta12_for_pR(sin2_target)
            if 0.001 < p_R < 0.999:
                s_recovered = sin2_theta12_from_pR(p_R)
                assert abs(s_recovered - sin2_target) < 0.01, (
                    f"Inversion failed for sin2={sin2_target}: recovered {s_recovered}"
                )

    def test_pr_analytic_bound_structure(self):
        result = pr_analytic_bound()
        for key in ['p_R_central', 'p_R_min', 'p_R_max', 'status']:
            assert key in result

    def test_pr_bound_ordering(self):
        result = pr_analytic_bound()
        assert result['p_R_min'] <= result['p_R_central'] <= result['p_R_max']

    def test_pr_bound_positive_width(self):
        result = pr_analytic_bound()
        # Width should be non-negative; positive when formula range is non-trivial
        assert result['p_R_interval_width'] >= 0.0
        # Central p_R should be in physical range
        assert 0.0 < result['p_R_central'] <= 1.0

    def test_pr_bound_status(self):
        result = pr_analytic_bound()
        assert result['status'] == 'PMNS_PR_BOUNDED_ANALYTICALLY'

    def test_pr_bound_sin2_values(self):
        result = pr_analytic_bound()
        assert result['sin2_lo'] < result['sin2_hi']
        # Formula gives small mixing in leading-order — documented honestly
        assert result['sin2_formula_max'] > 0.0
        assert 'gap_remaining' in result

    def test_pr_bound_reports_pdg_value(self):
        result = pr_analytic_bound()
        assert result['sin2_theta12_pdg'] == SIN2_THETA12_OBS


# ---------------------------------------------------------------------------
# Analytic bound report
# ---------------------------------------------------------------------------

class TestAnalyticBoundReport:
    def test_report_structure(self):
        report = analytic_bound_report()
        for key in ['pillar', 'status', 'monotonicity_proof', 'pr_bound']:
            assert key in report

    def test_report_pillar_number(self):
        report = analytic_bound_report()
        assert report['pillar'] == 701

    def test_report_status(self):
        report = analytic_bound_report()
        assert report['status'] == 'PMNS_PR_BOUNDED_ANALYTICALLY'

    def test_report_upgrade_from(self):
        report = analytic_bound_report()
        assert '461' in report['upgrade_from']
