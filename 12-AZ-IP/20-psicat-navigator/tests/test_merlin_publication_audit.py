# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import copy
import gzip
import hashlib
import json
import threading

import httpx

from ox_navigator.engine.merlin_publication_audit import (
    EXPORTS_PATH,
    PAGE_BREAK,
    audit_exports,
    build_corrections,
    check_claims,
    contents_page_check,
    glyph_check,
    is_letter_spaced,
    library_counts,
    load_exports,
    load_exports_provenance,
    load_live_registry,
    parse_publications,
    publication_inventory,
    summarise_exports,
)
from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool
from ox_navigator.engine.merlin_webspace_index import load_full_index
from ox_navigator.engine.merlin_webspace_remediation import (
    apply_remediation_register,
    compare_indexes,
    ingest_index_file,
    stale_bundle_exposure,
    store_index,
    load_remediation_register,
    privilege_expansion_review,
    summarise_remediation,
    verify_register_entry,
)


def _index_titles() -> list[str]:
    return [p["title"] for p in load_full_index()["content"]["articles_source"]["published"]]


def test_export_texts_match_provenance() -> None:
    exports = load_exports()
    provenance = load_exports_provenance()
    assert set(exports) == {"publications", "comic_shop", "knowledge_library"}
    for name, text in exports.items():
        source = provenance["sources"][name]
        assert hashlib.sha256(text.encode()).hexdigest() == source["text_sha256"]
        assert text.count(PAGE_BREAK) + 1 == source["pages"]
        assert len(source["upload_commit"]) == 40 and len(source["pdf_sha256"]) == 64
    raw = gzip.decompress(EXPORTS_PATH.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == provenance["stored_json_sha256"]
    assert {n: provenance["sources"][n]["pages"] for n in exports} == {
        "publications": 118, "comic_shop": 16, "knowledge_library": 53}


def test_publications_match_index_inventory() -> None:
    works = parse_publications(load_exports()["publications"], _index_titles())
    inventory = publication_inventory(works, load_full_index())
    assert inventory["works_in_pdf"] == inventory["works_in_index"] == 36
    assert inventory["titles_matched_to_index"] == 36
    assert inventory["index_titles_missing_from_pdf"] == [] and inventory["category_mismatches"] == []
    assert inventory["date_offset_days_index_minus_pdf"] == {1: 36}
    dup = inventory["duplicate_titles_in_pdf"]
    assert [d["positions"] for d in dup] == [[15, 28]] and dup[0]["identical_opening"] is False


def test_claims_against_live_registry() -> None:
    works = parse_publications(load_exports()["publications"], _index_titles())
    claims = check_claims(works, load_live_registry())
    verdicts = {(c["rule"], c["verdict"]) for c in claims}
    for rule in ("NS-VALUE", "NS-PULL", "KCS-VALUE", "CS-VALUE", "BETA-VALUE", "DESI-SIGMA", "JUNO-SIGMA"):
        assert (rule, "consistent") in verdicts and (rule, "contradicts") not in verdicts
    assert ("R-STATUS", "contradicts") in verdicts
    assert ("CMB-IRREDUCIBLE", "contradicts") in verdicts
    assert ("DESI-LABEL", "contradicts") in verdicts
    assert ("TEST-COUNT", "stale") in verdicts
    assert ("LEAN-SCOPE", "omits") in verdicts


def test_claim_rules_follow_registry_changes() -> None:
    works = [{"title": "t", "position": 1, "text": "The Unitary Manifold Framework predicts n_s ~= 0.9635. "
              "It predicts r ~= 0.0315 and the prediction holds."}]
    registry = copy.deepcopy(load_live_registry())
    rows = check_claims(works, registry)
    assert {r["rule"]: r["verdict"] for r in rows} == {"NS-VALUE": "consistent", "R-STATUS": "contradicts"}
    for item in registry["predictions"]:
        if item["id"] == "EXP-4":
            item["status"] = "CONSISTENT"
    registry["physics"]["cmb_spectral_index_n_s"] = 0.9700
    rows = check_claims(works, registry)
    assert {r["rule"]: r["verdict"] for r in rows} == {"NS-VALUE": "contradicts", "R-STATUS": "consistent"}


def test_rendering_checks() -> None:
    exports = load_exports()
    for name, entries in (("publications", 36), ("comic_shop", 15), ("knowledge_library", 4)):
        toc = contents_page_check(exports[name])
        assert toc["matched_entries"] == entries == toc["wrong_page_entries"]
        assert toc["each_entry_points_to_next_work"] is True
        assert toc["entries_beyond_last_page"] == [entries]
    assert glyph_check(exports["publications"])["lines_with_mangled_glyphs"] > 0
    assert glyph_check(exports["knowledge_library"])["lines_with_mangled_glyphs"] == 0
    assert is_letter_spaced(" T h e   S t r o n g   F o r c e") and not is_letter_spaced("The Strong Force")
    synthetic = "Contents\n01 A ...... 2\n02 B ...... 3" + PAGE_BREAK + "T1\nx" + PAGE_BREAK + "T2\ny"
    assert contents_page_check(synthetic)["wrong_page_entries"] == 0


def test_library_counts_reproduce() -> None:
    lib = library_counts(load_exports()["knowledge_library"])
    assert lib["tiers_reproduce"] is True and lib["counted_tiers"] == {"T1": 135, "T2": 80, "T3": 16, "T5": 1}
    assert lib["unique_links"] == lib["entries"] == 232
    assert all(d["declared"] in (None, d["sum_of_domain_counts"]) for d in lib["domain_sums"].values())
    assert (lib["declared_api"], lib["entries_marked_programmatic_api"]) == (14, 9)


def test_export_findings() -> None:
    report = audit_exports()
    ids = {f["id"]: f["severity"] for f in report["findings"]}
    assert ids["PX-R-TENSION-OMITTED"] == "high" and ids["PX-CMB-IRREDUCIBLE-RETIRED"] == "high"
    for fid in ("PX-CONTENTS-PAGES", "PX-GLYPH-CORRUPTION", "PX-DESI-MISSTATED", "PX-PROOF-OVERSTATED"):
        assert ids[fid] == "medium"
    assert "PX-VALUE-MISMATCH" not in ids and "PX-INVENTORY-MISMATCH" not in ids
    assert {"PX-VALUES-CONSISTENT", "PX-INVENTORY-MATCHES", "PX-LIBRARY-COUNTS-VERIFIED"} <= set(ids)
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    severities = [f["severity"] for f in report["findings"]]
    assert severities == sorted(severities, key=order.get)


def test_register_never_clears_on_older_index() -> None:
    index = load_full_index()
    entry = next(e for e in load_remediation_register()["entries"] if e["finding_id"] == "IX-GITHUB-WRITE-SCOPE")
    assert verify_register_entry(entry, index)["verification_outcome"] == "awaiting_newer_index"
    newer = copy.deepcopy(index)
    newer["provenance"]["generated_at"] = "2026-10-09T00:00:00Z"
    assert verify_register_entry(entry, newer)["verification_outcome"] == "contradicted_by_index"
    for connector in newer["backend"]["connectors"]:
        if connector["type"] == "github":
            connector["granted_scopes"] = ["read:user"]
    assert verify_register_entry(entry, newer)["verification_outcome"] == "verified"
    annotated = apply_remediation_register([{"id": "IX-GITHUB-WRITE-SCOPE"}, {"id": "IX-OTHER"}], index)
    assert annotated[0]["remediation"]["status"] == "steward_reported_fixed"
    assert annotated[1]["remediation"] == {"status": "open", "verification_outcome": "no_report"}


def test_privilege_expansion_review() -> None:
    review = privilege_expansion_review()
    assert review["function_count"] == 41 == sum(len(v) for v in review["tiers"].values())
    assert {"elevenlabsProxy", "watchlistScan", "psicatStewardDigest"} <= set(review["tiers"]["read_first"])
    scores = [r["score"] for r in review["ranked"]]
    assert scores == sorted(scores, reverse=True)
    assert review["ready_to_expand"] is False
    pre = {p["id"]: p for p in review["preconditions"]}
    assert pre["PRE-GITHUB-READ-ONLY"]["state"] == "awaiting_newer_index"
    assert pre["PRE-LINKEDIN-WRITE"]["state"] == "write_capable"
    assert "User" in review["entities_without_declared_rls"]


def test_tools_and_endpoints() -> None:
    names = {item["name"]: item for item in _tool_manifest()["functions"]}
    for tool in ("getMerlinWebspaceRemediation", "getMerlinPublicationAudit"):
        assert "args_schema" in names[tool]
        assert route_tool(tool, {})["ok"] is True
    assert summarise_exports()["works"] == 36
    tracked = {t["id"]: t for t in summarise_remediation()["tracked_findings"]}
    assert tracked["IX-STALE-BUNDLE-CREDENTIAL-FILE"]["verification_outcome"] == "awaiting_newer_index"

    from ox_navigator.app.server import serve

    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60.0) as client:
            body = client.get("/api/psicat/webspace-remediation").json()
            assert body["ok"] is True and body["webspace_remediation"]["privilege_expansion"]["function_count"] == 41
            body = client.get("/api/psicat/publication-audit").json()
            assert body["ok"] is True and body["publication_audit"]["severity_counts"]["high"] == 2
            assert json.dumps(body)
    finally:
        httpd.shutdown()
        httpd.server_close()


def _newer_index() -> dict:
    newer = copy.deepcopy(load_full_index())
    newer["provenance"]["generated_at"] = "2026-10-09T00:00:00Z"
    return newer


def test_stale_bundle_exposure() -> None:
    exposure = stale_bundle_exposure()
    assert exposure["public_path"] is True
    assert ".npmrc" in exposure["credential_type_files_in_bundle"]
    assert "psicat" in exposure["agents_instructed_to_read_source"]


def test_compare_indexes_with_simulated_fixes() -> None:
    old, newer = load_full_index(), _newer_index()
    for connector in newer["backend"]["connectors"]:
        if connector["type"] == "github":
            connector["granted_scopes"] = ["read:user"]
    unreferenced = next(e for e in load_remediation_register()["entries"]
                        if e["finding_id"] == "IX-UNREFERENCED-SECRETS")
    gone = {unreferenced["verification"]["secret"]}
    newer["backend"]["secrets"] = [s for s in newer["backend"]["secrets"] if s.get("name") not in gone]
    diff = compare_indexes(old, newer)
    outcomes = {r["finding_id"]: r["verification_outcome"] for r in diff["register"]}
    assert outcomes["IX-GITHUB-WRITE-SCOPE"] == "verified"
    assert outcomes["IX-SERVICE-ROLE-UNAUTHENTICATED"] == "still_present"
    assert diff["connector_scopes"]["github"]["after"] == ["read:user"]
    assert diff["files"] == {"added": [], "removed": [], "changed": []}
    assert outcomes["IX-UNREFERENCED-SECRETS"] == "verified"
    assert set(diff["secrets"]["removed"]) == gone


def test_clean_bundle_still_needs_rotation() -> None:
    newer = _newer_index()
    bundle = next(f for f in newer["verification_findings"] if f.get("area") == "source-bundle")
    bundle["evidence"]["in_bundle_not_in_tree"] = [p for p in bundle["evidence"]["in_bundle_not_in_tree"]
                                                   if p != ".npmrc"]
    entry = next(e for e in load_remediation_register()["entries"]
                 if e["finding_id"] == "IX-STALE-BUNDLE-CREDENTIAL-FILE")
    assert verify_register_entry(entry, load_full_index())["verification_outcome"] == "awaiting_newer_index"
    assert verify_register_entry(entry, newer)["verification_outcome"] == "bundle_clean_rotation_unconfirmed"
    confirmed = copy.deepcopy(entry)
    confirmed["rotation_confirmed"] = True
    assert verify_register_entry(confirmed, newer)["verification_outcome"] == "verified"


def test_ingest_and_store_index(tmp_path, monkeypatch) -> None:
    from ox_navigator.engine import merlin_webspace_index

    monkeypatch.setattr(merlin_webspace_index, "RAW_DIR", tmp_path)
    newer = _newer_index()
    source = tmp_path / "upload.json"
    source.write_text(json.dumps(newer), encoding="utf-8")
    index, intake = ingest_index_file(source)
    assert intake["tree_hash_check"]["verified"] is True
    stored = store_index(index, intake)
    assert stored.name == "machine_index_2026-10-09.json.gz"
    assert store_index(index, intake) == stored
    with gzip.open(stored, "rt", encoding="utf-8") as handle:
        assert json.load(handle)["provenance"]["generated_at"] == "2026-10-09T00:00:00Z"
    tampered = copy.deepcopy(index)
    next(iter(tampered["hashes"]["files"].values()))["sha256"] = "0" * 64
    _, bad = ingest_index_file(_write(tmp_path / "bad.json", tampered))
    assert bad["tree_hash_check"]["verified"] is False
    try:
        store_index(tampered, bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unverified index was stored")
    tampered["hashes"]["files"] = index["hashes"]["files"]
    tampered["provenance"]["note"] = "different"
    try:
        store_index(tampered, intake)
    except FileExistsError:
        pass
    else:
        raise AssertionError("existing index was overwritten")


def _write(path, payload) -> object:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_correction_packet() -> None:
    summary = summarise_exports()
    corrections = summary["corrections"]
    assert summary["articles_needing_correction"] == sorted({c["position"] for c in corrections})
    assert {"R-STATUS", "CMB-IRREDUCIBLE", "HARDGATE-MEANING"} <= {c["rule"] for c in corrections}
    for c in corrections:
        assert c["sentence"] and "page " not in c["sentence"] and c["suggested_wording"]
    r_fix = next(c for c in corrections if c["rule"] == "R-STATUS")["suggested_wording"]
    registry = copy.deepcopy(load_live_registry())
    exp = next(p for p in registry["predictions"] if p["id"] == "EXP-4")
    exp["verdict"] = "SENTINEL VERDICT."
    assert exp["status"] in r_fix
    report = audit_exports(registry=registry)
    assert any("SENTINEL VERDICT." in c["suggested_wording"] for c in report["corrections"])
