# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 437 — SPHEREx f_NL Preregistration Package."""
from __future__ import annotations

import hashlib
import math
import pytest

from src.core.pillar437_spherex_fnl_preregistration import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    RHO_BRAID,
    F_NL_DBI,
    DELTA_FNL_KK,
    F_NL_UM_CANONICAL,
    F_NL_RANGE_LOW,
    F_NL_RANGE_HIGH,
    SPHEREX_SIGMA_FNL,
    PLANCK_FNL_CENTRAL,
    PLANCK_FNL_SIGMA,
    PREREGISTRATION_HASH,
    PREREGISTRATION_STRING,
    dbi_fnl,
    kk_braid_correction,
    um_fnl_canonical,
    spherex_discriminating_power,
    falsification_routing,
    preregistration_hash_verify,
    preregistration_package,
    spherex_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'FNLPREREGISTERED_SPHEREX'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 437

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_rho_braid(self):
        assert abs(RHO_BRAID - 70.0 / 74.0) < 1e-12

    def test_f_nl_dbi_negative(self):
        assert F_NL_DBI < 0.0

    def test_f_nl_dbi_range(self):
        # Should be around -2.758
        assert -4.0 < F_NL_DBI < -2.0

    def test_delta_fnl_kk_positive(self):
        # KK correction moves f_NL toward zero
        assert DELTA_FNL_KK > 0.0

    def test_f_nl_canonical_in_range(self):
        assert F_NL_RANGE_LOW <= F_NL_UM_CANONICAL <= F_NL_RANGE_HIGH

    def test_f_nl_range_low(self):
        assert F_NL_RANGE_LOW == pytest.approx(-2.9, rel=0.01)

    def test_f_nl_range_high(self):
        assert F_NL_RANGE_HIGH == pytest.approx(-0.2, rel=0.01)

    def test_spherex_sigma_positive(self):
        assert SPHEREX_SIGMA_FNL > 0.0

    def test_planck_sigma_large(self):
        assert PLANCK_FNL_SIGMA > 40.0


class TestDbiFnl:
    def test_um_value(self):
        fnl = dbi_fnl(12.0 / 37.0)
        assert abs(fnl - F_NL_DBI) < 1e-10

    def test_formula_exact(self):
        c_s = 12.0 / 37.0
        expected = -(35.0 / 108.0) * ((37.0 / 12.0) ** 2 - 1.0)
        assert abs(dbi_fnl(c_s) - expected) < 1e-10

    def test_c_s_one_gives_zero(self):
        assert dbi_fnl(1.0) == pytest.approx(0.0, abs=1e-10)

    def test_smaller_c_s_larger_magnitude(self):
        assert abs(dbi_fnl(0.1)) > abs(dbi_fnl(0.5))

    def test_negative_always(self):
        for c_s in [0.1, 0.3, 0.5, 0.8, 0.99]:
            assert dbi_fnl(c_s) <= 0.0

    def test_invalid_c_s_raises(self):
        with pytest.raises(ValueError):
            dbi_fnl(0.0)
        with pytest.raises(ValueError):
            dbi_fnl(1.5)


class TestKkBraidCorrection:
    def test_um_values(self):
        corr = kk_braid_correction(C_S, RHO_BRAID)
        assert abs(corr - DELTA_FNL_KK) < 1e-10

    def test_positive(self):
        assert kk_braid_correction(C_S, RHO_BRAID) > 0.0

    def test_rho_zero_gives_zero(self):
        assert kk_braid_correction(C_S, 0.0) == pytest.approx(0.0, abs=1e-10)

    def test_rho_ge_one_gives_zero(self):
        assert kk_braid_correction(C_S, 1.0) == 0.0

    def test_magnitudes_reasonable(self):
        # KK correction should be of the same order as DBI
        corr = kk_braid_correction(C_S, RHO_BRAID)
        assert 1.0 < corr < 5.0


class TestUmFnlCanonical:
    def test_returns_dict(self):
        result = um_fnl_canonical()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = um_fnl_canonical()
        for key in ['f_nl_dbi', 'delta_fnl_kk', 'f_nl_canonical', 'range_low', 'range_high']:
            assert key in result

    def test_canonical_value(self):
        result = um_fnl_canonical()
        assert abs(result['f_nl_canonical'] - F_NL_UM_CANONICAL) < 1e-10

    def test_canonical_in_range(self):
        result = um_fnl_canonical()
        assert result['range_low'] <= result['f_nl_canonical'] <= result['range_high']

    def test_dbi_contribution(self):
        result = um_fnl_canonical()
        assert result['f_nl_dbi'] < 0.0

    def test_kk_contribution(self):
        result = um_fnl_canonical()
        assert result['delta_fnl_kk'] > 0.0


class TestSphereXDiscriminatingPower:
    def test_returns_dict(self):
        result = spherex_discriminating_power()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = spherex_discriminating_power()
        for key in ['tension_vs_lcdm_spherex', 'discrimination_ratio', 'verdict']:
            assert key in result

    def test_discrimination_ratio_large(self):
        result = spherex_discriminating_power()
        assert result['discrimination_ratio'] > 5.0

    def test_dbi_tension_positive(self):
        result = spherex_discriminating_power()
        assert result['tension_dbi_vs_lcdm_spherex'] > 0.0

    def test_verdict_is_string(self):
        result = spherex_discriminating_power()
        assert isinstance(result['verdict'], str)


class TestFalsificationRouting:
    def test_inside_range_is_pass(self):
        result = falsification_routing(-1.5, 1.6)
        assert result['verdict'] == 'PASS'

    def test_near_boundary_pass(self):
        # Just inside theory band
        result = falsification_routing(-2.8, 1.6)
        assert result['verdict'] == 'PASS'

    def test_moderately_outside_is_tension(self):
        # f_NL = +2 is > 3σ above range high (-0.2), with σ=0.5
        result = falsification_routing(2.0, 0.5)
        assert result['verdict'] in ('TENSION', 'FALSIFIED')

    def test_strongly_positive_is_falsified(self):
        # f_NL = +6, σ = 0.5 → clearly positive at high σ
        result = falsification_routing(6.0, 0.3)
        assert result['verdict'] == 'FALSIFIED'

    def test_returns_required_keys(self):
        result = falsification_routing(0.0, 1.6)
        for key in ['verdict', 'condition', 'sigma_from_range', 'f_nl_measured', 'theory_band']:
            assert key in result

    def test_theory_band_correct(self):
        result = falsification_routing(0.0, 1.6)
        assert result['theory_band'] == (F_NL_RANGE_LOW, F_NL_RANGE_HIGH)


class TestPreregistrationHash:
    def test_hash_is_64_hex_chars(self):
        assert len(PREREGISTRATION_HASH) == 64

    def test_hash_is_hex(self):
        int(PREREGISTRATION_HASH, 16)  # should not raise

    def test_hash_matches_string(self):
        expected = hashlib.sha256(PREREGISTRATION_STRING.encode()).hexdigest()
        assert PREREGISTRATION_HASH == expected

    def test_verify_returns_verified(self):
        result = preregistration_hash_verify()
        assert result['status'] == 'VERIFIED'

    def test_verify_hash_matches(self):
        result = preregistration_hash_verify()
        assert result['sha256_hash'] == PREREGISTRATION_HASH


class TestPreregistrationPackage:
    def setup_method(self):
        self.pkg = preregistration_package()

    def test_returns_dict(self):
        assert isinstance(self.pkg, dict)

    def test_pillar_number(self):
        assert self.pkg['pillar'] == 437

    def test_status(self):
        assert self.pkg['status'] == 'FNLPREREGISTERED_SPHEREX'

    def test_experiment(self):
        assert self.pkg['experiment'] == 'SPHEREx'

    def test_prediction_keys(self):
        pred = self.pkg['prediction']
        for key in ['f_nl_dbi', 'delta_fnl_kk', 'f_nl_canonical', 'theory_band']:
            assert key in pred

    def test_derivation_chain(self):
        assert len(self.pkg['derivation_chain']) >= 5

    def test_hash_verified(self):
        assert self.pkg['preregistration']['status'] == 'VERIFIED'

    def test_falsification_conditions(self):
        fc = self.pkg['falsification_conditions']
        assert 'PASS' in fc
        assert 'TENSION' in fc
        assert 'FALSIFIED' in fc


class TestSphereXVerdict:
    def test_inside_band(self):
        assert spherex_verdict(-1.5, 1.6) == 'PASS'

    def test_large_positive(self):
        assert spherex_verdict(8.0, 0.3) == 'FALSIFIED'

    def test_returns_string(self):
        assert isinstance(spherex_verdict(-2.0, 1.6), str)


class TestNumerics:
    def test_dbi_formula_exact(self):
        # Manual calculation for c_s = 12/37
        c_s = 12.0 / 37.0
        inv_cs2 = (37.0 / 12.0) ** 2
        expected = -(35.0 / 108.0) * (inv_cs2 - 1.0)
        assert abs(dbi_fnl(c_s) - expected) < 1e-10

    def test_kk_correction_formula(self):
        rho = 70.0 / 74.0
        rho_sq = rho ** 2
        delta_c_tilde = rho_sq / (2.0 * (1.0 - rho_sq))
        c_s = 12.0 / 37.0
        inv_cs2_m1 = (37.0 / 12.0) ** 2 - 1.0
        expected = (5.0 / 81.0) * inv_cs2_m1 * delta_c_tilde
        assert abs(kk_braid_correction(c_s, rho) - expected) < 1e-10

    def test_canonical_sum(self):
        assert abs(F_NL_UM_CANONICAL - (F_NL_DBI + DELTA_FNL_KK)) < 1e-10
