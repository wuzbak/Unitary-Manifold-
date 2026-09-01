# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for 12-AZ-IP/lib/open_science shared library."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from open_science.litebird import (
    assess_birefringence_measurement,
    days_to_litebird,
    LITEBIRD_LAUNCH_YEAR,
    BIREFRINGENCE_PREDICTION,
)
from open_science.desi import (
    check_desi_tension,
    get_falsification_status,
    DESI_DR3_PREREGISTRATION,
)
from open_science.planck import get_planck_cmb_reference, PLANCK_N_S, UM_N_S
from open_science.arxiv import fetch_recent_kk_preprints


# ── LiteBIRD tests ─────────────────────────────────────────────────────────

class TestLiteBIRD:
    def test_launch_year(self):
        assert LITEBIRD_LAUNCH_YEAR == 2032

    def test_days_to_litebird_positive(self):
        d = days_to_litebird()
        assert isinstance(d, int)
        assert d > 0  # not yet launched

    def test_prediction_structure(self):
        p = BIREFRINGENCE_PREDICTION
        assert "canonical_deg" in p
        assert "admissible_window_deg" in p
        assert "falsification_gap_deg" in p
        assert len(p["canonical_deg"]) == 2
        assert p["admissible_window_deg"][0] < p["admissible_window_deg"][1]

    def test_canonical_in_window(self):
        for beta in BIREFRINGENCE_PREDICTION["canonical_deg"]:
            result = assess_birefringence_measurement(beta)
            assert result["in_admissible_window"]
            assert not result["in_falsification_gap"]
            assert not result["falsifies"]

    def test_outside_window_below_falsifies(self):
        result = assess_birefringence_measurement(0.10)
        assert result["falsifies"]

    def test_outside_window_above_falsifies(self):
        result = assess_birefringence_measurement(0.50)
        assert result["falsifies"]

    def test_in_gap_falsifies(self):
        result = assess_birefringence_measurement(0.30)
        assert result["in_falsification_gap"]
        assert result["falsifies"]

    def test_near_canonical_0273(self):
        result = assess_birefringence_measurement(0.273)
        assert result["near_canonical_prediction"]
        assert not result["falsifies"]

    def test_near_canonical_0331(self):
        result = assess_birefringence_measurement(0.331)
        assert result["near_canonical_prediction"]
        assert not result["falsifies"]

    def test_falsified_verdict_string(self):
        result = assess_birefringence_measurement(0.10)
        assert "FALSIFIED" in result["verdict"]

    def test_consistent_verdict_string(self):
        result = assess_birefringence_measurement(0.273)
        assert "CONSISTENT" in result["verdict"]

    def test_epistemic_note_present(self):
        result = assess_birefringence_measurement(0.273)
        assert "epistemic_note" in result
        assert len(result["epistemic_note"]) > 10

    def test_admissible_midpoint_not_gap(self):
        result = assess_birefringence_measurement(0.25)
        assert result["in_admissible_window"]
        assert not result["in_falsification_gap"]

    def test_result_has_beta_deg(self):
        result = assess_birefringence_measurement(0.273)
        assert result["beta_deg"] == 0.273


# ── DESI tests ─────────────────────────────────────────────────────────────

class TestDESI:
    def test_preregistration_date(self):
        assert DESI_DR3_PREREGISTRATION["preregistration_date"] == "2026-08-29"

    def test_w0_prediction(self):
        assert DESI_DR3_PREREGISTRATION["w0_prediction"] == -1.0

    def test_wa_prediction(self):
        assert DESI_DR3_PREREGISTRATION["wa_prediction"] == 0.0

    def test_pillar_p824(self):
        assert DESI_DR3_PREREGISTRATION["pillar"] == "P824"

    def test_status_preregistered(self):
        assert DESI_DR3_PREREGISTRATION["status"] == "PREREGISTERED"

    def test_consistent_at_prediction(self):
        result = check_desi_tension(-1.0, 0.0)
        assert result["consistent"]
        assert result["combined_tension_sigma"] == 0.0

    def test_dr2_shows_tension(self):
        result = check_desi_tension(-0.827, -0.75)
        assert result["combined_tension_sigma"] > 1.0

    def test_strong_tension_verdict(self):
        result = check_desi_tension(-0.5, -2.0)
        assert "TENSION" in result["verdict"]

    def test_falsification_status_structure(self):
        status = get_falsification_status()
        assert "total_claims" in status
        assert "claims" in status
        assert status["total_claims"] >= 4
        assert "primary_falsifier" in status

    def test_birefringence_claim_present(self):
        status = get_falsification_status()
        ids = [c["id"] for c in status["claims"]]
        assert "birefringence" in ids

    def test_desi_dr3_claim_present(self):
        status = get_falsification_status()
        ids = [c["id"] for c in status["claims"]]
        assert "desi_dr3" in ids

    def test_ns_consistent_claim(self):
        status = get_falsification_status()
        ns_claim = next(c for c in status["claims"] if c["id"] == "n_s_prediction")
        assert "CONSISTENT" in ns_claim["status"]

    def test_epistemic_note_in_status(self):
        status = get_falsification_status()
        assert "epistemic_note" in status

    def test_check_desi_required_keys(self):
        result = check_desi_tension(-1.0, 0.0)
        required = {"w0_observed", "wa_observed", "consistent", "verdict", "combined_tension_sigma"}
        assert required.issubset(result.keys())

    def test_delta_w0_correct(self):
        result = check_desi_tension(-0.9, 0.1)
        assert abs(result["delta_w0"] - 0.1) < 1e-9
        assert abs(result["delta_wa"] - 0.1) < 1e-9


# ── Planck tests ────────────────────────────────────────────────────────────

class TestPlanck:
    def test_planck_ns_range(self):
        assert 0.96 < PLANCK_N_S < 0.97

    def test_um_ns_within_1sigma(self):
        assert abs(UM_N_S - PLANCK_N_S) < 0.0042

    def test_reference_has_parameters(self):
        ref = get_planck_cmb_reference()
        assert "parameters" in ref

    def test_reference_has_um_status(self):
        ref = get_planck_cmb_reference()
        assert "um_status" in ref

    def test_reference_has_caveat(self):
        ref = get_planck_cmb_reference()
        assert "caveat" in ref

    def test_ns_tension_below_1sigma(self):
        ref = get_planck_cmb_reference()
        assert ref["parameters"]["n_s"]["tension_sigma"] < 1.0

    def test_r_consistent(self):
        ref = get_planck_cmb_reference()
        assert "CONSISTENT" in ref["um_status"]["r"]

    def test_as_open_gap(self):
        ref = get_planck_cmb_reference()
        assert "OPEN GAP" in ref["um_status"]["A_s"]

    def test_source_attribution(self):
        ref = get_planck_cmb_reference()
        assert "Planck" in ref["source"]


# ── arXiv tests (offline-safe) ──────────────────────────────────────────────

class TestArxiv:
    def test_returns_list(self):
        result = fetch_recent_kk_preprints("kk_extra_dimensions", max_results=2)
        assert isinstance(result, list)

    def test_unknown_topic_no_raise(self):
        result = fetch_recent_kk_preprints("nonexistent_xyz", max_results=1)
        assert isinstance(result, list)

    def test_result_structure_if_any(self):
        result = fetch_recent_kk_preprints("cmb_birefringence", max_results=1)
        if result:
            entry = result[0]
            assert "title" in entry
            assert "arxiv_id" in entry
            assert "published" in entry

    def test_litebird_topic(self):
        result = fetch_recent_kk_preprints("litebird", max_results=1)
        assert isinstance(result, list)
