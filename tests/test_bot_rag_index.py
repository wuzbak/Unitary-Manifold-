# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for bot/rag_index.py — RAG Q&A endpoint."""
from __future__ import annotations

import pytest
from pathlib import Path

import bot.rag_index as rag_index_module
from bot.rag_index import (
    KNOWLEDGE_BASE,
    DocumentChunk,
    RAGIndex,
    answer_question,
    build_context_scaffold,
    build_default_index,
    build_runtime_knowledge_base,
    detect_query_lane,
    render_context_scaffold,
    retrieve_intent,
    build_intent_index,
)


# ---------------------------------------------------------------------------
# KNOWLEDGE_BASE
# ---------------------------------------------------------------------------

def test_knowledge_base_non_empty():
    assert len(KNOWLEDGE_BASE) > 0


def test_knowledge_base_structure():
    """Every KB entry must have topic, answer, sources, status."""
    for key, entry in KNOWLEDGE_BASE.items():
        assert "topic" in entry, f"Missing 'topic' in KB entry {key}"
        assert "answer" in entry, f"Missing 'answer' in KB entry {key}"
        assert "sources" in entry, f"Missing 'sources' in KB entry {key}"
        assert "status" in entry, f"Missing 'status' in KB entry {key}"


def test_knowledge_base_birefringence():
    assert "birefringence" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["birefringence"]
    assert "0.273" in entry["answer"] or "0.331" in entry["answer"]
    assert "LiteBIRD" in entry["answer"]


def test_knowledge_base_toe_score():
    assert "toe_score" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["toe_score"]
    assert "not established" in entry["answer"]
    assert "%" not in entry["answer"]
    assert "live" not in entry["answer"]
    assert "ToE" not in entry["answer"]
    assert entry["sources"] == ["docs/TRUTH_LAYER.md", "FALLIBILITY.md"]


def test_knowledge_base_alpha_gut():
    assert "alpha_gut" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["alpha_gut"]
    assert "5D SU" in entry["answer"] or "current closure path" in entry["answer"]


def test_knowledge_base_trusted_open_resources():
    assert "trusted_open_resources" in KNOWLEDGE_BASE
    entry = KNOWLEDGE_BASE["trusted_open_resources"]
    assert "Pillar 258" in entry["topic"] or "Pillar 258" in entry["answer"]
    assert "100 trusted, free online research resources" in entry["answer"]


def test_runtime_knowledge_base_has_repo_state():
    kb = build_runtime_knowledge_base(Path(__file__).parent.parent)
    assert "repo_state" in kb
    assert "sources" in kb["repo_state"]


@pytest.fixture
def status_fixture_root(request):
    root = Path(__file__).parent.parent / ".rag-status-fixtures" / request.node.name
    root.mkdir(parents=True, exist_ok=True)
    yield root
    (root / "STATUS.md").unlink(missing_ok=True)
    root.rmdir()
    parent = root.parent
    if not any(parent.iterdir()):
        parent.rmdir()


@pytest.mark.parametrize("marker", [
    "*v38.2 Sprint CX — Current action scope.*",
    "**v38.2 Sprint CX — Current action scope.**",
    "*Unitary Manifold v38.2 — Current action scope.*",
    "## Unitary Manifold v38.2 — Current action scope.",
])
def test_status_header_selects_first_version_marker(status_fixture_root, marker):
    (status_fixture_root / "STATUS.md").write_text(
        "# STATUS.md\n> Repair note mentions v38.3 but makes no promotion.\n\n"
        + marker + "\n\n*v38.1 Sprint CW — Older scope.*\n"
        "*Unitary Manifold v10.4 — Much older history.*\n",
        encoding="utf-8",
    )
    header = rag_index_module._extract_status_header(status_fixture_root)
    assert header == "v38.2 Sprint CX — Current action scope." or header == (
        "v38.2 — Current action scope."
    )
    kb = build_runtime_knowledge_base(status_fixture_root)
    assert "v38.2" in kb["repo_state"]["answer"]
    assert "v38.1" not in kb["repo_state"]["answer"]
    assert "v10.4" not in kb["repo_state"]["answer"]


@pytest.mark.parametrize("label", [
    "Latest verified full regression in current branch history:",
    "Latest verified full regression in current branch history remains",
    "Latest verified branch regression:",
])
def test_regression_marker_is_historical_not_new_execution(status_fixture_root, label):
    receipt = "64,150 passed · 22 skipped · 18 deselected · 0 failed (Sprint CU record)"
    (status_fixture_root / "STATUS.md").write_text(
        f"*v38.2 Sprint CX. {label} {receipt}.*\n"
        "*Unitary Manifold v10.4. Latest verified branch regression: 10 passed.*\n",
        encoding="utf-8",
    )
    assert rag_index_module._extract_latest_regression(status_fixture_root) == receipt + "."
    entry = build_runtime_knowledge_base(status_fixture_root)["latest_regression"]
    assert entry["status"] == "HISTORICAL_BASELINE"
    assert "not evidence of new execution" in entry["answer"]
    assert "10 passed" not in entry["answer"]
    assert entry["sources"] == ["STATUS.md"]


@pytest.mark.parametrize("current_receipt", [
    "No new regression receipt.",
    "Latest verified full regression in current branch history: REGRESSION_PLACEHOLDER_CV.",
])
def test_current_header_without_regression_does_not_copy_history(status_fixture_root, current_receipt):
    (status_fixture_root / "STATUS.md").write_text(
        f"*v38.2 Sprint CX — {current_receipt}*\n"
        "*Unitary Manifold v10.4. Latest verified branch regression: 10 passed.*\n",
        encoding="utf-8",
    )
    assert rag_index_module._extract_latest_regression(status_fixture_root) is None
    assert "latest_regression" not in build_runtime_knowledge_base(status_fixture_root)


def test_detect_query_lane_prefers_runtime_performance():
    lane = detect_query_lane("Review runtime benchmark latency and training profile behavior.")
    assert lane["lane_id"] == "runtime_performance"


def test_detect_query_lane_defaults_to_physics_navigation_without_keyword_hits():
    lane = detect_query_lane("Untethered umbrella harmonics without any indexed trigger words.")
    assert lane["lane_id"] == "physics_navigation"


def test_detect_query_lane_supports_multiword_keywords(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(rag_index_module._LANE_HINTS["formal_proof"], "keywords", {"formal proof"})
    lane = detect_query_lane("Please assemble a formal proof for this claim.")
    assert lane["lane_id"] == "formal_proof"
    assert lane["matched_keywords"] == "formal proof"


def test_build_context_scaffold_includes_ast_and_tool_hints():
    idx = RAGIndex()
    scaffold = build_context_scaffold(idx, "How is alpha_gut derived?", repo_root=Path(__file__).parent.parent)
    assert scaffold["schema_version"] == "rag_context_scaffold_v1"
    assert scaffold["boundary"]["dominant_gate"] == "OPEN_GAP"
    assert scaffold["ast"]["enabled"] is True
    assert scaffold["tooling"]["suggested_endpoints"]


def test_build_context_scaffold_collects_ast_hints_until_limit(monkeypatch: pytest.MonkeyPatch):
    idx = RAGIndex()
    repo_root = Path(__file__).parent.parent

    python_path = repo_root / "src/core/metric.py"
    ignored_path = repo_root / "README.md"

    monkeypatch.setattr(idx, "lookup_kb", lambda _query: {"status": "hardgate", "sources": ["README.md", "src/core/metric.py"]})
    monkeypatch.setattr(idx, "search", lambda _query, top_k=5: [])

    def fake_build_ast_hint(_repo_root: Path, path: Path):
        if path == python_path:
            return {"path": "src/core/metric.py", "symbol_density": 3, "symbols": ["Metric", "curvature", "ricci"]}
        return None

    monkeypatch.setattr(rag_index_module, "_build_ast_hint", fake_build_ast_hint)
    scaffold = build_context_scaffold(idx, "metric structure", repo_root=repo_root, ast_file_limit=1)
    assert scaffold["ast"]["enabled"] is True
    assert scaffold["ast"]["record_count"] == 1
    assert scaffold["ast"]["files"][0]["path"] == "src/core/metric.py"


def test_build_context_scaffold_clamps_negative_ast_limit():
    idx = RAGIndex()
    scaffold = build_context_scaffold(idx, "How is alpha_gut derived?", repo_root=Path(__file__).parent.parent, ast_file_limit=-5)
    assert scaffold["ast"]["file_limit"] == 1
    assert scaffold["tooling"]["ast_file_limit"] == 1


def test_build_context_scaffold_falls_back_on_invalid_ast_limit():
    idx = RAGIndex()
    scaffold = build_context_scaffold(idx, "How is alpha_gut derived?", repo_root=Path(__file__).parent.parent, ast_file_limit="oops")
    assert scaffold["ast"]["file_limit"] == 3
    assert scaffold["tooling"]["ast_file_limit"] == 3


def test_build_context_scaffold_deduplicates_provenance_sources(monkeypatch: pytest.MonkeyPatch):
    idx = RAGIndex()
    repo_root = Path(__file__).parent.parent
    shared_chunk = DocumentChunk("README.md", "Readme", "physics navigation")

    monkeypatch.setattr(idx, "lookup_kb", lambda _query: {"status": "hardgate", "sources": ["README.md"]})
    monkeypatch.setattr(idx, "search", lambda _query, top_k=3: [(0.9, shared_chunk)])

    scaffold = build_context_scaffold(idx, "physics navigation", repo_root=repo_root)
    assert scaffold["provenance"]["source_count"] == 1
    assert scaffold["provenance"]["sources"][0]["label"] == "README.md"


def test_render_context_scaffold_contains_structural_sections():
    idx = RAGIndex()
    scaffold = build_context_scaffold(idx, "Inspect tool routing and agentToolkit orchestration.", repo_root=Path(__file__).parent.parent)
    rendered = render_context_scaffold(scaffold)
    assert "[CONTEXT SCAFFOLD]" in rendered
    assert "[TOOL/RUNTIME HINTS]" in rendered


# ---------------------------------------------------------------------------
# DocumentChunk
# ---------------------------------------------------------------------------

def test_document_chunk_tokens():
    chunk = DocumentChunk("test.md", "Test", "Hello world physics")
    assert "hello" in chunk.tokens
    assert "world" in chunk.tokens
    assert "physics" in chunk.tokens


def test_document_chunk_score_perfect():
    chunk = DocumentChunk("test.md", "Test", "birefringence litebird prediction")
    query = {"birefringence", "litebird"}
    assert chunk.score(query) == 1.0


def test_document_chunk_score_zero():
    chunk = DocumentChunk("test.md", "Test", "hello world")
    query = {"birefringence", "alpha_s"}
    assert chunk.score(query) == 0.0


def test_document_chunk_score_empty_query():
    chunk = DocumentChunk("test.md", "Test", "some text")
    assert chunk.score(set()) == 0.0


def test_document_chunk_score_partial():
    chunk = DocumentChunk("test.md", "Test", "birefringence alpha_s prediction")
    query = {"birefringence", "litebird"}
    score = chunk.score(query)
    assert 0.0 < score < 1.0


def test_document_chunk_title_bonus_improves_score():
    chunk = DocumentChunk("test.md", "LiteBIRD monitor", "prediction window and launch notes")
    with_title = chunk.score({"litebird"})
    without_match = chunk.score({"desi"})
    assert with_title > without_match


# ---------------------------------------------------------------------------
# RAGIndex
# ---------------------------------------------------------------------------

def test_rag_index_build_no_chunks_kb_only():
    """Build with no repo files — should still have KB entries."""
    idx = RAGIndex(chunks=[], knowledge_base=KNOWLEDGE_BASE)
    assert len(idx.knowledge_base) > 0


def test_rag_index_kb_lookup_birefringence():
    idx = RAGIndex()
    result = idx.lookup_kb("birefringence prediction")
    assert result is not None
    assert "LiteBIRD" in result["answer"]


def test_rag_index_kb_lookup_alpha_gut():
    idx = RAGIndex()
    result = idx.lookup_kb("GUT coupling alpha_gut derivation")
    assert result is not None
    assert "5D" in result["answer"] or "current closure path" in result["answer"]


def test_rag_index_kb_lookup_repo_state():
    idx = RAGIndex()
    result = idx.lookup_kb("current repository wave status")
    assert result is not None
    assert any(src in result["sources"] for src in ["docs/WAVE_CHANGELOG.md", "STATUS.md"])


def test_rag_index_kb_lookup_no_match():
    idx = RAGIndex()
    result = idx.lookup_kb("xyzzy incomprehensible query zzz")
    assert result is None


def test_rag_index_search_empty_returns_empty():
    idx = RAGIndex(chunks=[])
    results = idx.search("birefringence", top_k=5)
    assert results == []


def test_rag_index_search_with_chunks():
    chunks = [
        DocumentChunk("a.md", "A", "birefringence litebird 0.273 0.331 prediction"),
        DocumentChunk("b.md", "B", "unrelated content about cats"),
    ]
    idx = RAGIndex(chunks=chunks)
    results = idx.search("birefringence litebird", top_k=2)
    assert len(results) == 2
    # First result should be the birefringence chunk
    assert results[0][1].source == "a.md"
    assert results[0][0] > results[1][0]


def test_rag_index_search_alias_beta_hits_birefringence():
    chunks = [DocumentChunk("a.md", "A", "birefringence litebird prediction window")]
    idx = RAGIndex(chunks=chunks)
    results = idx.search("beta litebird", top_k=1)
    assert results[0][1].source == "a.md"
    assert results[0][0] > 0.0


def test_rag_index_build_from_repo():
    """Build from the actual repo — should succeed without errors."""
    repo_root = Path(__file__).parent.parent
    idx = RAGIndex.build(repo_root=repo_root)
    # Should have at least the KB entries
    assert len(idx.knowledge_base) > 0


# ---------------------------------------------------------------------------
# answer_question
# ---------------------------------------------------------------------------

def test_answer_question_birefringence():
    idx = RAGIndex()
    result = answer_question(idx, "What is the birefringence prediction?")
    assert isinstance(result, dict)
    assert "answer" in result
    assert "0.273" in result["answer"] or "LiteBIRD" in result["answer"]


def test_answer_question_source_type():
    idx = RAGIndex()
    result = answer_question(idx, "birefringence litebird prediction")
    assert result["source_type"] in ("knowledge_base", "document_retrieval", "no_result")
    assert result["context_scaffold"]["schema_version"] == "rag_context_scaffold_v1"


def test_answer_question_repo_state():
    idx = RAGIndex()
    result = answer_question(idx, "What is the current repository wave?")
    assert "answer" in result
    assert result["source_type"] == "knowledge_base"


def test_answer_question_no_result_graceful():
    idx = RAGIndex(chunks=[])
    result = answer_question(idx, "xyzzy42 incomprehensible nonsense query")
    assert "answer" in result
    assert result["source_type"] == "no_result"


def test_answer_question_litebird():
    idx = RAGIndex()
    result = answer_question(idx, "When is LiteBIRD launching?")
    assert "answer" in result
    assert "2032" in result["answer"] or "LiteBIRD" in result["answer"]


def test_answer_question_toe_score():
    idx = RAGIndex()
    result = answer_question(idx, "What is the current framework derivation coverage status?")
    assert "answer" in result
    assert len(result["answer"]) > 20
    assert result["topic"] == KNOWLEDGE_BASE["toe_score"]["topic"]
    assert "%" not in result["answer"]


@pytest.fixture(scope="module")
def built_science_index():
    return RAGIndex.build(repo_root=Path(__file__).parent.parent)


@pytest.mark.parametrize("query,key", [
    ("What is the current action-derived evolution status?", "action_to_evolution"),
    ("Is the action-to-evolution contract closed?", "action_to_evolution"),
    ("Have the Euler-Lagrange equations been earned?", "action_to_evolution"),
    ("Is physical time evolution certified?", "action_to_evolution"),
    ("What is the dark matter model status?", "dark_matter"),
    ("Has the dark-matter model been proved?", "dark_matter"),
    ("Does the halo prescription solve formation?", "dark_matter"),
    ("What is the photon origin status?", "photon_origin"),
    ("Does the orbifold restore a photon zero mode?", "photon_origin"),
    ("Is winding number n_w = 5 unique from first principles?", "winding_number"),
    ("What is the DESI dark energy tension?", "desi"),
    ("What is the cosmological constant status?", "cosmological_constant"),
    ("What is the current framework derivation coverage status?", "toe_score"),
    ("toe_score", "toe_score"),
])
def test_built_index_routes_science_topics(built_science_index, query, key):
    result = answer_question(built_science_index, query)
    entry = KNOWLEDGE_BASE[key]
    assert result["source_type"] == "knowledge_base"
    assert result["topic"] == entry["topic"]
    assert result["answer"] == entry["answer"]
    assert result["status"] == entry["status"]
    assert result["sources"] == entry["sources"]
    assert "%" not in result["answer"]


def test_action_evolution_reports_earned_deliverables_not_physical_time(built_science_index):
    result = answer_question(built_science_index, "current action-derived evolution status")
    assert result["status"] == "DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN"
    for boundary in (
        "deliverables are earned", "1-D periodic", "on a circle",
        "t is not coordinate time", "physical-time evolution is not certified",
        "legacy", "not framework closure",
    ):
        assert boundary in result["answer"]
    assert result["context_scaffold"]["boundary"]["dominant_gate"] == "OPEN_GAP"


def test_dark_matter_scopes_distinct_models(built_science_index):
    answer = answer_question(built_science_index, "dark matter model status")["answer"]
    for boundary in (
        "gauge-dependent B²", "F=dB", "zero gauge energy", "non-overproduction",
        "structure formation", "supplied mass and coupling", "not geometric derivations",
    ):
        assert boundary in answer


def test_photon_origin_does_not_claim_circle_reduction_rescues_orbifold(built_science_index):
    answer = answer_question(built_science_index, "photon origin")["answer"]
    assert "vanishes at both fixed planes" in answer
    assert "no constant massless zero mode" in answer
    assert "argument is withdrawn" in answer


def test_winding_uniqueness_respects_current_scope(built_science_index):
    answer = answer_question(built_science_index, "winding number uniqueness")["answer"]
    assert "observationally selected" in answer
    assert "conditionally" in answer
    assert "do not establish unconditional first-principles uniqueness" in answer
    assert "foundation reassessment" in answer
    assert "pure theorem" not in answer


@pytest.mark.parametrize("query", [
    "What is the current axolotl model status?",
    "Has the blorptastic theory been proved from 5D geometry?",
    "What is the current status?",
    "What is the dark blorptastic model status?",
])
def test_generic_question_words_do_not_prove_unknown_topic(built_science_index, query):
    assert built_science_index.lookup_kb(query) is None
    result = answer_question(built_science_index, query)
    assert result["source_type"] == "no_result"
    assert "No highly relevant result" in result["answer"]


def test_kb_ignores_incidental_answer_and_source_words():
    idx = RAGIndex(knowledge_base={
        "unrelated": {
            "topic": "Unrelated subject",
            "answer": "The axolotl model is proved, current status closed.",
            "sources": ["axolotl_proof.py"],
            "status": "PROVED",
        },
    })
    assert idx.lookup_kb("What is the current axolotl model status?") is None


@pytest.mark.parametrize("builder", [RAGIndex.build, RAGIndex.build_intent_index])
def test_foundation_index_excludes_superseded_truth_layer_sprints(builder):
    idx = builder(repo_root=Path(__file__).parent.parent)
    truth_text = "".join(
        chunk.text for chunk in idx.chunks if chunk.source == "docs/TRUTH_LAYER.md"
    )
    assert "DELIVERABLES_EARNED_EVOLUTION_LAW_OPEN" in truth_text
    assert "## Synthesis repair (2026-10-05)" in truth_text
    assert "The historical 64,150-pass marker is not" in truth_text
    assert "The previous fixed-plane composite-photon argument is withdrawn" in truth_text
    assert "### Sprint CI foundation-lane contraction" not in truth_text
    assert "### Lane 1 executable gradient-flow audit" not in truth_text
    assert any(chunk.source == "1-THEORY/Z2_PARITY_NOTE.md" for chunk in idx.chunks)


def test_current_truth_filter_includes_level_two_repair_without_history():
    text = (
        "## Synthesis repair (2026-10-05)\nCurrent repair evidence.\n"
        "```bash\n# Repeat execution for each batch\npython local_runner.py\n```\n"
        "### Scoped validation\nTargeted only, no new full-suite receipt.\n"
        "## Historical archive\nOld closure claim.\n"
        "### Sprint CI foundation-lane contraction\nOld unearned deliverables.\n"
    )
    selected = rag_index_module._current_document_text("docs/TRUTH_LAYER.md", text)
    assert "Current repair evidence." in selected
    assert "Targeted only" in selected
    assert "# Repeat execution for each batch" in selected
    assert "Historical archive" not in selected
    assert "Old closure" not in selected


def test_science_answers_do_not_import_expensive_certificates(built_science_index, monkeypatch):
    import builtins

    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        assert not name.startswith("src.core."), f"Unexpected science import: {name}"
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    for query in ("action-derived evolution", "dark matter", "photon origin"):
        assert answer_question(built_science_index, query)["source_type"] == "knowledge_base"


def test_science_kb_sources_are_existing_local_paths():
    root = Path(__file__).parent.parent
    for key in ("action_to_evolution", "dark_matter", "photon_origin", "winding_number", "toe_score"):
        for source in KNOWLEDGE_BASE[key]["sources"]:
            assert "://" not in source
            assert (root / source).is_file()


@pytest.mark.parametrize("key", [
    "alpha_s", "higgs_mass", "cosmological_constant", "desi", "alpha_gut",
    "neutrino_masses", "proton_electron_ratio", "sin2_theta_w", "higgs_vev",
    "alpha_em", "yukawa_hierarchy", "pillar102", "dune",
])
def test_audited_static_science_is_scoped_not_promoted(key):
    entry = KNOWLEDGE_BASE[key]
    assert "docs/TRUTH_LAYER.md" in entry["sources"]
    assert "OPEN_GAP" in entry["status"] or entry["status"] == "HONEST_OPEN_PROBLEM"
    assert "historical" in entry["answer"].lower()
    for marketing in (
        "ToE", "fully derived", "pure theorem", "closes the gap",
        "GEOMETRIC_PREDICTION", "CERTIFIED", "AxiomZero", "upgrades",
    ):
        assert marketing not in entry["answer"]
    for source in entry["sources"]:
        assert (Path(__file__).parent.parent / source).is_file()
    idx = RAGIndex(knowledge_base=KNOWLEDGE_BASE)
    result = answer_question(idx, key)
    assert result["answer"] == entry["answer"]
    assert result["context_scaffold"]["boundary"]["dominant_gate"] == "OPEN_GAP"


def test_alpha_s_distinguishes_historical_routes_from_unearned_completion():
    answer = KNOWLEDGE_BASE["alpha_s"]["answer"]
    assert "0.030–0.048" in answer
    assert "not one canonical derivation" in answer
    assert "not an established solution" in answer
    assert "joint UV/Higgs predictivity remains open" in answer


def test_higgs_answers_expose_supplied_mass_and_mixing_inputs():
    assert "supplied VEV, base-mass, radion and brane inputs" in KNOWLEDGE_BASE["higgs_mass"]["answer"]
    answer = KNOWLEDGE_BASE["higgs_vev"]["answer"]
    assert "m_H is a PDG input" in answer
    assert "Iteration does not remove that dependence" in answer
    assert "245.96" in answer


def test_gauge_sector_estimates_do_not_claim_metric_selects_internal_bundle():
    assert "not an independently established coupling derivation" in KNOWLEDGE_BASE["alpha_gut"]["answer"]
    assert "spatial reflection does not select SU(5)" in KNOWLEDGE_BASE["sin2_theta_w"]["answer"]
    assert "orbifold photon obstruction" in KNOWLEDGE_BASE["alpha_em"]["answer"]
    assert "1/137.0" in KNOWLEDGE_BASE["alpha_em"]["answer"]


def test_flavor_and_vacuum_estimates_do_not_promote_assumed_parameters():
    assert "not discrete bulk masses" in KNOWLEDGE_BASE["yukawa_hierarchy"]["answer"]
    assert "without deriving the absolute mass scale" in KNOWLEDGE_BASE["neutrino_masses"]["answer"]
    assert "not by itself a rigorous remainder bound" in KNOWLEDGE_BASE["proton_electron_ratio"]["answer"]
    assert "does not derive the observed vacuum" in KNOWLEDGE_BASE["cosmological_constant"]["answer"]


def test_desi_legacy_inflation_expression_is_not_late_time_confirmation():
    answer = KNOWLEDGE_BASE["desi"]["answer"]
    assert "inflationary-epoch expression" in answer
    assert "not a derived late-time dark-energy value" in answer
    assert "not a live data fetch" in answer


def test_old_roadmap_does_not_reintroduce_aggregate_score_branding():
    entry = KNOWLEDGE_BASE["roadmap_v10_18"]
    assert entry["status"] == "HISTORICAL_ROADMAP_RECORD"
    assert "not the current scientific status" in entry["answer"]
    assert "%" not in entry["answer"]
    assert "ToE" not in entry["answer"]
    assert "docs/TRUTH_LAYER.md" in entry["sources"]


def test_monitor_forecasts_are_not_new_observations_or_verified_phase_values():
    cmb = KNOWLEDGE_BASE["cmbs4"]
    assert "historical forecasts" in cmb["answer"]
    assert "does not supply new observations" in cmb["answer"]
    assert "docs/TRUTH_LAYER.md" in cmb["sources"]
    assert cmb["status"].startswith("PENDING")
    dune = KNOWLEDGE_BASE["dune"]["answer"]
    assert "disagrees with its executable constant" in dune
    assert "must not be treated as a verified phase prediction" in dune
    assert "[0.85, 1.30]" in dune


def test_birefringence_answer_and_falsifier_remain_unchanged():
    assert KNOWLEDGE_BASE["birefringence"]["answer"] == (
        "The Unitary Manifold predicts two birefringence modes from the braided "
        "winding state: β₁ ≈ 0.273° (canonical, k_CS=61 secondary state) and "
        "β₂ ≈ 0.331° (derived, k_CS=74 primary state). "
        "The admissible window is [0.22°, 0.38°] with a predicted gap [0.29°, 0.31°]. "
        "These predictions will be tested by the LiteBIRD satellite (~2032). "
        "Any β outside [0.22°, 0.38°] or inside [0.29°, 0.31°] falsifies the theory."
    )


def test_answer_question_desi():
    idx = RAGIndex()
    result = answer_question(idx, "What is the DESI dark energy tension?")
    assert "answer" in result


def test_answer_question_alpha_gut():
    idx = RAGIndex()
    result = answer_question(idx, "How is alpha_gut derived?")
    assert "answer" in result
    assert "DERIVED" in result["answer"] or "CS" in result["answer"]


def test_answer_question_trusted_resources():
    idx = RAGIndex()
    result = answer_question(idx, "trusted datasets and pubmed resources")
    assert result["source_type"] == "knowledge_base"
    assert "100 trusted, free online research resources" in result["answer"]


def test_answer_question_with_doc_chunks():
    """With real document chunks, retrieval should work."""
    chunks = [
        DocumentChunk("FALLIBILITY.md", "Fallibility", "n_w = 5 winding number pure theorem pillar 70-D"),
        DocumentChunk("STATUS.md", "Status", "pillar set closed 217 pillars"),
    ]
    idx = RAGIndex(chunks=chunks)
    result = answer_question(idx, "winding number n_w theorem")
    assert result["source_type"] in ("knowledge_base", "document_retrieval")


# ---------------------------------------------------------------------------
# build_default_index
# ---------------------------------------------------------------------------

def test_build_default_index_returns_rag_index():
    idx = build_default_index()
    assert isinstance(idx, RAGIndex)
    assert len(idx.knowledge_base) > 0


def test_build_intent_index_returns_rag_index():
    idx = build_intent_index()
    assert isinstance(idx, RAGIndex)
    assert len(idx.chunks) > 0


def test_retrieve_intent_latest_uses_snapshot_sources():
    idx = build_intent_index()
    result = retrieve_intent(idx, mode="latest_intent")
    assert result["mode"] == "latest_intent"
    assert result["sources"]
    assert all("score" in src for src in result["sources"])
