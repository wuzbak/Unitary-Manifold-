# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 349 — r vs ACT DR6 Bayesian Routing Package."""
import math
import pytest
from src.core.pillar349_act_dr6_r_routing import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE,
    R_BRAIDED_LO, R_BRAIDED_NLO, R_BRAIDED_NNLO,
    R_ACT_DR6_LIMIT, R_ACT_DR6_CENTRAL, R_ACT_SIGMA,
    DELTA_LOOP_NLO, DELTA_LOOP_NNLO, C_S, RHO_WZW,
    r_braided_loop_budget, bayesian_posterior_r, bayesian_tension_sigma,
    so_routing, cmbs4_routing, litebird_routing, r_routing_protocol,
    act_dr6_certificate, separation_guard,
)


# ── Identity ─────────────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 349


def test_constants():
    assert C_S == pytest.approx(12 / 37, rel=1e-10)
    assert R_BRAIDED_LO == pytest.approx(0.0315, rel=1e-10)
    assert R_ACT_DR6_LIMIT == 0.016


def test_nlo_less_than_lo():
    assert R_BRAIDED_NLO < R_BRAIDED_LO


def test_nnlo_less_than_nlo():
    assert R_BRAIDED_NNLO < R_BRAIDED_NLO


def test_loop_corrections_small():
    assert DELTA_LOOP_NLO < 0.01   # < 1%
    assert DELTA_LOOP_NNLO < 1e-4  # < 0.01% (NLO² ~ 3e-5)


# ── Loop Budget ─────────────────────────────────────────────────────────────────

def test_loop_budget_convergent():
    result = r_braided_loop_budget()
    assert result["series_type"] == "RAPIDLY_CONVERGENT"
    orders = result["loop_orders"]
    r_vals = [o["r"] for o in orders]
    # Should be monotonically decreasing
    for i in range(len(r_vals) - 1):
        assert r_vals[i] >= r_vals[i + 1]


def test_loop_budget_irreducible():
    result = r_braided_loop_budget()
    assert result["irreducible"]   # r > 0.016 at all orders
    assert not result["below_act_limit"]


def test_loop_budget_lo():
    result = r_braided_loop_budget()
    assert result["loop_orders"][0]["r"] == pytest.approx(R_BRAIDED_LO)


def test_loop_budget_nlo():
    result = r_braided_loop_budget()
    assert result["loop_orders"][1]["r"] == pytest.approx(R_BRAIDED_NLO, rel=1e-6)


def test_loop_budget_5loops():
    result = r_braided_loop_budget(n_loops=5)
    assert len(result["loop_orders"]) == 6   # 0 through 5
    # Converged value still above ACT limit
    assert result["r_converged"] > R_ACT_DR6_LIMIT


# ── Bayesian Posterior ────────────────────────────────────────────────────────────

def test_bayesian_posterior_positive():
    result = bayesian_posterior_r()
    assert 0 < result["posterior_weight"] < 1


def test_bayesian_posterior_z_score():
    result = bayesian_posterior_r()
    # z = (r_NLO - 0) / sigma_ACT
    expected_z = (R_BRAIDED_NLO - R_ACT_DR6_CENTRAL) / R_ACT_SIGMA
    assert result["z_score"] == pytest.approx(expected_z, rel=1e-6)


def test_bayesian_posterior_at_act_central_is_max():
    # At r = 0 (ACT central), posterior should be maximum (= 1)
    result = bayesian_posterior_r(r_um=0.0)
    assert result["posterior_weight"] == pytest.approx(1.0)


def test_bayesian_posterior_high_tension():
    result = bayesian_posterior_r()
    # r_NLO ≈ 0.0313 vs ACT sigma ≈ 0.008: ~3.9σ
    assert result["gaussian_sigma_tension"] > 2.0


# ── Tension Sigma ────────────────────────────────────────────────────────────────

def test_tension_sigma_positive():
    tension = bayesian_tension_sigma()
    assert tension > 0


def test_tension_sigma_calculation():
    tension = bayesian_tension_sigma()
    expected = (R_BRAIDED_NLO - R_ACT_DR6_LIMIT) / R_ACT_SIGMA
    assert tension == pytest.approx(expected, rel=1e-6)


# ── SO Routing ──────────────────────────────────────────────────────────────────

def test_so_routing_template():
    result = so_routing()
    assert "instrument" in result
    assert "Simons Observatory" in result["instrument"]
    assert result["preregistered"]


def test_so_routing_consistent():
    # If SO measures r ≈ 0.03 (near UM prediction): CONSISTENT
    result = so_routing(r_so=0.03, sigma_r_so=0.003)
    assert result["verdict"] in ("CONSISTENT", "POSSIBLE_CONFIRMATION")


def test_so_routing_falsified():
    # If SO measures r = 0.005 with σ=0.003: tension ≈ (0.0313-0.005)/0.003 ≈ 8.8σ → FALSIFIED
    result = so_routing(r_so=0.005, sigma_r_so=0.003)
    assert result["verdict"] == "FALSIFIED__EXECUTE_PROTOCOL"


# ── CMB-S4 Routing ──────────────────────────────────────────────────────────────

def test_cmbs4_routing_template():
    result = cmbs4_routing()
    assert result["preregistered"]
    assert "CMB-S4" in result["instrument"]


def test_cmbs4_routing_confirmed():
    result = cmbs4_routing(r_s4=R_BRAIDED_NLO * 0.99)
    assert result["verdict"] == "CONFIRMED"


def test_cmbs4_routing_falsified():
    result = cmbs4_routing(r_s4=0.005, sigma_r_s4=0.001)
    # tension = (0.0313 - 0.005) / 0.001 ≈ 26σ → FALSIFIED
    assert result["verdict"] == "FALSIFIED__FRAMEWORK_REVISION"


# ── LiteBIRD Routing ─────────────────────────────────────────────────────────────

def test_litebird_routing_template():
    result = litebird_routing()
    assert result["preregistered"]
    assert "LiteBIRD" in result["instrument"]
    assert "joint_protocol" in result


def test_litebird_routing_confirmed():
    result = litebird_routing(r_lb=R_BRAIDED_NLO * 1.01)
    assert result["verdict"] == "FRAMEWORK_CONFIRMED"


# ── Master Routing Protocol ──────────────────────────────────────────────────────

def test_r_routing_protocol():
    result = r_routing_protocol()
    assert result["current_status"] == "HIGH_TENSION__NOT_FALSIFIED"
    assert result["irreducible_certified"]
    assert result["r_um_lo"] == R_BRAIDED_LO
    assert result["r_um_nlo"] == R_BRAIDED_NLO
    assert result["r_act_dr6_limit"] == R_ACT_DR6_LIMIT


def test_r_routing_loop_budget_present():
    result = r_routing_protocol()
    assert "loop_budget" in result
    assert result["loop_budget"]["irreducible"]


def test_r_routing_schedule():
    result = r_routing_protocol()
    assert "SO_Year5_2028" in result["routing_schedule"]
    assert "CMB-S4_2030" in result["routing_schedule"]
    assert "LiteBIRD_2032" in result["routing_schedule"]


# ── ACT DR6 Certificate ──────────────────────────────────────────────────────────

def test_act_dr6_certificate():
    cert = act_dr6_certificate()
    assert cert["pillar"] == 349
    assert "HIGH_TENSION" in cert["status"]
    assert "IRREDUCIBLE" in cert["status"]
    assert "NOT_FALSIFIED" in cert["status"]
    assert cert["irreducible_at_all_loops"]


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "349" in guard
