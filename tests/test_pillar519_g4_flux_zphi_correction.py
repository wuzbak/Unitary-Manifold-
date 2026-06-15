# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 519 — 11D G₄-flux quantitative correction to Z_φ.

Status: FRONTIER_COMPUTATION (🔵 ADJACENT TRACK)
"""

from __future__ import annotations

import math
import pytest

from src.eleventd.g4_flux_zphi_correction import (
    CHI_QUINTIC,
    H11_QUINTIC,
    H21_QUINTIC,
    K_CS,
    N_W,
    PI_KR,
    PILLAR518_RESIDUAL_BASELINE,
    ZPHI_ZERO_POINT,
    cmb_residual_fraction_resolved,
    cy3_euler_characteristic,
    delta_zphi_g4,
    g4_flux_selection_summary,
    g4_zphi_correction_report,
    kk_geometry_factor,
    zphi_nlo,
    zphi_zero_point,
)


# ── Module-level constant tests ────────────────────────────────────────────────


class TestModuleConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_h11_quintic(self):
        assert H11_QUINTIC == 1

    def test_h21_quintic(self):
        assert H21_QUINTIC == 101

    def test_chi_quintic(self):
        assert CHI_QUINTIC == -200

    def test_zphi_zero_point_constant(self):
        # Z_φ^{(0)} = 1 + √74/2 ≈ 5.301
        expected = 1.0 + math.sqrt(74) / 2.0
        assert ZPHI_ZERO_POINT == pytest.approx(expected, rel=1e-10)

    def test_residual_baseline(self):
        assert PILLAR518_RESIDUAL_BASELINE == pytest.approx(0.26)


# ── cy3_euler_characteristic ───────────────────────────────────────────────────


class TestCY3EulerCharacteristic:
    def test_quintic_default(self):
        assert cy3_euler_characteristic() == -200

    def test_quintic_explicit(self):
        assert cy3_euler_characteristic(1, 101) == -200

    def test_formula(self):
        # χ = 2(h11 - h21)
        assert cy3_euler_characteristic(3, 243) == 2 * (3 - 243)

    def test_symmetric_case(self):
        # h11 = h21 → χ = 0
        assert cy3_euler_characteristic(5, 5) == 0

    def test_positive_chi(self):
        assert cy3_euler_characteristic(10, 1) == 18


# ── kk_geometry_factor ────────────────────────────────────────────────────────


class TestKKGeometryFactor:
    def test_canonical_value(self):
        # G_KK(37) = 37 / (1 + 37/74) = 37 / 1.5 ≈ 24.667
        expected = 37.0 / (1.0 + 37.0 / 74)
        assert kk_geometry_factor() == pytest.approx(expected, rel=1e-10)

    def test_ir_limit(self):
        # For x ≪ K_CS: G_KK ≈ x
        val = kk_geometry_factor(0.1, 74)
        assert val == pytest.approx(0.1 / (1.0 + 0.1 / 74), rel=1e-8)

    def test_saturation(self):
        # For x ≫ K_CS: G_KK → K_CS
        val = kk_geometry_factor(1e6, 74)
        assert val == pytest.approx(74.0, rel=1e-2)

    def test_positive(self):
        assert kk_geometry_factor() > 0

    def test_monotone_in_pi_kr(self):
        g1 = kk_geometry_factor(20.0)
        g2 = kk_geometry_factor(50.0)
        assert g2 > g1


# ── delta_zphi_g4 ─────────────────────────────────────────────────────────────


class TestDeltaZphiG4:
    def test_positive(self):
        dz = delta_zphi_g4()
        assert dz > 0

    def test_canonical_formula(self):
        # δZ = (|chi| / (8π K_CS)) × G_KK(πkR)
        abs_chi = 200
        g_kk = kk_geometry_factor()
        expected = abs_chi / (8.0 * math.pi * 74) * g_kk
        assert delta_zphi_g4() == pytest.approx(expected, rel=1e-10)

    def test_scales_with_chi(self):
        dz1 = delta_zphi_g4(chi=-100)
        dz2 = delta_zphi_g4(chi=-200)
        assert dz2 == pytest.approx(2 * dz1, rel=1e-10)

    def test_scales_with_abs_chi(self):
        # |χ| only matters
        dz_neg = delta_zphi_g4(chi=-200)
        dz_pos = delta_zphi_g4(chi=200)
        assert dz_neg == pytest.approx(dz_pos, rel=1e-10)

    def test_zero_chi_gives_zero_correction(self):
        assert delta_zphi_g4(chi=0) == pytest.approx(0.0)

    def test_magnitude_order(self):
        # δZ_φ^{G4} should be in O(0.1–5) range for quintic
        dz = delta_zphi_g4()
        assert 0.05 < dz < 10.0

    def test_custom_parameters(self):
        dz = delta_zphi_g4(chi=-100, pi_kr=20.0, k_cs=50)
        assert dz > 0


# ── zphi_zero_point ───────────────────────────────────────────────────────────


class TestZphiZeroPoint:
    def test_canonical_value(self):
        z0 = zphi_zero_point()
        assert z0 == pytest.approx(1.0 + math.sqrt(74) / 2.0, rel=1e-10)

    def test_greater_than_one(self):
        assert zphi_zero_point() > 1.0

    def test_approx_5_301(self):
        # Documented value from Pillar 355
        assert zphi_zero_point() == pytest.approx(5.301, abs=0.01)


# ── zphi_nlo ──────────────────────────────────────────────────────────────────


class TestZphiNlo:
    def test_greater_than_zero_point(self):
        z_nlo = zphi_nlo()
        z0 = zphi_zero_point()
        assert z_nlo > z0

    def test_equals_sum(self):
        z0 = zphi_zero_point()
        dz = delta_zphi_g4()
        assert zphi_nlo() == pytest.approx(z0 + dz, rel=1e-10)

    def test_positive(self):
        assert zphi_nlo() > 0


# ── cmb_residual_fraction_resolved ────────────────────────────────────────────


class TestCmbResidualFractionResolved:
    def test_returns_dict(self):
        result = cmb_residual_fraction_resolved()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = cmb_residual_fraction_resolved()
        for key in (
            "zphi_0",
            "delta_zphi_g4",
            "zphi_nlo",
            "sigma_residual_0",
            "sigma_residual_nlo",
            "fraction_resolved",
            "pct_resolved",
        ):
            assert key in result, f"Missing key: {key}"

    def test_sigma_0_is_baseline(self):
        result = cmb_residual_fraction_resolved()
        assert result["sigma_residual_0"] == pytest.approx(0.26)

    def test_sigma_nlo_less_than_sigma_0(self):
        result = cmb_residual_fraction_resolved()
        assert result["sigma_residual_nlo"] < result["sigma_residual_0"]

    def test_fraction_resolved_positive(self):
        result = cmb_residual_fraction_resolved()
        assert result["fraction_resolved"] > 0

    def test_fraction_resolved_less_than_one(self):
        # Partial resolution only; not full closure
        result = cmb_residual_fraction_resolved()
        assert result["fraction_resolved"] < 1.0

    def test_pct_resolved_consistent_with_fraction(self):
        result = cmb_residual_fraction_resolved()
        assert result["pct_resolved"] == pytest.approx(
            result["fraction_resolved"] * 100.0, rel=1e-10
        )

    def test_zphi_nlo_consistent(self):
        result = cmb_residual_fraction_resolved()
        assert result["zphi_nlo"] == pytest.approx(
            result["zphi_0"] + result["delta_zphi_g4"], rel=1e-10
        )


# ── g4_zphi_correction_report ─────────────────────────────────────────────────


class TestG4ZphiCorrectionReport:
    @pytest.fixture(scope="class")
    def report(self):
        return g4_zphi_correction_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 519

    def test_status(self, report):
        assert report["status"] == "FRONTIER_COMPUTATION"

    def test_track_label(self, report):
        assert "ADJACENT TRACK" in report["track"]

    def test_no_hardgate_score_change(self, report):
        assert report["no_hardgate_score_change"] is True

    def test_cy3_benchmark(self, report):
        cy3 = report["cy3_benchmark"]
        assert cy3["h11"] == 1
        assert cy3["h21"] == 101
        assert cy3["chi"] == -200

    def test_zphi_0_present(self, report):
        assert report["zphi_0"] > 0

    def test_delta_zphi_g4_present(self, report):
        assert report["delta_zphi_g4"] > 0

    def test_zphi_nlo_greater(self, report):
        assert report["zphi_nlo"] > report["zphi_0"]

    def test_cmb_amplitude_residual(self, report):
        cmb = report["cmb_amplitude_residual"]
        assert cmb["fraction_resolved"] > 0
        assert cmb["fraction_resolved"] < 1.0
        assert cmb["architecture_limit_status"] == "PARTIALLY_RESOLVED_BY_11D_G4"

    def test_upstream_pillars(self, report):
        assert 518 in report["upstream_pillars"]
        assert 355 in report["upstream_pillars"]

    def test_downstream_pillars(self, report):
        assert 522 in report["downstream_pillars"]
        assert 524 in report["downstream_pillars"]

    def test_deterministic(self):
        r1 = g4_zphi_correction_report()
        r2 = g4_zphi_correction_report()
        assert r1["zphi_nlo"] == r2["zphi_nlo"]
        assert r1["delta_zphi_g4"] == r2["delta_zphi_g4"]


# ── g4_flux_selection_summary (extended) ──────────────────────────────────────


class TestG4FluxSelectionSummaryExtended:
    @pytest.fixture(scope="class")
    def summary(self):
        return g4_flux_selection_summary()

    def test_zphi_correction_key_present(self, summary):
        assert "zphi_correction" in summary

    def test_zphi_correction_delta_positive(self, summary):
        assert summary["zphi_correction"]["delta_zphi_g4"] > 0

    def test_zphi_correction_nlo_positive(self, summary):
        assert summary["zphi_correction"]["zphi_nlo"] > 0

    def test_zphi_correction_pillar(self, summary):
        assert summary["zphi_correction"]["pillar"] == 519

    def test_zphi_correction_status(self, summary):
        assert summary["zphi_correction"]["status"] == "FRONTIER_COMPUTATION"

    def test_pct_residual_resolved_range(self, summary):
        pct = summary["zphi_correction"]["pct_residual_resolved"]
        assert 0 < pct < 100
