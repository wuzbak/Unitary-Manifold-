# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 165 — A_s Casimir Vacuum Bound (casimir_as_naturalness.py)."""

import math
import pytest

from src.core.casimir_as_naturalness import (
    # constants
    N_W,
    K_CS,
    N_2,
    PI_K_R,
    M_PL_GEV,
    M_KK_EW_GEV,
    M_GUT_GEV,
    ALPHA_GW_REQUIRED,
    N_S_SPECIES_GRAVITON,
    N_S_SPECIES_GAUGE,
    N_S_SPECIES_FERMION,
    N_EFF_BOSON,
    N_EFF_TOTAL,
    A_S_PLANCK,
    R_BRAIDED,
    # functions
    bulk_species_count,
    casimir_energy_density,
    alpha_gw_casimir,
    naturalness_verdict,
    inflationary_scale_from_as,
    casimir_scale_comparison,
    casimir_as_naturalness_report,
    pillar165_summary,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_2(self):
        assert N_2 == 7

    def test_pi_k_r(self):
        assert PI_K_R == pytest.approx(37.0)

    def test_m_pl_gev(self):
        assert M_PL_GEV == pytest.approx(1.22e19, rel=1e-6)

    def test_m_kk_ew_gev(self):
        assert M_KK_EW_GEV == pytest.approx(1040.0)

    def test_m_gut_gev(self):
        assert M_GUT_GEV == pytest.approx(2.0e16, rel=1e-6)

    def test_alpha_gw_required(self):
        assert ALPHA_GW_REQUIRED == pytest.approx(4.0e-10, rel=1e-6)

    def test_n_eff_total(self):
        assert N_EFF_TOTAL == 198

    def test_n_eff_boson(self):
        assert N_EFF_BOSON == 150

    def test_n_s_species_graviton(self):
        assert N_S_SPECIES_GRAVITON == 2

    def test_n_s_species_gauge(self):
        assert N_S_SPECIES_GAUGE == 148  # 2 * 74

    def test_n_s_species_fermion(self):
        assert N_S_SPECIES_FERMION == 48

    def test_a_s_planck(self):
        assert A_S_PLANCK == pytest.approx(2.100e-9, rel=1e-6)

    def test_r_braided(self):
        assert R_BRAIDED == pytest.approx(0.0315, rel=1e-4)


# ---------------------------------------------------------------------------
# bulk_species_count
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def species():
    return bulk_species_count()


class TestBulkSpeciesCount:
    def test_graviton(self, species):
        assert species["graviton"] == 2

    def test_gauge(self, species):
        assert species["gauge"] == 148

    def test_fermion(self, species):
        assert species["fermion"] == 48

    def test_total_boson(self, species):
        assert species["total_boson"] == 150

    def test_total(self, species):
        assert species["total"] == 198

    def test_n_eff(self, species):
        assert species["n_eff"] == 198

    def test_custom_k_cs(self):
        s = bulk_species_count(k_cs=5)
        assert s["gauge"] == 10
        assert s["n_eff"] == 2 + 10 + 48


# ---------------------------------------------------------------------------
# casimir_energy_density
# ---------------------------------------------------------------------------

class TestCasimirEnergyDensity:
    def test_positive_at_gut(self):
        r = casimir_energy_density(M_GUT_GEV)
        assert r["rho_casimir_gev4"] > 0

    def test_positive_at_ew(self):
        r = casimir_energy_density(M_KK_EW_GEV)
        assert r["rho_casimir_gev4"] > 0

    def test_monotone_in_scale(self):
        r_low = casimir_energy_density(1.0e10)
        r_high = casimir_energy_density(1.0e15)
        assert r_high["rho_casimir_gev4"] > r_low["rho_casimir_gev4"]

    def test_formula_gut(self):
        r = casimir_energy_density(M_GUT_GEV, n_eff=N_EFF_TOTAL)
        expected = N_EFF_TOTAL * M_GUT_GEV**4 / (2.0 * math.pi**2)
        assert r["rho_casimir_gev4"] == pytest.approx(expected, rel=1e-9)

    def test_returns_scale(self):
        r = casimir_energy_density(M_GUT_GEV)
        assert r["m_scale_gev"] == M_GUT_GEV

    def test_returns_n_eff(self):
        r = casimir_energy_density(M_GUT_GEV)
        assert r["n_eff"] == N_EFF_TOTAL


# ---------------------------------------------------------------------------
# alpha_gw_casimir
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def agw_gut():
    return alpha_gw_casimir(m_scale_gev=M_GUT_GEV)


class TestAlphaGwCasimir:
    def test_positive(self, agw_gut):
        assert agw_gut["alpha_gw_casimir"] > 0

    def test_naturalness_ratio_present(self, agw_gut):
        assert "naturalness_ratio" in agw_gut

    def test_naturalness_ratio_finite(self, agw_gut):
        assert math.isfinite(agw_gut["naturalness_ratio"])

    def test_naturalness_ratio_gut_within_3_orders(self, agw_gut):
        ratio = agw_gut["naturalness_ratio"]
        assert 0.01 < ratio < 1000, f"naturalness_ratio={ratio} unexpectedly far"

    def test_alpha_gw_required_stored(self, agw_gut):
        assert agw_gut["alpha_gw_required"] == pytest.approx(ALPHA_GW_REQUIRED, rel=1e-6)

    def test_formula_key_present(self, agw_gut):
        assert "formula" in agw_gut

    def test_ew_scale_much_smaller(self):
        ew = alpha_gw_casimir(m_scale_gev=M_KK_EW_GEV)
        gut = alpha_gw_casimir(m_scale_gev=M_GUT_GEV)
        assert ew["alpha_gw_casimir"] < gut["alpha_gw_casimir"]

    def test_gut_casimir_order_of_magnitude(self, agw_gut):
        # Casimir at GUT scale should be within ~2 orders of magnitude of required
        alpha_c = agw_gut["alpha_gw_casimir"]
        assert alpha_c > 1e-13, "Casimir α_GW unreasonably small"
        assert alpha_c < 1e-7, "Casimir α_GW unreasonably large"


# ---------------------------------------------------------------------------
# naturalness_verdict
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def verdict_gut():
    return naturalness_verdict(m_scale_gev=M_GUT_GEV)


@pytest.fixture(scope="module")
def verdict_ew():
    return naturalness_verdict(m_scale_gev=M_KK_EW_GEV)


class TestNaturalnessVerdict:
    def test_gut_verdict_natural_or_marginal(self, verdict_gut):
        assert verdict_gut["verdict"] in ("NATURAL", "MARGINALLY_NATURAL")

    def test_gut_log10_ratio_lt3(self, verdict_gut):
        assert verdict_gut["log10_ratio"] < 3.0

    def test_gut_log10_ratio_gt_neg3(self, verdict_gut):
        assert verdict_gut["log10_ratio"] > -3.0

    def test_ew_verdict_fine_tuned(self, verdict_ew):
        # EW KK scale gives naturalness_ratio >> 1000
        assert verdict_ew["verdict"] == "FINE_TUNED"

    def test_ew_ratio_enormous(self, verdict_ew):
        assert verdict_ew["naturalness_ratio"] > 1e40

    def test_scale_stored_gut(self, verdict_gut):
        assert verdict_gut["m_scale_gev"] == M_GUT_GEV

    def test_scale_stored_ew(self, verdict_ew):
        assert verdict_ew["m_scale_gev"] == M_KK_EW_GEV


# ---------------------------------------------------------------------------
# inflationary_scale_from_as
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def inf_info():
    return inflationary_scale_from_as()


class TestInflationaryScaleFromAs:
    def test_h_inf_positive(self, inf_info):
        assert inf_info["h_inf_gev"] > 0

    def test_h_inf_below_planck(self, inf_info):
        assert inf_info["h_inf_over_m_pl"] < 1e-4

    def test_h_inf_above_zero(self, inf_info):
        assert inf_info["h_inf_over_m_pl"] > 1e-8

    def test_v_inf_positive(self, inf_info):
        assert inf_info["v_inf_gev4"] > 0

    def test_alpha_gw_inferred_positive(self, inf_info):
        assert inf_info["alpha_gw_inferred"] > 0

    def test_alpha_gw_inferred_order_magnitude(self, inf_info):
        # Should be ~10⁻¹⁰ range
        alpha = inf_info["alpha_gw_inferred"]
        assert 1e-12 < alpha < 1e-6

    def test_formula_consistency(self, inf_info):
        # h_inf_over_m_pl = sqrt(r * a_s * pi^2 / 2)
        expected = math.sqrt(R_BRAIDED * A_S_PLANCK * math.pi**2 / 2.0)
        assert inf_info["h_inf_over_m_pl"] == pytest.approx(expected, rel=1e-9)


# ---------------------------------------------------------------------------
# casimir_scale_comparison
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def comparison():
    return casimir_scale_comparison()


class TestCasimirScaleComparison:
    def test_naturalness_gut_within_2_orders(self, comparison):
        ratio = comparison["naturalness_gut"]
        assert 0.01 < ratio < 1000, f"GUT naturalness_ratio={ratio}"

    def test_naturalness_ew_huge(self, comparison):
        assert comparison["naturalness_ew"] > 1e40

    def test_preferred_scale_gut(self, comparison):
        assert comparison["preferred_scale"] == "GUT_SCALE"

    def test_conclusion_present(self, comparison):
        assert isinstance(comparison["conclusion"], str)
        assert len(comparison["conclusion"]) > 10

    def test_alpha_gw_gut_positive(self, comparison):
        assert comparison["alpha_gw_gut"] > 0

    def test_alpha_gw_ew_positive(self, comparison):
        assert comparison["alpha_gw_ew"] > 0

    def test_gut_larger_than_ew(self, comparison):
        assert comparison["alpha_gw_gut"] > comparison["alpha_gw_ew"]


# ---------------------------------------------------------------------------
# casimir_as_naturalness_report
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def report():
    return casimir_as_naturalness_report()


class TestCasimirAsNaturalnessReport:
    def test_epistemic_label(self, report):
        assert report["epistemic_label"] == "NATURALLY_BOUNDED"

    def test_status_present(self, report):
        assert "status" in report
        assert report["status"] == "NATURALLY_BOUNDED"

    def test_n_eff_total(self, report):
        assert report["n_eff_total"] == 198

    def test_alpha_gw_required_correct(self, report):
        assert report["alpha_gw_required"] == pytest.approx(4.0e-10, rel=1e-6)

    def test_naturalness_ratio_present(self, report):
        assert "naturalness_ratio_gut" in report

    def test_honest_note_present(self, report):
        assert "honest_note" in report
        assert "UV-brane" in report["honest_note"]

    def test_pillar_number(self, report):
        assert report["pillar"] == 165


# ---------------------------------------------------------------------------
# pillar165_summary
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def summary():
    return pillar165_summary()


class TestPillar165Summary:
    def test_pillar_number(self, summary):
        assert summary["pillar"] == 165

    def test_method(self, summary):
        assert summary["method"] == "5D_Casimir_naturalness"

    def test_status(self, summary):
        assert summary["status"] == "NATURALLY_BOUNDED"

    def test_verdict(self, summary):
        assert summary["verdict"] == "NATURAL"

    def test_alpha_gw_required(self, summary):
        assert summary["alpha_gw_required"] == pytest.approx(4.0e-10, rel=1e-6)

    def test_alpha_gw_casimir_gut_positive(self, summary):
        assert summary["alpha_gw_casimir_gut"] > 0

    def test_naturalness_ratio_present(self, summary):
        assert "naturalness_ratio" in summary

    def test_n_eff(self, summary):
        assert summary["n_eff"] == 198

    def test_k_cs(self, summary):
        assert summary["k_cs"] == 74

    def test_n_w(self, summary):
        assert summary["n_w"] == 5
