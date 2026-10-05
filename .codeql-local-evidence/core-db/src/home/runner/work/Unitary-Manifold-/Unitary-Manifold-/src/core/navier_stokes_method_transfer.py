# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable Navier-Stokes method-transfer packet for UM and PsiCat."""

from __future__ import annotations

from typing import Any, Dict, List

INTAKE_PACKET_PATH = "proof/NAVIER_STOKES_METHOD_TRANSFER_PACKET.md"
CURRICULUM_PACKET_PATH = "proof/PSICAT_NAVIER_STOKES_CURRICULUM_PACKET.md"
BRAID_AUDIT_ANCHOR = "src/core/braided_winding.py"

OPEN_OBLIGATION_MAPPING: List[Dict[str, Any]] = [
    {
        "obligation_id": "ACTION_TO_EVOLUTION_EQUIVALENCE",
        "status_surface": "docs/TRUTH_LAYER.md#sprint-cq-continuation-packet",
        "priority": "primary",
        "leverage": [
            "useful_reduction_strategy",
            "useful_asymptotic_scaling_method",
            "useful_cancellation_audit_pattern",
            "useful_proof_boundary_discipline",
        ],
        "note": (
            "The Navier-Stokes construction is most relevant here as a model for narrowing one "
            "active mechanism, stating the exact blowup/control quantities, and keeping the "
            "promotion boundary separate from suggestive analogy."
        ),
    },
    {
        "obligation_id": "PHOTON_ORIGIN",
        "status_surface": "docs/TRUTH_LAYER.md#foundation-reassessment",
        "priority": "open_secondary",
        "leverage": ["useful_proof_boundary_discipline"],
        "note": (
            "The paper helps with honesty about what symmetry/ansatz buys, but it does not provide "
            "a transferable construction for the orbifold photon obstruction."
        ),
    },
    {
        "obligation_id": "INDEPENDENT_CMB_NORMALIZATION",
        "status_surface": "README.md",
        "priority": "open_secondary",
        "leverage": ["useful_cancellation_audit_pattern", "useful_proof_boundary_discipline"],
        "note": (
            "The main transfer is methodological: separate calibrated cancellation from derived "
            "normalization and keep the supporting norm bounds explicit."
        ),
    },
    {
        "obligation_id": "JOINT_UV_PREDICTIVITY",
        "status_surface": "README.md",
        "priority": "open_secondary",
        "leverage": ["no_relevant_direct_leverage", "useful_proof_boundary_discipline"],
        "note": (
            "The blowup result does not supply UV predictive structure for UM, but it does reinforce "
            "the discipline of refusing promotion beyond the exact proved perimeter."
        ),
    },
]


def navier_stokes_method_transfer_packet() -> Dict[str, Any]:
    """Return the machine-readable UM/PsiCat method-transfer packet."""
    return {
        "program": "NAVIER_STOKES_METHOD_TRANSFER",
        "status": "SUMMARY_BASED_LOCAL_INTAKE_PENDING_DIRECT_PAPER_RECHECK",
        "local_artifacts": {
            "intake_packet": INTAKE_PACKET_PATH,
            "curriculum_packet": CURRICULUM_PACKET_PATH,
        },
        "source_basis": {
            "primary_basis": "user_problem_statement_summary",
            "verification_requirement": (
                "Recheck the packet against the cited paper directly before any promotion, benchmark "
                "publication, or downstream theorem-language reuse."
            ),
            "non_transfer_clause": (
                "No Navier-Stokes result closes any Unitary Manifold foundational obligation by "
                "analogy alone."
            ),
        },
        "proof_architecture": {
            "governing_system": [
                "incompressible 3D Navier-Stokes evolution with smooth compactly supported forcing",
                "divergence-free velocity constraint",
            ],
            "similarity_coordinates": {
                "tau": "T - t",
                "X": "r / sqrt(tau)",
                "eta": "z / tau^d",
            },
            "core_mechanisms": [
                "axisymmetric concentrating background vortex ansatz",
                "self-similar spatial concentration toward a finite-time singular point",
                "designed cancellation among acceleration, pressure-gradient, viscous, and forcing contributions",
                "norm-separation between pointwise blowup and finite kinetic energy",
            ],
            "layers": {
                "constructs": [
                    "a similarity-coordinate vortex profile",
                    "a smooth forcing lane compatible with the constructed profile",
                    "a finite-time concentration mechanism",
                ],
                "proves": [
                    "finite-time blowup of a pointwise velocity quantity",
                    "finite-energy compatibility of the constructed evolution",
                    "a sharp distinction between the divergent norm and the controlled norm",
                ],
                "heuristic_or_stability_sensitive": [
                    "robustness of the construction away from the designed axisymmetric setting",
                    "what persists under perturbation of the chosen geometry/ansatz",
                    "any transfer from this PDE setting into Unitary Manifold closure claims",
                ],
            },
        },
        "um_open_obligation_mapping": list(OPEN_OBLIGATION_MAPPING),
        "action_to_evolution_sharpening": {
            "deliverable_checklist": [
                "checkable action functional",
                "explicit Euler-Lagrange equations",
                "fixed variable/time-identification map",
                "residual comparison against implemented flow",
                "promotion-boundary note with exact verified perimeter",
            ],
            "local_vs_global_prompt": (
                "Identify which UM quantity would need the role of a divergent local diagnostic and "
                "which global quantity must remain controlled for the action-to-evolution bridge."
            ),
            "scaling_audit_prompt": (
                "Check whether any implemented UM evolution equation relies on hidden self-similar, "
                "rescaled, or asymptotic assumptions that are not yet surfaced in the boundary note."
            ),
        },
        "braided_winding_audit": {
            "anchor_path": BRAID_AUDIT_ANCHOR,
            "derived_now": [
                "the repository uses the (5,7) sector and k_CS = 74 as an active computational/topological constraint",
            ],
            "observationally_supported_now": [
                "birefringence-facing matching and downstream phenomenology support continued study of the braid sector",
            ],
            "structurally_conjectural_now": [
                "the full necessity of the braid/CS identity from topology alone remains open",
            ],
            "review_instruction": (
                "Use the external paper to stress-test whether the braid story is structurally forced or "
                "partly reverse-supported by later observational matching; do not claim the paper missed it."
            ),
        },
        "psicat_training": {
            "lane": "lane_d_formal_proof_foundry",
            "skills": [
                "theorem_dependency_extraction",
                "ansatz_identification",
                "hidden_assumption_detection",
                "asymptotic_scaling_review",
                "cancellation_audit",
                "norm_separation_reasoning",
                "construction_vs_interpretation_classification",
            ],
            "receipt_surfaces": [
                "getMerlinTrainingExecutionQueue",
                "runMerlinTrainingCycle",
                "getMerlinLaneProgressLedgers",
                "getMerlinTrainingChallengePack",
                "getMerlinSprintReviewPacket",
            ],
            "separation_rule": (
                "Keep the Navier-Stokes corpus distinct from repository-native closure corpora so method "
                "transfer does not blur UM truth status."
            ),
        },
        "crosswalk_questions": [
            "what_is_structurally_analogous",
            "what_is_only_metaphorically_similar",
            "what_is_mathematically_reusable",
            "what_is_completely_non_transferable",
        ],
        "adversarial_review_questions": [
            "what is the precise blowup quantity",
            "why finite energy does not prevent pointwise blowup",
            "where smooth forcing is preserved",
            "what relies on axisymmetry",
            "what would break under perturbation",
            "what is proved versus arranged by construction",
        ],
        "guardrails": [
            "do_not_promote_new_physics_closure_from_this_packet",
            "do_not_use_analogy_to_upgrade_action_to_evolution",
            "do_not_use_analogy_to_upgrade_photon_origin",
            "do_not_use_analogy_to_upgrade_braid_necessity",
            "retain_failed_reviews_as_retraining_assets",
        ],
    }


__all__ = [
    "INTAKE_PACKET_PATH",
    "CURRICULUM_PACKET_PATH",
    "BRAID_AUDIT_ANCHOR",
    "OPEN_OBLIGATION_MAPPING",
    "navier_stokes_method_transfer_packet",
]
