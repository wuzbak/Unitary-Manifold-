# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Remediation tracking and a privilege-expansion review for the webspace.

ADJACENT TRACK.  The steward confirmed the three high findings of the full
machine index and plans to widen PsiCat's admin, backend and frontend
access on the webspace.  This module does two things.

1. It applies the remediation register (``data/webspace_remediation_register.json``)
   to the index findings.  A steward report is recorded as a claim.  A
   finding becomes *verified* only when a machine index generated after the
   report shows the fix; an index from before the report can neither verify
   nor contradict it.
2. It ranks the service-role functions with no detected login check by what
   the index metadata says they can reach, so they can be read in a sensible
   order, and lists what should be settled before privileges widen.

The ranking uses metadata only (secrets, outbound hosts, entities, invoked
functions, schedules).  It is a reading order, not a verdict: the index's
own scan can miss checks, and nothing here has read the function source.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .merlin_webspace_index import audit_full_index, backend_posture, load_full_index

STATUS_LABEL = "ADJACENT_TRACK"
REGISTER_PATH = Path(__file__).resolve().parent / "data" / "webspace_remediation_register.json"
SELF_HOST_SUFFIX = "base44.app"
OUTBOUND_MESSAGE_FUNCTIONS = frozenset({"psicatEmailQueue"})


def load_remediation_register(path: str | Path | None = None) -> dict[str, Any]:
    return json.loads(Path(path or REGISTER_PATH).read_text(encoding="utf-8"))


def _index_date(index: dict[str, Any]) -> date | None:
    stamp = str(index.get("provenance", {}).get("generated_at") or "")[:10]
    try:
        return date.fromisoformat(stamp)
    except ValueError:
        return None


def _fix_visible(verification: dict[str, Any], index: dict[str, Any]) -> bool | None:
    backend = index.get("backend", {})
    kind = verification.get("kind")
    if kind == "connector_scopes_absent":
        scopes = set(verification.get("scopes", []))
        for connector in backend.get("connectors", []):
            if connector.get("type") == verification.get("connector"):
                return not scopes & set(connector.get("granted_scopes", []))
        return True
    if kind == "secret_absent":
        return all(s.get("name") != verification.get("secret") for s in backend.get("secrets", []))
    if kind == "service_role_unchecked_absent":
        return not backend_posture(index)["service_role_without_auth_check"]
    if kind == "stale_bundle_credential_absent":
        bundle = next((f for f in index.get("verification_findings", []) if f.get("area") == "source-bundle"), None)
        if bundle is None or bundle.get("status") != "open":
            return True
        return verification.get("file") not in bundle.get("evidence", {}).get("in_bundle_not_in_tree", [])
    return None


def verify_register_entry(entry: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    """Check one register entry against an index; never clears on a stale index."""
    index_date = _index_date(index)
    reported = date.fromisoformat(entry["reported_at"])
    visible = _fix_visible(entry.get("verification", {}), index)
    if visible is None:
        outcome = "manual_evidence_required"
    elif index_date is None or index_date < reported:
        outcome = "awaiting_newer_index"
    elif visible and entry.get("rotation_confirmed") is False:
        outcome = "bundle_clean_rotation_unconfirmed"
    elif visible:
        outcome = "verified"
    elif entry["status"] == "steward_reported_fixed":
        outcome = "contradicted_by_index"
    else:
        outcome = "still_present"
    return {**entry, "index_generated_at": index.get("provenance", {}).get("generated_at"),
            "fix_visible_in_index": visible, "verification_outcome": outcome}


def apply_remediation_register(findings: list[dict[str, Any]], index: dict[str, Any],
                               register: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    register = register or load_remediation_register()
    by_id = {e["finding_id"]: verify_register_entry(e, index) for e in register.get("entries", [])}
    annotated = []
    for finding in findings:
        entry = by_id.get(finding["id"])
        remediation = ({"status": entry["status"], "reported_at": entry["reported_at"],
                        "statement": entry["statement"], "verification_outcome": entry["verification_outcome"],
                        "ledger_note": entry.get("ledger_note")}
                       if entry else {"status": "open", "verification_outcome": "no_report"})
        annotated.append({**finding, "remediation": remediation})
    return annotated


def _function_risk(fn: dict[str, Any], scheduled: set[str]) -> dict[str, Any]:
    hosts = fn.get("external_hosts", [])
    outbound = [h for h in hosts if not h.endswith(SELF_HOST_SUFFIX)]
    self_calls = [h for h in hosts if h.endswith(SELF_HOST_SUFFIX)]
    invoked = fn.get("functions_invoked", [])
    reasons: list[str] = []
    score = 0
    if fn.get("secrets_referenced"):
        score += 3 * len(fn["secrets_referenced"])
        reasons.append(f"uses secret(s) {', '.join(fn['secrets_referenced'])} - an open caller can spend or relay them")
    if outbound:
        score += 2
        reasons.append(f"makes outbound calls ({len(outbound)} host(s)) - open callers can drive traffic and cost")
    if self_calls:
        score += 1
        reasons.append("calls back into the app")
    entities = fn.get("entities_referenced", [])
    if entities:
        score += min(len(entities), 4)
        reasons.append(f"touches {len(entities)} {'entity' if len(entities) == 1 else 'entities'} "
                       f"with service privileges: {', '.join(entities)}")
    if invoked:
        score += len(invoked)
        reasons.append(f"invokes {', '.join(invoked)}")
    if OUTBOUND_MESSAGE_FUNCTIONS & set(invoked):
        score += 2
        reasons.append("can queue outbound email")
    lowered = fn["name"].lower()
    if "proxy" in lowered or "admin" in lowered:
        score += 2
        reasons.append("a proxy or admin-verification function: the place a missed check costs most")
    if fn["name"] in scheduled:
        score += 1
        reasons.append("run by a schedule - should accept platform-scheduled calls only")
    tier = "read_first" if score >= 6 else "read_next" if score >= 3 else "read_last"
    return {"name": fn["name"], "score": score, "tier": tier, "reasons": reasons,
            "conditionals": fn.get("ast_counts", {}).get("conditionals"),
            "source_ref": fn.get("source_ref")}


def privilege_expansion_review(index: dict[str, Any] | None = None) -> dict[str, Any]:
    index = index or load_full_index()
    if not index:
        return {"status_label": STATUS_LABEL, "available": False}
    backend = index.get("backend", {})
    posture = backend_posture(index)
    by_name = {f["name"]: f for f in backend.get("functions", [])}
    scheduled = {c for w in backend.get("workflows", []) if w.get("trigger_type") == "scheduled"
                 for c in w.get("calls_functions", [])}
    ranked = sorted((_function_risk(by_name[n], scheduled) for n in posture["service_role_without_auth_check"]),
                    key=lambda r: (-r["score"], r["name"]))
    tiers = {t: [r["name"] for r in ranked if r["tier"] == t] for t in ("read_first", "read_next", "read_last")}
    admin_entities = sorted(e["name"] for e in backend.get("entities", []) if "admin" in json.dumps(e.get("rls")))
    no_rls_entities = sorted(e["name"] for e in backend.get("entities", []) if e.get("rls") is None)
    write_connectors = [c for c in posture["connectors"] if c["write_capable_scopes"]]
    register = {e["finding_id"]: verify_register_entry(e, index) for e in load_remediation_register()["entries"]}
    preconditions = [
        {"id": "PRE-GITHUB-READ-ONLY", "settled": register["IX-GITHUB-WRITE-SCOPE"]["verification_outcome"] == "verified",
         "state": register["IX-GITHUB-WRITE-SCOPE"]["verification_outcome"],
         "what": "GitHub connector carries no write scope. Steward reports this done; a newer index must show it."},
        {"id": "PRE-DELETE-UNUSED-TOKEN", "settled": register["IX-UNREFERENCED-SECRETS"]["verification_outcome"] == "verified",
         "state": register["IX-UNREFERENCED-SECRETS"]["verification_outcome"],
         "what": "Delete PSICAT_GITHUB_TOKEN; no function uses it."},
        {"id": "PRE-NPMRC-ROTATION",
         "settled": register["IX-STALE-BUNDLE-CREDENTIAL-FILE"]["verification_outcome"] == "verified",
         "state": register["IX-STALE-BUNDLE-CREDENTIAL-FILE"]["verification_outcome"],
         "what": "Open the .npmrc in the stale public bundle; rotate any token in it; withdraw the bundle."},
        {"id": "PRE-READ-FIRST-FUNCTIONS", "settled": False, "state": "unread",
         "what": f"Read the {len(tiers['read_first'])} read-first functions and either confirm a check the scan missed or add one."},
        {"id": "PRE-LINKEDIN-WRITE", "settled": False, "state": "write_capable" if any(
            c["type"] == "linkedin" for c in write_connectors) else "absent",
         "what": "LinkedIn connector holds w_organization_social (posting as the organisation). Confirm it is intended and gated by steward approval before PsiCat gains wider control."},
        {"id": "PRE-ADMIN-SCOPE-KNOWN", "settled": False, "state": "listed",
         "what": f"Admin role reaches {len(admin_entities)} admin-gated entities and every function marked admin-only; "
                 "grant it knowing that list."},
        {"id": "PRE-RLS-UNDECLARED", "settled": False, "state": "listed",
         "what": f"{len(no_rls_entities)} entities declare no row-level rules ({', '.join(no_rls_entities)}); "
                 "confirm the platform default before widening access."},
        {"id": "PRE-REPUBLISH-INDEX", "settled": False, "state": "pending",
         "what": "Publish a fresh machine index after the changes so each register entry can move to verified."},
    ]
    return {
        "status_label": STATUS_LABEL,
        "available": True,
        "index_generated_at": index.get("provenance", {}).get("generated_at"),
        "method": ("Metadata-only ranking of service-role functions with no detected login check. "
                   "A reading order, not a verdict; the index scan can miss checks and no source was read."),
        "function_count": len(ranked),
        "tiers": tiers,
        "ranked": ranked,
        "admin_gated_entities": admin_entities,
        "entities_without_declared_rls": no_rls_entities,
        "write_capable_connectors": write_connectors,
        "preconditions": preconditions,
        "ready_to_expand": all(p["settled"] for p in preconditions),
    }


def summarise_remediation(index: dict[str, Any] | None = None) -> dict[str, Any]:
    index = index or load_full_index()
    if not index:
        return {"status_label": STATUS_LABEL, "available": False}
    findings = apply_remediation_register(audit_full_index(index), index)
    tracked = [f for f in findings if f["remediation"]["status"] != "open" or f["id"] in
               {e["finding_id"] for e in load_remediation_register()["entries"]}]
    review = privilege_expansion_review(index)
    return {
        "status_label": STATUS_LABEL,
        "available": True,
        "tracked_findings": [{"id": f["id"], "severity": f["severity"], **f["remediation"]} for f in tracked],
        "privilege_expansion": {k: review[k] for k in ("function_count", "tiers", "preconditions", "ready_to_expand")},
        "stale_bundle_exposure": stale_bundle_exposure(index),
        "stored_indexes": [p.name for p in stored_index_paths()],
        "reading": ("Steward reports are recorded as claims. The current index predates them, so nothing is verified yet; "
                    "the next published index decides each entry."),
    }


# ---------------------------------------------------------------------------
# The stale bundle: how the .npmrc can be reached
# ---------------------------------------------------------------------------

def stale_bundle_exposure(index: dict[str, Any] | None = None) -> dict[str, Any]:
    """What the index says about the stale source bundle and who can read it."""
    index = index or load_full_index()
    if not index:
        return {"available": False}
    finding = next((f for f in index.get("verification_findings", []) if f.get("area") == "source-bundle"), {})
    evidence = finding.get("evidence", {})
    url = str(evidence.get("url") or "")
    functions = {f["name"]: f for f in index.get("backend", {}).get("functions", [])}
    readers = {name: {"admin_only": functions[name].get("admin_only"), "auth_checked": functions[name].get("auth_checked")}
               for name in ("readSourceFile", "listSourceFiles") if name in functions}
    agent_told_to_read = [a["name"] for a in index.get("backend", {}).get("agents", [])
                          if "readSourceFile" in str(a.get("system_prompt", ""))]
    excluded = [e["pattern"] for e in index.get("redaction", {}).get("exclusions", [])]
    in_bundle_only = evidence.get("in_bundle_not_in_tree", [])
    return {
        "available": bool(finding),
        "status": finding.get("status"),
        "bundle_url": url,
        "public_path": "/public/" in url,
        "url_published_in_index": bool(url),
        "bundle_file_count": evidence.get("bundle_file_count"),
        "tree_file_count": evidence.get("tree_file_count"),
        "credential_type_files_in_bundle": [p for p in in_bundle_only if p in excluded or p.startswith(".env")],
        "in_app_readers": readers,
        "agents_instructed_to_read_source": agent_told_to_read,
        "reading": (
            "The bundle sits under a public file path and the index publishes its URL, so the admin-only readers do "
            "not protect it: anyone with the URL can download it. The psicat agent is told to read its own source "
            "through readSourceFile; with admin rights it can also read the stale bundle, .npmrc included. "
            "Inspect the file, rotate anything in it, and delete or replace the bundle before widening PsiCat's access."
        ),
    }


# ---------------------------------------------------------------------------
# A newer index: ingest, verify, compare
# ---------------------------------------------------------------------------

def stored_index_paths() -> list[Path]:
    from .merlin_webspace_index import RAW_DIR

    return sorted(RAW_DIR.glob("machine_index_*.json.gz"))


def ingest_index_file(path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load a machine index from .json, .json.gz or a PDF export; return it with an intake record."""
    import gzip as _gzip

    from .merlin_webspace_index import extract_pdf_text, reconstruct_index, redact_phone_shaped_strings, verify_tree_hash

    source = Path(path)
    intake: dict[str, Any] = {"source_file": source.name}
    if source.suffix.lower() == ".pdf":
        index, counts = reconstruct_index(extract_pdf_text(source))
        intake["normalisation_rule_counts"] = counts
    elif source.suffix.lower() == ".gz":
        with _gzip.open(source, "rt", encoding="utf-8") as handle:
            index = json.load(handle)
    else:
        index = json.loads(source.read_text(encoding="utf-8"))
    intake["phone_shaped_samples_withheld"] = redact_phone_shaped_strings(index)
    intake["tree_hash_check"] = verify_tree_hash(index)
    intake["generated_at_by_webspace"] = index.get("provenance", {}).get("generated_at")
    return index, intake


def _names(items: list[dict[str, Any]], key: str = "name") -> set[str]:
    return {str(i.get(key)) for i in items}


def compare_indexes(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """What changed between two machine indexes, in the terms the findings use."""
    old_files, new_files = old.get("hashes", {}).get("files", {}), new.get("hashes", {}).get("files", {})
    changed = sorted(p for p in set(old_files) & set(new_files)
                     if old_files[p].get("sha256") != new_files[p].get("sha256"))
    old_b, new_b = old.get("backend", {}), new.get("backend", {})
    old_p, new_p = backend_posture(old), backend_posture(new)

    def scopes(posture: dict[str, Any]) -> dict[str, list[str]]:
        return {str(c["type"]): sorted(c["granted_scopes"]) for c in posture["connectors"]}

    old_scopes, new_scopes = scopes(old_p), scopes(new_p)
    old_unchecked, new_unchecked = set(old_p["service_role_without_auth_check"]), set(new_p["service_role_without_auth_check"])
    return {
        "old_generated_at": old.get("provenance", {}).get("generated_at"),
        "new_generated_at": new.get("provenance", {}).get("generated_at"),
        "files": {"added": sorted(set(new_files) - set(old_files)), "removed": sorted(set(old_files) - set(new_files)),
                  "changed": changed},
        "functions": {"added": sorted(_names(new_b.get("functions", [])) - _names(old_b.get("functions", []))),
                      "removed": sorted(_names(old_b.get("functions", [])) - _names(new_b.get("functions", [])))},
        "service_role_without_auth_check": {"now_checked_or_gone": sorted(old_unchecked - new_unchecked),
                                            "newly_flagged": sorted(new_unchecked - old_unchecked),
                                            "count": [len(old_unchecked), len(new_unchecked)]},
        "connector_scopes": {t: {"before": old_scopes.get(t), "after": new_scopes.get(t)}
                             for t in sorted(set(old_scopes) | set(new_scopes)) if old_scopes.get(t) != new_scopes.get(t)},
        "secrets": {"added": sorted(_names(new_b.get("secrets", [])) - _names(old_b.get("secrets", []))),
                    "removed": sorted(_names(old_b.get("secrets", [])) - _names(new_b.get("secrets", [])))},
        "stale_bundle": {"before": stale_bundle_exposure(old).get("status"), "after": stale_bundle_exposure(new).get("status")},
        "register": [{"finding_id": e["finding_id"], **{k: v for k, v in verify_register_entry(e, new).items()
                                                         if k in ("verification_outcome", "fix_visible_in_index")}}
                     for e in load_remediation_register()["entries"]],
    }


def store_index(index: dict[str, Any], intake: dict[str, Any]) -> Path:
    """Store a verified newer index beside the first one, with its intake sidecar."""
    import gzip as _gzip
    import hashlib as _hashlib

    from .merlin_webspace_index import RAW_DIR

    if not intake["tree_hash_check"]["verified"]:
        raise ValueError("refusing to store an index whose tree hash does not reproduce")
    stamp = str(index.get("provenance", {}).get("generated_at") or "")[:10]
    target = RAW_DIR / f"machine_index_{stamp}.json.gz"
    raw = json.dumps(index, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if target.exists():
        with _gzip.open(target, "rb") as handle:
            if handle.read() != raw:
                raise FileExistsError(f"{target.name} already holds a different index; it will not be overwritten")
    with _gzip.GzipFile(target, "wb", mtime=0) as handle:
        handle.write(raw)
    sidecar = {**intake, "stored_json_sha256": _hashlib.sha256(raw).hexdigest()}
    target.with_name(f"machine_index_{stamp}.provenance.json").write_text(json.dumps(sidecar, indent=2) + "\n",
                                                                          encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin CLI over tested functions
    import argparse

    parser = argparse.ArgumentParser(description="Ingest a newer webspace machine index and verify the register.")
    parser.add_argument("path", help="machine-index .json, .json.gz, or a PDF export of it")
    parser.add_argument("--store", action="store_true", help="store it under data/raw/ if the tree hash reproduces")
    args = parser.parse_args(argv)
    new, intake = ingest_index_file(args.path)
    report = {"intake": intake, "comparison": compare_indexes(load_full_index(), new)}
    if args.store:
        report["stored_at"] = str(store_index(new, intake))
    print(json.dumps(report, indent=2, default=str))
    return 0 if intake["tree_hash_check"]["verified"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
