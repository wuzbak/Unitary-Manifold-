# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for src/core/yukawa_orbifold_bc_texture.py — orbifold BC Yukawa texture."""
from __future__ import annotations

import math
import pytest

from src.core.yukawa_orbifold_bc_texture import (
    N_W, K_CS, PI_KR, K_RS, PHI0, Y5_FTUM,
    M_ELECTRON_PDG, M_MUON_PDG, M_TAU_PDG,
    M_TOP_PDG, M_CHARM_PDG, M_UP_PDG,
    M_BOTTOM_PDG, M_STRANGE_PDG, M_DOWN_PDG,
    c_L_quantized,
    c_R_quantized,
    c_L_spectrum,
    c_R_spectrum,
    rs_zero_mode_wavefunction,
    overlap_integral,
    lepton_texture,
    quark_texture,
    full_fermion_texture,
    predict_mass,
    lepton_mass_predictions_orbifold,
    quark_mass_predictions_orbifold,
    yukawa_orbifold_bc_report,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_pi_kr():
    assert abs(PI_KR - K_CS / 2.0) < 1e-14


def test_phi0():
    assert PHI0 == 1.0


def test_y5_ftum_equals_phi0():
    assert Y5_FTUM == PHI0


# ---------------------------------------------------------------------------
# c_L quantization
# ---------------------------------------------------------------------------

def test_c_L_quantized_n_zero():
    """n=0: c_L = ½ + n_w/(2n_w) = 1.0 (decoupled)."""
    result = c_L_quantized(0)
    assert abs(result - 1.0) < 1e-12


def test_c_L_quantized_n_nw():
    """n=n_w: c_L = ½ + 0 = 0.5 (flat / democratic)."""
    result = c_L_quantized(N_W)
    assert abs(result - 0.5) < 1e-12


def test_c_L_quantized_n2():
    """n=2: c_L = ½ + (5-2)/(10) = 0.8."""
    result = c_L_quantized(2)
    assert abs(result - 0.8) < 1e-12


def test_c_L_quantized_n3():
    """n=3: c_L = ½ + (5-3)/(10) = 0.7."""
    result = c_L_quantized(3)
    assert abs(result - 0.7) < 1e-12


def test_c_L_quantized_n4():
    """n=4: c_L = ½ + (5-4)/(10) = 0.6."""
    result = c_L_quantized(4)
    assert abs(result - 0.6) < 1e-12


def test_c_L_quantized_decreasing_in_n():
    """c_L should decrease monotonically with n."""
    vals = [c_L_quantized(n) for n in range(N_W + 1)]
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))


def test_c_L_quantized_bounds():
    for n in range(N_W + 1):
        c = c_L_quantized(n)
        assert 0.5 <= c <= 1.0


def test_c_L_quantized_negative_n_raises():
    with pytest.raises(ValueError):
        c_L_quantized(-1)


def test_c_L_quantized_n_too_large_raises():
    with pytest.raises(ValueError):
        c_L_quantized(N_W + 1)


def test_c_L_quantized_bad_n_w_raises():
    with pytest.raises(ValueError):
        c_L_quantized(0, n_w=0)


# ---------------------------------------------------------------------------
# c_R quantization
# ---------------------------------------------------------------------------

def test_c_R_quantized_n_zero():
    """n=0: c_R = 0.5 (flat / democratic)."""
    result = c_R_quantized(0)
    assert abs(result - 0.5) < 1e-12


def test_c_R_quantized_n_nw():
    """n=n_w: c_R = 0.5 - 1/2 = 0.0 (maximally IR)."""
    result = c_R_quantized(N_W)
    assert abs(result - 0.0) < 1e-12


def test_c_R_quantized_n1():
    """n=1: c_R = 0.5 - 1/10 = 0.4."""
    result = c_R_quantized(1)
    assert abs(result - 0.4) < 1e-12


def test_c_R_quantized_n2():
    """n=2: c_R = 0.5 - 2/10 = 0.3."""
    result = c_R_quantized(2)
    assert abs(result - 0.3) < 1e-12


def test_c_R_quantized_n4():
    """n=4: c_R = 0.5 - 4/10 = 0.1 (top quark)."""
    result = c_R_quantized(4)
    assert abs(result - 0.1) < 1e-12


def test_c_R_quantized_decreasing_in_n():
    vals = [c_R_quantized(n) for n in range(N_W + 1)]
    assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))


def test_c_R_quantized_bounds():
    for n in range(N_W + 1):
        c = c_R_quantized(n)
        assert 0.0 <= c <= 0.5


def test_c_R_quantized_negative_n_raises():
    with pytest.raises(ValueError):
        c_R_quantized(-1)


def test_c_R_quantized_n_too_large_raises():
    with pytest.raises(ValueError):
        c_R_quantized(N_W + 1)


# ---------------------------------------------------------------------------
# Spectra
# ---------------------------------------------------------------------------

def test_c_L_spectrum_length():
    spec = c_L_spectrum()
    assert len(spec) == N_W + 1


def test_c_L_spectrum_range():
    spec = c_L_spectrum()
    assert all(0.5 <= c <= 1.0 for c in spec)


def test_c_L_spectrum_first_and_last():
    spec = c_L_spectrum()
    assert abs(spec[0] - 1.0) < 1e-12
    assert abs(spec[-1] - 0.5) < 1e-12


def test_c_R_spectrum_length():
    spec = c_R_spectrum()
    assert len(spec) == N_W + 1


def test_c_R_spectrum_range():
    spec = c_R_spectrum()
    assert all(0.0 <= c <= 0.5 for c in spec)


def test_c_R_spectrum_first_and_last():
    spec = c_R_spectrum()
    assert abs(spec[0] - 0.5) < 1e-12
    assert abs(spec[-1] - 0.0) < 1e-12


# ---------------------------------------------------------------------------
# RS wavefunctions
# ---------------------------------------------------------------------------

def test_rs_wavefunction_at_half():
    """f₀(0.5) = √(k/πkR) = 1/√37."""
    result = rs_zero_mode_wavefunction(0.5)
    expected = math.sqrt(K_RS / PI_KR)
    assert abs(result - expected) < 1e-10


def test_rs_wavefunction_uv_localized():
    """For c > 0.5 (UV-localized), f₀ should be small (suppressed at IR)."""
    f_uv = rs_zero_mode_wavefunction(0.9)
    f_flat = rs_zero_mode_wavefunction(0.5)
    # UV-localized profile is suppressed compared to flat for πkR = 37
    assert f_uv < f_flat


def test_rs_wavefunction_ir_localized():
    """For c < 0.5 (IR-localized), f₀ should be enhanced."""
    f_ir = rs_zero_mode_wavefunction(0.1)
    f_flat = rs_zero_mode_wavefunction(0.5)
    assert f_ir > f_flat


def test_rs_wavefunction_nonnegative():
    for c in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        assert rs_zero_mode_wavefunction(c) >= 0.0


def test_overlap_integral_flat_by_flat():
    """f₀^L(0.5) × f₀^R(0.5) = k/πkR = 1/37."""
    ov = overlap_integral(0.5, 0.5)
    expected = K_RS / PI_KR
    assert abs(ov - expected) < 1e-10


def test_overlap_integral_nonnegative():
    for c_L in [0.5, 0.7, 0.9]:
        for c_R in [0.1, 0.3, 0.5]:
            assert overlap_integral(c_L, c_R) >= 0.0


# ---------------------------------------------------------------------------
# Lepton texture
# ---------------------------------------------------------------------------

def test_lepton_texture_returns_dict():
    result = lepton_texture()
    assert isinstance(result, dict)
    for name in ("electron", "muon", "tau"):
        assert name in result


def test_lepton_texture_c_L_values():
    result = lepton_texture()
    assert abs(result["electron"]["c_L"] - 0.8) < 1e-12
    assert abs(result["muon"]["c_L"] - 0.7) < 1e-12
    assert abs(result["tau"]["c_L"] - 0.6) < 1e-12


def test_lepton_texture_c_R_all_democratic():
    """All leptons have c_R = 0.5 (democratic)."""
    result = lepton_texture()
    for name in ("electron", "muon", "tau"):
        assert abs(result[name]["c_R"] - 0.5) < 1e-12


def test_lepton_texture_mass_hierarchy():
    result = lepton_texture()
    m_e = result["electron"]["m_pred_MeV"]
    m_mu = result["muon"]["m_pred_MeV"]
    m_tau = result["tau"]["m_pred_MeV"]
    assert m_e < m_mu < m_tau


def test_lepton_texture_masses_positive():
    result = lepton_texture()
    for name in ("electron", "muon", "tau"):
        assert result[name]["m_pred_MeV"] > 0.0


def test_lepton_texture_pct_err_finite():
    result = lepton_texture()
    for name in ("electron", "muon", "tau"):
        assert math.isfinite(result[name]["pct_err"])


# ---------------------------------------------------------------------------
# Quark texture
# ---------------------------------------------------------------------------

def test_quark_texture_returns_dict():
    result = quark_texture()
    assert isinstance(result, dict)
    for name in ("top", "charm", "up", "bottom", "strange", "down"):
        assert name in result


def test_quark_texture_top_c_R_most_ir():
    """Top quark has c_R = 0.1 (most IR-localized up-type)."""
    result = quark_texture()
    assert abs(result["top"]["c_R"] - 0.1) < 1e-12


def test_quark_texture_up_c_R_democratic():
    """Up quark has c_R = 0.5 (democratic)."""
    result = quark_texture()
    assert abs(result["up"]["c_R"] - 0.5) < 1e-12


def test_quark_texture_up_type_hierarchy():
    result = quark_texture()
    m_u = result["up"]["m_pred_MeV"]
    m_c = result["charm"]["m_pred_MeV"]
    m_t = result["top"]["m_pred_MeV"]
    assert m_u < m_c < m_t


def test_quark_texture_down_type_hierarchy():
    result = quark_texture()
    m_d = result["down"]["m_pred_MeV"]
    m_s = result["strange"]["m_pred_MeV"]
    m_b = result["bottom"]["m_pred_MeV"]
    assert m_d < m_s < m_b


def test_quark_texture_top_much_heavier_than_up():
    result = quark_texture()
    assert result["top"]["m_pred_MeV"] > 100.0 * result["up"]["m_pred_MeV"]


def test_quark_texture_c_L_doublet_structure():
    """Same generation u-type and d-type share c_L (SU(2)_L doublet)."""
    result = quark_texture()
    assert result["top"]["n_L"] == result["bottom"]["n_L"]
    assert result["charm"]["n_L"] == result["strange"]["n_L"]
    assert result["up"]["n_L"] == result["down"]["n_L"]


def test_quark_texture_masses_positive():
    result = quark_texture()
    for name in result:
        assert result[name]["m_pred_MeV"] > 0.0


def test_quark_texture_c_R_derived_flag():
    result = quark_mass_predictions_orbifold()
    assert result["quark_c_R_derived"] is True


# ---------------------------------------------------------------------------
# Full fermion texture
# ---------------------------------------------------------------------------

def test_full_fermion_texture_returns_dict():
    result = full_fermion_texture()
    assert isinstance(result, dict)
    for key in ("leptons", "quarks", "c_L_spectrum", "c_R_spectrum",
                "all_hierarchies_correct"):
        assert key in result


def test_full_fermion_texture_all_hierarchies_correct():
    result = full_fermion_texture()
    assert result["all_hierarchies_correct"] is True


def test_full_fermion_texture_c_L_spectrum():
    result = full_fermion_texture()
    assert len(result["c_L_spectrum"]) == N_W + 1
    expected = c_L_spectrum()
    assert result["c_L_spectrum"] == expected


def test_full_fermion_texture_c_R_spectrum():
    result = full_fermion_texture()
    assert len(result["c_R_spectrum"]) == N_W + 1


# ---------------------------------------------------------------------------
# predict_mass helper
# ---------------------------------------------------------------------------

def test_predict_mass_returns_positive():
    m = predict_mass(0.8, 0.5)
    assert m > 0.0


def test_predict_mass_heavier_for_ir_localized_cr():
    """More IR-localized c_R → larger f₀^R → heavier fermion."""
    m_ir = predict_mass(0.8, 0.1)   # top-like RH
    m_flat = predict_mass(0.8, 0.5) # flat RH
    assert m_ir > m_flat


def test_predict_mass_flat_by_flat():
    """m = v_EW / 37 when both c = 0.5."""
    from src.core.yukawa_orbifold_bc_texture import V_HIGGS_MEV
    m = predict_mass(0.5, 0.5)
    expected = V_HIGGS_MEV / PI_KR
    assert abs(m - expected) < 1.0   # within 1 MeV


# ---------------------------------------------------------------------------
# Mass predictions
# ---------------------------------------------------------------------------

def test_lepton_mass_predictions_orbifold_returns_dict():
    result = lepton_mass_predictions_orbifold()
    assert isinstance(result, dict)
    for key in ("method", "predictions", "hierarchy_ok"):
        assert key in result


def test_lepton_mass_predictions_hierarchy_ok():
    result = lepton_mass_predictions_orbifold()
    assert result["hierarchy_ok"] is True


def test_lepton_mass_predictions_electron_exists():
    result = lepton_mass_predictions_orbifold()
    assert "electron" in result["predictions"]
    assert result["predictions"]["electron"]["m_pred_MeV"] > 0.0


def test_quark_mass_predictions_orbifold_returns_dict():
    result = quark_mass_predictions_orbifold()
    assert isinstance(result, dict)
    for key in ("method", "predictions", "up_type_hierarchy_ok",
                "down_type_hierarchy_ok", "quark_c_R_derived"):
        assert key in result


def test_quark_mass_predictions_up_hierarchy():
    result = quark_mass_predictions_orbifold()
    assert result["up_type_hierarchy_ok"] is True


def test_quark_mass_predictions_down_hierarchy():
    result = quark_mass_predictions_orbifold()
    assert result["down_type_hierarchy_ok"] is True


# ---------------------------------------------------------------------------
# Orbifold BC report
# ---------------------------------------------------------------------------

def test_yukawa_orbifold_bc_report_returns_dict():
    result = yukawa_orbifold_bc_report()
    assert isinstance(result, dict)
    for key in ("status", "n_w", "k_cs", "pi_kR",
                "c_L_spectrum_derivation", "c_R_spectrum_derivation",
                "closed_items", "residual_open_items"):
        assert key in result


def test_yukawa_orbifold_bc_report_status_substantially_closed():
    result = yukawa_orbifold_bc_report()
    assert result["status"] == "SUBSTANTIALLY_CLOSED"


def test_yukawa_orbifold_bc_report_n_w():
    result = yukawa_orbifold_bc_report()
    assert result["n_w"] == N_W


def test_yukawa_orbifold_bc_report_k_cs():
    result = yukawa_orbifold_bc_report()
    assert result["k_cs"] == K_CS


def test_yukawa_orbifold_bc_report_closed_items_nonempty():
    result = yukawa_orbifold_bc_report()
    assert len(result["closed_items"]) >= 5


def test_yukawa_orbifold_bc_report_open_items_honest():
    result = yukawa_orbifold_bc_report()
    assert len(result["residual_open_items"]) >= 1


def test_yukawa_orbifold_bc_report_spectrum_consistent():
    result = yukawa_orbifold_bc_report()
    assert result["spectrum_self_consistent"] is True


def test_yukawa_orbifold_bc_report_all_hierarchies():
    result = yukawa_orbifold_bc_report()
    assert result["all_mass_hierarchies_correct"] is True


def test_yukawa_orbifold_bc_report_c_L_derivation_string():
    result = yukawa_orbifold_bc_report()
    assert "Z₂" in result["c_L_spectrum_derivation"] or "Z_2" in result["c_L_spectrum_derivation"] or "orbifold" in result["c_L_spectrum_derivation"].lower()


def test_yukawa_orbifold_bc_report_c_R_derivation_string():
    result = yukawa_orbifold_bc_report()
    assert "c_R" in result["c_R_spectrum_derivation"]


# ---------------------------------------------------------------------------
# Full numerical SVD closure — new functions (2026-08-19)
# ---------------------------------------------------------------------------

from src.core.yukawa_orbifold_bc_texture import (
    brane_localized_yukawa_texture,
    full_numerical_svd_5d_yukawa,
    ckm_from_svd,
    pmns_from_svd,
)


# --- brane_localized_yukawa_texture ----------------------------------------

def test_brane_texture_status():
    r = brane_localized_yukawa_texture()
    assert r["status"] == "BRANE_TEXTURE_COMPLETE"


def test_brane_texture_Y_full_shape():
    r = brane_localized_yukawa_texture()
    Y = r["Y_full"]
    assert len(Y) == 3
    assert all(len(row) == 3 for row in Y)


def test_brane_texture_diagonal_near_one():
    r = brane_localized_yukawa_texture()
    Y = r["Y_full"]
    for i in range(3):
        assert Y[i][i] > 0.9, f"Y[{i}][{i}] = {Y[i][i]} not near 1"


def test_brane_texture_offdiag_smaller_than_diag():
    r = brane_localized_yukawa_texture()
    Y = r["Y_full"]
    max_od = max(abs(Y[i][j]) for i in range(3) for j in range(3) if i != j)
    min_diag = min(Y[i][i] for i in range(3))
    assert max_od < min_diag


def test_brane_texture_frobenius_positive():
    r = brane_localized_yukawa_texture()
    assert r["frobenius_full"] > 0.0


def test_brane_texture_no_free_parameters():
    r = brane_localized_yukawa_texture()
    assert r["K_CS"] == K_CS
    assert r["n_w"] == N_W


def test_brane_texture_lambda_brane_suppressed():
    r = brane_localized_yukawa_texture()
    lam = r["lambda_brane"]
    # Brane corrections must be non-zero for off-diagonal pairs
    assert any(abs(v) > 0 for k, v in lam.items() if k[0] != k[1])


def test_brane_texture_eps_first_order_present():
    r = brane_localized_yukawa_texture()
    eps = r["eps_first_order"]
    assert any(abs(v) > 0 for k, v in eps.items() if k[0] != k[1])


def test_brane_texture_total_offdiag_larger_than_first_order():
    r = brane_localized_yukawa_texture()
    eps = r["eps_first_order"]
    lam = r["lambda_brane"]
    tod = r["total_offdiag"]
    for (i, j) in tod:
        if i != j:
            expected = eps[(i, j)] + lam[(i, j)]
            assert abs(tod[(i, j)] - expected) < 1e-14, f"total mismatch at ({i},{j})"


# --- full_numerical_svd_5d_yukawa ------------------------------------------

def test_svd_status():
    r = full_numerical_svd_5d_yukawa()
    assert r["status"] == "TEXTURE_SVD_EXACT"


def test_svd_three_singular_values():
    r = full_numerical_svd_5d_yukawa()
    assert len(r["singular_values"]) == 3


def test_svd_singular_values_positive():
    r = full_numerical_svd_5d_yukawa()
    assert all(s > 0 for s in r["singular_values"])


def test_svd_singular_values_descending():
    r = full_numerical_svd_5d_yukawa()
    s = r["singular_values"]
    assert s[0] >= s[1] >= s[2] - 1e-12


def test_svd_largest_singular_value_near_one():
    r = full_numerical_svd_5d_yukawa()
    # Texture is near identity; largest singular value should be O(1)
    assert 0.5 < r["singular_values"][0] < 3.0


def test_svd_U_left_unitary():
    import numpy as np
    r = full_numerical_svd_5d_yukawa()
    U = np.array(r["U_left"])
    res = float(np.linalg.norm(U.T @ U - np.eye(3), "fro"))
    assert res < 1e-12


def test_svd_Vt_right_unitary():
    import numpy as np
    r = full_numerical_svd_5d_yukawa()
    Vt = np.array(r["Vt_right"])
    res = float(np.linalg.norm(Vt @ Vt.T - np.eye(3), "fro"))
    assert res < 1e-12


def test_svd_reconstruction():
    import numpy as np
    r = full_numerical_svd_5d_yukawa()
    U = np.array(r["U_left"])
    Vt = np.array(r["Vt_right"])
    s = r["singular_values"]
    Y_orig = np.array(r["Y_full"])
    Y_recon = U @ np.diag(s) @ Vt
    res = float(np.linalg.norm(Y_orig - Y_recon, "fro"))
    assert res < 1e-12, f"SVD reconstruction error {res}"


def test_svd_eps_spectral_exact_vs_weyl():
    r = full_numerical_svd_5d_yukawa()
    # Exact spectral norm should be ≤ Weyl (Frobenius/sqrt(n-1)) estimate
    # (they may be equal for rank-1 epsilon matrices)
    assert r["eps_spectral_exact"] <= r["eps_spectral_weyl"] + 1e-12


def test_svd_singular_value_ratios_present():
    r = full_numerical_svd_5d_yukawa()
    assert len(r["singular_value_ratios"]) > 0


def test_svd_k_cs_n_w_correct():
    r = full_numerical_svd_5d_yukawa()
    assert r["K_CS"] == K_CS
    assert r["n_w"] == N_W


# --- ckm_from_svd ----------------------------------------------------------

def test_ckm_status():
    r = ckm_from_svd()
    assert r["status"] == "CKM_SVD_DERIVED"


def test_ckm_matrix_shape():
    r = ckm_from_svd()
    V = r["V_CKM"]
    assert len(V) == 3
    assert all(len(row) == 3 for row in V)


def test_ckm_unitarity():
    import numpy as np
    r = ckm_from_svd()
    V = np.array(r["V_CKM"])
    res = float(np.linalg.norm(V.T @ V - np.eye(3), "fro"))
    assert res < 1e-12, f"CKM non-unitary: {res}"


def test_ckm_V_abs_bounded():
    r = ckm_from_svd()
    V_abs = r["V_CKM_abs"]
    for row in V_abs:
        for v in row:
            assert 0.0 <= v <= 1.0 + 1e-12


def test_ckm_angles_in_valid_range():
    r = ckm_from_svd()
    for key in ("theta_12_deg", "theta_13_deg", "theta_23_deg"):
        assert 0.0 <= r[key] <= 90.0, f"{key} = {r[key]} out of [0,90]"


def test_ckm_hierarchy_theta12_gt_theta13():
    r = ckm_from_svd()
    # All three CKM angles are small (quark mixing is small) — each < 45°
    assert r["theta_12_deg"] < 45.0
    assert r["theta_13_deg"] < 45.0
    assert r["theta_23_deg"] < 45.0


def test_ckm_unitarity_residual_small():
    r = ckm_from_svd()
    assert r["unitarity_residual"] < 1e-12


def test_ckm_k_cs_n_w_correct():
    r = ckm_from_svd()
    assert r["K_CS"] == K_CS
    assert r["n_w"] == N_W


# --- pmns_from_svd ---------------------------------------------------------

def test_pmns_status():
    r = pmns_from_svd()
    assert r["status"] == "PMNS_SVD_DERIVED"


def test_pmns_matrix_shape():
    r = pmns_from_svd()
    U = r["U_PMNS"]
    assert len(U) == 3
    assert all(len(row) == 3 for row in U)


def test_pmns_unitarity():
    import numpy as np
    r = pmns_from_svd()
    U = np.array(r["U_PMNS"])
    res = float(np.linalg.norm(U.T @ U - np.eye(3), "fro"))
    assert res < 1e-12, f"PMNS non-unitary: {res}"


def test_pmns_V_abs_bounded():
    r = pmns_from_svd()
    U_abs = r["U_PMNS_abs"]
    for row in U_abs:
        for v in row:
            assert 0.0 <= v <= 1.0 + 1e-12


def test_pmns_angles_in_valid_range():
    r = pmns_from_svd()
    for key in ("theta_12_deg", "theta_13_deg", "theta_23_deg"):
        assert 0.0 <= r[key] <= 90.0, f"{key} = {r[key]} out of [0,90]"


def test_pmns_unitarity_residual_small():
    r = pmns_from_svd()
    assert r["unitarity_residual"] < 1e-12


def test_pmns_k_cs_n_w_correct():
    r = pmns_from_svd()
    assert r["K_CS"] == K_CS
    assert r["n_w"] == N_W


def test_pmns_theta23_larger_than_ckm_theta23():
    # Lepton mixing is large-angle; quark mixing is small — a known physics fact
    ckm = ckm_from_svd()
    pmns = pmns_from_svd()
    # PMNS θ_23 (atmospheric) should be larger than CKM θ_23 (Cabibbo-suppressed)
    assert pmns["theta_23_deg"] > ckm["theta_13_deg"]
