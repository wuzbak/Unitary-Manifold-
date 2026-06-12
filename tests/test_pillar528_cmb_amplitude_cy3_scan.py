# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 528 — CMB Amplitude CY₃ Topology Scan."""

from __future__ import annotations

import math
import pytest

from src.eleventd.cmb_amplitude_cy3_scan import (
    A_S_INFLATION,
    A_S_PLANCK,
    A_S_PLANCK_SIGMA,
    A_S_UM_QUINTIC,
    CHI_CY3_QUINTIC,
    DELTA_KK_QUINTIC,
    F_SUPP_MAX,
    F_SUPP_MIN,
    F_SUPP_QUINTIC,
    H11_QUINTIC,
    H21_QUINTIC,
    K_CS,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    a_s_um,
    a_s_within_planck,
    architecture_verdict,
    delta_kk,
    f_supp,
    find_compatible_topologies,
    h21_from_chi,
    pillar528_report,
    scan_cy3_family,
    topology_resolves_amplitude,
)


class TestPillarMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 528

    def test_status_correct(self):
        assert PILLAR_STATUS == "CMB_AMPLITUDE_ARCHITECTURE_LIMIT_SCANNED"

    def test_title_mentions_scan(self):
        assert "Scan" in PILLAR_TITLE or "scan" in PILLAR_TITLE

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_chi_quintic(self):
        assert CHI_CY3_QUINTIC == -200

    def test_h11_quintic(self):
        assert H11_QUINTIC == 1

    def test_h21_quintic(self):
        assert H21_QUINTIC == 101


class TestConstants:
    def test_a_s_planck_value(self):
        assert abs(A_S_PLANCK - 2.100e-9) < 1e-12

    def test_a_s_planck_sigma(self):
        assert abs(A_S_PLANCK_SIGMA - 0.030e-9) < 1e-14

    def test_f_supp_quintic_value(self):
        assert abs(F_SUPP_QUINTIC - 5.6) < 1e-10

    def test_f_supp_band_contains_quintic(self):
        assert F_SUPP_MIN <= F_SUPP_QUINTIC <= F_SUPP_MAX

    def test_f_supp_min_positive(self):
        assert F_SUPP_MIN > 1.0

    def test_delta_kk_quintic(self):
        assert abs(DELTA_KK_QUINTIC - (F_SUPP_QUINTIC - 1.0)) < 1e-10

    def test_a_s_inflation_above_planck(self):
        assert A_S_INFLATION > A_S_PLANCK

    def test_a_s_um_quintic_close_to_planck(self):
        # By construction (calibration): A_s^{UM}@quintic == A_s^{Planck}
        assert abs(A_S_UM_QUINTIC - A_S_PLANCK) < 1e-15


class TestH21FromChi:
    def test_quintic(self):
        assert abs(h21_from_chi(CHI_CY3_QUINTIC, H11_QUINTIC) - H21_QUINTIC) < 1e-10

    def test_chi_zero(self):
        assert abs(h21_from_chi(0, 1) - 1.0) < 1e-10

    def test_chi_negative_increases_h21(self):
        h21_small = h21_from_chi(-10, 1)
        h21_large = h21_from_chi(-200, 1)
        assert h21_large > h21_small

    def test_formula(self):
        chi = -100
        assert abs(h21_from_chi(chi, 2) - (2 - chi / 2)) < 1e-10


class TestDeltaKK:
    def test_quintic_matches_calibration(self):
        dk = delta_kk(CHI_CY3_QUINTIC)
        assert abs(dk - DELTA_KK_QUINTIC) < 1e-10

    def test_zero_for_zero_h21(self):
        # χ = 2(h11 - h21) = 2×1 = 2 → h21=0
        assert delta_kk(2, 1) == 0.0

    def test_smaller_absolute_chi_gives_smaller_delta(self):
        dk_small = delta_kk(-20)
        dk_large = delta_kk(-200)
        assert dk_small < dk_large

    def test_positive(self):
        assert delta_kk(CHI_CY3_QUINTIC) > 0

    def test_scales_linearly_with_h21(self):
        dk_100 = delta_kk(-198, 1)  # h21=100
        dk_101 = delta_kk(-200, 1)  # h21=101
        ratio = dk_101 / dk_100
        assert abs(ratio - 101 / 100) < 1e-8


class TestFSupp:
    def test_quintic(self):
        fs = f_supp(CHI_CY3_QUINTIC)
        assert abs(fs - F_SUPP_QUINTIC) < 1e-10

    def test_greater_than_one(self):
        assert f_supp(CHI_CY3_QUINTIC) > 1

    def test_unity_for_h21_zero(self):
        assert abs(f_supp(2, 1) - 1.0) < 1e-10

    def test_larger_chi_gives_larger_f_supp(self):
        fs_small = f_supp(-20)
        fs_large = f_supp(-200)
        assert fs_large > fs_small


class TestASUM:
    def test_quintic_equals_planck(self):
        # Calibration identity
        assert abs(a_s_um(CHI_CY3_QUINTIC) - A_S_PLANCK) < 1e-20

    def test_smaller_chi_gives_larger_a_s(self):
        # Less suppression → higher A_s
        a_small = a_s_um(-20)
        a_large = a_s_um(-200)
        assert a_small > a_large

    def test_positive(self):
        assert a_s_um(CHI_CY3_QUINTIC) > 0


class TestASWithinPlanck:
    def test_quintic_within_1sigma(self):
        # By construction (calibration)
        assert a_s_within_planck(CHI_CY3_QUINTIC) is True

    def test_very_suppressed_outside_1sigma(self):
        # Very large |χ| → large suppression → A_s much below Planck
        assert a_s_within_planck(-960) is False

    def test_small_chi_may_resolve(self):
        # Very small |χ| → f_supp ≈ 1 → A_s ≈ A_s_inflation >> Planck
        # (actually above Planck, so also outside 1σ)
        a = a_s_um(-2)
        # Should be much above Planck (f_supp ≈ 1)
        assert a > A_S_PLANCK * 2  # at least 2× Planck


class TestTopologyResolvesAmplitude:
    def test_quintic_returns_dict(self):
        r = topology_resolves_amplitude(CHI_CY3_QUINTIC)
        assert isinstance(r, dict)

    def test_quintic_keys_present(self):
        r = topology_resolves_amplitude(CHI_CY3_QUINTIC)
        for key in ("chi", "h11", "h21", "f_supp", "planck_sigma_residual",
                    "within_1sigma", "verdict"):
            assert key in r

    def test_quintic_chi_recorded(self):
        r = topology_resolves_amplitude(CHI_CY3_QUINTIC)
        assert r["chi"] == CHI_CY3_QUINTIC

    def test_quintic_within_1sigma(self):
        r = topology_resolves_amplitude(CHI_CY3_QUINTIC)
        assert r["within_1sigma"] is True

    def test_suppressed_topology_verdict(self):
        r = topology_resolves_amplitude(-960)
        assert r["verdict"] == "SUPPRESSED"


class TestScanCY3Family:
    def test_returns_list(self):
        results = scan_cy3_family(-200, -2, 2)
        assert isinstance(results, list)

    def test_nonempty(self):
        results = scan_cy3_family(-200, -2, 2)
        assert len(results) > 0

    def test_includes_quintic(self):
        results = scan_cy3_family(-200, -200, 2)
        assert len(results) == 1
        assert results[0]["chi"] == -200

    def test_ordered_by_chi(self):
        results = scan_cy3_family(-10, -2, 2)
        chis = [r["chi"] for r in results]
        assert chis == sorted(chis)


class TestFindCompatibleTopologies:
    def test_returns_list(self):
        compat = find_compatible_topologies(-960, -2)
        assert isinstance(compat, list)

    def test_quintic_in_compatible(self):
        compat = find_compatible_topologies(-960, -2, 1, 1.0)
        chis = [r["chi"] for r in compat]
        assert CHI_CY3_QUINTIC in chis


class TestArchitectureVerdict:
    def setup_method(self):
        self.v = architecture_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_quintic_f_supp_correct(self):
        assert abs(self.v["quintic_f_supp"] - F_SUPP_QUINTIC) < 1e-8

    def test_note_present(self):
        assert "note" in self.v
        assert len(self.v["note"]) > 20

    def test_verdict_present(self):
        assert "verdict" in self.v

    def test_n_topologies_scanned_positive(self):
        assert self.v["n_topologies_scanned"] > 0

    def test_quintic_sigma_residual_small(self):
        # |quintic A_s - Planck| / sigma should be ~0 (calibration)
        assert abs(self.v["quintic_a_s_sigma_residual"]) < 1e-3


class TestPillar528Report:
    def setup_method(self):
        self.r = pillar528_report()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_pillar_number(self):
        assert self.r["pillar"] == 528

    def test_status_correct(self):
        assert self.r["status"] == "CMB_AMPLITUDE_ARCHITECTURE_LIMIT_SCANNED"

    def test_quintic_cy3_section(self):
        assert "quintic_cy3" in self.r
        q = self.r["quintic_cy3"]
        assert q["chi"] == CHI_CY3_QUINTIC
        assert q["h21"] == H21_QUINTIC

    def test_scan_section(self):
        assert "scan" in self.r
        assert "verdict" in self.r["scan"]

    def test_architecture_limit_section(self):
        assert "architecture_limit" in self.r
        al = self.r["architecture_limit"]
        assert al["pillar_certified"] == 518
        assert al["confirmed_by_scan"] is True
        assert al["irreducible_in_5D_EFT"] is True

    def test_upstream_contains_526_527(self):
        assert 526 in self.r["upstream"]
        assert 527 in self.r["upstream"]

    def test_summary_mentions_architecture(self):
        assert "architecture" in self.r["summary"].lower()
