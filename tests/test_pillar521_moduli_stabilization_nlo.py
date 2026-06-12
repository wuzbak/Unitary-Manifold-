# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 521 — 11D Goldberger-Wise moduli stabilization to NLO.

Status: CONDITIONAL_DERIVATION (🔵 ADJACENT TRACK)
"""

from __future__ import annotations

import math
import pytest

from src.eleventd.moduli_stabilization_nlo import (
    CHI_CY3,
    ETA_BAR_0,
    GW_EPSILON,
    GW_K,
    K_CS,
    NLO_BOUND_PCT,
    N_W,
    PI_KR_0,
    VOL_CY3_REF,
    delta_v_g4,
    lambda_g4,
    minimize_radion_nlo,
    minimize_vol_cy3,
    moduli_stabilization_nlo_report,
    nlo_moduli_minimum,
    nlo_reheating_corrections,
    nlo_seed_corrections,
    v_gw_11d,
    v_gw_5d,
)


# ── Module constants ───────────────────────────────────────────────────────────


class TestModuleConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_pi_kr_0(self):
        assert PI_KR_0 == pytest.approx(37.0)

    def test_chi_cy3(self):
        assert CHI_CY3 == -200

    def test_nlo_bound(self):
        assert NLO_BOUND_PCT == pytest.approx(0.74)

    def test_vol_cy3_ref(self):
        expected = (37.0 / 74) ** 3
        assert VOL_CY3_REF == pytest.approx(expected, rel=1e-10)

    def test_eta_bar_0(self):
        assert ETA_BAR_0 == pytest.approx(0.5)


# ── v_gw_5d ───────────────────────────────────────────────────────────────────


class TestVGW5D:
    def test_formula(self):
        pi_kr = PI_KR_0
        eps = GW_EPSILON
        expected = 4 * eps**2 * math.exp(-2 * pi_kr) - eps**2 * math.exp(-4 * pi_kr)
        assert v_gw_5d(pi_kr) == pytest.approx(expected, rel=1e-8)

    def test_decreases_with_pi_kr(self):
        v1 = v_gw_5d(10.0)
        v2 = v_gw_5d(30.0)
        assert v2 < v1

    def test_custom_epsilon(self):
        v1 = v_gw_5d(PI_KR_0, epsilon=0.1)
        v2 = v_gw_5d(PI_KR_0, epsilon=0.2)
        # v2 should be 4× v1 since ε² dependence
        assert abs(v2 / v1 - 4.0) < 0.01


# ── lambda_g4 ─────────────────────────────────────────────────────────────────


class TestLambdaG4:
    def test_formula(self):
        expected = 200.0 / (24.0 * math.pi)
        assert lambda_g4() == pytest.approx(expected, rel=1e-10)

    def test_positive(self):
        assert lambda_g4() > 0

    def test_zero_for_zero_chi(self):
        assert lambda_g4(chi=0) == pytest.approx(0.0)

    def test_scales_with_abs_chi(self):
        assert lambda_g4(-100) == pytest.approx(lambda_g4(100), rel=1e-10)


# ── delta_v_g4 ────────────────────────────────────────────────────────────────


class TestDeltaVG4:
    def test_negative(self):
        dv = delta_v_g4(PI_KR_0, VOL_CY3_REF)
        assert dv < 0

    def test_formula(self):
        lam = lambda_g4()
        vol = VOL_CY3_REF
        pi_kr = PI_KR_0
        expected = -lam * vol * math.exp(-2.0 * pi_kr / 3.0)
        assert delta_v_g4(pi_kr, vol) == pytest.approx(expected, rel=1e-10)

    def test_scales_with_vol(self):
        dv1 = delta_v_g4(PI_KR_0, 0.1)
        dv2 = delta_v_g4(PI_KR_0, 0.2)
        assert dv2 == pytest.approx(2 * dv1, rel=1e-10)


# ── v_gw_11d ──────────────────────────────────────────────────────────────────


class TestVGW11D:
    def test_equals_sum(self):
        pi_kr = PI_KR_0
        vol = VOL_CY3_REF
        v5d = v_gw_5d(pi_kr)
        dv = delta_v_g4(pi_kr, vol)
        assert v_gw_11d(pi_kr, vol) == pytest.approx(v5d + dv, rel=1e-10)

    def test_less_than_5d(self):
        # G4 term is negative, so 11D potential < 5D potential
        v5d = v_gw_5d(PI_KR_0)
        v11d = v_gw_11d(PI_KR_0, VOL_CY3_REF)
        assert v11d < v5d


# ── minimize_radion_nlo ───────────────────────────────────────────────────────


class TestMinimizeRadionNlo:
    @pytest.fixture(scope="class")
    def result(self):
        return minimize_radion_nlo()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_required_keys(self, result):
        for k in ("pi_kr_min", "v_min", "delta_pi_kr", "nlo_shift_pct"):
            assert k in result

    def test_pi_kr_min_positive(self, result):
        assert result["pi_kr_min"] > 0

    def test_nlo_shift_pct_within_bound(self, result):
        # NLO shift should be modest
        assert result["nlo_shift_pct"] < 20.0  # 20% generous bound for search

    def test_deterministic(self):
        r1 = minimize_radion_nlo()
        r2 = minimize_radion_nlo()
        assert r1["pi_kr_min"] == pytest.approx(r2["pi_kr_min"])


# ── minimize_vol_cy3 ──────────────────────────────────────────────────────────


class TestMinimizeVolCY3:
    @pytest.fixture(scope="class")
    def result(self):
        return minimize_vol_cy3()

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_required_keys(self, result):
        for k in ("vol_min", "v_min", "delta_vol", "nlo_shift_pct"):
            assert k in result

    def test_vol_min_positive(self, result):
        assert result["vol_min"] > 0

    def test_deterministic(self):
        r1 = minimize_vol_cy3()
        r2 = minimize_vol_cy3()
        assert r1["vol_min"] == pytest.approx(r2["vol_min"])


# ── nlo_moduli_minimum ────────────────────────────────────────────────────────


class TestNLOModuliMinimum:
    @pytest.fixture(scope="class")
    def minimum(self):
        return nlo_moduli_minimum()

    def test_required_keys(self, minimum):
        for k in ("pi_kr_0", "pi_kr_nlo", "pi_kr_shift_pct",
                  "vol_cy3_ref", "vol_cy3_nlo", "vol_cy3_shift_pct"):
            assert k in minimum

    def test_pi_kr_nlo_positive(self, minimum):
        assert minimum["pi_kr_nlo"] > 0

    def test_vol_cy3_nlo_positive(self, minimum):
        assert minimum["vol_cy3_nlo"] > 0

    def test_pi_kr_0_matches_constant(self, minimum):
        assert minimum["pi_kr_0"] == pytest.approx(PI_KR_0)

    def test_vol_cy3_ref_matches_constant(self, minimum):
        assert minimum["vol_cy3_ref"] == pytest.approx(VOL_CY3_REF)


# ── nlo_seed_corrections ──────────────────────────────────────────────────────


class TestNLOSeedCorrections:
    @pytest.fixture(scope="class")
    def seed(self):
        return nlo_seed_corrections()

    def test_required_keys(self, seed):
        for k in ("eta_bar_0", "eta_bar_nlo", "pi_kr_0", "pi_kr_nlo",
                  "pi_kr_shift_pct", "vol_cy3_nlo", "vol_cy3_shift_pct",
                  "within_nlo_bound_pct_0_74"):
            assert k in seed

    def test_eta_bar_nlo_equals_0(self, seed):
        # η̄ unchanged by G4 NLO at this order
        assert seed["eta_bar_nlo"] == pytest.approx(seed["eta_bar_0"])

    def test_pi_kr_nlo_positive(self, seed):
        assert seed["pi_kr_nlo"] > 0

    def test_seed_purity_noted(self, seed):
        assert "geometric_only" in seed["seed_purity"]


# ── nlo_reheating_corrections ─────────────────────────────────────────────────


class TestNLOReheatingCorrections:
    def test_zero_shift_no_correction(self):
        result = nlo_reheating_corrections(PI_KR_0, PI_KR_0)
        assert result["delta_pi_kr"] == pytest.approx(0.0)
        assert result["t_rh_shift_pct"] == pytest.approx(0.0, abs=1e-10)
        assert result["n_e_shift_pct"] == pytest.approx(0.0, abs=1e-10)

    def test_small_shift_within_bound(self):
        # A 0.1% shift in πkR should give small T_RH shift
        pi_kr_nlo = PI_KR_0 * 1.001
        result = nlo_reheating_corrections(pi_kr_nlo)
        assert result["t_rh_shift_pct"] < 1.0

    def test_required_keys(self):
        result = nlo_reheating_corrections(PI_KR_0)
        for k in ("pi_kr_nlo", "pi_kr_0", "delta_pi_kr",
                  "t_rh_shift_pct", "n_e_shift_pct", "within_nlo_bound"):
            assert k in result


# ── moduli_stabilization_nlo_report ──────────────────────────────────────────


class TestModuliStabilizationNloReport:
    @pytest.fixture(scope="class")
    def report(self):
        return moduli_stabilization_nlo_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 521

    def test_status(self, report):
        assert report["status"] == "CONDITIONAL_DERIVATION"

    def test_track_label(self, report):
        assert "ADJACENT TRACK" in report["track"]

    def test_prerequisite_pillars(self, report):
        assert 92 in report["prerequisite_pillars"]
        assert 364 in report["prerequisite_pillars"]

    def test_nlo_minimum_present(self, report):
        nm = report["nlo_minimum"]
        assert nm["pi_kr_nlo"] > 0
        assert nm["vol_cy3_nlo"] > 0

    def test_nlo_seed_present(self, report):
        seed = report["nlo_seed"]
        assert seed["eta_bar"] == pytest.approx(0.5)
        assert seed["pi_kr"] > 0

    def test_nlo_bound_check_present(self, report):
        assert "nlo_bound_check" in report
        assert "reference_pillar" in report["nlo_bound_check"]
        assert report["nlo_bound_check"]["reference_pillar"] == 388

    def test_downstream_unlocks(self, report):
        assert "pillar_520" in report["downstream_unlocks"]
        assert "pillar_522" in report["downstream_unlocks"]

    def test_no_hardgate_score_change(self, report):
        assert report["no_hardgate_score_change"] is True

    def test_deterministic(self):
        r1 = moduli_stabilization_nlo_report()
        r2 = moduli_stabilization_nlo_report()
        assert (
            r1["nlo_minimum"]["pi_kr_nlo"]
            == pytest.approx(r2["nlo_minimum"]["pi_kr_nlo"])
        )
        assert (
            r1["nlo_minimum"]["vol_cy3_nlo"]
            == pytest.approx(r2["nlo_minimum"]["vol_cy3_nlo"])
        )
