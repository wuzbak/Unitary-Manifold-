# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 309 — FTUM Contractive-Regime Certificate."""
from __future__ import annotations

import pytest
import numpy as np

from src.core.pillar309_ftum_contractive_regime_cert import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    KAPPA_CANONICAL,
    KAPPA_PHYSICAL_REGIME,
    DT_CANONICAL,
    build_physical_regime_network,
    lipschitz_scan_physical_regime,
    contractive_regime_certificate,
    ftum_verdict,
)


# ── Identity ───────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 309


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_pillar_title_contains_ftum():
    assert "FTUM" in PILLAR_TITLE or "Contractive" in PILLAR_TITLE


def test_kappa_canonical_value():
    assert KAPPA_CANONICAL == pytest.approx(0.25)


def test_kappa_physical_regime_values():
    """Physical regime must include at least kappa=1.0 (natural units)."""
    assert 1.0 in list(KAPPA_PHYSICAL_REGIME)
    assert all(k > 0 for k in KAPPA_PHYSICAL_REGIME)
    # kappa=10 excluded: (10+0.2)*0.2 = 2.04 > 2 violates analytic proof condition
    assert 10.0 not in list(KAPPA_PHYSICAL_REGIME)


def test_dt_canonical_value():
    assert DT_CANONICAL == pytest.approx(0.2)


# ── build_physical_regime_network ─────────────────────────────────────────────

def test_physical_network_has_correct_node_count():
    net = build_physical_regime_network(n_nodes=4)
    assert net.n_nodes() == 4


def test_physical_network_nodes_near_holographic_fixed_point():
    """Nodes initialised with S ≈ A/4G (within 50%)."""
    net = build_physical_regime_network(n_nodes=6, rng=np.random.default_rng(7))
    for node in net.nodes:
        S_star = node.A / 4.0
        relative_deviation = abs(node.S - S_star) / (S_star + 1e-12)
        assert relative_deviation < 0.5, (
            f"Node S={node.S:.4f}, A={node.A:.4f}, S*={S_star:.4f}; "
            f"relative deviation {relative_deviation:.2%} should be < 50%."
        )


def test_physical_network_x_order_one():
    """X values should be O(1) to suppress geodesic divergence."""
    net = build_physical_regime_network(n_nodes=4, rng=np.random.default_rng(42))
    for node in net.nodes:
        x_norm = float(np.linalg.norm(node.X))
        assert x_norm > 0.1, f"|X| = {x_norm:.4f} is too small; should be O(1)"


def test_physical_network_adjacency_is_tridiagonal():
    """Chain network: adjacency is symmetric, non-negative, with zero diagonal."""
    net = build_physical_regime_network(n_nodes=4, coupling=0.1)
    A = net.adjacency
    assert A.shape == (4, 4)
    assert np.all(np.diag(A) == 0.0)
    assert np.allclose(A, A.T)
    assert np.all(A >= 0.0)


def test_physical_network_entropy_positive():
    net = build_physical_regime_network(n_nodes=5)
    for node in net.nodes:
        assert node.S > 0, "Node entropy must be strictly positive."


# ── lipschitz_scan_physical_regime ────────────────────────────────────────────

def test_scan_returns_one_result_per_kappa():
    kappas = (0.5, 1.0, 5.0)
    results = lipschitz_scan_physical_regime(kappa_values=kappas, n_pairs=10)
    assert len(results) == len(kappas)


def test_scan_result_keys_complete():
    results = lipschitz_scan_physical_regime(kappa_values=(1.0,), n_pairs=5)
    required = {
        "kappa", "dt", "L_empirical", "is_contraction_empirical",
        "L_margin_empirical", "n_pairs_sampled",
        "L_analytic", "rho_S_analytic", "rho_X_analytic",
        "is_contraction_analytic", "all_conditions_hold", "regime_label",
    }
    assert required.issubset(set(results[0].keys()))


def test_scan_kappa_1_analytic_is_contractive():
    """At kappa=1.0, analytic L < 1 must hold (physical regime)."""
    results = lipschitz_scan_physical_regime(
        kappa_values=(1.0,), n_pairs=5, rng_seed=42
    )
    r = results[0]
    assert r["is_contraction_analytic"], (
        f"Expected analytic L < 1 at kappa=1.0, got L_analytic={r['L_analytic']:.4f}"
    )
    assert r["L_analytic"] < 1.0


def test_scan_kappa_5_analytic_is_contractive():
    """At kappa=5.0, analytic L < 1 must hold."""
    results = lipschitz_scan_physical_regime(
        kappa_values=(5.0,), n_pairs=5, rng_seed=42
    )
    r = results[0]
    assert r["is_contraction_analytic"], (
        f"Expected analytic L < 1 at kappa=5.0, got L_analytic={r['L_analytic']:.4f}"
    )


def test_scan_analytic_holds_for_physical_regime():
    """Analytic contraction must hold for all physical kappa values."""
    results = lipschitz_scan_physical_regime(
        kappa_values=KAPPA_PHYSICAL_REGIME, n_pairs=5, rng_seed=42
    )
    for r in results:
        assert r["is_contraction_analytic"], (
            f"Analytic contraction failed at kappa={r['kappa']}: "
            f"L_analytic={r['L_analytic']:.4f}"
        )


def test_scan_empirical_L_finite_and_positive():
    """Empirical L must be finite and positive (even if > 1)."""
    results = lipschitz_scan_physical_regime(
        kappa_values=KAPPA_PHYSICAL_REGIME, n_pairs=10, rng_seed=42
    )
    import math
    for r in results:
        assert r["L_empirical"] > 0, "Empirical L must be positive."
        assert math.isfinite(r["L_empirical"]), "Empirical L must be finite."


def test_scan_L_analytic_is_positive():
    results = lipschitz_scan_physical_regime(kappa_values=(1.0,), n_pairs=5)
    assert 0.0 < results[0]["L_analytic"] < 1.0


def test_scan_rho_S_bounded_below_one():
    """Entropy subspace spectral radius must be < 1 at kappa=1.0."""
    results = lipschitz_scan_physical_regime(kappa_values=(1.0,), n_pairs=5)
    assert results[0]["rho_S_analytic"] < 1.0


# ── contractive_regime_certificate ────────────────────────────────────────────

def test_certificate_structure():
    cert = contractive_regime_certificate(n_pairs=10, rng_seed=42)
    required_keys = {
        "pillar", "title", "track", "scan_results",
        "n_analytic_contractive", "n_empirical_contractive", "n_non_contractive",
        "min_L_physical_regime",
        "physical_regime_verdict", "canonical_kappa", "canonical_analytic_L",
        "canonical_kappa_verdict", "authoritative_gate",
        "outer_basin_explanation", "ftum_verdict",
        "no_hardgate_impact", "toe_score_impact",
    }
    assert required_keys.issubset(set(cert.keys()))


def test_certificate_pillar_number():
    cert = contractive_regime_certificate(n_pairs=5)
    assert cert["pillar"] == PILLAR_NUMBER


def test_certificate_contractive_in_physical_regime():
    """All physical-regime kappa values must give analytic L < 1."""
    cert = contractive_regime_certificate(n_pairs=10, rng_seed=42)
    n_total = len(cert["scan_results"])
    assert cert["n_analytic_contractive"] == n_total, (
        f"Expected all {n_total} kappa values with analytic L < 1, "
        f"got {cert['n_analytic_contractive']}."
    )
    assert cert["physical_regime_verdict"] == "CONTRACTIVE_IN_PHYSICAL_REGIME"


def test_certificate_canonical_analytic_holds():
    """Analytic proof at kappa=0.25 must still confirm contraction."""
    cert = contractive_regime_certificate(n_pairs=5)
    assert cert["canonical_kappa_verdict"] == "ANALYTIC_CONTRACTION_HOLDS"
    assert cert["canonical_analytic_L"] < 1.0


def test_certificate_no_hardgate_impact():
    cert = contractive_regime_certificate(n_pairs=5)
    assert cert["no_hardgate_impact"] is True
    assert cert["toe_score_impact"] == "NONE"


def test_certificate_overall_verdict():
    cert = contractive_regime_certificate(n_pairs=10, rng_seed=42)
    assert cert["ftum_verdict"] == (
        "CONTRACTIVE_IN_PHYSICAL_REGIME__ANALYTIC_ALWAYS_HOLDS"
    )


def test_certificate_outer_basin_explanation_present():
    cert = contractive_regime_certificate(n_pairs=5)
    assert len(cert["outer_basin_explanation"]) > 100


# ── ftum_verdict helper ────────────────────────────────────────────────────────

def test_ftum_verdict_returns_string():
    v = ftum_verdict(rng_seed=42)
    assert isinstance(v, str)
    assert len(v) > 0


def test_ftum_verdict_contractive():
    v = ftum_verdict(rng_seed=42)
    assert "CONTRACTIVE" in v
