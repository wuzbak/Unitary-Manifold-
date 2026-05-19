# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 284 — DESI DR3 Falsification Preparedness: No-Rescue Declaration."""
from __future__ import annotations

import math
import pytest

from src.core.pillar284_desi_falsification_preparedness import (
    ADJACENCY_TRACK_LABEL,
    DESI_DR2,
    FALSIFICATION_THRESHOLD_SIGMA,
    HIGH_TENSION_THRESHOLD_SIGMA,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    TENSION_THRESHOLD_SIGMA,
    UM_WA_PREDICTION,
    compute_tension_sigma,
    desi_dr2_triple_check,
    desi_dr3_all_scenarios,
    desi_dr3_scenario_projection,
    desi_falsification_preparedness_report,
    desi_y5_roman_projection,
    exhaustive_rescue_search,
    post_falsified_action_protocol,
    separation_guard,
    what_is_lost_if_falsified,
    what_survives_if_falsified,
)


# ---------------------------------------------------------------------------
# Identity and metadata
# ---------------------------------------------------------------------------

def test_pillar_identity():
    assert PILLAR_NUMBER == 284
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_um_wa_prediction():
    assert UM_WA_PREDICTION == 0.0


def test_threshold_ordering():
    assert TENSION_THRESHOLD_SIGMA < HIGH_TENSION_THRESHOLD_SIGMA < FALSIFICATION_THRESHOLD_SIGMA


def test_separation_guard():
    g = separation_guard()
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
    assert g["no_rescue_declared"] is True
    assert g["provides_post_falsified_protocol"] is True


# ---------------------------------------------------------------------------
# DESI DR2 constants (triple-checked at module load time)
# ---------------------------------------------------------------------------

def test_dr2_bao_tension_is_2_07sigma():
    """The DR2 BAO tension must be 2.07σ — triple-checked."""
    tension = abs(DESI_DR2["wa_central_bao"] - UM_WA_PREDICTION) / DESI_DR2["wa_sigma_bao"]
    assert abs(tension - DESI_DR2["tension_sigma_bao"]) < 1.0e-10
    # Exact value: 0.62 / 0.30 = 2.0666...
    assert abs(tension - 0.62 / 0.30) < 1.0e-10


def test_dr2_combined_tension_is_2_75sigma():
    """The DR2 combined tension must be 2.75σ — triple-checked."""
    tension = abs(DESI_DR2["wa_central_combined"] - UM_WA_PREDICTION) / DESI_DR2["wa_sigma_combined"]
    assert abs(tension - DESI_DR2["tension_sigma_combined"]) < 1.0e-10
    # Exact value: 0.55 / 0.20 = 2.75
    assert abs(tension - 2.75) < 1.0e-10


def test_dr2_w0_tension_vs_desi():
    """w₀ from UM is 0.11σ from DESI DR2 — consistent."""
    tension = abs(-0.930 - DESI_DR2["w0_central"]) / DESI_DR2["w0_sigma"]
    assert tension < 0.2   # well within 1σ


def test_dr2_falsification_not_reached():
    assert DESI_DR2["tension_sigma_bao"] < FALSIFICATION_THRESHOLD_SIGMA
    assert DESI_DR2["tension_sigma_combined"] < FALSIFICATION_THRESHOLD_SIGMA


# ---------------------------------------------------------------------------
# compute_tension_sigma (triple-check function)
# ---------------------------------------------------------------------------

def test_compute_tension_sigma_basic():
    r = compute_tension_sigma(wa_observed=-0.62, wa_sigma=0.30)
    assert abs(r["sigma_tension"] - 0.62 / 0.30) < 1.0e-10
    assert r["triple_check_passed"] is True
    assert r["triple_check_max_discrepancy"] < 1.0e-10


def test_compute_tension_sigma_bao():
    r = compute_tension_sigma(
        wa_observed=DESI_DR2["wa_central_bao"],
        wa_sigma=DESI_DR2["wa_sigma_bao"],
    )
    assert abs(r["sigma_tension"] - DESI_DR2["tension_sigma_bao"]) < 1.0e-10


def test_compute_tension_sigma_combined():
    r = compute_tension_sigma(
        wa_observed=DESI_DR2["wa_central_combined"],
        wa_sigma=DESI_DR2["wa_sigma_combined"],
    )
    assert abs(r["sigma_tension"] - DESI_DR2["tension_sigma_combined"]) < 1.0e-10


def test_compute_tension_sigma_verdicts():
    # CONSISTENT
    r = compute_tension_sigma(wa_observed=-0.10, wa_sigma=0.30)
    assert r["verdict"] == "CONSISTENT"
    # TENSION
    r = compute_tension_sigma(wa_observed=-0.62, wa_sigma=0.30)
    assert r["verdict"] == "TENSION"
    # HIGH_TENSION
    r = compute_tension_sigma(wa_observed=-0.62, wa_sigma=0.24)
    assert r["verdict"] == "HIGH_TENSION"
    # FALSIFIED
    r = compute_tension_sigma(wa_observed=-0.62, wa_sigma=0.18)
    assert r["verdict"] == "FALSIFIED"


def test_compute_tension_sigma_validation():
    with pytest.raises(ValueError):
        compute_tension_sigma(wa_observed=-0.62, wa_sigma=0.0)
    with pytest.raises(ValueError):
        compute_tension_sigma(wa_observed=-0.62, wa_sigma=-0.10)


def test_compute_tension_sigma_three_methods_agree():
    r = compute_tension_sigma(wa_observed=-0.55, wa_sigma=0.20)
    s1, s2, s3 = r["triple_check_methods"]
    assert abs(s1 - s2) < 1.0e-12
    assert abs(s1 - s3) < 1.0e-12


# ---------------------------------------------------------------------------
# DR2 triple-check
# ---------------------------------------------------------------------------

def test_desi_dr2_triple_check():
    check = desi_dr2_triple_check()
    assert check["stored_constants_verified"] is True
    assert check["dr2_bao"]["triple_check_passed"] is True
    assert check["dr2_combined"]["triple_check_passed"] is True
    assert check["current_status"] == "NOT_FALSIFIED_YET"


def test_desi_dr2_triple_check_verdict():
    check = desi_dr2_triple_check()
    # BAO: 2.07σ → TENSION (≥2.0 and <2.5)
    assert check["dr2_bao"]["verdict"] == "TENSION"
    # Combined: 2.75σ → HIGH_TENSION (≥2.5 and <3.0)
    assert check["dr2_combined"]["verdict"] == "HIGH_TENSION"


# ---------------------------------------------------------------------------
# DR3 scenario projection
# ---------------------------------------------------------------------------

def test_dr3_scenario_bao_conservative():
    """DR3 BAO-only with √(3/2) improvement from wₐ=-0.62 → should be HIGH_TENSION."""
    import math as _math
    improve = 1.0 / _math.sqrt(3.0 / 2.0)
    s = desi_dr3_scenario_projection(-0.62, improve, "BAO_ONLY")
    # 0.62 / (0.30 × 0.816) ≈ 0.62 / 0.245 ≈ 2.53σ → HIGH_TENSION
    assert s["sigma_tension"] > 2.0
    assert s["verdict"] in ("HIGH_TENSION", "FALSIFIED")
    assert s["triple_check_passed"] is True


def test_dr3_scenario_combined_conservative():
    """DR3 combined with √(3/2) improvement from wₐ=-0.62 → FALSIFIED."""
    import math as _math
    improve = 1.0 / _math.sqrt(3.0 / 2.0)
    s = desi_dr3_scenario_projection(-0.62, improve, "COMBINED")
    # 0.62 / (0.20 × 0.816) ≈ 0.62 / 0.163 ≈ 3.80σ → FALSIFIED
    assert s["verdict"] == "FALSIFIED"
    assert s["is_danger_scenario"] is True


def test_dr3_scenario_validation():
    with pytest.raises(ValueError):
        desi_dr3_scenario_projection(-0.62, -0.5, "BAO_ONLY")
    with pytest.raises(ValueError):
        desi_dr3_scenario_projection(-0.62, 0.8, "UNKNOWN_DATASET")


def test_dr3_all_scenarios_structure():
    scenarios = desi_dr3_all_scenarios()
    assert len(scenarios) > 8
    # Sorted by tension descending
    tensions = [s["sigma_tension"] for s in scenarios]
    assert tensions == sorted(tensions, reverse=True)
    # At least some FALSIFIED scenarios
    falsified = [s for s in scenarios if s["verdict"] == "FALSIFIED"]
    assert len(falsified) >= 2


# ---------------------------------------------------------------------------
# Exhaustive rescue search
# ---------------------------------------------------------------------------

def test_exhaustive_rescue_search_structure():
    candidates = exhaustive_rescue_search()
    assert len(candidates) >= 5
    for c in candidates:
        assert "mechanism" in c
        assert "status" in c
        assert "elimination_reason" in c


def test_exhaustive_rescue_no_rescue():
    candidates = exhaustive_rescue_search()
    for c in candidates:
        assert c["status"] in ("ELIMINATED", "NOT_IN_UM"), (
            f"Unexpected status '{c['status']}' for '{c['mechanism']}'"
        )


def test_exhaustive_rescue_radion_is_frozen():
    candidates = exhaustive_rescue_search()
    radion = next(c for c in candidates if "radion" in c["mechanism"].lower() and "primary" in c["mechanism"].lower())
    assert radion["status"] == "ELIMINATED"
    assert radion["m_r_over_H0"] > 1.0e40   # vastly superhorizon mass


def test_exhaustive_rescue_wa_upper_bound_negligible():
    candidates = exhaustive_rescue_search()
    radion = next(c for c in candidates if "primary" in c["mechanism"].lower())
    assert radion["wa_upper_bound"] < 1.0e-80


# ---------------------------------------------------------------------------
# Post-FALSIFIED action protocol
# ---------------------------------------------------------------------------

def test_post_falsified_protocol_structure():
    protocol = post_falsified_action_protocol()
    assert protocol["response_deadline_hours"] == 24
    assert len(protocol["mandatory_actions"]) >= 5


def test_post_falsified_protocol_mandatory_files():
    protocol = post_falsified_action_protocol()
    actions = protocol["mandatory_actions"]
    filenames_mentioned = " ".join(
        a.get("content", "") + a.get("action", "") for a in actions
    )
    assert "FALLIBILITY.md" in filenames_mentioned
    assert "CLAIM_MASTER_BOARD.md" in filenames_mentioned


def test_post_falsified_protocol_honest_assessment():
    protocol = post_falsified_action_protocol()
    assessment = protocol["honest_assessment"].lower()
    assert "cannot be patched" in assessment or "no path" in assessment or "cannot be mitigated" in assessment or "patched" in assessment


# ---------------------------------------------------------------------------
# What survives / what is lost
# ---------------------------------------------------------------------------

def test_what_survives_contains_key_claims():
    survives = what_survives_if_falsified()
    text = " ".join(survives).lower()
    assert "n_s" in text or "spectral index" in text.lower()
    assert "birefringence" in text.lower()


def test_what_is_lost_contains_wa():
    lost = what_is_lost_if_falsified()
    text = " ".join(lost)
    assert "wₐ = 0" in text or "wa" in text.lower() or "FALSIFIED" in text


def test_sm_parameters_survive():
    """The SM parameter derivations must survive a DE falsification."""
    survives = what_survives_if_falsified()
    survive_text = " ".join(survives)
    assert "SURVIVES" in survive_text
    # At least the core SM parameters should be mentioned as surviving
    core_count = sum(1 for s in survives if "SURVIVES" in s)
    assert core_count >= 8


# ---------------------------------------------------------------------------
# DESI Y5 / Roman projection
# ---------------------------------------------------------------------------

def test_desi_y5_roman_structure():
    proj = desi_y5_roman_projection()
    assert "projections" in proj
    assert "most_dangerous" in proj
    assert proj["desi_y5_falsifies_if_wa_stays_negative"] is True
    assert proj["roman_falsifies_if_wa_stays_negative"] is True


def test_desi_y5_roman_has_falsified_scenarios():
    proj = desi_y5_roman_projection()
    assert proj["falsified_count"] > 0


# ---------------------------------------------------------------------------
# Full report
# ---------------------------------------------------------------------------

def test_full_report_structure():
    report = desi_falsification_preparedness_report()
    assert report["pillar"] == 284
    assert "executive_summary" in report
    assert "dr2_triple_check" in report
    assert "dr3_scenarios" in report
    assert "exhaustive_rescue_search" in report
    assert "post_falsified_protocol" in report
    assert "what_survives" in report
    assert "what_is_lost" in report


def test_full_report_no_rescue_declared():
    report = desi_falsification_preparedness_report()
    search = report["exhaustive_rescue_search"]
    assert search["all_eliminated"] is True
    assert "FALSIFIED" in search["no_rescue_declaration"]


def test_full_report_executive_threat_level():
    report = desi_falsification_preparedness_report()
    es = report["executive_summary"]
    assert es["no_rescue"] is True
    assert es["current_status"] == "NOT_FALSIFIED (2.07σ BAO-only, 2.75σ combined)"


def test_full_report_no_hardgate_drift():
    report = desi_falsification_preparedness_report()
    g = report["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
