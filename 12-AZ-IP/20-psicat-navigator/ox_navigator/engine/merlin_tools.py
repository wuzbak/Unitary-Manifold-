# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Safe, tiered tool registry and orchestration helpers for Merlin."""

from __future__ import annotations

import os
import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Any

from .flashcard import get_categories, load_flashcards
from .interrogator import get_tension_map_data, search_kb
from .merlin_admission import evaluate_model_admission, get_model_admission_policy
from .merlin_benchmark import (
    build_merlin_control_tower,
    build_stage_a_artifact_bundle,
    build_stage_a_replacement_readiness,
    build_promotion_packet,
    get_benchmark_corpus,
    evaluate_longitudinal_acceptance,
    evaluate_geometric_longitudinal_acceptance,
    evaluate_benchmark_response,
    evaluate_empirical_gate,
    evaluate_domain_gate_summary,
    get_domain_gate_contract,
    get_multi_stage_benchmark_plan,
    get_stage_b_benchmark_corpus,
    get_stage_c_benchmark_corpus,
    get_stage_d_benchmark_corpus,
    get_stage_e_benchmark_corpus,
    get_expert_domain_benchmark_corpus,
    get_stage_a_benchmark_corpus,
    run_stage_a_head_to_head_receipts_sync,
    run_stage_b_head_to_head_receipts_sync,
    run_stage_c_head_to_head_receipts_sync,
    run_stage_d_head_to_head_receipts_sync,
    run_stage_e_head_to_head_receipts_sync,
    run_stage_domain_head_to_head_receipts_sync,
)
from .merlin_identity import authorize_privileged_request, verify_identity_signals
from .merlin_memory import MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY, MerlinSession
from .merlin_program import (
    get_backend_expansion_policy,
    get_merlin_adversarial_growth_lane,
    get_merlin_applications_tools_lane,
    get_competitive_benchmark_plan,
    get_cross_model_exchange_protocol,
    get_current_stack_baseline,
    get_deterministic_proof_closure_contract,
    get_kawamura_closure_burden_ledger,
    get_merlin_books_articles_lane,
    get_merlin_cross_review_packet,
    get_merlin_capability_ontology,
    get_merlin_continuous_learning_protocol,
    get_merlin_ethics_contract,
    get_dual_loop_learning_contract,
    get_domain_research_missions,
    get_dual_lane_master_sprint_plan,
    get_dual_loop_sprint_command_rhythm,
    get_energy_optimization_track,
    get_expert_mastery_program,
    get_merlin_benchmark_suite,
    get_merlin_execution_graph,
    get_merlin_optimization_priorities,
    get_knowledge_transfer_cycles,
    get_knowledge_unknowns_ledger,
    get_exit_criteria,
    get_frontier_readiness_packet,
    get_full_program_blueprint,
    get_frontier_open_weight_stack,
    get_merlin_execution_board,
    get_merlin_heavy_reasoning_lane,
    get_merlin_three_lane_intensive_sprint,
    get_merlin_validation_resilience_packet,
    get_governance_integration_policy,
    get_identity_and_trust_policy,
    get_knowledge_core_sources,
    get_mentorship_completion_contract,
    get_mentorship_library_and_study_assets,
    get_mentorship_sprint_charter,
    get_proof_first_closure_charter,
    get_mythos_astra_contract,
    get_model_strategy,
    get_mirrored_training_cycle_contract,
    get_open_science_resource_registry,
    get_open_weight_acquisition_ledger,
    get_operating_rhythm,
    get_program_office,
    get_program_charter,
    get_program_doctrine,
    get_training_curation_ledger,
    get_merlin_pentad_contract,
    get_merlin_teacher_trace_policy,
    get_reliability_security_plan,
    get_regulatory_change_watch,
    get_replacement_scope,
    get_rollout_plan,
    get_sovereignty_roadmap,
    get_sentinel_enforcement_policy,
    get_specialized_model_faculty_matrix,
    get_mlflow_experiment_manifests,
    get_merlin_sovereign_model_board,
    get_merlin_sprint_review_packet,
    get_navier_stokes_method_transfer_packet,
    run_merlin_targeted_rigor_sprint,
    build_training_dataset_bundle,
    get_training_architecture,
    get_training_and_adaptation,
    get_trust_source_library,
    get_weights_and_measures,
    build_training_artifact_bundle,
    evaluate_teacher_trace_admission,
    run_sync_checks,
)
from .merlin_training_execution import (
    build_merlin_training_execution_queue,
    get_merlin_lane_progress_ledgers,
    get_merlin_training_challenge_pack,
    run_merlin_training_cycle,
)
from .merlin_inference_health import get_merlin_inference_health
from .merlin_local_inference import get_inference_providers
from .merlin_meta_learning import (
    analyze_depth,
    consolidate_memory,
    generate_falsification_oracle,
    run_self_audit,
)
from .merlin_reasoning_graph import get_reasoning_chain
from .merlin_research_cycle import run_research_cycle
from .merlin_counterexample import build_counterexample_digest
from .merlin_router import choose_runtime, get_router_policy
from .merlin_runtime import empirical_observatory_check, run_kernel_p_lean_proof_probe
from .merlin_rag import (
    INTERROGATOR_ENTRIES,
    PILLAR_KNOWLEDGE,
    build_rag_context,
    build_status_response,
    lookup_kb,
)
from .merlin_energy_ledger import build_merlin_energy_ledger
from .merlin_sync_contract import REQUIRED_TOOLKIT_FUNCTIONS
from .merlin_workspace import get_workspace_policy, get_workspace_state

_LIMIT_SYNC_ARGS_SCHEMA = {
    "type": "object",
    "properties": {
        "limit": {"type": "integer"},
        "sync_checks_ok": {"type": "boolean"},
    },
    "additionalProperties": False,
}

MERLIN_SESSION_SCHEMA = {
    "title": "MerlinSession",
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "context_type": {
            "type": "string",
            "enum": ["chat", "interrogation", "flashcards", "geo-interpretation", "falsification"],
        },
        "messages_json": {"type": "array"},
        "deck_json": {"type": ["array", "null"]},
    },
    "required": ["title", "context_type", "messages_json"],
}


def _matches_schema_type(value: Any, schema_type: Any) -> bool:
    if isinstance(schema_type, list):
        return any(_matches_schema_type(value, item) for item in schema_type)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "number":
        return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)
    if schema_type == "boolean":
        return isinstance(value, bool)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "null":
        return value is None
    return True


def _validate_args_schema(schema: dict[str, Any] | None, args: dict[str, Any]) -> str | None:
    if not schema:
        return None
    reserved_keys = {"human_gate_approved"}
    required = list(schema.get("required") or [])
    for key in required:
        if key not in args:
            return f"Missing required argument: {key}"
    props = dict(schema.get("properties") or {})
    for key, value in args.items():
        if key in reserved_keys:
            continue
        if key in props:
            expected = props[key].get("type")
            if expected and not _matches_schema_type(value, expected):
                return f"Invalid argument type for '{key}': expected {expected}"
        elif schema.get("additionalProperties") is False:
            return f"Unexpected argument: {key}"
    return None


def _tool_manifest() -> dict[str, Any]:
    functions = [
            {"name": "fetchRepoContext", "summary": "Return canonical live repo status", "domain": "functions"},
            {"name": "listPillars", "summary": "List representative pillar records", "domain": "functions"},
            {"name": "getPillar", "summary": "Return one pillar by id", "domain": "functions"},
            {"name": "searchKnowledgeBase", "summary": "Search canonical Merlin KB", "domain": "functions"},
            {"name": "searchInterrogator", "summary": "Search bundled interrogator KB", "domain": "functions"},
            {"name": "getTensionMap", "summary": "Return interrogator sigma/confidence points", "domain": "functions"},
            {"name": "loadFlashcards", "summary": "Return Merlin flashcard deck", "domain": "functions"},
            {"name": "getFlashcardCategories", "summary": "Return flashcard categories", "domain": "functions"},
            {"name": "getMerlinProgramCharter", "summary": "Return Merlin replacement program charter", "domain": "functions"},
            {"name": "getMerlinProgramDoctrine", "summary": "Return hard doctrine and success definition", "domain": "functions"},
            {"name": "getMerlinPentadContract", "summary": "Return hard I/O contract for Sage/Prover/Router/Auditor/Gate kernels", "domain": "functions"},
            {"name": "getMerlinProgramOffice", "summary": "Return Merlin Program Office command structure and gate authority", "domain": "functions"},
            {"name": "getMerlinMentorshipSprintCharter", "summary": "Return Merlin mentorship sprint charter and non-negotiables", "domain": "functions"},
            {"name": "getMerlinFacultyMatrix", "summary": "Return specialized model faculty roles, rubrics, and artifact requirements", "domain": "functions"},
            {"name": "getMerlinKnowledgeTransferCycles", "summary": "Return structured specialist knowledge-transfer cycle contract", "domain": "functions"},
            {"name": "getMerlinLibraryAndStudy", "summary": "Return governed Merlin library plus study assets contract", "domain": "functions"},
            {"name": "getMerlinExchangeProtocol", "summary": "Return cross-model review/reconciliation/risk protocol", "domain": "functions"},
            {"name": "getMerlinMentorshipClosureContract", "summary": "Return mentorship-to-runtime closure contract", "domain": "functions"},
            {"name": "getMerlinProofFirstClosureCharter", "summary": "Return single-target proof-first sprint charter for the active Kawamura residual", "domain": "functions"},
            {"name": "getMerlinKawamuraBurdenLedger", "summary": "Return machine-readable burden ledger for the Kawamura independence residual", "domain": "functions"},
            {"name": "getMerlinCrossReviewPacket", "summary": "Return Merlin/Copilot cross-review packet for proof-first closure work", "domain": "functions"},
            {"name": "getMerlinDualLoopContract", "summary": "Return kitty-loop + HILS-loop learning contract and transfer boundaries", "domain": "functions"},
            {"name": "getMerlinMirroredTrainingCycle", "summary": "Return mirrored practice/production cycle and delta review contract", "domain": "functions"},
            {"name": "getMerlinDeterministicClosureContract", "summary": "Return deterministic proof closure packet and verdict constraints", "domain": "functions"},
            {"name": "getMerlinDualLoopSprintRhythm", "summary": "Return kickoff/mid/closeout command rhythm for dual-loop sprints", "domain": "functions"},
            {"name": "getMerlinSovereigntyRoadmap", "summary": "Return implementation checklist mapped to blueprint", "domain": "functions"},
            {"name": "getMerlinReplacementScope", "summary": "Return in-scope and fallback policy boundaries", "domain": "functions"},
            {"name": "getMerlinStackBaseline", "summary": "Return baseline capabilities and replacement gaps", "domain": "functions"},
            {"name": "getMerlinWeightsAndMeasures", "summary": "Return scorecard axes and benchmark battery", "domain": "functions"},
            {"name": "getMerlinKnowledgeCore", "summary": "Return typed provenance source registry", "domain": "functions"},
            {"name": "getMerlinTrustSourceLibrary", "summary": "Return authoritative trust-source library for business/tax/legal/HR expert tracks", "domain": "functions"},
            {"name": "getMerlinKnowledgeUnknownsLedger", "summary": "Return explicit unknowns and open-research ledger for expert tracks", "domain": "functions"},
            {"name": "getMerlinRegulatoryChangeWatch", "summary": "Return cadence and protocol for continuous legal/regulatory change detection", "domain": "functions"},
            {"name": "getMerlinDomainResearchMissions", "summary": "Return active research missions to close domain unknowns", "domain": "functions"},
            {"name": "getMerlinExpertMasteryProgram", "summary": "Return curriculum, drills, and assessment gates for expert mastery", "domain": "functions"},
            {"name": "runMerlinSyncChecks", "summary": "Run canonical source sync checks", "domain": "functions"},
            {"name": "getMerlinModelStrategy", "summary": "Return staged small/medium/heavy strategy", "domain": "functions"},
            {"name": "getMerlinRouterPolicy", "summary": "Return sovereign router and 12/37 cadence policy", "domain": "functions"},
            {"name": "previewMerlinRoute", "summary": "Preview lane/provider decision for a query", "domain": "functions"},
            {"name": "getMerlinModelAdmissionPolicy", "summary": "Return open-science model admission policy", "domain": "functions"},
            {"name": "evaluateMerlinModelAdmission", "summary": "Evaluate one model against admission policy", "domain": "functions"},
            {"name": "getMerlinTrainingPlan", "summary": "Return adaptation and training tracks", "domain": "functions"},
            {"name": "getMerlinEthicsContract", "summary": "Return ethics and legality contract for capability distillation", "domain": "functions"},
            {"name": "getMerlinCapabilityOntology", "summary": "Return normalized capability ontology and provider-family transfer map", "domain": "functions"},
            {"name": "getMerlinTeacherTracePolicy", "summary": "Return governed teacher-trace distillation and admission policy", "domain": "functions"},
            {"name": "evaluateMerlinTeacherTrace", "summary": "Evaluate one teacher trace sample for license/provenance admission", "domain": "functions"},
            {"name": "getMerlinTrainingArchitecture", "summary": "Return full Merlin training architecture and seed corpus manifest", "domain": "functions"},
            {"name": "getMerlinNavierStokesMethodTransferPacket", "summary": "Return the governed Navier-Stokes method-transfer packet for UM/PsiCat", "domain": "functions"},
            {"name": "getMerlinOpenScienceRegistry", "summary": "Return governed external open-science ingestion registry", "domain": "functions"},
            {"name": "getMerlinOpenWeightAcquisitionLedger", "summary": "Return scored open-weight acquisition channels, candidate roster, and roster freeze policy", "domain": "functions"},
            {"name": "getMerlinFrontierStack", "summary": "Return open-weight model and kernel stack for frontier-local Merlin training", "domain": "functions"},
            {"name": "getMerlinDualLaneMasterSprint", "summary": "Return governed dual-lane physics+Merlin sprint contract", "domain": "functions"},
            {"name": "getMerlinThreeLaneIntensiveSprint", "summary": "Return rigorous three-lane Merlin sprint across apps, books, and adversarial self-correction", "domain": "functions"},
            {"name": "getMerlinApplicationsToolsLane", "summary": "Return Lane A applications/tools mastery inventory and gates", "domain": "functions"},
            {"name": "getMerlinBooksArticlesLane", "summary": "Return Lane B books/articles mastery inventory and study gates", "domain": "functions"},
            {"name": "getMerlinAdversarialGrowthLane", "summary": "Return Lane C contradiction, falsification, and self-correction drills", "domain": "functions"},
            {"name": "getMerlinContinuousLearningProtocol", "summary": "Return governed between-session learning cadence and queue", "domain": "functions"},
            {"name": "getMerlinTrainingExecutionQueue", "summary": "Return active retained-training queue state across all three lanes", "domain": "functions"},
            {"name": "getMerlinLaneProgressLedgers", "summary": "Return automated lane-by-lane progress ledgers and retained receipt summaries", "domain": "functions"},
            {"name": "runMerlinTrainingCycle", "summary": "Execute queued three-lane training work and retain auditable receipts in session memory", "domain": "functions"},
            {"name": "runMerlinTargetedRigorSprint", "summary": "Execute bounded full-rigor sprint packet: retained training cycle + Stage A-E receipts + fail-closed blockers", "domain": "functions"},
            {"name": "getMerlinTrainingChallengePack", "summary": "Return deterministic challenge drills prioritized by stale or review-required training work", "domain": "functions"},
            {"name": "getMerlinCompetitiveBenchmarkPlan", "summary": "Return competitive benchmark families and promotion metrics", "domain": "functions"},
            {"name": "getMerlinTrainingArtifacts", "summary": "Return exportable Merlin training artifact bundle", "domain": "functions"},
            {"name": "getMerlinEnergyPlan", "summary": "Return energy-first optimization controls", "domain": "functions"},
            {"name": "getMerlinBackendPolicy", "summary": "Return backend expansion policy controls", "domain": "functions"},
            {"name": "getMerlinWorkspacePolicy", "summary": "Return governed back-room workspace policy", "domain": "functions"},
            {"name": "getMerlinWorkspaceState", "summary": "Return back-room workspace state summary", "domain": "functions"},
            {"name": "getMerlinGovernancePolicy", "summary": "Return Pentad governance integration policy", "domain": "functions"},
            {"name": "getMerlinReliabilityPlan", "summary": "Return reliability and abuse-resistance controls", "domain": "functions"},
            {"name": "getMerlinRolloutPlan", "summary": "Return staged rollout and rollback policy", "domain": "functions"},
            {"name": "getMerlinOperatingRhythm", "summary": "Return weekly/monthly/quarterly cadence", "domain": "functions"},
            {"name": "getMerlinExitCriteria", "summary": "Return hard replacement exit criteria", "domain": "functions"},
            {"name": "getMerlinProgramBlueprint", "summary": "Return full integrated Merlin replacement blueprint", "domain": "functions"},
            {"name": "getMerlinIdentityPolicy", "summary": "Return canonical identity and trust policy", "domain": "functions"},
            {"name": "verifyMerlinIdentity", "summary": "Verify identity signals for privileged actions", "domain": "functions"},
            {"name": "authorizeMerlinPrivilege", "summary": "Authorize privileged Merlin modification requests", "domain": "functions"},
            {"name": "getMerlinSentinelPolicy", "summary": "Return Sentinel safety enforcement policy", "domain": "functions"},
            {"name": "getMerlinMythosAstraContract", "summary": "Return Merlin runtime contract for Mythos/Astra parity", "domain": "functions"},
            {"name": "getMerlinOptimizationPriorities", "summary": "Return ordered top optimization priorities", "domain": "functions"},
            {"name": "getMerlinExecutionGraph", "summary": "Return max-rigor execution graph", "domain": "functions"},
            {"name": "getMerlinBenchmarkSuite", "summary": "Return benchmark harness definition", "domain": "functions"},
            {"name": "getMerlinBenchmarkCorpus", "summary": "Return Stage A benchmark prompt corpus", "domain": "functions"},
            {"name": "getMerlinStageBCorpus", "summary": "Return Stage B benchmark corpus", "domain": "functions"},
            {"name": "getMerlinStageCCorpus", "summary": "Return Stage C benchmark corpus", "domain": "functions"},
            {"name": "getMerlinStageDCorpus", "summary": "Return Stage D benchmark corpus", "domain": "functions"},
            {"name": "getMerlinStageECorpus", "summary": "Return Stage E benchmark corpus", "domain": "functions"},
            {"name": "getMerlinExpertDomainCorpus", "summary": "Return expert-domain benchmark corpus expansion from mission tracks", "domain": "functions"},
            {"name": "getMerlinBenchmarkCorpora", "summary": "Return all Merlin benchmark corpora or a selected stage", "domain": "functions"},
            {"name": "getMerlinMultiStageBenchmarks", "summary": "Return multi-stage benchmark batteries and acceptance cadence", "domain": "functions"},
            {"name": "evaluateMerlinBenchmarkResponse", "summary": "Score one response against a Merlin benchmark", "domain": "functions"},
            {"name": "runMerlinStageAReceipts", "summary": "Run self-hosted Stage A receipt set", "domain": "functions"},
            {"name": "runMerlinStageBReceipts", "summary": "Run self-hosted Stage B receipt set", "domain": "functions"},
            {"name": "runMerlinStageCReceipts", "summary": "Run self-hosted Stage C receipt set", "domain": "functions"},
            {"name": "runMerlinStageDReceipts", "summary": "Run self-hosted Stage D receipt set", "domain": "functions"},
            {"name": "runMerlinStageEReceipts", "summary": "Run self-hosted Stage E receipt set", "domain": "functions"},
            {"name": "runMerlinDomainReceipts", "summary": "Run self-hosted expert-domain mastery receipt set", "domain": "functions"},
            {"name": "evaluateMerlinEmpiricalGate", "summary": "Evaluate sustained Merlin-vs-incumbent replacement gate", "domain": "functions"},
            {"name": "getMerlinDomainGateContract", "summary": "Return per-domain pass/fail threshold contract for expert mastery gates", "domain": "functions"},
            {"name": "evaluateMerlinDomainGates", "summary": "Evaluate domain-by-domain mastery gates from benchmark runs", "domain": "functions"},
            {"name": "evaluateMerlinLongitudinalAcceptance", "summary": "Evaluate sustained clean-window promotion cadence over gate history", "domain": "functions"},
            {"name": "evaluateMerlinGeometricLongitudinalAcceptance", "summary": "Evaluate sustained geometric-memory acceptance cadence over gate history", "domain": "functions"},
            {"name": "getMerlinPromotionPacket", "summary": "Return explicit replacement promotion packet", "domain": "functions"},
            {"name": "getMerlinReplacementReadiness", "summary": "Return concrete self-hosted replacement readiness packet", "domain": "functions"},
            {"name": "getMerlinStageAArtifacts", "summary": "Return exportable Stage A artifact bundle", "domain": "functions"},
            {"name": "getMerlinFrontierReadiness", "summary": "Return merged readiness packet with fail-closed promotion blockers", "domain": "functions"},
            {"name": "getMerlinControlTower", "summary": "Return control tower readiness, drift alerts, trendlines, and deployment eligibility", "domain": "functions"},
            {"name": "getMerlinSprintReviewPacket", "summary": "Return the canonical Stage A-E review packet with receipts, blockers, and failure reasons", "domain": "functions"},
            {"name": "getMerlinHeavyReasoningLane", "summary": "Return heavy-lane provider comparison, benchmark pack, failure taxonomy, and tuning agenda", "domain": "functions"},
            {"name": "getMerlinSovereignModelBoard", "summary": "Return runtime-tier shortlists, scoring board, and adaptation-vs-abandonment policy", "domain": "functions"},
            {"name": "getMerlinExecutionBoard", "summary": "Return the follow-on execution board with immediate tasks, blockers, validation resilience, and blunt board", "domain": "functions"},
            {"name": "getMerlinValidationResiliencePacket", "summary": "Return repo-size mitigation actions and CodeQL scope-reduction strategy for validation resilience", "domain": "functions"},
            {"name": "getMerlinTrainingDataset", "summary": "Return structured Merlin JSONL-ready training and benchmark dataset bundle", "domain": "functions"},
            {"name": "getMerlinTrainingCuration", "summary": "Return low-token Merlin curation ledger and budget metrics", "domain": "functions"},
            {"name": "getMerlinMLflowManifests", "summary": "Return MLflow-ready experiment manifests for Merlin training and gates", "domain": "functions"},
            {"name": "getMerlinMemoryState", "summary": "Return Merlin multi-tier memory state", "domain": "functions"},
            {"name": "getMerlinMemoryGeometry", "summary": "Return geometry-constrained memory landmark map", "domain": "functions"},
            {"name": "runMerlinMemoryAudit", "summary": "Audit which durable memories match a query", "domain": "functions"},
            {"name": "getMerlinTelemetrySummary", "summary": "Return measurable run summary for recent Merlin turns", "domain": "functions"},
            {"name": "getMerlinInferenceProviders", "summary": "Return sovereign local inference provider registry", "domain": "functions"},
            {"name": "getMerlinInferenceHealth", "summary": "Return inference provider availability and health", "domain": "functions"},
            {"name": "getMerlinReasoningChain", "summary": "Return a multi-hop pillar reasoning chain with Lean4 hits", "domain": "functions"},
            {"name": "runMerlinResearchCycle", "summary": "Run a bounded repository-grounded Merlin research cycle", "domain": "functions"},
            {"name": "getMerlinCounterexampleDigest", "summary": "Return typed contradiction and counterexample digest artifacts", "domain": "functions"},
            {"name": "getMerlinEnergyLedger", "summary": "Return Merlin-vs-incumbent energy ledger entries", "domain": "functions"},
            {"name": "merlinConsolidateMemory", "summary": "Synthesize memory tiers and detect governed training gaps", "domain": "functions"},
            {"name": "merlinSelfAudit", "summary": "Return calibration and contradiction audit for recent telemetry", "domain": "functions"},
            {"name": "generateFalsificationOracle", "summary": "Generate domain kill-conditions and persist trusted oracle notes", "domain": "functions"},
            {"name": "merlinAnalyzeDepth", "summary": "Recommend deterministic reasoning depth from telemetry trends", "domain": "functions"},
            {"name": "empiricalObservatoryCheck", "summary": "Evaluate DESI/JUNO/LiteBIRD tripwires and rupture events", "domain": "functions"},
            {"name": "kernelPProofProbe", "summary": "Run gated KERNEL_P Lean4 proof probe with fallback", "domain": "functions"},
        ]
    policy_overrides = {
        "getPillar": {
            "args_schema": {
                "type": "object",
                "properties": {"pillar_id": {"type": "integer"}},
                "required": ["pillar_id"],
                "additionalProperties": True,
            },
        },
        "searchKnowledgeBase": {
            "args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
        "searchInterrogator": {
            "args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
        "previewMerlinRoute": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "confidence": {"type": "number"},
                },
                "required": ["query"],
            },
        },
        "evaluateMerlinModelAdmission": {
            "args_schema": {"type": "object", "properties": {"model": {"type": "object"}}, "required": ["model"]},
            "risk_level": "medium",
        },
        "evaluateMerlinTeacherTrace": {
            "args_schema": {"type": "object", "properties": {"trace": {"type": "object"}}, "required": ["trace"]},
            "risk_level": "medium",
        },
        "getMerlinTrainingArchitecture": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinNavierStokesMethodTransferPacket": {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "getMerlinTrainingArtifacts": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinTrainingDataset": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinTrainingCuration": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinMLflowManifests": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinFrontierReadiness": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinSprintReviewPacket": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinHeavyReasoningLane": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinSovereignModelBoard": {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "getMerlinExecutionBoard": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinValidationResiliencePacket": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinOpenWeightAcquisitionLedger": {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "getMerlinDualLaneMasterSprint": {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "getMerlinThreeLaneIntensiveSprint": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinApplicationsToolsLane": {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "getMerlinBooksArticlesLane": {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "getMerlinAdversarialGrowthLane": {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "getMerlinContinuousLearningProtocol": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinTrainingExecutionQueue": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinLaneProgressLedgers": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "runMerlinTrainingCycle": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "runMerlinTargetedRigorSprint": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                    "training_limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
        },
        "getMerlinTrainingChallengePack": {"args_schema": _LIMIT_SYNC_ARGS_SCHEMA},
        "getMerlinMemoryGeometry": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            }
        },
        "getMerlinBenchmarkCorpora": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "stage": {
                        "type": "string",
                        "enum": [
                            "all",
                            "stage_a",
                            "stage_a_parity_capture",
                            "a",
                            "stage_b",
                            "stage_b_sovereign_takeover",
                            "b",
                            "stage_c",
                            "stage_c_capability_expansion",
                            "c",
                            "stage_d",
                            "stage_d_replacement_gates",
                            "d",
                            "stage_e",
                            "stage_e_external_decommission",
                            "e",
                            "stage_domain",
                            "stage_expert_domain_mastery",
                            "domain",
                            "expert",
                            "expert_domain",
                        ],
                    }
                },
                "additionalProperties": False,
            },
        },
        "verifyMerlinIdentity": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "user_context": {"type": "string"},
                    "page_context": {"type": "string"},
                },
            },
            "risk_level": "medium",
        },
        "authorizeMerlinPrivilege": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "user_context": {"type": "string"},
                    "page_context": {"type": "string"},
                },
            },
            "risk_level": "high",
            "requires_human_gate": True,
        },
        "evaluateMerlinBenchmarkResponse": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "benchmark_id": {"type": "string"},
                    "response": {"type": "object"},
                    "stage": {
                        "type": "string",
                        "enum": [
                            "stage_a",
                            "stage_a_parity_capture",
                            "a",
                            "stage_b",
                            "stage_b_sovereign_takeover",
                            "b",
                            "stage_c",
                            "stage_c_capability_expansion",
                            "c",
                            "stage_d",
                            "stage_d_replacement_gates",
                            "d",
                            "stage_e",
                            "stage_e_external_decommission",
                            "e",
                        ],
                    },
                },
                "required": ["benchmark_id", "response"],
            },
        },
        "evaluateMerlinLongitudinalAcceptance": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "gate_history": {"type": "array"},
                    "window_size": {"type": "integer"},
                    "min_clean_windows": {"type": "integer"},
                },
                "required": ["gate_history"],
            },
            "risk_level": "medium",
        },
        "evaluateMerlinGeometricLongitudinalAcceptance": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "gate_history": {"type": "array"},
                    "window_size": {"type": "integer"},
                    "min_clean_windows": {"type": "integer"},
                },
                "required": ["gate_history"],
            },
            "risk_level": "medium",
        },
        "runMerlinStageAReceipts": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "runMerlinStageBReceipts": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "runMerlinStageCReceipts": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "runMerlinStageDReceipts": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "runMerlinStageEReceipts": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "runMerlinDomainReceipts": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "evaluateMerlinEmpiricalGate": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "head_to_head_runs": {"type": "array"},
                    "min_runs": {"type": "integer"},
                    "max_quality_regressions": {"type": "integer"},
                },
                "required": ["head_to_head_runs"],
            },
            "risk_level": "medium",
        },
        "evaluateMerlinDomainGates": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "runs": {"type": "array"},
                    "required_domains": {"type": "array"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "getMerlinPromotionPacket": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "head_to_head_runs": {"type": "array"},
                    "sync_checks_ok": {"type": "boolean"},
                },
                "additionalProperties": True,
            },
            "risk_level": "medium",
        },
        "getMerlinReplacementReadiness": {
            "args_schema": _LIMIT_SYNC_ARGS_SCHEMA,
            "risk_level": "medium",
        },
        "getMerlinStageAArtifacts": {
            "args_schema": _LIMIT_SYNC_ARGS_SCHEMA,
            "risk_level": "medium",
        },
        "getMerlinControlTower": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer"},
                    "gate_history": {"type": "array"},
                },
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "runMerlinSyncChecks": {
            "capability_class": "verification",
            "risk_level": "high",
            "args_schema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        "runMerlinMemoryAudit": {
            "args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            "capability_class": "state_read",
        },
        "getMerlinMemoryState": {"capability_class": "state_read"},
        "getMerlinMemoryGeometry": {
            "capability_class": "state_read",
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "additionalProperties": False,
            },
        },
        "getMerlinTelemetrySummary": {"capability_class": "state_read"},
        "getMerlinInferenceProviders": {"capability_class": "state_read"},
        "getMerlinInferenceHealth": {
            "capability_class": "state_read",
            "args_schema": {
                "type": "object",
                "properties": {"provider": {"type": "string"}},
                "additionalProperties": False,
            },
        },
        "getMerlinReasoningChain": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_hops": {"type": "integer", "minimum": 1},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
        "runMerlinResearchCycle": {
            "args_schema": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "budget": {"type": "integer", "minimum": 1},
                },
                "required": ["question"],
                "additionalProperties": False,
            },
            "risk_level": "medium",
        },
        "getMerlinCounterexampleDigest": {
            "capability_class": "state_read",
            "args_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1}},
                "additionalProperties": False,
            },
        },
        "getMerlinEnergyLedger": {
            "capability_class": "state_read",
            "args_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1}},
                "additionalProperties": False,
            },
        },
        "merlinConsolidateMemory": {
            "capability_class": "state_read",
            "args_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1}},
                "additionalProperties": False,
            },
        },
        "merlinSelfAudit": {
            "capability_class": "state_read",
            "args_schema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        "generateFalsificationOracle": {
            "capability_class": "verification",
            "risk_level": "medium",
            "args_schema": {
                "type": "object",
                "properties": {"domain": {"type": "string"}},
                "required": ["domain"],
                "additionalProperties": False,
            },
        },
        "merlinAnalyzeDepth": {
            "capability_class": "state_read",
            "args_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1}},
                "additionalProperties": False,
            },
        },
        "empiricalObservatoryCheck": {
            "capability_class": "verification",
            "risk_level": "high",
            "args_schema": {
                "type": "object",
                "properties": {"observed": {"type": "object"}},
                "additionalProperties": False,
            },
        },
        "kernelPProofProbe": {
            "capability_class": "verification",
            "risk_level": "medium",
            "args_schema": {
                "type": "object",
                "properties": {
                    "conjecture": {"type": "string"},
                    "context": {"type": "string"},
                    "enable_repl": {"type": "boolean"},
                },
                "required": ["conjecture"],
                "additionalProperties": False,
            },
        },
    }
    enriched_functions = []
    for item in functions:
        enriched = {
            "capability_class": "read",
            "risk_level": "low",
            "requires_human_gate": False,
            "sync_required": item["name"] in REQUIRED_TOOLKIT_FUNCTIONS,
            "args_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            **item,
            **policy_overrides.get(item["name"], {}),
        }
        enriched_functions.append(enriched)
    return {
        "functions": enriched_functions,
        "integrations": [],
        "entities": [
            {
                "name": "MerlinSession",
                "summary": "Audited Merlin session with durable memory, contradictions, and telemetry.",
                "domain": "entities",
                "operations": ["schema", "state", "audit"],
            },
        ],
        "connectors": [
            {
                "name": "github",
                "summary": "Standalone compatibility summary only; no token exposure.",
                "domain": "connectors",
                "risk_level": "low",
            },
        ],
        "secrets": [
            {"name": "OPENROUTER_API_KEY", "domain": "secrets"},
            {"name": "BRAVE_API_KEY", "domain": "secrets"},
            {"name": "HF_API_TOKEN", "domain": "secrets"},
        ],
    }


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        if value is None:
            return max(1, int(default))
        return max(1, int(value))
    except (TypeError, ValueError):
        return max(1, int(default))


def _validate_args_schema(args: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, str]:
    properties = dict(schema.get("properties") or {})
    required = list(schema.get("required") or [])
    allow_extra = bool(schema.get("additionalProperties", False))
    reserved_keys = {"human_gate_approved"}
    filtered_args = {k: v for k, v in args.items() if k not in reserved_keys}
    declared_keys = set(properties.keys())
    for key in required:
        if key not in filtered_args:
            return False, f"Missing required argument: {key}"
    if not allow_extra:
        extra = sorted(set(filtered_args.keys()) - declared_keys)
        if extra:
            return False, f"Unknown argument(s): {', '.join(extra)}"
    type_map = {
        "string": str,
        "boolean": bool,
        "object": dict,
        "array": list,
    }

    def _matches(expected_type: str, value: Any) -> bool:
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        py_type = type_map.get(expected_type)
        return isinstance(value, py_type) if py_type else True
    for key, spec in properties.items():
        if key not in filtered_args:
            continue
        expected = spec.get("type")
        if isinstance(expected, list):
            valid = any(_matches(str(t), filtered_args[key]) for t in expected)
        else:
            valid = _matches(str(expected), filtered_args[key]) if expected else True
        if not valid:
            return False, f"Invalid type for '{key}', expected {expected}"
        minimum = spec.get("minimum")
        if minimum is not None and isinstance(filtered_args[key], (int, float)) and not isinstance(filtered_args[key], bool):
            if filtered_args[key] < minimum:
                return False, f"Invalid value for '{key}', must be >= {minimum}"
        if "enum" in spec and filtered_args[key] not in list(spec.get("enum") or []):
            return False, f"Invalid value for '{key}', expected one of {list(spec.get('enum') or [])}"
    return True, ""


def _build_replay_artifact(*, tool: str, args: dict[str, Any], result: Any, ok: bool) -> dict[str, Any]:
    secret_markers = ("token", "secret", "key", "password", "credential")
    safe_args = {}
    for key, value in dict(args or {}).items():
        lower = str(key).lower()
        safe_args[key] = "***REDACTED***" if any(marker in lower for marker in secret_markers) else value
    replay = {
        "generated_at": _utcnow(),
        "tool": tool,
        "args": safe_args,
        "ok": ok,
        "result_excerpt": json.dumps(result, ensure_ascii=False)[:800] if result is not None else "",
    }
    replay_payload = json.dumps(replay, ensure_ascii=False, sort_keys=True)
    replay["digest_sha256"] = hashlib.sha256(replay_payload.encode("utf-8")).hexdigest()
    return replay


def fetch_repo_context() -> dict[str, Any]:
    return {"data": build_status_response()}


def list_pillars() -> dict[str, Any]:
    return {"data": {"pillars": PILLAR_KNOWLEDGE, "total": len(PILLAR_KNOWLEDGE)}}


def get_pillar(pillar_id: int) -> dict[str, Any]:
    for pillar in PILLAR_KNOWLEDGE:
        if int(pillar["id"]) == int(pillar_id):
            return {"data": pillar}
    return {"data": None, "error": f"Pillar {pillar_id} not found"}


def search_knowledge_base(query: str) -> dict[str, Any]:
    return {"data": {"match": lookup_kb(query), "context": build_rag_context(query)}}


def search_interrogator(query: str) -> dict[str, Any]:
    return {"data": {"results": search_kb(INTERROGATOR_ENTRIES, query)[:5]}}


def get_tension_map() -> dict[str, Any]:
    return {"data": {"points": get_tension_map_data(INTERROGATOR_ENTRIES)}}


def load_flashcards_tool() -> dict[str, Any]:
    cards = load_flashcards()
    return {"data": {"count": len(cards), "cards": cards}}


def get_flashcard_categories() -> dict[str, Any]:
    return {"data": {"categories": get_categories(load_flashcards())}}


_FUNCTIONS = {
    "fetchRepoContext": fetch_repo_context,
    "listPillars": list_pillars,
    "getPillar": lambda **args: get_pillar(int(args.get("pillar_id", args.get("id", 0)))),
    "searchKnowledgeBase": lambda **args: search_knowledge_base(str(args.get("query", ""))),
    "searchInterrogator": lambda **args: search_interrogator(str(args.get("query", ""))),
    "getTensionMap": lambda **args: get_tension_map(),
    "loadFlashcards": lambda **args: load_flashcards_tool(),
    "getFlashcardCategories": lambda **args: get_flashcard_categories(),
    "getMerlinProgramCharter": lambda **args: {"data": get_program_charter()},
    "getMerlinProgramDoctrine": lambda **args: {"data": get_program_doctrine()},
    "getMerlinPentadContract": lambda **args: {"data": get_merlin_pentad_contract()},
    "getMerlinProgramOffice": lambda **args: {"data": get_program_office()},
    "getMerlinMentorshipSprintCharter": lambda **args: {"data": get_mentorship_sprint_charter()},
    "getMerlinFacultyMatrix": lambda **args: {"data": get_specialized_model_faculty_matrix()},
    "getMerlinKnowledgeTransferCycles": lambda **args: {"data": get_knowledge_transfer_cycles()},
    "getMerlinLibraryAndStudy": lambda **args: {"data": get_mentorship_library_and_study_assets()},
    "getMerlinExchangeProtocol": lambda **args: {"data": get_cross_model_exchange_protocol()},
    "getMerlinMentorshipClosureContract": lambda **args: {"data": get_mentorship_completion_contract()},
    "getMerlinProofFirstClosureCharter": lambda **args: {"data": get_proof_first_closure_charter()},
    "getMerlinKawamuraBurdenLedger": lambda **args: {"data": get_kawamura_closure_burden_ledger()},
    "getMerlinCrossReviewPacket": lambda **args: {"data": get_merlin_cross_review_packet()},
    "getMerlinDualLoopContract": lambda **args: {"data": get_dual_loop_learning_contract()},
    "getMerlinMirroredTrainingCycle": lambda **args: {"data": get_mirrored_training_cycle_contract()},
    "getMerlinDeterministicClosureContract": lambda **args: {"data": get_deterministic_proof_closure_contract()},
    "getMerlinDualLoopSprintRhythm": lambda **args: {"data": get_dual_loop_sprint_command_rhythm()},
    "getMerlinSovereigntyRoadmap": lambda **args: {"data": get_sovereignty_roadmap()},
    "getMerlinReplacementScope": lambda **args: {"data": get_replacement_scope()},
    "getMerlinStackBaseline": lambda **args: {"data": get_current_stack_baseline()},
    "getMerlinWeightsAndMeasures": lambda **args: {"data": get_weights_and_measures()},
    "getMerlinKnowledgeCore": lambda **args: {"data": get_knowledge_core_sources()},
    "getMerlinTrustSourceLibrary": lambda **args: {"data": get_trust_source_library()},
    "getMerlinKnowledgeUnknownsLedger": lambda **args: {"data": get_knowledge_unknowns_ledger()},
    "getMerlinRegulatoryChangeWatch": lambda **args: {"data": get_regulatory_change_watch()},
    "getMerlinDomainResearchMissions": lambda **args: {"data": get_domain_research_missions()},
    "getMerlinExpertMasteryProgram": lambda **args: {"data": get_expert_mastery_program()},
    "runMerlinSyncChecks": lambda **args: {"data": run_sync_checks()},
    "getMerlinModelStrategy": lambda **args: {"data": get_model_strategy()},
    "getMerlinRouterPolicy": lambda **args: {"data": get_router_policy()},
    "previewMerlinRoute": lambda **args: {"data": choose_runtime(str(args.get("query", "")), confidence=float(args.get("confidence", 0.7)))},
    "getMerlinModelAdmissionPolicy": lambda **args: {"data": get_model_admission_policy()},
    "evaluateMerlinModelAdmission": lambda **args: {"data": evaluate_model_admission(dict(args.get("model") or {}))},
    "getMerlinEthicsContract": lambda **args: {"data": get_merlin_ethics_contract()},
    "getMerlinCapabilityOntology": lambda **args: {"data": get_merlin_capability_ontology()},
    "getMerlinTeacherTracePolicy": lambda **args: {"data": get_merlin_teacher_trace_policy()},
    "evaluateMerlinTeacherTrace": lambda **args: {"data": evaluate_teacher_trace_admission(dict(args.get("trace") or {}))},
    "getMerlinTrainingPlan": lambda **args: {"data": get_training_and_adaptation()},
    "getMerlinTrainingArchitecture": lambda **args: {"data": get_training_architecture(limit=args.get("limit"))},
    "getMerlinNavierStokesMethodTransferPacket": lambda **args: {"data": get_navier_stokes_method_transfer_packet()},
    "getMerlinOpenScienceRegistry": lambda **args: {"data": get_open_science_resource_registry()},
    "getMerlinOpenWeightAcquisitionLedger": lambda **args: {"data": get_open_weight_acquisition_ledger()},
    "getMerlinFrontierStack": lambda **args: {"data": get_frontier_open_weight_stack()},
    "getMerlinDualLaneMasterSprint": lambda **args: {"data": get_dual_lane_master_sprint_plan()},
    "getMerlinThreeLaneIntensiveSprint": lambda **args: {"data": get_merlin_three_lane_intensive_sprint(limit=args.get("limit"))},
    "getMerlinApplicationsToolsLane": lambda **args: {"data": get_merlin_applications_tools_lane()},
    "getMerlinBooksArticlesLane": lambda **args: {"data": get_merlin_books_articles_lane()},
    "getMerlinAdversarialGrowthLane": lambda **args: {"data": get_merlin_adversarial_growth_lane()},
    "getMerlinContinuousLearningProtocol": lambda **args: {"data": get_merlin_continuous_learning_protocol(limit=args.get("limit"))},
    "getMerlinTrainingExecutionQueue": lambda **args: {"data": build_merlin_training_execution_queue(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=args.get("limit"),
    )},
    "getMerlinLaneProgressLedgers": lambda **args: {"data": get_merlin_lane_progress_ledgers(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=_coerce_positive_int(args.get("limit"), 5),
    )},
    "runMerlinTrainingCycle": lambda **args: {"data": run_merlin_training_cycle(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=args.get("limit"),
    )},
    "getMerlinTrainingChallengePack": lambda **args: {"data": get_merlin_training_challenge_pack(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=_coerce_positive_int(args.get("limit"), 12),
    )},
    "getMerlinCompetitiveBenchmarkPlan": lambda **args: {"data": get_competitive_benchmark_plan()},
    "getMerlinTrainingArtifacts": lambda **args: {"data": build_training_artifact_bundle(limit=args.get("limit"))},
    "getMerlinEnergyPlan": lambda **args: {"data": get_energy_optimization_track()},
    "getMerlinBackendPolicy": lambda **args: {"data": get_backend_expansion_policy()},
    "getMerlinWorkspacePolicy": lambda **args: {"data": get_workspace_policy()},
    "getMerlinWorkspaceState": lambda **args: {"data": get_workspace_state()},
    "getMerlinGovernancePolicy": lambda **args: {"data": get_governance_integration_policy()},
    "getMerlinReliabilityPlan": lambda **args: {"data": get_reliability_security_plan()},
    "getMerlinRolloutPlan": lambda **args: {"data": get_rollout_plan()},
    "getMerlinOperatingRhythm": lambda **args: {"data": get_operating_rhythm()},
    "getMerlinExitCriteria": lambda **args: {"data": get_exit_criteria()},
    "getMerlinProgramBlueprint": lambda **args: {"data": get_full_program_blueprint()},
    "getMerlinIdentityPolicy": lambda **args: {"data": get_identity_and_trust_policy()},
    "verifyMerlinIdentity": lambda **args: {"data": verify_identity_signals(
        str(args.get("query", "")),
        str(args.get("user_context", "")),
        str(args.get("page_context", "")),
    )},
    "authorizeMerlinPrivilege": lambda **args: {"data": authorize_privileged_request(
        str(args.get("query", "")),
        page_context=str(args.get("page_context", "")),
        user_context=str(args.get("user_context", "")),
    )},
    "getMerlinSentinelPolicy": lambda **args: {"data": get_sentinel_enforcement_policy()},
    "getMerlinMythosAstraContract": lambda **args: {"data": get_mythos_astra_contract()},
    "getMerlinOptimizationPriorities": lambda **args: {"data": get_merlin_optimization_priorities()},
    "getMerlinExecutionGraph": lambda **args: {"data": get_merlin_execution_graph()},
    "getMerlinBenchmarkSuite": lambda **args: {"data": get_merlin_benchmark_suite()},
    "getMerlinStageBCorpus": lambda **args: {"data": get_stage_b_benchmark_corpus()},
    "getMerlinStageCCorpus": lambda **args: {"data": get_stage_c_benchmark_corpus()},
    "getMerlinStageDCorpus": lambda **args: {"data": get_stage_d_benchmark_corpus()},
    "getMerlinStageECorpus": lambda **args: {"data": get_stage_e_benchmark_corpus()},
    "getMerlinExpertDomainCorpus": lambda **args: {"data": get_expert_domain_benchmark_corpus()},
    "getMerlinBenchmarkCorpora": lambda **args: {"data": get_benchmark_corpus(stage=args.get("stage"))},
    "getMerlinMultiStageBenchmarks": lambda **args: {"data": get_multi_stage_benchmark_plan()},
    "getMerlinDomainGateContract": lambda **args: {"data": get_domain_gate_contract()},
    "runMerlinStageAReceipts": lambda **args: {"data": run_stage_a_head_to_head_receipts_sync(limit=args.get("limit"))},
    "runMerlinStageBReceipts": lambda **args: {"data": run_stage_b_head_to_head_receipts_sync(limit=args.get("limit"))},
    "runMerlinStageCReceipts": lambda **args: {"data": run_stage_c_head_to_head_receipts_sync(limit=args.get("limit"))},
    "runMerlinStageDReceipts": lambda **args: {"data": run_stage_d_head_to_head_receipts_sync(limit=args.get("limit"))},
    "runMerlinStageEReceipts": lambda **args: {"data": run_stage_e_head_to_head_receipts_sync(limit=args.get("limit"))},
    "runMerlinDomainReceipts": lambda **args: {"data": run_stage_domain_head_to_head_receipts_sync(limit=args.get("limit"))},
    "getMerlinReplacementReadiness": lambda **args: {"data": build_stage_a_replacement_readiness(
        limit=args.get("limit"),
        sync_checks_ok=args.get("sync_checks_ok"),
    )},
    "getMerlinStageAArtifacts": lambda **args: {"data": build_stage_a_artifact_bundle(
        limit=args.get("limit"),
        sync_checks_ok=args.get("sync_checks_ok"),
    )},
    "getMerlinFrontierReadiness": lambda **args: {"data": get_frontier_readiness_packet(limit=args.get("limit"))},
    "getMerlinControlTower": lambda **args: {"data": build_merlin_control_tower(
        limit=_coerce_positive_int(args.get("limit"), 3),
        gate_history=list(args.get("gate_history") or []) or None,
    )},
    "getMerlinSprintReviewPacket": lambda **args: {"data": get_merlin_sprint_review_packet(limit=args.get("limit"))},
    "runMerlinTargetedRigorSprint": lambda **args: {"data": run_merlin_targeted_rigor_sprint(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=args.get("limit"),
        training_limit=args.get("training_limit"),
    )},
    "getMerlinHeavyReasoningLane": lambda **args: {"data": get_merlin_heavy_reasoning_lane(limit=args.get("limit"))},
    "getMerlinSovereignModelBoard": lambda **args: {"data": get_merlin_sovereign_model_board()},
    "getMerlinExecutionBoard": lambda **args: {"data": get_merlin_execution_board(limit=args.get("limit"))},
    "getMerlinValidationResiliencePacket": lambda **args: {"data": get_merlin_validation_resilience_packet(limit=args.get("limit"))},
    "getMerlinTrainingDataset": lambda **args: {"data": build_training_dataset_bundle(limit=args.get("limit"))},
    "getMerlinTrainingCuration": lambda **args: {"data": get_training_curation_ledger(limit=args.get("limit"))},
    "getMerlinMLflowManifests": lambda **args: {"data": get_mlflow_experiment_manifests(limit=args.get("limit"))},
    "getMerlinInferenceProviders": lambda **args: {"data": {"providers": get_inference_providers()}},
    "getMerlinInferenceHealth": lambda **args: {"data": get_merlin_inference_health(provider_name=str(args.get("provider", "")).strip() or None)},
"getMerlinReasoningChain": lambda **args: {"data": get_reasoning_chain(str(args.get("query", "")), max_hops=args.get("max_hops", 3))},
    "runMerlinResearchCycle": lambda **args: {"data": run_research_cycle(
        question=str(args.get("question", "")),
        budget=_coerce_positive_int(args.get("budget"), 3),
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
    )},
    "getMerlinCounterexampleDigest": lambda **args: {"data": build_counterexample_digest(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=_coerce_positive_int(args.get("limit"), 10),
    )},
    "getMerlinEnergyLedger": lambda **args: {"data": build_merlin_energy_ledger(
        (args.get("__session").telemetry if isinstance(args.get("__session"), MerlinSession) else MerlinSession().telemetry),
        limit=_coerce_positive_int(args.get("limit"), 10),
    )},
    "getMerlinMemoryGeometry": lambda **args: {"data": (
        args.get("__session").get_geometric_memory_map(
            str(args.get("query", "")),
            limit=_coerce_positive_int(args.get("limit"), 12),
        )
        if isinstance(args.get("__session"), MerlinSession)
        else MerlinSession().get_geometric_memory_map(
            str(args.get("query", "")),
            limit=_coerce_positive_int(args.get("limit"), 12),
        )
    )},
    "merlinConsolidateMemory": lambda **args: {"data": consolidate_memory(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=_coerce_positive_int(args.get("limit"), 10),
    )},
    "merlinSelfAudit": lambda **args: {"data": run_self_audit(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession()
    )},
    "generateFalsificationOracle": lambda **args: {"data": generate_falsification_oracle(
        domain=str(args.get("domain", "")),
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
    )},
    "merlinAnalyzeDepth": lambda **args: {"data": analyze_depth(
        session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else MerlinSession(),
        limit=_coerce_positive_int(args.get("limit"), 25),
    )},
"empiricalObservatoryCheck": lambda **args: {"data": {"delegated": "session_bound"}},
"kernelPProofProbe": lambda **args: {"data": {"delegated": "session_bound"}},
}


def get_toolkit_view(view: str = "index", *, domain: str | None = None, tool: str | None = None) -> dict[str, Any]:
    """Return one of the Merlin toolkit discovery views."""
    manifest = _tool_manifest()
    if view == "index":
        return {
            "view": "index",
            "functions": [f"{item['name']} — {item['summary']}" for item in manifest["functions"]],
            "integrations": [],
            "entities": [f"{item['name']} — {item['summary']}" for item in manifest["entities"]],
            "connectors": [f"{item['name']} — {item['summary']}" for item in manifest["connectors"]],
            "secrets": [item["name"] for item in manifest["secrets"]],
        }
    if view == "domain":
        selected = manifest.get(domain or "", [])
        return {"view": "domain", "domain": domain, "items": selected}
    if view == "tool":
        for group_name, items in manifest.items():
            for item in items:
                if item["name"] == tool:
                    return {"view": "tool", "tool": tool, "type": group_name[:-1], "detail": item}
        return {"view": "tool", "tool": tool, "error": "not found"}
    if view == "full":
        return {"view": "full", **manifest}
    if view == "state":
        state_session = MerlinSession()
        return {
            "view": "state",
            "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "repo": build_status_response(),
            "connectors": {
                "github": {
                    "authorized": bool(os.environ.get("GITHUB_TOKEN")),
                    "summary": "Standalone compatibility view only; no token is ever exposed.",
                },
            },
            "secrets": {
                "OPENROUTER_API_KEY": {
                    "available": bool(os.environ.get("OPENROUTER_API_KEY")),
                    "description": "OpenRouter access for compatibility-only fallback path.",
                },
                "BRAVE_API_KEY": {
                    "available": bool(os.environ.get("BRAVE_API_KEY")),
                    "description": "External literature alignment search.",
                },
                "HF_API_TOKEN": {
                    "available": bool(os.environ.get("HF_API_TOKEN")),
                    "description": "HF inference compatibility token.",
                },
            },
            "router": {
                "policy": get_router_policy(),
                "openrouter_compat_enabled": bool(os.environ.get("MERLIN_ENABLE_OPENROUTER_COMPAT")),
            },
            "inference": get_merlin_inference_health(),
            "reasoning_graph": {
                "multi_hop": True,
                "surface": "getMerlinReasoningChain",
            },
            "mentorship": {
                "charter": get_mentorship_sprint_charter(),
                "faculty_matrix": get_specialized_model_faculty_matrix(),
                "knowledge_transfer_cycles": get_knowledge_transfer_cycles(),
                "library_and_study": get_mentorship_library_and_study_assets(),
                "exchange_protocol": get_cross_model_exchange_protocol(),
                "closure_contract": get_mentorship_completion_contract(),
                "proof_first_closure_target": get_proof_first_closure_charter(),
                "burden_ledger": get_kawamura_closure_burden_ledger(),
                "dual_loop": get_dual_loop_learning_contract(),
                "mirrored_training_cycle": get_mirrored_training_cycle_contract(),
                "deterministic_proof_closure": get_deterministic_proof_closure_contract(),
                "cross_review_packet": get_merlin_cross_review_packet(),
                "sprint_command_rhythm": get_dual_loop_sprint_command_rhythm(),
            },
            "memory": state_session.get_public_memory_state(),
            "telemetry": state_session.get_telemetry_summary(public=True),
            "entities": {
                "MerlinSession": {
                    "summary": "Audited multi-tier session memory with contradiction tracking and measurable run telemetry.",
                    "schema": MERLIN_SESSION_SCHEMA,
                    "sample_count": 0,
                    "samples": [],
                    "storage_keys": [MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY],
                },
            },
        }
    return {"view": view, "error": "unsupported view"}


def route_tool(tool: str, args: dict[str, Any] | None = None, *, session: MerlinSession | None = None) -> dict[str, Any]:
    """Route a Merlin tool call to a safe local capability."""
    args = dict(args or {})
    active_session = session if session is not None else MerlinSession()
    manifest = _tool_manifest()
    policy = next((item for item in manifest["functions"] if item["name"] == tool), None)
    if policy is None and tool.startswith("entity.MerlinSession."):
        op = tool.split(".")[-1]
        if op == "audit":
            policy = {"args_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "additionalProperties": False}}
        elif op in {"schema", "state"}:
            policy = {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}}
    if policy is None and tool == "connector.github":
        policy = {"args_schema": {"type": "object", "properties": {}, "additionalProperties": False}}
    allowed_tools = {
        *(item["name"] for item in manifest["functions"]),
        "getMerlinBenchmarkCorpus",
        "evaluateMerlinBenchmarkResponse",
        "getMerlinMemoryState",
        "getMerlinMemoryGeometry",
        "runMerlinMemoryAudit",
        "getMerlinTelemetrySummary",
        "connector.github",
    }
    started = time.perf_counter()
    tool_type = "unknown"
    ok = True
    error = ""
    result: Any = None
    try:
        if not (tool in allowed_tools or tool.startswith("entity.MerlinSession.")):
            ok = False
            error = f"Tool not allowlisted: {tool}"
            raise ValueError(error)
        if policy:
            schema_ok, schema_error = _validate_args_schema(args, dict(policy.get("args_schema") or {}))
            if not schema_ok:
                ok = False
                error = schema_error
                raise ValueError(schema_error)
            if bool(policy.get("requires_human_gate")) and not bool(args.get("human_gate_approved")):
                ok = False
                error = "Human gate approval required for this tool."
                raise ValueError(error)
        if tool in _FUNCTIONS or tool in {"runMerlinResearchCycle", "getMerlinCounterexampleDigest", "getMerlinEnergyLedger", "getMerlinMemoryGeometry", "merlinConsolidateMemory", "merlinSelfAudit", "generateFalsificationOracle", "merlinAnalyzeDepth", "empiricalObservatoryCheck", "kernelPProofProbe", "getMerlinTrainingExecutionQueue", "getMerlinLaneProgressLedgers", "runMerlinTrainingCycle", "getMerlinTrainingChallengePack"}:
            tool_type = "function"
            if tool == "getMerlinTrainingDataset":
                result = {"data": build_training_dataset_bundle(
                    limit=args.get("limit"),
                    compiled_insights=active_session.get_compiled_training_insights(),
                )}
            elif tool == "getMerlinTrainingArtifacts":
                result = {"data": build_training_artifact_bundle(
                    limit=args.get("limit"),
                    compiled_insights=active_session.get_compiled_training_insights(),
                )}
            elif tool == "getMerlinTrainingCuration":
                result = {"data": get_training_curation_ledger(
                    limit=args.get("limit"),
                    compiled_insights=active_session.get_compiled_training_insights(),
                )}
            elif tool == "getMerlinMLflowManifests":
                result = {"data": get_mlflow_experiment_manifests(
                    limit=args.get("limit"),
                    compiled_insights=active_session.get_compiled_training_insights(),
                )}
            elif tool == "runMerlinResearchCycle":
                result = {"data": run_research_cycle(
                    question=str(args.get("question", "")),
                    budget=_coerce_positive_int(args.get("budget"), 3),
                    session=active_session,
                )}
            elif tool == "getMerlinCounterexampleDigest":
                result = {"data": build_counterexample_digest(
                    session=active_session,
                    limit=_coerce_positive_int(args.get("limit"), 10),
                )}
            elif tool == "getMerlinEnergyLedger":
                result = {"data": build_merlin_energy_ledger(
                    active_session.telemetry,
                    limit=_coerce_positive_int(args.get("limit"), 10),
                )}
            elif tool == "merlinConsolidateMemory":
                result = {"data": consolidate_memory(
                    session=active_session,
                    limit=_coerce_positive_int(args.get("limit"), 10),
                )}
            elif tool == "merlinSelfAudit":
                result = {"data": run_self_audit(session=active_session)}
            elif tool == "generateFalsificationOracle":
                result = {"data": generate_falsification_oracle(
                    domain=str(args.get("domain", "")),
                    session=active_session,
                )}
            elif tool == "merlinAnalyzeDepth":
                result = {"data": analyze_depth(
                    session=active_session,
                    limit=_coerce_positive_int(args.get("limit"), 25),
                )}
            elif tool == "empiricalObservatoryCheck":
                observatory = empirical_observatory_check(dict(args.get("observed") or {}))
                for rupture in list(observatory.get("ruptures") or []):
                    active_session.register_observatory_event(dict(rupture))
                result = {"data": observatory}
            elif tool == "kernelPProofProbe":
                probe = run_kernel_p_lean_proof_probe(
                    conjecture=str(args.get("conjecture") or ""),
                    context=str(args.get("context") or ""),
                    enable_repl=bool(args.get("enable_repl", False)),
                )
                active_session.register_proof_attempt(dict(probe))
                result = {"data": probe}
            else:
                session_passthrough_tools = {
                    "runMerlinResearchCycle",
                    "getMerlinCounterexampleDigest",
                    "getMerlinEnergyLedger",
                    "getMerlinMemoryGeometry",
                    "merlinConsolidateMemory",
                    "merlinSelfAudit",
                    "generateFalsificationOracle",
                    "merlinAnalyzeDepth",
                    "getMerlinTrainingExecutionQueue",
                    "getMerlinLaneProgressLedgers",
                    "runMerlinTrainingCycle",
                    "getMerlinTrainingChallengePack",
                }
                if tool in session_passthrough_tools:
                    result = _FUNCTIONS[tool](**{**args, "__session": active_session})
                else:
                    result = _FUNCTIONS[tool](**args)
        elif tool == "getMerlinBenchmarkCorpus":
            tool_type = "function"
            result = {"data": get_stage_a_benchmark_corpus()}
        elif tool == "evaluateMerlinBenchmarkResponse":
            tool_type = "function"
            result = {"data": evaluate_benchmark_response(
                str(args.get("benchmark_id", "")),
                dict(args.get("response") or {}),
                stage=str(args.get("stage")) if "stage" in args else None,
            )}
        elif tool == "evaluateMerlinEmpiricalGate":
            tool_type = "function"
            result = {"data": evaluate_empirical_gate(
                list(args.get("head_to_head_runs") or []),
                min_runs=int(args.get("min_runs", 12)),
                max_quality_regressions=int(args.get("max_quality_regressions", 0)),
            )}
        elif tool == "evaluateMerlinDomainGates":
            tool_type = "function"
            result = {"data": evaluate_domain_gate_summary(
                list(args.get("runs") or []),
                required_domains=list(args.get("required_domains") or []) or None,
            )}
        elif tool == "evaluateMerlinLongitudinalAcceptance":
            tool_type = "function"
            result = {"data": evaluate_longitudinal_acceptance(
                list(args.get("gate_history") or []),
                window_size=_coerce_positive_int(args.get("window_size"), 4),
                min_clean_windows=_coerce_positive_int(args.get("min_clean_windows"), 3),
            )}
        elif tool == "evaluateMerlinGeometricLongitudinalAcceptance":
            tool_type = "function"
            result = {"data": evaluate_geometric_longitudinal_acceptance(
                list(args.get("gate_history") or []),
                window_size=_coerce_positive_int(args.get("window_size"), 4),
                min_clean_windows=_coerce_positive_int(args.get("min_clean_windows"), 2),
            )}
        elif tool == "getMerlinPromotionPacket":
            tool_type = "function"
            sync_checks_ok = (
                bool(args.get("sync_checks_ok"))
                if "sync_checks_ok" in args
                else bool(run_sync_checks().get("ok"))
            )
            result = {"data": build_promotion_packet(
                head_to_head_runs=list(args.get("head_to_head_runs") or []),
                telemetry_summary=active_session.get_telemetry_summary(public=True),
                sync_checks_ok=sync_checks_ok,
                kernel_gate_summary=dict(args.get("kernel_gate_summary") or {}),
            )}
        elif tool == "getMerlinMemoryState":
            tool_type = "function"
            result = {"data": active_session.get_public_memory_state()}
        elif tool == "runMerlinMemoryAudit":
            tool_type = "function"
            audit = active_session.audit_memory(str(args.get("query", "")))
            result = {"data": {
                "query": audit["query"],
                "matched_memory_count": audit["matched_memory_count"],
                "matched_scopes": audit["matched_scopes"],
            }}
        elif tool == "getMerlinTelemetrySummary":
            tool_type = "function"
            result = {"data": active_session.get_telemetry_summary(public=True)}
        elif tool.startswith("entity.MerlinSession."):
            tool_type = "entity"
            op = tool.split(".")[-1]
            if op == "schema":
                result = {"data": MERLIN_SESSION_SCHEMA}
            elif op == "state":
                result = {"data": active_session.get_public_memory_state()}
            elif op == "audit":
                query = str(args.get("query", "")).strip()
                if query:
                    audit = active_session.audit_memory(query)
                    result = {"data": {
                        "query": query,
                        "matched_memory_count": audit["matched_memory_count"],
                        "matched_scopes": audit["matched_scopes"],
                    }}
                else:
                    result = {
                        "data": {
                            "recent_memory_audits": active_session.get_memory_state()["recent_memory_audits"],
                            "contradiction_event_count": active_session.get_memory_state()["contradiction_event_count"],
                        },
                    }
            else:
                ok = False
                error = "Unsupported MerlinSession operation."
        elif tool == "connector.github":
            tool_type = "connector"
            result = {
                "authorized": bool(os.environ.get("GITHUB_TOKEN")),
                "type": "github",
                "connectionConfig": {"mode": "compatibility-summary-only"},
            }
        else:
            ok = False
            error = f"Unknown tool: {tool}"
    except Exception as exc:  # pragma: no cover
        ok = False
        error = str(exc)
    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    replay = _build_replay_artifact(tool=tool, args=args, result=result, ok=ok)
    return {
        "ok": ok,
        "tool": tool,
        "type": tool_type,
        "result": result,
        "error": error,
        "policy": {
            "capability_class": (policy or {}).get("capability_class", "unknown"),
            "risk_level": (policy or {}).get("risk_level", "unknown"),
            "requires_human_gate": bool((policy or {}).get("requires_human_gate", False)),
        },
        "audit": {
            "args_keys": sorted(args.keys()),
            "duration_ms": duration_ms,
        },
        "replay_artifact": replay,
        "duration_ms": duration_ms,
    }


def get_path(obj: Any, path: str | None):
    """Resolve a dotted path into an object."""
    if not path:
        return obj
    current = obj
    for key in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(key)]
            except Exception:
                return None
        elif isinstance(current, dict):
            current = current.get(key)
        else:
            return None
    return current


def _step_trajectory_risk(step: dict[str, Any]) -> dict[str, Any]:
    tool = str(step.get("tool") or "")
    args = dict(step.get("args") or {})
    mutating_tool = tool in {
        "authorizeMerlinPrivilege",
        "runMerlinSyncChecks",
    }
    method = str(args.get("method") or args.get("http_method") or "").strip().upper()
    external_write = bool(args.get("write")) or method in {"POST", "PUT", "PATCH", "DELETE"}
    privilege = any(token in tool.lower() for token in ("privilege", "authorize"))
    high_risk = bool(mutating_tool or external_write or privilege)
    return {
        "tool": tool,
        "high_risk": high_risk,
        "reasons": [
            reason
            for reason, condition in (
                ("state_mutation", mutating_tool),
                ("external_write_path", external_write),
                ("privilege_surface", privilege),
            )
            if condition
        ],
    }


def _validate_trajectory_preflight(steps: list[dict[str, Any]]) -> dict[str, Any]:
    assessments = [_step_trajectory_risk(step) for step in steps]
    high_risk = [item for item in assessments if item["high_risk"]]
    validated_contracts: list[dict[str, Any]] = []
    invalid_contract_steps: list[dict[str, Any]] = []
    missing_contract_steps: list[dict[str, Any]] = []
    for index, risk in enumerate(assessments):
        if not risk["high_risk"]:
            continue
        payload = dict((steps[index] or {}).get("trajectory_contract") or {})
        if not payload:
            missing_contract_steps.append({"step": index, "tool": risk["tool"], "reasons": risk["reasons"]})
            continue
        invariants = payload.get("invariants")
        valid_invariants = (
            isinstance(invariants, list)
            and len(invariants) > 0
            and all(isinstance(item, str) and item.strip() for item in invariants)
        )
        contract_valid = bool(payload.get("id")) and valid_invariants
        if not contract_valid:
            invalid_contract_steps.append({"step": index, "tool": risk["tool"], "reasons": risk["reasons"]})
        else:
            validated_contracts.append({"step": index, **payload})
    if high_risk and missing_contract_steps:
        return {
            "ok": False,
            "high_risk_count": len(high_risk),
            "high_risk_steps": high_risk,
            "error": "trajectory_contract_required_for_high_risk_chain",
            "verification": "failed_closed",
            "missing_contract_steps": missing_contract_steps,
        }
    if high_risk and invalid_contract_steps:
        return {
            "ok": False,
            "high_risk_count": len(high_risk),
            "high_risk_steps": high_risk,
            "error": "trajectory_contract_invalid",
            "verification": "failed_closed",
            "invalid_contract_steps": invalid_contract_steps,
        }
    lean_hook = any(bool(item.get("lean4_hook_enabled")) for item in validated_contracts)
    lean_probe = (
        run_kernel_p_lean_proof_probe(
            conjecture=f"Trajectory invariants: {','.join(str(item.get('id')) for item in validated_contracts)}",
            context=json.dumps([item.get("invariants") for item in validated_contracts], ensure_ascii=False),
            enable_repl=lean_hook,
        )
        if high_risk and validated_contracts
        else {"proof_verdict": "not_applicable", "repl_used": False}
    )
    if lean_hook and str(lean_probe.get("proof_verdict") or "") != "verified":
        return {
            "ok": False,
            "high_risk_count": len(high_risk),
            "high_risk_steps": high_risk,
            "error": "trajectory_lean_preflight_failed",
            "verification": "failed_closed",
            "contracts": validated_contracts,
            "lean_preflight": lean_probe,
        }
    return {
        "ok": True,
        "high_risk_count": len(high_risk),
        "high_risk_steps": high_risk,
        "contracts": validated_contracts,
        "lean_preflight": lean_probe,
    }


def orchestrate_steps(steps: list[dict[str, Any]], *, session: MerlinSession | None = None) -> dict[str, Any]:
    """Execute a bounded sequential Merlin tool chain."""
    if len(steps) > 10:
        raise ValueError("step cap exceeded (max 10)")
    if any(str(step.get("tool", "")).strip() == "authorizeMerlinPrivilege" for step in steps):
        raise ValueError("authorizeMerlinPrivilege is blocked in orchestration; use single-step invocation with explicit human gate.")
    preflight = _validate_trajectory_preflight(steps)
    if not bool(preflight.get("ok")):
        return {
            "ok": False,
            "steps": [],
            "total_duration_ms": 0.0,
            "audit_log_mode": "required",
            "human_gate_required": True,
            "policy_summary": {
                "high_risk_steps": int(preflight.get("high_risk_count", 0)),
                "blocked_tools_in_orchestration": ["authorizeMerlinPrivilege"],
            },
            "trajectory_preflight": preflight,
            "error": str(preflight.get("error") or "trajectory_preflight_failed"),
            "replay_artifact": {"generated_at": _utcnow(), "step_count": 0, "steps": [], "digest_sha256": ""},
        }
    started = time.perf_counter()
    results = []
    for index, step in enumerate(steps):
        tool = str(step.get("tool", ""))
        args = dict(step.get("args") or {})
        threading = step.get("input_from") or {}
        if threading:
            from_step = int(threading.get("step", -1))
            prior = results[from_step] if 0 <= from_step < len(results) else None
            if prior and prior.get("ok"):
                threaded = get_path(prior.get("result"), threading.get("path"))
                into = threading.get("into")
                template = threading.get("template")
                if into and template is not None:
                    args[into] = str(template).replace("{value}", "" if threaded is None else str(threaded))
                elif into:
                    args[into] = threaded
                elif isinstance(threaded, dict):
                    args.update(threaded)
                else:
                    args["_threaded"] = threaded
        result = route_tool(tool, args, session=session)
        result["step"] = index
        result["threading"] = threading
        results.append(result)
    total_duration_ms = round((time.perf_counter() - started) * 1000, 3)
    high_risk_steps = sum(1 for step in results if str((step.get("policy") or {}).get("risk_level")) == "high")
    replay = {
        "generated_at": _utcnow(),
        "step_count": len(results),
        "steps": [
            {
                "step": step.get("step"),
                "tool": step.get("tool"),
                "ok": step.get("ok"),
                "policy": step.get("policy"),
                "args_keys": (step.get("audit") or {}).get("args_keys", []),
                "threading": step.get("threading", {}),
                "duration_ms": step.get("duration_ms"),
                "replay_digest": ((step.get("replay_artifact") or {}).get("digest_sha256", "")),
            }
            for step in results
        ],
    }
    replay_payload = json.dumps(replay, ensure_ascii=False, sort_keys=True)
    replay["digest_sha256"] = hashlib.sha256(replay_payload.encode("utf-8")).hexdigest()
    return {
        "ok": all(step.get("ok") for step in results),
        "steps": results,
        "total_duration_ms": total_duration_ms,
        "audit_log_mode": "required",
        "human_gate_required": any((step.get("policy") or {}).get("requires_human_gate") for step in results),
        "policy_summary": {
            "high_risk_steps": high_risk_steps,
            "blocked_tools_in_orchestration": ["authorizeMerlinPrivilege"],
        },
        "trajectory_preflight": preflight,
        "replay_artifact": replay,
    }
