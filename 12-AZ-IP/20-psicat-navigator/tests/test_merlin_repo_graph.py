# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import ast
import shutil
import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_repo_graph
from ox_navigator.engine.merlin_repo_graph import build_repo_graph, route_context_via_repo_graph


def _write_graph_fixture(root: Path, relative: str, content: str = "def example(): pass\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_import_edge_index_preserves_suffix_and_relative_resolution() -> None:
    paths = [
        "src/core/consumer.py",
        "src/core/helper.py",
        "src/core/myhelper.py",
        "src/core/package/__init__.py",
        "other/helper.py",
        "docs/helper.md",
    ]
    imports = ["helper", "core.helper", "src.core.helper", "package", ".helper", ".package", "missing"]
    records = [
        {"path": path, "imports": imports if path == paths[0] else []}
        for path in paths
    ]
    known_paths = set(paths)
    expected_targets = set()
    for imported in imports:
        if imported.startswith("."):
            candidates = merlin_repo_graph._relative_import_candidates(paths[0], imported)
        else:
            module_path = imported.replace(".", "/")
            candidates = {
                path for path in paths
                if path.endswith(f"{module_path}.py")
                or path.endswith(f"{module_path}/__init__.py")
            }
        expected_targets.update(candidates & known_paths)
    edges = merlin_repo_graph._edge_records(records)
    assert edges == [
        {"source": paths[0], "target": target, "relation": "imports"}
        for target in sorted(expected_targets)
    ]


def test_python_record_skips_literal_nodes_but_preserves_nested_statements(
    graph_root, monkeypatch,
) -> None:
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root)
    source = (
        "DATA = [" + ", ".join(str(index) for index in range(5000)) + "]\n"
        "import os\n"
        "class Container:\n"
        "    def method(self):\n"
        "        try:\n"
        "            from pathlib import Path\n"
        "            if True:\n"
        "                def nested(): pass\n"
        "        except Exception:\n"
        "            import json\n"
    )
    relative = "src/core/large_literals.py"
    _write_graph_fixture(graph_root, relative, source)
    tree = ast.parse(source)
    expected_symbols = sorted({
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    })
    original = ast.iter_child_nodes
    visits = []

    def record_visit(node):
        visits.append(type(node).__name__)
        return original(node)

    monkeypatch.setattr(ast, "iter_child_nodes", record_visit)
    record = merlin_repo_graph._python_record(graph_root / relative)
    assert record["symbols"] == expected_symbols
    assert record["imports"] == ["json", "os", "pathlib", "pathlib.Path"]
    assert record["parse_status"] == "ok"
    assert "Constant" not in visits
    assert len(visits) < 40


@pytest.fixture
def graph_root(tmp_path):
    yield tmp_path
    shutil.rmtree(tmp_path)


def test_repo_graph_routes_late_matching_module_tests_docs_and_product(graph_root, monkeypatch) -> None:
    tmp_path = graph_root
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", tmp_path)
    for index in range(620):
        _write_graph_fixture(tmp_path, f"src/core/aaa_{index:04d}.py")
    matching = {
        "src/core/regression_supervision_plan.py",
        "tests/test_regression_supervision_plan.py",
        "docs/regression_supervision_plan.md",
        "proof/regression_supervision_plan.md",
        "12-AZ-IP/20-psicat-navigator/ox_navigator/engine/regression_supervision_plan.py",
    }
    for relative in matching:
        _write_graph_fixture(tmp_path, relative)
    for cap in (8, 600):
        route = route_context_via_repo_graph("regression supervision plan", max_files=cap)
        assert matching <= {item["path"] for item in route["suggested_files"]}
        assert route == route_context_via_repo_graph("regression supervision plan", max_files=cap)
        assert route["graph_summary"]["file_count"] == cap
        assert route["graph_summary"]["total_discovered"] == 625
        assert route["graph_summary"]["truncated_count"] == 625 - cap
        assert route["graph_summary"]["truncated"] is True


def test_repo_graph_discovers_added_files_and_drops_removed_paths(graph_root, monkeypatch) -> None:
    tmp_path = graph_root
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", tmp_path)
    original = "src/core/initial.py"
    added = "tests/test_new_graph_module.py"
    _write_graph_fixture(tmp_path, original)
    assert build_repo_graph()["summary"]["total_discovered"] == 1
    _write_graph_fixture(tmp_path, added)
    graph = build_repo_graph()
    assert {node["path"] for node in graph["nodes"]} == {original, added}
    assert graph["summary"]["total_discovered"] == 2
    (tmp_path / original).unlink()
    graph = build_repo_graph()
    assert [node["path"] for node in graph["nodes"]] == [added]
    assert graph["summary"]["total_discovered"] == 1


def test_discovery_preserves_source_suffixes_and_visits_each_subtree_once(graph_root, monkeypatch) -> None:
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root)
    included = {
        "src/core/example.py", "src/core/example.md", "tests/test_example.py",
        "proof/example.py", "proof/example.md", "docs/example.md", "1-THEORY/example.md",
        "12-AZ-IP/20-psicat-navigator/example.py", "12-AZ-IP/20-psicat-navigator/example.md",
    }
    excluded = {"src/core/example.json", "tests/example.md", "docs/example.py"}
    for relative in included | excluded:
        _write_graph_fixture(graph_root, relative)
    original_scandir = merlin_repo_graph.os.scandir
    visits = []

    def counted_scandir(path):
        visits.append(path)
        return original_scandir(path)

    monkeypatch.setattr(merlin_repo_graph.os, "scandir", counted_scandir)
    discovered = merlin_repo_graph._discover_files()
    assert {path.relative_to(graph_root).as_posix() for path in discovered} == included
    assert len(visits) == len(set(visits))
    assert len(visits) >= 6


def test_selection_reuses_path_tokens_without_caching_discovery(graph_root, monkeypatch) -> None:
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root)
    merlin_repo_graph._file_layout_cached.cache_clear()
    for name in ("alpha", "beta"):
        _write_graph_fixture(graph_root, f"src/core/{name}.py")
    tokenize = merlin_repo_graph._tokenize
    calls = []

    def counted_tokenize(*parts):
        calls.extend(parts)
        return tokenize(*parts)

    monkeypatch.setattr(merlin_repo_graph, "_tokenize", counted_tokenize)
    assert merlin_repo_graph._candidate_files(1, "alpha")[0].name == "alpha.py"
    assert merlin_repo_graph._candidate_files(1, "beta")[0].name == "beta.py"
    assert calls.count("src/core/alpha.py") == 1
    assert calls.count("src/core/beta.py") == 1
    _write_graph_fixture(graph_root, "tests/test_gamma.py")
    assert merlin_repo_graph._candidate_files(1, "gamma")[0].name == "test_gamma.py"
    (graph_root / "tests/test_gamma.py").unlink()
    assert len(merlin_repo_graph._candidate_files(10)) == 2


def test_graph_metadata_cache_reuses_benchmark_query_cycle_and_invalidates_sources(graph_root, monkeypatch) -> None:
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root)
    merlin_repo_graph._build_repo_graph_cached.cache_clear()
    for index in range(8):
        _write_graph_fixture(graph_root, f"src/core/topic{index}.py")
    original_edges = merlin_repo_graph._edge_records
    calls = []

    def counted_edges(records):
        calls.append(records)
        return original_edges(records)

    monkeypatch.setattr(merlin_repo_graph, "_edge_records", counted_edges)
    first = [merlin_repo_graph._build_repo_graph(1, f"topic{index}") for index in range(8)]
    second = [merlin_repo_graph._build_repo_graph(1, f"topic{index}") for index in range(8)]
    assert second == first
    assert len(calls) == 8
    _write_graph_fixture(graph_root, "src/core/topic0.py", "def updated_source(): pass\n")
    updated = merlin_repo_graph._build_repo_graph(1, "topic0")
    assert updated["nodes"][0]["symbols"] == ["updated_source"]
    assert len(calls) == 9
    assert merlin_repo_graph._build_repo_graph_cached.cache_info().maxsize == 32


def test_public_graph_mutations_do_not_modify_cached_metadata(graph_root, monkeypatch) -> None:
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root)
    _write_graph_fixture(graph_root, "src/core/example.py")
    graph = build_repo_graph()
    graph["nodes"][0]["symbols"].append("injected_symbol")
    graph["edges"].append({"source": "injected", "target": "injected", "relation": "injected"})
    graph["summary"]["file_count"] = 0
    fresh = build_repo_graph()
    assert fresh["nodes"][0]["symbols"] == ["example"]
    assert fresh["edges"] == []
    assert fresh["summary"]["file_count"] == 1
    route = route_context_via_repo_graph("example")
    route["suggested_files"][0]["symbols"].append("injected_symbol")
    assert route_context_via_repo_graph("example")["suggested_files"][0]["symbols"] == ["example"]


def test_discovery_reuses_priority_metadata_and_keys_it_by_root(graph_root, monkeypatch) -> None:
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root)
    merlin_repo_graph._priority_key_cached.cache_clear()
    merlin_repo_graph._discovery_layout_cached.cache_clear()
    _write_graph_fixture(graph_root, "src/core/alpha.py")
    first = merlin_repo_graph._discover_files()
    assert merlin_repo_graph._discover_files() == first
    assert merlin_repo_graph._discovery_layout_cached.cache_info().hits == 1
    assert merlin_repo_graph._priority_key(first[0]) == (0, "src/core/alpha.py")
    cache = merlin_repo_graph._priority_key_cached.cache_info()
    assert cache.misses == 1
    assert cache.hits == 1
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root / "src")
    assert merlin_repo_graph._priority_key(first[0]) == (7, "core/alpha.py")


@pytest.mark.parametrize("requested,cap", [(-10, 1), (1, 1), (7, 7), (600, 600), (999, 600)])
def test_repo_graph_representative_sampling_is_deterministic_and_bounded(
    graph_root, monkeypatch, requested, cap
) -> None:
    tmp_path = graph_root
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", tmp_path)
    for index in range(605):
        _write_graph_fixture(tmp_path, f"src/core/aaa_{index:04d}.py")
    other_areas = {
        "tests/test_example.py",
        "proof/example.md",
        "1-THEORY/example.md",
        "docs/example.md",
        "12-AZ-IP/20-psicat-navigator/ox_navigator/example.py",
        "src/consciousness/example.py",
    }
    for relative in other_areas:
        _write_graph_fixture(tmp_path, relative)
    graph = build_repo_graph(max_files=requested)
    assert graph == build_repo_graph(max_files=requested)
    assert graph["summary"]["file_count"] == cap
    assert graph["summary"]["max_files"] == cap
    assert graph["summary"]["total_discovered"] == 611
    assert graph["summary"]["truncated_count"] == 611 - cap
    assert graph["summary"]["truncated"] is True
    assert "not an epistemic truth source" in graph["guardrail"]
    if cap >= 7:
        assert other_areas <= {node["path"] for node in graph["nodes"]}


@pytest.mark.parametrize(
    "area,suffix,parser,original,updated,field",
    [
        ("src/core", ".py", "_python_record", "def initial(): pass\n",
         "def updated_record(): pass\n", "symbols"),
        ("docs", ".md", "_markdown_record", "# initial\n",
         "# updated_record\n", "headings"),
    ],
)
def test_repo_graph_reuses_records_across_queries_and_invalidates_edits(
    graph_root, monkeypatch, area, suffix, parser, original, updated, field
) -> None:
    monkeypatch.setattr(merlin_repo_graph, "REPO_ROOT", graph_root)
    merlin_repo_graph._build_repo_graph_cached.cache_clear()
    merlin_repo_graph._record_for_cached.cache_clear()
    shared = f"{area}/common_alpha_beta{suffix}"
    for name in ("alpha_only", "beta_only", "common_alpha_beta"):
        _write_graph_fixture(graph_root, f"{area}/{name}{suffix}", original)
    parse_record = getattr(merlin_repo_graph, parser)
    calls: list[Path] = []

    def counted_record(path):
        calls.append(path)
        return parse_record(path)

    monkeypatch.setattr(merlin_repo_graph, parser, counted_record)
    alpha = merlin_repo_graph._build_repo_graph(2, "alpha")
    beta = merlin_repo_graph._build_repo_graph(2, "beta")
    assert {node["path"] for node in alpha["nodes"]} != {
        node["path"] for node in beta["nodes"]
    }
    shared_path = (graph_root / shared).resolve()
    assert calls.count(shared_path) == 1
    assert len(calls) == 3
    _write_graph_fixture(graph_root, shared, updated)
    refreshed = merlin_repo_graph._build_repo_graph(2, "beta")
    record = next(node for node in refreshed["nodes"] if node["path"] == shared)
    assert record[field] == ["updated_record"]
    assert calls.count(shared_path) == 2
    assert len(calls) == 4
    cache = merlin_repo_graph._record_for_cached.cache_info()
    assert cache.maxsize == 1200
    assert cache.currsize <= cache.maxsize
