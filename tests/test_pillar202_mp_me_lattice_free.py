# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 202 — Lattice-Free m_p/m_e from Braid Geometry."""

import math
import pytest

from src.core.pillar202_mp_me_lattice_free import (
    N_W, K_CS, N_C,
    MP_ME_GEO, MP_ME_PDG, MP_ME_RESIDUAL_PCT,
    mp_me_geometric,
    proton_sector_chain,
    electron_sector_chain,
    ratio_derivation,
    axiom_zero_audit,
    pillar202_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_mp_me_geo_formula(self):
        expected = 74 ** 2 / 3.0
        assert MP_ME_GEO == pytest.approx(expected, rel=1e-6)

    def test_mp_me_geo_value(self):
        assert MP_ME_GEO == pytest.approx(5476.0 / 3.0, rel=1e-6)

    def test_mp_me_pdg(self):
        assert MP_ME_PDG == pytest.approx(1836.15267, rel=1e-6)

    def test_residual_below_1pct(self):
        assert MP_ME_RESIDUAL_PCT < 1.0

    def test_residual_positive(self):
        assert MP_ME_RESIDUAL_PCT >= 0.0

    def test_mp_me_geo_below_pdg(self):
        assert MP_ME_GEO < MP_ME_PDG

    def test_residual_approx_059(self):
        assert 0.4 < MP_ME_RESIDUAL_PCT < 0.8


class TestMpMeGeometric:
    def test_default_value(self):
        assert mp_me_geometric() == pytest.approx(5476.0 / 3.0, rel=1e-6)

    def test_custom_kcs_nw(self):
        result = mp_me_geometric(100, 7)
        n_c = math.ceil(7 / 2)  # = 4
        assert result == pytest.approx(10000.0 / 4.0, rel=1e-6)

    def test_positive(self):
        assert mp_me_geometric() > 0

    def test_sensitivity_to_k_cs(self):
        r74 = mp_me_geometric(74, 5)
        r72 = mp_me_geometric(72, 5)
        # 72²/3 = 5184/3 = 1728 vs 74²/3 = 1825
        assert r74 > r72

    def test_kcs_74_nw_5_is_1825(self):
        assert mp_me_geometric(74, 5) == pytest.approx(1825.333, rel=1e-3)


class TestProtonSectorChain:
    def setup_method(self):
        self.result = proton_sector_chain()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pi_kr(self):
        assert self.result["pi_kR"] == pytest.approx(37.0)

    def test_r_dil_positive(self):
        assert self.result["r_dil"] > 0

    def test_r_dil_formula(self):
        assert "K_CS" in self.result["r_dil_formula"]

    def test_m_rho_positive(self):
        assert self.result["m_rho_over_mkk"] > 0

    def test_lambda_qcd_positive(self):
        assert self.result["lambda_qcd_over_mkk"] > 0

    def test_c_lat_note_present(self):
        assert "lattice" in self.result["c_lat_note"].lower()

    def test_status_external(self):
        assert "EXTERNAL" in self.result["status"]

    def test_m_p_scale_positive(self):
        assert self.result["m_p_scale_over_mkk"] > 0


class TestElectronSectorChain:
    def setup_method(self):
        self.result = electron_sector_chain()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_alpha_y_positive(self):
        assert self.result["alpha_Y_at_MKK"] > 0

    def test_alpha_y_formula(self):
        assert "K_CS" in self.result["alpha_Y_formula"]

    def test_y_eff_scale_positive(self):
        assert self.result["Y_eff_scale"] > 0

    def test_m_e_scale_positive(self):
        assert self.result["m_e_scale_over_mkk"] > 0

    def test_caveats_nonempty(self):
        assert len(self.result["caveats"]) > 0

    def test_status_schematic(self):
        assert "SCHEMATIC" in self.result["status"]


class TestRatioDerivation:
    def setup_method(self):
        self.result = ratio_derivation()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_axiom_zero_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_no_sm_anchors(self):
        assert self.result["sm_anchors_used"] == []

    def test_formula(self):
        assert "K_CS" in self.result["formula"]

    def test_ratio_geo(self):
        assert self.result["ratio_geo"] == pytest.approx(5476.0 / 3.0, rel=1e-6)

    def test_ratio_pdg(self):
        assert self.result["ratio_pdg"] == pytest.approx(1836.15267, rel=1e-6)

    def test_residual_below_1(self):
        assert self.result["residual_pct"] < 1.0

    def test_permanent_limitations_nonempty(self):
        assert len(self.result["permanent_limitations"]) > 0

    def test_status_geometric(self):
        assert "GEOMETRIC IDENTITY" in self.result["status"]

    def test_pillar_tag(self):
        assert self.result["pillar"] == "202"

    def test_algebra_sketch_present(self):
        assert "m_p" in self.result["algebra_sketch"]


class TestAxiomZeroAudit:
    def setup_method(self):
        self.result = axiom_zero_audit()

    def test_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_zero_sm_anchors(self):
        assert self.result["sm_anchors_count"] == 0

    def test_k_cs_in_inputs(self):
        inputs_str = " ".join(self.result["derivation_inputs"])
        assert "74" in inputs_str or "K_CS" in inputs_str

    def test_mp_in_excluded(self):
        excluded_str = " ".join(self.result["quantities_not_used"])
        assert "938" in excluded_str or "m_p" in excluded_str


class TestPillar202Summary:
    def setup_method(self):
        self.result = pillar202_summary()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "202"

    def test_version(self):
        assert "v10" in self.result["version"]

    def test_result_residual_below_1(self):
        assert self.result["result"]["residual_pct"] < 1.0

    def test_formula_string(self):
        assert "5476" in self.result["formula"] or "74²" in self.result["formula"]

    def test_toe_impact_present(self):
        assert "TOE" in self.result["toe_impact"].upper() or "score" in self.result["toe_impact"].lower()

    def test_status_geometric(self):
        assert "GEOMETRIC" in self.result["status"]

    def test_c_lat_honest(self):
        assert "C_lat" in self.result["status"] or "C_lat" in self.result["toe_impact"] or "lattice" in self.result["status"].lower()
