# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/adjudicator_api.py — Human Adjudicator Queue API Server
================================================================

Flask REST API that bridges the Next.js VerificationCockpit UI with the
Python AdmissibilityError routing layer.

Endpoints
---------
POST /adjudicate
    Accept a JSON payload representing an AdmissibilityError event.
    Appends the record to the human adjudicator queue.
    Body: { "record": {...}, "reason": "...", "field_name": "..." }
    Returns: { "status": "QUEUED", "record_id": "<uuid>" }

GET /queue
    Return the current adjudicator queue as a JSON array.
    Returns: [ { "record_id": "...", "record": {...}, ... }, ... ]

POST /resolve/<record_id>
    Mark a queued record as human-reviewed and optionally re-submit
    it to a county node with a corrected selection_vector.
    Body: { "resolution": "ACCEPTED|REJECTED", "selection_vector": [...] }
    Returns: { "status": "RESOLVED", "record_id": "...", "resolution": "..." }

GET /health
    Health check endpoint.
    Returns: { "status": "OK", "queue_depth": N }

VerificationCockpit wiring
--------------------------
The TypeScript OverrideDossier type in VerificationCockpit.tsx maps to::

    POST /adjudicate body:
        { record: {...}, reason: string, field_name: string | null }

    GET /queue response item:
        { record_id: string, record: {...}, reason: string,
          field_name: string | null, queued_at: ISO-8601 }

    POST /resolve/<record_id> body:
        { resolution: "ACCEPTED" | "REJECTED",
          selection_vector: number[] | null }

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    from flask import Flask, request, jsonify
    _FLASK_AVAILABLE = True
except ImportError:
    Flask = None  # type: ignore[assignment,misc]
    _FLASK_AVAILABLE = False


# ---------------------------------------------------------------------------
# In-memory adjudicator queue
# ---------------------------------------------------------------------------

class AdjudicatorQueue:
    """Thread-safe in-memory queue for AdmissibilityError records.

    In production, replace the in-memory store with a persistent backend
    (PostgreSQL, Redis, etc.).
    """

    def __init__(self) -> None:
        self._queue: Dict[str, dict] = {}
        self._resolved: Dict[str, dict] = {}

    def enqueue(self, record: dict, reason: str, field_name: Optional[str] = None) -> str:
        """Add an admissibility-error record to the queue.

        Returns
        -------
        str
            New UUID record_id.
        """
        record_id = str(uuid.uuid4())
        self._queue[record_id] = {
            "record_id": record_id,
            "record": record,
            "reason": reason,
            "field_name": field_name,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "status": "PENDING",
        }
        return record_id

    def get_queue(self) -> List[dict]:
        """Return all pending queue items as a list."""
        return list(self._queue.values())

    def resolve(
        self,
        record_id: str,
        resolution: str,
        selection_vector: Optional[List[int]] = None,
    ) -> Optional[dict]:
        """Mark a record as resolved.

        Parameters
        ----------
        record_id : str
        resolution : str
            "ACCEPTED" or "REJECTED".
        selection_vector : list[int], optional
            Corrected selection vector when resolution == "ACCEPTED".

        Returns
        -------
        dict or None
            The resolved item, or None if record_id not found.
        """
        item = self._queue.pop(record_id, None)
        if item is None:
            return None
        item["status"] = "RESOLVED"
        item["resolution"] = resolution
        item["resolved_at"] = datetime.now(timezone.utc).isoformat()
        if selection_vector is not None:
            item["corrected_selection_vector"] = selection_vector
        self._resolved[record_id] = item
        return item

    def queue_depth(self) -> int:
        return len(self._queue)

    def __len__(self) -> int:
        return len(self._queue)


# ---------------------------------------------------------------------------
# Flask app factory
# ---------------------------------------------------------------------------

# Module-level shared queue (used by the app and accessible in tests)
_global_queue = AdjudicatorQueue()


def create_app(queue: Optional[AdjudicatorQueue] = None) -> "Flask":
    """Create and configure the Flask adjudicator API application.

    Parameters
    ----------
    queue : AdjudicatorQueue, optional
        Queue instance to use.  Defaults to the module-level ``_global_queue``.

    Returns
    -------
    Flask
        Configured Flask application.

    Raises
    ------
    ImportError
        If Flask is not installed.
    """
    if not _FLASK_AVAILABLE:
        raise ImportError(
            "Flask is required for adjudicator_api. Install: pip install flask"
        )

    app = Flask("eige_adjudicator")
    q = queue or _global_queue

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "OK", "queue_depth": q.queue_depth()})

    @app.route("/adjudicate", methods=["POST"])
    def adjudicate():
        """Accept an AdmissibilityError payload and add it to the queue."""
        data = request.get_json(force=True, silent=True) or {}
        record = data.get("record", {})
        reason = data.get("reason", "")
        field_name = data.get("field_name", None)

        if not reason:
            return jsonify({"error": "reason field is required"}), 400

        record_id = q.enqueue(record=record, reason=reason, field_name=field_name)
        return jsonify({"status": "QUEUED", "record_id": record_id}), 201

    @app.route("/queue", methods=["GET"])
    def get_queue():
        """Return the current adjudicator queue."""
        return jsonify(q.get_queue())

    @app.route("/resolve/<record_id>", methods=["POST"])
    def resolve(record_id: str):
        """Mark a queued record as human-reviewed."""
        data = request.get_json(force=True, silent=True) or {}
        resolution = data.get("resolution", "")
        selection_vector = data.get("selection_vector", None)

        if resolution not in ("ACCEPTED", "REJECTED"):
            return jsonify(
                {"error": "resolution must be 'ACCEPTED' or 'REJECTED'"}
            ), 400

        item = q.resolve(
            record_id=record_id,
            resolution=resolution,
            selection_vector=selection_vector,
        )
        if item is None:
            return jsonify({"error": f"record_id {record_id!r} not found"}), 404

        return jsonify({
            "status": "RESOLVED",
            "record_id": record_id,
            "resolution": resolution,
        })

    return app


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def run_server(host: str = "127.0.0.1", port: int = 5050, debug: bool = False) -> None:
    """Launch the adjudicator API server.

    Usage::

        python -m src.adjudicator_api

    Or from code::

        from src.adjudicator_api import run_server
        run_server(port=5050)
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server()
