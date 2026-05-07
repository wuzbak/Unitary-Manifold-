# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for WS-E: src/core/open_parameters_p26_p27_certification.py"""

from __future__ import annotations

import pytest

from src.core.open_parameters_p26_p27_certification import (
    N_W, K_CS, PI_KR,
    THETA_QCD_PDG_BOUND,
    LAMBDA_CC_DIMENSIONLESS_OBS,
    M_KK_MEV, F_BRAID, RHO_KK_MEV4, RHO_OBS_MEV4, LAMBDA_CC_RESIDUAL_ORDERS,
    P26_STATUS, P27_STATUS,
    p26_definition,
    p27_definition,
    p26_derivation_attempt,
    p27_derivation_attempt,
    p26_certification,
    p27_certification,
    wse_gate_report,
    pillar_wse_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_theta_qcd_bound(self):
        assert THETA_QCD_PDG_BOUND == pytest.approx(1e-10)

    def test_lambda_cc_obs_small(self):
        assert LAMBDA_CC_DIMENSIONLESS_OBS < 1e-100

    def test_f_braid(self):
        assert F_BRAID == pytest.approx(5.0 / 74.0)

    def test_rho_kk_positive(self):
        assert RHO_KK_MEV4 > 0.0

    def test_rho_obs_positive(self):
        assert RHO_OBS_MEV4 > 0.0

    def test_residual_orders_positive(self):
        assert LAMBDA_CC_RESIDUAL_ORDERS > 0.0

    def test_p26_status_contains_architecture(self):
        assert "ARCHITECTURE_LIMIT" in P26_STATUS

    def test_p27_status_contains_estimate(self):
        assert "ESTIMATE" in P27_STATUS or "GEOMETRIC" in P27_STATUS


class TestP26Definition:
    def test_returns_dict(self):
        assert isinstance(p26_definition(), dict)

    def test_parameter_id(self):
        r = p26_definition()
        assert r["parameter_id"] == "P26"

    def test_name_is_theta_qcd(self):
        r = p26_definition()
        assert "θ_QCD" in r["name"] or "theta_QCD" in r["name"].lower()

    def test_pdg_bound_correct(self):
        r = p26_definition()
        assert r["pdg_bound"] == pytest.approx(1e-10)

    def test_table_placement_nonempty(self):
        r = p26_definition()
        assert len(r["table_placement"]) > 5


class TestP27Definition:
    def test_returns_dict(self):
        assert isinstance(p27_definition(), dict)

    def test_parameter_id(self):
        r = p27_definition()
        assert r["parameter_id"] == "P27"

    def test_name_contains_cc(self):
        r = p27_definition()
        assert "CC" in r["name"] or "cc" in r["name"].lower() or "Λ" in r["name"]

    def test_dimensionless_value(self):
        r = p27_definition()
        assert r["dimensionless_value"] < 1e-100


class TestP26DerivationAttempt:
    def test_returns_dict(self):
        assert isinstance(p26_derivation_attempt(), dict)

    def test_two_routes(self):
        r = p26_derivation_attempt()
        assert len(r["routes"]) == 2

    def test_route_b_is_architecture_limit(self):
        r = p26_derivation_attempt()
        route_b = next(x for x in r["routes"] if x["id"] == "B")
        assert "ARCHITECTURE_LIMIT" in route_b["status"]

    def test_has_falsifiable_condition(self):
        r = p26_derivation_attempt()
        assert len(r["falsifiable_condition"]) > 10

    def test_has_no_go(self):
        r = p26_derivation_attempt()
        assert len(r["no_go"]) > 10


class TestP27DerivationAttempt:
    def test_returns_dict(self):
        assert isinstance(p27_derivation_attempt(), dict)

    def test_two_routes(self):
        r = p27_derivation_attempt()
        assert len(r["routes"]) == 2

    def test_route_a_is_geometric_estimate(self):
        r = p27_derivation_attempt()
        route_a = next(x for x in r["routes"] if x["id"] == "A")
        assert "ESTIMATE" in route_a["status"]

    def test_route_b_not_a_prediction(self):
        r = p27_derivation_attempt()
        route_b = next(x for x in r["routes"] if x["id"] == "B")
        assert "NOT" in route_b["status"]


class TestP26Certification:
    def test_returns_dict(self):
        assert isinstance(p26_certification(), dict)

    def test_status_is_architecture_limit(self):
        r = p26_certification()
        assert "ARCHITECTURE_LIMIT" in r["status"]

    def test_cert_type(self):
        r = p26_certification()
        assert r["certification_type"] == "ARCHITECTURE_LIMIT"

    def test_gate_passed_for_cert(self):
        r = p26_certification()
        assert r["gate_passed"] is True   # cert delivered

    def test_partial_derivation_exists(self):
        r = p26_certification()
        assert r["partial_derivation_exists"] is True


class TestP27Certification:
    def test_returns_dict(self):
        assert isinstance(p27_certification(), dict)

    def test_status_is_geometric_estimate(self):
        r = p27_certification()
        assert "GEOMETRIC ESTIMATE" in r["status"] or "ESTIMATE" in r["status"]

    def test_kk_energy_positive(self):
        r = p27_certification()
        assert r["kk_vacuum_energy_mev4"] > 0.0

    def test_gate_passed_for_cert(self):
        r = p27_certification()
        assert r["gate_passed"] is True


class TestWseGateReport:
    def test_returns_dict(self):
        assert isinstance(wse_gate_report(), dict)

    def test_workstream(self):
        assert wse_gate_report()["workstream"] == "WS-E"

    def test_gate_passed(self):
        assert wse_gate_report()["gate_passed"] is True

    def test_has_all_deliverables(self):
        r = wse_gate_report()
        assert "deliverable_E1_definitions" in r
        assert "deliverable_E2_derivation_attempts" in r
        assert "deliverable_E3_certification" in r

    def test_status_change_includes_p26_p27(self):
        r = wse_gate_report()
        assert "P26" in str(r["status_change"])
        assert "P27" in str(r["status_change"])

    def test_sm_table_complete(self):
        r = wse_gate_report()
        assert r["what_is_newly_achieved"][-1].count("P1–P28") > 0 or \
               any("complete" in s.lower() for s in r["what_is_newly_achieved"])


class TestPillarWseSummary:
    def test_returns_dict(self):
        assert isinstance(pillar_wse_summary(), dict)

    def test_gate_passed(self):
        r = pillar_wse_summary()
        assert r["gate_passed"] is True

    def test_sm_table_complete(self):
        r = pillar_wse_summary()
        assert r["sm_table_complete"] is True
