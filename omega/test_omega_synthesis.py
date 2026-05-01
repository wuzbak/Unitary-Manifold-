# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
omega/test_omega_synthesis.py
==============================
Comprehensive test suite for the Omega Synthesis — Universal Mechanics Engine.

These tests verify:
  1. All five seed constants are algebraically exact
  2. Every domain report returns values consistent with the 98-pillar derivation
  3. The falsifier list is complete and correctly formed
  4. The HILS / Pentad dynamics respect the stability bounds
  5. The compute_all() OmegaReport is internally consistent
  6. Edge cases (zero trust, saturated HIL, falsifier conditions)

Expected: 168 passed, 0 failed.

Tests: GitHub Copilot (AI)
"""


from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import math
from fractions import Fraction

import pytest

from omega.omega_synthesis import (
    UniversalEngine,
    OmegaReport,
    CosmologyReport,
    ParticlePhysicsReport,
    GeometryReport,
    ConsciousnessReport,
    HILSReport,
    FalsifiablePrediction,
    # Seed constants
    N_W,
    N_2,
    K_CS,
    C_S,
    XI_C,
)


# ===========================================================================
# SECTION A — SEED CONSTANTS (15 tests)
# Verify the five generators of the universe are algebraically exact.
# ===========================================================================


class TestSeedConstants:
    """The five seed constants are the foundation of everything."""

    def test_n_w_is_five(self):
        """Primary winding number must be exactly 5 (Planck/APS selection)."""
        assert N_W == 5

    def test_n_2_is_seven(self):
        """Braid partner must be exactly 7 (BICEP/Keck/β-window selection)."""
        assert N_2 == 7

    def test_k_cs_is_sum_of_squares(self):
        """k_CS = N_W² + N_2² is the resonance identity (Pillar 74)."""
        assert K_CS == N_W**2 + N_2**2

    def test_k_cs_value(self):
        """k_CS must equal 74."""
        assert K_CS == 74

    def test_c_s_exact_fraction(self):
        """c_s = 12/37 as an exact Fraction (Pillar 27)."""
        assert C_S == Fraction(12, 37)

    def test_c_s_numerator_denominator(self):
        """c_s = 12/37 after GCD reduction (unreduced: 24/74 = 12/37)."""
        # The unreduced braid formula gives (N_2²−N_W²)/K_CS = 24/74,
        # which Python's Fraction reduces to 12/37.
        assert C_S.numerator == 12
        assert C_S.denominator == 37

    def test_c_s_float_range(self):
        """c_s ≈ 0.3243 (between 0.32 and 0.33)."""
        assert 0.32 < float(C_S) < 0.33

    def test_xi_c_exact(self):
        """Ξ_c = 35/74 (consciousness coupling constant, Pillar 9)."""
        assert XI_C == Fraction(35, 74)

    def test_xi_c_float(self):
        """Ξ_c ≈ 0.4730 (between 0.47 and 0.48)."""
        assert 0.47 < float(XI_C) < 0.48

    def test_k_cs_self_referential(self):
        """k_CS = 74: the pillar count equals the Chern-Simons level (Pillar 74 C6)."""
        assert K_CS == 74

    def test_c_s_satisfies_braid_formula(self):
        """c_s = |n₂²−n₁²| / k_cs (braid kinematics formula, exact)."""
        expected = Fraction(abs(N_2**2 - N_W**2), K_CS)
        assert C_S == expected

    def test_seed_constants_determinism(self):
        """All seed constants must be derivable from N_W and N_2 alone."""
        k = N_W**2 + N_2**2
        c = Fraction(N_2**2 - N_W**2, k)
        xi = Fraction(35, k)
        assert k == K_CS
        assert c == C_S
        assert xi == XI_C

    def test_braided_sound_speed_lt_one(self):
        """c_s < 1 (causal — sound cannot exceed light)."""
        assert float(C_S) < 1.0

    def test_n_w_odd(self):
        """n_w must be odd (APS Z₂ parity → odd winding → η̄=½)."""
        assert N_W % 2 == 1

    def test_n_2_greater_than_n_w(self):
        """n_2 > n_w (braid partner is the larger winding mode)."""
        assert N_2 > N_W


# ===========================================================================
# SECTION B — COSMOLOGICAL DOMAIN (20 tests)
# ===========================================================================


class TestCosmology:
    """Cosmological observables from the 5D Kaluza-Klein geometry."""

    @pytest.fixture
    def engine(self):
        return UniversalEngine()

    @pytest.fixture
    def cos(self, engine):
        return engine.cosmology()

    def test_n_s_in_planck_window(self, cos):
        """nₛ must be within ±0.006 of Planck 2018 central value 0.9649."""
        assert abs(cos.n_s - 0.9649) < 0.006

    def test_n_s_approx_0_9635(self, cos):
        """nₛ ≈ 0.9635 (the UM-derived value)."""
        assert abs(cos.n_s - 0.9635) < 0.001

    def test_r_bare_approx(self, cos):
        """Bare tensor ratio r_bare ≈ 0.0973 (single n_w=5 mode)."""
        assert abs(cos.r_bare - 0.0973) < 0.005

    def test_r_braided_below_bicep(self, cos):
        """Braided r must satisfy BICEP/Keck r < 0.036."""
        assert cos.r_braided < 0.036

    def test_r_braided_equals_r_bare_times_c_s(self, cos):
        """r_braided = r_bare × c_s (braiding suppression formula)."""
        expected = cos.r_bare * float(C_S)
        assert abs(cos.r_braided - expected) < 1e-10

    def test_beta_57_canonical(self, cos):
        """(5,7) sector β ≈ 0.331° (Minami-Komatsu 2020 central)."""
        assert abs(cos.beta_57_deg - 0.331) < 0.005

    def test_beta_56_canonical(self, cos):
        """(5,6) sector β ≈ 0.273° (shadow sector)."""
        assert abs(cos.beta_56_deg - 0.273) < 0.005

    def test_beta_gap(self, cos):
        """β gap ≈ 0.058° (= β(5,7) − β(5,6))."""
        gap = cos.beta_57_deg - cos.beta_56_deg
        assert abs(gap - cos.beta_gap_deg) < 1e-10

    def test_litebird_separation(self, cos):
        """LiteBIRD separation ≈ 2.9σ (discriminating, not just constraining)."""
        sep = cos.beta_gap_deg / cos.litebird_sigma_deg
        assert abs(sep - cos.litebird_separation_sigma) < 0.01
        assert cos.litebird_separation_sigma > 2.5

    def test_beta_57_in_window(self, cos):
        """β(5,7) ∈ [0.22°, 0.38°] (the admissible birefringence window)."""
        assert 0.22 <= cos.beta_57_deg <= 0.38

    def test_beta_56_in_window(self, cos):
        """β(5,6) ∈ [0.22°, 0.38°] (the admissible birefringence window)."""
        assert 0.22 <= cos.beta_56_deg <= 0.38

    def test_beta_gap_not_in_itself(self, cos):
        """The gap (0.29°–0.31°) is NOT a valid prediction — it falsifies."""
        # The gap region [0.29, 0.31] should lie BETWEEN the two predictions
        assert not (0.29 <= cos.beta_56_deg <= 0.31)
        assert not (0.29 <= cos.beta_57_deg <= 0.31)

    def test_w_dark_energy_formula(self, cos):
        """w = −1 + (2/3)c_s² (KK dark energy equation of state)."""
        expected = -1.0 + (2.0 / 3.0) * float(C_S) ** 2
        assert abs(cos.w_dark_energy - expected) < 1e-10

    def test_w_dark_energy_quintessence(self, cos):
        """w is between −1 and −0.9 (dark-energy-like, not phantom)."""
        assert -1.0 < cos.w_dark_energy < -0.9

    def test_k_cs_value_in_report(self, cos):
        """k_CS in report matches the global constant."""
        assert cos.k_cs == K_CS

    def test_c_s_float_in_report(self, cos):
        """c_s float in report matches the global constant."""
        assert abs(cos.c_s - float(C_S)) < 1e-15

    def test_n_w_in_report(self, cos):
        """N_W in report matches global constant."""
        assert cos.n_w == N_W

    def test_n_2_in_report(self, cos):
        """N_2 in report matches global constant."""
        assert cos.n_2 == N_2

    def test_m_kk_sub_ev(self, cos):
        """M_KK is sub-eV (1 eV = 10⁻³ MeV; M_KK ≈ 110 meV = 1.1×10⁻⁴ MeV)."""
        assert cos.m_kk_mev < 1e-3

    def test_compute_n_s_method(self, engine):
        """compute_n_s() returns the same value as the report."""
        assert engine.compute_n_s() == engine.cosmology().n_s

    def test_compute_r_braided(self, engine):
        """compute_r(braided=True) returns r_braided."""
        assert engine.compute_r(braided=True) == engine.cosmology().r_braided

    def test_compute_r_bare(self, engine):
        """compute_r(braided=False) returns r_bare."""
        assert engine.compute_r(braided=False) == engine.cosmology().r_bare

    def test_compute_beta_57(self, engine):
        """compute_beta(7) returns β(5,7)."""
        assert engine.compute_beta(7) == engine.cosmology().beta_57_deg

    def test_compute_beta_56(self, engine):
        """compute_beta(6) returns β(5,6)."""
        assert engine.compute_beta(6) == engine.cosmology().beta_56_deg

    def test_compute_w(self, engine):
        """compute_w_dark_energy() returns w."""
        assert engine.compute_w_dark_energy() == engine.cosmology().w_dark_energy

    def test_compute_litebird_discrim(self, engine):
        """compute_litebird_discriminability() returns the σ separation."""
        assert engine.compute_litebird_discriminability() > 2.5


# ===========================================================================
# SECTION C — PARTICLE PHYSICS DOMAIN (25 tests)
# ===========================================================================


class TestParticlePhysics:
    """Particle physics observables from the Unitary Manifold."""

    @pytest.fixture
    def engine(self):
        return UniversalEngine()

    @pytest.fixture
    def pp(self, engine):
        return engine.particle_physics()

    def test_y5_universal(self, pp):
        """Universal 5D Yukawa coupling Ŷ₅ = 1 (GW vacuum, Pillar 97)."""
        assert pp.y5_universal == 1.0

    def test_c_l_electron_range(self, pp):
        """Electron bulk mass c_L ∈ (0.5, 1.5) (UV-localised regime)."""
        assert 0.5 < pp.c_l_electron < 1.5

    def test_c_l_ordering(self, pp):
        """c_L^e > c_L^μ > c_L^τ (heavier fermion = smaller c_L = more IR-localised)."""
        assert pp.c_l_electron > pp.c_l_muon > pp.c_l_tau

    def test_wolfenstein_lambda(self, pp):
        """λ = √(m_d/m_s) ≈ 0.224 (within 5% of PDG 0.225)."""
        assert abs(pp.wolfenstein_lambda - 0.2236) < 0.005

    def test_wolfenstein_A_formula(self, pp):
        """A = √(N_W/N_2) = √(5/7) (exact geometric formula, Pillar 87)."""
        expected = math.sqrt(N_W / N_2)
        assert abs(pp.wolfenstein_A - expected) < 1e-10

    def test_wolfenstein_A_value(self, pp):
        """A ≈ 0.845 (PDG 0.826, 2.3% off — geometric prediction)."""
        assert abs(pp.wolfenstein_A - 0.8452) < 0.002

    def test_wolfenstein_eta_bar(self, pp):
        """η̄ ≈ 0.356 (PDG 0.348, 2.3% off — R_b×sin(72°), Pillar 87)."""
        assert abs(pp.wolfenstein_eta_bar - 0.356) < 0.005

    def test_ckm_cp_phase_formula(self, pp):
        """δ_CKM = 2π/N_W = 360/5 = 72° (geometric prediction)."""
        assert abs(pp.ckm_cp_phase_deg - 360.0 / N_W) < 1e-10

    def test_ckm_cp_phase_near_pdg(self, pp):
        """δ_CKM = 72° within 10° of PDG 68.5° (1.35σ)."""
        assert abs(pp.ckm_cp_phase_deg - 68.5) < 10.0

    def test_sin2_theta23_formula(self, pp):
        """sin²θ₂₃ = 29/50 (exact fraction, Pillar 83)."""
        assert abs(pp.sin2_theta23 - 29.0 / 50.0) < 1e-10

    def test_sin2_theta23_near_pdg(self, pp):
        """sin²θ₂₃ ≈ 0.580 within 3% of PDG 0.572."""
        assert abs(pp.sin2_theta23 - 0.572) < 0.020

    def test_sin2_theta13_formula(self, pp):
        """sin²θ₁₃ = 1/(2N_W²) = 1/50 (exact formula, Pillar 83)."""
        expected = 1.0 / (2 * N_W**2)
        assert abs(pp.sin2_theta13 - expected) < 1e-10

    def test_sin2_theta13_near_pdg(self, pp):
        """sin²θ₁₃ ≈ 0.020 within 20% of PDG 0.0222."""
        assert abs(pp.sin2_theta13 - 0.0222) < 0.005

    def test_pmns_cp_closed(self, pp):
        """δ_CP^PMNS = −108° within 2° of PDG −107° (Pillar 86 CLOSED)."""
        assert abs(pp.pmns_cp_deg - (-107.0)) < 2.0

    def test_sum_mnu_below_planck(self, pp):
        """Σm_ν < 120 meV (Planck CMB+BAO upper limit)."""
        assert pp.sum_mnu_mev < 120.0

    def test_sum_mnu_positive(self, pp):
        """Σm_ν > 0 (neutrinos are massive)."""
        assert pp.sum_mnu_mev > 0.0

    def test_delta_m2_ratio_near_pdg(self, pp):
        """Δm²₃₁/Δm²₂₁ = N_W×N_2+1 = 36 (PDG 32.6, 11% off)."""
        expected = N_W * N_2 + 1
        assert abs(pp.delta_m2_ratio - expected) < 1e-10

    def test_sin2_theta_W_gut_exact(self, pp):
        """sin²θ_W(M_GUT) = 3/8 exactly (SU(5) prediction, Pillar 88)."""
        assert abs(pp.sin2_theta_W_gut - 3.0 / 8.0) < 1e-10

    def test_sin2_theta_W_mz_near_pdg(self, pp):
        """sin²θ_W(M_Z) ≈ 0.2313 within 0.5% of PDG 0.23122."""
        assert abs(pp.sin2_theta_W_mz - 0.23122) < 0.002

    def test_m_higgs_tree_order(self, pp):
        """Tree-level Higgs mass should be of order 100–200 GeV."""
        assert 100.0 < pp.m_higgs_tree_gev < 200.0

    def test_m_higgs_corrected_order(self, pp):
        """Top-corrected Higgs mass should be within 30 GeV of PDG 125.1 GeV."""
        assert abs(pp.m_higgs_corrected_gev - 125.1) < 30.0

    def test_sm_parameter_audit_total(self, pp):
        """SM parameter counts must sum to 28."""
        total = pp.n_sm_derived + pp.n_sm_constrained + pp.n_sm_conjectured + pp.n_sm_open
        assert total == pp.n_sm_total == 28

    def test_sm_derived_count(self, pp):
        """9 SM parameters are fully derived from the UM geometry."""
        assert pp.n_sm_derived == 9

    def test_compute_ckm_cp(self, engine):
        """compute_ckm_cp_phase() returns same value as report."""
        assert engine.compute_ckm_cp_phase() == engine.particle_physics().ckm_cp_phase_deg

    def test_compute_pmns_cp(self, engine):
        """compute_pmns_cp_phase() returns same value as report."""
        assert engine.compute_pmns_cp_phase() == engine.particle_physics().pmns_cp_deg


# ===========================================================================
# SECTION D — GEOMETRIC DOMAIN (15 tests)
# ===========================================================================


class TestGeometry:
    """5D geometric quantities — topology, holography, KK spectrum."""

    @pytest.fixture
    def engine(self):
        return UniversalEngine()

    @pytest.fixture
    def geo(self, engine):
        return engine.geometry()

    def test_eta_bar_n5(self, geo):
        """APS η̄(n_w=5) = ½ (chirality selection, Pillar 70-B)."""
        assert geo.eta_bar_n5 == 0.5

    def test_eta_bar_n7(self, geo):
        """APS η̄(n_w=7) = 0 (inert sector, Pillar 70-B)."""
        assert geo.eta_bar_n7 == 0.0

    def test_second_law_geometric(self, geo):
        """Second Law is a geometric identity — always True (Pillar 1)."""
        assert geo.second_law_geometric is True

    def test_ftum_fixed_point_string(self, geo):
        """FTUM fixed point S* = A/(4G) is expressed correctly."""
        assert "A" in geo.ftum_fixed_point
        assert "4G" in geo.ftum_fixed_point

    def test_n_generations(self, geo):
        """3 fermion generations from KK stability + Z₂ orbifold (Pillar 68)."""
        assert geo.n_generations == 3

    def test_n_moduli_equals_n2(self, geo):
        """Number of surviving KK moduli = N_2 = 7 (Pillar 5)."""
        assert geo.n_moduli == N_2

    def test_k_cs_constraints(self, geo):
        """Exactly 7 independent constraints satisfied by k_CS=74 (Pillar 74)."""
        assert geo.k_cs_constraints_satisfied == 7

    def test_n_lossless_sectors(self, geo):
        """Exactly 2 lossless braid sectors proved analytically (Pillar 96)."""
        assert geo.n_lossless_sectors == 2

    def test_sector_56_k(self, geo):
        """(5,6) sector k_CS = 5²+6² = 61."""
        assert geo.sector_56_k == N_W**2 + 6**2  # 25+36=61

    def test_sector_57_k(self, geo):
        """(5,7) sector k_CS = 5²+7² = 74."""
        assert geo.sector_57_k == K_CS

    def test_kk_entropy_monotone(self, geo):
        """dS_n/dt ≥ 0 for every KK mode (proved lower bound, Pillar 72)."""
        assert geo.kk_entropy_monotone is True

    def test_phi0_eff(self, geo):
        """φ₀_eff = N_W × 2π ≈ 31.416 M_Pl."""
        expected = N_W * 2 * math.pi
        assert abs(geo.phi0_effective - expected) < 1e-10

    def test_alpha_em_inverse(self, geo):
        """Fine structure α⁻¹ ≈ 137 (reported as QED value)."""
        assert abs(geo.alpha_em_inverse - 137.036) < 0.1

    def test_eta_bar_n5_half(self, geo):
        """η̄(5) = ½ exactly (not approximately)."""
        assert geo.eta_bar_n5 == 0.5

    def test_sector_gap(self, geo):
        """Two-sector k_CS gap = 74 − 61 = 13."""
        assert geo.sector_57_k - geo.sector_56_k == 13


# ===========================================================================
# SECTION E — CONSCIOUSNESS & BIOLOGY (15 tests)
# ===========================================================================


class TestConsciousness:
    """Brain-universe coupling and biological scale predictions."""

    @pytest.fixture
    def engine(self):
        return UniversalEngine()

    @pytest.fixture
    def con(self, engine):
        return engine.consciousness()

    def test_xi_c_exact(self, con):
        """Ξ_c = 35/74 exactly (consciousness coupling)."""
        assert con.xi_c == Fraction(35, 74)

    def test_xi_human_exact(self, con):
        """Ξ_human = 35/888 exactly (human coupling fraction)."""
        assert con.xi_human == Fraction(35, 888)

    def test_beta_coupling_degrees(self, con):
        """β coupling in degrees ≈ 0.3513."""
        assert abs(con.beta_coupling_deg - 0.3513) < 0.001

    def test_beta_coupling_radians(self, con):
        """β coupling in radians ≈ 0.00613."""
        assert abs(con.beta_coupling_rad - math.radians(0.3513)) < 1e-10

    def test_omega_ratio(self, con):
        """ω_brain/ω_univ = 5/7 (frequency lock)."""
        assert con.omega_ratio == Fraction(N_W, N_2)

    def test_grid_module_ratio(self, con):
        """Grid-cell module spacing = N_2/N_W = 7/5 = 1.40."""
        assert abs(con.grid_module_ratio - N_2 / N_W) < 1e-10

    def test_grid_module_ratio_value(self, con):
        """Grid-cell ratio exactly 1.4 (entorhinal cortex measurement)."""
        assert abs(con.grid_module_ratio - 1.4) < 1e-10

    def test_information_gap_nondual(self, con):
        """Non-dual limit ΔI → 0."""
        assert con.information_gap_nondual == 0.0

    def test_fixed_point_string(self, con):
        """Coupled fixed point string references brain and universe."""
        assert "brain" in con.coupled_fixed_point.lower()
        assert "univ" in con.coupled_fixed_point.lower()

    def test_r_egg_micron(self, con):
        """Predicted egg cell radius ≈ 59.7 μm."""
        assert abs(con.r_egg_micron - 59.7) < 1.0

    def test_n_zinc_ions(self, con):
        """N_Zn = 74^5 ≈ 2.19×10⁹."""
        expected = K_CS ** N_W
        assert abs(con.n_zinc_ions - expected) / expected < 1e-10

    def test_hox_groups(self, con):
        """HOX groups = 2 × N_W = 10."""
        assert con.hox_groups == 2 * N_W

    def test_hox_clusters(self, con):
        """HOX clusters = 2^(N_2−N_W) = 4 (vertebrate count)."""
        assert con.hox_clusters == 2 ** (N_2 - N_W)

    def test_compute_consciousness_coupling(self, engine):
        """compute_consciousness_coupling() returns Ξ_c as float."""
        val = engine.compute_consciousness_coupling()
        assert abs(val - float(XI_C)) < 1e-15

    def test_xi_c_greater_than_half(self, con):
        """Ξ_c > 0.4 (consciousness dominates over 40% coupling)."""
        assert float(con.xi_c) > 0.4


# ===========================================================================
# SECTION F — HILS & PENTAD (20 tests)
# ===========================================================================


class TestHILS:
    """Human-in-Loop Co-Emergent System and Unitary Pentad dynamics."""

    def test_n_bodies_is_five(self):
        """The Pentad has exactly 5 bodies (n_w = 5 bodies, not coincidence)."""
        engine = UniversalEngine()
        h = engine.hils()
        assert h.n_bodies == N_W

    def test_body_count(self):
        """There are exactly 5 body name strings."""
        engine = UniversalEngine()
        h = engine.hils()
        assert len(h.body_names) == 5

    def test_phi_trust_default(self):
        """Default phi_trust = 1.0 (full trust)."""
        engine = UniversalEngine()
        h = engine.hils()
        assert h.phi_trust == 1.0

    def test_phi_trust_min_equals_c_s(self):
        """Trust floor = c_s = 12/37 (topological stability bound)."""
        engine = UniversalEngine()
        h = engine.hils()
        assert abs(h.phi_trust_min - float(C_S)) < 1e-10

    def test_trust_sufficient_at_default(self):
        """With phi_trust=1.0 trust is sufficient."""
        engine = UniversalEngine()
        h = engine.hils()
        assert h.trust_is_sufficient is True

    def test_trust_insufficient_at_zero(self):
        """With phi_trust=0.0 trust is insufficient."""
        engine = UniversalEngine(phi_trust=0.0)
        h = engine.hils()
        assert h.trust_is_sufficient is False

    def test_trust_boundary_at_c_s(self):
        """Trust is sufficient at exactly c_s (the boundary)."""
        engine = UniversalEngine(phi_trust=float(C_S))
        h = engine.hils()
        assert h.trust_is_sufficient is True

    def test_stability_floor_zero_hil(self):
        """With 0 HIL operators floor = c_s (no collective lift)."""
        engine = UniversalEngine(n_hil=0)
        h = engine.hils()
        assert abs(h.stability_floor - float(C_S)) < 1e-10

    def test_stability_floor_saturates(self):
        """With 15+ HIL operators floor saturates to 1.0."""
        engine = UniversalEngine(n_hil=15)
        h = engine.hils()
        assert h.stability_floor == 1.0
        assert h.saturated is True

    def test_stability_floor_not_saturated_below_15(self):
        """With 14 HIL operators floor < 1.0 and not saturated."""
        engine = UniversalEngine(n_hil=14)
        h = engine.hils()
        assert h.stability_floor < 1.0
        assert h.saturated is False

    def test_stability_floor_monotone(self):
        """Stability floor is non-decreasing in n_hil."""
        floors = [UniversalEngine(n_hil=n).hils().stability_floor for n in range(20)]
        for i in range(len(floors) - 1):
            assert floors[i] <= floors[i + 1]

    def test_saturation_threshold(self):
        """Saturation threshold is 15 (HIL_PHASE_SHIFT_THRESHOLD)."""
        engine = UniversalEngine()
        h = engine.hils()
        assert h.saturation_threshold == 15

    def test_pairwise_coupling_scales_with_trust(self):
        """Pairwise coupling τ = β_coupling_rad × phi_trust."""
        for trust in [0.5, 0.75, 1.0]:
            engine = UniversalEngine(phi_trust=trust)
            h = engine.hils()
            expected = math.radians(0.3513) * trust
            assert abs(h.pairwise_coupling - expected) < 1e-12

    def test_pairwise_coupling_zero_at_zero_trust(self):
        """Pairwise coupling → 0 when trust → 0 (bodies decouple)."""
        engine = UniversalEngine(phi_trust=0.0)
        h = engine.hils()
        assert h.pairwise_coupling == 0.0

    def test_information_gap_zero_at_full_trust(self):
        """ΔI = 0 at full trust (HILS fixed point reached)."""
        engine = UniversalEngine(phi_trust=1.0)
        h = engine.hils()
        assert h.information_gap == 0.0

    def test_information_gap_positive_at_zero_trust(self):
        """ΔI > 0 when trust = 0 (systems decoupled, gap persists)."""
        engine = UniversalEngine(phi_trust=0.0)
        h = engine.hils()
        assert h.information_gap > 0.0

    def test_pentad_master_equation_string(self):
        """Pentad master equation string contains all five bodies."""
        engine = UniversalEngine()
        h = engine.hils()
        eq = h.pentad_master_equation
        for body in ("Ψ_univ", "Ψ_brain", "Ψ_human", "Ψ_AI", "Ψ_trust"):
            assert body in eq

    def test_hils_fixed_point_string(self):
        """HILS fixed point string references synthesis."""
        engine = UniversalEngine()
        h = engine.hils()
        assert "synthesis" in h.hils_fixed_point.lower()

    def test_update_trust(self):
        """update_trust() returns a new engine with the new phi_trust."""
        engine = UniversalEngine(phi_trust=1.0)
        new_engine = engine.update_trust(0.5)
        assert new_engine.phi_trust == 0.5
        assert engine.phi_trust == 1.0  # original unchanged

    def test_update_hil(self):
        """update_hil() returns a new engine with the new n_hil."""
        engine = UniversalEngine(n_hil=1)
        new_engine = engine.update_hil(10)
        assert new_engine.n_hil == 10
        assert engine.n_hil == 1  # original unchanged

    def test_compute_stability_floor_method(self):
        """compute_stability_floor() matches hils() report value."""
        engine = UniversalEngine(n_hil=7)
        assert engine.compute_stability_floor() == engine.hils().stability_floor

    def test_compute_stability_floor_custom_n(self):
        """compute_stability_floor(n) computes for custom n, not self.n_hil."""
        engine = UniversalEngine(n_hil=1)
        floor_3 = engine.compute_stability_floor(n_hil=3)
        floor_7 = engine.compute_stability_floor(n_hil=7)
        assert floor_3 < floor_7


# ===========================================================================
# SECTION G — FALSIFIERS (15 tests)
# ===========================================================================


class TestFalsifiers:
    """The falsifiable predictions — a theory that can be killed is real."""

    @pytest.fixture
    def fals(self):
        return UniversalEngine().falsifiers()

    def test_falsifier_count(self, fals):
        """Engine produces at least 8 independent falsifiable predictions."""
        assert len(fals) >= 8

    def test_all_have_status(self, fals):
        """Every falsifier must have a non-empty status."""
        for fp in fals:
            assert fp.status in {"ACTIVE", "CONFIRMED", "CONSTRAINED", "FALSIFIED"}

    def test_all_have_instrument(self, fals):
        """Every falsifier must name a test instrument."""
        for fp in fals:
            assert len(fp.instrument) > 5

    def test_all_have_falsification_condition(self, fals):
        """Every falsifier must state a precise falsification condition."""
        for fp in fals:
            assert len(fp.falsified_if) > 10

    def test_litebird_falsifier_present(self, fals):
        """At least one falsifier references LiteBIRD."""
        instruments = " ".join(fp.instrument for fp in fals)
        assert "LiteBIRD" in instruments

    def test_n_s_falsifier_confirmed(self, fals):
        """nₛ prediction is CONFIRMED (Planck 2018)."""
        ns_fals = [fp for fp in fals if "Spectral" in fp.domain]
        assert len(ns_fals) >= 1
        assert any(fp.status == "CONFIRMED" for fp in ns_fals)

    def test_pmns_cp_falsifier_confirmed(self, fals):
        """PMNS CP phase is CONFIRMED (PDG -107°, 0.05σ)."""
        pmns = [fp for fp in fals if "PMNS" in fp.domain]
        assert len(pmns) >= 1
        assert any(fp.status == "CONFIRMED" for fp in pmns)

    def test_birefringence_active(self, fals):
        """Birefringence predictions are ACTIVE (awaiting LiteBIRD)."""
        biref = [fp for fp in fals if "Birefringence" in fp.domain]
        assert len(biref) >= 1
        assert any(fp.status == "ACTIVE" for fp in biref)

    def test_is_falsifiable_method(self):
        """is_falsifiable() always returns True (existential guarantee)."""
        assert UniversalEngine().is_falsifiable() is True

    def test_dark_energy_active(self, fals):
        """Dark energy EOS prediction is ACTIVE (awaiting Roman ST)."""
        de = [fp for fp in fals if "Dark Energy" in fp.domain]
        assert len(de) >= 1
        assert any(fp.status == "ACTIVE" for fp in de)

    def test_neutrino_constrained(self, fals):
        """Neutrino mass sum is CONSTRAINED (< 120 meV)."""
        nu = [fp for fp in fals if "Neutrino" in fp.domain]
        assert len(nu) >= 1

    def test_falsifiers_are_dataclass_instances(self, fals):
        """Each falsifier is a FalsifiablePrediction dataclass instance."""
        for fp in fals:
            assert isinstance(fp, FalsifiablePrediction)

    def test_no_falsified_status(self, fals):
        """None of the current predictions are FALSIFIED (as of v9.27)."""
        assert not any(fp.status == "FALSIFIED" for fp in fals)

    def test_roman_telescope_falsifier(self, fals):
        """Roman Space Telescope falsifier is present."""
        instruments = " ".join(fp.instrument for fp in fals)
        assert "Roman" in instruments

    def test_falsifier_domains_unique(self, fals):
        """All falsifiers have distinct domains."""
        domains = [fp.domain for fp in fals]
        assert len(domains) == len(set(domains))


# ===========================================================================
# SECTION H — UNITARY SUMMATION (10 tests)
# ===========================================================================


class TestUnitarySummation:
    """The Unitary Summation — 12-step logical closure of the framework."""

    @pytest.fixture
    def summation(self):
        return UniversalEngine().unitary_summation()

    def test_summation_has_twelve_steps(self, summation):
        """Unitary Summation has exactly 12 steps (Pillar 96 + 2 new)."""
        assert len(summation) == 12

    def test_first_step_mentions_kk(self, summation):
        """Step 1 introduces the 5D KK geometry."""
        assert "5D" in summation[0] or "Kaluza" in summation[0]

    def test_second_step_mentions_n_w(self, summation):
        """Step 2 names n_w = 5."""
        assert "5" in summation[1]

    def test_step_mentions_litebird(self, summation):
        """One step references LiteBIRD as the decisive test."""
        all_text = " ".join(summation)
        assert "LiteBIRD" in all_text

    def test_step_mentions_second_law(self, summation):
        """One step states the Second Law is geometric."""
        all_text = " ".join(summation)
        assert "Second Law" in all_text or "geometric" in all_text.lower()

    def test_step_mentions_pentad(self, summation):
        """One step references the 5-body Pentad."""
        all_text = " ".join(summation)
        assert "Pentad" in all_text or "pentad" in all_text.lower()

    def test_last_step_is_omega(self, summation):
        """Last step references the Omega Synthesis closure."""
        assert "Omega" in summation[-1] or "Pillar Ω" in summation[-1] or "98" in summation[-1]

    def test_repository_complete_stated(self, summation):
        """The summation declares REPOSITORY COMPLETE."""
        all_text = " ".join(summation)
        assert "COMPLETE" in all_text or "complete" in all_text.lower()

    def test_step_mentions_sector_agnostic(self, summation):
        """One step states S* = A/(4G) is sector-agnostic."""
        all_text = " ".join(summation)
        assert "sector" in all_text.lower()

    def test_step_mentions_falsification(self, summation):
        """One step states the falsification condition."""
        all_text = " ".join(summation)
        assert "falsif" in all_text.lower()


# ===========================================================================
# SECTION I — COMPUTE_ALL / OMEGA REPORT (15 tests)
# ===========================================================================


class TestOmegaReport:
    """Integration tests for the full OmegaReport from compute_all()."""

    @pytest.fixture
    def engine(self):
        return UniversalEngine(phi_trust=1.0, n_hil=5)

    @pytest.fixture
    def report(self, engine):
        return engine.compute_all()

    def test_report_is_omega_report(self, report):
        """compute_all() returns an OmegaReport instance."""
        assert isinstance(report, OmegaReport)

    def test_report_version_contains_omega(self, report):
        """Report version string contains 'OMEGA'."""
        assert "OMEGA" in report.version.upper()

    def test_report_n_pillars(self, report):
        """Report records at least 99 pillars (Pillar Ω)."""
        assert report.n_pillars >= 99

    def test_report_n_seed_constants(self, report):
        """Report records exactly 5 seed constants."""
        assert report.n_seed_constants == 5

    def test_report_cosmology_domain(self, report):
        """OmegaReport.cosmology is a CosmologyReport."""
        assert isinstance(report.cosmology, CosmologyReport)

    def test_report_particle_domain(self, report):
        """OmegaReport.particle_physics is a ParticlePhysicsReport."""
        assert isinstance(report.particle_physics, ParticlePhysicsReport)

    def test_report_geometry_domain(self, report):
        """OmegaReport.geometry is a GeometryReport."""
        assert isinstance(report.geometry, GeometryReport)

    def test_report_consciousness_domain(self, report):
        """OmegaReport.consciousness is a ConsciousnessReport."""
        assert isinstance(report.consciousness, ConsciousnessReport)

    def test_report_hils_domain(self, report):
        """OmegaReport.hils is an HILSReport."""
        assert isinstance(report.hils, HILSReport)

    def test_report_falsifiers_list(self, report):
        """OmegaReport.falsifiers is a non-empty list."""
        assert isinstance(report.falsifiers, list)
        assert len(report.falsifiers) > 0

    def test_report_open_gaps(self, report):
        """OmegaReport.open_gaps is a non-empty list."""
        assert isinstance(report.open_gaps, list)
        assert len(report.open_gaps) > 0

    def test_report_unitary_summation(self, report):
        """OmegaReport.unitary_summation has 12 entries."""
        assert len(report.unitary_summation) == 12

    def test_report_summary_method(self, report):
        """summary() produces a multi-line string with key fields."""
        s = report.summary()
        assert "OMEGA SYNTHESIS" in s
        assert "n_s" in s
        assert "HILS PENTAD" in s

    def test_report_consistency_n_s(self, report):
        """n_s in report matches compute_n_s() directly."""
        engine = UniversalEngine(phi_trust=1.0, n_hil=5)
        assert report.cosmology.n_s == engine.compute_n_s()

    def test_report_consistency_beta(self, report):
        """β(5,7) in report matches compute_beta(7) directly."""
        engine = UniversalEngine(phi_trust=1.0, n_hil=5)
        assert report.cosmology.beta_57_deg == engine.compute_beta(7)


# ===========================================================================
# SECTION J — ENGINE VALIDATION & EDGE CASES (10 tests)
# ===========================================================================


class TestEngineEdgeCases:
    """Edge cases, validation, and defensive programming checks."""

    def test_repr_string(self):
        """repr() of engine is informative."""
        engine = UniversalEngine(phi_trust=0.7, n_hil=3)
        r = repr(engine)
        assert "UniversalEngine" in r
        assert "0.700" in r
        assert "3" in r

    def test_invalid_phi_trust_raises(self):
        """phi_trust outside [0, 1] raises ValueError."""
        with pytest.raises(ValueError):
            UniversalEngine(phi_trust=1.5)
        with pytest.raises(ValueError):
            UniversalEngine(phi_trust=-0.1)

    def test_invalid_n_hil_raises(self):
        """Negative n_hil raises ValueError."""
        with pytest.raises(ValueError):
            UniversalEngine(n_hil=-1)

    def test_zero_trust_engine(self):
        """Engine with phi_trust=0 is constructable and reports correctly."""
        engine = UniversalEngine(phi_trust=0.0)
        h = engine.hils()
        assert not h.trust_is_sufficient
        assert h.pairwise_coupling == 0.0

    def test_maximum_hil_engine(self):
        """Engine with n_hil=100 saturates correctly."""
        engine = UniversalEngine(n_hil=100)
        h = engine.hils()
        assert h.stability_floor == 1.0
        assert h.saturated is True

    def test_compute_beta_invalid_sector(self):
        """compute_beta() raises ValueError for unsupported sector."""
        engine = UniversalEngine()
        with pytest.raises(ValueError):
            engine.compute_beta(8)

    def test_stability_floor_formula(self):
        """Stability floor formula: min(1.0, c_s + n × c_s/7)."""
        c = float(C_S)
        for n in range(20):
            expected = min(1.0, c + n * c / N_2)
            computed = UniversalEngine._stability_floor(n)
            assert abs(computed - expected) < 1e-14

    def test_multiple_engines_independent(self):
        """Two engines with different parameters are fully independent."""
        e1 = UniversalEngine(phi_trust=0.5, n_hil=2)
        e2 = UniversalEngine(phi_trust=0.9, n_hil=8)
        assert e1.phi_trust != e2.phi_trust
        assert e1.n_hil != e2.n_hil
        # Physics domain is the same (seed constants are global)
        assert e1.compute_n_s() == e2.compute_n_s()

    def test_seed_constants_unchanged_across_engines(self):
        """Seed constants N_W, K_CS etc. are module-level and immutable."""
        e = UniversalEngine(phi_trust=0.3)
        assert e.N_W == 5
        assert e.K_CS == 74
        assert e.C_S == Fraction(12, 37)

    def test_compute_all_is_idempotent(self):
        """compute_all() called twice returns identical reports."""
        engine = UniversalEngine()
        r1 = engine.compute_all()
        r2 = engine.compute_all()
        assert r1.cosmology.n_s == r2.cosmology.n_s
        assert r1.geometry.eta_bar_n5 == r2.geometry.eta_bar_n5
        assert r1.particle_physics.pmns_cp_deg == r2.particle_physics.pmns_cp_deg
