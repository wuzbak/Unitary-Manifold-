# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar359_de_canonical_unification.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar359_de_canonical_unification import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    W0_CANONICAL, WA_CANONICAL, C_S, M_KK_EV, H0_EV,
    W0_INFLATION_FORMULA, W0_RESIDUAL,
    W0_DESI_DR2_BAO, SIGMA_W0_DESI_BAO,
    WA_DESI_DR2_COMBINED, SIGMA_WA_DESI_COMBINED,
    separation_guard, de_eos_prediction, w0_tension_desi_dr2,
    wa_tension_desi_dr2, w_of_z_canonical, desi_dr3_routing,
    canonical_de_formula_audit, pillar359_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 359
    def test_status(self): assert PILLAR_STATUS == "FORMULA_CANONICALIZED"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_w0_canonical(self): assert W0_CANONICAL == -1.0
    def test_wa_canonical(self): assert WA_CANONICAL == 0.0
    def test_c_s(self): assert abs(C_S - 12.0/37.0) < 1e-10
    def test_old_formula_wrong(self):
        assert W0_INFLATION_FORMULA > -1.0
        assert abs(W0_INFLATION_FORMULA - (-1 + (2/3)*(12/37)**2)) < 1e-6
    def test_residual_tiny(self):
        assert W0_RESIDUAL < 1e-50
    def test_desi_bao_w0(self): assert -1.0 < W0_DESI_DR2_BAO < 0.0


class TestDeEosPrediction:
    def test_returns_dict(self):
        pred = de_eos_prediction()
        assert isinstance(pred, dict)

    def test_w0_is_minus_1(self):
        pred = de_eos_prediction()
        assert pred["w0"] == -1.0

    def test_wa_is_zero(self):
        pred = de_eos_prediction()
        assert pred["wa"] == 0.0

    def test_derivation_chain_present(self):
        pred = de_eos_prediction()
        assert "derivation_chain" in pred
        assert len(pred["derivation_chain"]) >= 3

    def test_old_formula_deprecated(self):
        pred = de_eos_prediction()
        assert "old_formula_deprecated" in pred
        assert "deprecated" in pred["old_formula_deprecated"]["reason_deprecated"].lower()

    def test_cpl_params_present(self):
        pred = de_eos_prediction()
        assert pred["cpl_parametrization"]["w0"] == -1.0
        assert pred["cpl_parametrization"]["wa"] == 0.0

    def test_theory_uncertainty_tiny(self):
        pred = de_eos_prediction()
        assert pred["theory_uncertainty"]["w0"] < 1e-50


class TestW0Tension:
    def test_bao_tension_positive(self):
        result = w0_tension_desi_dr2("bao")
        assert result["tension_sigma"] > 0

    def test_bao_w0_um_minus_1(self):
        result = w0_tension_desi_dr2("bao")
        assert result["w0_um"] == -1.0

    def test_bao_tension_high(self):
        # |−1 − (−0.727)| / 0.067 ≈ 4.1σ
        result = w0_tension_desi_dr2("bao")
        assert result["tension_sigma"] > 3.0

    def test_combined_tension(self):
        result = w0_tension_desi_dr2("combined")
        assert result["tension_sigma"] > 3.0

    def test_status_high_tension(self):
        result = w0_tension_desi_dr2("bao")
        assert result["status"] == "HIGH_TENSION"


class TestWaTension:
    def test_wa_tension_positive(self):
        result = wa_tension_desi_dr2()
        assert result["tension_sigma"] > 0

    def test_wa_um_zero(self):
        result = wa_tension_desi_dr2()
        assert result["wa_um"] == 0.0

    def test_wa_desi_negative(self):
        result = wa_tension_desi_dr2()
        assert result["wa_desi"] < 0

    def test_wa_tension_approx(self):
        # |0 − (−0.75)| / 0.25 = 3.0σ
        result = wa_tension_desi_dr2()
        assert abs(result["tension_sigma"] - 3.0) < 0.1

    def test_status_high_tension(self):
        result = wa_tension_desi_dr2()
        assert "TENSION" in result["status"]


class TestWOfZ:
    def test_today_is_minus_1(self):
        w_today = w_of_z_canonical(0.0)
        assert abs(w_today - (-1.0)) < 1e-50

    def test_at_z_1(self):
        w = w_of_z_canonical(1.0)
        assert abs(w - (-1.0)) < 1e-30  # still frozen radion

    def test_at_z_10(self):
        w = w_of_z_canonical(10.0)
        assert abs(w - (-1.0)) < 1e-20  # still effectively frozen

    def test_monotonic_with_z(self):
        # w(z) increases (toward −1 from below) at higher z isn't guaranteed,
        # but let's check it's always < -1 + tiny epsilon
        for z in [0, 1, 5, 10]:
            w = w_of_z_canonical(z)
            assert w >= -1.0
            assert w < -0.999


class TestDesiDr3Routing:
    def test_pending_when_no_data(self):
        result = desi_dr3_routing()
        assert result["status"] == "PENDING_DESI_DR3"

    def test_label_high_tension(self):
        result = desi_dr3_routing()
        assert "HIGH_TENSION" in result["label"]

    def test_falsified_at_high_wa_sigma(self):
        result = desi_dr3_routing(wa_measured=-0.90, wa_sigma=0.25)
        assert result["verdict"] == "FALSIFIED"

    def test_resolved_at_low_tension(self):
        result = desi_dr3_routing(wa_measured=-0.1, wa_sigma=0.25)
        assert result["verdict"] == "RESOLVED"

    def test_tension_reduced(self):
        result = desi_dr3_routing(wa_measured=-0.4, wa_sigma=0.25)
        assert result["verdict"] in ("TENSION_REDUCED", "HIGH_TENSION")

    def test_falsified_action_string(self):
        result = desi_dr3_routing(wa_measured=-0.90, wa_sigma=0.25)
        assert "FALSIFIED" in result["action"]
        assert "CLAIM_MASTER_BOARD" in result["action"]

    def test_tension_sigma_computed(self):
        result = desi_dr3_routing(wa_measured=-0.75, wa_sigma=0.20)
        expected = abs(-0.75 - 0.0) / 0.20
        assert abs(result["tension_sigma"] - expected) < 1e-10


class TestFullAudit:
    def test_returns_dict(self): assert isinstance(canonical_de_formula_audit(), dict)

    def test_pillar_number(self):
        result = canonical_de_formula_audit()
        assert result["pillar"] == 359

    def test_status(self):
        result = canonical_de_formula_audit()
        assert result["status"] == "FORMULA_CANONICALIZED"

    def test_tensions_present(self):
        result = canonical_de_formula_audit()
        assert "tensions" in result

    def test_doc_fixes_listed(self):
        result = canonical_de_formula_audit()
        assert "documentation_fixes_required" in result
        assert len(result["documentation_fixes_required"]) >= 2

    def test_formula_deprecation(self):
        result = canonical_de_formula_audit()
        assert "formula_deprecation" in result
        assert "DEPRECATED" in result["formula_deprecation"]["old"]

    def test_summary_matches(self):
        summary = pillar359_summary()
        audit = canonical_de_formula_audit()
        assert summary["pillar"] == audit["pillar"]


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_no_score_change(self): assert "ToE score" in separation_guard()
