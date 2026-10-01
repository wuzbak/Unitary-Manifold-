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
    assert surface["status"] == "ACTION_DERIVED_FIELD_EQUATIONS_WITH_DECLARED_RELAXATION_FLOW"
    assert surface["flow_law"] == "action_derived"
    assert "-2 R^E_μν" in surface["equations"]["metric"]["rhs_terms"]
    assert surface["equations"]["gauge"]["rhs_terms"] == ["g^E_νρ ∇_μ(λ² φ³ F^μρ)"]
    assert "α R φ" not in surface["equations"]["scalar"]["rhs_terms"]
    legacy = surface["legacy_flow_surface"]
    assert legacy["status"] == "PHENOMENOLOGICAL_FLOW_IMPLEMENTATION"
    assert legacy["equations"]["scalar"]["rhs_terms"] == ["□φ", "α R φ", "S[H]", "-m²_φ (φ − φ₀)"]
    assert surface["time_domain_boundary"]["identified_with_coordinate_time"] is False
    assert surface["time_domain_boundary"]["coordinate_time_gauge_fixed"] is True


def test_deliverable_contract_tracks_evidence_and_remaining_single_blocker() -> None:
    contract = action_to_evolution_deliverable_contract()
    deliverables = contract["primary_deliverables"]
    retirement_units = contract["retirement_units"]
    assert contract["status"] == "DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN"
    assert contract["promotion_ready"] is False
    assert len(deliverables) == 3
    assert len(retirement_units) == 7
    assert [item["id"] for item in deliverables] == PRIMARY_DELIVERABLE_IDS
    assert retirement_units[0]["claim_id"] == "A2E_VARIABLE_IDENTIFICATION"
    assert retirement_units[-1]["claim_id"] == "A2E_RESIDUAL_ERROR_COMPARISON"

    first = deliverables[0]
    assert first["earned"] is True
    assert first["status"] == "EVIDENCE_SURFACED"

    second = deliverables[1]
    assert second["earned"] is True
    assert second["status"] == "EARNED"
    assert second["steward_promotion"]["promoted"] is True
    assert second["euler_lagrange_mismatch_receipt"]["status"] == "RECEIPT_READY"

    third = deliverables[2]
    assert third["earned"] is True
    assert third["status"] == "EVIDENCE_SURFACED"

    assert contract["remaining_blockers"] == []
    assert "T_RELAXATION_LAW_DECLARED_NOT_DERIVED" in contract["residual_obligations"]
    assert contract["promotion_ready"] is False
    assert {
        item["status"] for item in retirement_units
    } <= {"CONDITIONAL_ONLY", "BLOCKED_NOT_YET_DERIVABLE", "CLOSED_NOW"}


def test_deliverable_contract_keeps_support_surfaces_secondary_only() -> None:
    contract = action_to_evolution_deliverable_contract()
    assert contract["secondary_support_only"]["unit_ids"] == SECONDARY_SUPPORT_ONLY_IDS
    assert "cannot stand in" in contract["secondary_support_only"]["guardrail"]
    assert contract["boundary"] == phenomenological_flow_boundary()
