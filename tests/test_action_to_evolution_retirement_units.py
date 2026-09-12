# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.action_to_evolution_retirement_units import (
    build_action_to_evolution_retirement_units,
)


def test_retirement_units_surface_exact_board() -> None:
    units = build_action_to_evolution_retirement_units()
    assert len(units) == 7
    assert units[0]["claim_id"] == "A2E_VARIABLE_IDENTIFICATION"
    assert units[-1]["claim_id"] == "A2E_RESIDUAL_ERROR_COMPARISON"
    assert {item["status"] for item in units} <= {
        "CONDITIONAL_ONLY",
        "BLOCKED_NOT_YET_DERIVABLE",
        "CLOSED_NOW",
    }
