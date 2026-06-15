# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar373_nonperturbative_braid_resummation.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar373_nonperturbative_braid_resummation import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    GAMMA_THEORY_ONE_LOOP, GAMMA_FIT, GAMMA_DISCREPANCY_FRACTION,
    K_CS, ALPHA_GUT, Z_PHI_0, C_S,
    separation_guard, instanton_expansion, tight_binding_lattice_model,
    pade_resummation, l2_closure_assessment,
    gamma_discrepancy_characterization, pillar373_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 373
    def test_status(self): assert PILLAR_STATUS == "L2_PARTIALLY_CLOSED"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_gamma_theory(self): assert abs(GAMMA_THEORY_ONE_LOOP - 0.242) < 0.001
    def test_gamma_fit(self): assert abs(GAMMA_FIT - 0.273) < 0.001
    def test_discrepancy_positive(self): assert GAMMA_DISCREPANCY_FRACTION > 0
    def test_k_cs(self): assert K_CS == 74
    def test_alpha_gut(self): assert abs(ALPHA_GUT - 3.0 / 74.0) < 1e-6
    def test_c_s(self): assert abs(C_S - 12.0 / 37.0) < 1e-6
    def test_discrepancy_fraction_range(self):
        assert 0.05 < GAMMA_DISCREPANCY_FRACTION < 0.25


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_l2_present(self): assert "L2" in separation_guard()


class TestInstantonExpansion:
    def test_returns_dict(self): assert isinstance(instanton_expansion(), dict)
    def test_instanton_action_large(self):
        r = instanton_expansion()
        assert r["instanton_action"] > 1000
    def test_instanton_weight_tiny(self):
        r = instanton_expansion()
        assert r["instanton_weight"] < 1e-100
    def test_gamma_inst_contribution_zero(self):
        r = instanton_expansion()
        assert r["gamma_inst_contribution"] < 1e-100
    def test_verdict_suppressed(self):
        r = instanton_expansion()
        assert "SUPPRESSED" in r["verdict"].upper()
    def test_k_cs_present(self):
        r = instanton_expansion()
        assert r["k_cs"] == K_CS
    def test_alpha_gut_present(self):
        r = instanton_expansion()
        assert abs(r["alpha_gut"] - ALPHA_GUT) < 1e-5


class TestTightBindingLatticeModel:
    def test_returns_dict(self): assert isinstance(tight_binding_lattice_model(), dict)
    def test_gamma_1d_negative(self):
        r = tight_binding_lattice_model()
        assert r["gamma_lattice_1d"] < 0
    def test_wrong_sign(self):
        r = tight_binding_lattice_model()
        assert r["sign_agreement"] is False
    def test_bandwidth_positive(self):
        r = tight_binding_lattice_model()
        assert r["bandwidth"] > 0
    def test_hopping_cs(self):
        r = tight_binding_lattice_model()
        assert abs(r["hopping_parameter"] - C_S) < 1e-5
    def test_verdict_wrong_sign(self):
        r = tight_binding_lattice_model()
        assert "WRONG" in r["verdict"].upper()
    def test_gamma_fit_target(self):
        r = tight_binding_lattice_model()
        assert abs(r["gamma_fit_target"] - GAMMA_FIT) < 0.001


class TestPadeResummation:
    def test_returns_dict(self): assert isinstance(pade_resummation(), dict)
    def test_required_coeff_large(self):
        r = pade_resummation()
        assert r["required_pade_coefficient_combo"] > 10
    def test_exceeds_weak_coupling(self):
        r = pade_resummation()
        assert r["exceeds_weak_coupling_expectation"] is True
    def test_delta_gamma_correct(self):
        r = pade_resummation()
        assert abs(r["delta_gamma"] - (GAMMA_FIT - GAMMA_THEORY_ONE_LOOP)) < 0.001
    def test_verdict_nonperturbative(self):
        r = pade_resummation()
        assert "non-perturbative" in r["verdict"].lower() or "NON-PERTURBATIVE" in r["verdict"]
    def test_custom_args(self):
        r = pade_resummation(0.24, 0.27, 0.001)
        assert isinstance(r, dict)


class TestL2ClosureAssessment:
    def test_returns_dict(self): assert isinstance(l2_closure_assessment(), dict)
    def test_pillar(self): assert l2_closure_assessment()["pillar"] == 373
    def test_l2_status(self): assert l2_closure_assessment()["l2_status"] == "L2_PARTIALLY_CLOSED"
    def test_three_approaches(self):
        r = l2_closure_assessment()
        assert len(r["approaches"]) == 3
    def test_each_approach_has_verdict(self):
        r = l2_closure_assessment()
        for a in r["approaches"]:
            assert "verdict" in a
    def test_remaining_candidates_present(self):
        r = l2_closure_assessment()
        assert len(r["remaining_candidates"]) >= 2
    def test_summary_present(self): assert "summary" in l2_closure_assessment()


class TestGammaDiscrepancyCharacterization:
    def test_returns_dict(self): assert isinstance(gamma_discrepancy_characterization(), dict)
    def test_two_loop_tiny(self):
        r = gamma_discrepancy_characterization()
        assert r["two_loop_correction"] < 1e-3
    def test_gamma_two_loop_close_to_one_loop(self):
        r = gamma_discrepancy_characterization()
        assert abs(r["gamma_two_loop"] - GAMMA_THEORY_ONE_LOOP) < 0.01
    def test_ruled_out_list(self):
        r = gamma_discrepancy_characterization()
        assert "ruled_out" in r
        assert len(r["ruled_out"]) >= 3
    def test_remaining_nonperturbative(self):
        r = gamma_discrepancy_characterization()
        assert "non-perturbative" in r["remaining"].lower()
    def test_status_l2(self):
        r = gamma_discrepancy_characterization()
        assert r["status"] == "L2_PARTIALLY_CLOSED"


class TestPillar373Summary:
    def test_pillar(self): assert pillar373_summary()["pillar"] == 373
    def test_status(self): assert pillar373_summary()["status"] == "L2_PARTIALLY_CLOSED"
    def test_gamma_theory(self): assert abs(pillar373_summary()["gamma_theory"] - 0.242) < 0.001
    def test_gamma_fit(self): assert abs(pillar373_summary()["gamma_fit"] - 0.273) < 0.001
    def test_instantons_suppressed(self): assert "SUPPRESSED" in pillar373_summary()["instantons"].upper()
    def test_pade_nonperturbative(self): assert "PERTURBATIVE" in pillar373_summary()["pade"].upper()
