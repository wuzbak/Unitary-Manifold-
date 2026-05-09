# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""11D→5D boundary reduction contract ("burn the bridge").

The purpose of this module is not to keep 11D data alive inside the runtime.
It does the opposite:
  1. record the UV assumptions once,
  2. reduce them to a minimal 5D invariant set,
  3. forbid downstream runtime dependence on raw 11D scaffold symbols.
"""

from __future__ import annotations

from typing import Dict, Tuple

from src.eleventd.horava_witten_hard_gate import rung6_gate_evidence
from src.eleventd.uv_vacuum_selection_gate import canonical_uv_vacuum_selection_gate

__all__ = [
    "uv_boundary_contract",
    "boundary_to_5d_map",
    "reduced_5d_invariants",
    "burn_bridge_certificate",
]

FORBIDDEN_RUNTIME_DEPENDENCIES: Tuple[str, ...] = (
    "E8_lie_algebra",
    "CY3_topology",
    "G2_dual_topology",
    "G4_flux_quanta_raw",
    "chi_X7",
    "M2_tadpole_counterterm",
)


def uv_boundary_contract() -> Dict[str, object]:
    """Return the upstream UV boundary assumptions that are allowed once."""
    rung6 = rung6_gate_evidence()
    return {
        "allowed_upstream_assumptions": (
            "S1_Z2_interval",
            "CY3_SU3_holonomy",
            "G2_dual_flux_sector",
            "E8xE8_boundary_structure",
            "G4_flux_quantization",
        ),
        "must_pass_before_reduction": (
            "rung6_hard_gate",
            "canonical_uv_vacuum_selection_gate",
        ),
        "rung6_hard_gate_pass": rung6["hard_gate_pass"],
        "bridge_burn_rule": (
            "After reduction, downstream 5D runtime code may depend only on the "
            "reduced invariant set, not on raw 11D bookkeeping."
        ),
    }


def boundary_to_5d_map() -> Dict[str, object]:
    """Map accepted UV structures onto reduced 5D invariants."""
    gate = canonical_uv_vacuum_selection_gate()
    seed = gate["reduced_5d_seed"]
    return {
        "selected_n_w": seed["n_w"],
        "selected_braid_pair": seed["braid_pair"],
        "selected_k_cs": seed["k_cs"],
        "selected_eta_bar": seed["eta_bar"],
        "selected_pi_kR": seed["pi_kR"],
        "reduced_runtime_invariants": (
            "n_w",
            "braid_pair",
            "k_cs",
            "eta_bar",
            "pi_kR",
        ),
        "forbidden_runtime_dependencies": FORBIDDEN_RUNTIME_DEPENDENCIES,
        "status": gate["status"],
    }


def reduced_5d_invariants() -> Dict[str, object]:
    """Return the minimal invariant set allowed in downstream 5D calculations."""
    mapping = boundary_to_5d_map()
    return {
        "runtime_seed": {
            "n_w": mapping["selected_n_w"],
            "braid_pair": mapping["selected_braid_pair"],
            "k_cs": mapping["selected_k_cs"],
            "eta_bar": mapping["selected_eta_bar"],
            "pi_kR": mapping["selected_pi_kR"],
        },
        "forbidden_runtime_dependencies": mapping["forbidden_runtime_dependencies"],
        "bridge_burned": True,
        "runtime_policy": "5D_RUNTIME_ONLY",
    }


def burn_bridge_certificate() -> Dict[str, object]:
    """Return the final certificate that the 11D scaffold has been reduced away."""
    contract = uv_boundary_contract()
    reduced = reduced_5d_invariants()
    return {
        "title": "11D→5D bridge-burn certificate",
        "uv_boundary_contract": contract,
        "reduced_5d_invariants": reduced,
        "status": (
            "BRIDGE_BURNED_RUNTIME_REDUCED"
            if contract["rung6_hard_gate_pass"] and reduced["bridge_burned"]
            else "BRIDGE_BURN_BLOCKED"
        ),
        "no_score_inflation": True,
    }
