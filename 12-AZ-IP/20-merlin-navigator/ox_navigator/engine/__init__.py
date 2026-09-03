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
from .merlin_persona import build_persona_prompt, build_system_prompt, detect_persona_mode, extract_urls, is_internal_question
from .merlin_runtime import (
    get_advanced_execution_graph,
    get_benchmark_suite,
    get_mythos_astra_runtime_contract,
    get_optimization_priorities,
)
from .merlin_program import (
    get_backend_expansion_policy,
    get_current_stack_baseline,
    get_energy_optimization_track,
    get_merlin_benchmark_suite,
    get_merlin_execution_graph,
    get_merlin_optimization_priorities,
    get_exit_criteria,
    get_full_program_blueprint,
    get_governance_integration_policy,
    get_identity_and_trust_policy,
    get_knowledge_core_sources,
    get_mythos_astra_contract,
    get_model_strategy,
    get_operating_rhythm,
    get_program_charter,
    get_reliability_security_plan,
    get_replacement_scope,
    get_rollout_plan,
    get_sentinel_enforcement_policy,
    get_training_and_adaptation,
    get_weights_and_measures,
    run_sync_checks,
)
from .merlin_rag import build_rag_context, closest_pillar, lookup_kb, retrieve_context
from .merlin_tools import get_path, get_toolkit_view, orchestrate_steps, route_tool
from .pillar_graph import PILLAR_DEPENDENCY_GRAPH, find_critical_path, get_dependencies, get_dependents
from .session import OxSession

__all__ = [
    'API_BASE', 'BETA_C1', 'BETA_C2', 'DEFAULT_TEMPERATURE', 'EXAMPLE_QUERIES',
    'GATE_LABELS', 'K_CS', 'MAX_HISTORY', 'MODEL_ID', 'N_S', 'R_BRAIDED',
    'WINDING_NUMBER', 'OxApiKeyMissingError', 'OxClient', 'OxSession',
    'classify_response', 'extract_gate_badges', 'filter_by_category',
    'get_categories', 'get_tension_map_data', 'load_flashcards', 'load_kb', 'search_kb',
    'LEAN4_THEOREM_COUNT', 'LEAN4_THEOREM_SAMPLE', 'search_theorems', 'get_theorem_count',
    'get_theorems_by_pillar', 'PILLAR_DEPENDENCY_GRAPH', 'get_dependencies', 'get_dependents',
    'find_critical_path', 'MerlinSession', 'MERLIN_ACTIVE_SESSION_KEY', 'MERLIN_CACHE_KEY',
    'MERLIN_MAX_HISTORY', 'build_persona_prompt', 'build_system_prompt', 'detect_persona_mode',
    'extract_urls', 'is_internal_question', 'lookup_kb', 'retrieve_context', 'build_rag_context',
    'closest_pillar', 'extract_tool_call', 'strip_tool_call', 'query_merlin', 'get_toolkit_view',
    'route_tool', 'orchestrate_steps', 'get_path', 'CANONICAL_IDENTITY', 'ALLOWED_ALIASES',
    'FORBIDDEN_ALIASES', 'TRUSTED_SOURCES_RANKED', 'get_identity_policy', 'detect_identity_mentions',
    'verify_identity_signals', 'is_privileged_modification_request', 'authorize_privileged_request',
    'get_mythos_astra_runtime_contract', 'get_optimization_priorities',
    'get_advanced_execution_graph', 'get_benchmark_suite',
    'get_program_charter', 'get_replacement_scope',
    'get_current_stack_baseline', 'get_weights_and_measures', 'get_knowledge_core_sources',
    'run_sync_checks', 'get_model_strategy', 'get_training_and_adaptation',
    'get_energy_optimization_track', 'get_backend_expansion_policy',
    'get_governance_integration_policy', 'get_reliability_security_plan',
    'get_identity_and_trust_policy', 'get_sentinel_enforcement_policy',
    'get_mythos_astra_contract', 'get_merlin_optimization_priorities',
    'get_merlin_execution_graph', 'get_merlin_benchmark_suite',
    'get_rollout_plan', 'get_operating_rhythm', 'get_exit_criteria',
    'get_full_program_blueprint',
]
