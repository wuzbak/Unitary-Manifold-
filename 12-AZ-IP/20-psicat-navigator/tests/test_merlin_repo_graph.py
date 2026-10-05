# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

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
