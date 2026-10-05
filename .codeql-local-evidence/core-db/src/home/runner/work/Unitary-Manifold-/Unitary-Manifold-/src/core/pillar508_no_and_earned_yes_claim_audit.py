# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 508 — No-Claim / Earned-Yes Claim Audit.

This module turns the requested "no" and earned "yes" boundary into an
executable claim ledger.  It consumes the Pillar 507 frontier proof-lane
certificate and emits two disjoint boards:

* `no_claim_board()` — lanes that must not be represented as closed/proved
  without external receipts or stronger mathematics.
* `earned_yes_board()` — repository-side statuses that are actually earned by
  executable evidence already present in the repository.

The audit is intentionally conservative: every no-claim lane has a blocking
criterion, every earned-yes lane has a concrete evidence pointer, and the net
hardgate score delta is zero.
"""
from __future__ import annotations

from typing import Dict, List

from src.core import pillar507_frontier_proof_lane_certificate as p507

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "NO_CLAIM_KEYS",
    "EARNED_YES_KEYS",
    "no_claim_board",
    "earned_yes_board",
    "claim_boundary_audit",
    "pillar_report",
]

PILLAR_NUMBER: int = 508
PILLAR_STATUS: str = "NO_AND_EARNED_YES_AUDIT_COMPLETE"
PILLAR_TITLE: str = "No-claim and earned-yes claim-boundary audit"
VERSION: str = "v15.5"

NO_CLAIM_KEYS: List[str] = [
    "FULL_NONPERTURBATIVE_5D_KK_QUANTUM_GRAVITY_CLOSURE",
    "P8_FULL_FUNCTIONAL_SPACE_PROOF",
    "EXTERNAL_L2_GAMMA_HMC_RECEIPT",
    "LEAN4_BUILD_RECEIPT",
    "CCR_THEOREM_PROOF",
    "ER_EPR_THEOREM_PROOF",
]

EARNED_YES_KEYS: List[str] = [
    "FRONTIER_PROOF_LANE_LEDGER_COMPLETE",
    "P8_INTEGER_LATTICE_PROOF",
    "FIVE_D_KK_STRUCTURAL_GAP_CERTIFIED",
    "L2_GAMMA_FINITE_VOLUME_BOUND_PACKET",
    "LEAN4_LOCAL_MANIFEST_PRESENT",
    "CCR_ER_EPR_CONJECTURE_LANES_FORMALIZED",
]


def _lane_registry() -> Dict[str, Dict[str, object]]:
    return p507.frontier_lane_registry()


def no_claim_board() -> Dict[str, Dict[str, object]]:
    """Return the forbidden-overclaim board for frontier lanes."""
    lanes = _lane_registry()
    return {
        "FULL_NONPERTURBATIVE_5D_KK_QUANTUM_GRAVITY_CLOSURE": {
            "claim": "No full non-perturbative 5D-KK quantum-gravity closure is claimed.",
            "status": "NO_CLAIM__ARCHITECTURE_LIMIT_CERTIFIED",
            "source_lane": "5D_KK_NONPERTURBATIVE_QUANTIZATION",
            "evidence_status": lanes["5D_KK_NONPERTURBATIVE_QUANTIZATION"]["status"],
            "claimed_as_closed": bool(lanes["5D_KK_NONPERTURBATIVE_QUANTIZATION"].get("nonperturbative_full_solution_claimed")),
            "blocking_criterion": lanes["5D_KK_NONPERTURBATIVE_QUANTIZATION"]["closure_criterion"],
            "hardgate_score_delta": 0.0,
        },
        "P8_FULL_FUNCTIONAL_SPACE_PROOF": {
            "claim": "No P8 full functional-space proof is claimed.",
            "status": "NO_CLAIM__NAMED_RESIDUAL",
            "source_lane": "P8_FULL_FUNCTIONAL_SPACE",
            "evidence_status": lanes["P8_FULL_FUNCTIONAL_SPACE"]["status"],
            "claimed_as_closed": bool(lanes["P8_FULL_FUNCTIONAL_SPACE"].get("full_function_space_proved")),
            "blocking_criterion": lanes["P8_FULL_FUNCTIONAL_SPACE"]["closure_criterion"],
            "hardgate_score_delta": 0.0,
        },
        "EXTERNAL_L2_GAMMA_HMC_RECEIPT": {
            "claim": "No external L2/γ HMC receipt is claimed.",
            "status": "NO_CLAIM__EXTERNAL_RECEIPT_PENDING",
            "source_lane": "L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION",
            "evidence_status": lanes["L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION"]["status"],
            "claimed_as_closed": bool(lanes["L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION"].get("external_hmc_receipt")),
            "blocking_criterion": lanes["L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION"]["closure_criterion"],
            "hardgate_score_delta": 0.0,
        },
        "LEAN4_BUILD_RECEIPT": {
            "claim": "No Lean4 build receipt is claimed.",
            "status": "NO_CLAIM__BUILD_RECEIPT_REQUIRED",
            "source_lane": "LEAN4_CERTIFICATION",
            "evidence_status": lanes["LEAN4_CERTIFICATION"]["status"],
            "claimed_as_closed": "BUILD_RECEIPT_REQUIRED" not in str(lanes["LEAN4_CERTIFICATION"]["status"]),
            "blocking_criterion": lanes["LEAN4_CERTIFICATION"]["completion_criterion"],
            "hardgate_score_delta": 0.0,
        },
        "CCR_THEOREM_PROOF": {
            "claim": "CCR remains a conjectural theorem lane, not a proved theorem.",
            "status": "NO_CLAIM__CONJECTURAL",
            "source_lane": "CCR_OPERATOR_LIMIT",
            "evidence_status": lanes["CCR_OPERATOR_LIMIT"]["status"],
            "claimed_as_closed": lanes["CCR_OPERATOR_LIMIT"]["status"] != "CONJECTURAL",
            "blocking_criterion": lanes["CCR_OPERATOR_LIMIT"]["closure_criterion"],
            "hardgate_score_delta": 0.0,
        },
        "ER_EPR_THEOREM_PROOF": {
            "claim": "ER=EPR remains a conjectural theorem lane, not a proved theorem.",
            "status": "NO_CLAIM__CONJECTURAL",
            "source_lane": "ER_EPR_KK_HOLOGRAPHY",
            "evidence_status": lanes["ER_EPR_KK_HOLOGRAPHY"]["status"],
            "claimed_as_closed": lanes["ER_EPR_KK_HOLOGRAPHY"]["status"] != "CONJECTURAL",
            "blocking_criterion": lanes["ER_EPR_KK_HOLOGRAPHY"]["closure_criterion"],
            "hardgate_score_delta": 0.0,
        },
    }


def earned_yes_board() -> Dict[str, Dict[str, object]]:
    """Return the statuses that are positively earned by repository evidence."""
    lanes = _lane_registry()
    certificate = p507.completion_certificate()
    return {
        "FRONTIER_PROOF_LANE_LEDGER_COMPLETE": {
            "yes": "The frontier proof-lane ledger is complete as a repository-side certificate.",
            "status": p507.PILLAR_STATUS,
            "evidence": "src/core/pillar507_frontier_proof_lane_certificate.py",
            "earned": bool(certificate["all_expected_lanes_present"] and certificate["all_lanes_have_closure_criteria"]),
            "scope": "repository-side ledger completeness only",
        },
        "P8_INTEGER_LATTICE_PROOF": {
            "yes": "P8 minimum-step uniqueness is proved on the audited integer winding lattice.",
            "status": "PROVED_OVER_INTEGER_LATTICE",
            "evidence": "src/core/pillar455_p8_field_theoretic_proof.py",
            "earned": bool(lanes["P8_FULL_FUNCTIONAL_SPACE"]["integer_lattice_proved"]),
            "scope": "integer winding lattice, not full functional space",
        },
        "FIVE_D_KK_STRUCTURAL_GAP_CERTIFIED": {
            "yes": "The non-perturbative 5D-KK/WdW gap is structurally named and certified.",
            "status": lanes["5D_KK_NONPERTURBATIVE_QUANTIZATION"]["status"],
            "evidence": "src/core/pillar295_wheeler_dewitt_structural_gap_certificate.py",
            "earned": bool(lanes["5D_KK_NONPERTURBATIVE_QUANTIZATION"].get("structural_gap_certified")),
            "scope": "gap certification, not quantum-gravity closure",
        },
        "L2_GAMMA_FINITE_VOLUME_BOUND_PACKET": {
            "yes": "The L2/γ finite-volume braid-condensate bound packet is repository-ready.",
            "status": lanes["L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION"]["finite_volume_bound_status"],
            "evidence": "src/core/pillar504_lattice_braid_phase4_np_condensate.py",
            "earned": bool(lanes["L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION"]["finite_volume_monotone_stable"]),
            "scope": "finite-volume packet; external HMC receipt still pending",
        },
        "LEAN4_LOCAL_MANIFEST_PRESENT": {
            "yes": "The local Lean4 manifest is present and file-complete.",
            "status": lanes["LEAN4_CERTIFICATION"]["status"],
            "evidence": "lean4/lean-toolchain, lean4/lakefile.lean, lean4/UnitaryManifold/*.lean",
            "earned": bool(lanes["LEAN4_CERTIFICATION"]["all_expected_files_present"]),
            "scope": "local manifest only; no build receipt",
        },
        "CCR_ER_EPR_CONJECTURE_LANES_FORMALIZED": {
            "yes": "CCR and ER=EPR are formally stated conjecture lanes with closure criteria.",
            "status": "FORMAL_CONJECTURE_LANES_PRESENT",
            "evidence": "src/core/pillar456_quantum_theorem_formal_status.py",
            "earned": all(lanes[name]["status"] == "CONJECTURAL" and lanes[name]["closure_criterion"] for name in ("CCR_OPERATOR_LIMIT", "ER_EPR_KK_HOLOGRAPHY")),
            "scope": "formal conjecture status, not theorem proof",
        },
    }


def claim_boundary_audit() -> Dict[str, object]:
    """Return the combined no/yes boundary audit."""
    no_board = no_claim_board()
    yes_board = earned_yes_board()
    no_claims_clean = all(entry["claimed_as_closed"] is False for entry in no_board.values())
    yes_claims_earned = all(entry["earned"] is True for entry in yes_board.values())
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "no_claim_count": len(no_board),
        "earned_yes_count": len(yes_board),
        "no_claim_keys_match": sorted(no_board) == sorted(NO_CLAIM_KEYS),
        "earned_yes_keys_match": sorted(yes_board) == sorted(EARNED_YES_KEYS),
        "no_claims_clean": no_claims_clean,
        "earned_yes_claims_earned": yes_claims_earned,
        "hardgate_score_delta": sum(float(entry["hardgate_score_delta"]) for entry in no_board.values()),
        "verdict": "NO_FALSE_CLOSURE__YES_ONLY_WHEN_EARNED" if no_claims_clean and yes_claims_earned else "CLAIM_BOUNDARY_FAILURE",
    }


def pillar_report() -> Dict[str, object]:
    """Machine-readable Pillar 508 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "no_claims": no_claim_board(),
        "earned_yes": earned_yes_board(),
        "audit": claim_boundary_audit(),
    }
