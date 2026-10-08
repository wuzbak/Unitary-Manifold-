# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import re
import threading

import httpx

from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool
from ox_navigator.engine.merlin_webspace_index import (
    INDEX_PATH,
    PAGE_BREAK,
    REDACTED_PHONE,
    audit_full_index,
    backend_posture,
    clock_comparison,
    load_full_index,
    load_index_provenance,
    reconstruct_index,
    reconstruct_index_text,
    redact_phone_shaped_strings,
    satisfies_caret,
    sbom_integrity,
    summarise_full_index,
    verify_tree_hash,
)

PUBLISHED_TREE_HASH = "1aa0540a8611552e26af436813958780bbacc7b42537271e18d74d36a3865b7e"


def _ids(findings: list[dict]) -> set[str]:
    return {f["id"] for f in findings}


def test_stored_index_matches_its_provenance_record() -> None:
    raw = gzip.decompress(INDEX_PATH.read_bytes())
    prov = load_index_provenance()
    assert hashlib.sha256(raw).hexdigest() == prov["stored_json_sha256"]
    assert prov["tree_hash_check"]["verified"] is True
    assert prov["source_commit_on_main"].startswith("f4fa4dc5")
    index = load_full_index()
    assert index["$schema"] == "axiomzero.machine-index/v2"
    assert set(index) >= {"sbom", "hashes", "backend", "frontend", "verification_findings"}


def test_tree_hash_reproduces_over_every_file_digest() -> None:
    index = load_full_index()
    result = verify_tree_hash(index)
    assert result["verified"] is True and result["recomputed"] == PUBLISHED_TREE_HASH
    assert result["file_count"] == result["declared_file_count"] == 1454
    assert result["total_bytes"] == result["declared_total_bytes"] == 10662000
    tampered = copy.deepcopy(index)
    first = next(iter(tampered["hashes"]["files"]))
    tampered["hashes"]["files"][first]["sha256"] = "0" * 64
    assert verify_tree_hash(tampered)["verified"] is False
    assert "IX-TREE-HASH-MISMATCH" in _ids(audit_full_index(tampered))


def test_reconstruction_rebuilds_wrapped_strings_and_strips_artifacts() -> None:
    extracted = (
        '{ \n  "path": " .gitignore" , \n  "note": "wrapped across \nlines. " , '
        + PAGE_BREAK
        + '"ex": " .env / .env. *" , "pem": "* .pem" , "pair": "\'A\' , \'B\'" , "url": "9-\nINFRA" }'
    )
    joined = json.loads(reconstruct_index_text(extracted))
    assert joined["note"] == "wrapped across lines. "
    index, counts = reconstruct_index(extracted)
    assert index == {"path": ".gitignore", "note": "wrapped across lines.", "ex": ".env / .env.*",
                     "pem": "*.pem", "pair": "'A', 'B'", "url": "9-INFRA"}
    assert counts["leading_space_before_dot"] == 2 and counts["trailing_space_after_punctuation"] == 1


def test_stored_copy_carries_no_phone_numbers_or_secret_values() -> None:
    index = load_full_index()
    assert index["redaction"]["phone_shaped_strings"]["sample"] == [REDACTED_PHONE] * 5
    assert not re.search(r"\b425\.788\.\d{4}\b", json.dumps(index))
    assert all(str(s["value"]).startswith("NOT PUBLISHED") for s in index["backend"]["secrets"])
    sample = {"redaction": {"phone_shaped_strings": {"sample": ["(555) 010-0000", "x"]}}}
    assert redact_phone_shaped_strings(sample) == 1
    assert sample["redaction"]["phone_shaped_strings"]["sample"] == [REDACTED_PHONE] * 2


def test_caret_ranges_follow_npm_semantics() -> None:
    assert satisfies_caret("4.22.0", "^4.22.0") and not satisfies_caret("3.21.0", "^4.22.0")
    assert satisfies_caret("0.2.9", "^0.2.0") and not satisfies_caret("0.3.0", "^0.2.0")
    assert satisfies_caret("0.0.3", "^0.0.3") and not satisfies_caret("0.0.4", "^0.0.3")
    assert not satisfies_caret("18.1.0", "^18.2.0")
    assert satisfies_caret("5.0.0-release.2", "^5.0.0-release.1")
    assert not satisfies_caret("5.0.0-beta.1", "^4.0.0")


def test_sbom_integrity_explains_the_inflated_counts() -> None:
    sb = sbom_integrity(load_full_index())
    assert sb["entries"] == sb["declared_package_count"] == 892
    assert sb["distinct_name_version_integrity"] == 870 and sb["repeat_surplus"] == 22
    assert sb["repeated_entries"][0] == {"name": "@radix-ui/react-slot", "version": "1.2.3", "occurrences": 8}
    assert sb["direct_entries"] == 111 and sb["declared_direct"] == 96
    wrong = {(d["name"], d["version"]) for d in sb["direct_flag_unsatisfied"]}
    assert {("@tensorflow/tfjs", "3.21.0"), ("apache-arrow", "17.0.0"), ("@types/node", "20.19.43")} <= wrong
    assert len(wrong) == 6 and sb["direct_flag_unsatisfied_entries"] == 7
    # 111 = 96 declared + 7 out-of-range entries + 8 nested in-range @radix-ui/react-slot 1.2.3 copies
    assert sb["direct_entries"] - sb["declared_direct"] - sb["direct_flag_unsatisfied_entries"] == 8
    assert {"@types/node", "@types/react", "@types/react-dom"} <= set(sb["dev_declared_but_flagged_runtime"])
    assert sb["declared_packages_with_multiple_majors"]["@tensorflow/tfjs"] == [3, 4]
    assert sb["hippocratic_packages"] == ["@react-leaflet/core@2.1.0", "react-leaflet@4.2.1"]
    assert sb["direct_hippocratic"] == ["react-leaflet"]
    assert sb["python_licensed"] == ["argparse@2.0.1 (dev=True)"]


def test_backend_posture_flags_scope_auth_and_duplicate_schedules() -> None:
    be = backend_posture(load_full_index())
    assert be["functions"] == 190 and be["secret_names"] == 18
    assert be["secret_values_published"] == []
    assert len(be["service_role_without_auth_check"]) == 41
    github = next(c for c in be["connectors"] if c["type"] == "github")
    assert github["write_capable_scopes"] == ["public_repo"]
    assert be["unreferenced_secrets"] == ["PSICAT_GITHUB_TOKEN"]
    assert ["PhiCat Auto-Braid", "PhiCat Braid Cycle"] in be["duplicate_schedules"]
    assert be["repo_write_functions_are_stub_refusals"] is True
    assert be["scheduled_runs_per_day"]["PhiCat Auto-Braid"] == 288
    assert be["scheduled_runs_per_day"]["PsiCat Training Relay"] == 60
    assert be["scheduled_runs_per_day"]["PsiCat Steward Digest"] == round(2 / 7, 3)


def test_clock_comparison_is_honest_about_what_the_index_shows() -> None:
    clock = clock_comparison(load_full_index())
    assert clock["merlin_tick"] == "12/37"
    assert clock["constants_visible"] is False
    assert clock["ratio_12_37_context"] == ["PsiCat Cat Nap"]
    assert clock["webspace_clock_workflows"]["PsiCat Internal Clock Tick"]["cron"] == "*/15 * * * *"
    assert "time.nist.gov" in clock["webspace_time_hosts"]


def test_full_index_findings_are_ordered_and_complete() -> None:
    findings = audit_full_index()
    ids = _ids(findings)
    for expected in (
        "IX-TREE-HASH-VERIFIED", "IX-SBOM-INSTALL-LOCATIONS", "IX-SBOM-DIRECT-FLAG", "IX-SBOM-DEV-FLAG",
        "IX-SBOM-MULTI-MAJOR", "IX-HIPPOCRATIC-NAMED", "IX-SERVICE-ROLE-UNAUTHENTICATED",
        "IX-GITHUB-WRITE-SCOPE", "IX-UNREFERENCED-SECRETS", "IX-DUPLICATE-SCHEDULE",
        "IX-STALE-BUNDLE-CREDENTIAL-FILE", "IX-SELF-VF-1", "IX-SELF-VF-6", "IX-CLOCK-12-37", "IX-SCHEDULE-LOAD",
    ):
        assert expected in ids
    assert not {"IX-TREE-HASH-MISMATCH", "IX-FILE-ARITHMETIC", "IX-SECRET-VALUE", "IX-REPO-WRITE"} & ids
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    severities = [f["severity"] for f in findings]
    assert severities == sorted(severities, key=order.get)


def test_summary_tool_and_endpoint() -> None:
    summary = summarise_full_index()
    assert summary["available"] is True and summary["status"] == "ADJACENT_TRACK"
    assert summary["inventory"]["workflows"] == 43 and summary["inventory"]["functions"] == 190
    assert "psicat" in summary["inventory"]["agents"]
    names = {item["name"]: item for item in _tool_manifest()["functions"]}
    assert "args_schema" in names["getMerlinWebspaceIndex"]
    routed = route_tool("getMerlinWebspaceIndex", {})
    assert routed["ok"] is True and routed["result"]["data"]["tree_hash"]["verified"] is True

    from ox_navigator.app.server import serve

    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60.0) as client:
            body = client.get("/api/psicat/webspace-index").json()
            assert body["ok"] is True
            assert body["webspace_index"]["tree_hash"]["recomputed"] == PUBLISHED_TREE_HASH
    finally:
        httpd.shutdown()
        httpd.server_close()
