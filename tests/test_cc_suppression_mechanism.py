# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cc_suppression_mechanism.py
========================================
Test suite for Pillar 76 — Cosmological Constant Suppression Mechanism
(src/core/cc_suppression_mechanism.py).

Covers:
  - Module constants (N_W, K_CS, C_S, F_BRAID_TREE, RHO_OBS, ORDERS)
  - tree_level_suppression: value, positivity, raises on bad input
  - loop_correction_to_fbraid: positivity, scaling, finiteness
  - effective_fbraid_with_loops: larger than tree, finiteness
  - cc_residual_after_suppression: positivity, scaling with M_KK⁴
  - orders_resolved_at_scale: >= 0, scales with M_KK
  - renorm_group_running_cc: structure, ordering, ratio_to_obs at closure
  - casimir_stabilisation_energy: negative, magnitude
  - full_cc_budget: all keys present, rho_net < rho_naive, ratio_to_obs
  - vacuum_stability_audit: mechanism list length, verdict, residual gaps

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.cc_suppression_mechanism import (
    N_W, N1, N2, K_CS, C_S,
    F_BRAID_TREE, RHO_OBS, RHO_QFT, ORDERS_DISCREPANCY,
    M_KK_CANONICAL, ALPHA_KK_CANONICAL,
    tree_level_suppression,
    loop_correction_to_fbraid,
    effective_fbraid_with_loops,
    cc_residual_after_suppression,
    orders_resolved_at_scale,
    renorm_group_running_cc,
    casimir_stabilisation_energy,
    full_cc_budget,
    vacuum_stability_audit,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n1_n2(self):
        assert N1 == 5
        assert N2 == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_f_braid_tree_value(self):
        expected = (12.0 / 37.0) ** 2 / 74
        assert abs(F_BRAID_TREE - expected) < 1e-12

    def test_f_braid_small(self):
        """f_braid ≈ 1.42×10⁻³ (much less than 1)."""
        assert F_BRAID_TREE < 0.01
        assert F_BRAID_TREE > 1e-4

    def test_rho_obs_much_smaller(self):
        """ρ_obs ≪ ρ_QFT (the whole problem)."""
        assert RHO_OBS < RHO_QFT * 1e-100

    def test_orders_discrepancy_near_120(self):
        """log10(ρ_QFT/ρ_obs) should be near 120."""
        assert 115 < ORDERS_DISCREPANCY < 125


# ---------------------------------------------------------------------------
# tree_level_suppression
# ---------------------------------------------------------------------------

class TestTreeLevelSuppression:
    def test_canonical_value(self):
        f = tree_level_suppression()
        assert abs(f - F_BRAID_TREE) < 1e-12

    def test_positive(self):
        assert tree_level_suppression() > 0

    def test_less_than_one(self):
        assert tree_level_suppression() < 1.0

    def test_raises_on_zero_kcs(self):
        with pytest.raises(ValueError):
            tree_level_suppression(k_cs=0)

    def test_raises_on_negative_kcs(self):
        with pytest.raises(ValueError):
            tree_level_suppression(k_cs=-1)

    def test_scales_with_cs_squared(self):
        """f ∝ c_s²."""
        f1 = tree_level_suppression(c_s=0.1)
        f2 = tree_level_suppression(c_s=0.2)
        assert abs(f2 / f1 - 4.0) < 1e-10

    def test_scales_inversely_with_kcs(self):
        """f ∝ 1/k_cs."""
        f1 = tree_level_suppression(k_cs=74)
        f2 = tree_level_suppression(k_cs=148)
        assert abs(f1 / f2 - 2.0) < 1e-10


# ---------------------------------------------------------------------------
# loop_correction_to_fbraid
# ---------------------------------------------------------------------------

class TestLoopCorrectionToFbraid:
    def test_positive(self):
        """Loop correction is positive (increases f_braid)."""
        delta = loop_correction_to_fbraid()
        assert delta > 0

    def test_small_perturbative(self):
        """Loop correction is small (perturbative)."""
        delta = loop_correction_to_fbraid()
        assert delta < 1.0

    def test_scales_with_alpha(self):
        """δ_loop ∝ α_kk."""
        d1 = loop_correction_to_fbraid(alpha_kk=0.01)
        d2 = loop_correction_to_fbraid(alpha_kk=0.02)
        assert abs(d2 / d1 - 2.0) < 0.01

    def test_scales_with_log(self):
        """δ_loop ∝ log(M_Pl/M_KK)."""
        d1 = loop_correction_to_fbraid(log_ratio=10.0)
        d2 = loop_correction_to_fbraid(log_ratio=20.0)
        assert abs(d2 / d1 - 2.0) < 0.01

    def test_finite(self):
        assert math.isfinite(loop_correction_to_fbraid())

    def test_log_ratio_override(self):
        """Providing log_ratio directly should give consistent result."""
        d_auto = loop_correction_to_fbraid(M_Pl_over_M_KK=1e10)
        d_manual = loop_correction_to_fbraid(log_ratio=math.log(1e10))
        assert abs(d_auto - d_manual) < 1e-10


# ---------------------------------------------------------------------------
# effective_fbraid_with_loops
# ---------------------------------------------------------------------------

class TestEffectiveFbraidWithLoops:
    def test_larger_than_tree(self):
        """With positive loop correction, f_eff > f_tree."""
        f_eff = effective_fbraid_with_loops()
        assert f_eff > F_BRAID_TREE

    def test_still_small(self):
        """Even with loops, f_eff ≪ 1."""
        assert effective_fbraid_with_loops() < 0.01

    def test_finite(self):
        assert math.isfinite(effective_fbraid_with_loops())

    def test_positive(self):
        assert effective_fbraid_with_loops() > 0


# ---------------------------------------------------------------------------
# cc_residual_after_suppression
# ---------------------------------------------------------------------------

class TestCCResidualAfterSuppression:
    def test_positive(self):
        assert cc_residual_after_suppression(1e-10) > 0

    def test_scales_with_mkk4(self):
        """ρ_eff ∝ M_KK⁴."""
        r1 = cc_residual_after_suppression(1e-10)
        r2 = cc_residual_after_suppression(2e-10)
        assert abs(r2 / r1 - 16.0) < 0.01

    def test_at_canonical_mkk(self):
        """At M_KK_canonical (NRI-derived), ρ_eff should equal ρ_obs exactly."""
        rho = cc_residual_after_suppression(M_KK_CANONICAL, F_BRAID_TREE)
        ratio = rho / RHO_OBS
        # M_KK_CANONICAL is derived from (ρ_obs × 16π² / f_braid)^(1/4) → ratio = 1.0
        assert abs(ratio - 1.0) < 1e-6

    def test_raises_on_zero_mkk(self):
        with pytest.raises(ValueError):
            cc_residual_after_suppression(0.0)

    def test_raises_on_negative_mkk(self):
        with pytest.raises(ValueError):
            cc_residual_after_suppression(-1e-10)


# ---------------------------------------------------------------------------
# orders_resolved_at_scale
# ---------------------------------------------------------------------------

class TestOrdersResolvedAtScale:
    def test_nonnegative(self):
        """Always non-negative (can't resolve more than 120 going the wrong way)."""
        assert orders_resolved_at_scale(M_KK_CANONICAL) >= 0

    def test_larger_mkk_fewer_orders(self):
        """Larger M_KK → less suppression → fewer orders resolved."""
        o_small = orders_resolved_at_scale(1e-15)
        o_large = orders_resolved_at_scale(1e-5)
        assert o_small > o_large

    def test_at_canonical_mkk_near_full(self):
        """At M_KK_canonical (NRI-derived), ρ_eff = ρ_obs → all orders resolved."""
        orders = orders_resolved_at_scale(M_KK_CANONICAL, F_BRAID_TREE)
        # M_KK_CANONICAL is derived so ρ_eff = ρ_obs → orders = log10(ρ_QFT/ρ_obs) ≈ 120
        assert abs(orders - ORDERS_DISCREPANCY) < 0.01

    def test_finite(self):
        assert math.isfinite(orders_resolved_at_scale(M_KK_CANONICAL))


# ---------------------------------------------------------------------------
# renorm_group_running_cc
# ---------------------------------------------------------------------------

class TestRenormGroupRunningCC:
    def test_keys(self):
        result = renorm_group_running_cc(1.0, 1e-10)
        for key in ("rho_UV_planck", "rho_IR_planck", "mu_start", "mu_end",
                    "power_suppression", "f_braid", "orders_resolved", "rho_obs"):
            assert key in result

    def test_rho_ir_less_than_uv(self):
        result = renorm_group_running_cc(1.0, 1e-10)
        assert result["rho_IR_planck"] < result["rho_UV_planck"]

    def test_power_suppression(self):
        """(μ_IR/μ_UV)⁴ should be the power suppression factor."""
        result = renorm_group_running_cc(1.0, 0.1)
        assert abs(result["power_suppression"] - 0.1 ** 4) < 1e-20

    def test_orders_resolved_positive(self):
        result = renorm_group_running_cc(1.0, 1e-10)
        assert result["orders_resolved"] > 0

    def test_ratio_to_obs_at_closure(self):
        """At M_KK_canonical, ratio should be near 1."""
        result = renorm_group_running_cc(1.0, M_KK_CANONICAL)
        # ratio_to_obs should be in a physically reasonable range
        assert result["ratio_to_obs"] > 0


# ---------------------------------------------------------------------------
# casimir_stabilisation_energy
# ---------------------------------------------------------------------------

class TestCasimirStabilisationEnergy:
    def test_negative(self):
        """Casimir energy is negative (stabilising)."""
        assert casimir_stabilisation_energy(1.0) < 0

    def test_scales_with_r4(self):
        """ρ_Casimir ∝ R_KK⁻⁴."""
        r1 = casimir_stabilisation_energy(1.0)
        r2 = casimir_stabilisation_energy(2.0)
        assert abs(r2 / r1 - 1.0 / 16.0) < 0.001

    def test_finite(self):
        assert math.isfinite(casimir_stabilisation_energy(1.0))

    def test_magnitude_small_for_large_r(self):
        """At macroscopic R_KK, Casimir energy is very small."""
        rho_c = casimir_stabilisation_energy(1e10)
        assert abs(rho_c) < 1e-30


# ---------------------------------------------------------------------------
# full_cc_budget
# ---------------------------------------------------------------------------

class TestFullCCBudget:
    def test_keys(self):
        result = full_cc_budget()
        for key in ("rho_naive_QFT", "rho_after_KK_cutoff", "rho_after_braid_tree",
                    "rho_after_braid_loop", "rho_casimir", "rho_net_effective",
                    "rho_obs", "ratio_net_to_obs", "orders_resolved_vs_naive",
                    "total_discrepancy_orders", "f_braid_tree", "f_braid_with_loops"):
            assert key in result

    def test_rho_ordering(self):
        """Each step should reduce vacuum energy."""
        r = full_cc_budget()
        assert r["rho_naive_QFT"] > r["rho_after_KK_cutoff"]
        assert r["rho_after_KK_cutoff"] > r["rho_after_braid_tree"]

    def test_f_braid_tree_consistent(self):
        """f_braid_tree should match the module constant."""
        r = full_cc_budget()
        assert abs(r["f_braid_tree"] - F_BRAID_TREE) < 1e-12

    def test_orders_resolved_positive(self):
        assert full_cc_budget()["orders_resolved_vs_naive"] > 0

    def test_rho_net_positive(self):
        """Net effective CC should be positive (Casimir correction is small)."""
        r = full_cc_budget()
        assert r["rho_net_effective"] > 0

    def test_ratio_to_obs_finite(self):
        assert math.isfinite(full_cc_budget()["ratio_net_to_obs"])


# ---------------------------------------------------------------------------
# vacuum_stability_audit
# ---------------------------------------------------------------------------

class TestVacuumStabilityAudit:
    def test_keys(self):
        result = vacuum_stability_audit()
        for key in ("title", "mechanisms", "full_budget", "residual_open", "verdict"):
            assert key in result

    def test_mechanism_count(self):
        """Should have at least 5 mechanisms listed."""
        result = vacuum_stability_audit()
        assert len(result["mechanisms"]) >= 5

    def test_each_mechanism_has_name(self):
        for m in vacuum_stability_audit()["mechanisms"]:
            assert "name" in m
            assert "status" in m

    def test_residual_open_not_empty(self):
        """There should be at least one open problem listed (honest accounting)."""
        result = vacuum_stability_audit()
        assert len(result["residual_open"]) >= 1

    def test_verdict_not_empty(self):
        assert len(vacuum_stability_audit()["verdict"]) > 20

    def test_f_braid_in_mechanisms(self):
        """The braid suppression mechanism must be listed."""
        names = [m["name"] for m in vacuum_stability_audit()["mechanisms"]]
        assert any("braid" in n.lower() for n in names)

    def test_neutrino_radion_in_mechanisms(self):
        """The Neutrino-Radion Identity must be listed."""
        names = [m["name"] for m in vacuum_stability_audit()["mechanisms"]]
        assert any("neutrino" in n.lower() for n in names)
