# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_triple_point.py
==============================
Tests for the Lean ↔ JAX ↔ Z3 Triple-Point pipeline.

Every test exercises the full cross-layer contract so a drift between
any two layers shows up as a test failure before it reaches CI.
"""

from __future__ import annotations

import pytest
import numpy as np
pytest.importorskip("jax")
pytest.importorskip("z3")
from src.core.triple_point import (
    lean_certificate,
    jax_evaluate,
    z3_bounds_check,
    z3_gradient_signs_check,
    triple_point_certificate,
    run_braid_resonance_scan,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    SIGMA_WINDOW,
    PHI0_CANONICAL,
)

# Canonical UM φ₀ that gives n_s = 0.9635 via formula 1 − 8·N_w/φ₀²
# PHI0_CANONICAL ≈ 33.104 = sqrt(8·5 / (1 − 0.9635))
N_W = 5


# ===========================================================================
# Layer 1 — Lean 4
# ===========================================================================

class TestLeanCertificate:
    def test_returns_dict(self):
        r = lean_certificate()
        assert isinstance(r, dict)

    def test_all_verified_true(self):
        r = lean_certificate()
        assert r["all_verified"] is True

    def test_status_pass(self):
        assert lean_certificate()["status"] == "PASS"

    def test_three_theorems(self):
        r = lean_certificate()
        assert len(r["theorems"]) == 3

    def test_theorem_ids_present(self):
        r = lean_certificate()
        ids = {t["theorem_id"] for t in r["theorems"]}
        assert "T1-NS-EQ" in ids
        assert "T1-R-EQ" in ids
        assert "T1-WKK-EQ" in ids

    def test_each_theorem_verified(self):
        for t in lean_certificate()["theorems"]:
            assert t["verified"] is True, f"{t['theorem_id']} not verified"

    def test_lean_file_key_present(self):
        assert "lean_file" in lean_certificate()

    def test_mathlib_flag(self):
        assert lean_certificate()["mathlib"] is True


# ===========================================================================
# Layer 2 — JAX
# ===========================================================================

class TestJaxEvaluate:
    def test_returns_dict(self):
        assert isinstance(jax_evaluate(PHI0_CANONICAL), dict)

    def test_ns_is_float(self):
        r = jax_evaluate(PHI0_CANONICAL)
        assert isinstance(r["n_s"], float)

    def test_ns_formula_matches_lean(self):
        """The JAX formula 1 - 8*n_w/phi0^2 must equal T1-NS-EQ output."""
        ns_jax = jax_evaluate(PHI0_CANONICAL, N_W)["n_s"]
        ns_expected = 1.0 - 8.0 * N_W / PHI0_CANONICAL ** 2
        assert abs(ns_jax - ns_expected) < 1e-9

    def test_gradient_phi0_positive(self):
        """dn_s/dφ₀ > 0: larger φ₀ moves n_s toward scale-invariance."""
        r = jax_evaluate(PHI0_CANONICAL)
        assert r["dn_s_dphi0"] > 0

    def test_gradient_nw_negative(self):
        """dn_s/dn_w < 0: more winding reduces the spectral index."""
        r = jax_evaluate(PHI0_CANONICAL)
        assert r["dn_s_dnw"] < 0

    def test_gradient_phi0_analytic(self):
        """dn_s/dφ₀ = 16·N_w / φ₀³ analytically."""
        r = jax_evaluate(PHI0_CANONICAL, N_W)
        expected = 16.0 * N_W / PHI0_CANONICAL ** 3
        assert abs(r["dn_s_dphi0"] - expected) < 1e-6

    def test_gradient_nw_analytic(self):
        """dn_s/dn_w = -8 / φ₀² analytically."""
        r = jax_evaluate(PHI0_CANONICAL, N_W)
        expected = -8.0 / PHI0_CANONICAL ** 2
        assert abs(r["dn_s_dnw"] - expected) < 1e-6

    def test_jax_version_present(self):
        assert len(jax_evaluate(PHI0_CANONICAL)["jax_version"]) > 0

    def test_phi0_echoed(self):
        r = jax_evaluate(PHI0_CANONICAL)
        assert r["phi0"] == PHI0_CANONICAL

    def test_different_phi0_gives_different_ns(self):
        ns1 = jax_evaluate(10.0)["n_s"]
        ns2 = jax_evaluate(20.0)["n_s"]
        assert ns1 != ns2


# ===========================================================================
# Layer 3 — Z3
# ===========================================================================

class TestZ3BoundsCheck:
    def test_ns_in_2sigma_passes(self):
        """Planck central value is trivially in-band."""
        r = z3_bounds_check(PLANCK_NS_CENTRAL, sigma_window=2)
        assert r["status"] == "PASS"
        assert r["in_band_proven"] is True

    def test_ns_far_out_fails(self):
        """A wildly wrong n_s should fail the Z3 check."""
        r = z3_bounds_check(0.5, sigma_window=2)
        assert r["status"] == "FAIL"
        assert r["in_band_proven"] is False

    def test_bounds_use_sigma_window(self):
        r = z3_bounds_check(PLANCK_NS_CENTRAL, sigma_window=3)
        expected_lower = PLANCK_NS_CENTRAL - 3 * PLANCK_NS_SIGMA
        assert abs(r["lower_bound"] - expected_lower) < 1e-12

    def test_um_ns_in_2sigma(self):
        """UM prediction 0.9635 must survive the 2σ Planck check."""
        um_ns = 0.9635  # from src.core.jax_backend.N_S
        r = z3_bounds_check(um_ns, sigma_window=2)
        # 0.9635 vs 0.9649 ± 0.0042: pull = -0.33σ — well within 2σ
        assert r["status"] == "PASS"

    def test_returns_z3_result_key(self):
        r = z3_bounds_check(PLANCK_NS_CENTRAL)
        assert "z3_result" in r


class TestZ3GradientSigns:
    def test_correct_signs_pass(self):
        r = z3_gradient_signs_check(dns_dphi0=0.01, dns_dnw=-0.03)
        assert r["status"] == "PASS"

    def test_wrong_phi0_sign_fails(self):
        r = z3_gradient_signs_check(dns_dphi0=-0.01, dns_dnw=-0.03)
        assert r["status"] == "FAIL"

    def test_wrong_nw_sign_fails(self):
        r = z3_gradient_signs_check(dns_dphi0=0.01, dns_dnw=0.03)
        assert r["status"] == "FAIL"

    def test_canonical_gradients_pass(self):
        jax_r = jax_evaluate(PHI0_CANONICAL)
        r = z3_gradient_signs_check(jax_r["dn_s_dphi0"], jax_r["dn_s_dnw"])
        assert r["status"] == "PASS"


# ===========================================================================
# Full Triple-Point certificate
# ===========================================================================

class TestTriplePointCertificate:
    def setup_method(self):
        self.cert = triple_point_certificate(PHI0_CANONICAL)

    def test_returns_dict(self):
        assert isinstance(self.cert, dict)

    def test_has_all_layers(self):
        for key in ("lean_layer", "jax_layer", "z3_bounds", "z3_gradients"):
            assert key in self.cert, f"Missing key: {key}"

    def test_overall_pass(self):
        assert self.cert["overall_pass"] is True

    def test_braid_invariant_present(self):
        bi = self.cert["braid_invariant"]
        assert bi["n_w"] == 5
        assert bi["k_cs"] == 74
        assert bi["k_cs_decomposition"] == "5² + 7² = 74"

    def test_braid_invariant_lean_proved(self):
        assert self.cert["braid_invariant"]["lean_proved"] is True

    def test_timestamp_is_string(self):
        assert isinstance(self.cert["timestamp"], str)
        assert self.cert["timestamp"].endswith("Z")

    def test_lean_layer_pass(self):
        assert self.cert["lean_layer"]["status"] == "PASS"

    def test_z3_bounds_pass(self):
        assert self.cert["z3_bounds"]["status"] == "PASS"

    def test_z3_gradients_pass(self):
        assert self.cert["z3_gradients"]["status"] == "PASS"

    def test_phi0_echoed(self):
        assert self.cert["phi0"] == PHI0_CANONICAL

    def test_jax_ns_agrees_with_formula(self):
        ns = self.cert["jax_layer"]["n_s"]
        expected = 1.0 - 8.0 * N_W / PHI0_CANONICAL ** 2
        assert abs(ns - expected) < 1e-9


# ===========================================================================
# Braid resonance scan (JAX vmap)
# ===========================================================================

class TestBraidResonanceScan:
    def test_returns_dict(self):
        r = run_braid_resonance_scan([10.0, 13.66, 20.0])
        assert isinstance(r, dict)

    def test_phi0_values_echoed(self):
        phi0s = [10.0, 13.0, 13.66, 14.0, 20.0]
        r = run_braid_resonance_scan(phi0s)
        assert r["phi0_values"] == phi0s

    def test_ns_values_count_matches(self):
        phi0s = [10.0, 13.0, 13.66, 14.0, 20.0]
        r = run_braid_resonance_scan(phi0s)
        assert len(r["ns_values"]) == len(phi0s)

    def test_in_band_mask_is_list_of_bool(self):
        r = run_braid_resonance_scan([10.0, 13.66, 20.0])
        assert all(isinstance(v, bool) for v in r["in_band_mask"])

    def test_canonical_phi0_is_in_band(self):
        # The canonical φ₀ ≈ 33.104 gives n_s ≈ 0.9635, inside 2σ of Planck
        r = run_braid_resonance_scan([PHI0_CANONICAL])
        assert r["in_band_mask"][0] is True

    def test_bad_phi0_is_out_of_band(self):
        # φ₀ = 5 gives n_s = 1 - 8*5/25 = -0.6 — wildly out of band
        r = run_braid_resonance_scan([5.0])
        assert r["in_band_mask"][0] is False

    def test_n_inband_is_int(self):
        r = run_braid_resonance_scan([10.0, 13.66, 20.0])
        assert isinstance(r["n_inband"], int)

    def test_jax_version_present(self):
        r = run_braid_resonance_scan([13.66])
        assert "jax_version" in r
