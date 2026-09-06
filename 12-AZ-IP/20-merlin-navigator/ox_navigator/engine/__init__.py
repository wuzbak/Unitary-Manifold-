# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Engine exports for OX Navigator."""

from .client import OxApiKeyMissingError, OxClient
from .constants import (
    API_BASE,
    BETA_C1,
    BETA_C2,
    DEFAULT_TEMPERATURE,
    EXAMPLE_QUERIES,
    GATE_LABELS,
    K_CS,
    MAX_HISTORY,
    MERLIN_TICK_DENOMINATOR,
    MERLIN_TICK_NUMERATOR,
    MERLIN_TICK_RATIO,
    MODEL_ID,
    N_S,
    R_BRAIDED,
    WINDING_NUMBER,
)
from .flashcard import filter_by_category, get_categories, load_flashcards
from .gate_parser import classify_response, extract_gate_badges
from .interrogator import get_tension_map_data, load_kb, search_kb
from .lean4_index import LEAN4_THEOREM_COUNT, LEAN4_THEOREM_SAMPLE, get_theorem_count, get_theorems_by_pillar, search_theorems
from .merlin_engine import extract_tool_call, query_merlin, strip_tool_call
from .merlin_identity import (
    ALLOWED_ALIASES,
    CANONICAL_IDENTITY,
    FORBIDDEN_ALIASES,
    TRUSTED_SOURCES_RANKED,
    authorize_privileged_request,
    detect_identity_mentions,
    get_identity_policy,
    is_privileged_modification_request,
    verify_identity_signals,
)
from .merlin_memory import MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY, MERLIN_MAX_HISTORY, MerlinSession
from .merlin_persona import build_persona_prompt, build_system_prompt, detect_persona_mode, extract_urls, is_internal_question, persona_governance_violations
from .merlin_runtime import (
    get_advanced_execution_graph,
    get_benchmark_suite,
    get_mythos_astra_runtime_contract,
    get_optimization_priorities,
)
from .merlin_benchmark import (
    evaluate_benchmark_response,
    get_benchmark_corpus,
    get_stage_a_benchmark_corpus,
    get_stage_b_benchmark_corpus,
    get_stage_c_benchmark_corpus,
    match_benchmark_for_query,
)
from .merlin_telemetry import build_run_telemetry, estimate_cost_usd, estimate_energy_joules, estimate_token_count, summarize_runs
from .merlin_program import (
    get_backend_expansion_policy,
    get_competitive_benchmark_plan,
    get_current_stack_baseline,
    get_deterministic_proof_closure_contract,
    get_dual_loop_learning_contract,
    get_dual_loop_sprint_command_rhythm,
    get_energy_optimization_track,
    get_merlin_benchmark_suite,
    get_merlin_execution_graph,
    get_merlin_optimization_priorities,
    get_mirrored_training_cycle_contract,
    get_exit_criteria,
    get_full_program_blueprint,
    get_frontier_open_weight_stack,
    get_governance_integration_policy,
    get_identity_and_trust_policy,
    get_knowledge_core_sources,
    get_mythos_astra_contract,
    get_model_strategy,
    get_open_science_resource_registry,
    get_operating_rhythm,
    get_program_charter,
    get_program_doctrine,
    get_merlin_pentad_contract,
    get_reliability_security_plan,
    get_replacement_scope,
    get_rollout_plan,
    get_sovereignty_roadmap,
    get_sentinel_enforcement_policy,
    get_mlflow_experiment_manifests,
    build_training_dataset_bundle,
    get_training_architecture,
    get_training_and_adaptation,
    get_weights_and_measures,
    build_training_artifact_bundle,
    run_sync_checks,
)
from .merlin_admission import evaluate_model_admission, get_model_admission_policy
from .merlin_router import choose_runtime, get_router_policy
from .merlin_rag import build_rag_context, closest_pillar, lookup_kb, retrieve_context
from .merlin_tools import get_path, get_toolkit_view, orchestrate_steps, route_tool
from .merlin_workspace import get_workspace_policy, get_workspace_state
from .pillar_graph import PILLAR_DEPENDENCY_GRAPH, find_critical_path, get_dependencies, get_dependents
from .session import OxSession

__all__ = [
    'API_BASE', 'BETA_C1', 'BETA_C2', 'DEFAULT_TEMPERATURE', 'EXAMPLE_QUERIES',
    'GATE_LABELS', 'K_CS', 'MAX_HISTORY', 'MERLIN_TICK_NUMERATOR', 'MERLIN_TICK_DENOMINATOR', 'MERLIN_TICK_RATIO', 'MODEL_ID', 'N_S', 'R_BRAIDED',
    'WINDING_NUMBER', 'OxApiKeyMissingError', 'OxClient', 'OxSession',
    'classify_response', 'extract_gate_badges', 'filter_by_category',
    'get_categories', 'get_tension_map_data', 'load_flashcards', 'load_kb', 'search_kb',
    'LEAN4_THEOREM_COUNT', 'LEAN4_THEOREM_SAMPLE', 'search_theorems', 'get_theorem_count',
    'get_theorems_by_pillar', 'PILLAR_DEPENDENCY_GRAPH', 'get_dependencies', 'get_dependents',
    'find_critical_path', 'MerlinSession', 'MERLIN_ACTIVE_SESSION_KEY', 'MERLIN_CACHE_KEY',
    'MERLIN_MAX_HISTORY', 'build_persona_prompt', 'build_system_prompt', 'detect_persona_mode',
    'extract_urls', 'is_internal_question', 'persona_governance_violations', 'lookup_kb', 'retrieve_context', 'build_rag_context',
    'closest_pillar', 'extract_tool_call', 'strip_tool_call', 'query_merlin', 'get_toolkit_view',
    'route_tool', 'orchestrate_steps', 'get_path', 'CANONICAL_IDENTITY', 'ALLOWED_ALIASES',
    'FORBIDDEN_ALIASES', 'TRUSTED_SOURCES_RANKED', 'get_identity_policy', 'detect_identity_mentions',
    'verify_identity_signals', 'is_privileged_modification_request', 'authorize_privileged_request',
    'get_mythos_astra_runtime_contract', 'get_optimization_priorities',
    'get_advanced_execution_graph', 'get_benchmark_suite', 'get_stage_a_benchmark_corpus',
    'get_stage_b_benchmark_corpus', 'get_stage_c_benchmark_corpus', 'get_benchmark_corpus',
    'match_benchmark_for_query', 'evaluate_benchmark_response', 'estimate_token_count', 'estimate_cost_usd',
    'estimate_energy_joules', 'build_run_telemetry', 'summarize_runs',
    'get_program_charter', 'get_program_doctrine', 'get_sovereignty_roadmap', 'get_replacement_scope',
    'get_merlin_pentad_contract', 'get_dual_loop_learning_contract',
    'get_mirrored_training_cycle_contract', 'get_deterministic_proof_closure_contract',
    'get_dual_loop_sprint_command_rhythm',
    'get_current_stack_baseline', 'get_weights_and_measures', 'get_knowledge_core_sources',
    'run_sync_checks', 'get_model_strategy', 'get_training_and_adaptation',
    'get_training_architecture', 'get_open_science_resource_registry',
    'get_frontier_open_weight_stack',
    'get_competitive_benchmark_plan', 'build_training_dataset_bundle',
    'get_mlflow_experiment_manifests', 'build_training_artifact_bundle',
    'get_energy_optimization_track', 'get_backend_expansion_policy',
    'get_governance_integration_policy', 'get_reliability_security_plan',
    'get_identity_and_trust_policy', 'get_sentinel_enforcement_policy',
    'get_mythos_astra_contract', 'get_merlin_optimization_priorities',
    'get_merlin_execution_graph', 'get_merlin_benchmark_suite',
    'get_rollout_plan', 'get_operating_rhythm', 'get_exit_criteria',
    'get_full_program_blueprint', 'get_model_admission_policy', 'evaluate_model_admission',
    'get_router_policy', 'choose_runtime', 'get_workspace_policy', 'get_workspace_state',
]
