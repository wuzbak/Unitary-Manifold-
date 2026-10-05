# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
bot/rag_index.py — RAG (Retrieval-Augmented Generation) index builder for
the Unitary Manifold repository.

Builds a keyword index over the repository's key documents, prediction
registry, and FALLIBILITY.md for in-context Q&A without a vector database.

Usage::

    from bot.rag_index import RAGIndex, answer_question
    idx = RAGIndex.build()
    result = answer_question(idx, "What is the birefringence prediction?")
    print(result["answer"])

This is a pure-Python implementation with no external dependencies beyond
the standard library.  For production use, replace the keyword scoring
with a proper embedding model.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import ast
import os
import re
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from bot.session_bootstrap import current_intent_snapshot

__all__ = [
    "RAGIndex",
    "DocumentChunk",
    "answer_question",
    "build_default_index",
    "build_context_scaffold",
    "build_intent_index",
    "detect_query_lane",
    "render_context_scaffold",
    "retrieve_intent",
]

_TOKEN_ALIASES = {
    "β": "birefringence",
    "beta": "birefringence",
    "cmb": "cmb",
    "gut": "alpha_gut",
    "toe": "toe_score",
    "intent": "intent",
    "wave": "wave",
    "session": "intent",
    "radion": "radion",
    "dataset": "trusted_open_resources",
    "datasets": "trusted_open_resources",
    "resources": "trusted_open_resources",
    "pubmed": "trusted_open_resources",
    "openalex": "trusted_open_resources",
    "kaggle": "trusted_open_resources",
}

# Intent/session sources should outrank generic documentation on tie-like matches
# because they represent the freshest operator-visible state.
HILS_SESSION_WEIGHT = 1.35
CO_EMERGENCE_WEIGHT = 1.20
DOCS_WEIGHT = 1.10
TITLE_BONUS_WEIGHT = 0.25
PHRASE_MATCH_BONUS = 0.15
KB_PHRASE_MATCH_BONUS = 0.20
_QUERY_NOISE = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "can", "could",
    "did", "do", "does", "for", "from", "has", "have", "how", "i", "in", "is",
    "it", "its", "of", "on", "or", "please", "the", "this", "to", "was", "we",
    "what", "when", "where", "which", "why", "will", "with", "would", "you",
    "current", "latest", "status", "model", "origin", "proof", "proved", "proven",
    "derived", "derivation", "prediction", "predictions", "theory", "framework",
    "physics", "geometry", "geometric", "5d", "scientific", "dark",
}
_FOUNDATION_DOCUMENTS = [
    ("docs/TRUTH_LAYER.md", "Current foundation reassessment / action-derived flow"),
    ("1-THEORY/Z2_PARITY_NOTE.md", "Orbifold photon origin — open boundary"),
]
_CURRENT_TRUTH_SECTIONS = (
    (2, "Synthesis repair (2026-10-05)"),
    (3, "Mathematical findings and assumptions"),
    (3, "Sprint CX action-derived flow steward promotion"),
    (3, "Lane 1 action-derived flow replacement (Sprint CW; promoted within perimeter in Sprint CX)"),
)
_AST_CONTEXT_SKIP_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules", "build", "dist"}
_GATE_PRIORITY = {
    "GOVERNANCE": 5,
    "HARDGATE": 4,
    "DERIVED": 3,
    "OPEN_GAP": 2,
    "ARCHITECTURE_LIMIT": 1,
    "ADJACENT_TRACK": 0,
}
_LANE_PRIORITY = {
    "formal_proof": 5,
    "memory_audit": 4,
    "tool_orchestration": 3,
    "runtime_performance": 2,
    "repository_state": 1,
    "physics_navigation": 0,
}
_LANE_HINTS = {
    "formal_proof": {
        "label": "Formal proof / theorem lane",
        "keywords": {"proof", "theorem", "derive", "derivation", "lean", "hardgate", "formal"},
        "tool_hints": ["/api/psicat/reasoning-chain", "/api/psicat/ast-context-records", "/api/psicat/training-dataset"],
    },
    "memory_audit": {
        "label": "Memory / contradiction lane",
        "keywords": {"memory", "contradiction", "drift", "recall", "audit", "history"},
        "tool_hints": ["/api/psicat/memory", "/api/psicat/memory-geometry", "/api/psicat/counterexample-digest"],
    },
    "tool_orchestration": {
        "label": "Tool routing / orchestration lane",
        "keywords": {"tool", "tools", "route", "routing", "orchestrate", "agenttoolkit", "agentinvoke", "agentorchestrate"},
        "tool_hints": ["/api/agentToolkit", "/api/agentInvoke", "/api/agentOrchestrate"],
    },
    "runtime_performance": {
        "label": "Runtime / performance lane",
        "keywords": {"runtime", "performance", "throughput", "benchmark", "training", "latency", "telemetry", "profile"},
        "tool_hints": ["/api/psicat/lane-e-runtime-profiles", "/api/psicat/training-execution-bundle", "/api/psicat/telemetry"],
    },
    "repository_state": {
        "label": "Repository status lane",
        "keywords": {"status", "wave", "regression", "tests", "changelog", "repo", "repository"},
        "tool_hints": ["/api/status", "/api/pillars"],
    },
    "physics_navigation": {
        "label": "Physics / repository navigation lane",
        "keywords": {"pillar", "litebird", "birefringence", "desi", "metric", "boundary", "prediction", "physics"},
        "tool_hints": ["/api/status", "/api/pillars", "/api/pillar/{pillar_id}"],
    },
}

# ---------------------------------------------------------------------------
# Structured knowledge base — key facts hard-coded for reliability
# ---------------------------------------------------------------------------

#: Core facts about the Unitary Manifold (always available without file I/O)
KNOWLEDGE_BASE: Dict[str, Dict] = {
    "birefringence": {
        "topic": "CMB birefringence β prediction",
        "answer": (
            "The Unitary Manifold predicts two birefringence modes from the braided "
            "winding state: β₁ ≈ 0.273° (canonical, k_CS=61 secondary state) and "
            "β₂ ≈ 0.331° (derived, k_CS=74 primary state). "
            "The admissible window is [0.22°, 0.38°] with a predicted gap [0.29°, 0.31°]. "
            "These predictions will be tested by the LiteBIRD satellite (~2032). "
            "Any β outside [0.22°, 0.38°] or inside [0.29°, 0.31°] falsifies the theory."
        ),
        "sources": ["src/core/prediction_registry.py", "docs/LITEBIRD_FALSIFIER_BRIEF.md"],
        "status": "GEOMETRIC_PREDICTION",
    },
    "winding_number": {
        "topic": "Winding number n_w = 5 selection",
        "match_terms": ["winding", "n_w", "nw5"],
        "answer": (
            "n_w = 5 is observationally selected by Planck n_s within the stated "
            "candidate family {5,7}. Historical APS boundary-phase arguments select "
            "5 conditionally on the half-class / boundary assumptions; they do not "
            "establish unconditional first-principles uniqueness. The current "
            "foundation reassessment controls stronger historical closure language: "
            "orbifold parity alone does not choose an internal gauge involution "
            "or supply the missing photon. Conditional algebra and observational "
            "agreement are not empirical confirmation of the full framework."
        ),
        "sources": [
            "1-THEORY/DERIVATION_STATUS.md",
            "1-THEORY/NW_UNIQUENESS_STATUS.md",
            "FALLIBILITY.md",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "OBSERVATIONALLY_SELECTED / CONDITIONAL_UNIQUENESS",
    },
    "alpha_s": {
        "topic": "Strong coupling α_s(M_Z)",
        "answer": (
            "The cited historical forward-chain audit quotes corrected "
            "α_s(M_EW) ≈ 0.030–0.048 versus the comparison value ≈ 0.118. "
            "It separately quotes an SU(5) running route near 0.118, conditional "
            "on unification assumptions; these are not one canonical derivation. "
            "A 10D CY₃/flux completion is exploratory, not an established solution "
            "of the gap. Current joint UV/Higgs predictivity remains open under "
            "the foundation reassessment in docs/TRUTH_LAYER.md. No new "
            "calculation or empirical confirmation is reported here."
        ),
        "sources": ["src/core/alpha_s_forward_chain_audit.py", "docs/TRUTH_LAYER.md"],
        "status": "HISTORICAL_CONDITIONAL_ESTIMATES / OPEN_GAP",
    },
    "higgs_mass": {
        "topic": "Higgs mass m_H = 125.25 GeV",
        "answer": (
            "Historical Higgs-sector summaries quote a conditional GW VEV "
            "estimate v ≈ 257.6 GeV and mass estimates around 125 GeV; these "
            "are not independent action-level predictions. The cited 6D+ mixing "
            "module uses supplied VEV, base-mass, radion and brane inputs and "
            "compares against m_H = 125.25 GeV. Numerical agreement is not a "
            "derivation of those inputs. Current joint UV/Higgs predictivity "
            "remains open under docs/TRUTH_LAYER.md's foundation reassessment."
        ),
        "sources": [
            "src/sixd/higgs_radion_full_geometry_6dplus.py",
            "src/core/sm_free_parameters.py",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_CONDITIONAL_ESTIMATES / OPEN_GAP",
    },
    "toe_score": {
        "topic": "Framework epistemic scope and derivation coverage",
        "match_terms": [
            "toe", "toe_score", "framework derivation coverage",
            "framework status", "framework completeness", "parameter completeness",
            "complete physical theory", "complete model",
        ],
        "answer": (
            "The framework is not established as a complete physical theory. "
            "Mathematical results apply within their stated assumptions and domains; "
            "test success does not establish empirical confirmation. The default "
            "flow has action-derived field equations within a restricted circle "
            "reduction, but self-consistent coupled physical-time evolution and orbifold photon origin "
            "remain open. Individual claims need scoped evidence and external tests, "
            "not an aggregate completeness score."
        ),
        "sources": ["docs/TRUTH_LAYER.md", "FALLIBILITY.md"],
        "status": "SCOPED_RESULTS / OPEN_PHYSICAL_OBLIGATIONS",
    },
    "action_to_evolution": {
        "topic": "Action-derived evolution / Euler-Lagrange field equations",
        "match_terms": [
            "action", "evolution", "euler lagrange", "euler_lagrange", "relaxation",
        ],
        "answer": (
            "The action-to-evolution contract reports "
            "DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN (Sprint CX, Pillar 1130). "
            "The checkable action, Euler-Lagrange match and stated time/domain "
            "deliverables are earned within the declared perimeter: y-independent "
            "zero modes on a 1-D periodic grid, reducing the 5D Einstein-Hilbert "
            "action on a circle. The default action_derived flow relaxes those "
            "field equations, with metric, gauge and scalar residual certificates. "
            "The t-relaxation law is declared, not derived; t is not coordinate "
            "time and coupled physical-time evolution is not certified. The separate "
            "Maxwell test-field solver uses physical coordinate time on a prescribed "
            "Minkowski background with constant radion; it does not solve the coupled "
            "Einstein/radion equations or promote this contract. Exact reduction "
            "beyond the reduced diagonal ansatz remains open. The legacy "
            "phenomenological flow is unchanged and not covered. This is PARTIAL "
            "action-to-evolution progress, not framework closure or photon recovery."
        ),
        "sources": [
            "src/core/action_to_evolution_contract.py",
            "src/core/action_to_evolution_derived_flow_certificate.py",
            "src/core/pillar1130_action_derived_flow_steward_promotion.py",
            "docs/TRUTH_LAYER.md",
            "FALLIBILITY.md",
            "src/core/maxwell_kk_reduction.py",
        ],
        "status": "DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN",
    },
    "maxwell_kk_reduction": {
        "topic": "Maxwell KK reduction / physical-time test-field evolution / orbifold photon limits",
        "match_terms": ["maxwell", "maxwell_kk_reduction", "maxwelltestfieldstate"],
        "answer": (
            "The separate MaxwellTestFieldState API evolves source-free electric "
            "and magnetic fields in physical Einstein-frame coordinate time on a "
            "prescribed Minkowski background with positive constant radion and "
            "circle vector zero mode, on one periodic spatial coordinate. The "
            "action weight is λ²φ₀³; centered spatial differences and RK4 evolve "
            "the fields, while discrete Gauss constraints and energy are measured. "
            "This is a test-field approximation, not self-consistent coupled "
            "Einstein/radion evolution: Maxwell stress still sources gravity, and "
            "generic fields source the radion through F². The standard metric "
            "orbifold projects out the odd vector zero mode; neither this circle "
            "solver nor the assumed independent U(1) coupling illustration "
            "identifies the observed photon or derives α_em. The action/evolution "
            "contract remains DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN; no pillar, "
            "hardgate or empirical-confirmation promotion is made."
        ),
        "sources": [
            "src/core/maxwell_kk_reduction.py",
            "docs/TRUTH_LAYER.md",
            "src/core/action_to_evolution_contract.py",
        ],
        "status": "PRESCRIBED_BACKGROUND_TEST_FIELD / OPEN_PHYSICAL_OBLIGATIONS",
    },
    "dark_matter": {
        "topic": "Dark matter model — imposed halos and KK relic benchmarks",
        "match_terms": ["dark matter", "dark_matter", "dm", "halo", "halos", "relic"],
        "answer": (
            "The dark matter modules are scoped models, not an established "
            "dark-matter explanation. dark_matter_geometry retains a "
            "phenomenological, gauge-dependent B² halo prescription; it is not "
            "reduced-action stress-energy or a solution showing halo formation. "
            "The massless reduced-action gauge energy depends on F=dB, so a "
            "constant potential or a locally pure-gauge radial one-form has zero "
            "gauge energy. dark_matter_kk uses a hot-relic parametrization; its "
            "legacy viability flag only checks non-overproduction, not the full "
            "abundance or structure formation. Pillar 714 is a toy WIMP freeze-out "
            "benchmark with supplied mass and coupling, not geometric derivations "
            "or a solved thermal history. These distinct models must not be "
            "combined into a claim of dark-matter closure."
        ),
        "sources": [
            "src/core/dark_matter_geometry.py",
            "src/core/dark_matter_kk.py",
            "src/core/pillar714_kk_dark_matter_relic_density.py",
        ],
        "status": "PHENOMENOLOGICAL_MODELS / OPEN_PHYSICAL_EXPLANATION",
    },
    "photon_origin": {
        "topic": "Photon origin under Z₂ orbifold parity",
        "match_terms": ["photon", "photons", "photon_origin"],
        "answer": (
            "Photon origin remains OPEN under the stated Z₂ orbifold assumptions. "
            "The metric vector G_mu5 and B_mu are odd: a regular odd field "
            "vanishes at both fixed planes and has no constant massless zero mode. "
            "Multiplication by a finite even radion cannot restore it; the old "
            "fixed-plane composite-photon argument is withdrawn. A circle "
            "reduction permits a gauge connection but does not resolve this "
            "orbifold obstruction. An independent even gauge field, justified "
            "boundary gauge sector or different compactification would need its "
            "own action, boundary conditions and demonstrated massless mode."
        ),
        "sources": ["1-THEORY/Z2_PARITY_NOTE.md", "docs/TRUTH_LAYER.md"],
        "status": "OPEN_GAP — ORBIFOLD_PHOTON_ORIGIN",
    },
    "litebird": {
        "topic": "LiteBIRD falsification timeline",
        "answer": (
            "LiteBIRD is the primary falsifier for the Unitary Manifold. Launch ~2032, "
            "first results ~2034. It will measure CMB polarisation birefringence β to "
            "precision ~0.1°. Falsification condition: β ∉ [0.22°, 0.38°] OR "
            "β ∈ [0.29°, 0.31°] (the predicted gap between the two UM modes). "
            "See docs/LITEBIRD_FALSIFIER_BRIEF.md for the full protocol."
        ),
        "sources": ["docs/LITEBIRD_FALSIFIER_BRIEF.md", "docs/TRUTH_LAYER.md"],
        "status": "PENDING — launch ~2032",
    },
    "cosmological_constant": {
        "topic": "Cosmological constant / dark energy",
        "match_terms": ["cosmological constant", "cosmological_constant", "dark energy", "vacuum energy"],
        "answer": (
            "The historical RS1/flux model quotes a conditional reduction of "
            "the cosmological-constant hierarchy from 10^{122} to 10^{58}, "
            "and a landscape count ~10^{74} for the assumed N_flux=37. "
            "Counting candidate vacua does not derive the observed vacuum or "
            "its selection. The cited module explicitly describes the "
            "Bousso-Polchinski selection as anthropic/probabilistic, not a "
            "first-principles result from the UM action. This remains an "
            "exploratory completion, not a solved cosmological constant or "
            "empirically confirmed dark-energy model; current scope is bounded "
            "by docs/TRUTH_LAYER.md."
        ),
        "sources": [
            "src/tend/cc_architecture_limit.py",
            "src/core/pillar206_cosmological_constant.py",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "EXPLORATORY_VACUUM_SELECTION / OPEN_GAP",
    },
    "desi": {
        "topic": "DESI dark energy tension",
        "match_terms": ["desi"],
        "answer": (
            "The historical DESI DR2 comparison uses w₀ = −0.838 ± 0.072 "
            "and wₐ = −0.62 ± 0.30. The legacy model quotes w₀ ≈ −0.9302 "
            "and wₐ = 0, but kk_de_wa_cpl.py warns that the former is an "
            "inflationary-epoch expression, not a derived late-time dark-energy "
            "value; the two claims cannot both follow from the frozen-radion "
            "mechanism. The historical wₐ discrepancy is about 2.1σ. "
            "This remains an open model/observational tension, not confirmation. "
            "The local monitor is a comparison harness, not a live data fetch "
            "or evidence that later DESI results have resolved the issue."
        ),
        "sources": [
            "src/core/kk_de_wa_cpl.py", "src/core/desi_year3_monitor.py", "docs/TRUTH_LAYER.md",
        ],
        "status": "HONEST_OPEN_PROBLEM",
    },
    "alpha_gut": {
        "topic": "GUT coupling α_GUT = N_c/K_CS derivation",
        "answer": (
            "The historical 5D SU(N_c) CS argument quotes "
            "α_GUT = N_c/K_CS = 3/74 ≈ 0.0405 under its gauge-bundle, "
            "quantization and normalization assumptions. This numerical "
            "relation is not an independently established coupling derivation "
            "from the metric alone. Current foundation reassessment states that "
            "spatial orbifold reflection does not choose an internal SU(5) "
            "involution or recover the missing photon. The physical gauge-sector "
            "identification remains unresolved; no purity or completion claim "
            "is inferred from the historical modules' labels."
        ),
        "sources": [
            "src/core/alpha_gut_cs_derivation.py",
            "src/core/alpha_gut_su5_complete.py",
            "FALLIBILITY.md",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_CONDITIONAL_RELATION / OPEN_GAP",
    },
    "neutrino_masses": {
        "topic": "Neutrino mass splittings",
        "answer": (
            "Historical T²/Z₃ overlap models assume a torsion split "
            "Δc₀₁ = 1/(2K_CS) = 1/148. A common seed can cancel from a "
            "splitting ratio within that model without deriving the absolute "
            "mass scale or the assumed bulk-mass spectrum. The atmospheric "
            "2NLO module quotes a residual ~6.87%, versus its 7.26% NLO "
            "baseline; these are historical conditional estimates, not new "
            "verification. Current flavor identifiability remains unresolved: "
            "parity alone does not fix bulk masses and overlaps, as documented "
            "in docs/TRUTH_LAYER.md."
        ),
        "sources": [
            "src/sixd/solar_splitting_6dplus.py",
            "src/sixd/neutrino_dm31_2nlo.py",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_CONDITIONAL_ESTIMATES / OPEN_GAP",
    },
    "roadmap_v10_18": {
        "topic": "v10.18 roadmap and delivery status",
        "answer": (
            "v10.18 is a historical roadmap record, not the current scientific "
            "status. It records parameter-estimate updates and delivery of "
            "CMB-S4/DUNE/Hyper-K/JUNO monitor harnesses plus RAG expansion. "
            "Those historical labels do not establish present derivation or "
            "empirical confirmation; current scope is controlled by the "
            "foundation reassessment in docs/TRUTH_LAYER.md."
        ),
        "sources": ["docs/mas_tracker.yml", "docs/TRUTH_LAYER.md"],
        "status": "HISTORICAL_ROADMAP_RECORD",
    },
    "monitor_matrix": {
        "topic": "Machine-readable monitor matrix",
        "answer": (
            "Cross-experiment monitor outputs are aggregated in "
            "src/core/experiment_monitor_matrix.py. The bundle combines CMB-S4, DUNE, "
            "Hyper-K/JUNO, and DESI reports, and emits binary hard-gate routing "
            "(pass→freeze, fail→targeted ticket) in machine-readable form."
        ),
        "sources": [
            "src/core/experiment_monitor_matrix.py",
            "src/core/cmbs4_monitor.py",
            "src/core/dune_dcp_monitor.py",
            "src/core/hyperk_juno_monitor.py",
            "src/core/desi_year3_monitor.py",
        ],
        "status": "v10.18 monitor bundle",
    },
    "proton_electron_ratio": {
        "topic": "Proton-electron mass ratio m_p/m_e",
        "answer": (
            "The historical conditional ratio formula "
            "m_p/m_e = K_CS²/N_c = 74²/3 ≈ 1825.3 is about 0.59% below "
            "the cited comparison 1836.15. The module quotes an "
            "O(1/πkR) ≈ 2.7% correction scale and cancellation of C_lat "
            "within that ansatz; an order estimate is not by itself a rigorous "
            "remainder bound or derivation of physical proton/electron masses. "
            "Current foundation and flavor assumptions require reassessment "
            "under docs/TRUTH_LAYER.md. Numerical proximity is not independent "
            "empirical confirmation."
        ),
        "sources": [
            "src/core/mp_me_geometric_prediction.py",
            "src/core/pillar202_mp_me_lattice_free.py",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_CONDITIONAL_ESTIMATE / OPEN_GAP",
    },
    "sin2_theta_w": {
        "topic": "sin²θ_W electroweak mixing angle P4",
        "answer": (
            "Assuming the SU(5) embedding and chosen internal orbifold "
            "involution, the historical calculation uses "
            "sin²θ_W(M_GUT) = 3/8 and quotes one-loop running from "
            "M_GUT ≈ 10^13 GeV to sin²θ_W(M_Z) ≈ 0.2313 "
            "(comparison 0.23122). This is a conditional model estimate. "
            "The foundation reassessment states that spatial reflection "
            "does not select SU(5) or its internal involution; n_w=5 "
            "does not supply that missing physical identification."
        ),
        "sources": [
            "src/core/sin2_theta_w_geometric.py",
            "src/core/sm_free_parameters.py",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_CONDITIONAL_ESTIMATE / OPEN_GAP",
    },
    "higgs_vev": {
        "topic": "Higgs VEV v = 246 GeV P6",
        "answer": (
            "The historical Higgs VEV model uses λ_H^tree = 25/148, "
            "M_KK ≈ 1042 GeV and a top-Yukawa/RGE prescription. Its "
            "documentation quotes λ_eff ≈ 0.130 and v ≈ 245.96 GeV "
            "versus 246.22 GeV; these are conditional historical estimates, "
            "not a newly evaluated result. higgs_vev_exact.py explicitly "
            "notes that m_H is a PDG input (or comes from a chain using "
            "PDG VEV/top-mass inputs). Iteration does not remove that "
            "dependence. Independent joint UV/Higgs predictivity remains "
            "unresolved under docs/TRUTH_LAYER.md."
        ),
        "sources": [
            "src/core/higgs_vev_exact.py", "src/core/higgs_vev_upgrade_p6.py", "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_INPUT_DEPENDENT_ESTIMATE / OPEN_GAP",
    },
    "alpha_em": {
        "topic": "Fine structure constant alpha α P13",
        "answer": (
            "The historical module quotes α_em(0) ≈ 1/137.0 "
            "(comparison 1/137.036), conditional on α_GUT = 3/74 "
            "and an SU(5) running/matching prescription. Its source states "
            "that 137.0 is a quoted chain value; the close comparison does "
            "not independently derive the assumed gauge bundle or "
            "normalization. Current foundation reassessment retains the "
            "orbifold photon obstruction and conditional internal gauge "
            "selection. This is not an unconditional metric-derived or "
            "empirically confirmed fine-structure constant."
        ),
        "sources": [
            "src/core/alpha_em_geometric.py",
            "src/core/alpha_gut_cs_derivation.py",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_CONDITIONAL_ESTIMATE / OPEN_GAP",
    },
    "cmbs4": {
        "topic": "CMB-S4 predictions falsification",
        "answer": (
            "The historical CMB-S4 monitor uses conditional targets "
            "n_s = 0.9635 and r = 0.0315, comparing against "
            "Planck 0.9649±0.0042 and a BICEP/Keck upper limit 0.036. "
            "Its configured falsifiers remain n_s ∉ [0.955, 0.972] "
            "at σ<0.001, or r < 0.010 at >3σ. Its ~2030 date and "
            "sensitivities σ(n_s)≈0.002, σ(r)≈0.001 are historical "
            "forecasts, not a checked current project schedule. This local "
            "harness does not supply new observations or resolve the "
            "foundation and CMB-normalization obligations in docs/TRUTH_LAYER.md."
        ),
        "sources": ["src/core/cmbs4_monitor.py", "docs/TRUTH_LAYER.md"],
        "status": "PENDING — HISTORICAL_MONITOR_FORECAST",
    },
    "dune": {
        "topic": "DUNE delta CP leptonic CP violation",
        "answer": (
            "Historical DUNE monitor text quotes δ_CP ≈ 1.216 rad "
            "against a stored comparison 1.20 ± 0.20 rad. That quote "
            "disagrees with its executable constant π/3 + (9/74)×0.05, "
            "so it must not be treated as a verified phase prediction. "
            "The configured falsifier remains δ_CP ∉ [0.85, 1.30] rad "
            "at < 3% uncertainty. The ~2028–2032 dates and ~0.05 rad "
            "sensitivity are historical forecasts, not checked current "
            "schedule or observational evidence. An independent physical "
            "derivation remains unresolved under the current foundation boundary."
        ),
        "sources": [
            "src/core/dune_dcp_monitor.py", "src/nined/cp_phase_9d_refinement.py", "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_MONITOR_ESTIMATE / OPEN_GAP",
    },
    "yukawa_hierarchy": {
        "topic": "Yukawa hierarchy top bottom tau electron",
        "answer": (
            "Historical wavefunction-overlap models can reproduce a large "
            "Yukawa hierarchy using chosen bulk masses; their documentation "
            "quotes πkR = 37 and Δc_L ≈ 0.17 for a top/electron hierarchy "
            "of order 10^5. That is a conditional mechanism estimate, not "
            "selection of the mass parameters. Current foundation "
            "reassessment exhibits a continuum of normalizable profiles: "
            "parity selects chirality, not discrete bulk masses. Additional "
            "mass-fixing equations and overlaps are needed; first-principles "
            "flavor identifiability remains unresolved."
        ),
        "sources": [
            "src/sixd/yukawa_hierarchy_6d.py",
            "src/core/fermion_cL_spectrum_6d_audit.py",
            "docs/TRUTH_LAYER.md",
        ],
        "status": "HISTORICAL_OVERLAP_MODEL / OPEN_GAP",
    },
    "pillar102": {
        "topic": "Pillar 102 gravitational waves brane dynamics",
        "answer": (
            "Pillar 102 explores conditional brane/KK gravitational-wave "
            "estimates. Its historical benchmark uses M_KK ≈ 1042 GeV, "
            "a collision frequency of order 10^26 Hz and radion mass "
            "≈ 70 GeV, far from current LISA/LIGO collision-frequency bands. "
            "Those model formulas do not independently establish a physical "
            "source population, detectability or a completed higher-dimensional "
            "theory. Their present derivation status is unresolved under "
            "docs/TRUTH_LAYER.md's foundation boundary; no new GW result "
            "is reported here."
        ),
        "sources": [
            "src/core/pillar102_brane_gw.py", "src/core/kk_gw_background.py", "docs/TRUTH_LAYER.md",
        ],
        "status": "EXPLORATORY_GW_BENCHMARK / OPEN_GAP",
    },
    "trusted_open_resources": {
        "topic": "Trusted open research resources (Pillar 258)",
        "answer": (
            "Pillar 258 adds a deterministic registry of 100 trusted, free online "
            "research resources grouped across seven categories: academic literature, "
            "open data/statistics, government/public agency portals, digital libraries, "
            "open-source technology repositories, life-science registries, and "
            "fact-checking/legal archives. The registry includes topic-aware source "
            "suggestion and AI prompt-building helpers for repository research workflows."
        ),
        "sources": [
            "src/core/pillar258_trusted_open_resource_registry.py",
            "5-GOVERNANCE/Unitary Pentad/pentad_research_resource_gateway.py",
            "bot/research_resources.py",
        ],
        "status": "ADJACENT TRACK (non-hardgate)",
    },
}


def _normalize_token(token: str) -> str:
    token = token.strip().lower()
    return _TOKEN_ALIASES.get(token, token)


def _normalize_positive_limit(value: Any, default: int) -> int:
    try:
        return max(1, int(default if value is None else value))
    except (TypeError, ValueError):
        return max(1, int(default))


def _tokenize(text: str) -> Set[str]:
    return {
        _normalize_token(token)
        for token in re.findall(r"\w+", text.lower())
        if token.strip()
    }


def _query_tokens(text: str) -> Set[str]:
    return _tokenize(text) - _QUERY_NOISE


def _current_document_text(source: str, text: str) -> str:
    """Exclude superseded sprint narratives from the current truth-layer index."""
    if source != "docs/TRUTH_LAYER.md":
        return text
    selected = []
    active_level = None
    fence = None
    for line in text.splitlines(keepends=True):
        fence_match = re.match(r"^[ \t]*(`{3,}|~{3,})", line)
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1]:
                fence = None
        elif fence is None:
            heading_match = re.match(r"^(#{1,6})[ \t]+(.+?)\s*$", line)
            if heading_match:
                level = len(heading_match.group(1))
                if active_level is not None and level <= active_level:
                    active_level = None
                if (level, heading_match.group(2)) in _CURRENT_TRUTH_SECTIONS:
                    active_level = level
        if active_level is not None:
            selected.append(line)
    return "".join(selected)


def _matches_lane_keyword(query_tokens: Set[str], normalized_query: str, keyword: str) -> bool:
    normalized_keyword = str(keyword or "").strip().lower()
    if not normalized_keyword:
        return False
    if " " in normalized_keyword:
        pattern = r"\b" + re.escape(normalized_keyword).replace(r"\ ", r"[\s-]+") + r"\b"
        return re.search(pattern, normalized_query) is not None
    return _normalize_token(normalized_keyword) in query_tokens


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _extract_latest_wave(repo_root: Path) -> Optional[str]:
    changelog = _safe_read_text(repo_root / "docs/WAVE_CHANGELOG.md")
    match = re.search(r"^##\s+(v[0-9.]+)\b", changelog, re.MULTILINE)
    return match.group(1) if match else None


def _extract_latest_changelog_entry(repo_root: Path) -> Optional[str]:
    changelog = _safe_read_text(repo_root / "docs/WAVE_CHANGELOG.md")
    match = re.search(r"^##[ \t]+([^\n]+)", changelog, re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_status_header(repo_root: Path) -> Optional[str]:
    status = _safe_read_text(repo_root / "STATUS.md")
    match = re.search(
        r"^[ \t]*(?:\*{1,2}|#{1,6}[ \t]+)(?:Unitary Manifold[ \t]+)?"
        r"(v[0-9]+(?:\.[0-9]+)+\b[^\n]*)",
        status,
        re.MULTILINE,
    )
    return match.group(1).rstrip("*").strip() if match else None


def _extract_latest_regression(repo_root: Path) -> Optional[str]:
    # A missing receipt in the current marker must not fall through to old sprints.
    status = _extract_status_header(repo_root)
    if status is None:
        status = _safe_read_text(repo_root / "STATUS.md")
    match = re.search(
        r"Latest verified (?:full regression in current branch history|branch regression)"
        r"(?::|[ \t]+remains)[ \t]*([^\n]+)",
        status,
    )
    if match and re.search(r"\b[0-9][0-9,]*[ \t]+passed\b", match.group(1)):
        return match.group(1).strip()
    return None


def build_runtime_knowledge_base(repo_root: Optional[Path] = None) -> Dict[str, Dict]:
    """Merge static facts with lightweight runtime facts from canonical ledgers."""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent

    kb = dict(KNOWLEDGE_BASE)
    latest_wave = _extract_latest_wave(repo_root)
    latest_entry = _extract_latest_changelog_entry(repo_root)
    status_header = _extract_status_header(repo_root)
    latest_regression = _extract_latest_regression(repo_root)

    if latest_entry or latest_wave or status_header:
        answer_parts = []
        if latest_entry:
            answer_parts.append(f"Latest entry in docs/WAVE_CHANGELOG.md: {latest_entry}.")
        if latest_wave:
            answer_parts.append(f"Latest versioned wave in docs/WAVE_CHANGELOG.md: {latest_wave}.")
        if status_header:
            answer_parts.append(f"STATUS.md version marker (historical narrative): {status_header.rstrip('.')}.")
        answer_parts.append("These ledger records do not establish new execution or physical closure.")
        kb["repo_state"] = {
            "topic": "Current repository wave and status snapshot",
            "match_terms": ["repository", "repo", "wave"],
            "answer": " ".join(answer_parts),
            "sources": ["docs/WAVE_CHANGELOG.md", "STATUS.md"],
            "status": latest_wave or status_header or "AVAILABLE",
        }

    if latest_regression:
        kb["latest_regression"] = {
            "topic": "Historical branch regression baseline",
            "answer": (
                f"Historical baseline recorded in STATUS.md: {latest_regression.rstrip('.')}. "
                "This is not evidence of new execution or successful verification "
                "of the current changes."
            ),
            "sources": ["STATUS.md"],
            "status": "HISTORICAL_BASELINE",
        }

    return kb


def _normalize_gate_label(status: str) -> str:
    sample = str(status or "").strip().upper()
    if "GOVERNANCE" in sample:
        return "GOVERNANCE"
    if "ADJACENT" in sample:
        return "ADJACENT_TRACK"
    if any(label in sample for label in (
        "OPEN_GAP", "HONEST_OPEN_PROBLEM", "EVOLUTION_LAW_OPEN", "OPEN_PHYSICAL",
    )):
        return "OPEN_GAP"
    if "ARCHITECTURE_LIMIT" in sample or "CONSTRAINED" in sample or "PENDING" in sample:
        return "ARCHITECTURE_LIMIT"
    if "DERIVED" in sample:
        return "DERIVED"
    if "GEOMETRIC_PREDICTION" in sample or "HARDGATE" in sample or "CERTIFIED" in sample:
        return "HARDGATE"
    return "ARCHITECTURE_LIMIT"


def detect_query_lane(query: str) -> Dict[str, str]:
    normalized_query = str(query or "").lower()
    query_tokens = _tokenize(query)
    best_lane = "physics_navigation"
    best_matches: list[str] = []
    best_rank = (0, 0, 0, _LANE_PRIORITY[best_lane])
    for lane_id, config in _LANE_HINTS.items():
        matched = sorted([
            keyword
            for keyword in config["keywords"]
            if _matches_lane_keyword(query_tokens, normalized_query, keyword)
        ])
        if not matched:
            continue
        lane_rank = (
            len(matched),
            max(len(keyword.split()) for keyword in matched),
            max(len(keyword) for keyword in matched),
            _LANE_PRIORITY.get(lane_id, 0),
        )
        if lane_rank > best_rank:
            best_lane = lane_id
            best_matches = matched
            best_rank = lane_rank
    matched_keywords = best_matches[:6]
    return {
        "lane_id": best_lane,
        "label": _LANE_HINTS[best_lane]["label"],
        "matched_keywords": ", ".join(matched_keywords) if matched_keywords else "none",
        "tool_bias": "structural_context_first",
    }


def _existing_source_path(repo_root: Path, source: str) -> Path | None:
    cleaned = str(source or "").strip()
    if not cleaned or "://" in cleaned:
        return None
    cleaned = cleaned.split(" §", 1)[0].strip()
    cleaned = cleaned.split(" line ", 1)[0].strip()
    candidate = repo_root / cleaned
    try:
        candidate.resolve().relative_to(repo_root.resolve())
        return candidate if candidate.is_file() else None
    except (OSError, RuntimeError, ValueError):
        return None


def _related_test_paths(repo_root: Path, path: Path) -> list[str]:
    candidates = [
        repo_root / "tests" / f"test_{path.stem}.py",
        path.with_name(f"test_{path.stem}.py"),
    ]
    seen: list[str] = []
    for candidate in candidates:
        if candidate.exists():
            rel = candidate.relative_to(repo_root).as_posix()
            if rel not in seen:
                seen.append(rel)
    return seen[:3]


def _build_ast_hint(repo_root: Path, path: Path) -> dict[str, Any] | None:
    if path.suffix != ".py" or any(part in _AST_CONTEXT_SKIP_PARTS for part in path.parts):
        return None
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return None
    functions: list[str] = []
    classes: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
    if not functions and not classes:
        return None
    rel = path.relative_to(repo_root).as_posix()
    return {
        "path": rel,
        "module_doc_excerpt": (ast.get_docstring(tree) or "").strip()[:180],
        "function_count": len(functions),
        "class_count": len(classes),
        "function_names": functions[:12],
        "class_names": classes[:12],
        "symbol_density": len(functions) + len(classes),
        "related_tests": _related_test_paths(repo_root, path),
    }


def build_context_scaffold(
    index: "RAGIndex",
    query: str,
    *,
    repo_root: Optional[Path] = None,
    top_k: int = 3,
    ast_file_limit: int = 3,
) -> Dict[str, Any]:
    if repo_root is None:
        repo_root = Path(__file__).parent.parent
    lane = detect_query_lane(query)
    kb_entry = index.lookup_kb(query)
    retrieval_results = index.search(query, top_k=top_k)
    top_chunks = [
        {
            "score": round(float(score), 4),
            "source": chunk.source,
            "title": chunk.title,
            "excerpt": chunk.text[:220],
        }
        for score, chunk in retrieval_results
        if score > 0.0
    ]
    provenance_sources: list[dict[str, Any]] = []
    seen_provenance_labels: set[str] = set()
    seen_paths: set[str] = set()
    candidate_paths: list[Path] = []

    def append_provenance(label: str, *, kind: str, gate: str, confidence_tier: str = "retrieved") -> None:
        if label in seen_provenance_labels:
            return
        seen_provenance_labels.add(label)
        provenance_sources.append({
            "label": label,
            "path": label,
            "kind": kind,
            "gate": gate,
            "confidence_tier": confidence_tier,
        })

    if kb_entry is not None:
        gate = _normalize_gate_label(kb_entry.get("status", ""))
        for source in kb_entry.get("sources", [])[:6]:
            label = str(source)
            append_provenance(label, kind="knowledge_base", gate=gate, confidence_tier="curated_navigation")
            real_path = _existing_source_path(repo_root, label)
            if real_path is not None and real_path.as_posix() not in seen_paths:
                candidate_paths.append(real_path)
                seen_paths.add(real_path.as_posix())
    for item in top_chunks:
        label = str(item["source"])
        append_provenance(label, kind="document_chunk", gate="ARCHITECTURE_LIMIT")
        real_path = _existing_source_path(repo_root, label)
        if real_path is not None and real_path.as_posix() not in seen_paths:
            candidate_paths.append(real_path)
            seen_paths.add(real_path.as_posix())
    ast_limit = _normalize_positive_limit(ast_file_limit, 3)
    ast_hints: list[dict[str, Any]] = []
    for path in candidate_paths:
        hint = _build_ast_hint(repo_root, path)
        if hint is not None:
            ast_hints.append(hint)
            if len(ast_hints) >= ast_limit:
                break
    normalized_gates = [
        *([_normalize_gate_label(kb_entry.get("status", ""))] if kb_entry is not None else []),
        *[item["gate"] for item in provenance_sources if item.get("gate")],
    ]
    gate_candidates = {gate for gate in normalized_gates if gate}
    dominant_gate = sorted(
        gate_candidates,
        key=lambda item: (-_GATE_PRIORITY.get(item, -1), item),
    )[0] if gate_candidates else "ARCHITECTURE_LIMIT"
    guardrails = {
        "context_role": "architectural_scaffold",
        "do_not_treat_as": "raw_core_memory_dump",
        "keep_primary_model_focus": "reason_over_scoped_context_only",
        "dominant_gate": dominant_gate,
        "gate_semantics": "navigation_labels_not_source_verification",
        "not_scientific_certification": True,
    }
    return {
        "schema_version": "rag_context_scaffold_v1",
        "query": str(query or ""),
        "lane": lane,
        "boundary": {
            "dominant_gate": dominant_gate,
            "guardrails": guardrails,
        },
        "retrieval": {
            "knowledge_match": (
                {
                    "topic": kb_entry.get("topic", ""),
                    "status": kb_entry.get("status", ""),
                    "answer": kb_entry.get("answer", ""),
                    "sources": list(kb_entry.get("sources", [])),
                }
                if kb_entry is not None
                else None
            ),
            "top_chunks": top_chunks,
        },
        "ast": {
            "enabled": bool(ast_hints),
            "file_limit": ast_limit,
            "record_count": len(ast_hints),
            "symbol_count_total": sum(int(item["symbol_density"]) for item in ast_hints),
            "files": ast_hints,
        },
        "tooling": {
            "suggested_endpoints": list(_LANE_HINTS.get(lane["lane_id"], {}).get("tool_hints", [])),
            "ast_file_limit": ast_limit,
            "retrieval_mode": "scaffold_before_generation",
        },
        "provenance": {
            "source_count": len(provenance_sources),
            "sources": provenance_sources[:10],
        },
    }


def render_context_scaffold(scaffold: Dict[str, Any]) -> str:
    lane = dict(scaffold.get("lane") or {})
    boundary = dict(scaffold.get("boundary") or {})
    retrieval = dict(scaffold.get("retrieval") or {})
    ast_payload = dict(scaffold.get("ast") or {})
    tooling = dict(scaffold.get("tooling") or {})
    lines = [
        "[CONTEXT SCAFFOLD]",
        f"Lane: {lane.get('lane_id', 'unknown')} | {lane.get('label', '')}",
        f"Matched keywords: {lane.get('matched_keywords', 'none')}",
        f"Dominant gate: {boundary.get('dominant_gate', 'ARCHITECTURE_LIMIT')}",
        "Role: architectural scaffold; not a raw memory dump.",
        "Gate labels and citations are navigation metadata, not source verification or scientific certification.",
    ]
    kb_match = retrieval.get("knowledge_match")
    if isinstance(kb_match, dict):
        lines.extend([
            "",
            "[KNOWLEDGE BASE MATCH]",
            f"Topic: {kb_match.get('topic', '')}",
            f"Status: {kb_match.get('status', '')}",
            f"Answer: {kb_match.get('answer', '')}",
            f"Sources: {', '.join(kb_match.get('sources', []))}",
        ])
    chunks = list(retrieval.get("top_chunks") or [])
    if chunks:
        lines.append("")
        lines.append("[RETRIEVAL HITS]")
        for item in chunks[:3]:
            lines.append(
                f"- {item.get('source', '')} | score={float(item.get('score', 0.0)):.3f} | {item.get('title', '')}"
            )
    ast_files = list(ast_payload.get("files") or [])
    if ast_files:
        lines.append("")
        lines.append("[AST STRUCTURE]")
        for item in ast_files[:3]:
            fn_names = ",".join(item.get("function_names", [])[:6]) or "none"
            cls_names = ",".join(item.get("class_names", [])[:4]) or "none"
            lines.append(
                f"- {item.get('path', '')} | fn={item.get('function_count', 0)} [{fn_names}] | "
                f"cls={item.get('class_count', 0)} [{cls_names}]"
            )
    endpoints = list(tooling.get("suggested_endpoints") or [])
    if endpoints:
        lines.extend([
            "",
            "[TOOL/RUNTIME HINTS]",
            f"Suggested endpoints: {', '.join(endpoints)}",
            f"AST file limit: {tooling.get('ast_file_limit', 0)}",
        ])
    return "\n".join(lines)


class DocumentChunk:
    """A searchable chunk of text from the repository."""

    __slots__ = ("source", "title", "text", "text_lower", "tokens", "title_tokens")

    def __init__(self, source: str, title: str, text: str) -> None:
        self.source = source
        self.title = title
        self.text = text
        self.text_lower = text.lower()
        self.tokens = _tokenize(" ".join((source, title, text)))
        self.title_tokens = _tokenize(title)

    def score(self, query_tokens: set, query_text: str = "") -> float:
        """TF-IDF-like score: fraction of query tokens present in chunk."""
        if not query_tokens:
            return 0.0
        matches = query_tokens & self.tokens
        title_matches = query_tokens & self.title_tokens
        base = len(matches) / len(query_tokens)
        title_bonus = TITLE_BONUS_WEIGHT * len(title_matches) / len(query_tokens)
        phrase_bonus = PHRASE_MATCH_BONUS if query_text and query_text in self.text_lower else 0.0
        return min(1.0, base + title_bonus + phrase_bonus)


class RAGIndex:
    """Lightweight keyword-based retrieval index for the UM repository.

    Attributes
    ----------
    chunks : list of DocumentChunk
        All indexed text chunks.
    knowledge_base : dict
        Structured fact entries (always available).
    """

    def __init__(
        self,
        chunks: Optional[List[DocumentChunk]] = None,
        knowledge_base: Optional[Dict] = None,
    ) -> None:
        self.chunks: List[DocumentChunk] = chunks or []
        self.knowledge_base: Dict = knowledge_base or build_runtime_knowledge_base()

    @classmethod
    def build(
        cls,
        repo_root: Optional[Path] = None,
        max_chunk_chars: int = 1500,
    ) -> "RAGIndex":
        """Build an index from the repository.

        Parameters
        ----------
        repo_root : Path, optional
            Root of the repository.  Defaults to two levels up from this file.
        max_chunk_chars : int
            Maximum characters per chunk.

        Returns
        -------
        RAGIndex
        """
        if repo_root is None:
            repo_root = Path(__file__).parent.parent

        chunks: List[DocumentChunk] = []

        # Index key documents
        target_files = [
            ("README.md", "README"),
            ("FALLIBILITY.md", "Fallibility / Limitations"),
            ("STATUS.md", "Pillar Status Registry"),
            ("docs/LITEBIRD_FALSIFIER_BRIEF.md", "LiteBIRD Falsifier Brief"),
            ("1-THEORY/UNIFICATION_PROOF.md", "Historical unification argument — scoped by current reassessment"),
        ] + _FOUNDATION_DOCUMENTS

        for rel_path, title in target_files:
            full_path = repo_root / rel_path
            if full_path.exists():
                try:
                    text = full_path.read_text(encoding="utf-8", errors="replace")
                    text = _current_document_text(rel_path, text)
                    # Split into chunks
                    for i in range(0, len(text), max_chunk_chars):
                        chunk_text = text[i: i + max_chunk_chars]
                        chunks.append(DocumentChunk(rel_path, title, chunk_text))
                except OSError:
                    pass

        return cls(chunks=chunks, knowledge_base=build_runtime_knowledge_base(repo_root))

    @classmethod
    def build_intent_index(
        cls,
        repo_root: Optional[Path] = None,
        max_chunk_chars: int = 1500,
    ) -> "RAGIndex":
        """Build an index weighted toward session-intent memory sources.

        Includes HILS_SESSION_CURRENT.md and HILS_SESSION_LOG.md in addition
        to the standard document set, giving priority to the session-history
        files for intent-continuity queries.

        Parameters
        ----------
        repo_root : Path, optional
            Root of the repository.  Defaults to two levels up from this file.
        max_chunk_chars : int
            Maximum characters per chunk.

        Returns
        -------
        RAGIndex with intent-weighted chunks.
        """
        if repo_root is None:
            repo_root = Path(__file__).parent.parent

        chunks: List[DocumentChunk] = []

        # Intent-memory sources (indexed first so they rank higher on ties)
        intent_sources = [
            ("HILS_SESSION_CURRENT.md", "Session Current State (identity/intent/open-loops)"),
            ("HILS_SESSION_LOG.md", "Session History Log (append-only intent trail)"),
            ("5-GOVERNANCE/co-emergence/LLM_INGEST.md", "HILS Co-emergence Framework"),
            ("5-GOVERNANCE/co-emergence/INTENT_LAYER.md", "HILS Intent Layer"),
            ("5-GOVERNANCE/co-emergence/TRUST_PROTOCOL.md", "HILS Trust Protocol"),
        ]

        # Standard physics/governance sources
        standard_sources = [
            ("README.md", "README"),
            ("FALLIBILITY.md", "Fallibility / Limitations"),
            ("STATUS.md", "Pillar Status Registry"),
            ("SEPARATION.md", "Epistemic Separation Boundary"),
            ("docs/WAVE_CHANGELOG.md", "Wave Changelog — historical records, not current proof"),
            ("docs/LITEBIRD_FALSIFIER_BRIEF.md", "LiteBIRD Falsifier Brief"),
            ("1-THEORY/UNIFICATION_PROOF.md", "Historical unification argument — scoped by current reassessment"),
            ("6-MONOGRAPH/MCP_INGEST.md", "MCP Ingest (full repo summary)"),
        ] + _FOUNDATION_DOCUMENTS

        for rel_path, title in intent_sources + standard_sources:
            full_path = repo_root / rel_path
            if full_path.exists():
                try:
                    text = full_path.read_text(encoding="utf-8", errors="replace")
                    text = _current_document_text(rel_path, text)
                    for i in range(0, len(text), max_chunk_chars):
                        chunk_text = text[i: i + max_chunk_chars]
                        chunks.append(DocumentChunk(rel_path, title, chunk_text))
                except OSError:
                    pass

        return cls(chunks=chunks, knowledge_base=build_runtime_knowledge_base(repo_root))

    def search(self, query: str, top_k: int = 5) -> List[Tuple[float, DocumentChunk]]:
        """Search for the most relevant chunks.

        Parameters
        ----------
        query : str  The natural-language query.
        top_k : int  Number of results to return.

        Returns
        -------
        list of (score, DocumentChunk) sorted by descending score.
        """
        query_tokens = _query_tokens(query)
        query_text = query.lower().strip()
        scored = [
            (min(1.0, chunk.score(query_tokens, query_text) * _source_weight(chunk.source)), chunk)
            for chunk in self.chunks
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def lookup_kb(self, query: str) -> Optional[Dict]:
        """Match topic anchors, never incidental words in answers or citations.

        Returns the best matching KB entry, or None.
        """
        query_tokens = _query_tokens(query)
        query_text = query.lower().strip()
        best_score = 0.0
        best_entry = None
        for key, entry in self.knowledge_base.items():
            combined = " ".join([key, key.replace("_", " "), entry.get("topic", "")])
            match_terms = entry.get("match_terms")
            if match_terms is not None:
                matched = [
                    term for term in match_terms
                    if _matches_lane_keyword(query_tokens, query_text, term)
                ]
                if not matched:
                    continue
                topic_tokens = _query_tokens(combined + " " + " ".join(matched))
            else:
                topic_tokens = _query_tokens(combined)
            score = len(query_tokens & topic_tokens) / max(len(query_tokens), 1)
            if match_terms is not None:
                score += KB_PHRASE_MATCH_BONUS
            if query_text and query_text in combined.lower():
                score = min(1.0, score + KB_PHRASE_MATCH_BONUS)
            if score > best_score:
                best_score = score
                best_entry = entry
        if best_score > 0.15:  # threshold for KB match
            return best_entry
        return None


def answer_question(index: RAGIndex, query: str, top_k: int = 3) -> Dict:
    """Answer a question about the Unitary Manifold.

    First checks the structured knowledge base for a direct match.
    Falls back to retrieving the most relevant document chunks.

    Parameters
    ----------
    index : RAGIndex  The built index.
    query : str       Natural-language question.
    top_k : int       Number of context chunks to include.

    Returns
    -------
    dict with 'answer', 'source_type', 'context_chunks', and 'query'.
    """
    scaffold = build_context_scaffold(index, query, top_k=top_k)
    # Try KB lookup first
    kb_entry = index.lookup_kb(query)
    if kb_entry is not None:
        return {
            "query": query,
            "answer": kb_entry["answer"],
            "source_type": "knowledge_base",
            "topic": kb_entry.get("topic", ""),
            "status": kb_entry.get("status", ""),
            "sources": kb_entry.get("sources", []),
            "context_chunks": [],
            "context_scaffold": scaffold,
        }

    # Fall back to document retrieval
    results = index.search(query, top_k=top_k)
    if not results or results[0][0] < 0.05:
        return {
            "query": query,
            "answer": (
                "No highly relevant result found in the index. "
                "Please consult FALLIBILITY.md, STATUS.md, or docs/TRUTH_LAYER.md "
                "for comprehensive coverage of the Unitary Manifold framework."
            ),
            "source_type": "no_result",
            "context_chunks": [],
            "context_scaffold": scaffold,
        }

    context_chunks = [
        {"score": score, "source": chunk.source, "title": chunk.title, "excerpt": chunk.text[:300]}
        for score, chunk in results
        if score > 0.0
    ]

    # Build a simple answer from the top chunk
    top_chunk = results[0][1]
    answer = (
        f"Relevant excerpt from {top_chunk.source} ({top_chunk.title}):\n\n"
        + top_chunk.text[:600]
        + ("\n\n[...continued in source file]" if len(top_chunk.text) > 600 else "")
    )

    return {
        "query": query,
        "answer": answer,
        "source_type": "document_retrieval",
        "context_chunks": context_chunks,
        "sources": [chunk["source"] for chunk in context_chunks],
        "context_scaffold": scaffold,
    }


def build_default_index() -> RAGIndex:
    """Build the default RAG index from the repository root.

    Returns
    -------
    RAGIndex
    """
    return RAGIndex.build()


def build_intent_index() -> RAGIndex:
    """Build a session-intent-weighted RAG index from the repository root.

    Includes HILS_SESSION_CURRENT.md and HILS_SESSION_LOG.md so that intent
    queries receive session-history-aware answers.

    Returns
    -------
    RAGIndex
    """
    return RAGIndex.build_intent_index()


def retrieve_intent(
    index: RAGIndex,
    mode: str = "latest_intent",
) -> Dict:
    """Deterministic intent retrieval from the session-memory sources.

    Parameters
    ----------
    index : RAGIndex
        An intent-weighted index (from build_intent_index()).
    mode : str
        One of:
        - "latest_intent"   — Current strategic intent and open loops.
        - "long_arc_intent" — Persistent goals spanning multiple sessions.
        - "unresolved_intent" — Open loops not yet resolved.

    Returns
    -------
    dict with 'mode', 'answer', 'sources'.
    """
    _QUERIES: Dict[str, str] = {
        "latest_intent": (
            "current strategic intent active wave open loops next session"
        ),
        "long_arc_intent": (
            "persistent long term goal derivation track physics wave plan"
        ),
        "unresolved_intent": (
            "open loops unresolved pending trigger conditions next entry"
        ),
    }

    if mode not in _QUERIES:
        return {
            "mode": mode,
            "answer": f"Unknown mode '{mode}'. Choose from: {list(_QUERIES)}.",
            "sources": [],
        }

    snapshot = current_intent_snapshot()
    if mode == "latest_intent":
        intents = snapshot.get("strategic_intent", [])
        lines = [f"Active wave: {snapshot.get('active_wave', 'UNKNOWN')}"]
        if intents:
            lines.append("Current strategic intent:")
            lines.extend(f"- {item['intent']} ({item['status']})" for item in intents)
        if snapshot.get("unresolved_loops"):
            lines.append("Unresolved loops:")
            lines.extend(f"- {loop}" for loop in snapshot["unresolved_loops"])
        return {
            "mode": mode,
            "answer": "\n".join(lines),
            "sources": [{"source": source, "title": "session snapshot", "score": 1.0} for source in snapshot["sources"]],
        }

    if mode == "unresolved_intent":
        unresolved = snapshot.get("unresolved_loops", [])
        triggers = snapshot.get("next_triggers", [])
        if unresolved or triggers:
            lines = []
            if unresolved:
                lines.append("Unresolved loops:")
                lines.extend(f"- {loop}" for loop in unresolved)
            if triggers:
                lines.append("Next triggers:")
                lines.extend(f"- {trigger}" for trigger in triggers)
            return {
                "mode": mode,
                "answer": "\n".join(lines),
                "sources": [{"source": source, "title": "session snapshot", "score": 1.0} for source in snapshot["sources"]],
            }

    query = _QUERIES[mode]
    results = index.search(query, top_k=5)
    relevant = [(s, c) for s, c in results if s > 0.05]

    if not relevant:
        return {
            "mode": mode,
            "answer": "No intent data found. Ensure HILS_SESSION_CURRENT.md and HILS_SESSION_LOG.md are indexed.",
            "sources": [],
        }

    answer_parts = []
    sources = []
    for score, chunk in relevant:
        answer_parts.append(chunk.text[:400])
        sources.append({"source": chunk.source, "title": chunk.title, "score": round(score, 3)})

    return {
        "mode": mode,
        "answer": "\n\n---\n\n".join(answer_parts),
        "sources": sources,
    }


def _source_weight(source: str) -> float:
    lower = source.lower()
    if lower.startswith("hils_session_"):
        return HILS_SESSION_WEIGHT
    if lower.startswith("5-governance/co-emergence/"):
        return CO_EMERGENCE_WEIGHT
    if lower.startswith("docs/"):
        return DOCS_WEIGHT
    return 1.0
