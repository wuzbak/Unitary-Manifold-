# Copyright (C) 2026  ThomasCory Walker-Pearson
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

import os
import re
import math
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from bot.session_bootstrap import current_intent_snapshot

__all__ = [
    "RAGIndex",
    "DocumentChunk",
    "answer_question",
    "build_default_index",
    "build_intent_index",
    "retrieve_intent",
]

_TOKEN_ALIASES = {
    "β": "birefringence",
    "beta": "birefringence",
    "cmb": "cmb",
    "gut": "alpha_gut",
    "toe": "toe_score",
    "theory": "toe_score",
    "intent": "intent",
    "wave": "wave",
    "session": "intent",
    "radion": "radion",
}

# Intent/session sources should outrank generic documentation on tie-like matches
# because they represent the freshest operator-visible state.
HILS_SESSION_WEIGHT = 1.35
CO_EMERGENCE_WEIGHT = 1.20
DOCS_WEIGHT = 1.10
TITLE_BONUS_WEIGHT = 0.25
PHRASE_MATCH_BONUS = 0.15
KB_PHRASE_MATCH_BONUS = 0.20

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
        "answer": (
            "The winding number n_w = 5 is a pure theorem from 5D geometry (Pillar 70-D). "
            "The Z₂-odd CS boundary phase condition k_CS(n_w) × η̄(n_w) = odd integer "
            "selects n_w=5 (product=37, odd ✓) and excludes n_w=7 (product=0, even ✗). "
            "The Planck nₛ = 0.9649 ± 0.0042 confirms this at 0.33σ but is not the "
            "selection mechanism. n_w=5 is derived without observational input."
        ),
        "sources": ["src/core/nw5_pure_theorem.py", "FALLIBILITY.md §III"],
        "status": "DERIVED — pure theorem",
    },
    "alpha_s": {
        "topic": "Strong coupling α_s(M_Z)",
        "answer": (
            "α_s(M_Z) is P3 in the ToE table, currently ARCHITECTURE_LIMIT_CERTIFIED(10D). "
            "The 5D geometric chain gives α_s ≈ 0.095 (19% below PDG 0.1179). "
            "The 10D CY₃ + flux estimate closes the gap. "
            "Full closure requires WS-IV (CY₃ moduli + flux α_s 10D calculation)."
        ),
        "sources": ["src/core/alpha_s_forward_chain_audit.py", "docs/TOE_SCORE_AUDIT.md"],
        "status": "ARCHITECTURE_LIMIT_CERTIFIED(10D)",
    },
    "higgs_mass": {
        "topic": "Higgs mass m_H = 125.25 GeV",
        "answer": (
            "The Higgs mass is P5 in the ToE table, ARCHITECTURE_LIMIT_CERTIFIED(6D+). "
            "The 5D Goldberger-Wise mechanism gives the Higgs VEV v ≈ 257.6 GeV (4.6% residual). "
            "The Higgs mass itself (125.25 GeV) requires the brane-localised kinetic mixing "
            "θ_HR in the full 6D+ geometry (WS-I). The current 5D estimate gives ~125 GeV "
            "but cannot close to sub-percent without the full 6D brane-localised calculation."
        ),
        "sources": ["src/sixd/higgs_radion_full_geometry_6dplus.py", "docs/mas_tracker.yml"],
        "status": "ARCHITECTURE_LIMIT_CERTIFIED(6D+)",
    },
    "toe_score": {
        "topic": "ToE score — completeness",
        "answer": (
            "The canonical ToE / closure percentage is no longer maintained as a fixed "
            "hard-coded number inside the bot. Consult docs/mas_tracker.yml, STATUS.md, "
            "and docs/WAVE_CHANGELOG.md for the live % and the current wave-specific "
            "epistemic promotions."
        ),
        "sources": ["docs/mas_tracker.yml", "STATUS.md", "docs/WAVE_CHANGELOG.md"],
        "status": "CANONICAL_LEDGER_TRACKED",
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
        "sources": ["docs/LITEBIRD_FALSIFIER_BRIEF.md", "docs/TOE_SCORE_AUDIT.md"],
        "status": "PENDING — launch ~2032",
    },
    "cosmological_constant": {
        "topic": "Cosmological constant / dark energy",
        "answer": (
            "P28 (cosmological constant) is ARCHITECTURE_LIMIT_CERTIFIED(10D). "
            "RS1 reduces the problem from 10^{122} to 10^{58}. "
            "The 10D Bousso-Polchinski flux landscape with N_flux=37=K_CS/2 provides "
            "~10^{74} vacua that can in principle reach Λ_obs, but selection requires "
            "the full 10D supergravity effective action (beyond current 5D UM scope). "
            "See src/tend/cc_architecture_limit.py for the formal certificate."
        ),
        "sources": ["src/tend/cc_architecture_limit.py", "src/core/pillar206_cosmological_constant.py"],
        "status": "ARCHITECTURE_LIMIT_CERTIFIED(10D)",
    },
    "desi": {
        "topic": "DESI dark energy tension",
        "answer": (
            "DESI DR2 (2025) gives w₀ = −0.838 ± 0.072 and wₐ = −0.62 ± 0.30. "
            "The UM predicts w₀ = −0.9302 (1.3σ consistent) and wₐ = 0 (2.1σ tension). "
            "The wₐ=0 tension is an HONEST_OPEN_PROBLEM: the GW-stabilised radion gives "
            "wₐ < 10^{-80}, far too small to explain DESI. DESI Year 3 (~2026) will "
            "test whether the tension persists or resolves. See src/core/desi_year3_monitor.py."
        ),
        "sources": ["src/core/kk_de_wa_cpl.py", "src/core/desi_year3_monitor.py"],
        "status": "HONEST_OPEN_PROBLEM",
    },
    "alpha_gut": {
        "topic": "GUT coupling α_GUT = N_c/K_CS derivation",
        "answer": (
            "α_GUT = N_c/K_CS = 3/74 ≈ 0.0405 was previously 'POSTULATED BY CS ANALOGY'. "
            "The current closure path derives it from the 5D SU(N_c) CS action: "
            "(1) 5D Dirac condition → g₄² = 2π/K_CS; "
            "(2) KK dimensional reduction; "
            "(3) SU(N_c) trace normalisation → K_CS × α_GUT = N_c. "
            "Residual caveat: higher-dimensional completion for full GUT field identification. "
            "See the current α_GUT closure modules and WAVE_CHANGELOG ledger for the latest status."
        ),
        "sources": ["src/core/alpha_gut_cs_derivation.py", "src/core/alpha_gut_su5_complete.py", "FALLIBILITY.md §III.3.1"],
        "status": "DERIVED / CONSTRAINED CLOSURE PATH",
    },
    "neutrino_masses": {
        "topic": "Neutrino mass splittings",
        "answer": (
            "P16 (Δm²₂₁, solar splitting) is now GEOMETRIC_ESTIMATE_CERTIFIED (v10.17). "
            "The T²/Z₃ torsion split Δc₀₁ = 1/(2K_CS) = 1/148 produces a geometric ratio "
            "Δm²₂₁/Δm²₃₁ that is independent of the seed mass. "
            "P17 (Δm²₃₁, atmospheric splitting) is GEOMETRIC_ESTIMATE_CERTIFIED with "
            "2NLO follow-up residual ~6.87% (improved from 7.26% NLO baseline). "
            "Both require full 6D+ moduli stabilisation (WS-III) for GEOMETRIC_PREDICTION. "
            "See src/sixd/solar_splitting_6dplus.py and neutrino_dm31_2nlo.py."
        ),
        "sources": ["src/sixd/solar_splitting_6dplus.py", "src/sixd/neutrino_dm31_2nlo.py"],
        "status": "P16: GEOMETRIC_ESTIMATE_CERTIFIED; P17: GEOMETRIC_ESTIMATE_CERTIFIED",
    },
    "roadmap_v10_18": {
        "topic": "v10.18 roadmap and delivery status",
        "answer": (
            "Canonical roadmap status is maintained in docs/mas_tracker.yml. "
            "v10.18 records ToE 15.2→15.8 (54%→56%), P6 and P13 promoted to "
            "GEOMETRIC_PREDICTION, P17 2NLO improvement to 6.87% residual, and "
            "delivery of CMB-S4/DUNE/Hyper-K/JUNO monitor harnesses plus RAG expansion."
        ),
        "sources": ["docs/mas_tracker.yml", "docs/TOE_SCORE_AUDIT.md"],
        "status": "v10.18 delivered",
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
            "m_p/m_e = K_CS²/N_c = 74²/3 = 5476/3 ≈ 1825.3 (PDG: 1836.15). "
            "Residual: 0.59%. NLO error bound: O(1/πkR) ≈ 2.7% < 5%. "
            "v10.17 upgrades P12 from CONSTRAINED to GEOMETRIC_PREDICTION. "
            "C_lat (lattice QCD normalization) cancels exactly in the ratio formula. "
            "See src/core/mp_me_geometric_prediction.py."
        ),
        "sources": ["src/core/mp_me_geometric_prediction.py", "src/core/pillar202_mp_me_lattice_free.py"],
        "status": "GEOMETRIC_PREDICTION (upgraded v10.17)",
    },
    "sin2_theta_w": {
        "topic": "sin²θ_W electroweak mixing angle P4",
        "answer": (
            "P4 (sin²θ_W) is GEOMETRIC_PREDICTION (v10.17). "
            "Derivation: K_CS=74 and n_w=5 select SU(5) via Kawamura Z₂ orbifold → "
            "sin²θ_W(M_GUT) = 3/8 (exact Georgi-Glashow). 1-loop SM RGE (Georgi-Quinn-Weinberg) "
            "from M_GUT=10^13 GeV to M_Z gives sin²θ_W(M_Z) ≈ 0.2313 (PDG: 0.23122, residual 0.05%). "
            "See src/core/sin2_theta_w_geometric.py."
        ),
        "sources": ["src/core/sin2_theta_w_geometric.py", "src/core/sm_free_parameters.py"],
        "status": "GEOMETRIC_PREDICTION (v10.17, 0.05% residual)",
    },
    "higgs_vev": {
        "topic": "Higgs VEV v = 246 GeV P6",
        "answer": (
            "P6 (Higgs VEV v) is GEOMETRIC_PREDICTION (v10.18). "
            "Derivation via Pillar 139 (higgs_vev_exact.py): quartic λ_H^tree = 25/148 (from n_w=5, k_CS=74), "
            "KK threshold M_KK ≈ 1042 GeV, 1-loop top-Yukawa RGE correction gives λ_eff ≈ 0.130. "
            "v_pred = m_H/sqrt(2λ_eff) ≈ 245.96 GeV (PDG: 246.22 GeV, residual ≈ 0.10%). "
            "See src/core/higgs_vev_exact.py and higgs_vev_upgrade_p6.py."
        ),
        "sources": ["src/core/higgs_vev_exact.py", "src/core/higgs_vev_upgrade_p6.py"],
        "status": "GEOMETRIC_PREDICTION (v10.18, 0.10% residual)",
    },
    "alpha_em": {
        "topic": "Fine structure constant alpha α P13",
        "answer": (
            "P13 (fine structure constant α) is GEOMETRIC_PREDICTION (v10.18). "
            "Derivation: α_GUT = N_C/K_CS = 3/74 is fully derived from the 5D SU(N_c) CS action "
            "(src/core/alpha_gut_cs_derivation.py). 1-loop SU(5)→SM RGE running from M_GUT to M_Z "
            "then to 0 (Pillar 94, sm_free_parameters.py) gives α_em(0) ≈ 1/137.0. "
            "PDG: 1/137.036, residual ≈ 0.026%. "
            "See src/core/alpha_em_geometric.py."
        ),
        "sources": ["src/core/alpha_em_geometric.py", "src/core/alpha_gut_cs_derivation.py"],
        "status": "GEOMETRIC_PREDICTION (v10.18, 0.026% residual)",
    },
    "cmbs4": {
        "topic": "CMB-S4 predictions falsification",
        "answer": (
            "CMB-S4 (~2030) will measure n_s and r with precision σ(n_s)≈0.002 and σ(r)≈0.001. "
            "UM predictions: n_s = 0.9635 (Planck: 0.9649±0.0042, currently 0.33σ CONSISTENT), "
            "r = 0.0315 (< BICEP/Keck upper limit of 0.036 CONSISTENT). "
            "Falsification: n_s ∉ [0.955, 0.972] at σ<0.001, or r < 0.010 at >3σ. "
            "See src/core/cmbs4_monitor.py."
        ),
        "sources": ["src/core/cmbs4_monitor.py", "docs/TOE_SCORE_AUDIT.md"],
        "status": "PENDING — CMB-S4 launch ~2030",
    },
    "dune": {
        "topic": "DUNE delta CP leptonic CP violation",
        "answer": (
            "DUNE (~2028-2032) will measure leptonic CP phase δ_CP with precision ~0.05 rad. "
            "UM prediction (P15): δ_CP = π/3 + 9D correction ≈ 1.216 rad. "
            "PDG: δ_CP = 1.20 ± 0.20 rad (currently 0.08σ CONSISTENT). "
            "Falsification: δ_CP ∉ [0.85, 1.30] rad at < 3% uncertainty. "
            "See src/core/dune_dcp_monitor.py."
        ),
        "sources": ["src/core/dune_dcp_monitor.py", "src/nined/cp_phase_9d_refinement.py"],
        "status": "BEST_EVIDENCE_CONSTRAINED — DUNE first physics 2028",
    },
    "yukawa_hierarchy": {
        "topic": "Yukawa hierarchy top bottom tau electron",
        "answer": (
            "P7-P10 (y_t, y_b, y_τ, y_e) are CONSTRAINED (all within 50% of PDG). "
            "The 6D mechanism: fermion wavefunctions localized in the extra dimension with bulk mass c_L. "
            "Overlap integral y ∝ f(c_L) where f decays exponentially with c_L. "
            "With π kR = 37, Δc_L ≈ 0.17 between top and electron generates the full 10^5 hierarchy. "
            "Current c_L parameters are CONSTRAINED (not yet derived from first principles). "
            "Full derivation requires 6D wavefunction spectrum (WS-VII). "
            "See src/sixd/yukawa_hierarchy_6d.py."
        ),
        "sources": ["src/sixd/yukawa_hierarchy_6d.py", "src/core/fermion_cL_spectrum_6d_audit.py"],
        "status": "CONSTRAINED — WS-VII path to GEOMETRIC_PREDICTION",
    },
    "pillar102": {
        "topic": "Pillar 102 gravitational waves brane dynamics",
        "answer": (
            "Pillar 102 (post-101 extension): GW signals from brane dynamics. "
            "The UM predicts GW from: (1) brane-brane collisions at M_KK ≈ 1042 GeV "
            "(f_peak ≈ 10^26 Hz — far above LISA/LIGO); (2) radion oscillations at m_r ≈ 70 GeV; "
            "(3) stochastic KK graviton background Ω_GW ~ (M_KK/M_Pl)² × π_kR. "
            "Detection requires future high-frequency GW detectors (>kHz). "
            "ARCHITECTURE_LIMIT: brane GW signals are a genuine 6D+ prediction, not yet testable. "
            "See src/core/pillar102_brane_gw.py."
        ),
        "sources": ["src/core/pillar102_brane_gw.py", "src/core/kk_gw_background.py"],
        "status": "ARCHITECTURE_LIMIT — future high-frequency GW detectors needed",
    },
}


def _normalize_token(token: str) -> str:
    token = token.strip().lower()
    return _TOKEN_ALIASES.get(token, token)


def _tokenize(text: str) -> Set[str]:
    return {
        _normalize_token(token)
        for token in re.findall(r"\w+", text.lower())
        if token.strip()
    }


def _safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _extract_latest_wave(repo_root: Path) -> Optional[str]:
    changelog = _safe_read_text(repo_root / "docs/WAVE_CHANGELOG.md")
    match = re.search(r"^##\s+(v[0-9.]+)\b", changelog, re.MULTILINE)
    return match.group(1) if match else None


def _extract_status_header(repo_root: Path) -> Optional[str]:
    status = _safe_read_text(repo_root / "STATUS.md")
    match = re.search(r"\*Unitary Manifold ([^*]+)\*", status)
    return match.group(1).strip() if match else None


def _extract_latest_regression(repo_root: Path) -> Optional[str]:
    status = _safe_read_text(repo_root / "STATUS.md")
    match = re.search(r"Latest verified branch regression:\s*([^\n]+)", status)
    return match.group(1).strip() if match else None


def build_runtime_knowledge_base(repo_root: Optional[Path] = None) -> Dict[str, Dict]:
    """Merge static facts with lightweight runtime facts from canonical ledgers."""
    if repo_root is None:
        repo_root = Path(__file__).parent.parent

    kb = dict(KNOWLEDGE_BASE)
    latest_wave = _extract_latest_wave(repo_root)
    status_header = _extract_status_header(repo_root)
    latest_regression = _extract_latest_regression(repo_root)

    if latest_wave or status_header:
        answer_parts = []
        if latest_wave:
            answer_parts.append(f"Latest wave entry in docs/WAVE_CHANGELOG.md: {latest_wave}.")
        if status_header:
            answer_parts.append(f"STATUS.md header: {status_header}.")
        kb["repo_state"] = {
            "topic": "Current repository wave and status snapshot",
            "answer": " ".join(answer_parts),
            "sources": ["docs/WAVE_CHANGELOG.md", "STATUS.md"],
            "status": latest_wave or status_header or "AVAILABLE",
        }

    if latest_regression:
        kb["latest_regression"] = {
            "topic": "Latest verified branch regression",
            "answer": f"The canonical STATUS.md ledger reports: {latest_regression}.",
            "sources": ["STATUS.md"],
            "status": "REGRESSION_BASELINE",
        }

    return kb


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
            ("docs/TOE_SCORE_AUDIT.md", "ToE Score Audit"),
            ("docs/LITEBIRD_FALSIFIER_BRIEF.md", "LiteBIRD Falsifier Brief"),
            ("docs/MAS_COMPLETION_CERTIFICATE.md", "MAS Completion Certificate"),
            ("1-THEORY/UNIFICATION_PROOF.md", "Unification Proof"),
        ]

        for rel_path, title in target_files:
            full_path = repo_root / rel_path
            if full_path.exists():
                try:
                    text = full_path.read_text(encoding="utf-8", errors="replace")
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
            ("docs/TOE_SCORE_AUDIT.md", "ToE Score Audit"),
            ("docs/WAVE_CHANGELOG.md", "Wave Changelog"),
            ("docs/LITEBIRD_FALSIFIER_BRIEF.md", "LiteBIRD Falsifier Brief"),
            ("1-THEORY/UNIFICATION_PROOF.md", "Unification Proof"),
            ("6-MONOGRAPH/MCP_INGEST.md", "MCP Ingest (full repo summary)"),
        ]

        for rel_path, title in intent_sources + standard_sources:
            full_path = repo_root / rel_path
            if full_path.exists():
                try:
                    text = full_path.read_text(encoding="utf-8", errors="replace")
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
        query_tokens = _tokenize(query)
        query_text = query.lower().strip()
        scored = [
            (min(1.0, chunk.score(query_tokens, query_text) * _source_weight(chunk.source)), chunk)
            for chunk in self.chunks
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def lookup_kb(self, query: str) -> Optional[Dict]:
        """Look up the knowledge base for a direct fact match.

        Returns the best matching KB entry, or None.
        """
        query_tokens = _tokenize(query)
        query_text = query.lower().strip()
        best_score = 0.0
        best_entry = None
        for key, entry in self.knowledge_base.items():
            combined = " ".join(
                [
                    key,
                    entry.get("topic", ""),
                    entry.get("answer", ""),
                    " ".join(entry.get("sources", [])),
                ]
            )
            topic_tokens = _tokenize(combined)
            score = len(query_tokens & topic_tokens) / max(len(query_tokens), 1)
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
        }

    # Fall back to document retrieval
    results = index.search(query, top_k=top_k)
    if not results or results[0][0] < 0.05:
        return {
            "query": query,
            "answer": (
                "No highly relevant result found in the index. "
                "Please consult FALLIBILITY.md, STATUS.md, or docs/TOE_SCORE_AUDIT.md "
                "for comprehensive coverage of the Unitary Manifold framework."
            ),
            "source_type": "no_result",
            "context_chunks": [],
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
