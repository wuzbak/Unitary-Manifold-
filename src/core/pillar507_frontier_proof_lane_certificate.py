# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 507 — Frontier Proof-Lane Completion Certificate.

STATUS: FRONTIER_PROOF_LANES_CERTIFIED

This pillar converts the requested frontier bundle into a single executable
certificate without overstating what is not yet externally proved.  It covers:

* non-perturbative 5D-KK/WdW quantization,
* P8 full functional-space residual,
* PMNS solar-angle residual,
* L2/γ non-perturbative braid-condensate external-confirmation lane,
* Lean4 certification status, and
* the CCR and ER=EPR quantum-theorem lanes.

The certificate is complete as a repository-side proof-lane ledger: every lane
has a status, evidence source, closure criterion, and hardgate-impact guard.
External receipts remain explicitly pending where the repository cannot create
them.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.core import pillar295_wheeler_dewitt_structural_gap_certificate as p295
from src.core import pillar455_p8_field_theoretic_proof as p455
from src.core import pillar456_quantum_theorem_formal_status as p456
from src.core import pillar503_pmns_pr_full_chain as p503
from src.core import pillar504_lattice_braid_phase4_np_condensate as p504

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "LANE_NAMES",
    "lean4_certification_manifest",
    "five_d_kk_quantization_lane",
    "p8_full_functional_space_lane",
    "pmns_solar_angle_residual_lane",
    "l2_gamma_external_confirmation_lane",
    "quantum_theorem_lanes",
    "frontier_lane_registry",
    "completion_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 507
PILLAR_STATUS: str = "FRONTIER_PROOF_LANES_CERTIFIED"
PILLAR_TITLE: str = "Frontier proof-lane completion certificate"
VERSION: str = "v15.4"

LANE_NAMES: List[str] = [
    "5D_KK_NONPERTURBATIVE_QUANTIZATION",
    "P8_FULL_FUNCTIONAL_SPACE",
    "PMNS_SOLAR_ANGLE_RESIDUAL",
    "L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION",
    "LEAN4_CERTIFICATION",
    "CCR_OPERATOR_LIMIT",
    "ER_EPR_KK_HOLOGRAPHY",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def lean4_certification_manifest() -> Dict[str, object]:
    """Return the local Lean4 certificate manifest and completion criterion."""
    lean_root = _repo_root() / "lean4"
    expected_modules = [
        "UnitaryManifold/Basic.lean",
        "UnitaryManifold/BraidUniqueness.lean",
        "UnitaryManifold/Extended.lean",
        "UnitaryManifold/FalsifierBoundary.lean",
        "UnitaryManifold/KCSTopological.lean",
        "UnitaryManifold/NumericalChecks.lean",
    ]
    module_presence = {
        module: (lean_root / module).exists()
        for module in expected_modules
    }
    return {
        "lane": "LEAN4_CERTIFICATION",
        "status": "LOCAL_CERTIFICATE_MANIFEST_PRESENT__BUILD_RECEIPT_REQUIRED",
        "lean_root": str(lean_root),
        "toolchain_present": (lean_root / "lean-toolchain").exists(),
        "lakefile_present": (lean_root / "lakefile.lean").exists(),
        "modules": module_presence,
        "all_expected_files_present": all(module_presence.values()),
        "completion_criterion": "Attach a successful `cd lean4 && lake build` receipt for the current commit.",
        "hardgate_score_delta": 0.0,
    }


def five_d_kk_quantization_lane() -> Dict[str, object]:
    """Package the non-perturbative 5D-KK quantization proof-lane status."""
    cert = p295.wdw_architecture_limit_certificate()
    return {
        "lane": "5D_KK_NONPERTURBATIVE_QUANTIZATION",
        "status": cert["gap_status"],
        "evidence_pillar": p295.PILLAR_NUMBER,
        "gap_name": cert["gap_name"],
        "closed_at": cert["closed_at"],
        "open_regime": cert["open_regime"],
        "nonperturbative_full_solution_claimed": False,
        "structural_gap_certified": True,
        "closure_criterion": cert["requires"],
        "hardgate_score_delta": 0.0,
    }


def p8_full_functional_space_lane() -> Dict[str, object]:
    """Package the P8 integer-lattice proof and full-function-space residual."""
    proof = p455.prove_minimum_step_uniqueness()
    residual = p455.named_residual_statement()
    return {
        "lane": "P8_FULL_FUNCTIONAL_SPACE",
        "status": residual["status"],
        "evidence_pillar": 455,
        "integer_lattice_proved": bool(proof["integer_lattice_proved"]),
        "canonical_pair": proof["unique_global_pair"],
        "full_function_space_proved": False,
        "residual_name": residual["name"],
        "closure_criterion": residual["what_would_close_it"],
        "hardgate_score_delta": 0.0,
    }


def pmns_solar_angle_residual_lane() -> Dict[str, object]:
    """Package the PMNS p_R solar-angle residual status."""
    consistency = p503.full_chain_consistency()
    window = consistency["solar_window"]
    return {
        "lane": "PMNS_SOLAR_ANGLE_RESIDUAL",
        "status": consistency["status"],
        "evidence_pillar": p503.PILLAR_NUMBER,
        "residual_name": consistency["residual_name"],
        "target_in_window": bool(window["target_in_window"]),
        "center_residual_deg": window["center_residual_deg"],
        "residual_retained": bool(consistency["pdg_gap_retained"]),
        "closure_criterion": "Solve the microscopic three-generation RS Dirac/Yukawa system and remove the p_R surrogate.",
        "hardgate_score_delta": consistency["hardgate_score_delta"],
    }


def l2_gamma_external_confirmation_lane() -> Dict[str, object]:
    """Package the L2/γ braid-condensate external confirmation lane."""
    cert = p504.l2_closure_certificate()
    return {
        "lane": "L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION",
        "status": "EXTERNAL_CONFIRMATION_PACKET_READY__HMC_RECEIPT_PENDING",
        "evidence_pillar": p504.PILLAR_NUMBER,
        "finite_volume_bound_status": cert["status"],
        "finite_volume_monotone_stable": cert["finite_volume_monotone_stable"],
        "external_hmc_receipt": cert["external_hmc_receipt"],
        "residual_band": cert["residual_band"],
        "closure_criterion": "Attach an independent lattice/HMC condensate receipt matching the registered residual band.",
        "hardgate_score_delta": cert["hardgate_score_delta"],
    }


def quantum_theorem_lanes() -> Dict[str, Dict[str, object]]:
    """Package CCR and ER=EPR as explicit theorem lanes."""
    ccr = p456.ccr_formal_conjecture()
    er_epr = p456.er_epr_formal_conjecture()
    return {
        "CCR_OPERATOR_LIMIT": {
            "lane": "CCR_OPERATOR_LIMIT",
            "status": ccr["status"],
            "evidence_pillar": 456,
            "statement": ccr["statement"],
            "obstruction": ccr["obstruction"],
            "closure_criterion": ccr["proof_criteria"],
            "hardgate_score_delta": 0.0,
        },
        "ER_EPR_KK_HOLOGRAPHY": {
            "lane": "ER_EPR_KK_HOLOGRAPHY",
            "status": er_epr["status"],
            "evidence_pillar": 456,
            "statement": er_epr["statement"],
            "obstruction": er_epr["obstruction"],
            "closure_criterion": er_epr["proof_criteria"],
            "hardgate_score_delta": 0.0,
        },
    }


def frontier_lane_registry() -> Dict[str, Dict[str, object]]:
    """Return all frontier proof lanes keyed by canonical lane name."""
    theorem_lanes = quantum_theorem_lanes()
    return {
        "5D_KK_NONPERTURBATIVE_QUANTIZATION": five_d_kk_quantization_lane(),
        "P8_FULL_FUNCTIONAL_SPACE": p8_full_functional_space_lane(),
        "PMNS_SOLAR_ANGLE_RESIDUAL": pmns_solar_angle_residual_lane(),
        "L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION": l2_gamma_external_confirmation_lane(),
        "LEAN4_CERTIFICATION": lean4_certification_manifest(),
        "CCR_OPERATOR_LIMIT": theorem_lanes["CCR_OPERATOR_LIMIT"],
        "ER_EPR_KK_HOLOGRAPHY": theorem_lanes["ER_EPR_KK_HOLOGRAPHY"],
    }


def completion_certificate() -> Dict[str, object]:
    """Return the Pillar 507 completion certificate."""
    registry = frontier_lane_registry()
    external_receipt_pending = [
        name for name, lane in registry.items()
        if "RECEIPT_PENDING" in str(lane["status"]) or "BUILD_RECEIPT_REQUIRED" in str(lane["status"])
    ]
    unproved_but_named = [
        name for name, lane in registry.items()
        if lane["status"] in {"NAMED_RESIDUAL", "CONJECTURAL", p295.GAP_STATUS}
    ]
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "lane_count": len(registry),
        "all_expected_lanes_present": sorted(registry) == sorted(LANE_NAMES),
        "all_lanes_have_closure_criteria": all(bool(lane.get("closure_criterion") or lane.get("completion_criterion")) for lane in registry.values()),
        "external_receipt_pending": external_receipt_pending,
        "unproved_but_named": unproved_but_named,
        "hardgate_score_delta": sum(float(lane["hardgate_score_delta"]) for lane in registry.values()),
        "claim_guard": "Conjectural, external, and architecture-limit lanes are not promoted to hardgate proof.",
    }


def pillar_report() -> Dict[str, object]:
    """Machine-readable Pillar 507 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "lanes": frontier_lane_registry(),
        "certificate": completion_certificate(),
    }
