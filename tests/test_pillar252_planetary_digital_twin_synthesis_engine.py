# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 252 — Planetary Digital-Twin Synthesis Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar252_planetary_digital_twin_synthesis_engine import (
    ADJACENCY_TRACK_LABEL,
    C_S,
    K_CS,
    N_W,
    PHI0,
    PLANETARY_TWIN_TRACK_LABEL,
    PlanetaryTwinState,
    SECTORS,
    __provenance__,
    baseline_planetary_twin_state,
    coupling_matrix,
    intervention_allocator,
    pillar252_planetary_digital_twin_report,
    scenario_risk_envelope,
    sector_adequacy,
    separation_guard,
    simulate_planetary_path,
    step_planetary_twin,
    twin_coherence_index,
)


def _state() -> PlanetaryTwinState:
    return baseline_planetary_twin_state()


def test_provenance_contract():
    assert __provenance__["pillar"] == 252
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_framework_constants_contract():
    assert N_W == 5
    assert K_CS == 74
    assert K_CS == 5**2 + 7**2
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_separation_guard_contract():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["track"] == PLANETARY_TWIN_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["deterministic_forecast_claim_allowed"] is False


def test_state_schema_sanity():
    s = _state()
    assert isinstance(s, PlanetaryTwinState)
    assert 0.0 <= s.phi_trust <= 1.0
    assert s.n_hil >= 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("climate_resilience", 1.2),
        ("food_security", -0.1),
        ("n_hil", -1),
    ],
)
def test_state_validation_raises(field: str, value: float):
    s = _state()
    with pytest.raises(ValueError):
        PlanetaryTwinState(**{**s.__dict__, field: value})


def test_sector_adequacy_keys_and_range():
    a = sector_adequacy(_state())
    assert tuple(a.keys()) == SECTORS
    for v in a.values():
        assert 0.0 <= v <= 1.0


def test_coupling_matrix_shape_and_diagonal_zero():
    m = coupling_matrix(_state())
    assert set(m.keys()) == set(SECTORS)
    for i in SECTORS:
        assert set(m[i].keys()) == set(SECTORS)
        assert m[i][i] == 0.0


def test_coupling_matrix_symmetric():
    m = coupling_matrix(_state())
    for i in SECTORS:
        for j in SECTORS:
            assert abs(m[i][j] - m[j][i]) < 1e-15


def test_coherence_index_range():
    x = twin_coherence_index(_state())
    assert 0.0 <= x <= 1.0


def test_step_planetary_twin_contract():
    s2 = step_planetary_twin(_state(), years=1.0)
    assert isinstance(s2, PlanetaryTwinState)
    for v in sector_adequacy(s2).values():
        assert 0.0 <= v <= 1.0


def test_step_planetary_twin_invalid_years_raises():
    with pytest.raises(ValueError):
        step_planetary_twin(_state(), years=0)


def test_simulate_path_length_and_years():
    p = simulate_planetary_path(_state(), horizon_years=6)
    assert len(p) == 7
    assert p[0]["year"] == 0
    assert p[-1]["year"] == 6


def test_simulate_path_invalid_horizon_raises():
    with pytest.raises(ValueError):
        simulate_planetary_path(_state(), horizon_years=0)


def test_intervention_allocator_fraction_sum_close_to_one():
    rows = intervention_allocator(_state(), budget_usd=1_000_000.0)
    frac_sum = sum(float(r["allocated_fraction"]) for r in rows)
    assert abs(frac_sum - 1.0) < 1e-10


def test_intervention_allocator_zero_budget():
    rows = intervention_allocator(_state(), budget_usd=0.0)
    assert all(r["allocated_budget_usd"] == 0.0 for r in rows)


def test_intervention_allocator_negative_budget_raises():
    with pytest.raises(ValueError):
        intervention_allocator(_state(), budget_usd=-1.0)


def test_scenario_risk_envelope_contract_and_ordering():
    r = scenario_risk_envelope(_state(), horizon_years=5, n_trials=40, seed=13)
    assert 0.0 <= float(r["p10_terminal"]) <= 1.0
    assert 0.0 <= float(r["p50_terminal"]) <= 1.0
    assert 0.0 <= float(r["p90_terminal"]) <= 1.0
    assert float(r["p10_terminal"]) <= float(r["p50_terminal"]) <= float(r["p90_terminal"])


def test_scenario_risk_envelope_seed_reproducible():
    a = scenario_risk_envelope(_state(), horizon_years=4, n_trials=40, seed=3)
    b = scenario_risk_envelope(_state(), horizon_years=4, n_trials=40, seed=3)
    assert a == b


def test_scenario_risk_envelope_invalid_inputs_raise():
    with pytest.raises(ValueError):
        scenario_risk_envelope(_state(), n_trials=9)
    with pytest.raises(ValueError):
        scenario_risk_envelope(_state(), sigma=-0.1)


def test_report_shape_and_falsification_clause():
    r = pillar252_planetary_digital_twin_report(horizon_years=5)
    assert r["provenance"]["pillar"] == 252
    assert len(r["path"]) == 6
    assert len(r["allocation"]) == len(SECTORS)
    assert "FALSIFIED" in r["falsification_condition"]
