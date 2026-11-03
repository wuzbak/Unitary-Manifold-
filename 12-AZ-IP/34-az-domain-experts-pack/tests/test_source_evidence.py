# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Regression coverage for source-grounded retrieval and its HTTP contract."""

import ast
import hashlib
import json
import sys
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_domain_experts_pack import DomainExpert
from az_domain_experts_pack.app.server import build_server


class _FirstEvidence:
    def shared(self):
        """citationprobe first owner.

        A multiline source quotation.
        """


class _SecondEvidence:
    async def shared(self):
        """citationprobe second owner."""


def assert_citation(result, source_dir):
    source_path = Path(result["source_path"])
    citation = result["citation"]
    assert source_path == source_dir / citation["relative_path"]
    source = source_path.read_bytes()
    assert citation["source_sha256"] == hashlib.sha256(source).hexdigest()
    lines = source.decode("utf-8").splitlines()
    literal = "\n".join(lines[citation["start_line"] - 1:citation["end_line"]])
    doc_tree = ast.parse(literal.strip())
    assert ast.get_docstring(doc_tree) == result["text"]


def test_nested_qualified_symbols_have_exact_citations():
    source_dir = Path(__file__).resolve().parent
    expert = DomainExpert("evidence-fixture", source_dir)
    results = expert.query("citationprobe", top_k=50)
    symbols = {result["symbol"] for result in results}
    assert "test_source_evidence._FirstEvidence.shared" in symbols
    assert "test_source_evidence._SecondEvidence.shared" in symbols
    for result in results:
        assert_citation(result, source_dir)
    before = results
    expert.build()
    assert expert.query("citationprobe", top_k=50) == before


def test_recursively_indexes_package_modules():
    source_dir = PRODUCT_ROOT / "az_domain_experts_pack"
    expert = DomainExpert("package-fixture", source_dir)
    results = expert.query("Static HTTP server", top_k=50)
    result = next(result for result in results if result["symbol"] == "app.server")
    assert result["citation"]["relative_path"] == "app/server.py"
    assert_citation(result, source_dir)


@pytest.mark.parametrize("top_k", [0, -1, 51, True, 1.5, "3", None])
def test_retrieval_rejects_invalid_limits(top_k):
    expert = DomainExpert("evidence-fixture", Path(__file__).parent)
    with pytest.raises(ValueError, match="between 1 and 50"):
        expert.query("citationprobe", top_k=top_k)


@pytest.fixture
def live_server():
    server = build_server(port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_http_query_returns_verifiable_domain_evidence(live_server):
    query = urlencode({"expert": "materials-science", "question": "polaron", "top_k": 2})
    with urlopen(f"{live_server}/api/query?{query}", timeout=5) as response:
        assert response.status == 200
        payload = json.load(response)
    assert 0 < len(payload["results"]) <= 2
    from az_domain_experts_pack import MATERIALS_EXPERT
    for result in payload["results"]:
        assert_citation(result, MATERIALS_EXPERT.source_dir)
    with urlopen(live_server, timeout=5) as response:
        html = response.read().decode()
    assert "c.relative_path" in html
    assert "c.source_sha256" in html
    assert "not independently validated science" in html


@pytest.mark.parametrize("top_k", ["0", "-1", "51", "bad"])
def test_http_rejects_invalid_limits(live_server, top_k):
    query = urlencode({"expert": "materials-science", "question": "polaron", "top_k": top_k})
    with pytest.raises(HTTPError) as error:
        urlopen(f"{live_server}/api/query?{query}", timeout=5)
    assert error.value.code == 400
    assert "error" in json.load(error.value)


def test_http_no_match_does_not_invent_evidence(live_server):
    query = urlencode({"expert": "atomic-spectroscopy", "question": "xyzxyz_qqq"})
    with urlopen(f"{live_server}/api/query?{query}", timeout=5) as response:
        assert json.load(response)["results"] == []
