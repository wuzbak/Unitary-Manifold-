# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 250 — Quantum-Materials Hardware Inverse-Design Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar250_quantum_materials_hardware_inverse_design_engine import (
    ADJACENCY_TRACK_LABEL,
    BRAID_PAIR,
    C_S,
    DOMAIN_ORDER,
    K_CS,
    N_W,
    PHI0,
    QUANTUM_HARDWARE_TRACK_LABEL,
    QuantumHardwareScenario,
    SCORE_WEIGHTS,
    __provenance__,
    architecture_alignment_scores,
    baseline_quantum_hardware_scenario,
    hardware_domain_scores,
    intervention_priority,
    inverse_design_readiness_surface,
    monte_carlo_readiness,
    pillar250_quantum_hardware_inverse_design_report,
    separation_guard,
)


def _scenario() -> QuantumHardwareScenario:
    return baseline_quantum_hardware_scenario()


def test_provenance_contract():
    assert __provenance__["pillar"] == 250
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_framework_constants_contract():
    assert N_W == 5
    assert K_CS == 74
    assert K_CS == 5**2 + 7**2
    assert BRAID_PAIR == (5, 7)
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_domain_weights_cover_domain_order_and_sum_to_one():
    assert tuple(SCORE_WEIGHTS.keys()) == DOMAIN_ORDER
    assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-12


def test_separation_guard_contract():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["track"] == QUANTUM_HARDWARE_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["toe_score_delta_allowed"] is False
    assert g["device_performance_guarantee_allowed"] is False


def test_baseline_schema_sanity():
    s = _scenario()
    assert isinstance(s, QuantumHardwareScenario)
    assert s.coherence_time_us > 0
    assert s.two_qubit_gate_time_ns > 0
    assert 0.0 <= s.two_qubit_fidelity <= 1.0


@pytest.mark.parametrize(
    "field,value",
    [
        ("two_qubit_fidelity", 1.2),
        ("fabrication_yield_fraction", -0.1),
        ("coherence_time_us", 0.0),
        ("thermal_budget_mw", 0.0),
    ],
)
def test_schema_validation_raises(field: str, value: float):
    s = _scenario()
    with pytest.raises(ValueError):
        QuantumHardwareScenario(**{**s.__dict__, field: value})


def test_hardware_domain_scores_shape_and_range():
    r = hardware_domain_scores(_scenario())
    assert tuple(r.keys()) == DOMAIN_ORDER
    for v in r.values():
        assert 0.0 <= v <= 1.0


def test_readiness_surface_range():
    score = inverse_design_readiness_surface(_scenario())
    assert 0.0 <= score <= 1.0


def test_readiness_improves_for_stronger_scenario():
    s = _scenario()
    stronger = QuantumHardwareScenario(
        **{
            **s.__dict__,
            "coherence_time_us": s.coherence_time_us * 2.0,
            "two_qubit_fidelity": 0.992,
            "fabrication_yield_fraction": 0.88,
            "error_correction_overhead": 0.35,
            "defect_density_ppm": 3.0,
        }
    )
    assert inverse_design_readiness_surface(stronger) > inverse_design_readiness_surface(s)


def test_architecture_alignment_sorted_descending():
    rows = architecture_alignment_scores(_scenario())
    assert len(rows) == 4
    for i in range(len(rows) - 1):
        assert rows[i]["alignment_score"] >= rows[i + 1]["alignment_score"]


def test_intervention_priority_zero_budget():
    rows = intervention_priority(_scenario(), budget_usd=0.0)
    assert len(rows) == len(DOMAIN_ORDER)
    assert all(r["allocated_budget_usd"] == 0.0 for r in rows)


def test_intervention_priority_negative_budget_raises():
    with pytest.raises(ValueError):
        intervention_priority(_scenario(), budget_usd=-1.0)


def test_intervention_priority_fraction_sum_close_to_one():
    rows = intervention_priority(_scenario(), budget_usd=1_000_000.0)
    frac_sum = sum(float(r["allocated_fraction"]) for r in rows)
    assert abs(frac_sum - 1.0) < 1e-10


def test_monte_carlo_readiness_contract_and_ordering():
    r = monte_carlo_readiness(_scenario(), n_trials=40, seed=42)
    assert 0.0 <= float(r["p10"]) <= 1.0
    assert 0.0 <= float(r["p50"]) <= 1.0
    assert 0.0 <= float(r["p90"]) <= 1.0
    assert float(r["p10"]) <= float(r["p50"]) <= float(r["p90"])


def test_monte_carlo_readiness_seed_reproducible():
    a = monte_carlo_readiness(_scenario(), n_trials=40, seed=7)
    b = monte_carlo_readiness(_scenario(), n_trials=40, seed=7)
    assert a == b


def test_monte_carlo_invalid_inputs_raise():
    with pytest.raises(ValueError):
        monte_carlo_readiness(_scenario(), n_trials=5)
    with pytest.raises(ValueError):
        monte_carlo_readiness(_scenario(), sigma=-0.1)


def test_report_shape_and_falsification_clause():
    r = pillar250_quantum_hardware_inverse_design_report()
    assert r["provenance"]["pillar"] == 250
    assert 0.0 <= r["readiness_score"] <= 1.0
    assert len(r["intervention_priority"]) == len(DOMAIN_ORDER)
    assert "FALSIFIED" in r["falsification_condition"]
