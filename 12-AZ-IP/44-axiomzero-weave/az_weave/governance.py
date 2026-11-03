# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Durable before-effect authorization; authenticated hosts supply principals."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
from typing import Callable, Any
from uuid import uuid4

from . import OBLIGATIONS

POLICY = "az-weave-pentad-v1"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class AuthorizationError(ValueError):
    """A requested transition is not authorized."""


class Journal:
    """Local identity is established by the CLI/HTTP host, never model text.

    Audit digests detect accidental changes; they are not signatures. A crash
    during a claimed effect leaves an ambiguous outcome and cannot auto-retry.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        if self.path.is_symlink() or self.path.parent.is_symlink():
            raise ValueError("journal must not be a symlink")
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY, principal TEXT NOT NULL, action TEXT NOT NULL,
                    args_hash TEXT NOT NULL, sources TEXT NOT NULL, policy TEXT NOT NULL,
                    expires REAL NOT NULL, state TEXT NOT NULL, result TEXT, error TEXT);
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, at REAL NOT NULL,
                    decision_id TEXT NOT NULL, state TEXT NOT NULL,
                    previous TEXT NOT NULL, hash TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS active_effect (
                    slot INTEGER PRIMARY KEY CHECK(slot=1), decision_id TEXT NOT NULL);
            """)
        os.chmod(self.path, 0o600)

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def _event(db: sqlite3.Connection, decision_id: str, state: str) -> None:
        row = db.execute("SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        previous = row["hash"] if row else ""
        at = time.time()
        hashed = digest([at, decision_id, state, previous])
        db.execute("INSERT INTO events(at,decision_id,state,previous,hash) VALUES(?,?,?,?,?)",
                   (at, decision_id, state, previous, hashed))

    def approve(self, principal: str, action: str, arguments: dict, *,
                obligations: dict, sources: list[dict], ttl: int = 300) -> str:
        if not isinstance(principal, str) or not principal.strip() or len(principal) > 200:
            raise AuthorizationError("authenticated principal required")
        if not isinstance(action, str) or not action or len(action) > 100:
            raise AuthorizationError("action required")
        if not isinstance(arguments, dict) or len(canonical(arguments)) > 200_000:
            raise AuthorizationError("bounded argument object required")
        if type(ttl) is not int or not 1 <= ttl <= 3600:
            raise AuthorizationError("expiry must be between 1 and 3600 seconds")
        if not isinstance(obligations, dict) or set(obligations) != set(OBLIGATIONS):
            raise AuthorizationError("all independent Pentad obligations must be reviewed")
        if any(value != "PASS" for value in obligations.values()):
            raise AuthorizationError("unknown, pending or failed obligations cannot authorize effects")
        identifier = uuid4().hex
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (identifier, principal, action, digest(arguments), canonical(sources),
                        POLICY, time.time() + ttl, "APPROVED", None, None))
            self._event(db, identifier, "APPROVED")
        return identifier

    def get(self, identifier: str, principal: str) -> dict:
        with self.connect() as db:
            row = db.execute("SELECT * FROM decisions WHERE id=? AND principal=?",
                             (identifier, principal)).fetchone()
        if row is None:
            raise AuthorizationError("decision not found for this principal")
        result = dict(row)
        result["sources"] = json.loads(result["sources"])
        if result["result"] is not None:
            result["result"] = json.loads(result["result"])
        return result

    def revoke(self, identifier: str, principal: str) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            changed = db.execute(
                "UPDATE decisions SET state='REVOKED' WHERE id=? AND principal=? AND state='APPROVED'",
                (identifier, principal)).rowcount
            if not changed:
                raise AuthorizationError("only an unclaimed approval can be revoked")
            self._event(db, identifier, "REVOKED")

    def execute(self, identifier: str, principal: str, action: str, arguments: dict,
                handler: Callable[[], dict], verify: Callable[[list[dict]], bool]) -> dict:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM decisions WHERE id=? AND principal=?",
                             (identifier, principal)).fetchone()
            if row is None:
                raise AuthorizationError("approval required")
            if row["action"] != action or row["args_hash"] != digest(arguments) or row["policy"] != POLICY:
                raise AuthorizationError("approval does not bind this exact action, input and policy")
            if row["state"] == "SUCCEEDED":
                return {"decision_id": identifier, "state": "SUCCEEDED",
                        "replayed": True, "result": json.loads(row["result"])}
            if row["state"] != "APPROVED":
                raise AuthorizationError(f"effect cannot run in state {row['state']}; reconcile, do not retry")
            if row["expires"] <= time.time():
                raise AuthorizationError("approval expired")
            if not verify(json.loads(row["sources"])):
                raise AuthorizationError("source evidence changed or disappeared")
            active = db.execute("SELECT decision_id FROM active_effect WHERE slot=1").fetchone()
            if active:
                raise AuthorizationError("another effect is running or unresolved; reconcile it first")
            db.execute("INSERT INTO active_effect VALUES(1,?)", (identifier,))
            db.execute("UPDATE decisions SET state='RUNNING' WHERE id=?", (identifier,))
            self._event(db, identifier, "RUNNING")
        try:
            output = handler()
            serialized = canonical(output)
        except Exception as exc:
            # A handler may have already caused an effect before raising.
            with self.connect() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute("UPDATE decisions SET state='AMBIGUOUS',error=? WHERE id=?",
                           (type(exc).__name__, identifier))
                self._event(db, identifier, "AMBIGUOUS")
            raise
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE decisions SET state='SUCCEEDED',result=? WHERE id=?",
                       (serialized, identifier))
            db.execute("DELETE FROM active_effect WHERE decision_id=?", (identifier,))
            self._event(db, identifier, "SUCCEEDED")
        return {"decision_id": identifier, "state": "SUCCEEDED", "replayed": False, "result": output}

    def reconcile(self, identifier: str, principal: str, *, resolution: str) -> None:
        if resolution not in {"CONFIRMED_EFFECT", "CONFIRMED_NO_EFFECT"}:
            raise AuthorizationError("explicit observed resolution required")
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            changed = db.execute(
                "UPDATE decisions SET state=? WHERE id=? AND principal=? AND state IN ('RUNNING','AMBIGUOUS')",
                (resolution, identifier, principal)).rowcount
            if not changed:
                raise AuthorizationError("no ambiguous or interrupted effect to reconcile")
            db.execute("DELETE FROM active_effect WHERE decision_id=?", (identifier,))
            self._event(db, identifier, resolution)

    def verify_audit(self) -> bool:
        previous = ""
        with self.connect() as db:
            for row in db.execute("SELECT * FROM events ORDER BY seq"):
                if row["previous"] != previous or row["hash"] != digest(
                    [row["at"], row["decision_id"], row["state"], previous]
                ):
                    return False
                previous = row["hash"]
        return True
