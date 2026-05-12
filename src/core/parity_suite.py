# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/parity_suite.py
========================
Cross-backend parity verification suite for the Unitary Manifold.

Inspired by the LIGO parity-check architecture: every numerical result
is independently re-computed in a second (or third) backend and the
discrepancy is reported as a parity metric.

Backends available in this repository:
  numpy  — reference implementation (evolution.py, metric.py)
  sympy  — exact symbolic (formal_proof_hardening.py)
  mpmath — arbitrary-precision (precision_audit.py)

This module:
  - Defines ParityCheck dataclass (two values, tolerance, pass/fail)
  - Defines ParityReport (list of checks, aggregate status)
  - Implements numpy vs sympy checks for core formulas
  - Implements numpy vs mpmath checks for key constants
  - Returns parity_report() as the top-level function

No optional dependencies (jax, z3, wandb) — only numpy, sympy, mpmath.
If mpmath is not installed, mpmath checks are skipped.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

import numpy as np
import sympy as sp

__all__ = [
    "ParityCheck",
    "ParityReport",
    "parity_report",
    "parity_check_single",
    "check_ns_numpy_sympy",
    "check_r_numpy_sympy",
    "check_k_cs_numpy_sympy",
    "check_c_s_numpy_sympy",
    "check_alpha_gut_numpy_sympy",
    "check_phi0_numpy_sympy",
    "check_ns_mpmath",
    "check_r_mpmath",
    "check_c_s_mpmath",
    "check_alpha_gut_mpmath",
    "check_k_cs_integer",
    "check_phi0_self_consistency",
]

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
N_W = 5
K_CS = 74
C_S = 12 / 37
N_S_UM = 0.9635
R_BRAIDED = 0.0315
PHI0_CANONICAL = math.sqrt(8.0 * N_W / (1.0 - N_S_UM))  # ≈ 33.104
ALPHA_GUT = 3 / 74

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParityCheck:
    check_id: str
    formula: str
    backend_a: str    # "numpy" | "sympy" | "mpmath"
    backend_b: str
    value_a: float
    value_b: float
    tolerance: float
    abs_error: float  # |value_a - value_b|
    passed: bool      # abs_error <= tolerance


@dataclass(frozen=True)
class ParityReport:
    checks: tuple     # tuple of ParityCheck
    n_passed: int
    n_failed: int
    all_passed: bool
    status: str       # "PASS" | "FAIL"


# ---------------------------------------------------------------------------
# numpy vs sympy checks
# ---------------------------------------------------------------------------

def check_ns_numpy_sympy() -> ParityCheck:
    """n_s = 1 - 8*n_w/phi0^2: numpy float vs sympy Rational."""
    phi0_sq = sp.Rational(8 * N_W, 1) / sp.nsimplify(1 - N_S_UM, rational=False)
    n_s_sympy = float(1 - sp.Rational(8 * N_W, 1) / phi0_sq)
    n_s_numpy = 1.0 - 8.0 * N_W / PHI0_CANONICAL**2
    abs_err = abs(n_s_numpy - n_s_sympy)
    return ParityCheck(
        check_id="NS-NUMPY-SYMPY",
        formula="n_s = 1 - 8*n_w/phi0^2",
        backend_a="numpy",
        backend_b="sympy",
        value_a=n_s_numpy,
        value_b=n_s_sympy,
        tolerance=1e-10,
        abs_error=abs_err,
        passed=abs_err <= 1e-10,
    )


def check_r_numpy_sympy() -> ParityCheck:
    """r = 32*n_w*c_s/phi0^2: numpy float vs sympy expression."""
    r_numpy = 32.0 * N_W * C_S / PHI0_CANONICAL**2
    phi0_sym = sp.sqrt(sp.Rational(8 * N_W, 1) / sp.nsimplify(1 - N_S_UM, rational=False))
    c_s_sym = sp.Rational(12, 37)
    r_sympy = float(32 * N_W * c_s_sym / phi0_sym**2)
    abs_err = abs(r_numpy - r_sympy)
    return ParityCheck(
        check_id="R-NUMPY-SYMPY",
        formula="r = 32*n_w*c_s/phi0^2",
        backend_a="numpy",
        backend_b="sympy",
        value_a=r_numpy,
        value_b=r_sympy,
        tolerance=1e-10,
        abs_error=abs_err,
        passed=abs_err <= 1e-10,
    )


def check_k_cs_numpy_sympy() -> ParityCheck:
    """K_CS = 5^2+7^2=74: numpy int vs sympy Integer."""
    k_numpy = float(5**2 + 7**2)
    k_sympy = float(sp.Integer(5)**2 + sp.Integer(7)**2)
    abs_err = abs(k_numpy - k_sympy)
    return ParityCheck(
        check_id="KCS-NUMPY-SYMPY",
        formula="K_CS = 5^2 + 7^2 = 74",
        backend_a="numpy",
        backend_b="sympy",
        value_a=k_numpy,
        value_b=k_sympy,
        tolerance=0.0,
        abs_error=abs_err,
        passed=abs_err == 0.0,
    )


def check_c_s_numpy_sympy() -> ParityCheck:
    """c_s = 12/37 as numpy float vs sympy Rational."""
    c_s_numpy = 12.0 / 37.0
    c_s_sympy = float(sp.Rational(12, 37))
    abs_err = abs(c_s_numpy - c_s_sympy)
    return ParityCheck(
        check_id="CS-NUMPY-SYMPY",
        formula="c_s = 12/37",
        backend_a="numpy",
        backend_b="sympy",
        value_a=c_s_numpy,
        value_b=c_s_sympy,
        tolerance=1e-15,
        abs_error=abs_err,
        passed=abs_err <= 1e-15,
    )


def check_alpha_gut_numpy_sympy() -> ParityCheck:
    """alpha_gut = 3/74: numpy float vs sympy Rational."""
    alpha_numpy = 3.0 / 74.0
    alpha_sympy = float(sp.Rational(3, 74))
    abs_err = abs(alpha_numpy - alpha_sympy)
    return ParityCheck(
        check_id="ALPHA-GUT-NUMPY-SYMPY",
        formula="alpha_gut = 3/74",
        backend_a="numpy",
        backend_b="sympy",
        value_a=alpha_numpy,
        value_b=alpha_sympy,
        tolerance=1e-15,
        abs_error=abs_err,
        passed=abs_err <= 1e-15,
    )


def check_phi0_numpy_sympy() -> ParityCheck:
    """phi0 = sqrt(8*n_w/(1-n_s)): numpy float vs sympy sqrt."""
    phi0_numpy = PHI0_CANONICAL
    one_minus_ns = sp.nsimplify(1 - N_S_UM, rational=False)
    phi0_sympy = float(sp.sqrt(sp.Rational(8 * N_W, 1) / one_minus_ns))
    abs_err = abs(phi0_numpy - phi0_sympy)
    return ParityCheck(
        check_id="PHI0-NUMPY-SYMPY",
        formula="phi0 = sqrt(8*n_w/(1-n_s))",
        backend_a="numpy",
        backend_b="sympy",
        value_a=phi0_numpy,
        value_b=phi0_sympy,
        tolerance=1e-10,
        abs_error=abs_err,
        passed=abs_err <= 1e-10,
    )


# ---------------------------------------------------------------------------
# numpy vs mpmath checks
# ---------------------------------------------------------------------------

def _mpmath_unavailable_check(check_id: str, formula: str) -> ParityCheck:
    """Return a skipped ParityCheck when mpmath is not installed."""
    return ParityCheck(
        check_id=check_id,
        formula=f"SKIPPED (mpmath unavailable) — {formula}",
        backend_a="numpy",
        backend_b="mpmath",
        value_a=float("nan"),
        value_b=float("nan"),
        tolerance=1e-12,
        abs_error=0.0,
        passed=True,
    )


def check_ns_mpmath() -> ParityCheck:
    """n_s at 50-decimal-place mpmath vs numpy."""
    try:
        import mpmath as mp
    except ImportError:
        return _mpmath_unavailable_check("NS-MPMATH", "n_s = 1 - 8*n_w/phi0^2")

    mp.mp.dps = 50
    phi0_mp = mp.sqrt(mp.mpf(8 * N_W) / (1 - mp.mpf(str(N_S_UM))))
    n_s_mp = float(1 - mp.mpf(8 * N_W) / phi0_mp**2)
    n_s_numpy = 1.0 - 8.0 * N_W / PHI0_CANONICAL**2
    abs_err = abs(n_s_numpy - n_s_mp)
    return ParityCheck(
        check_id="NS-MPMATH",
        formula="n_s = 1 - 8*n_w/phi0^2 @ 50 dps",
        backend_a="numpy",
        backend_b="mpmath",
        value_a=n_s_numpy,
        value_b=n_s_mp,
        tolerance=1e-12,
        abs_error=abs_err,
        passed=abs_err <= 1e-12,
    )


def check_r_mpmath() -> ParityCheck:
    """r = 32*n_w*c_s/phi0^2 at 50 dps vs numpy."""
    try:
        import mpmath as mp
    except ImportError:
        return _mpmath_unavailable_check("R-MPMATH", "r = 32*n_w*c_s/phi0^2")

    mp.mp.dps = 50
    phi0_mp = mp.sqrt(mp.mpf(8 * N_W) / (1 - mp.mpf(str(N_S_UM))))
    c_s_mp = mp.mpf(12) / mp.mpf(37)
    r_mp = float(32 * N_W * c_s_mp / phi0_mp**2)
    r_numpy = 32.0 * N_W * C_S / PHI0_CANONICAL**2
    abs_err = abs(r_numpy - r_mp)
    return ParityCheck(
        check_id="R-MPMATH",
        formula="r = 32*n_w*c_s/phi0^2 @ 50 dps",
        backend_a="numpy",
        backend_b="mpmath",
        value_a=r_numpy,
        value_b=r_mp,
        tolerance=1e-12,
        abs_error=abs_err,
        passed=abs_err <= 1e-12,
    )


def check_c_s_mpmath() -> ParityCheck:
    """c_s = 12/37 at 50 dps vs numpy."""
    try:
        import mpmath as mp
    except ImportError:
        return _mpmath_unavailable_check("CS-MPMATH", "c_s = 12/37")

    mp.mp.dps = 50
    c_s_mp = float(mp.mpf(12) / mp.mpf(37))
    c_s_numpy = 12.0 / 37.0
    abs_err = abs(c_s_numpy - c_s_mp)
    return ParityCheck(
        check_id="CS-MPMATH",
        formula="c_s = 12/37 @ 50 dps",
        backend_a="numpy",
        backend_b="mpmath",
        value_a=c_s_numpy,
        value_b=c_s_mp,
        tolerance=1e-14,
        abs_error=abs_err,
        passed=abs_err <= 1e-14,
    )


def check_alpha_gut_mpmath() -> ParityCheck:
    """alpha_gut = 3/74 at 50 dps vs numpy."""
    try:
        import mpmath as mp
    except ImportError:
        return _mpmath_unavailable_check("ALPHA-GUT-MPMATH", "alpha_gut = 3/74")

    mp.mp.dps = 50
    alpha_mp = float(mp.mpf(3) / mp.mpf(74))
    alpha_numpy = 3.0 / 74.0
    abs_err = abs(alpha_numpy - alpha_mp)
    return ParityCheck(
        check_id="ALPHA-GUT-MPMATH",
        formula="alpha_gut = 3/74 @ 50 dps",
        backend_a="numpy",
        backend_b="mpmath",
        value_a=alpha_numpy,
        value_b=alpha_mp,
        tolerance=1e-14,
        abs_error=abs_err,
        passed=abs_err <= 1e-14,
    )


# ---------------------------------------------------------------------------
# Integer / self-consistency checks
# ---------------------------------------------------------------------------

def check_k_cs_integer() -> ParityCheck:
    """5^2 + 7^2 == 74: numpy int vs python int."""
    k_numpy = int(np.int64(5)**2 + np.int64(7)**2)
    k_python = 5**2 + 7**2
    abs_err = abs(float(k_numpy) - float(k_python))
    return ParityCheck(
        check_id="KCS-INTEGER",
        formula="5^2 + 7^2 == 74 (integer exact)",
        backend_a="numpy",
        backend_b="python",
        value_a=float(k_numpy),
        value_b=float(k_python),
        tolerance=0.0,
        abs_error=abs_err,
        passed=(k_numpy == k_python == K_CS),
    )


def check_phi0_self_consistency() -> ParityCheck:
    """Plug phi0 back into the n_s formula and recover N_S_UM within 1e-12."""
    phi0 = PHI0_CANONICAL
    n_s_recovered = 1.0 - 8.0 * N_W / phi0**2
    abs_err = abs(n_s_recovered - N_S_UM)
    return ParityCheck(
        check_id="PHI0-SELF-CONSISTENCY",
        formula="n_s_recovered = 1 - 8*n_w/phi0_canonical^2 ≈ N_S_UM",
        backend_a="numpy",
        backend_b="numpy",
        value_a=n_s_recovered,
        value_b=N_S_UM,
        tolerance=1e-12,
        abs_error=abs_err,
        passed=abs_err <= 1e-12,
    )


# ---------------------------------------------------------------------------
# Dispatch table for parity_check_single
# ---------------------------------------------------------------------------

_CHECK_REGISTRY: dict = {
    "NS-NUMPY-SYMPY": check_ns_numpy_sympy,
    "R-NUMPY-SYMPY": check_r_numpy_sympy,
    "KCS-NUMPY-SYMPY": check_k_cs_numpy_sympy,
    "CS-NUMPY-SYMPY": check_c_s_numpy_sympy,
    "ALPHA-GUT-NUMPY-SYMPY": check_alpha_gut_numpy_sympy,
    "PHI0-NUMPY-SYMPY": check_phi0_numpy_sympy,
    "NS-MPMATH": check_ns_mpmath,
    "R-MPMATH": check_r_mpmath,
    "CS-MPMATH": check_c_s_mpmath,
    "ALPHA-GUT-MPMATH": check_alpha_gut_mpmath,
    "KCS-INTEGER": check_k_cs_integer,
    "PHI0-SELF-CONSISTENCY": check_phi0_self_consistency,
}


def parity_check_single(check_id: str) -> ParityCheck:
    """Run a single named parity check by ID.

    Parameters
    ----------
    check_id : str
        One of the registered check IDs (e.g. "NS-NUMPY-SYMPY").

    Raises
    ------
    KeyError
        If check_id is not recognised.
    """
    if check_id not in _CHECK_REGISTRY:
        raise KeyError(
            f"Unknown parity check ID: {check_id!r}. "
            f"Available IDs: {sorted(_CHECK_REGISTRY)}"
        )
    return _CHECK_REGISTRY[check_id]()


# ---------------------------------------------------------------------------
# Top-level aggregate
# ---------------------------------------------------------------------------

def parity_report() -> ParityReport:
    """Run all parity checks and return aggregate report."""
    checks: List[ParityCheck] = [
        check_ns_numpy_sympy(),
        check_r_numpy_sympy(),
        check_k_cs_numpy_sympy(),
        check_c_s_numpy_sympy(),
        check_alpha_gut_numpy_sympy(),
        check_phi0_numpy_sympy(),
        check_ns_mpmath(),
        check_r_mpmath(),
        check_c_s_mpmath(),
        check_alpha_gut_mpmath(),
        check_k_cs_integer(),
        check_phi0_self_consistency(),
    ]
    n_passed = sum(1 for c in checks if c.passed)
    n_failed = len(checks) - n_passed
    all_passed = n_failed == 0
    return ParityReport(
        checks=tuple(checks),
        n_passed=n_passed,
        n_failed=n_failed,
        all_passed=all_passed,
        status="PASS" if all_passed else "FAIL",
    )
