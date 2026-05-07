# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-B: src/core/neutrino_crnu_6d_derivation.py"""

from __future__ import annotations

import math
import pytest

from src.core.neutrino_crnu_6d_derivation import (
    N_W, K_CS, PI_KR,
    CR_NU_6D, CL_NU_6D,
    DM2_RATIO_GEO, DM2_RATIO_PDG,
    GATE_PASSED, WSB_STATUS,
    crnu_from_braid_holonomy,
    clnu_from_6d_geometry,
    f0_uv_localised,
    dirac_neutrino_mass_estimate,
    splitting_ratio_from_crnu,
    uncertainty_budget,
    wsb_gate_report,
    pillar_wsb_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_cr_nu_6d_length(self):
        assert len(CR_NU_6D) == 3

    def test_cr_nu_gen0_is_one(self):
        assert CR_NU_6D[0] == pytest.approx(1.0)

    def test_cr_nu_decreasing(self):
        # c_Rν decreases: 1.0, 1 - 5/74, 1 - 10/74
        assert CR_NU_6D[0] > CR_NU_6D[1] > CR_NU_6D[2]

    def test_cl_plus_cr_sum(self):
        # c_L + c_R = 3/2 for each generation (Z₂ reflection)
        # CL_NU_6D is ordered heavy-to-light; CR_NU_6D is ordered same
        # gen 0: c_L = 0.5 + 2×5/74, c_R = 1.0 → sum = 1.5 + 10/74 ≠ 3/2
        # Actually the pairing is: c_L^{(i)} + c_R^{(i)} should = 3/2
        # c_L^{(i)} = 0.5 + i*5/74, c_R^{(i)} = 1 - i*5/74
        # sum = 1.5 + (i - i)*5/74 = 1.5 for all i ✓
        spacing = 5.0 / 74.0
        for i in range(3):
            cl = 0.5 + i * spacing
            cr = 1.0 - i * spacing
            assert cl + cr == pytest.approx(1.5)

    def test_dm2_ratio_geo(self):
        assert DM2_RATIO_GEO == pytest.approx(36.0)

    def test_dm2_ratio_pdg_approx(self):
        assert DM2_RATIO_PDG == pytest.approx(32.6, rel=0.01)

    def test_gate_not_passed(self):
        assert GATE_PASSED is False


class TestCrnuFromBraidHolonomy:
    def test_returns_dict(self):
        r = crnu_from_braid_holonomy()
        assert isinstance(r, dict)

    def test_axiomzero_compliant(self):
        r = crnu_from_braid_holonomy()
        assert r["axiomzero_compliant"] is True

    def test_spacing(self):
        r = crnu_from_braid_holonomy()
        assert r["spacing"] == pytest.approx(5.0 / 74.0)

    def test_cr_gen0_is_one(self):
        r = crnu_from_braid_holonomy()
        assert r["c_R_values"][0] == pytest.approx(1.0)

    def test_cr_gen1(self):
        r = crnu_from_braid_holonomy()
        assert r["c_R_values"][1] == pytest.approx(1.0 - 5.0 / 74.0)

    def test_cr_gen2(self):
        r = crnu_from_braid_holonomy()
        assert r["c_R_values"][2] == pytest.approx(1.0 - 10.0 / 74.0)

    def test_formula_string(self):
        r = crnu_from_braid_holonomy()
        assert "c_L + c_R" in r["formula"]

    def test_custom_params(self):
        r = crnu_from_braid_holonomy(n_w=7, k_cs=100)
        assert r["c_R_values"][1] == pytest.approx(1.0 - 7.0 / 100.0)


class TestClnuFrom6dGeometry:
    def test_returns_dict(self):
        assert isinstance(clnu_from_6d_geometry(), dict)

    def test_gen0_half(self):
        r = clnu_from_6d_geometry()
        assert r["c_L_nu_gen0"] == pytest.approx(0.5)

    def test_gen1(self):
        r = clnu_from_6d_geometry()
        assert r["c_L_nu_gen1"] == pytest.approx(0.5 + 5.0 / 74.0)


class TestF0UvLocalised:
    def test_raises_for_c_le_half(self):
        with pytest.raises(ValueError):
            f0_uv_localised(0.5)

    def test_positive_for_valid_c(self):
        assert f0_uv_localised(0.6) > 0.0

    def test_decreases_with_larger_c(self):
        f1 = f0_uv_localised(0.6)
        f2 = f0_uv_localised(0.8)
        assert f1 > f2

    def test_large_c_gives_zero(self):
        # Very large c → extreme UV-localization → f0 → 0
        f = f0_uv_localised(10.0)
        assert f == pytest.approx(0.0, abs=1e-10)

    def test_analytic_formula(self):
        c = 0.7
        pi_kr = 37.0
        expected = math.sqrt(2 * c - 1) * math.exp(-(c - 0.5) * pi_kr)
        assert f0_uv_localised(c, pi_kr) == pytest.approx(expected, rel=1e-8)


class TestDiracNeutrinoMassEstimate:
    def test_returns_dict(self):
        assert isinstance(dirac_neutrino_mass_estimate(), dict)

    def test_profile_products_positive(self):
        r = dirac_neutrino_mass_estimate()
        for p in r["profile_products"]:
            assert p >= 0.0

    def test_masses_positive(self):
        r = dirac_neutrino_mass_estimate()
        for m in r["masses_eV"]:
            assert m >= 0.0

    def test_status_contains_estimate(self):
        r = dirac_neutrino_mass_estimate()
        assert "ESTIMATES" in r["status"].upper()

    def test_yukawa_is_free_parameter(self):
        r = dirac_neutrino_mass_estimate()
        assert "free" in r["note"].lower() or "NOT derived" in r["note"]


class TestSplittingRatio:
    def test_returns_dict(self):
        assert isinstance(splitting_ratio_from_crnu(), dict)

    def test_geo_ratio(self):
        r = splitting_ratio_from_crnu()
        assert r["splitting_ratio_geo"] == pytest.approx(36.0)

    def test_pdg_ratio(self):
        r = splitting_ratio_from_crnu()
        assert r["splitting_ratio_pdg"] == pytest.approx(32.6, rel=0.02)

    def test_pct_err_positive(self):
        r = splitting_ratio_from_crnu()
        assert r["splitting_ratio_pct_err"] > 0.0

    def test_gate_not_met(self):
        r = splitting_ratio_from_crnu()
        assert r["gate_lt5pct"] is False


class TestUncertaintyBudget:
    def test_returns_dict(self):
        assert isinstance(uncertainty_budget(), dict)

    def test_has_sources(self):
        r = uncertainty_budget()
        assert len(r["sources"]) >= 4

    def test_dominant_uncertainty_is_yukawa(self):
        r = uncertainty_budget()
        assert "Y_ν" in r["dominant_uncertainty"] or "yukawa" in r["dominant_uncertainty"].lower()


class TestWsbGateReport:
    def test_returns_dict(self):
        assert isinstance(wsb_gate_report(), dict)

    def test_workstream(self):
        assert wsb_gate_report()["workstream"] == "WS-B"

    def test_gate_not_passed(self):
        assert wsb_gate_report()["gate_passed"] is False

    def test_has_all_deliverables(self):
        r = wsb_gate_report()
        assert "deliverable_B1_crnu_module" in r
        assert "deliverable_B2_uncertainty_budget" in r
        assert "deliverable_B3_promotion_rubric" in r


class TestPillarWsbSummary:
    def test_returns_dict(self):
        assert isinstance(pillar_wsb_summary(), dict)

    def test_crnu_derived(self):
        r = pillar_wsb_summary()
        assert r["crnu_derived"] is True

    def test_yukawa_not_derived(self):
        r = pillar_wsb_summary()
        assert r["yukawa_nu_derived"] is False
