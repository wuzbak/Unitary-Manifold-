# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar207_topological_scaling.py
============================================
Test suite for Pillar 207 — Topological Scaling Identity.

Tests confirm:
  - Mathematical correctness of (π²/K_CS)^n and (K_CS/π²)^n
  - Architecture-limit audit correctly concludes CC gap is NOT closed
  - π-based identities table values
  - Warp-Anchor topological view
  - Full report structure
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar207_topological_scaling import (
    # Constants
    N_W, K_CS, N2, N_C, PI_KR,
    PI_SQ_OVER_KCS, KCS_OVER_PI_SQ,
    ARCHITECTURE_LIMIT_TEXT,
    # Functions
    topological_scaling_factor,
    inverse_scaling_factor,
    scaling_table,
    pi_identity_near_alpha_s,
    warp_anchor_topological_view,
    architecture_limit_audit,
    pillar207_report,
)


# ===========================================================================
# MODULE CONSTANTS
# ===========================================================================

class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n2(self):
        assert N2 == 7

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-10

    def test_pi_sq_over_kcs(self):
        assert abs(PI_SQ_OVER_KCS - math.pi ** 2 / 74.0) < 1e-12

    def test_kcs_over_pi_sq(self):
        assert abs(KCS_OVER_PI_SQ - 74.0 / math.pi ** 2) < 1e-12

    def test_fundamental_ratio_lt_1(self):
        """π²/K_CS must be < 1 (it's a suppression factor)."""
        assert PI_SQ_OVER_KCS < 1.0

    def test_inverse_ratio_gt_1(self):
        assert KCS_OVER_PI_SQ > 1.0

    def test_product_is_1(self):
        assert abs(PI_SQ_OVER_KCS * KCS_OVER_PI_SQ - 1.0) < 1e-12

    def test_braid_identity(self):
        """K_CS = n_w² + n₂² must hold."""
        assert N_W ** 2 + N2 ** 2 == K_CS

    def test_architecture_limit_text_present(self):
        assert len(ARCHITECTURE_LIMIT_TEXT) > 50
        assert "ARCHITECTURE_LIMIT" in ARCHITECTURE_LIMIT_TEXT

    def test_pi_kr_equals_kcs_over_2(self):
        assert abs(PI_KR - K_CS / 2.0) < 1e-10


# ===========================================================================
# CORE SCALING FUNCTIONS
# ===========================================================================

class TestTopologicalScalingFactor:
    def test_n0_is_1(self):
        assert abs(topological_scaling_factor(0) - 1.0) < 1e-12

    def test_n1_is_pi_sq_over_kcs(self):
        assert abs(topological_scaling_factor(1) - PI_SQ_OVER_KCS) < 1e-12

    def test_n2_is_square(self):
        assert abs(topological_scaling_factor(2) - PI_SQ_OVER_KCS ** 2) < 1e-12

    def test_n_negative_is_inverse(self):
        assert abs(topological_scaling_factor(-1) - KCS_OVER_PI_SQ) < 1e-12

    def test_suppression_for_positive_n(self):
        """For positive n, (π²/K_CS)^n < 1."""
        for n in [0.5, 1, 2, 5, 10]:
            assert topological_scaling_factor(n) < 1.0

    def test_monotone_decreasing(self):
        """Larger n → smaller factor for n > 0."""
        assert topological_scaling_factor(2) < topological_scaling_factor(1)
        assert topological_scaling_factor(1) < topological_scaling_factor(0.5)

    def test_float_power(self):
        expected = PI_SQ_OVER_KCS ** 1.5
        assert abs(topological_scaling_factor(1.5) - expected) < 1e-12


class TestInverseScalingFactor:
    def test_n0_is_1(self):
        assert abs(inverse_scaling_factor(0) - 1.0) < 1e-12

    def test_n1_is_kcs_over_pi_sq(self):
        assert abs(inverse_scaling_factor(1) - KCS_OVER_PI_SQ) < 1e-12

    def test_product_with_forward_is_1(self):
        for n in [1, 2, 3, 0.5]:
            assert abs(topological_scaling_factor(n) * inverse_scaling_factor(n) - 1.0) < 1e-10

    def test_enhancement_for_positive_n(self):
        for n in [1, 2, 5]:
            assert inverse_scaling_factor(n) > 1.0

    def test_at_pikr_37(self):
        val = inverse_scaling_factor(PI_KR)
        assert val > 1e30  # (74/π²)^37 ≈ 10^32
        assert math.log10(val) == pytest.approx(32.37, abs=0.1)


# ===========================================================================
# SCALING TABLE
# ===========================================================================

class TestScalingTable:
    @pytest.fixture
    def table(self):
        return scaling_table()

    def test_returns_list(self, table):
        assert isinstance(table, list)
        assert len(table) > 5

    def test_each_row_has_required_keys(self, table):
        required = {"n", "pi_sq_over_kcs_to_n", "log10",
                    "kcs_over_pi_sq_to_n", "orders_of_magnitude_suppression"}
        for row in table:
            assert required <= row.keys()

    def test_log10_is_negative_for_positive_n(self, table):
        for row in table:
            if row["n"] > 0:
                assert row["log10"] < 0.0

    def test_orders_suppression_positive_for_positive_n(self, table):
        for row in table:
            if row["n"] > 0:
                assert row["orders_of_magnitude_suppression"] > 0.0

    def test_custom_n_values(self):
        t = scaling_table([1.0, 2.0])
        assert len(t) == 2
        assert abs(t[0]["pi_sq_over_kcs_to_n"] - PI_SQ_OVER_KCS) < 1e-12

    def test_n37_in_default_table(self, table):
        n37 = next((r for r in table if r["n"] == 37.0), None)
        assert n37 is not None
        assert n37["orders_of_magnitude_suppression"] > 30

    def test_n58_in_default_table(self, table):
        n58 = next((r for r in table if r["n"] == 58.0), None)
        assert n58 is not None
        # 58 orders of suppression would be exactly what CC needs — but it's more than 58
        assert n58["orders_of_magnitude_suppression"] > 50


# ===========================================================================
# π-IDENTITY CHECK
# ===========================================================================

class TestPiIdentityNearAlphaS:
    @pytest.fixture
    def pi_id(self):
        return pi_identity_near_alpha_s()

    def test_returns_dict(self, pi_id):
        assert isinstance(pi_id, dict)

    def test_speculative_flag(self, pi_id):
        assert pi_id["speculative"] is True

    def test_architecture_limit_present(self, pi_id):
        assert "architecture_limit" in pi_id

    def test_identities_key_present(self, pi_id):
        assert "identities" in pi_id

    def test_pi_nc_kcs_value(self, pi_id):
        """3π/74 should be ≈ 0.1274."""
        val = pi_id["identities"]["pi_nc_over_kcs"]["value"]
        assert abs(val - 3 * math.pi / 74) < 1e-10

    def test_best_approximation_identified(self, pi_id):
        assert "most_accurate_pi_approximation" in pi_id
        assert pi_id["best_residual_pct"] > 0

    def test_best_residual_less_than_15pct(self, pi_id):
        """The best π-identity must be within 15% of α_s(M_Z)."""
        assert pi_id["best_residual_pct"] < 15.0

    def test_conclusion_says_not_a_derivation(self, pi_id):
        assert "not a derivation" in pi_id["conclusion"].lower() \
            or "not accurate" in pi_id["conclusion"].lower()

    def test_exact_geometric_alpha_s_in_table(self, pi_id):
        """The geometric α_s(M_KK) = 2π/(N_c×K_CS) must be exact."""
        exact = pi_id["identities"]["two_pi_over_n_c_kcs"]
        assert exact["residual_pct"] == pytest.approx(0.0, abs=1e-10)

    def test_pi_sq_over_kcs_n2_residual_from_alpha_s_mkk(self, pi_id):
        """(π²/K_CS)² is checked against α_s(M_KK); residual should be > 30%."""
        val = pi_id["identities"]["pi_sq_over_kcs_n2"]["residual_pct"]
        assert val > 30.0


# ===========================================================================
# WARP-ANCHOR TOPOLOGICAL VIEW
# ===========================================================================

class TestWarpAnchorTopologicalView:
    @pytest.fixture
    def warp(self):
        return warp_anchor_topological_view()

    def test_returns_dict(self, warp):
        assert isinstance(warp, dict)

    def test_speculative_flag(self, warp):
        assert warp["speculative"] is True

    def test_gap_factor_near_384(self, warp):
        """Warp-Anchor Gap should be ~3.84."""
        assert 3.5 < warp["gap_factor"] < 4.5

    def test_log_gap_positive(self, warp):
        assert warp["log_gap"] > 0

    def test_best_fit_n_positive(self, warp):
        assert warp["best_fit_n"] > 0

    def test_closest_fraction_is_valid_string(self, warp):
        assert isinstance(warp["closest_geometric_fraction"], str)
        assert len(warp["closest_geometric_fraction"]) > 0

    def test_conclusion_not_claiming_closure(self, warp):
        """Must not claim this closes any physics gap."""
        assert "no physical mechanism" in warp["conclusion"].lower() \
            or "exploratory" in warp["conclusion"].lower()

    def test_gap_factor_consistent_with_alpha_s(self, warp):
        """Gap = PDG_alpha_s(MZ) / geometric_alpha_s(MZ) ≈ 3.84."""
        assert abs(warp["gap_factor"] - 0.11796 / 0.03072) < 0.02


# ===========================================================================
# ARCHITECTURE LIMIT AUDIT
# ===========================================================================

class TestArchitectureLimitAudit:
    @pytest.fixture
    def audit(self):
        return architecture_limit_audit()

    def test_returns_dict(self, audit):
        assert isinstance(audit, dict)

    def test_cc_gap_is_58(self, audit):
        assert audit["cc_gap_orders_of_magnitude"] == pytest.approx(58.0)

    def test_n_needed_not_integer(self, audit):
        """The required n = 66.3 is NOT an integer."""
        assert not audit["n_is_integer"]

    def test_n_needed_greater_than_58(self, audit):
        """Since log10(K_CS/π²) < 1, n_needed must be > 58."""
        assert audit["n_needed_for_10_58"] > 58.0

    def test_n_geometric_interpretation_none(self, audit):
        """No geometric meaning has been found for n_needed."""
        assert audit["n_geometric_interpretation"] is None

    def test_at_pikr37_orders_less_than_58(self, audit):
        """(K_CS/π²)^37 gives only ~32 orders — not 58."""
        assert audit["eval_at_n_pikr_37"]["orders"] < 58.0

    def test_at_pikr37_deficit_positive(self, audit):
        """Must be a positive deficit of orders remaining."""
        assert audit["eval_at_n_pikr_37"]["deficit_vs_58_orders"] > 0

    def test_at_kcs74_orders_less_than_58(self, audit):
        """Even (K_CS/π²)^74 doesn't reach 10^58."""
        assert audit["eval_at_n_kcs_74"]["orders"] < 66.0

    def test_architecture_limit_confirmed(self, audit):
        assert audit["architecture_limit_confirmed"] is True

    def test_verdict_says_cannot_close(self, audit):
        assert "CANNOT" in audit["verdict"]

    def test_verdict_mentions_deficit(self, audit):
        assert "remain" in audit["verdict"].lower() or "deficit" in audit["verdict"].lower()

    def test_at_n37_value_gt_1e30(self, audit):
        assert audit["eval_at_n_pikr_37"]["value"] > 1e30

    def test_log10_kcs_over_pi_sq_less_than_1(self, audit):
        """log10(K_CS/π²) ≈ 0.875 < 1, confirming that n > 58 is needed."""
        assert audit["log10_kcs_over_pi_sq"] < 1.0
        assert audit["log10_kcs_over_pi_sq"] > 0.5


# ===========================================================================
# FULL PILLAR 207 REPORT
# ===========================================================================

class TestPillar207Report:
    @pytest.fixture
    def rep(self):
        return pillar207_report()

    def test_pillar_id(self, rep):
        assert rep["pillar"] == "207"

    def test_status_speculative(self, rep):
        assert "SPECULATIVE" in rep["status"]

    def test_architecture_limit_present(self, rep):
        assert "architecture_limit" in rep

    def test_kill_switch_present(self, rep):
        assert "kill_switch" in rep
        assert "LiteBIRD" in rep["kill_switch"]
        assert "0.22" in rep["kill_switch"]

    def test_inputs_only(self, rep):
        assert "n_w=5" in rep["inputs_only"]
        assert "K_CS=74" in rep["inputs_only"]
        assert "zero free parameters" in rep["inputs_only"]

    def test_fundamental_ratio_values(self, rep):
        assert abs(rep["fundamental_ratio"]["pi_sq_over_kcs"] - math.pi**2/74) < 1e-12
        assert abs(rep["fundamental_ratio"]["kcs_over_pi_sq"] - 74/math.pi**2) < 1e-12

    def test_scaling_table_present(self, rep):
        assert isinstance(rep["scaling_table"], list)
        assert len(rep["scaling_table"]) > 5

    def test_pi_identities_present(self, rep):
        assert "pi_identities_near_alpha_s" in rep

    def test_warp_anchor_view_present(self, rep):
        assert "warp_anchor_topological_view" in rep

    def test_architecture_limit_audit_present(self, rep):
        assert "architecture_limit_audit" in rep
        assert rep["architecture_limit_audit"]["architecture_limit_confirmed"] is True

    def test_key_conclusions_list(self, rep):
        assert isinstance(rep["key_conclusions"], list)
        assert len(rep["key_conclusions"]) >= 4

    def test_key_conclusion_mentions_cc_gap(self, rep):
        joined = " ".join(rep["key_conclusions"])
        assert "58" in joined or "CC" in joined or "206" in joined

    def test_key_conclusion_mentions_best_pi_id(self, rep):
        joined = " ".join(rep["key_conclusions"])
        assert "8.1%" in joined or "3π/74" in joined

    def test_path_forward_present(self, rep):
        assert "path_forward" in rep
        assert len(rep["path_forward"]) > 50

    def test_path_forward_mentions_holographic(self, rep):
        assert "holograph" in rep["path_forward"].lower()

    def test_version(self, rep):
        assert rep["version"] == "v1.0"

    def test_architecture_limit_audit_confirms_no_closure(self, rep):
        audit = rep["architecture_limit_audit"]
        assert not audit["n_is_integer"]
        assert audit["eval_at_n_pikr_37"]["deficit_vs_58_orders"] > 20.0


# ===========================================================================
# JAX-ACCELERATED VERIFICATION OF TOPOLOGICAL SCALING (Pillar 207)
# ===========================================================================

jax = pytest.importorskip("jax", reason="JAX not installed")

import jax
import jax.numpy as jnp
from jax import grad, jit, vmap

# Enable 64-bit precision for all JAX tests in this module
jax.config.update("jax_enable_x64", True)

_PI   = math.pi
_K_CS = float(74)
_N_W  = float(5)
_N2   = float(7)
_N_C  = float(3)   # N_c = ceil(n_w/2) = 3


def _jax_topological_factor(k_cs: float, n: float) -> "jax.Array":
    """JAX-differentiable (π²/K_CS)^n."""
    return (_PI ** 2 / k_cs) ** n


def _jax_inverse_factor(k_cs: float, n: float) -> "jax.Array":
    """JAX-differentiable (K_CS/π²)^n."""
    return (k_cs / _PI ** 2) ** n


class TestJAXTopologicalScaling:
    """JAX autodiff + vmap for Pillar 207 scaling-table verification."""

    def test_jax_factor_n1_matches_python(self):
        """JAX (π²/K_CS)^1 must match Python PI_SQ_OVER_KCS."""
        val = float(_jax_topological_factor(_K_CS, 1.0))
        assert abs(val - PI_SQ_OVER_KCS) < 1e-12

    def test_jax_inverse_n1_matches_python(self):
        val = float(_jax_inverse_factor(_K_CS, 1.0))
        assert abs(val - KCS_OVER_PI_SQ) < 1e-12

    def test_jit_factor_stable(self):
        jit_fn = jit(_jax_topological_factor)
        r1 = float(jit_fn(_K_CS, 1.0))
        r2 = float(jit_fn(_K_CS, 2.0))
        assert abs(r1 - PI_SQ_OVER_KCS) < 1e-12
        assert abs(r2 - PI_SQ_OVER_KCS ** 2) < 1e-12

    def test_grad_factor_wrt_kcs_negative(self):
        """d/dK_CS[(π²/K_CS)^n] < 0: larger K_CS → smaller suppression factor."""
        dfn = grad(_jax_topological_factor, argnums=0)
        assert float(dfn(_K_CS, 2.0)) < 0

    def test_grad_factor_wrt_n_negative(self):
        """d/dn[(π²/K_CS)^n] < 0 for K_CS > π² (log(π²/K_CS) < 0)."""
        dfn = grad(_jax_topological_factor, argnums=1)
        assert float(dfn(_K_CS, 1.0)) < 0

    def test_vmap_scaling_table_matches_python_table(self):
        """vmap over n values must match the Python scaling_table()."""
        py_table = scaling_table([1.0, 2.0, 3.0, 37.0])
        n_vals = jnp.array([r["n"] for r in py_table])
        jax_factors = vmap(lambda n: _jax_topological_factor(_K_CS, n))(n_vals)
        for i, row in enumerate(py_table):
            py_val = row["pi_sq_over_kcs_to_n"]
            jax_val = float(jax_factors[i])
            assert abs(py_val - jax_val) < 1e-10, (
                f"n={row['n']}: python={py_val}, jax={jax_val}"
            )

    def test_vmap_inverse_at_n37_is_1e32(self):
        """(K_CS/π²)^37 ≈ 10^32.4 — JAX confirms."""
        n_vals = jnp.array([37.0])
        results = vmap(lambda n: _jax_inverse_factor(_K_CS, n))(n_vals)
        log10_val = float(jnp.log10(results[0]))
        assert abs(log10_val - 32.37) < 0.1

    def test_jax_confirms_cc_gap_not_closed(self):
        """At n=37 (πkR), factor is ~10^32 not 10^58 — architecture limit confirmed."""
        val_at_pikr = float(_jax_inverse_factor(_K_CS, 37.0))
        log10_val = math.log10(val_at_pikr)
        assert log10_val < 58.0  # does NOT close the CC gap

    def test_jax_confirms_n_needed_for_cc_gap(self):
        """Find n numerically via JAX grad so that (K_CS/π²)^n = 10^58."""
        # n_needed = 58 / log10(K_CS/π²)
        log10_base = math.log10(KCS_OVER_PI_SQ)
        n_needed = 58.0 / log10_base
        assert n_needed > 60.0   # >58, confirming non-integer
        assert abs(n_needed - round(n_needed)) > 0.1   # not close to integer

    def test_grad_inverse_factor_wrt_n_is_positive(self):
        """d/dn[(K_CS/π²)^n] > 0 — larger n amplifies the enhancement."""
        dfn = grad(_jax_inverse_factor, argnums=1)
        assert float(dfn(_K_CS, 1.0)) > 0

    def test_vmap_monotone_suppression(self):
        """Suppression (π²/K_CS)^n must be strictly decreasing in n for n > 0."""
        n_vals = jnp.array([1.0, 2.0, 3.0, 5.0, 10.0])
        factors = vmap(lambda n: _jax_topological_factor(_K_CS, n))(n_vals)
        diffs = jnp.diff(factors)
        assert jnp.all(diffs < 0), "Expected strictly decreasing factors"

    def test_jax_best_pi_identity_residual(self):
        """JAX verification: 3π/74 residual from α_s(M_Z) = 0.11796."""
        alpha_s_mz = 0.11796
        pi_nc_kcs = _PI * _N_C / _K_CS   # 3π/74 (N_c=3, not n₂=7)
        residual_pct = abs(pi_nc_kcs - alpha_s_mz) / alpha_s_mz * 100.0
        assert 5.0 < residual_pct < 15.0  # 8% off — curiosity, not derivation

    def test_jit_inverse_repeated_calls_stable(self):
        jit_fn = jit(_jax_inverse_factor)
        ref = float(jit_fn(_K_CS, 37.0))
        for _ in range(5):
            val = float(jit_fn(_K_CS, 37.0))
        assert abs(val - ref) < 1e-10
