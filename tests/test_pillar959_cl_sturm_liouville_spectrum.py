# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 959 — c_L Sturm-Liouville First Principles."""

import math
import pytest
from src.core.pillar959_cl_sturm_liouville_spectrum import (
    PILLAR_STATUS, PILLAR_VALID, N_W, K_CS, N_C, ALPHA_GUT_GEO, PI_KR, PHI0,
    CL_LADDER_P677,
    dirac_sl_problem_statement, sl_eigenvalue_spectrum,
    quark_lepton_cl_splitting, zero_mode_normalization,
    sl_spectrum_consistency_check, fallibility_update, pillar959_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "CL_SL_SPECTRUM_ANALYTICALLY_DERIVED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert N_C == 3
    assert abs(ALPHA_GUT_GEO - 3.0/74.0) < 1e-12
    assert abs(PI_KR - 37.0) < 1e-10


def test_cl_ladder_p677():
    assert len(CL_LADDER_P677) == 3
    assert CL_LADDER_P677[0] > CL_LADDER_P677[1] > CL_LADDER_P677[2]


def test_cl_gen1_exact():
    expected = 71.0 / 74.0
    assert abs(CL_LADDER_P677[0] - expected) < 1e-12


def test_cl_gen2_exact():
    expected = 141.0 / 148.0
    assert abs(CL_LADDER_P677[1] - expected) < 1e-12


def test_cl_gen3_exact():
    # Gen 3: 1 - N_c/K_CS - 2/(2*K_CS) = 1 - 3/74 - 1/74 = 70/74
    expected = 70.0 / 74.0
    assert abs(CL_LADDER_P677[2] - expected) < 1e-12


def test_dirac_sl_problem_statement():
    stmt = dirac_sl_problem_statement()
    assert "c_L" in stmt["equation"]
    assert "Z₂" in stmt["bc"]
    assert "c_L" in stmt["wavefunction"]


def test_sl_spectrum_base_cl():
    spec = sl_eigenvalue_spectrum()
    expected_base = 1.0 - N_C / K_CS
    assert abs(spec["cl_base"] - expected_base) < 1e-12


def test_sl_spectrum_step():
    spec = sl_eigenvalue_spectrum()
    expected_step = 0.5 / K_CS  # η̄/K_CS = 0.5/74
    assert abs(spec["cl_step"] - expected_step) < 1e-12


def test_sl_spectrum_matches_p677():
    spec = sl_eigenvalue_spectrum()
    for entry in spec["generation_spectrum"]:
        assert entry["agreement_with_p677"] is True


def test_sl_spectrum_all_agree():
    spec = sl_eigenvalue_spectrum()
    assert spec["all_agree_with_p677"] is True


def test_sl_spectrum_gen1():
    spec = sl_eigenvalue_spectrum()
    gen1 = spec["generation_spectrum"][0]
    assert gen1["generation"] == 1
    assert abs(gen1["c_l_sl"] - CL_LADDER_P677[0]) < 1e-12


def test_sl_spectrum_ordering():
    spec = sl_eigenvalue_spectrum()
    cls = [e["c_l_sl"] for e in spec["generation_spectrum"]]
    assert cls[0] > cls[1] > cls[2]


def test_quark_lepton_splitting_second_order():
    split = quark_lepton_cl_splitting()
    assert split["splitting_is_second_order"] is True
    assert split["splitting_within_texture_bound"] is True


def test_quark_correction_negative():
    split = quark_lepton_cl_splitting()
    assert split["quark_correction"] < 0


def test_quark_cl_smaller_than_lepton():
    split = quark_lepton_cl_splitting()
    for ql, ll in zip(split["quark_cl_gen123"], split["lepton_cl_gen123"]):
        assert ql < ll


def test_zero_mode_normalization_finite():
    for cl in CL_LADDER_P677:
        result = zero_mode_normalization(cl)
        # Large exponent → underflow is expected (UV-localized fermion)
        assert result["norm_integral_finite"] is True
        assert result["uv_localized"] is True
        # log_norm_N should be a finite (large negative) number
        assert math.isfinite(result["log_norm_N"])


def test_zero_mode_uv_localized():
    for cl in CL_LADDER_P677:
        result = zero_mode_normalization(cl)
        assert result["uv_localized"] is True  # c_L > 0.5


def test_sl_bisection_consistency():
    check = sl_spectrum_consistency_check()
    assert check["all_within_2_percent"] is True
    assert check["sl_vs_bisection_max_diff_pct"] < 2.0


def test_bisection_consistency_all_gens():
    check = sl_spectrum_consistency_check()
    for c in check["consistency_checks"]:
        assert c["within_2_percent"] is True


def test_fallibility_update():
    fb = fallibility_update()
    assert "SL_SPECTRUM_DERIVED" in fb["new_status"]
    assert fb["pillar"] == 959


def test_summary():
    s = pillar959_summary()
    assert s["pillar"] == 959
    assert s["valid"] is True
    assert len(s["derivation_chain"]) >= 5
