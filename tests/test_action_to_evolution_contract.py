# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.action_to_evolution_contract import (
    PRIMARY_DELIVERABLE_IDS,
    SECONDARY_SUPPORT_ONLY_IDS,
    action_to_evolution_deliverable_contract,
)
from src.core.evolution import implemented_flow_equation_surface, phenomenological_flow_boundary


def test_implemented_flow_surface_stays_explicit() -> None:
    surface = implemented_flow_equation_surface()
    assert surface["status"] == "PHENOMENOLOGICAL_FLOW_IMPLEMENTATION"
    assert surface["equations"]["metric"]["rhs_terms"] == ["-2 R_μν", "T_μν[B, φ]"]
    assert surface["equations"]["gauge"]["rhs_terms"] == ["∇_ν (λ² H^νμ)"]
    assert surface["equations"]["scalar"]["rhs_terms"] == ["□φ", "α R φ", "S[H]", "-m²_φ (φ − φ₀)"]
    assert surface["time_domain_boundary"]["identified_with_coordinate_time"] is False
    assert surface["time_domain_boundary"]["coordinate_time_gauge_fixed"] is True


def test_deliverable_contract_matches_exact_three_blockers() -> None:
    contract = action_to_evolution_deliverable_contract()
    deliverables = contract["primary_deliverables"]
    assert contract["status"] == "OPEN"
    assert len(deliverables) == 3
    assert [item["id"] for item in deliverables] == PRIMARY_DELIVERABLE_IDS
    assert contract["remaining_blockers"] == PRIMARY_DELIVERABLE_IDS
    assert all(item["earned"] is False for item in deliverables)
    assert contract["promotion_ready"] is False


def test_deliverable_contract_keeps_support_surfaces_secondary_only() -> None:
    contract = action_to_evolution_deliverable_contract()
    assert contract["secondary_support_only"]["unit_ids"] == SECONDARY_SUPPORT_ONLY_IDS
    assert "cannot stand in" in contract["secondary_support_only"]["guardrail"]
    assert contract["boundary"] == phenomenological_flow_boundary()
