# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 242 — Planetary Coherence & Cascade Resilience Engine (PCCRE)."""

from __future__ import annotations

import math

import pytest

from src.core.pillar242_planetary_coherence_cascade_resilience_engine import (
    N_W,
    N_2,
    K_CS,
    C_S,
    XI_C,
    SECTORS,
    N_SECTORS,
    N_CASCADE_PAIRS,
    HOLON_THEORETICAL_CONFIDENCE,
    __provenance__,
    CascadeState,
    hils_stability_weight,
    cascade_coupling_matrix,
    cascade_penalty,
    unified_planetary_readiness_index,
    compound_cascade_failure_probability,
    cross_sector_budget_allocation,
    monte_carlo_upri,
    sector_coherence_score,
    pccre_full_report,
    baseline_cascade_state,
    pillar242_pccre_report,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _perfect_state() -> CascadeState:
    """All sectors at 1.0, full HILS saturation."""
    return CascadeState(
        sector_adequacy={s: 1.0 for s in SECTORS},
        phi_trust=1.0,
        n_hil=15,
    )


def _failed_state() -> CascadeState:
    """All sectors at 0.0, no trust."""
    return CascadeState(
        sector_adequacy={s: 0.0 for s in SECTORS},
        phi_trust=0.0,
        n_hil=0,
    )


def _baseline() -> CascadeState:
    return baseline_cascade_state()


# ---------------------------------------------------------------------------
# Provenance and constants
# ---------------------------------------------------------------------------

def test_provenance_pillar_number():
    assert __provenance__["pillar"] == 242


def test_provenance_title():
    assert "Planetary Coherence" in __provenance__["title"]
    assert "Cascade Resilience" in __provenance__["title"]


def test_provenance_status_adjacent():
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]


def test_provenance_license():
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_provenance_co_emergent_insight():
    assert "n_w = 5" in __provenance__["co_emergent_insight"]
    assert "N_SECTORS" in __provenance__["co_emergent_insight"]


def test_constants_n_w():
    assert N_W == 5


def test_constants_k_cs():
    assert K_CS == 74


def test_constants_c_s():
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0, abs_tol=1e-15)


def test_constants_xi_c():
    assert math.isclose(XI_C, 35.0 / 74.0, rel_tol=0, abs_tol=1e-15)


def test_constants_n_2():
    assert N_2 == 7


# ---------------------------------------------------------------------------
# Structural invariants — the co-emergent insight
# ---------------------------------------------------------------------------

def test_sector_count_equals_n_w():
    """Core co-emergent insight: 5 physics dimensions = 5 civilizational sectors."""
    assert N_SECTORS == N_W


def test_sectors_tuple_length():
    assert len(SECTORS) == 5


def test_cascade_pairs_count():
    assert N_CASCADE_PAIRS == 10  # C(5,2) = 10


def test_holon_confidence_is_one():
    """Holon Zero reports 0 OPEN parameters → theoretical confidence = 1.0."""
    assert HOLON_THEORETICAL_CONFIDENCE == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# CascadeState validation
# ---------------------------------------------------------------------------

def test_cascade_state_creation():
    state = CascadeState(sector_adequacy={s: 0.5 for s in SECTORS})
    for s in SECTORS:
        assert state.sector_adequacy[s] == pytest.approx(0.5)


def test_cascade_state_defaults():
    state = CascadeState(sector_adequacy={s: 0.5 for s in SECTORS})
    assert state.phi_trust == 1.0
    assert state.n_hil == 1


def test_cascade_state_invalid_adequacy_raises():
    bad = {s: 0.5 for s in SECTORS}
    bad[SECTORS[0]] = 1.5
    with pytest.raises(ValueError):
        CascadeState(sector_adequacy=bad)


def test_cascade_state_invalid_phi_trust_raises():
    with pytest.raises(ValueError):
        CascadeState(sector_adequacy={s: 0.5 for s in SECTORS}, phi_trust=1.5)


def test_cascade_state_invalid_n_hil_raises():
    with pytest.raises(ValueError):
        CascadeState(sector_adequacy={s: 0.5 for s in SECTORS}, n_hil=-1)


def test_cascade_state_missing_sector_raises():
    incomplete = {SECTORS[0]: 0.5}
    with pytest.raises(ValueError):
        CascadeState(sector_adequacy=incomplete)


# ---------------------------------------------------------------------------
# HILS stability weight
# ---------------------------------------------------------------------------

def test_hils_weight_unit_interval():
    for n in range(0, 20):
        w = hils_stability_weight(1.0, n)
        assert 0.0 <= w <= 1.0


def test_hils_weight_base_at_n0():
    """At n_hil=0, weight = phi_trust × C_S."""
    w = hils_stability_weight(1.0, 0)
    assert w == pytest.approx(C_S, rel=1e-10)


def test_hils_weight_saturated_at_n15():
    """At n_hil=15, weight saturates at phi_trust × 1.0."""
    w = hils_stability_weight(1.0, 15)
    assert w == pytest.approx(1.0, abs=1e-9)


def test_hils_weight_saturated_above_n15():
    w = hils_stability_weight(1.0, 20)
    assert w == pytest.approx(1.0, abs=1e-9)


def test_hils_weight_scales_with_trust():
    w_full = hils_stability_weight(1.0, 5)
    w_half = hils_stability_weight(0.5, 5)
    assert w_half == pytest.approx(w_full * 0.5, rel=1e-10)


def test_hils_weight_invalid_trust_raises():
    with pytest.raises(ValueError):
        hils_stability_weight(1.5, 5)


def test_hils_weight_invalid_n_hil_raises():
    with pytest.raises(ValueError):
        hils_stability_weight(1.0, -1)


# ---------------------------------------------------------------------------
# Cascade coupling matrix
# ---------------------------------------------------------------------------

def test_cascade_matrix_shape():
    state = _baseline()
    matrix = cascade_coupling_matrix(state)
    assert set(matrix.keys()) == set(SECTORS)
    for row in matrix.values():
        assert set(row.keys()) == set(SECTORS)


def test_cascade_matrix_self_coupling_zero():
    state = _baseline()
    matrix = cascade_coupling_matrix(state)
    for s in SECTORS:
        assert matrix[s][s] == 0.0


def test_cascade_matrix_is_symmetric():
    state = _baseline()
    matrix = cascade_coupling_matrix(state)
    for si in SECTORS:
        for sj in SECTORS:
            assert matrix[si][sj] == pytest.approx(matrix[sj][si])


def test_cascade_matrix_zero_when_all_perfect():
    state = _perfect_state()
    matrix = cascade_coupling_matrix(state)
    for si in SECTORS:
        for sj in SECTORS:
            assert matrix[si][sj] == 0.0


def test_cascade_matrix_values_unit_interval():
    state = _baseline()
    matrix = cascade_coupling_matrix(state)
    for si in SECTORS:
        for sj in SECTORS:
            assert 0.0 <= matrix[si][sj] <= 1.0


# ---------------------------------------------------------------------------
# Cascade penalty
# ---------------------------------------------------------------------------

def test_cascade_penalty_unit_interval():
    assert 0.0 <= cascade_penalty(_baseline()) <= 1.0


def test_cascade_penalty_zero_when_all_perfect():
    assert cascade_penalty(_perfect_state()) == pytest.approx(0.0)


def test_cascade_penalty_increases_with_failure():
    perfect = _perfect_state()
    failing = CascadeState(
        sector_adequacy={s: 0.2 for s in SECTORS},
        phi_trust=1.0,
        n_hil=1,
    )
    assert cascade_penalty(failing) > cascade_penalty(perfect)


# ---------------------------------------------------------------------------
# Unified Planetary Readiness Index (UPRI)
# ---------------------------------------------------------------------------

def test_upri_unit_interval():
    assert 0.0 <= unified_planetary_readiness_index(_baseline()) <= 1.0


def test_upri_zero_for_all_failed():
    assert unified_planetary_readiness_index(_failed_state()) == pytest.approx(0.0)


def test_upri_leq_mean_adequacy():
    """UPRI is always <= naive sector mean (cascade penalty reduces it)."""
    state = _baseline()
    mean_adeq = sum(state.sector_adequacy[s] for s in SECTORS) / N_SECTORS
    upri = unified_planetary_readiness_index(state)
    assert upri <= mean_adeq + 1e-10


def test_upri_improves_with_better_sectors():
    state = _baseline()
    better = CascadeState(
        sector_adequacy={s: min(1.0, state.sector_adequacy[s] + 0.3) for s in SECTORS},
        phi_trust=state.phi_trust,
        n_hil=state.n_hil,
    )
    assert unified_planetary_readiness_index(better) >= unified_planetary_readiness_index(state)


def test_upri_improves_with_more_hil():
    state = _baseline()
    state_more_hil = CascadeState(
        sector_adequacy=state.sector_adequacy,
        phi_trust=state.phi_trust,
        n_hil=15,
    )
    assert unified_planetary_readiness_index(state_more_hil) >= unified_planetary_readiness_index(state)


def test_upri_positive_with_baseline():
    """Baseline UPRI should be > 0 (sectors are not all failed)."""
    assert unified_planetary_readiness_index(_baseline()) > 0.0


# ---------------------------------------------------------------------------
# Compound cascade failure probability
# ---------------------------------------------------------------------------

def test_compound_failure_prob_unit_interval():
    assert 0.0 <= compound_cascade_failure_probability(_baseline()) <= 1.0


def test_compound_failure_prob_one_for_failed_state():
    assert compound_cascade_failure_probability(_failed_state()) == pytest.approx(1.0, abs=1e-9)


def test_compound_failure_prob_lower_for_better_state():
    assert (
        compound_cascade_failure_probability(_perfect_state())
        < compound_cascade_failure_probability(_baseline())
    )


# ---------------------------------------------------------------------------
# Cross-sector budget allocation
# ---------------------------------------------------------------------------

def test_budget_allocation_length():
    alloc = cross_sector_budget_allocation(_baseline(), 1e9)
    assert len(alloc) == N_SECTORS


def test_budget_allocation_all_sectors_present():
    alloc = cross_sector_budget_allocation(_baseline(), 1e9)
    sectors_in_alloc = {a["sector"] for a in alloc}
    assert sectors_in_alloc == set(SECTORS)


def test_budget_allocation_fractions_sum_to_one():
    alloc = cross_sector_budget_allocation(_baseline(), 1e9)
    total_frac = sum(a["allocated_fraction"] for a in alloc)
    assert total_frac == pytest.approx(1.0, abs=1e-10)


def test_budget_allocation_amounts_sum_to_budget():
    budget = 5e8
    alloc = cross_sector_budget_allocation(_baseline(), budget)
    total_alloc = sum(a["allocated_budget_usd"] for a in alloc)
    assert total_alloc == pytest.approx(budget, rel=1e-10)


def test_budget_allocation_sorted_descending():
    alloc = cross_sector_budget_allocation(_baseline(), 1e9)
    for i in range(len(alloc) - 1):
        assert alloc[i]["cascade_impact_score"] >= alloc[i + 1]["cascade_impact_score"]


def test_budget_zero_gives_zero_allocations():
    alloc = cross_sector_budget_allocation(_baseline(), 0.0)
    for a in alloc:
        assert a["allocated_budget_usd"] == 0.0


def test_budget_negative_raises():
    with pytest.raises(ValueError):
        cross_sector_budget_allocation(_baseline(), -1.0)


# ---------------------------------------------------------------------------
# Monte Carlo UPRI
# ---------------------------------------------------------------------------

def test_monte_carlo_keys():
    mc = monte_carlo_upri(_baseline(), n_trials=40, seed=242)
    for key in ("mean_upri", "p10_upri", "p50_upri", "p90_upri"):
        assert key in mc


def test_monte_carlo_bounds():
    mc = monte_carlo_upri(_baseline(), n_trials=40, seed=242)
    for v in mc.values():
        assert 0.0 <= v <= 1.0


def test_monte_carlo_percentile_order():
    mc = monte_carlo_upri(_baseline(), n_trials=100, seed=242)
    assert mc["p10_upri"] <= mc["p50_upri"] <= mc["p90_upri"]


def test_monte_carlo_reproducible():
    mc1 = monte_carlo_upri(_baseline(), n_trials=40, seed=99)
    mc2 = monte_carlo_upri(_baseline(), n_trials=40, seed=99)
    assert mc1 == mc2


def test_monte_carlo_invalid_trials_raises():
    with pytest.raises(ValueError):
        monte_carlo_upri(_baseline(), n_trials=0)


# ---------------------------------------------------------------------------
# Sector coherence score
# ---------------------------------------------------------------------------

def test_coherence_unit_interval():
    assert 0.0 <= sector_coherence_score(_baseline()) <= 1.0


def test_coherence_one_for_uniform_sectors():
    state = CascadeState(sector_adequacy={s: 0.6 for s in SECTORS})
    assert sector_coherence_score(state) == pytest.approx(1.0, abs=1e-9)


def test_coherence_lower_for_unequal_sectors():
    balanced = CascadeState(sector_adequacy={s: 0.5 for s in SECTORS})
    unbalanced = CascadeState(
        sector_adequacy={
            SECTORS[0]: 0.0,
            SECTORS[1]: 0.0,
            SECTORS[2]: 1.0,
            SECTORS[3]: 1.0,
            SECTORS[4]: 0.5,
        }
    )
    assert sector_coherence_score(unbalanced) <= sector_coherence_score(balanced)


# ---------------------------------------------------------------------------
# Full PCCRE report
# ---------------------------------------------------------------------------

def test_full_report_keys():
    report = pccre_full_report(_baseline(), n_trials=30, budget_usd=1e9, seed=242)
    for key in (
        "pillar",
        "status",
        "co_emergent_insight",
        "sector_count_equals_n_w",
        "sector_adequacy",
        "sector_coherence_score",
        "upri",
        "upri_status",
        "compound_cascade_failure_probability",
        "cascade_coupling_matrix",
        "cascade_penalty",
        "hils_weight",
        "budget_allocation",
        "monte_carlo_upri",
        "holon_theoretical_confidence",
        "falsification_condition",
    ):
        assert key in report


def test_full_report_pillar_number():
    assert pccre_full_report(_baseline(), n_trials=20)["pillar"] == 242


def test_full_report_sector_count_equals_nw_true():
    assert pccre_full_report(_baseline(), n_trials=20)["sector_count_equals_n_w"] is True


def test_full_report_falsification_string():
    report = pccre_full_report(_baseline(), n_trials=20)
    assert "FALSIFIED" in report["falsification_condition"]


def test_full_report_holon_confidence():
    assert pccre_full_report(_baseline(), n_trials=20)["holon_theoretical_confidence"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Integrated report (from baseline scenarios of Pillars 237-241)
# ---------------------------------------------------------------------------

def test_integrated_report_pillar_number():
    report = pillar242_pccre_report(n_trials=20)
    assert report["pillar"] == 242


def test_integrated_report_upri_positive():
    report = pillar242_pccre_report(n_trials=20)
    assert report["upri"] > 0.0


def test_integrated_report_upri_below_mean_adequacy():
    """Key property: UPRI < naive mean due to cascade penalty."""
    report = pillar242_pccre_report(n_trials=20)
    mean_adeq = sum(report["sector_adequacy"].values()) / N_SECTORS
    assert report["upri"] <= mean_adeq + 1e-10


def test_baseline_cascade_state_returns_cascade_state():
    state = baseline_cascade_state()
    assert isinstance(state, CascadeState)
    assert set(state.sector_adequacy.keys()) == set(SECTORS)
