# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 526 — G4 Flux Quantization: Vol(CY₃) Unconditional Derivation."""

from __future__ import annotations

import math
import pytest

from src.eleventd.g4_flux_quantization import (
    CHI_CY3_QUINTIC,
    H11_QUINTIC,
    H21_QUINTIC,
    K_CS,
    LAMBDA_G4_FIXED,
    N_BRANE_CANONICAL,
    N_FLUX_CANONICAL,
    N_W,
    NLO_BOUND_PCT,
    PI_KR_0,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VOL_CY3_FIXED,
    bianchi_identity_check,
    flux_quantization_report,
    gw_potential_11d,
    lambda_g4_from_flux,
    nlo_shift_check,
    scan_flux_lattice,
    select_canonical_flux,
    tadpole_cancellation_target,
    tadpole_candidate_pairs,
    tadpole_residual,
    vol_cy3_from_lambda_g4,
)


class TestPillarMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 526

    def test_pillar_status(self):
        assert PILLAR_STATUS == "FLUX_QUANTIZATION_COMPLETE"

    def test_pillar_title(self):
        assert "Flux Quantization" in PILLAR_TITLE

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_pi_kr_0(self):
        assert PI_KR_0 == 37.0


class TestCY3Constants:
    def test_chi_quintic(self):
        assert CHI_CY3_QUINTIC == -200

    def test_euler_characteristic_formula(self):
        chi_computed = 2 * (H11_QUINTIC - H21_QUINTIC)
        assert chi_computed == CHI_CY3_QUINTIC

    def test_h11_quintic(self):
        assert H11_QUINTIC == 1

    def test_h21_quintic(self):
        assert H21_QUINTIC == 101


class TestCanonicalFluxSelection:
    def test_n_flux_canonical_is_minus_8(self):
        assert N_FLUX_CANONICAL == -8

    def test_n_brane_canonical_is_zero(self):
        assert N_BRANE_CANONICAL == 0

    def test_lambda_g4_fixed_positive(self):
        assert LAMBDA_G4_FIXED > 0

    def test_lambda_g4_computation(self):
        expected = abs(CHI_CY3_QUINTIC) * abs(N_FLUX_CANONICAL) / (24.0 * math.pi)
        assert abs(LAMBDA_G4_FIXED - expected) < 1e-9

    def test_vol_cy3_fixed_positive(self):
        assert VOL_CY3_FIXED > 0

    def test_vol_cy3_fixed_finite(self):
        assert math.isfinite(VOL_CY3_FIXED)


class TestTadpoleFunctions:
    def test_tadpole_target(self):
        target = tadpole_cancellation_target()
        assert abs(target - (-200 / 24)) < 1e-9

    def test_tadpole_target_near_minus_8(self):
        target = tadpole_cancellation_target()
        assert -9 < target < -8

    def test_candidate_pairs_includes_minus_8(self):
        pairs = tadpole_candidate_pairs()
        n_flux_values = [p[0] for p in pairs]
        assert -8 in n_flux_values

    def test_candidate_pairs_all_tuples(self):
        pairs = tadpole_candidate_pairs()
        for p in pairs:
            assert len(p) == 2

    def test_tadpole_residual_for_canonical(self):
        res = tadpole_residual(N_FLUX_CANONICAL, N_BRANE_CANONICAL)
        # N_flux=-8, N_brane=0: residual = |-8 + 0 - (-200/24)| = |-8 + 8.333| = 0.333
        assert abs(res - abs(-8 - (-200 / 24))) < 1e-9

    def test_tadpole_residual_non_negative(self):
        res = tadpole_residual(-8, 0)
        assert res >= 0


class TestLambdaG4:
    def test_lambda_g4_zero_flux(self):
        assert lambda_g4_from_flux(0) == 0.0

    def test_lambda_g4_positive_for_n8(self):
        assert lambda_g4_from_flux(-8) > 0

    def test_lambda_g4_scaling(self):
        l8 = lambda_g4_from_flux(-8)
        l4 = lambda_g4_from_flux(-4)
        assert abs(l8 / l4 - 2.0) < 1e-9

    def test_lambda_g4_formula(self):
        expected = 200 * 8 / (24 * math.pi)
        assert abs(lambda_g4_from_flux(-8) - expected) < 1e-9


class TestVolCY3:
    def test_vol_cy3_positive(self):
        lam = lambda_g4_from_flux(-8)
        assert vol_cy3_from_lambda_g4(lam) > 0

    def test_vol_cy3_zero_for_zero_lambda(self):
        assert vol_cy3_from_lambda_g4(0.0) == 0.0

    def test_vol_cy3_increases_with_lambda(self):
        l1 = lambda_g4_from_flux(-4)
        l2 = lambda_g4_from_flux(-8)
        v1 = vol_cy3_from_lambda_g4(l1)
        v2 = vol_cy3_from_lambda_g4(l2)
        assert v2 > v1

    def test_vol_cy3_matches_module_constant(self):
        lam = LAMBDA_G4_FIXED
        vol = vol_cy3_from_lambda_g4(lam)
        assert abs(vol - VOL_CY3_FIXED) < 1e-9


class TestGWPotential:
    def test_gw_potential_returns_float(self):
        lam = lambda_g4_from_flux(-8)
        vol = vol_cy3_from_lambda_g4(lam)
        pot = gw_potential_11d(PI_KR_0, vol, lam)
        assert isinstance(pot, float)
        assert math.isfinite(pot)

    def test_gw_potential_finite_for_canonical(self):
        lam = LAMBDA_G4_FIXED
        vol = VOL_CY3_FIXED
        pot = gw_potential_11d(PI_KR_0, vol, lam)
        assert math.isfinite(pot)


class TestFluxLatticeScan:
    def setup_method(self):
        self.candidates = scan_flux_lattice()

    def test_returns_list(self):
        assert isinstance(self.candidates, list)

    def test_non_empty(self):
        assert len(self.candidates) > 0

    def test_sorted_by_tadpole_residual(self):
        residuals = [c["tadpole_residual"] for c in self.candidates]
        assert residuals == sorted(residuals)

    def test_all_have_required_keys(self):
        for c in self.candidates:
            for key in ("n_flux", "n_brane", "lambda_g4", "vol_cy3", "potential", "tadpole_residual"):
                assert key in c

    def test_first_is_best_candidate(self):
        best = self.candidates[0]
        assert best["tadpole_residual"] <= self.candidates[-1]["tadpole_residual"]

    def test_no_zero_flux(self):
        for c in self.candidates:
            assert c["n_flux"] != 0

    def test_vol_cy3_positive_for_all(self):
        for c in self.candidates:
            assert c["vol_cy3"] >= 0


class TestSelectCanonicalFlux:
    def setup_method(self):
        self.sel = select_canonical_flux()

    def test_returns_dict(self):
        assert isinstance(self.sel, dict)

    def test_status_complete(self):
        assert self.sel["status"] == "FLUX_QUANTIZATION_COMPLETE"

    def test_n_flux_canonical_minus_8(self):
        assert self.sel["n_flux_canonical"] == -8

    def test_vol_cy3_fixed_positive(self):
        assert self.sel["vol_cy3_fixed"] > 0

    def test_unique_selection(self):
        assert self.sel["unique"] is True

    def test_lambda_g4_positive(self):
        assert self.sel["lambda_g4_fixed"] > 0

    def test_candidates_scanned_positive(self):
        assert self.sel["candidates_scanned"] > 0

    def test_note_present(self):
        assert "note" in self.sel
        assert len(self.sel["note"]) > 0


class TestBianchiCheck:
    def setup_method(self):
        self.b = bianchi_identity_check()

    def test_returns_dict(self):
        assert isinstance(self.b, dict)

    def test_n_flux_correct(self):
        assert self.b["n_flux"] == N_FLUX_CANONICAL

    def test_chi_correct(self):
        assert self.b["chi"] == CHI_CY3_QUINTIC

    def test_bianchi_residual_non_negative(self):
        assert self.b["bianchi_residual"] >= 0

    def test_verdict_in_valid_set(self):
        assert self.b["verdict"] in ("BIANCHI_SATISFIED", "BIANCHI_TENSION")


class TestNLOShiftCheck:
    def setup_method(self):
        self.nlo = nlo_shift_check()

    def test_returns_dict(self):
        assert isinstance(self.nlo, dict)

    def test_vol_cy3_fixed_positive(self):
        assert self.nlo["vol_cy3_fixed"] > 0

    def test_nlo_shift_pct_non_negative(self):
        assert self.nlo["nlo_shift_pct"] >= 0

    def test_pillar388_bound_recorded(self):
        assert self.nlo["pillar388_bound_pct"] == NLO_BOUND_PCT

    def test_note_present(self):
        assert "note" in self.nlo


class TestFluxQuantizationReport:
    def setup_method(self):
        self.r = flux_quantization_report()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_pillar_number(self):
        assert self.r["pillar"] == 526

    def test_status_complete(self):
        assert self.r["status"] == "FLUX_QUANTIZATION_COMPLETE"

    def test_vol_cy3_fixed_present(self):
        assert "vol_cy3_fixed" in self.r
        assert self.r["vol_cy3_fixed"] > 0

    def test_lambda_g4_fixed_present(self):
        assert "lambda_g4_fixed" in self.r
        assert self.r["lambda_g4_fixed"] > 0

    def test_downstream_unlocked_has_three(self):
        assert len(self.r["downstream_unlocked"]) >= 3

    def test_epistemic_upgrade_present(self):
        assert "epistemic_upgrade" in self.r
        assert "from" in self.r["epistemic_upgrade"]
        assert "to" in self.r["epistemic_upgrade"]

    def test_upgrade_from_conditional(self):
        assert "CONDITIONAL" in self.r["epistemic_upgrade"]["from"]

    def test_upgrade_to_complete(self):
        assert "COMPLETE" in self.r["epistemic_upgrade"]["to"]

    def test_summary_mentions_vol_cy3(self):
        assert "Vol" in self.r["summary"]

    def test_flux_selection_present(self):
        assert "flux_selection" in self.r

    def test_bianchi_check_present(self):
        assert "bianchi_check" in self.r

    def test_nlo_shift_check_present(self):
        assert "nlo_shift_check" in self.r
