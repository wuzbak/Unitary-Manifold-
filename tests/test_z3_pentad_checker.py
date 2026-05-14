# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_z3_pentad_checker.py
====================================
Tests for src/core/z3_pentad_checker.py — Z3 SMT formal verification.
"""
import pytest
z3 = pytest.importorskip("z3")

from src.core.z3_pentad_checker import (
    check_trust_stability,
    check_no_deadlock,
    check_cs_bound,
    check_xi_c_rational,
    full_pentad_check,
    TRUST_PHI_MIN,
    CS_NUM, CS_DEN,
    XI_C_NUM, XI_C_DEN,
)


# ---------------------------------------------------------------------------
# Z3 availability
# ---------------------------------------------------------------------------

def test_z3_importable():
    assert hasattr(z3, "Solver")
    assert hasattr(z3, "Real")
    version = z3.get_version_string()
    assert isinstance(version, str)
    assert len(version) > 0


# ---------------------------------------------------------------------------
# check_trust_stability
# ---------------------------------------------------------------------------

def test_trust_stability_pass():
    result = check_trust_stability()
    assert result["status"] == "PASS"


def test_trust_stability_result_key():
    result = check_trust_stability()
    assert result["result"] in ("sat", "unsat", "unknown")


def test_trust_stability_has_model():
    result = check_trust_stability()
    assert "model" in result
    assert isinstance(result["model"], dict)


def test_trust_stability_sat():
    result = check_trust_stability()
    assert result["result"] == "sat"


# ---------------------------------------------------------------------------
# check_no_deadlock
# ---------------------------------------------------------------------------

def test_no_deadlock_pass():
    result = check_no_deadlock()
    assert result["status"] == "PASS"


def test_no_deadlock_flag():
    result = check_no_deadlock()
    assert result["deadlock_possible"] is False


def test_no_deadlock_unsat():
    result = check_no_deadlock()
    assert result["deadlock_possible"] is False


# ---------------------------------------------------------------------------
# check_cs_bound
# ---------------------------------------------------------------------------

def test_cs_bound_pass():
    result = check_cs_bound()
    assert result["status"] == "PASS"


def test_cs_bound_in_bounds():
    result = check_cs_bound()
    assert result["in_bounds"] is True


def test_z3_cs_exact_value():
    result = check_cs_bound()
    expected = CS_NUM / CS_DEN
    assert abs(result["cs_value"] - expected) < 1e-15


def test_cs_bound_value_range():
    result = check_cs_bound()
    cs = result["cs_value"]
    assert 0 < cs < 1


def test_cs_bound_numerics():
    assert CS_NUM == 12
    assert CS_DEN == 37


# ---------------------------------------------------------------------------
# check_xi_c_rational
# ---------------------------------------------------------------------------

def test_xi_c_rational_pass():
    result = check_xi_c_rational()
    assert result["status"] == "PASS"


def test_xi_c_below_half():
    result = check_xi_c_rational()
    assert result["below_half"] is True


def test_z3_xi_c_exact_value():
    result = check_xi_c_rational()
    expected = XI_C_NUM / XI_C_DEN
    assert abs(result["xi_c"] - expected) < 1e-15


def test_xi_c_value_range():
    result = check_xi_c_rational()
    assert result["xi_c"] < 0.5


def test_xi_c_numerics():
    assert XI_C_NUM == 35
    assert XI_C_DEN == 74


# ---------------------------------------------------------------------------
# full_pentad_check
# ---------------------------------------------------------------------------

def test_full_pentad_check_all_pass():
    result = full_pentad_check()
    assert result["all_pass"] is True


def test_full_pentad_check_keys():
    result = full_pentad_check()
    assert "trust_stability" in result
    assert "no_deadlock" in result
    assert "cs_bound" in result
    assert "xi_c_rational" in result
    assert "all_pass" in result


def test_full_pentad_check_sub_results():
    result = full_pentad_check()
    for key in ("trust_stability", "no_deadlock", "cs_bound", "xi_c_rational"):
        assert result[key]["status"] == "PASS"


def test_trust_phi_min_value():
    assert abs(TRUST_PHI_MIN - 0.1) < 1e-15
