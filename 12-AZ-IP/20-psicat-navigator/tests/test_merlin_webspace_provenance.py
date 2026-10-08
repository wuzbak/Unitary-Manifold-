# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import copy
import re
import hashlib
import threading

import httpx
import pytest

from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool
from ox_navigator.engine.merlin_webspace_provenance import (
    REPO_ROOT,
    answer_provenance_question,
    audit_webspace_provenance,
    chain_hash,
    load_snapshot,
    nibble_step_rate,
    tree_hash,
    verify_chain_hash,
)

H1 = hashlib.sha256(b"one").hexdigest()
H2 = hashlib.sha256(b"two").hexdigest()


def _ids(report: dict) -> set[str]:
    return {f["id"] for f in report["findings"]}


def test_snapshot_transcription_is_internally_consistent() -> None:
    snap = load_snapshot()
    mi = snap["machine_index"]
    sbom = mi["sbom"]
    assert len(sbom["declared_runtime_dependencies"]) == mi["coverage"]["dependencies"]["direct_dependencies"] == 79
    assert len(sbom["declared_dev_dependencies"]) == mi["coverage"]["dependencies"]["direct_dev_dependencies"] == 17
    assert sum(sbom["license_histogram"].values()) + len(sbom["packages_without_license_metadata"]) == 892
    assert sum(mi["redaction"]["per_file_counts"].values()) == mi["redaction"]["personal_mailboxes_redacted"]
    assert len(snap["data_provenance_page"]["components"]) == 8
    text = str(snap)
    assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)  # no mailboxes transcribed
    assert "425.788" not in text  # phone-shaped samples deliberately omitted


def test_chain_hash_convention_is_explicit_and_order_sensitive() -> None:
    assert chain_hash([H1, H2]) == hashlib.sha256((H1 + H2).encode()).hexdigest()
    assert chain_hash([H1, H2]) != chain_hash([H2, H1])
    assert chain_hash([H2, H1], sort=True) == chain_hash([H1, H2], sort=True)
    with pytest.raises(ValueError):
        chain_hash(["f8c2b7d3"])
    low, high = sorted([H1, H2])
    result = verify_chain_hash([high, low], chain_hash([low, high]))
    assert result["verified"] is True and result["matched_conventions"] == ["sorted_no_separator"]
    assert verify_chain_hash([H1, H2], "0" * 64)["verified"] is False


def test_tree_hash_follows_machine_index_definition() -> None:
    files = {"b.txt": H2, "a.txt": H1}
    expected = hashlib.sha256(f"a.txt\0{H1}\nb.txt\0{H2}".encode()).hexdigest()
    assert tree_hash(files) == expected


def test_nibble_step_rate_separates_real_digests_from_patterns() -> None:
    real = [hashlib.sha256(str(i).encode()).hexdigest()[:8] for i in range(40)]
    assert nibble_step_rate(real)["rate"] < 0.2
    synthetic = nibble_step_rate(["f8c2b7d3", "e7b1a6c2", "d6a0f5b1", "c5f9e4a0", "b4e8d3f9"])
    assert synthetic["unit_decrements"] == 27 and synthetic["steps"] == 32


def test_audit_reports_the_expected_findings() -> None:
    report = audit_webspace_provenance(repo_version="38.2")
    ids = _ids(report)
    for expected in (
        "DP-CHAIN-UNVERIFIABLE", "DP-LICENSE-CONTRADICTION", "DP-TIMELINE-PLACEHOLDER",
        "DP-TIMELINE-TRUNCATED", "DP-TIMELINE-ORDER", "DP-TIMELINE-STALE", "DP-VERSION-DRIFT",
        "DP-EXTERNAL-UNDERCOUNT", "DP-DEP-VERSION-TAILWINDCSS", "MI-VERSION-DRIFT",
        "MI-DIRECT-COUNT", "MI-HIPPOCRATIC", "IX-TREE-HASH-VERIFIED",
    ):
        assert expected in ids
    # the full index supersedes the partial-transcription notice
    assert "MI-TRUNCATED" not in ids and report["full_index_available"] is True
    assert report["machine_index_tree_hash_check"]["verified"] is True
    partial = audit_webspace_provenance(repo_version="38.2", include_full_index=False)
    assert "MI-TRUNCATED" in _ids(partial) and not any(i.startswith("IX-") for i in _ids(partial))
    # arithmetic that checks out is not reported
    assert not {"MI-PAGE-ARITHMETIC", "MI-DIRECT-DEPS", "MI-LICENSE-HISTOGRAM", "DP-INTERNAL-COUNT"} & ids
    # react and three match package.json
    assert "DP-DEP-VERSION-REACT" not in ids and "DP-DEP-VERSION-THREE" not in ids
    severities = [f["severity"] for f in report["findings"]]
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    assert severities == sorted(severities, key=order.get)
    assert report["status"] == "ADJACENT_TRACK"


def test_audit_reads_repository_version_and_respects_authority_split() -> None:
    report = audit_webspace_provenance()
    assert report["repository_framework_version"]
    assert "GitHub repository is the authority" in report["authority_split"]
    matched = audit_webspace_provenance(repo_version="37.7")
    assert "MI-VERSION-DRIFT" not in _ids(matched)


def test_audit_clears_findings_when_page_is_fixed() -> None:
    snap = copy.deepcopy(load_snapshot())
    page = snap["data_provenance_page"]
    for i, comp in enumerate(page["components"]):
        comp["sha256"] = hashlib.sha256(str(i).encode()).hexdigest()
        if comp["kind"] == "internal":
            comp["license"] = "AGPL-3.0-or-later"
            if comp["name"] != "Tarot Oracle Engine":
                comp["version"] = "v38.2"
    page["components"][-1]["version"] = "v3.4.17"
    ids = _ids(audit_webspace_provenance(snap, repo_version="38.2", repo_root=REPO_ROOT))
    assert not {"DP-CHAIN-UNVERIFIABLE", "DP-LICENSE-CONTRADICTION", "DP-VERSION-DRIFT", "DP-DEP-VERSION-TAILWINDCSS"} & ids


def test_question_routing_uses_authority_split() -> None:
    assert answer_provenance_question("what framework version is current?")["authority"] == "repository_live_registry"
    licence = answer_provenance_question("why do components say MIT")
    assert licence["authority"] == "machine_index"
    assert "DP-LICENSE-CONTRADICTION" in {f["id"] for f in licence["relevant_findings"]}


def test_tool_registered_and_routed() -> None:
    names = {item["name"]: item for item in _tool_manifest()["functions"]}
    assert "args_schema" in names["getMerlinWebspaceProvenance"]
    result = route_tool("getMerlinWebspaceProvenance", {})
    assert result["ok"] is True
    assert result["result"]["data"]["findings"]


def test_server_exposes_webspace_provenance_endpoint() -> None:
    from ox_navigator.app.server import serve

    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60.0) as client:
            response = client.get("/api/psicat/webspace-provenance")
            assert response.status_code == 200
            body = response.json()
            assert body["ok"] is True
            assert body["webspace_provenance"]["provenance_chain_hash"].startswith("35ccd2ab")
    finally:
        httpd.shutdown()
        httpd.server_close()
