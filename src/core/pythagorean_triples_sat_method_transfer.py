# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Machine-readable SAT proof method-transfer packet for UM and PsiCat."""

from __future__ import annotations

from typing import Any, Dict, List

INTAKE_PACKET_PATH = "proof/PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER_PACKET.md"
ARXIV_ABS_URL = "https://arxiv.org/abs/1605.00723"
ARXIV_PDF_URL = "https://arxiv.org/pdf/1605.00723"

OPEN_OBLIGATION_MAPPING: List[Dict[str, Any]] = [
    {
        "obligation_id": "ACTION_TO_EVOLUTION_EQUIVALENCE",
        "status_surface": "docs/TRUTH_LAYER.md#sprint-cq-continuation-packet",
        "priority": "primary",
        "leverage": [
            "cnf_style_obligation_encoding",
            "unsat_or_counterexample_search_discipline",
            "independent_certificate_verification_pattern",
            "compute_scale_transparency",
        ],
        "note": (
            "The strongest transfer is methodological: encode obligations with explicit assumptions, "
            "search aggressively for counterexamples first, and require independently checkable "
            "certificates before closure language."
        ),
    },
    {
        "obligation_id": "PHOTON_ORIGIN",
        "status_surface": "docs/TRUTH_LAYER.md#foundation-reassessment",
        "priority": "open_secondary",
        "leverage": [
            "counterexample_first_screening",
            "proof_vs_search_boundary_discipline",
        ],
        "note": (
            "The SAT workflow helps stress-test claim structure and hidden assumptions, but it does "
            "not import a physical derivation for the photon-origin obstruction."
        ),
    },
    {
        "obligation_id": "INDEPENDENT_CMB_NORMALIZATION",
        "status_surface": "README.md",
        "priority": "open_secondary",
        "leverage": [
            "minimal_assumption_encoding",
            "certificate_backed_reproducibility",
        ],
        "note": (
            "Transfer value is in explicit requirement encoding and verification receipts, not in "
            "direct normalization content for UM cosmology."
        ),
    },
    {
        "obligation_id": "JOINT_UV_PREDICTIVITY",
        "status_surface": "README.md",
        "priority": "open_secondary",
        "leverage": [
            "high_scale_compute_governance",
            "fail_closed_non_claim_enforcement",
        ],
        "note": (
            "The paper reinforces reproducibility and boundary discipline under large compute "
            "workloads; it does not provide UV predictive structure for UM."
        ),
    },
]


def pythagorean_triples_sat_method_transfer_packet() -> Dict[str, Any]:
    """Return the machine-readable SAT proof method-transfer packet."""
    return {
        "program": "PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER",
        "status": "EXTERNAL_METHOD_TRANSFER_PACKET_ACTIVE",
        "local_artifacts": {
            "intake_packet": INTAKE_PACKET_PATH,
        },
        "source_basis": {
            "primary_paper": {
                "title": "Solving and Verifying the boolean Pythagorean Triples problem via Cube-and-Conquer",
                "arxiv_abs_url": ARXIV_ABS_URL,
                "arxiv_pdf_url": ARXIV_PDF_URL,
            },
            "non_transfer_clause": (
                "This SAT proof paper informs method and verification discipline only; it does not close "
                "any Unitary Manifold foundational physics obligation by analogy."
            ),
        },
        "proof_architecture": {
            "core_pipeline": [
                "encode theorem claim as SAT instance",
                "run cube-and-conquer decomposition for tractable parallel search",
                "emit unsat proof certificates when no model exists",
                "independently verify certificates with a separate checker toolchain",
            ],
            "key_artifacts": [
                "SAT encoding with explicit assumptions",
                "decomposition strategy and solving telemetry",
                "proof certificate (DRAT-class)",
                "independent verification receipt",
            ],
            "epistemic_lessons": [
                "counterexample search is integral to proof workflow, not auxiliary",
                "certificate-checking separates solver trust from theorem trust",
                "compute scale must be reported as part of reproducibility metadata",
            ],
        },
        "um_open_obligation_mapping": list(OPEN_OBLIGATION_MAPPING),
        "psicat_training": {
            "lane": "lane_d_formal_proof_foundry",
            "skills": [
                "constraint_encoding_hygiene",
                "counterexample_search_first",
                "proof_certificate_verification_discipline",
                "assumption_minimization_and_traceability",
                "compute_scale_reproducibility_reporting",
            ],
            "receipt_surfaces": [
                "getMerlinTrainingExecutionQueue",
                "runMerlinTrainingCycle",
                "getMerlinLaneProgressLedgers",
                "getMerlinTrainingChallengePack",
                "getMerlinSprintReviewPacket",
            ],
            "separation_rule": (
                "Keep SAT method-transfer corpora distinct from repository-native closure evidence so "
                "proof workflow gains do not become false closure claims."
            ),
        },
        "crosswalk_questions": [
            "what_is_reusable_as_proof_workflow",
            "what_requires_new_domain_specific_encoding",
            "what_remains_non_transferable_to_um_physics",
            "what_verification_receipt_is_required_before_any_promotion",
        ],
        "adversarial_review_questions": [
            "what exactly was encoded and what was excluded",
            "how did decomposition affect completeness guarantees",
            "what verifies the emitted certificate independently",
            "where can overclaim happen between solve and interpretation",
            "what must be reproduced locally before claiming closure impact",
        ],
        "guardrails": [
            "do_not_claim_direct_physics_closure_from_sat_paper",
            "do_not_equate_solver_success_with_domain_transfer",
            "require_certificate_or_receipt_before_closure_language",
            "retain_failed_transfer_attempts_as_retraining_assets",
        ],
    }


__all__ = [
    "INTAKE_PACKET_PATH",
    "ARXIV_ABS_URL",
    "ARXIV_PDF_URL",
    "OPEN_OBLIGATION_MAPPING",
    "pythagorean_triples_sat_method_transfer_packet",
]
