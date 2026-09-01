# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Sprint BA constants wrapper for az-kernel."""
from __future__ import annotations

import json
from copy import deepcopy
from fractions import Fraction
from typing import Any, Dict, Mapping

SPRINT_BA_CONSTANTS: Dict[str, Any] = {
    "app": "02-az-kernel",
    "repository_version": "v25.5",
    "sprint": "BA",
    "status_labels": ["CLOSED", "PARTIAL", "OPEN"],
    "constants": {
        "winding_number": {
            "value": 5,
            "status": "CLOSED",
            "notes": "Framework seed constant used for Sprint BA consistency checks.",
        },
        "braid_partner": {
            "value": 7,
            "status": "CLOSED",
            "notes": "Companion winding used in the k_CS resonance identity.",
        },
        "k_cs": {
            "value": 74,
            "pillar": "P849",
            "status": "CLOSED",
            "notes": "Fixed by the 9D Green-Schwarz closure.",
        },
        "braided_sound_speed": {
            "value": Fraction(12, 37),
            "status": "CLOSED",
            "notes": "Derived from the braid identity (49-25)/74 = 24/74 = 12/37.",
        },
        "phi0": {
            "value": 1.0,
            "pillar": "P853",
            "status": "PARTIAL",
            "notes": "Tracked as a partial Sprint BA closure.",
        },
        "dimensional_chain": {
            "value": [11, 10, 9, 8, 7, 6, 5, 4],
            "step_count": 7,
            "pillar": "P858",
            "status": "CLOSED",
            "notes": "Closed 7-step descent from 11D to 4D.",
        },
    },
}


def _serialise(obj: Any) -> Any:
    if isinstance(obj, Fraction):
        return str(obj)
    if isinstance(obj, dict):
        return {key: _serialise(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_serialise(value) for value in obj]
    return obj


def get_sprint_ba_constants() -> Dict[str, Any]:
    """Return a defensive copy of the az-kernel Sprint BA constants."""
    return deepcopy(SPRINT_BA_CONSTANTS)


def validate_constants(payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Check internal consistency for the Sprint BA constants payload."""
    data = deepcopy(dict(payload)) if payload is not None else get_sprint_ba_constants()
    constants = data["constants"]

    winding_number = int(constants["winding_number"]["value"])
    braid_partner = int(constants["braid_partner"]["value"])
    k_cs = int(constants["k_cs"]["value"])
    phi0 = float(constants["phi0"]["value"])
    chain = list(constants["dimensional_chain"]["value"])
    step_count = int(constants["dimensional_chain"]["step_count"])
    c_s_value = Fraction(constants["braided_sound_speed"]["value"])

    checks = {
        "k_cs_identity": k_cs == winding_number ** 2 + braid_partner ** 2,
        "braided_sound_speed_identity": c_s_value == Fraction(braid_partner ** 2 - winding_number ** 2, k_cs),
        "phi0_unit_normalised": abs(phi0 - 1.0) < 1e-12,
        "phi0_status_honest": constants["phi0"]["status"] == "PARTIAL",
        "dimensional_chain_endpoints": chain[0] == 11 and chain[-1] == 4,
        "dimensional_chain_monotonic": all(chain[index] - chain[index + 1] == 1 for index in range(len(chain) - 1)),
        "dimensional_chain_step_count": step_count == len(chain) - 1 == 7,
        "closed_statuses_honest": constants["k_cs"]["status"] == "CLOSED" and constants["dimensional_chain"]["status"] == "CLOSED",
        "status_labels_supported": data["status_labels"] == ["CLOSED", "PARTIAL", "OPEN"],
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "constants": _serialise(constants),
    }


def self_test() -> Dict[str, Any]:
    """Run the built-in validation payload."""
    return validate_constants()


def main() -> int:
    """Run a CLI self-test and print the validation payload as JSON."""
    result = self_test()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("Sprint BA constants self-test: PASS" if result["valid"] else "Sprint BA constants self-test: FAIL")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
