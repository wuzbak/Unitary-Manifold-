# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 853 — φ₀ flux stabilization."""
from __future__ import annotations

import math

from src.core.pillar853_flux_landscape_phi0_stabilization import (
    FTUM_FIXED_POINT,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_FLUX_CANONICAL,
    PHI0_CONSISTENCY,
    PHI0_CONSISTENT,
    PHI0_FROM_FLUX,
    PHI0_5D_VALUE,
    PI_KR_CANONICAL,
    PILLAR_GATE,
    PILLAR_NUMBER,
    RAW_FLUX_ESTIMATE,
    VOL_CY3_ESTIMATE,
    VOL_S1,
    ftum_fixed_point_entropy,
    phi0_flux_stabilization_summary,
)


class TestPillar853Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 853
    def test_gate(self): assert PILLAR_GATE == "PHI0_FLUX_STABILIZATION_PARTIAL"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 25
    def test_lean4_total(self): assert LEAN4_TOTAL_AFTER == 2071
    def test_pi_kr(self): assert PI_KR_CANONICAL == 37.0
    def test_vol_s1_positive(self): assert VOL_S1 > 0.0
    def test_vol_cy3_positive(self): assert VOL_CY3_ESTIMATE > 0.0
    def test_volumes_match(self): assert math.isclose(VOL_CY3_ESTIMATE, VOL_S1)
    def test_fixed_point_value(self): assert math.isclose(FTUM_FIXED_POINT, 0.25)
    def test_raw_flux_between_zero_and_one(self): assert 0.0 < RAW_FLUX_ESTIMATE < 1.0
    def test_flux_quantum(self): assert N_FLUX_CANONICAL == 1
    def test_phi0_from_flux(self): assert math.isclose(PHI0_FROM_FLUX, 1.0)
    def test_phi0_5d_value(self): assert math.isclose(PHI0_5D_VALUE, 1.0)
    def test_phi0_consistent(self): assert PHI0_CONSISTENT is True
    def test_phi0_consistency_alias(self): assert PHI0_CONSISTENCY is True


class TestPillar853Functions:
    def test_ftum_fixed_point_entropy_default(self):
        assert math.isclose(ftum_fixed_point_entropy(), 0.25)

    def test_ftum_fixed_point_entropy_custom_area(self):
        assert math.isclose(ftum_fixed_point_entropy(area=2.0), 0.5)

    def test_summary_returns_dict(self):
        summary = phi0_flux_stabilization_summary()
        assert isinstance(summary, dict)

    def test_summary_gate(self):
        assert phi0_flux_stabilization_summary()["gate"] == PILLAR_GATE

    def test_summary_status_partial(self):
        assert phi0_flux_stabilization_summary()["status"] == "PARTIAL"

    def test_summary_phi0_consistent(self):
        assert phi0_flux_stabilization_summary()["phi0_consistent"] is True

    def test_summary_flux_selection_rule(self):
        assert "minimal_nonzero_flux" in phi0_flux_stabilization_summary()["selection_rule"]

    def test_summary_remaining_open(self):
        remaining = phi0_flux_stabilization_summary()["remaining_open"]
        assert "KKLT_NONPERTURBATIVE_COMPLETION_OPEN" in remaining
        assert "ALPHA_PRIME_CORRECTIONS_OPEN" in remaining

    def test_summary_lean4_total(self):
        assert phi0_flux_stabilization_summary()["lean4_total_after"] == 2071
