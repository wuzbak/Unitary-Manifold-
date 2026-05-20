# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_parity_suite.py
==========================
~40 tests for src/core/parity_suite.py — cross-backend parity verification.
"""

from __future__ import annotations

import math

import pytest

pytest.importorskip("sympy", reason="sympy not installed — skip SymPy-dependent tests")

from src.core.parity_suite import (
    ALPHA_GUT,
    C_S,
    K_CS,
    N_S_UM,
    N_W,
    PHI0_CANONICAL,
    R_BRAIDED,
    ParityCheck,
    ParityReport,
    check_alpha_gut_mpmath,
    check_alpha_gut_numpy_sympy,
    check_c_s_mpmath,
    check_c_s_numpy_sympy,
    check_k_cs_integer,
    check_k_cs_numpy_sympy,
    check_ns_mpmath,
    check_ns_numpy_sympy,
    check_phi0_numpy_sympy,
    check_phi0_self_consistency,
    check_r_mpmath,
    check_r_numpy_sympy,
    parity_check_single,
    parity_report,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s_value(self):
        assert abs(C_S - 12 / 37) < 1e-15

    def test_n_s_um(self):
        assert abs(N_S_UM - 0.9635) < 1e-15

    def test_r_braided(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-15

    def test_phi0_canonical(self):
        expected = math.sqrt(8.0 * 5 / (1.0 - 0.9635))
        assert abs(PHI0_CANONICAL - expected) < 1e-10

    def test_alpha_gut(self):
        assert abs(ALPHA_GUT - 3 / 74) < 1e-15


# ---------------------------------------------------------------------------
# ParityCheck dataclass
# ---------------------------------------------------------------------------

class TestParityCheckDataclass:
    def setup_method(self):
        self.check = check_ns_numpy_sympy()

    def test_has_check_id(self):
        assert hasattr(self.check, "check_id")

    def test_has_formula(self):
        assert hasattr(self.check, "formula")

    def test_has_backend_a(self):
        assert hasattr(self.check, "backend_a")

    def test_has_backend_b(self):
        assert hasattr(self.check, "backend_b")

    def test_has_value_a(self):
        assert hasattr(self.check, "value_a")

    def test_has_value_b(self):
        assert hasattr(self.check, "value_b")

    def test_has_tolerance(self):
        assert hasattr(self.check, "tolerance")

    def test_has_abs_error(self):
        assert hasattr(self.check, "abs_error")

    def test_has_passed(self):
        assert hasattr(self.check, "passed")

    def test_frozen(self):
        with pytest.raises((TypeError, AttributeError)):
            self.check.passed = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Individual numpy vs sympy checks
# ---------------------------------------------------------------------------

class TestNumpySympy:
    def test_ns_returns_parity_check(self):
        assert isinstance(check_ns_numpy_sympy(), ParityCheck)

    def test_ns_passed(self):
        assert check_ns_numpy_sympy().passed is True

    def test_ns_check_id(self):
        assert check_ns_numpy_sympy().check_id == "NS-NUMPY-SYMPY"

    def test_ns_value_a_close_to_ns_um(self):
        assert abs(check_ns_numpy_sympy().value_a - N_S_UM) < 1e-8

    def test_ns_abs_error_non_negative(self):
        assert check_ns_numpy_sympy().abs_error >= 0.0

    def test_r_returns_parity_check(self):
        assert isinstance(check_r_numpy_sympy(), ParityCheck)

    def test_r_passed(self):
        assert check_r_numpy_sympy().passed is True

    def test_r_value_a_positive(self):
        assert check_r_numpy_sympy().value_a > 0.0

    def test_kcs_returns_parity_check(self):
        assert isinstance(check_k_cs_numpy_sympy(), ParityCheck)

    def test_kcs_passed(self):
        assert check_k_cs_numpy_sympy().passed is True

    def test_kcs_value_a(self):
        assert check_k_cs_numpy_sympy().value_a == 74.0

    def test_cs_returns_parity_check(self):
        assert isinstance(check_c_s_numpy_sympy(), ParityCheck)

    def test_cs_passed(self):
        assert check_c_s_numpy_sympy().passed is True

    def test_cs_abs_error_small(self):
        assert check_c_s_numpy_sympy().abs_error < 1e-14

    def test_alpha_gut_returns_parity_check(self):
        assert isinstance(check_alpha_gut_numpy_sympy(), ParityCheck)

    def test_alpha_gut_passed(self):
        assert check_alpha_gut_numpy_sympy().passed is True

    def test_phi0_returns_parity_check(self):
        assert isinstance(check_phi0_numpy_sympy(), ParityCheck)

    def test_phi0_passed(self):
        assert check_phi0_numpy_sympy().passed is True

    def test_phi0_value_a_close_to_canonical(self):
        assert abs(check_phi0_numpy_sympy().value_a - PHI0_CANONICAL) < 1e-10


# ---------------------------------------------------------------------------
# Integer / self-consistency checks
# ---------------------------------------------------------------------------

class TestIntegerAndSelfConsistency:
    def test_kcs_integer_returns_parity_check(self):
        assert isinstance(check_k_cs_integer(), ParityCheck)

    def test_kcs_integer_passed(self):
        assert check_k_cs_integer().passed is True

    def test_kcs_integer_exact_zero_error(self):
        assert check_k_cs_integer().abs_error == 0.0

    def test_phi0_self_consistency_returns_parity_check(self):
        assert isinstance(check_phi0_self_consistency(), ParityCheck)

    def test_phi0_self_consistency_passed(self):
        assert check_phi0_self_consistency().passed is True

    def test_phi0_self_consistency_value_a_close(self):
        chk = check_phi0_self_consistency()
        assert abs(chk.value_a - N_S_UM) < 1e-12


# ---------------------------------------------------------------------------
# mpmath checks (skip-aware)
# ---------------------------------------------------------------------------

class TestMpmath:
    def test_ns_mpmath_returns_parity_check(self):
        assert isinstance(check_ns_mpmath(), ParityCheck)

    def test_ns_mpmath_passed(self):
        assert check_ns_mpmath().passed is True

    def test_r_mpmath_returns_parity_check(self):
        assert isinstance(check_r_mpmath(), ParityCheck)

    def test_r_mpmath_passed(self):
        assert check_r_mpmath().passed is True

    def test_cs_mpmath_returns_parity_check(self):
        assert isinstance(check_c_s_mpmath(), ParityCheck)

    def test_cs_mpmath_passed(self):
        assert check_c_s_mpmath().passed is True

    def test_alpha_gut_mpmath_returns_parity_check(self):
        assert isinstance(check_alpha_gut_mpmath(), ParityCheck)

    def test_alpha_gut_mpmath_passed(self):
        assert check_alpha_gut_mpmath().passed is True

    def test_all_mpmath_checks_have_non_negative_abs_error(self):
        for chk in (check_ns_mpmath(), check_r_mpmath(), check_c_s_mpmath(), check_alpha_gut_mpmath()):
            assert chk.abs_error >= 0.0

    def test_all_mpmath_checks_have_positive_tolerance(self):
        for chk in (check_ns_mpmath(), check_r_mpmath(), check_c_s_mpmath(), check_alpha_gut_mpmath()):
            assert chk.tolerance > 0.0


# ---------------------------------------------------------------------------
# parity_report aggregate
# ---------------------------------------------------------------------------

class TestParityReport:
    def setup_method(self):
        self.report = parity_report()

    def test_returns_parity_report(self):
        assert isinstance(self.report, ParityReport)

    def test_status_pass(self):
        assert self.report.status == "PASS"

    def test_all_passed(self):
        assert self.report.all_passed is True

    def test_n_failed_zero(self):
        assert self.report.n_failed == 0

    def test_n_passed_ge_10(self):
        assert self.report.n_passed >= 10

    def test_checks_is_tuple(self):
        assert isinstance(self.report.checks, tuple)

    def test_checks_length_12(self):
        assert len(self.report.checks) == 12

    def test_all_checks_are_parity_check(self):
        for chk in self.report.checks:
            assert isinstance(chk, ParityCheck)

    def test_all_abs_errors_non_negative(self):
        for chk in self.report.checks:
            assert chk.abs_error >= 0.0

    def test_all_tolerances_non_negative(self):
        for chk in self.report.checks:
            assert chk.tolerance >= 0.0

    def test_n_passed_plus_n_failed_equals_total(self):
        assert self.report.n_passed + self.report.n_failed == len(self.report.checks)


# ---------------------------------------------------------------------------
# parity_check_single
# ---------------------------------------------------------------------------

class TestParityCheckSingle:
    def test_ns_numpy_sympy_by_id(self):
        chk = parity_check_single("NS-NUMPY-SYMPY")
        assert isinstance(chk, ParityCheck)
        assert chk.check_id == "NS-NUMPY-SYMPY"

    def test_kcs_numpy_sympy_by_id(self):
        chk = parity_check_single("KCS-NUMPY-SYMPY")
        assert chk.passed is True

    def test_phi0_self_consistency_by_id(self):
        chk = parity_check_single("PHI0-SELF-CONSISTENCY")
        assert chk.passed is True

    def test_invalid_id_raises_key_error(self):
        with pytest.raises(KeyError):
            parity_check_single("NONEXISTENT-CHECK")

    def test_all_registered_ids_callable(self):
        ids = [
            "NS-NUMPY-SYMPY",
            "R-NUMPY-SYMPY",
            "KCS-NUMPY-SYMPY",
            "CS-NUMPY-SYMPY",
            "ALPHA-GUT-NUMPY-SYMPY",
            "PHI0-NUMPY-SYMPY",
            "NS-MPMATH",
            "R-MPMATH",
            "CS-MPMATH",
            "ALPHA-GUT-MPMATH",
            "KCS-INTEGER",
            "PHI0-SELF-CONSISTENCY",
        ]
        for cid in ids:
            chk = parity_check_single(cid)
            assert isinstance(chk, ParityCheck)
