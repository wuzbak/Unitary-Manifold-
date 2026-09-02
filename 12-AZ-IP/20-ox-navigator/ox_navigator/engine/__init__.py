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
from .merlin_memory import MERLIN_ACTIVE_SESSION_KEY, MERLIN_CACHE_KEY, MERLIN_MAX_HISTORY, MerlinSession
from .merlin_persona import build_persona_prompt, build_system_prompt, detect_persona_mode, extract_urls, is_internal_question
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
    'route_tool', 'orchestrate_steps', 'get_path',
]
