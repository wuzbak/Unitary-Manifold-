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
        {"id": "PRE-NPMRC-ROTATION", "settled": False,
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
        "reading": ("Steward reports are recorded as claims. The current index predates them, so nothing is verified yet; "
                    "the next published index decides each entry."),
    }
