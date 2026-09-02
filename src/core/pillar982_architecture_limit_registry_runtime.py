# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 982 — Runtime Architecture-Limit Registry (Sprint BL).

Creates a single machine-readable runtime artifact for the *current* open lanes,
explicitly linking each lane to:
- present status,
- the limiting boundary class,
- missing architectural objects,
- executable closure tests.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar949_cy4_intersection_ring_g4_explicit import B3_G4_OUTCOME
from src.core.pillar950_ckm_kk_excited_states_audit import KK_CORRECTION_REGIME
from src.core.pillar951_fermion_ri_constraint_scaffold import RI_WINDOW_STATUS
from src.core.pillar952_observational_readiness_v4 import OPEN_LANES
from src.core.pillar980_jarlskog_layer2_architecture_limit import BINARY_OUTCOME
from src.core.pillar987_uv_completion_compactification_layer import solve_uv_moduli_point
from src.core.pillar988_fully_coupled_kk_backreaction_engine import run_fully_coupled_kk_backreaction
from src.core.pillar989_flavor_closure_geometric_layer import flavor_closure_observables

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "RUNTIME_ARCHITECTURE_LIMIT_REGISTRY",
    "DEEP_LAYER_LINKS",
    "runtime_architecture_limit_registry",
]

PILLAR_NUMBER: int = 982
PILLAR_GATE: str = "RUNTIME_ARCHITECTURE_LIMIT_REGISTRY"

_UV = solve_uv_moduli_point()
_KK = run_fully_coupled_kk_backreaction(steps=12)
_FLAVOR = flavor_closure_observables()

DEEP_LAYER_LINKS: Dict[str, Dict[str, Any]] = {
    "uv_layer_987": {
        "status": _UV["status"],
        "best_point": {
            "tau": _UV["best_point"]["tau"],
            "rho": _UV["best_point"]["rho"],
            "score": _UV["best_point"]["score"],
        },
    },
    "kk_layer_988": {
        "status": _KK["status"],
        "tail_spread": _KK["tail_spread"],
        "mean_winding_abs": _KK["mean_winding_abs"],
    },
    "flavor_layer_989": {
        "status": _FLAVOR["status"],
        "theta13_deg": _FLAVOR["theta13_deg"],
        "vub": _FLAVOR["vub"],
    },
}

RUNTIME_ARCHITECTURE_LIMIT_REGISTRY: List[Dict[str, Any]] = [
    {
        "lane": "B3_G4_FLUX",
        "status": B3_G4_OUTCOME,
        "boundary_class": "UV_GLOBAL_GEOMETRY",
        "missing_objects": [
            "full_CY4_intersection_ring",
            "global_flux_basis_resolution",
            "moduli_stabilized_representative_G4",
        ],
        "closure_test": "construct explicit non-ambiguous G4 representative with unique integer N_D3",
        "evidence": "src/core/pillar949_cy4_intersection_ring_g4_explicit.py",
        "deep_layer_ref": "uv_layer_987",
    },
    {
        "lane": "CKM_THETA13",
        "status": f"TRUE_ARCHITECTURE_LIMIT_{KK_CORRECTION_REGIME}",
        "boundary_class": "UV_FLAVOR_STRUCTURES",
        "missing_objects": [
            "global_flavor_bundle_geometry",
            "nonlocal_wavefunction_overlap_tensor",
        ],
        "closure_test": "derive theta13 and |Vub| from compactification geometry without fitted radii",
        "evidence": "src/core/pillar950_ckm_kk_excited_states_audit.py",
        "deep_layer_ref": "flavor_layer_989",
    },
    {
        "lane": "FERMION_MASS_MAGNITUDES",
        "status": RI_WINDOW_STATUS,
        "boundary_class": "UV_FLAVOR_STRUCTURES",
        "missing_objects": [
            "species-resolved_Ri_geometry",
            "bundle/moduli locking for Yukawa magnitudes",
        ],
        "closure_test": "predict charged-fermion magnitude ladder without ad hoc species-dependent placements",
        "evidence": "src/core/pillar951_fermion_ri_constraint_scaffold.py",
        "deep_layer_ref": "flavor_layer_989",
    },
    {
        "lane": "JARLSKOG_LAYER2",
        "status": BINARY_OUTCOME,
        "boundary_class": "UV_FLAVOR_STRUCTURES",
        "missing_objects": [
            "higher-order flavor torsion completion",
            "global CKM phase geometry beyond in-EFT cap",
        ],
        "closure_test": "reduce residual below 1 percentage point via a derived UV mechanism",
        "evidence": "src/core/pillar980_jarlskog_layer2_architecture_limit.py",
        "deep_layer_ref": "flavor_layer_989",
    },
    {
        "lane": "CMB_AMP",
        "status": "FULLY_CONFIRMED_IRREDUCIBLE",
        "boundary_class": "NONPERTURBATIVE_UV_DYNAMICS",
        "missing_objects": [
            "nonperturbative amplitude-generation mechanism",
            "global UV completion of transfer normalization",
        ],
        "closure_test": "produce observed A_s normalization without free UV insertion",
        "evidence": "src/core/pillar952_observational_readiness_v4.py",
        "deep_layer_ref": "kk_layer_988",
    },
    {
        "lane": "ALPHA_S_TYPE_B_FLOOR",
        "status": "ARCHITECTURE_LIMIT",
        "boundary_class": "UV_GLOBAL_GEOMETRY",
        "missing_objects": [
            "fully specified CY moduli point",
            "high-order threshold map at compactification scale",
        ],
        "closure_test": "bring tightened alpha_s window into PDG support via derived compactification data",
        "evidence": "src/core/pillar952_observational_readiness_v4.py",
        "deep_layer_ref": "uv_layer_987",
    },
]


def _by_boundary(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in entries:
        key = str(row["boundary_class"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def runtime_architecture_limit_registry() -> Dict[str, Any]:
    """Return canonical runtime registry and summary statistics."""
    open_lane_ids = {entry["item"] for entry in OPEN_LANES}
    lane_alias = {
        "CKM_THETA13": "CKM_TEXTURE_13D",
        "FERMION_MASS_MAGNITUDES": "FERMION_MASS_RATIO",
        "ALPHA_S_TYPE_B_FLOOR": "ALPHA_S_13D",
    }
    mapped_open = 0
    for row in RUNTIME_ARCHITECTURE_LIMIT_REGISTRY:
        lane = str(row["lane"])
        if lane in open_lane_ids or lane_alias.get(lane) in open_lane_ids:
            mapped_open += 1
    n_rows = len(RUNTIME_ARCHITECTURE_LIMIT_REGISTRY)
    boundary_counts = _by_boundary(RUNTIME_ARCHITECTURE_LIMIT_REGISTRY)
    uv_clustered = boundary_counts.get("UV_GLOBAL_GEOMETRY", 0) + boundary_counts.get("UV_FLAVOR_STRUCTURES", 0)
    valid = n_rows >= 6 and mapped_open >= 4
    deep_links_covered = all(
        ("deep_layer_ref" in row and row["deep_layer_ref"] in DEEP_LAYER_LINKS)
        for row in RUNTIME_ARCHITECTURE_LIMIT_REGISTRY
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid and deep_links_covered,
        "rows": RUNTIME_ARCHITECTURE_LIMIT_REGISTRY,
        "n_rows": n_rows,
        "open_lanes_mapped": mapped_open,
        "open_lanes_total": len(open_lane_ids),
        "boundary_counts": boundary_counts,
        "deep_layer_links": DEEP_LAYER_LINKS,
        "deep_links_covered": deep_links_covered,
        "architecture_signal": {
            "uv_cluster_fraction": uv_clustered / n_rows,
            "interpretation": (
                "Most surviving limits cluster around UV/global geometry and UV flavor structures, "
                "supporting a coherent boundary rather than random model failure."
            ),
        },
    }


PILLAR_STATUS: str = "RUNTIME_ARCHITECTURE_LIMIT_REGISTRY_COMPLETE"
PILLAR_VALID: bool = runtime_architecture_limit_registry()["valid"]
