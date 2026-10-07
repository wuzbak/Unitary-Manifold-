# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Read-only policy and release-evidence gate; not legal certification."""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
from urllib.parse import urlsplit

POLICY_ID = "AZ-RECIPROCITY-2026-10-07"
REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = "9-INFRASTRUCTURE/licensing_policy.json"
DOCUMENTS = ("LICENSE", "LICENSE-AGPL", "LEGAL.md", "docs/policy/COMMERCIAL_TERMS.md")
SOFTWARE_LOCATIONS = (
    "src", "tests", "recycling", "scripts", "submission",
    "5-GOVERNANCE/Unitary Pentad", "omega", "bot", "embryology-manifold",
    "12-AZ-IP", "TOOLS", "9-INFRASTRUCTURE", "public-site",
)
MAX_JSON_BYTES = 1_048_576


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key.")
        result[key] = value
    return result


def read_object(path: Path) -> dict:
    with path.open("rb") as stream:
        data = stream.read(MAX_JSON_BYTES + 1)
    if len(data) > MAX_JSON_BYTES:
        raise ValueError("JSON evidence exceeds size limit.")
    value = json.loads(data, object_pairs_hook=_unique_object)
    if not isinstance(value, dict):
        raise TypeError("Expected a JSON object.")
    return value


def check_policy(root: Path) -> list[str]:
    """Check immutable safety boundaries and indexed document identifiers."""
    try:
        policy = read_object(root / POLICY_PATH)
    except (OSError, ValueError, TypeError, RecursionError):
        return ["Policy is missing or invalid JSON."]
    expected = {
        "schema_version": 1,
        "policy_id": POLICY_ID,
        "effective_date": "2026-10-07",
        "issuer": "AxiomZero Technologies & Consulting, SPC",
        "software_default": "AGPL-3.0-or-later",
        "scope_rule": "copyright-retained-first-party-software-only",
        "software_locations": list(SOFTWARE_LOCATIONS),
        "safeguards": {
            "preserve_prior_grants": True,
            "asset_notices_and_upstream_terms_control": True,
            "no_extra_agpl_restrictions": True,
            "no_automatic_ai_copyleft": True,
            "no_telemetry_or_remote_disabling": True,
            "no_automatic_exception_approval": True,
        },
        "exceptions": {
            "consideration": ["payment", "partnership"],
            "requires_executed_authorized_agreement": True,
            "requires_rights_review": True,
            "does_not_reduce_public_rights": True,
        },
        "contract_forum": {
            "requires_affirmative_acceptance": True,
            "governing_state": "Washington",
            "state_venue": "King County, Washington",
            "federal_venue": "Western District of Washington at Seattle",
            "subject_to_mandatory_law": True,
            "not_an_agpl_condition": True,
        },
        "documents": list(DOCUMENTS),
        "gate_limit": "structural-evidence-only-not-legal-certification",
    }
    errors = []
    # JSON comparison preserves the distinction between booleans and integers.
    if json.dumps(policy, sort_keys=True) != json.dumps(expected, sort_keys=True):
        errors.append("Policy differs from the approved scope and safety boundaries.")
    for name in DOCUMENTS:
        path = root / name
        try:
            if not path.resolve().is_relative_to(root.resolve()):
                errors.append("Indexed document escapes repository.")
            elif POLICY_ID not in path.read_text(encoding="utf-8"):
                errors.append(f"Missing policy identifier in {name}.")
        except (OSError, UnicodeError):
            errors.append(f"Missing or unreadable indexed document: {name}.")
    return errors


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 2048


def _public_https(value: object) -> bool:
    if not _text(value) or any(char.isspace() or ord(char) < 32 for char in value):
        return False
    try:
        url = urlsplit(value)
        host = url.hostname
        if (
            url.scheme != "https" or not host or url.username is not None
            or url.password is not None or url.fragment or url.query
            or url.port not in (None, 443)
        ):
            return False
        if host.lower() == "localhost" or host.lower().endswith((".localhost", ".local")):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return "." in host and all(part for part in host.split("."))
    except ValueError:
        return False


def check_release(evidence: dict) -> tuple[list[str], bool]:
    """Validate declarations offline; never authenticate or approve exceptions."""
    errors = []
    if evidence.get("policy_id") != POLICY_ID:
        errors.append("Release must identify the current policy.")
    if not _text(evidence.get("release_id")):
        errors.append("Release identifier is required.")
    activity = evidence.get("activity")
    if activity not in ("distribution", "modified_network", "private"):
        errors.append("Activity must be distribution, modified_network or private.")
    mode = evidence.get("mode")
    if mode not in ("public", "exception"):
        errors.append("Mode must be public or exception.")
    if mode == "exception":
        if not _text(evidence.get("agreement_reference")):
            errors.append("A non-sensitive agreement reference is required for review.")
        return errors, True
    if mode == "public" and activity in ("distribution", "modified_network"):
        if evidence.get("license") != "AGPL-3.0-or-later":
            errors.append("Covered public release must declare AGPL-3.0-or-later.")
        if not _public_https(evidence.get("source_url")):
            errors.append("Source URL must be HTTPS without credentials, queries or fragments.")
        if not _text(evidence.get("source_revision")):
            errors.append("Source revision is required.")
        if evidence.get("source_offer_visible") is not True:
            errors.append("A visible source offer must be declared.")
        if evidence.get("source_access") != "public-no-auth":
            errors.append("AxiomZero releases must declare public, unauthenticated source access.")
    return errors, False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--release-manifest", type=Path)
    args = parser.parse_args(argv)
    errors = check_policy(args.root)
    review = False
    if args.release_manifest is not None:
        try:
            evidence = read_object(args.release_manifest)
            release_errors, review = check_release(evidence)
            errors.extend(release_errors)
        except (OSError, ValueError, TypeError, RecursionError):
            errors.append("Release manifest is missing or invalid JSON.")
    status = (
        "invalid_evidence" if errors else
        "authorized_agreement_review_required" if review else
        "structural_evidence_checks_passed"
    )
    print(json.dumps({
        "policy_id": POLICY_ID,
        "status": status,
        "errors": errors,
        "legal_certification": False,
        "network_access_performed": False,
        "exception_authorized": False,
    }, sort_keys=True))
    return 1 if errors else 2 if review else 0


if __name__ == "__main__":
    raise SystemExit(main())
