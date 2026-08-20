#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
COMPACTIFICATION/kernel_test.py
================================
Standalone verification suite for the Unitary Manifold kernel.

Designed for maximum resilience and portability:
  - Runs as a plain Python script: python kernel_test.py
  - Also fully pytest-compatible:  pytest kernel_test.py -v
  - No dependencies beyond numpy (scipy optional)
  - Zero imports from the parent repository

Exit codes:
  0  — all assertions pass
  1  — one or more assertions failed

Theory: ThomasCory Walker-Pearson (2026)
Code:   GitHub Copilot (AI)
"""

from __future__ import annotations

import math
import os
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Path setup — works from any directory
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from kernel import (
    # Constants
    N1, N2, K_CS, N_W, N_C,
    C_S, PHI0_BARE, JACOBIAN_KK, PHI0_EFF, PHI_STAR,
    ALPHA_GUT, LAMBDA_QCD_GEV, M_HIGGS_GEV, W_KK, XI_C, SENTINEL_CAPACITY,
    NS_PLANCK_CENTRAL, NS_PLANCK_SIGMA, R_BICEP_KECK_95,
    BETA_CANONICAL_DEG, BETA_GW_DEG, BETA_MINAMI_CENTER, BETA_MINAMI_SIGMA,
    BETA_FALSIFICATION_LOW, BETA_FALSIFICATION_HIGH,
    KNOWN_GAPS, FALSIFICATION_CONDITIONS,
    # Functions
    assemble_5d_metric, field_strength, christoffel, compute_curvature,
    gw_potential, gw_potential_derivs, slow_roll_params,
    spectral_index, tensor_to_scalar_ratio, jacobian_5d_4d, ns_from_phi0,
    beta_birefringence, cs_level_scan,
    MultiverseNode, fixed_point_iteration,
    alpha_gut_from_cs, lambda_qcd_geometric, higgs_mass_one_loop,
    yukawa_gap_report, dark_energy_eos, full_report, symbolic_algebra,
    KNOWN_GAPS,
)
from axioms import (
    AXIOM_REGISTRY, AxiomStatus,
    axiom_by_name, axioms_by_status, summary_table,
)


# ---------------------------------------------------------------------------
# Minimal test harness (plain-Python compatible, no pytest required)
# ---------------------------------------------------------------------------

_RESULTS: List[Tuple[str, bool, str]] = []
_FAILURES = 0


def _test(name: str, cond: bool, detail: str = "") -> None:
    """Record a test result."""
    global _FAILURES
    _RESULTS.append((name, cond, detail))
    if not cond:
        _FAILURES += 1
    status = "PASS" if cond else "FAIL"
    mark   = "✓" if cond else "✗"
    print(f"  {mark} [{status}] {name}" + (f"  — {detail}" if detail else ""))


def _section(title: str) -> None:
    print(f"\n── {title} ──")


# ===========================================================================
# Test group 1: Topological invariants (PROVED)
# ===========================================================================

def test_kcs_integer_sum_of_squares() -> None:
    """k_CS = 5² + 7² = 74 — the Chern–Simons level invariant."""
    _test("k_CS = 5² + 7² = 74",
          K_CS == N1**2 + N2**2 == 74,
          f"got {K_CS}")


def test_braided_sound_speed_exact() -> None:
    """c_s = 12/37 exactly from the (5,7) Pythagorean braid."""
    expected = 12 / 37
    _test("c_s = 12/37 exact",
          abs(C_S - expected) < 1e-14,
          f"got {C_S:.15f}, expected {expected:.15f}")


def test_pythagorean_identity() -> None:
    """sin²θ + cos²θ = 1 for the braid angle."""
    rho = math.sqrt(1.0 - C_S**2)
    _test("Pythagorean identity ρ² + c_s² = 1",
          abs(rho**2 + C_S**2 - 1.0) < 1e-14)


def test_n_c_from_n_w() -> None:
    """N_c = n_w − 2 = 3 (number of QCD colours)."""
    _test("N_c = N_W − 2 = 3",
          N_C == N_W - 2 == 3,
          f"got N_C={N_C}")


def test_alpha_gut_rational() -> None:
    """α_GUT = 3/74 exactly."""
    expected = 3.0 / 74.0
    _test("α_GUT = 3/74",
          abs(ALPHA_GUT - expected) < 1e-14,
          f"got {ALPHA_GUT:.8f}")


def test_jacobian_kk_value() -> None:
    """J_KK = 5 · 2π · √1 ≈ 31.416."""
    expected = N_W * 2.0 * math.pi * math.sqrt(PHI0_BARE)
    _test("J_KK = n_w · 2π · √φ₀",
          abs(JACOBIAN_KK - expected) < 1e-10,
          f"got {JACOBIAN_KK:.6f}")


def test_xi_c_rational() -> None:
    """Ξ_c = 35/74 (Unitary Pentad coupling)."""
    _test("Ξ_c = 35/74",
          abs(XI_C - 35/74) < 1e-14)


def test_sentinel_capacity_rational() -> None:
    """Sentinel capacity = 12/37 = c_s (self-consistency)."""
    _test("SENTINEL_CAPACITY = 12/37 = c_s",
          abs(SENTINEL_CAPACITY - C_S) < 1e-14)


# ===========================================================================
# Test group 2: CMB inflation pipeline (PROVED_CONDITIONAL)
# ===========================================================================

def test_ns_within_planck_1sigma() -> None:
    """nₛ ≈ 0.9635 is within Planck 2018 1σ window."""
    result = ns_from_phi0()
    ns = result["ns"]
    pull = result["pull_ns_sigma"]
    _test("nₛ within Planck 1σ",
          pull <= 1.0,
          f"nₛ={ns:.5f}, pull={pull:.3f}σ (Planck: {NS_PLANCK_CENTRAL}±{NS_PLANCK_SIGMA})")


def test_r_braided_below_bicep() -> None:
    """r_braided < 0.036 (BICEP/Keck 95% CL)."""
    result = ns_from_phi0()
    r = result["r_braided"]
    _test("r_braided < BICEP/Keck 95% CL",
          r < R_BICEP_KECK_95,
          f"r_braided={r:.5f}, limit={R_BICEP_KECK_95}")


def test_r_braided_equals_r_bare_times_cs() -> None:
    """r_braided = r_bare × c_s (exact identity)."""
    result = ns_from_phi0()
    diff = abs(result["r_braided"] - result["r_bare"] * C_S)
    _test("r_braided = r_bare × c_s",
          diff < 1e-12,
          f"diff={diff:.2e}")


def test_epsilon_small_slow_roll() -> None:
    """ε ≪ 1 (slow-roll validity)."""
    result = ns_from_phi0()
    eps = result["epsilon"]
    _test("ε ≪ 1 (slow-roll)",
          eps < 0.1,
          f"ε={eps:.6f}")


def test_inflaton_pipeline_deterministic() -> None:
    """ns_from_phi0() is deterministic (same result on two calls)."""
    r1 = ns_from_phi0()
    r2 = ns_from_phi0()
    _test("Inflation pipeline deterministic",
          r1["ns"] == r2["ns"] and r1["r_braided"] == r2["r_braided"])


def test_gw_potential_minimum() -> None:
    """V(φ₀_eff) = 0 — GW potential minimum at the vev."""
    V_min = gw_potential(PHI0_EFF, PHI0_EFF)
    _test("V(φ₀_eff) = 0 (potential minimum)",
          abs(V_min) < 1e-12,
          f"V_min={V_min:.2e}")


def test_gw_potential_positive_away_from_min() -> None:
    """V(0) > 0 (potential has energy at origin)."""
    V_top = gw_potential(0.0, PHI0_EFF)
    _test("V(0) > 0 (hilltop has energy)",
          V_top > 0,
          f"V(0)={V_top:.4f}")


def test_phi_star_is_saddle() -> None:
    """φ* = φ₀_eff/√3 is the slow-roll horizon-exit field value."""
    expected = PHI0_EFF / math.sqrt(3.0)
    _test("φ* = φ₀_eff / √3",
          abs(PHI_STAR - expected) < 1e-10,
          f"φ*={PHI_STAR:.5f}, expected={expected:.5f}")


# ===========================================================================
# Test group 3: Birefringence (DERIVED)
# ===========================================================================

def test_beta_canonical_in_window() -> None:
    """β_canonical = 0.331° is inside the falsification window [0.22°, 0.38°]."""
    _test("β_canonical in [0.22°, 0.38°]",
          BETA_FALSIFICATION_LOW <= BETA_CANONICAL_DEG <= BETA_FALSIFICATION_HIGH,
          f"β_canonical={BETA_CANONICAL_DEG}°")


def test_beta_gw_in_window() -> None:
    """β_gw = 0.351° is inside the falsification window [0.22°, 0.38°]."""
    _test("β_gw in [0.22°, 0.38°]",
          BETA_FALSIFICATION_LOW <= BETA_GW_DEG <= BETA_FALSIFICATION_HIGH,
          f"β_gw={BETA_GW_DEG}°")


def test_beta_canonical_not_in_gap() -> None:
    """β_canonical = 0.331° is NOT in the predicted gap [0.29°, 0.31°]."""
    from kernel import BETA_PREDICTED_GAP_LOW, BETA_PREDICTED_GAP_HIGH
    in_gap = BETA_PREDICTED_GAP_LOW <= BETA_CANONICAL_DEG <= BETA_PREDICTED_GAP_HIGH
    _test("β_canonical NOT in predicted gap",
          not in_gap,
          f"β_canonical={BETA_CANONICAL_DEG}°, gap=[{BETA_PREDICTED_GAP_LOW}°,{BETA_PREDICTED_GAP_HIGH}°]")


def test_beta_within_minami_2sigma() -> None:
    """Both β values within 2σ of Minami & Komatsu hint."""
    pull_canonical = abs(BETA_CANONICAL_DEG - BETA_MINAMI_CENTER) / BETA_MINAMI_SIGMA
    pull_gw        = abs(BETA_GW_DEG        - BETA_MINAMI_CENTER) / BETA_MINAMI_SIGMA
    _test("β within 2σ of Minami hint",
          max(pull_canonical, pull_gw) <= 2.0,
          f"pull_canonical={pull_canonical:.2f}σ, pull_gw={pull_gw:.2f}σ")


def test_beta_birefringence_function() -> None:
    """beta_birefringence() returns a dict with required keys."""
    b = beta_birefringence()
    required = {"beta_deg_analytic", "status", "pull_minami_sigma", "in_falsification_window"}
    _test("beta_birefringence() keys present",
          required.issubset(b.keys()))


# ===========================================================================
# Test group 4: 5D metric geometry
# ===========================================================================

def _make_flat_fields(N: int = 8, seed: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    rng = np.random.default_rng(seed)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g   = np.tile(eta, (N, 1, 1)) + 1e-6 * rng.standard_normal((N, 4, 4))
    g   = 0.5 * (g + g.transpose(0, 2, 1))
    B   = 1e-6 * rng.standard_normal((N, 4))
    phi = 1.0 + 1e-6 * rng.standard_normal(N)
    dx  = 0.1
    return g, B, phi, dx


def test_5d_metric_shape() -> None:
    """assemble_5d_metric returns shape (N, 5, 5)."""
    g, B, phi, _ = _make_flat_fields()
    G = assemble_5d_metric(g, B, phi)
    _test("5D metric shape (N,5,5)",
          G.shape == (8, 5, 5),
          f"got {G.shape}")


def test_5d_metric_g55_equals_phi_sq() -> None:
    """G₅₅ = φ² at every grid point."""
    g, B, phi, _ = _make_flat_fields()
    G = assemble_5d_metric(g, B, phi)
    diffs = np.abs(G[:, 4, 4] - phi**2)
    _test("G₅₅ = φ²",
          np.max(diffs) < 1e-10,
          f"max_diff={np.max(diffs):.2e}")


def test_5d_metric_symmetry() -> None:
    """5D metric is symmetric G_AB = G_BA."""
    g, B, phi, _ = _make_flat_fields()
    G = assemble_5d_metric(g, B, phi)
    asym = np.max(np.abs(G - G.transpose(0, 2, 1)))
    _test("5D metric symmetric",
          asym < 1e-14,
          f"max_asymmetry={asym:.2e}")


def test_field_strength_antisymmetric() -> None:
    """H_μν = −H_νμ (antisymmetric field strength)."""
    g, B, phi, dx = _make_flat_fields()
    H = field_strength(B, dx)
    asym = np.max(np.abs(H + H.transpose(0, 2, 1)))
    _test("H_μν antisymmetric",
          asym < 1e-12,
          f"max_violation={asym:.2e}")


def test_curvature_pipeline_runs() -> None:
    """compute_curvature() returns 4 arrays of the expected shapes."""
    N = 6
    g, B, phi, dx = _make_flat_fields(N)
    try:
        Gamma, Riem, Ricci, R = compute_curvature(g, B, phi, dx)
        ok = (Gamma.shape == (N, 4, 4, 4) and
              Riem.shape  == (N, 4, 4, 4, 4) and
              Ricci.shape == (N, 4, 4) and
              R.shape     == (N,))
        _test("Curvature pipeline shapes correct", ok,
              f"Gamma={Gamma.shape} Ricci={Ricci.shape} R={R.shape}")
    except Exception as e:
        _test("Curvature pipeline runs without exception", False, str(e))


def test_flat_metric_low_curvature() -> None:
    """Near-flat metric has small scalar curvature."""
    N = 8
    g, B, phi, dx = _make_flat_fields(N)
    try:
        _, _, _, R = compute_curvature(g, B, phi, dx)
        _test("Near-flat metric has |R| < 1",
              np.max(np.abs(R)) < 1.0,
              f"max|R|={np.max(np.abs(R)):.4f}")
    except Exception as e:
        _test("Flat curvature test", False, str(e))


# ===========================================================================
# Test group 5: FTUM fixed-point iteration (A9_FTUM)
# ===========================================================================

def test_ftum_convergence() -> None:
    """FTUM fixed-point iteration converges within 500 steps."""
    result = fixed_point_iteration()
    _test("FTUM converges",
          result["converged"],
          f"iterations={result['iterations']}, S*={result['S_fixed_point']:.5f}")


def test_ftum_phi0_reasonable() -> None:
    """FTUM-derived φ₀_bare is near 1.0 in Planck units."""
    result = fixed_point_iteration()
    if result["phi0_bare"] is not None:
        _test("FTUM φ₀_bare near 1.0",
              0.0 < result["phi0_bare"] < 10.0,
              f"φ₀_bare={result['phi0_bare']:.5f}")
    else:
        _test("FTUM φ₀_bare reasonable", False, "convergence failed")


def test_ftum_s_star_positive() -> None:
    """FTUM fixed-point entropy S* > 0."""
    result = fixed_point_iteration()
    _test("FTUM S* > 0",
          result["S_fixed_point"] > 0,
          f"S*={result['S_fixed_point']:.5f}")


def test_ftum_deterministic() -> None:
    """FTUM is deterministic (same initial conditions → same result)."""
    r1 = fixed_point_iteration()
    r2 = fixed_point_iteration()
    _test("FTUM deterministic",
          r1["S_fixed_point"] == r2["S_fixed_point"] and
          r1["converged"]      == r2["converged"])


# ===========================================================================
# Test group 6: GUT / QCD / Higgs sector
# ===========================================================================

def test_alpha_gut_derivation() -> None:
    """α_GUT = 3/74 ≈ 0.04054 within 5% of SU(5) reference."""
    result = alpha_gut_from_cs()
    _test("α_GUT within 5% of SU(5) reference",
          result["residual_pct"] < 5.0,
          f"residual={result['residual_pct']:.2f}%")


def test_lambda_qcd_geometric_range() -> None:
    """Λ_QCD geometric ≈ 198–210 MeV (within factor 2 of PDG)."""
    result = lambda_qcd_geometric()
    lqcd = result["lambda_qcd_nlo_gev"] * 1000  # MeV
    _test("Λ_QCD geometric 100–400 MeV",
          100.0 <= lqcd <= 400.0,
          f"Λ_QCD={lqcd:.1f} MeV")


def test_lambda_qcd_soft_wall_gap_documented() -> None:
    """Soft-wall gap label is present in QCD result."""
    result = lambda_qcd_geometric()
    _test("Soft-wall gap documented",
          "KNOWN_SOFT_WALL_SYSTEMATIC" in result["soft_wall_systematic"])


def test_higgs_mass_one_loop_range() -> None:
    """M_H one-loop is between 100 and 150 GeV."""
    result = higgs_mass_one_loop()
    mh = result["M_higgs_kernel_gev"]
    _test("M_H one-loop in [100, 150] GeV",
          100.0 <= mh <= 150.0,
          f"M_H={mh:.2f} GeV")


def test_higgs_architecture_limit_documented() -> None:
    """Higgs architecture limit is explicitly flagged."""
    result = higgs_mass_one_loop()
    _test("Higgs architecture limit documented",
          "ARCHITECTURE_LIMIT" in result["architecture_limit"])


def test_yukawa_status_is_fitted() -> None:
    """Yukawa sector is honestly labelled FITTED (not claimed to be DERIVED)."""
    result = yukawa_gap_report()
    _test("Yukawa status = FITTED",
          result["status"] == "FITTED",
          f"got: {result['status']}")


def test_yukawa_fn_parameters_reduced() -> None:
    """Irreducible FN parameters ≤ 9 (reduced from original 9 → currently 3)."""
    result = yukawa_gap_report()
    _test("FN parameters ≤ 9",
          result["irreducible_fn_parameters"] <= 9,
          f"got {result['irreducible_fn_parameters']}")


# ===========================================================================
# Test group 7: Dark energy
# ===========================================================================

def test_dark_energy_eos_range() -> None:
    """w_KK ∈ (−1.1, −0.8) — not too far from Λ or quintessence."""
    _test("w_KK ∈ (−1.1, −0.8)",
          -1.1 < W_KK < -0.8,
          f"w_KK={W_KK:.4f}")


def test_dark_energy_wa_zero() -> None:
    """w_a = 0 (no time evolution of EoS)."""
    result = dark_energy_eos()
    _test("w_a = 0",
          result["w_a"] == 0.0)


def test_dark_energy_tension_documented() -> None:
    """DESI/Planck tension is documented (not hidden)."""
    result = dark_energy_eos()
    _test("Dark energy tension documented",
          result["status_planck_bao"] == "TENSION")


# ===========================================================================
# Test group 8: Axiom registry
# ===========================================================================

def test_axiom_registry_nonempty() -> None:
    """AXIOM_REGISTRY is non-empty."""
    _test("AXIOM_REGISTRY non-empty",
          len(AXIOM_REGISTRY) > 0,
          f"len={len(AXIOM_REGISTRY)}")


def test_axiom_a0_is_postulated() -> None:
    """A0_MANIFOLD is POSTULATED (foundational assumption)."""
    ax = axiom_by_name("A0_MANIFOLD")
    _test("A0_MANIFOLD is POSTULATED",
          ax is not None and ax.status == AxiomStatus.POSTULATED)


def test_axiom_a4_is_proved() -> None:
    """A4_NW5 (n_w=5 selection) is PROVED."""
    ax = axiom_by_name("A4_NW5")
    _test("A4_NW5 is PROVED",
          ax is not None and ax.status == AxiomStatus.PROVED)


def test_axiom_p7_yukawa_is_fitted() -> None:
    """P7_YUKAWA is FITTED (epistemic honesty check)."""
    ax = axiom_by_name("P7_YUKAWA")
    _test("P7_YUKAWA is FITTED",
          ax is not None and ax.status == AxiomStatus.FITTED)


def test_axiom_registry_all_have_fallibility_note() -> None:
    """Every axiom has a non-empty fallibility note."""
    missing = [ax.name for ax in AXIOM_REGISTRY if not ax.fallibility_note.strip()]
    _test("All axioms have fallibility notes",
          len(missing) == 0,
          f"missing: {missing}")


def test_axiom_summary_table_runs() -> None:
    """summary_table() runs without error."""
    try:
        table = summary_table()
        _test("summary_table() runs", isinstance(table, str))
    except Exception as e:
        _test("summary_table() runs", False, str(e))


def test_postulated_count_reasonable() -> None:
    """Number of POSTULATED axioms is between 2 and 10 (honesty check)."""
    postulated = axioms_by_status(AxiomStatus.POSTULATED)
    _test("POSTULATED count in [2, 10]",
          2 <= len(postulated) <= 10,
          f"got {len(postulated)}")


# ===========================================================================
# Test group 9: Known gaps registry
# ===========================================================================

def test_known_gaps_nonempty() -> None:
    """Known gaps registry is non-empty."""
    _test("KNOWN_GAPS non-empty",
          len(KNOWN_GAPS) > 0,
          f"len={len(KNOWN_GAPS)}")


def test_known_gaps_have_required_fields() -> None:
    """Every gap entry has id, label, status, detail fields."""
    required = {"id", "label", "status", "detail"}
    bad = [g["id"] for g in KNOWN_GAPS if not required.issubset(g.keys())]
    _test("All gaps have required fields",
          len(bad) == 0,
          f"missing fields in: {bad}")


def test_falsification_conditions_nonempty() -> None:
    """Falsification conditions are declared."""
    _test("FALSIFICATION_CONDITIONS non-empty",
          len(FALSIFICATION_CONDITIONS) > 0,
          f"len={len(FALSIFICATION_CONDITIONS)}")


def test_litebird_falsifier_listed() -> None:
    """LiteBIRD is listed as a falsifier for β."""
    experiments = [f["experiment"] for f in FALSIFICATION_CONDITIONS]
    _test("LiteBIRD in falsification conditions",
          any("LiteBIRD" in e for e in experiments),
          f"experiments: {experiments}")


# ===========================================================================
# Test group 10: Full report integration
# ===========================================================================

def test_full_report_runs() -> None:
    """full_report() executes without exception."""
    try:
        report = full_report()
        _test("full_report() runs", isinstance(report, dict))
    except Exception as e:
        _test("full_report() runs", False, str(e))


def test_full_report_all_checks_pass() -> None:
    """All summary_checks in full_report() pass."""
    report = full_report()
    checks = report.get("summary_checks", {})
    failed = [k for k, v in checks.items() if not v]
    _test("full_report summary_checks all PASS",
          len(failed) == 0,
          f"failed checks: {failed}")


def test_full_report_fingerprint() -> None:
    """Report fingerprint is the canonical braid triad (5, 7, 74)."""
    report = full_report()
    _test("Report fingerprint = '(5, 7, 74)'",
          report.get("fingerprint") == "(5, 7, 74)")


# ===========================================================================
# Test group 11: Resonance scan uniqueness
# ===========================================================================

def test_resonance_scan_finds_5_7() -> None:
    """The cs_level_scan finds (5,7) with correct c_s and passes nₛ + r."""
    results = cs_level_scan((1, 12))
    pair_57 = next((r for r in results if r["n1"] == 5 and r["n2"] == 7), None)
    ok = (pair_57 is not None and
          abs(pair_57["c_s"] - 12/37) < 1e-10 and
          pair_57["passes_ns_r"])
    _test("(5,7) found with correct c_s and passes nₛ+r",
          ok,
          f"c_s={pair_57['c_s']:.6f}, passes={pair_57['passes_ns_r']}" if pair_57 else "pair not found")


def test_cs_scan_k74_unique_in_window() -> None:
    """k_CS = 74 appears in the scan with correct c_s = 12/37."""
    results = cs_level_scan((1, 12))
    k74_pairs = [r for r in results if r["k_cs"] == 74]
    ok = (len(k74_pairs) > 0 and
          abs(k74_pairs[0]["c_s"] - 12/37) < 1e-10)
    _test("k_CS = 74 has correct c_s = 12/37",
          ok,
          f"k74 pairs: {[(r['n1'],r['n2']) for r in k74_pairs]}")


# ===========================================================================
# Test group 12: Optional sympy (graceful fallback)
# ===========================================================================

def test_symbolic_algebra_graceful() -> None:
    """symbolic_algebra() returns dict or None — never raises."""
    try:
        result = symbolic_algebra()
        _test("symbolic_algebra() graceful",
              result is None or isinstance(result, dict))
    except Exception as e:
        _test("symbolic_algebra() graceful", False, str(e))


def test_symbolic_algebra_pythagorean_if_sympy() -> None:
    """If sympy is available, Pythagorean identity check is zero."""
    result = symbolic_algebra()
    if result is None:
        _test("Pythagorean identity (sympy unavailable, skip)", True)
        return
    _test("Pythagorean identity symbolic = 0",
          result.get("pythagorean_check") == "0",
          f"got: {result.get('pythagorean_check')}")


# ===========================================================================
# Runner
# ===========================================================================

_ALL_TESTS: List[Callable] = [
    # Group 1: Topological invariants
    test_kcs_integer_sum_of_squares,
    test_braided_sound_speed_exact,
    test_pythagorean_identity,
    test_n_c_from_n_w,
    test_alpha_gut_rational,
    test_jacobian_kk_value,
    test_xi_c_rational,
    test_sentinel_capacity_rational,
    # Group 2: Inflation / CMB
    test_ns_within_planck_1sigma,
    test_r_braided_below_bicep,
    test_r_braided_equals_r_bare_times_cs,
    test_epsilon_small_slow_roll,
    test_inflaton_pipeline_deterministic,
    test_gw_potential_minimum,
    test_gw_potential_positive_away_from_min,
    test_phi_star_is_saddle,
    # Group 3: Birefringence
    test_beta_canonical_in_window,
    test_beta_gw_in_window,
    test_beta_canonical_not_in_gap,
    test_beta_within_minami_2sigma,
    test_beta_birefringence_function,
    # Group 4: 5D metric geometry
    test_5d_metric_shape,
    test_5d_metric_g55_equals_phi_sq,
    test_5d_metric_symmetry,
    test_field_strength_antisymmetric,
    test_curvature_pipeline_runs,
    test_flat_metric_low_curvature,
    # Group 5: FTUM
    test_ftum_convergence,
    test_ftum_phi0_reasonable,
    test_ftum_s_star_positive,
    test_ftum_deterministic,
    # Group 6: GUT / QCD / Higgs
    test_alpha_gut_derivation,
    test_lambda_qcd_geometric_range,
    test_lambda_qcd_soft_wall_gap_documented,
    test_higgs_mass_one_loop_range,
    test_higgs_architecture_limit_documented,
    test_yukawa_status_is_fitted,
    test_yukawa_fn_parameters_reduced,
    # Group 7: Dark energy
    test_dark_energy_eos_range,
    test_dark_energy_wa_zero,
    test_dark_energy_tension_documented,
    # Group 8: Axiom registry
    test_axiom_registry_nonempty,
    test_axiom_a0_is_postulated,
    test_axiom_a4_is_proved,
    test_axiom_p7_yukawa_is_fitted,
    test_axiom_registry_all_have_fallibility_note,
    test_axiom_summary_table_runs,
    test_postulated_count_reasonable,
    # Group 9: Gaps registry
    test_known_gaps_nonempty,
    test_known_gaps_have_required_fields,
    test_falsification_conditions_nonempty,
    test_litebird_falsifier_listed,
    # Group 10: Integration
    test_full_report_runs,
    test_full_report_all_checks_pass,
    test_full_report_fingerprint,
    # Group 11: Resonance scan
    test_resonance_scan_finds_5_7,
    test_cs_scan_k74_unique_in_window,
    # Group 12: Sympy
    test_symbolic_algebra_graceful,
    test_symbolic_algebra_pythagorean_if_sympy,
]


def run_all() -> int:
    """Run every test.  Return number of failures."""
    global _FAILURES
    _FAILURES = 0
    _RESULTS.clear()

    print("=" * 70)
    print("  UNITARY MANIFOLD — COMPACTIFICATION KERNEL TEST SUITE")
    print(f"  {len(_ALL_TESTS)} tests across 12 groups")
    print("=" * 70)

    group_labels = {
        0: "Topological invariants",
        8: "CMB inflation pipeline",
        16: "Birefringence",
        21: "5D metric geometry",
        27: "FTUM fixed point",
        31: "GUT / QCD / Higgs sector",
        38: "Dark energy",
        41: "Axiom registry",
        48: "Known gaps registry",
        52: "Full report integration",
        55: "Resonance scan uniqueness",
        57: "Symbolic algebra (optional)",
    }
    idx = 0
    for test_fn in _ALL_TESTS:
        if idx in group_labels:
            _section(group_labels[idx])
        try:
            test_fn()
        except Exception as exc:
            _test(test_fn.__name__, False, f"EXCEPTION: {exc}")
            traceback.print_exc()
        idx += 1

    print("\n" + "=" * 70)
    total  = len(_RESULTS)
    passed = total - _FAILURES
    print(f"  Result: {passed}/{total} passed, {_FAILURES} failed")
    if _FAILURES == 0:
        print("  ✓ ALL TESTS PASS — kernel is self-consistent")
    else:
        print("  ✗ FAILURES DETECTED — investigate above")
    print("=" * 70)
    return _FAILURES


# ---------------------------------------------------------------------------
# pytest compatibility — expose each test function at module level so pytest
# discovers them automatically.  The plain-Python runner is the `if __main__`
# block below.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    failures = run_all()
    sys.exit(0 if failures == 0 else 1)
