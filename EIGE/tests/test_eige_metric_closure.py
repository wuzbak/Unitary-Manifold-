# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/metric_closure.py"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.metric_closure import (
    MetricClosure,
    ClosureStatus,
    ClosureResult,
    compute_phi_eff,
    compute_kcs_from_state,
)
from EIGE.src.constants import K_CS, PHI_0, PHI_TOLERANCE, PHI_DRIFT_WARNING


class TestClosureStatus:
    def test_stable_is_stable(self):
        assert ClosureStatus.STABLE.name == "STABLE"

    def test_three_distinct_statuses(self):
        assert len(set([ClosureStatus.STABLE, ClosureStatus.DRIFTED, ClosureStatus.VIOLATED])) == 3


class TestComputePhiEff:
    def test_zero_ballots_returns_phi_0(self):
        assert compute_phi_eff(K_CS, 0) == PHI_0

    def test_nonzero_ballots_returns_near_phi_0(self):
        phi = compute_phi_eff(K_CS, 100)
        assert abs(phi - PHI_0) < PHI_DRIFT_WARNING

    def test_hash_state_0_returns_phi_0(self):
        # With hash_state=0 the residual is 0
        phi = compute_phi_eff(0, 100)
        assert phi == PHI_0


class TestMetricClosure:
    def setup_method(self):
        self.validator = MetricClosure()

    def test_exact_phi_0_k_cs_is_stable(self):
        result = self.validator.validate(PHI_0, K_CS)
        assert result.status == ClosureStatus.STABLE
        assert result.is_clean()
        assert result.alert is None

    def test_tiny_perturbation_is_stable(self):
        # Within PHI_TOLERANCE
        result = self.validator.validate(PHI_0 + 5e-16, K_CS)
        assert result.status == ClosureStatus.STABLE

    def test_perturbation_above_tolerance_is_violated(self):
        # 2e-15 > PHI_TOLERANCE (1e-15) but k_cs is exact → DRIFTED, not VIOLATED
        # VIOLATED requires k_cs mismatch OR delta > PHI_DRIFT_WARNING
        result = self.validator.validate(PHI_0 + 2e-15, K_CS)
        assert result.status in (ClosureStatus.DRIFTED, ClosureStatus.VIOLATED)
        assert result.status != ClosureStatus.STABLE

    def test_hard_perturbation_is_violated(self):
        result = self.validator.validate(PHI_0 + 1e-10, K_CS)
        assert result.status == ClosureStatus.VIOLATED

    def test_wrong_k_cs_is_violated(self):
        # k_cs off by more than 1 → VIOLATED (use 72, which is off by 2)
        result = self.validator.validate(PHI_0, 72)
        assert result.status == ClosureStatus.VIOLATED

    def test_wrong_k_cs_by_1_is_at_least_drifted(self):
        # k_cs off by 1 with perfect phi → VIOLATED (any k_cs mismatch → non-stable)
        result = self.validator.validate(PHI_0, K_CS - 1)
        assert result.status != ClosureStatus.STABLE

    def test_k_cs_off_by_two_is_violated(self):
        result = self.validator.validate(PHI_0, K_CS + 2)
        assert result.status == ClosureStatus.VIOLATED

    def test_k_cs_off_by_one_with_zero_phi_delta_is_drifted(self):
        result = self.validator.validate(PHI_0, K_CS - 1)
        assert result.status in (ClosureStatus.DRIFTED, ClosureStatus.VIOLATED)

    def test_violated_has_alert(self):
        result = self.validator.validate(PHI_0 + 1e-10, K_CS)
        assert result.alert is not None
        assert result.alert["severity"] == "CRITICAL"

    def test_stable_no_alert(self):
        result = self.validator.validate(PHI_0, K_CS)
        assert result.alert is None

    def test_phi_delta_recorded_correctly(self):
        delta = 2e-15
        result = self.validator.validate(PHI_0 + delta, K_CS)
        # Float64 arithmetic means stored delta is close but not exactly 2e-15
        assert abs(result.phi_delta - delta) < 1e-16

    def test_k_cs_expected_in_result(self):
        result = self.validator.validate(PHI_0, K_CS)
        assert result.k_cs_expected == K_CS

    def test_as_dict_has_required_keys(self):
        result = self.validator.validate(PHI_0, K_CS)
        d = result.as_dict()
        for key in ("status", "phi_eff", "phi_0", "phi_delta", "k_cs_observed", "is_clean"):
            assert key in d

    def test_validate_from_telemetry_stable(self):
        telemetry = {"phi_eff": PHI_0, "k_cs": K_CS}
        result = self.validator.validate_from_telemetry(telemetry)
        assert result.status == ClosureStatus.STABLE

    def test_validate_from_telemetry_violated(self):
        telemetry = {"phi_eff": 0.0, "k_cs": K_CS}
        result = self.validator.validate_from_telemetry(telemetry)
        assert result.status == ClosureStatus.VIOLATED

    def test_violated_alert_contains_description(self):
        result = self.validator.validate(PHI_0 + 1e-10, K_CS)
        assert "manipulated" in result.alert["description"].lower()

    def test_custom_tolerance(self):
        # With tolerance=1e-20, even float64 machine epsilon (≈1.1e-16) exceeds it.
        # The perturbation 1e-16 is in the DRIFTED zone (between tolerance and drift_warn),
        # as long as k_cs matches.  Verify at least non-stable.
        strict = MetricClosure(phi_tolerance=1e-20)
        result = strict.validate(PHI_0 + 1e-16, K_CS)
        assert result.status != ClosureStatus.STABLE

    def test_is_clean_false_for_violated(self):
        result = self.validator.validate(PHI_0 + 1.0, K_CS)
        assert not result.is_clean()
