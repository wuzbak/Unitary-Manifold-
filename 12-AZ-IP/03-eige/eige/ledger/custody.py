# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Chain-of-custody ledger for paper ballots and their containers.

Each event (seal applied, seal verified, seal broken, transfer, container
opened, storage check) must carry at least two Ed25519 sign-offs from distinct
officials (two-person integrity) and is appended to a :class:`MerkleLog`, so
its existence and order can later be proven to observers.

The ledger records what officials attest to; it cannot prove the attestations
are true.  Its value is that later disagreement between paper and record
becomes visible, attributable and timestamped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from ..crypto.signing import KeyRegistry, Signer
from .log import MerkleLog

CUSTODY_CONTEXT = "custody"
EVENT_TYPES = ("seal_applied", "seal_verified", "seal_broken", "transfer", "container_opened", "storage_check")
_REQUIRED = {
    "seal_applied": ("seal_id",),
    "seal_verified": ("seal_id",),
    "seal_broken": ("seal_id", "reason"),
    "transfer": ("from_party", "to_party"),
    "container_opened": ("reason",),
    "storage_check": (),
}
MIN_SIGNOFFS = 2
SIGNED_CUSTODY_TYPE = "custody_v2"


class CustodyError(ValueError):
    """Raised when a custody event is malformed or insufficiently attested."""


@dataclass(frozen=True)
class Signoff:
    official_id: str
    key_id: str
    signature: str

    def as_dict(self) -> dict:
        return {"official_id": self.official_id, "key_id": self.key_id, "signature": self.signature}


def custody_event(event_type: str, container_id: str, location: str, timestamp: int, **details: str) -> dict:
    """Build the unsigned body of a custody event."""
    if event_type not in EVENT_TYPES:
        raise CustodyError(f"unknown custody event type {event_type!r}")
    missing = [k for k in _REQUIRED[event_type] if not details.get(k)]
    if missing:
        raise CustodyError(f"{event_type} requires {', '.join(missing)}")
    if not container_id or not location:
        raise CustodyError("container_id and location are required")
    return {
        "event": event_type,
        "container_id": container_id,
        "location": location,
        "timestamp": int(timestamp),
        "details": {k: str(v) for k, v in sorted(details.items())},
    }


def sign_off(body: dict, official_id: str, signer: Signer) -> Signoff:
    return Signoff(official_id, signer.key_id, signer.sign(CUSTODY_CONTEXT, body))


def validate_bound_body(body: object, log_id: str) -> None:
    """Validate a custody body whose signatures are bound to one log."""
    if not isinstance(body, dict) or set(body) != {
        "event", "container_id", "location", "timestamp", "details", "log_id"
    }:
        raise CustodyError("custody body has missing or unexpected fields")
    if not isinstance(log_id, str) or not log_id or body["log_id"] != log_id:
        raise CustodyError("custody body is not bound to this log")
    if (not isinstance(body["timestamp"], int) or isinstance(body["timestamp"], bool)
            or body["timestamp"] < 0):
        raise CustodyError("custody timestamp must be a non-negative integer")
    if any(not isinstance(body[k], str) or not body[k].strip()
           for k in ("event", "container_id", "location")):
        raise CustodyError("event, container_id and location must be non-empty strings")
    details = body["details"]
    if not isinstance(details, dict) or any(
        not isinstance(k, str) or not k or not isinstance(v, str) for k, v in details.items()
    ):
        raise CustodyError("custody details must map strings to strings")
    if body["event"] not in EVENT_TYPES:
        raise CustodyError(f"unknown custody event type {body['event']!r}")
    missing = [k for k in _REQUIRED[body["event"]] if not details.get(k, "").strip()]
    if missing:
        raise CustodyError(f"{body['event']} requires {', '.join(missing)}")


def validate_signoff(body: dict, signoff: Signoff, registry: KeyRegistry, *, allow_development: bool = True) -> bool:
    if any(not isinstance(v, str) or not v.strip()
           for v in (signoff.official_id, signoff.key_id, signoff.signature)):
        raise CustodyError("sign-off fields must be non-empty strings")
    result = registry.verify(
        signoff.key_id, CUSTODY_CONTEXT, body, signoff.signature, body["timestamp"],
        expected_owner=signoff.official_id, expected_role="official", allow_development=allow_development,
    )
    if not result.valid:
        raise CustodyError(f"sign-off by {signoff.official_id} rejected: {result.reason}")
    return result.development_only


def validate_bound_entry(entry: object, registry: KeyRegistry, log_id: str, *, allow_development: bool = True) -> bool:
    """Validate a log-bound entry; return whether a development key was used."""
    if not isinstance(entry, dict) or set(entry) != {"type", "body", "signoffs"} or entry["type"] != SIGNED_CUSTODY_TYPE:
        raise CustodyError("invalid signed custody entry")
    body = entry["body"]
    validate_bound_body(body, log_id)
    if not isinstance(entry["signoffs"], list):
        raise CustodyError("custody signoffs must be a list")
    officials = set()
    development = False
    for item in entry["signoffs"]:
        if not isinstance(item, dict) or set(item) != {"official_id", "key_id", "signature"}:
            raise CustodyError("invalid custody sign-off fields")
        signoff = Signoff(**item)
        development = validate_signoff(body, signoff, registry, allow_development=allow_development) or development
        officials.add(signoff.official_id)
    if len(officials) < MIN_SIGNOFFS:
        raise CustodyError(f"two-person rule: need {MIN_SIGNOFFS} distinct officials, got {len(officials)}")
    return development


@dataclass
class CustodyScan:
    signed: int = 0
    legacy: int = 0
    failures: int = 0
    examples: List[tuple] = field(default_factory=list)
    development: bool = False

    def observe(self, entry: dict, index: int, registry: KeyRegistry, log_id: str) -> None:
        if entry.get("type") in ("custody", "chain_of_custody"):
            self.legacy += 1
        elif entry.get("type") == SIGNED_CUSTODY_TYPE:
            self.signed += 1
            try:
                self.development = validate_bound_entry(entry, registry, log_id) or self.development
            except CustodyError as exc:
                self.failures += 1
                if len(self.examples) < 10:
                    self.examples.append((index, str(exc)))

    def merge(self, other: "CustodyScan", offset: int) -> None:
        self.signed += other.signed
        self.legacy += other.legacy
        self.failures += other.failures
        self.examples.extend((offset + index, message) for index, message in other.examples[:10 - len(self.examples)])
        self.development = self.development or other.development


@dataclass
class CustodyLedger:
    log: MerkleLog
    registry: KeyRegistry
    _events: List[dict] = field(default_factory=list)

    def record(self, body: dict, signoffs: Sequence[Signoff]) -> int:
        """Validate two-person sign-off and append the event; returns the log index."""
        officials = set()
        for s in signoffs:
            res = self.registry.verify(
                s.key_id, CUSTODY_CONTEXT, body, s.signature, body["timestamp"],
                expected_owner=s.official_id, expected_role="official",
            )
            if not res.valid:
                raise CustodyError(f"sign-off by {s.official_id} rejected: {res.reason}")
            officials.add(s.official_id)
        if len(officials) < MIN_SIGNOFFS:
            raise CustodyError(f"two-person rule: need {MIN_SIGNOFFS} distinct officials, got {len(officials)}")
        entry = {"type": "custody", "body": body, "signoffs": [s.as_dict() for s in signoffs]}
        index = self.log.append(entry)
        self._events.append({**entry, "log_index": index})
        return index

    def history(self, container_id: str) -> List[dict]:
        return [e for e in self._events if e["body"]["container_id"] == container_id]

    def verify_container(self, container_id: str, initial_custodian: Optional[str] = None) -> List[str]:
        """Return human-readable custody issues for a container (empty = none found)."""
        issues: List[str] = []
        current_seal: Optional[str] = None
        custodian = initial_custodian
        last_ts: Optional[int] = None
        for e in self.history(container_id):
            b, d = e["body"], e["body"]["details"]
            where = f"log index {e['log_index']} ({b['event']})"
            if last_ts is not None and b["timestamp"] < last_ts:
                issues.append(f"{where}: timestamp earlier than previous event")
            last_ts = b["timestamp"]
            if b["event"] == "seal_applied":
                if current_seal is not None:
                    issues.append(f"{where}: new seal applied while seal {current_seal} still intact")
                current_seal = d["seal_id"]
            elif b["event"] == "seal_verified":
                if current_seal != d["seal_id"]:
                    issues.append(f"{where}: seal {d['seal_id']} does not match recorded seal {current_seal}")
            elif b["event"] == "seal_broken":
                if current_seal != d["seal_id"]:
                    issues.append(f"{where}: broken seal {d['seal_id']} was not the recorded seal {current_seal}")
                current_seal = None
            elif b["event"] == "container_opened":
                if current_seal is not None:
                    issues.append(f"{where}: container opened without recording seal {current_seal} as broken")
            elif b["event"] == "transfer":
                if custodian is not None and d["from_party"] != custodian:
                    issues.append(f"{where}: transfer from {d['from_party']} but custodian was {custodian}")
                if current_seal is None:
                    issues.append(f"{where}: transferred without an intact seal")
                custodian = d["to_party"]
        return issues

    def events(self) -> List[Dict]:
        return list(self._events)
