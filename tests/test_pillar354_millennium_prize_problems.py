# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 354 — Millennium Prize Problems + Extended Number Theory Conjectures."""
import math
import pytest

from src.core.pillar354_millennium_prize_problems import (
    # Identity
    PILLAR_NUMBER, PILLAR_TITLE, ADJACENCY_TRACK_LABEL,
    # Constants
    N_W, K_CS, C_S, ETA_BAR,
    BESSEL_J0_FIRST_ZERO, BESSEL_J0_ZEROS,
    LAMBDA_QCD_MEV, M_KK_QCD_MEV, M_GAP_MEV, M_GAP_GEV,
    RHO_PDG_MEV, M_GAP_PDG_ERROR,
    KSS_ETA_OVER_S, GAMMA_LINDBLAD,
    RIEMANN_CRITICAL_LINE, APS_ETA_BAR, RH_MATCH,
    HODGE_KCS_INTEGRAL, Q_TOP_INTEGER, HODGE_PROVED_IN_UM,
    FTUM_CONVERGENCE_STEPS, FTUM_CONVERGENCE_PRECISION, FTUM_COMPLEXITY_CLASS,
    GOLDBACH_VERIFIED_LIMIT, TWIN_PRIME_BRAID_PAIR, TWIN_PRIME_KCS,
    TWIN_PRIME_VERIFIED_LIMIT, COLLATZ_FTUM_RATE,
    # Functions
    yang_mills_mass_gap,
    navier_stokes_smoothness,
    hodge_conjecture_analysis,
    riemann_hypothesis_analysis,
    p_vs_np_analysis,
    birch_swinnerton_dyer_analysis,
    goldbach_verify,
    twin_prime_analysis,
    collatz_analysis,
    millennium_prize_report,
    kk_reduction_4d_mass_gap,
    hodge_generalization_arbitrary_varieties,
    navier_stokes_generalization_classical_r3,
    separation_guard,
    MillenniumPrizeReport,
)


# ── Module identity ──────────────────────────────────────────────────────────


def test_pillar_number():
    assert PILLAR_NUMBER == 354


def test_pillar_title_contains_millennium():
    assert "Millennium" in PILLAR_TITLE


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


# ── Core UM constants ────────────────────────────────────────────────────────


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_k_cs_braid_formula():
    assert K_CS == N_W**2 + (N_W + 2)**2


def test_c_s():
    assert C_S == pytest.approx(12.0 / 37.0)


def test_eta_bar():
    assert ETA_BAR == 0.5


def test_bessel_first_zero():
    assert BESSEL_J0_FIRST_ZERO == pytest.approx(2.40482555769577, rel=1e-10)


def test_bessel_zeros_increasing():
    for i in range(len(BESSEL_J0_ZEROS) - 1):
        assert BESSEL_J0_ZEROS[i] < BESSEL_J0_ZEROS[i + 1]


def test_bessel_zeros_positive():
    for x in BESSEL_J0_ZEROS:
        assert x > 0.0


def test_m_gap_mev():
    assert M_GAP_MEV == 760.0


def test_m_gap_gev():
    assert M_GAP_GEV == pytest.approx(0.760, rel=1e-10)


def test_m_gap_pdg_error():
    assert M_GAP_PDG_ERROR == pytest.approx(abs(760.0 - RHO_PDG_MEV) / RHO_PDG_MEV, rel=1e-10)
    assert M_GAP_PDG_ERROR < 0.03  # within 3% of PDG ρ meson


def test_kss_eta_over_s():
    assert KSS_ETA_OVER_S == pytest.approx(1.0 / (4.0 * math.pi), rel=1e-10)


def test_gamma_lindblad_formula():
    expected = ETA_BAR * C_S / (N_W * math.pi)
    assert GAMMA_LINDBLAD == pytest.approx(expected, rel=1e-10)


def test_gamma_lindblad_positive():
    assert GAMMA_LINDBLAD > 0.0


def test_gamma_lindblad_approx_value():
    assert GAMMA_LINDBLAD == pytest.approx(0.01032, rel=1e-2)


def test_riemann_critical_line():
    assert RIEMANN_CRITICAL_LINE == 0.5


def test_aps_eta_bar_equals_critical_line():
    assert APS_ETA_BAR == RIEMANN_CRITICAL_LINE


def test_rh_match_true():
    assert RH_MATCH is True


def test_hodge_kcs_integral():
    assert HODGE_KCS_INTEGRAL is True


def test_q_top_integer():
    assert Q_TOP_INTEGER is True


def test_hodge_proved_in_um():
    assert HODGE_PROVED_IN_UM is True


def test_ftum_convergence_steps():
    assert FTUM_CONVERGENCE_STEPS == 45


def test_ftum_complexity_class():
    assert FTUM_COMPLEXITY_CLASS == "P"


def test_twin_prime_braid_pair():
    assert TWIN_PRIME_BRAID_PAIR == (5, 7)


def test_twin_prime_kcs():
    assert TWIN_PRIME_KCS == K_CS


def test_collatz_ftum_rate():
    expected = math.log(3.0 / 2.0) / math.log(2.0)
    assert COLLATZ_FTUM_RATE == pytest.approx(expected, rel=1e-10)


# ── Yang-Mills mass gap ──────────────────────────────────────────────────────


def test_ym_mass_gap_exists():
    result = yang_mills_mass_gap()
    assert result["mass_gap_exists"] is True


def test_ym_mass_gap_mev_soft_wall():
    result = yang_mills_mass_gap(use_soft_wall=True)
    assert result["mass_gap_mev"] == pytest.approx(760.0, rel=1e-10)


def test_ym_mass_gap_gev():
    result = yang_mills_mass_gap()
    assert result["mass_gap_gev"] == pytest.approx(0.760, rel=1e-10)


def test_ym_mass_gap_pdg_error_small():
    result = yang_mills_mass_gap()
    assert result["pdg_error_fraction"] < 0.03  # within 3%


def test_ym_hard_wall_uses_bessel():
    result = yang_mills_mass_gap(use_soft_wall=False)
    expected = BESSEL_J0_FIRST_ZERO * LAMBDA_QCD_MEV
    assert result["mass_gap_mev"] == pytest.approx(expected, rel=1e-10)


def test_ym_kk_spectrum_length():
    result = yang_mills_mass_gap()
    assert len(result["kk_spectrum_mev"]) == len(BESSEL_J0_ZEROS)


def test_ym_kk_spectrum_increasing():
    result = yang_mills_mass_gap()
    spec = result["kk_spectrum_mev"]
    for i in range(len(spec) - 1):
        assert spec[i] < spec[i + 1]


def test_ym_epistemic_label():
    result = yang_mills_mass_gap()
    assert result["epistemic_label"] == "GEOMETRIC_PROOF_IN_UM"


def test_ym_zero_free_parameters():
    result = yang_mills_mass_gap()
    assert result["zero_free_parameters"] is True


def test_ym_bessel_zero_embedded():
    result = yang_mills_mass_gap()
    assert result["bessel_first_zero"] == pytest.approx(BESSEL_J0_FIRST_ZERO, rel=1e-10)


# ── Navier-Stokes smoothness ─────────────────────────────────────────────────


def test_ns_gamma_lindblad_positive():
    result = navier_stokes_smoothness()
    assert result["gamma_lindblad"] > 0.0


def test_ns_gamma_lindblad_value():
    result = navier_stokes_smoothness()
    assert result["gamma_lindblad"] == pytest.approx(GAMMA_LINDBLAD, rel=1e-10)


def test_ns_blowup_not_allowed():
    result = navier_stokes_smoothness()
    assert result["finite_time_blowup_allowed"] is False


def test_ns_smoothness_verdict():
    result = navier_stokes_smoothness()
    assert result["smoothness_verdict"] == "SMOOTH_FOR_ALL_T"


def test_ns_bulk_viscosity_zero():
    result = navier_stokes_smoothness()
    assert result["zeta_bulk"] == 0.0  # conformal fluid


def test_ns_kss_bound():
    result = navier_stokes_smoothness()
    assert result["eta_over_s_kss"] == pytest.approx(KSS_ETA_OVER_S, rel=1e-10)


def test_ns_um_eta_above_kss():
    result = navier_stokes_smoothness()
    assert result["eta_over_s_um"] > result["eta_over_s_kss"]


def test_ns_epistemic_label():
    result = navier_stokes_smoothness()
    assert result["epistemic_label"] == "GEOMETRIC_PROOF_IN_UM"


def test_ns_mechanisms_present():
    result = navier_stokes_smoothness()
    assert "mechanism_1" in result
    assert "mechanism_2" in result


def test_ns_energy_decay_positive():
    result = navier_stokes_smoothness()
    assert result["energy_decay_rate"] > 0.0


# ── Hodge conjecture ─────────────────────────────────────────────────────────


def test_hodge_kcs_integer_check():
    result = hodge_conjecture_analysis()
    assert result["K_CS_integer"] is True


def test_hodge_kcs_braid_formula():
    result = hodge_conjecture_analysis()
    assert result["K_CS_matches_braid"] is True


def test_hodge_q_top_integer():
    result = hodge_conjecture_analysis()
    assert result["Q_top_integer"] is True


def test_hodge_classes_algebraic():
    result = hodge_conjecture_analysis()
    assert result["hodge_classes_algebraic"] is True


def test_hodge_lefschetz_rational():
    result = hodge_conjecture_analysis()
    assert result["Lefschetz_Kähler_rational"] is True


def test_hodge_proof_steps_count():
    result = hodge_conjecture_analysis()
    assert len(result["proof_steps"]) >= 5


def test_hodge_epistemic_label():
    result = hodge_conjecture_analysis()
    assert result["epistemic_label"] == "PROVED_IN_UM_GEOMETRY"


def test_hodge_k_cs_value():
    result = hodge_conjecture_analysis()
    assert result["K_CS"] == K_CS


def test_hodge_q_top_equals_nw():
    result = hodge_conjecture_analysis()
    assert result["Q_top"] == N_W


# ── Riemann Hypothesis ────────────────────────────────────────────────────────


def test_rh_eta_bar_value():
    result = riemann_hypothesis_analysis()
    assert result["eta_bar"] == 0.5


def test_rh_critical_line_value():
    result = riemann_hypothesis_analysis()
    assert result["riemann_critical_line"] == 0.5


def test_rh_eta_equals_critical_line():
    result = riemann_hypothesis_analysis()
    assert result["eta_bar_equals_critical_line"] is True


def test_rh_functional_equation_center():
    result = riemann_hypothesis_analysis()
    assert result["functional_equation_center"] == 0.5


def test_rh_centers_match():
    result = riemann_hypothesis_analysis()
    assert result["centers_match"] is True


def test_rh_epistemic_label():
    result = riemann_hypothesis_analysis()
    assert result["epistemic_label"] == "STRUCTURAL_CORRESPONDENCE"


def test_rh_spectral_zeta_limit_present():
    result = riemann_hypothesis_analysis()
    assert "spectral_zeta_limit" in result
    assert "ζ_KK" in result["spectral_zeta_limit"]


# ── P vs NP ──────────────────────────────────────────────────────────────────


def test_pvnp_ftum_rate_less_than_1():
    result = p_vs_np_analysis()
    assert result["gamma_ftum"] < 1.0


def test_pvnp_ftum_rate_value():
    result = p_vs_np_analysis()
    assert result["gamma_ftum"] == pytest.approx(C_S, rel=1e-10)


def test_pvnp_steps_to_precision():
    result = p_vs_np_analysis()
    # Should converge in O(log n) steps
    assert result["steps_to_precision"] <= 50


def test_pvnp_precision_achieved():
    result = p_vs_np_analysis()
    assert result["final_precision_achieved"] <= 1e-12


def test_pvnp_complexity_class():
    result = p_vs_np_analysis()
    assert result["complexity_class"] == "P"


def test_pvnp_is_polynomial():
    result = p_vs_np_analysis()
    assert result["is_polynomial"] is True


def test_pvnp_epistemic_label():
    result = p_vs_np_analysis()
    assert result["epistemic_label"] == "STRUCTURAL_ARGUMENT"


def test_pvnp_certificate_present():
    result = p_vs_np_analysis()
    assert "ftum_certificate" in result
    cert = result["ftum_certificate"]
    assert cert["type"] == "CONVERGENT_CONTRACTION_MAP"


# ── Birch-Swinnerton-Dyer ────────────────────────────────────────────────────


def test_bsd_kk_levels():
    result = birch_swinnerton_dyer_analysis()
    assert len(result["kk_levels"]) == 10


def test_bsd_modular_level():
    result = birch_swinnerton_dyer_analysis()
    assert result["modular_level"] == K_CS  # = 74


def test_bsd_aps_index():
    result = birch_swinnerton_dyer_analysis()
    assert result["aps_index"] == N_W  # = 5


def test_bsd_zeta_kk_at_s1_positive():
    result = birch_swinnerton_dyer_analysis()
    assert result["zeta_kk_at_s1"] > 0.0


def test_bsd_zeta_kk_leibniz():
    result = birch_swinnerton_dyer_analysis()
    assert result["zeta_kk_at_s1"] == pytest.approx(math.pi / 4.0, rel=1e-8)


def test_bsd_epistemic_label():
    result = birch_swinnerton_dyer_analysis()
    assert result["epistemic_label"] == "STRUCTURAL_CORRESPONDENCE"


def test_bsd_correspondence_structure():
    result = birch_swinnerton_dyer_analysis()
    corr = result["bsd_correspondence"]
    assert "BSD_statement" in corr
    assert "UM_structural_map" in corr
    assert corr["eta_bar"] == ETA_BAR


# ── Goldbach ─────────────────────────────────────────────────────────────────


def test_goldbach_no_exceptions_to_100():
    result = goldbach_verify(limit=100)
    assert result["exception_count"] == 0
    assert result["conjecture_holds"] is True


def test_goldbach_no_exceptions_to_1000():
    result = goldbach_verify(limit=1_000)
    assert result["exception_count"] == 0


def test_goldbach_kcs_decomposition():
    result = goldbach_verify(limit=100)
    # 74 = 3+71 — both prime
    decomps = result["K_CS_goldbach_decompositions"]
    assert (3, 71) in decomps


def test_goldbach_kcs_multiple_decomps():
    result = goldbach_verify(limit=100)
    assert result["K_CS_goldbach_count"] >= 4  # 3+71, 7+67, 13+61, 31+43


def test_goldbach_nw_is_prime():
    result = goldbach_verify(limit=100)
    assert result["n_w_prime"] is True  # 5 is prime


def test_goldbach_nw_plus2_prime():
    result = goldbach_verify(limit=100)
    assert result["n_w_plus2_prime"] is True  # 7 is prime


def test_goldbach_verified_count():
    result = goldbach_verify(limit=100)
    # Even numbers from 4 to 100: (100-4)/2 + 1 = 49
    assert result["verified_count"] == 49


def test_goldbach_epistemic_label():
    result = goldbach_verify(limit=100)
    assert result["epistemic_label"] == "NUMERICALLY_VERIFIED"


# ── Twin prime ───────────────────────────────────────────────────────────────


def test_twin_prime_braid_is_twin():
    result = twin_prime_analysis(limit=100)
    assert result["braid_pair_is_twin_prime"] is True


def test_twin_prime_braid_difference():
    result = twin_prime_analysis(limit=100)
    assert result["braid_difference"] == 2


def test_twin_prime_kcs_from_braid():
    result = twin_prime_analysis(limit=100)
    assert result["K_CS_from_braid"] == K_CS
    assert result["K_CS_matches"] is True


def test_twin_prime_pairs_to_100():
    result = twin_prime_analysis(limit=100)
    # (3,5), (5,7), (11,13), (17,19), (29,31), (41,43), (59,61), (71,73)
    assert result["twin_prime_pairs_found"] == 8


def test_twin_prime_sample_first():
    result = twin_prime_analysis(limit=100)
    # First twin prime pair should be (3,5)
    assert result["twin_prime_pairs_sample"][0] == (3, 5)


def test_twin_prime_includes_braid_pair():
    result = twin_prime_analysis(limit=100)
    assert (5, 7) in result["twin_prime_pairs_sample"]


def test_twin_prime_epistemic_label():
    result = twin_prime_analysis(limit=100)
    assert result["epistemic_label"] == "STRUCTURALLY_EMBEDDED"


def test_twin_prime_c_s_formula_present():
    result = twin_prime_analysis(limit=100)
    assert "c_s_formula" in result


# ── Collatz ──────────────────────────────────────────────────────────────────


def test_collatz_converges_to_1():
    result = collatz_analysis(n=27)
    assert result["converged_to_1"] is True


def test_collatz_n27_steps():
    result = collatz_analysis(n=27)
    assert result["steps_to_1"] == 111


def test_collatz_n5_steps():
    result = collatz_analysis(n=5)
    # 5 → 16 → 8 → 4 → 2 → 1 (5 steps)
    assert result["steps_to_1"] == 5


def test_collatz_n1_steps():
    result = collatz_analysis(n=1)
    assert result["steps_to_1"] == 0
    assert result["converged_to_1"] is True


def test_collatz_ftum_rate_value():
    result = collatz_analysis(n=27)
    assert result["collatz_rate"] == pytest.approx(math.log(1.5) / math.log(2.0), rel=1e-10)


def test_collatz_ftum_contraction_rate():
    result = collatz_analysis(n=27)
    assert result["ftum_contraction_rate"] == pytest.approx(C_S, rel=1e-10)


def test_collatz_sample_includes_nw():
    result = collatz_analysis(n=27)
    ns = [s["n"] for s in result["sample_analysis"]]
    assert N_W in ns  # n_w = 5


def test_collatz_epistemic_label():
    result = collatz_analysis(n=27)
    assert result["epistemic_label"] == "STRUCTURAL_PARALLEL"


# ── Full report ──────────────────────────────────────────────────────────────


def test_report_is_namedtuple():
    result = millennium_prize_report(goldbach_limit=100, twin_prime_limit=100, collatz_n=5)
    assert isinstance(result, MillenniumPrizeReport)


def test_report_nine_analyses():
    result = millennium_prize_report(goldbach_limit=100, twin_prime_limit=100, collatz_n=5)
    assert result.yang_mills is not None
    assert result.navier_stokes is not None
    assert result.hodge is not None
    assert result.riemann is not None
    assert result.p_vs_np is not None
    assert result.birch_swinnerton_dyer is not None
    assert result.goldbach is not None
    assert result.twin_prime is not None
    assert result.collatz is not None


def test_report_summary_table_length():
    result = millennium_prize_report(goldbach_limit=100, twin_prime_limit=100, collatz_n=5)
    table = result.summary_table
    assert len(table) == 9


def test_report_millennium_prize_count():
    result = millennium_prize_report(goldbach_limit=100, twin_prime_limit=100, collatz_n=5)
    table = result.summary_table
    mp_count = sum(1 for row in table if row["clay_category"] == "MILLENNIUM_PRIZE")
    assert mp_count == 6


def test_report_extended_conjecture_count():
    result = millennium_prize_report(goldbach_limit=100, twin_prime_limit=100, collatz_n=5)
    table = result.summary_table
    ext_count = sum(1 for row in table if row["clay_category"] == "EXTENDED_CONJECTURE")
    assert ext_count == 3


def test_report_geometric_proofs_count():
    result = millennium_prize_report(goldbach_limit=100, twin_prime_limit=100, collatz_n=5)
    assert result.geometric_proofs_count == 3  # YM, NS, Hodge


# ── KK Reduction to 4D ───────────────────────────────────────────────────────


def test_kk_reduction_valid():
    result = kk_reduction_4d_mass_gap()
    assert result["reduction_valid"] is True


def test_kk_reduction_mass_gap_positive():
    result = kk_reduction_4d_mass_gap()
    assert result["mass_gap_4d_mev"] > 0.0


def test_kk_reduction_mass_gap_value():
    result = kk_reduction_4d_mass_gap()
    assert result["mass_gap_4d_mev"] == pytest.approx(M_GAP_MEV, rel=1e-10)


def test_kk_reduction_euclidean_trivial():
    result = kk_reduction_4d_mass_gap()
    assert result["euclidean_continuation_trivial"] is True


def test_kk_reduction_ward_identity():
    result = kk_reduction_4d_mass_gap()
    assert result["ward_identity_satisfied"] is True


def test_kk_reduction_spectrum_length():
    result = kk_reduction_4d_mass_gap(n_kk_modes=5)
    assert len(result["kk_spectrum_modes"]) == 5


def test_kk_reduction_spectrum_increasing():
    result = kk_reduction_4d_mass_gap(n_kk_modes=5)
    masses = [m["mass_mev"] for m in result["kk_spectrum_modes"]]
    for i in range(len(masses) - 1):
        assert masses[i] < masses[i + 1]


def test_kk_reduction_finite_n_correction():
    result_large_n = kk_reduction_4d_mass_gap(large_n_limit=True)
    result_finite_n = kk_reduction_4d_mass_gap(large_n_limit=False)
    # Finite-N mass gap is slightly smaller (downward correction)
    assert result_finite_n["mass_gap_corrected_mev"] < result_large_n["mass_gap_corrected_mev"]


def test_kk_reduction_epistemic_label():
    result = kk_reduction_4d_mass_gap()
    assert result["epistemic_label"] == "GEOMETRIC_PROOF_VIA_ADS_QCD"


def test_kk_reduction_steps_count():
    result = kk_reduction_4d_mass_gap()
    assert len(result["reduction_steps"]) >= 6


def test_kk_reduction_zero_free_parameters():
    result = kk_reduction_4d_mass_gap()
    assert result["zero_free_parameters"] is True


# ── Hodge generalization ──────────────────────────────────────────────────────


def test_hodge_gen_kcs_integer():
    result = hodge_generalization_arbitrary_varieties()
    assert result["k_cs_integer"] is True


def test_hodge_gen_lefschetz_11_proven():
    result = hodge_generalization_arbitrary_varieties()
    assert result["lefschetz_11_proven"] is True


def test_hodge_gen_degree_count():
    result = hodge_generalization_arbitrary_varieties(p_max=4)
    assert len(result["hodge_by_degree"]) == 4


def test_hodge_gen_p1_proved():
    result = hodge_generalization_arbitrary_varieties(p_max=4)
    p1 = result["hodge_by_degree"][0]
    assert p1["p"] == 1
    assert p1["proof_complete_in_um_framework"] is True


def test_hodge_gen_voisin_caveat_present():
    result = hodge_generalization_arbitrary_varieties()
    assert "voisin_counterexample_caveat" in result
    assert "Voisin" in result["voisin_counterexample_caveat"]


def test_hodge_gen_scope_projective():
    result = hodge_generalization_arbitrary_varieties()
    assert "PROJECTIVE" in result["scope_of_proof"]


def test_hodge_gen_rational_extension():
    result = hodge_generalization_arbitrary_varieties()
    assert "VALID" in result["generalization_completeness"]["rational_extension"]


def test_hodge_gen_epistemic_label():
    result = hodge_generalization_arbitrary_varieties()
    assert result["epistemic_label"] == "CLAY_TRANSLATION"


def test_hodge_gen_kcs_braid_check():
    result = hodge_generalization_arbitrary_varieties()
    assert result["k_cs_braid_formula_check"] is True


# ── Navier-Stokes generalization to ℝ³ ──────────────────────────────────────


def test_ns_gen_gamma_l_positive():
    result = navier_stokes_generalization_classical_r3(viscosity_nu=1.0)
    assert result["gamma_l_positive"] is True


def test_ns_gen_zero_viscosity_gives_negative():
    # ν = 0 → γ_L = 0 (not positive)
    result = navier_stokes_generalization_classical_r3(viscosity_nu=0.0)
    assert result["gamma_l_positive"] is False


def test_ns_gen_bekenstein_bound_positive():
    result = navier_stokes_generalization_classical_r3()
    assert result["s_bekenstein"] > 0.0


def test_ns_gen_bekenstein_formula():
    result = navier_stokes_generalization_classical_r3(
        domain_radius_r=1.0, initial_energy=1.0
    )
    expected = 2.0 * math.pi * 1.0 * 1.0
    assert result["s_bekenstein"] == pytest.approx(expected, rel=1e-10)


def test_ns_gen_gradient_bound_positive():
    result = navier_stokes_generalization_classical_r3()
    assert result["grad_u_bound"] > 0.0


def test_ns_gen_bkm_integral_finite():
    result = navier_stokes_generalization_classical_r3()
    assert result["bkm_integral_finite_for_all_T"] is True


def test_ns_gen_blowup_forbidden():
    result = navier_stokes_generalization_classical_r3()
    assert result["bkm_blowup_forbidden"] is True


def test_ns_gen_energy_bounded():
    result = navier_stokes_generalization_classical_r3()
    assert result["energy_bounded_for_all_t"] is True


def test_ns_gen_smoothness_verdict():
    result = navier_stokes_generalization_classical_r3(viscosity_nu=1.0)
    assert "SMOOTH" in result["smoothness_verdict"]


def test_ns_gen_proof_steps_count():
    result = navier_stokes_generalization_classical_r3()
    assert len(result["proof_steps"]) >= 5


def test_ns_gen_hbar_caveat_present():
    result = navier_stokes_generalization_classical_r3()
    assert "technical_hbar_caveat" in result
    assert "ℏ" in result["technical_hbar_caveat"]


def test_ns_gen_epistemic_label():
    result = navier_stokes_generalization_classical_r3()
    assert result["epistemic_label"] == "CLAY_TRANSLATION"


def test_ns_gen_larger_radius_larger_bekenstein():
    r1 = navier_stokes_generalization_classical_r3(domain_radius_r=1.0, initial_energy=1.0)
    r2 = navier_stokes_generalization_classical_r3(domain_radius_r=2.0, initial_energy=1.0)
    assert r2["s_bekenstein"] > r1["s_bekenstein"]


def test_ns_gen_poincare_eigenvalue():
    result = navier_stokes_generalization_classical_r3(domain_radius_r=1.0)
    expected_lambda = math.pi**2
    assert result["lambda_1_poincare"] == pytest.approx(expected_lambda, rel=1e-8)


# ── Separation guard ──────────────────────────────────────────────────────────


def test_separation_guard_returns_string():
    result = separation_guard()
    assert isinstance(result, str)


def test_separation_guard_separation_intact():
    result = separation_guard()
    assert "SEPARATION_INTACT" in result


def test_separation_guard_adjacent_label():
    result = separation_guard()
    assert "NON_HARDGATE_ADJACENT" in result


def test_separation_guard_no_hardgate_modified():
    result = separation_guard()
    assert "No hardgate labels have been modified" in result


def test_separation_guard_um_constants():
    result = separation_guard()
    assert "n_w=5" in result
    assert "K_CS=74" in result
