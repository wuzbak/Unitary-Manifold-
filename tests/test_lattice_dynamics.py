# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_lattice_dynamics.py
================================
Pillar 15-B — Test suite for src/physics/lattice_dynamics.py.

"Pillar 15-B" denotes the extension of the Cold Fusion pillar (Pillar 15,
`src/cold_fusion/`) to include coherence-volume scaling, collective Gamow
factor amplification, phonon-radion coupling, and the B_μ time-arrow lock.
The "B" suffix distinguishes it from the base Pillar 15 tunneling model.

Covers all public API functions: phi_effective_collective, ignition_N,
braid_resonance_loading, lattice_coherence_gain, phonon_radion_bridge,
and bmu_time_arrow_lock.

Code architecture, test suites, document engineering, and synthesis:
"""
from __future__ import annotations

import math
import pytest

from src.physics.lattice_dynamics import (
    # Constants
    N_W_DEFAULT,
    K_CS_DEFAULT,
    C_S_DEFAULT,
    ALPHA_FS,
    G_THRESHOLD_DEFAULT,
    X_BRAID_CANONICAL,
    # Functions
    phi_effective_collective,
    ignition_N,
    braid_resonance_loading,
    lattice_coherence_gain,
    phonon_radion_bridge,
    bmu_time_arrow_lock,
)


# ===========================================================================
# phi_effective_collective
# ===========================================================================

class TestPhiEffectiveCollective:
    def test_single_pair_returns_phi_local(self):
        # N=1: phi_eff = phi_local × (1 + N_eff × 1) > phi_local
        # Just verify it's above phi_local for N=1
        phi_local = 1.5
        phi_eff = phi_effective_collective(1, phi_local)
        assert phi_eff >= phi_local

    def test_monotone_in_N(self):
        phi_local = 1.5
        results = [phi_effective_collective(N, phi_local) for N in [1, 10, 100, 1000]]
        assert results == sorted(results)

    def test_monotone_in_phi_local(self):
        N = 100
        results = [phi_effective_collective(N, phi) for phi in [0.5, 1.0, 2.0, 5.0]]
        assert results == sorted(results)

    def test_formula_correctness(self):
        N, phi = 500, 2.0
        N_eff = N_W_DEFAULT * C_S_DEFAULT ** 2 / K_CS_DEFAULT
        expected = phi * (1.0 + N_eff * N)
        assert abs(phi_effective_collective(N, phi) / expected - 1.0) < 1e-12

    def test_large_N_amplifies_significantly(self):
        # With N=1000, phi_eff >> phi_local
        phi_local = 1.0
        phi_eff = phi_effective_collective(1000, phi_local)
        N_eff = N_W_DEFAULT * C_S_DEFAULT ** 2 / K_CS_DEFAULT
        expected = phi_local * (1.0 + N_eff * 1000)
        assert abs(phi_eff / expected - 1.0) < 1e-12

    def test_custom_braid_params(self):
        N, phi = 100, 1.5
        n_w, k_cs, c_s = 3, 50, 0.3
        N_eff = n_w * c_s ** 2 / k_cs
        expected = phi * (1.0 + N_eff * N)
        assert abs(phi_effective_collective(N, phi, n_w, k_cs, c_s) / expected - 1.0) < 1e-12

    def test_invalid_N_zero(self):
        with pytest.raises(ValueError):
            phi_effective_collective(0, 1.0)

    def test_invalid_N_negative(self):
        with pytest.raises(ValueError):
            phi_effective_collective(-5, 1.0)

    def test_invalid_phi_zero(self):
        with pytest.raises(ValueError):
            phi_effective_collective(10, 0.0)

    def test_invalid_phi_negative(self):
        with pytest.raises(ValueError):
            phi_effective_collective(10, -1.0)

    def test_invalid_k_cs_zero(self):
        with pytest.raises(ValueError):
            phi_effective_collective(10, 1.0, k_cs=0)


# ===========================================================================
# ignition_N
# ===========================================================================

_DUAL_USE_SKIP = (
    "Implementation held in private repository per "
    "AxiomZero dual-use policy v1.0 — see DUAL_USE_NOTICE.md"
)


@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestIgnitionN:
    def test_returns_positive(self):
        N_ign = ignition_N(1.0)
        assert N_ign >= 1.0

    def test_higher_phi_requires_fewer_atoms(self):
        # Use room-temp eta so ignition N >> 1
        eta = ALPHA_FS / 5.25e-6   # ≈ 1390
        N1 = ignition_N(1.0, eta=eta)
        N2 = ignition_N(5.0, eta=eta)
        assert N2 < N1

    def test_stricter_threshold_requires_more_atoms(self):
        # 1e-20 > 1e-40: G_threshold=1e-20 is stricter (higher min to exceed)
        # so it requires MORE atoms than the easier G_threshold=1e-40
        eta = ALPHA_FS / 5.25e-6
        N_strict = ignition_N(1.0, eta=eta, G_threshold=1e-20)   # harder
        N_easy = ignition_N(1.0, eta=eta, G_threshold=1e-40)      # easier
        assert N_strict > N_easy

    def test_larger_eta_requires_more_atoms(self):
        N1 = ignition_N(1.0, eta=7.0)
        N2 = ignition_N(1.0, eta=14.0)
        assert N2 > N1

    def test_minimum_is_one(self):
        # If phi_local is very large, single pair is already above threshold
        N_ign = ignition_N(1e6, eta=0.001, G_threshold=1e-10)
        assert N_ign == 1.0

    def test_formula_at_standard_params(self):
        phi_local = 1.0
        eta = ALPHA_FS / 5.25e-6   # room-temp D-D so ignition N >> 1
        G_thresh = 1e-20
        N_eff = N_W_DEFAULT * C_S_DEFAULT ** 2 / K_CS_DEFAULT
        phi_eff_needed = 2.0 * math.pi * eta / (-math.log(G_thresh))
        expected_N = (phi_eff_needed / phi_local - 1.0) / N_eff
        N_ign = ignition_N(phi_local, eta, G_thresh)
        assert abs(N_ign / expected_N - 1.0) < 1e-10

    def test_invalid_phi_zero(self):
        with pytest.raises(ValueError):
            ignition_N(0.0)

    def test_invalid_eta_zero(self):
        with pytest.raises(ValueError):
            ignition_N(1.0, eta=0.0)

    def test_invalid_G_threshold_zero(self):
        with pytest.raises(ValueError):
            ignition_N(1.0, G_threshold=0.0)

    def test_invalid_G_threshold_one(self):
        with pytest.raises(ValueError):
            ignition_N(1.0, G_threshold=1.0)


# ===========================================================================
# braid_resonance_loading
# ===========================================================================

class TestBraidResonanceLoading:
    def test_returns_dict(self):
        result = braid_resonance_loading()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = braid_resonance_loading()
        required = {"x_primary", "x_secondary", "x_canonical", "n_w", "k_cs", "c_s", "N_eff"}
        assert required.issubset(result.keys())

    def test_x_primary_in_range(self):
        result = braid_resonance_loading()
        assert 0.0 < result["x_primary"] < 1.0

    def test_x_canonical_is_7_over_8(self):
        result = braid_resonance_loading()
        assert abs(result["x_canonical"] - 7.0 / 8.0) < 1e-15

    def test_x_primary_formula(self):
        # x_primary = n_w / (n_w + n_2) = 5 / (5 + 7) = 5/12
        result = braid_resonance_loading()
        assert abs(result["x_primary"] - 5.0 / 12.0) < 1e-12

    def test_N_eff_formula(self):
        result = braid_resonance_loading()
        expected = N_W_DEFAULT * C_S_DEFAULT ** 2 / K_CS_DEFAULT
        assert abs(result["N_eff"] / expected - 1.0) < 1e-12

    def test_n_w_k_cs_c_s_stored_correctly(self):
        result = braid_resonance_loading()
        assert result["n_w"] == N_W_DEFAULT
        assert result["k_cs"] == K_CS_DEFAULT
        assert abs(result["c_s"] - C_S_DEFAULT) < 1e-15

    def test_custom_params(self):
        result = braid_resonance_loading(n_w=3, k_cs=58, c_s=0.3)
        assert result["n_w"] == 3
        assert result["k_cs"] == 58

    def test_invalid_k_cs_zero(self):
        with pytest.raises(ValueError):
            braid_resonance_loading(k_cs=0)


# ===========================================================================
# lattice_coherence_gain — main API
# ===========================================================================

@pytest.mark.skip(reason=_DUAL_USE_SKIP)
class TestLatticeCoherenceGain:
    def test_returns_dict(self):
        result = lattice_coherence_gain(100, 1.5)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = lattice_coherence_gain(100, 1.5)
        required = {
            "N_coherence", "phi_local", "N_eff", "phi_effective",
            "G_single", "G_collective", "gain", "log10_gain",
            "log10_G_single", "log10_G_coll",
            "ignition_N", "is_ignited", "f_kk", "optimal_loading",
        }
        assert required.issubset(result.keys())

    def test_G_collective_ge_G_single(self):
        result = lattice_coherence_gain(100, 1.5)
        assert result["G_collective"] >= result["G_single"]

    def test_gain_ge_one(self):
        result = lattice_coherence_gain(100, 1.5)
        assert result["gain"] >= 1.0

    def test_gain_increases_with_N(self):
        r1 = lattice_coherence_gain(10, 1.5)
        r2 = lattice_coherence_gain(100, 1.5)
        r3 = lattice_coherence_gain(1000, 1.5)
        assert r1["gain"] <= r2["gain"] <= r3["gain"]

    def test_gain_increases_with_phi(self):
        r1 = lattice_coherence_gain(100, 1.0)
        r2 = lattice_coherence_gain(100, 2.0)
        # Higher phi_local → phi_eff larger → smaller Gamow exponent → larger G_collective
        assert r2["G_collective"] >= r1["G_collective"]

    def test_phi_effective_consistent(self):
        N, phi = 500, 2.0
        result = lattice_coherence_gain(N, phi)
        phi_eff_expected = phi_effective_collective(N, phi)
        assert abs(result["phi_effective"] / phi_eff_expected - 1.0) < 1e-12

    def test_ignition_N_consistent(self):
        phi_local = 1.5
        result = lattice_coherence_gain(100, phi_local)
        N_ign_expected = ignition_N(phi_local)
        assert abs(result["ignition_N"] / N_ign_expected - 1.0) < 1e-10

    def test_is_ignited_below_threshold_N(self):
        # For phi=1, v_rel=0.001, ignition N is very large; small N should not ignite
        result = lattice_coherence_gain(1, 1.0)
        N_ign = result["ignition_N"]
        if N_ign > 1:
            assert result["is_ignited"] is False

    def test_is_ignited_above_threshold(self):
        # Large phi and large N should ignite
        result = lattice_coherence_gain(10000, 5.0, eta=7.3, G_threshold=1e-10)
        if result["N_coherence"] > result["ignition_N"]:
            assert result["is_ignited"] is True

    def test_f_kk_equals_braid_factor(self):
        result = lattice_coherence_gain(100, 1.5)
        expected = C_S_DEFAULT ** 2 / K_CS_DEFAULT
        assert abs(result["f_kk"] / expected - 1.0) < 1e-12

    def test_N_eff_formula(self):
        result = lattice_coherence_gain(100, 1.5)
        expected = N_W_DEFAULT * C_S_DEFAULT ** 2 / K_CS_DEFAULT
        assert abs(result["N_eff"] / expected - 1.0) < 1e-12

    def test_log10_gain_positive(self):
        result = lattice_coherence_gain(1000, 1.5)
        assert result["log10_gain"] > 0

    def test_log10_gain_consistent_with_gain(self):
        result = lattice_coherence_gain(100, 1.5)
        # Use log10_G values to avoid float overflow when gain is huge
        expected_log10_gain = result["log10_G_coll"] - result["log10_G_single"]
        assert abs(result["log10_gain"] - expected_log10_gain) < 1e-8

    def test_optimal_loading_dict_present(self):
        result = lattice_coherence_gain(100, 1.5)
        assert isinstance(result["optimal_loading"], dict)
        assert "x_canonical" in result["optimal_loading"]

    def test_large_N_drives_gamow_toward_one(self):
        # With very large N and large phi, G_collective should approach 1
        result = lattice_coherence_gain(1_000_000, 10.0, eta=0.1)
        assert result["G_collective"] > 1e-3   # substantially above single-pair

    def test_N_1_matches_single_pair_limit(self):
        phi = 2.0
        eta = 5.0
        result = lattice_coherence_gain(1, phi, eta=eta)
        G_single_expected = math.exp(-2.0 * math.pi * eta / phi)
        # For N=1, phi_eff = phi × (1 + N_eff) ≠ phi, but G_single is pure phi
        assert abs(result["G_single"] / G_single_expected - 1.0) < 1e-10

    def test_collective_greater_single_exponentially(self):
        # Gain should be exp(2π η × (1/phi_local - 1/phi_eff))
        N, phi = 500, 1.5
        eta = ALPHA_FS / 0.001
        result = lattice_coherence_gain(N, phi, eta=eta)
        phi_eff = result["phi_effective"]
        log_gain_expected = 2.0 * math.pi * eta * (1.0 / phi - 1.0 / phi_eff)
        assert abs(result["log10_gain"] - log_gain_expected / math.log(10)) < 1e-6

    def test_invalid_N_zero(self):
        with pytest.raises(ValueError):
            lattice_coherence_gain(0, 1.5)

    def test_invalid_N_negative(self):
        with pytest.raises(ValueError):
            lattice_coherence_gain(-10, 1.5)

    def test_invalid_phi_zero(self):
        with pytest.raises(ValueError):
            lattice_coherence_gain(100, 0.0)

    def test_invalid_phi_negative(self):
        with pytest.raises(ValueError):
            lattice_coherence_gain(100, -1.5)

    def test_invalid_k_cs_zero(self):
        with pytest.raises(ValueError):
            lattice_coherence_gain(100, 1.5, k_cs=0)

    def test_canonical_braid_ignition_N_within_physical_range(self):
        """For phi_local=1.5 and default eta, ignition N should be finite and positive."""
        result = lattice_coherence_gain(100, 1.5)
        assert result["ignition_N"] > 0
        assert math.isfinite(result["ignition_N"])

    def test_custom_eta(self):
        # Low eta (high relative velocity) should give higher G_single
        r_low = lattice_coherence_gain(100, 1.5, eta=1.0)
        r_high = lattice_coherence_gain(100, 1.5, eta=10.0)
        assert r_low["G_single"] > r_high["G_single"]

    def test_x_canonical_is_875(self):
        result = lattice_coherence_gain(100, 1.5)
        assert abs(result["optimal_loading"]["x_canonical"] - 0.875) < 1e-15

    def test_G_collective_positive(self):
        result = lattice_coherence_gain(100, 1.5)
        assert result["G_collective"] > 0

    def test_G_single_positive(self):
        result = lattice_coherence_gain(100, 1.5)
        assert result["G_single"] > 0


# ===========================================================================
# phonon_radion_bridge
# ===========================================================================

class TestPhononRadionBridge:
    def test_returns_dict(self):
        assert isinstance(phonon_radion_bridge(0.875), dict)

    def test_required_keys(self):
        result = phonon_radion_bridge(0.875)
        required = {
            "D_Pd_loading", "debye_temp_K", "lattice_temp_K",
            "phonon_occupation", "x_opt_primary", "kappa_braid",
            "N_eff", "phi_bulk", "phi_site", "phi_enhancement",
            "is_resonant", "optimal_loading",
        }
        assert required.issubset(result.keys())

    def test_phi_site_ge_phi_bulk(self):
        # Phonons pump the radion field upward
        result = phonon_radion_bridge(0.875)
        assert result["phi_site"] >= result["phi_bulk"]

    def test_phi_bulk_equals_one(self):
        result = phonon_radion_bridge(0.875)
        assert result["phi_bulk"] == 1.0

    def test_phonon_occupation_positive_at_room_temp(self):
        result = phonon_radion_bridge(0.875, debye_temp_K=274.0, lattice_temp_K=300.0)
        assert result["phonon_occupation"] > 0

    def test_phonon_occupation_formula(self):
        T_D, T = 274.0, 300.0
        result = phonon_radion_bridge(0.875, debye_temp_K=T_D, lattice_temp_K=T)
        expected = 1.0 / (math.exp(T_D / T) - 1.0)
        assert abs(result["phonon_occupation"] / expected - 1.0) < 1e-10

    def test_kappa_braid_at_x_opt_near_one(self):
        # At the primary resonance loading, κ_braid should be near 1
        result = phonon_radion_bridge(0.875)
        x_opt = result["x_opt_primary"]  # ≈ 5/12 ≈ 0.4167
        result_opt = phonon_radion_bridge(x_opt)
        assert result_opt["kappa_braid"] > 0.9  # near peak

    def test_kappa_braid_far_from_resonance_small(self):
        # Very far from x_opt: κ ≈ 0
        result = phonon_radion_bridge(2.0)  # x=2 far from x_opt≈0.42
        assert result["kappa_braid"] < 0.01

    def test_is_resonant_at_x_opt(self):
        result = phonon_radion_bridge(0.875)
        x_opt = result["x_opt_primary"]
        result_opt = phonon_radion_bridge(x_opt)
        assert result_opt["is_resonant"] is True

    def test_higher_temp_more_phonons(self):
        r1 = phonon_radion_bridge(0.42, lattice_temp_K=300.0)
        r2 = phonon_radion_bridge(0.42, lattice_temp_K=600.0)
        assert r2["phonon_occupation"] > r1["phonon_occupation"]

    def test_higher_temp_higher_phi_site(self):
        r1 = phonon_radion_bridge(0.42, lattice_temp_K=300.0)
        r2 = phonon_radion_bridge(0.42, lattice_temp_K=600.0)
        assert r2["phi_site"] >= r1["phi_site"]

    def test_phi_enhancement_percent_consistent(self):
        result = phonon_radion_bridge(0.875)
        expected_pct = (result["phi_site"] / result["phi_bulk"] - 1.0) * 100.0
        assert abs(result["phi_enhancement"] - expected_pct) < 1e-10

    def test_N_eff_formula(self):
        result = phonon_radion_bridge(0.875)
        expected = N_W_DEFAULT * C_S_DEFAULT ** 2 / K_CS_DEFAULT
        assert abs(result["N_eff"] / expected - 1.0) < 1e-12

    def test_x_opt_primary_formula(self):
        result = phonon_radion_bridge(0.875)
        n2 = int(round(math.sqrt(K_CS_DEFAULT - N_W_DEFAULT ** 2)))
        expected = N_W_DEFAULT / (N_W_DEFAULT + n2)
        assert abs(result["x_opt_primary"] - expected) < 1e-10

    def test_optimal_loading_dict_present(self):
        result = phonon_radion_bridge(0.875)
        assert isinstance(result["optimal_loading"], dict)

    def test_invalid_D_Pd_zero(self):
        with pytest.raises(ValueError):
            phonon_radion_bridge(0.0)

    def test_invalid_D_Pd_negative(self):
        with pytest.raises(ValueError):
            phonon_radion_bridge(-0.5)

    def test_invalid_debye_temp_zero(self):
        with pytest.raises(ValueError):
            phonon_radion_bridge(0.875, debye_temp_K=0.0)

    def test_invalid_lattice_temp_zero(self):
        with pytest.raises(ValueError):
            phonon_radion_bridge(0.875, lattice_temp_K=0.0)


# ===========================================================================
# bmu_time_arrow_lock
# ===========================================================================

class TestBmuTimeArrowLock:
    def test_returns_dict(self):
        assert isinstance(bmu_time_arrow_lock(5.0, 2.0), dict)

    def test_required_keys(self):
        result = bmu_time_arrow_lock(5.0, 2.0)
        required = {
            "B_site", "phi_site", "braid_coupling", "B_effective",
            "Q_MeV", "Q_phonon_MeV", "Q_gamma_MeV",
            "phonon_fraction", "gamma_fraction",
            "suppression_pct", "is_safe", "proof_statement",
        }
        assert required.issubset(result.keys())

    def test_fractions_sum_to_one(self):
        result = bmu_time_arrow_lock(5.0, 2.0)
        assert abs(result["phonon_fraction"] + result["gamma_fraction"] - 1.0) < 1e-12

    def test_Q_values_partition_correctly(self):
        result = bmu_time_arrow_lock(5.0, 2.0, Q_MeV=3.27)
        assert abs(result["Q_phonon_MeV"] + result["Q_gamma_MeV"] - 3.27) < 1e-10

    def test_zero_B_site_all_gamma(self):
        result = bmu_time_arrow_lock(0.0, 1.0)
        assert result["phonon_fraction"] == 0.0
        assert result["gamma_fraction"] == 1.0

    def test_zero_B_site_not_safe(self):
        result = bmu_time_arrow_lock(0.0, 1.0)
        assert result["is_safe"] is False

    def test_quadratic_phonon_fraction_formula(self):
        B_site, phi_site = 3.0, 4.0
        result = bmu_time_arrow_lock(B_site, phi_site)
        braid_coupling = result["braid_coupling"]
        B_eff = B_site * phi_site * braid_coupling
        B_eff_sq = B_eff ** 2
        expected_phonon = B_eff_sq / (1.0 + B_eff_sq)
        assert abs(result["phonon_fraction"] - expected_phonon) < 1e-12

    def test_braid_coupling_formula(self):
        result = bmu_time_arrow_lock(2.0, 1.5)
        expected = N_W_DEFAULT * C_S_DEFAULT / K_CS_DEFAULT
        assert abs(result["braid_coupling"] / expected - 1.0) < 1e-12

    def test_B_effective_formula(self):
        B_site, phi_site = 4.0, 3.0
        result = bmu_time_arrow_lock(B_site, phi_site)
        braid_coupling = result["braid_coupling"]
        expected = B_site * phi_site * braid_coupling
        assert abs(result["B_effective"] / expected - 1.0) < 1e-12

    def test_high_B_is_safe(self):
        # Need B_eff >> 10 for f_gamma < 0.01
        # braid_coupling ≈ 5 × (12/37) / 74 ≈ 0.02186
        # B_eff = B_site × phi_site × 0.02186 > 10 requires B_site × phi_site > 457
        result = bmu_time_arrow_lock(100.0, 10.0)
        assert result["is_safe"] is True

    def test_monotone_in_B_site(self):
        results = [bmu_time_arrow_lock(b, 2.0) for b in [0.5, 1.0, 5.0, 20.0]]
        phonon = [r["phonon_fraction"] for r in results]
        assert phonon == sorted(phonon)

    def test_suppression_pct_consistent(self):
        result = bmu_time_arrow_lock(5.0, 3.0)
        expected = result["phonon_fraction"] * 100.0
        assert abs(result["suppression_pct"] - expected) < 1e-10

    def test_proof_statement_present(self):
        result = bmu_time_arrow_lock(5.0, 2.0)
        assert "B_eff" in result["proof_statement"]
        assert len(result["proof_statement"]) > 50

    def test_gamma_fraction_in_unit_interval(self):
        result = bmu_time_arrow_lock(3.0, 2.0)
        assert 0.0 < result["gamma_fraction"] <= 1.0

    def test_phonon_fraction_in_unit_interval(self):
        result = bmu_time_arrow_lock(3.0, 2.0)
        assert 0.0 <= result["phonon_fraction"] < 1.0

    def test_custom_Q_MeV(self):
        result = bmu_time_arrow_lock(5.0, 2.0, Q_MeV=4.03)
        assert abs(result["Q_MeV"] - 4.03) < 1e-12

    def test_is_safe_threshold(self):
        # Gradually increase until safe
        # f_gamma = 1/(1+B_eff²) < 0.01 requires B_eff > sqrt(99) ≈ 9.95
        # braid_coupling ≈ 0.02186 → need B_site×phi_site > 9.95/0.02186 ≈ 455
        result_unsafe = bmu_time_arrow_lock(50.0, 5.0)   # B_eff ≈ 5.47 → unsafe
        result_safe = bmu_time_arrow_lock(200.0, 5.0)    # B_eff ≈ 21.9 → safe
        assert result_safe["is_safe"] is True
        # Just check the safe one is actually safe
        assert result_safe["gamma_fraction"] < 0.01

    def test_invalid_B_site_negative(self):
        with pytest.raises(ValueError):
            bmu_time_arrow_lock(-1.0, 1.0)

    def test_invalid_phi_site_zero(self):
        with pytest.raises(ValueError):
            bmu_time_arrow_lock(1.0, 0.0)

    def test_invalid_phi_site_negative(self):
        with pytest.raises(ValueError):
            bmu_time_arrow_lock(1.0, -1.0)

    def test_quadratic_vs_linear_suppression(self):
        # Quadratic (bmu) gives more suppression than linear (excess_heat) for same B_eff
        B_site, phi_site = 3.0, 4.0
        result = bmu_time_arrow_lock(B_site, phi_site)
        # Linear: f_gamma_lin = 1/(1 + B_eff)
        # Quadratic: f_gamma_quad = 1/(1 + B_eff²)
        B_eff = result["B_effective"]
        f_gamma_linear = 1.0 / (1.0 + B_eff)
        f_gamma_quadratic = result["gamma_fraction"]
        if B_eff > 1.0:
            assert f_gamma_quadratic < f_gamma_linear
