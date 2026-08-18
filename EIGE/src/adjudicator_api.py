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
        self._items: Dict[str, dict] = {}
        self._order: List[str] = []

    def enqueue(self, payload: dict) -> str:
        """Add an admissibility-error payload to the queue.

        Parameters
        ----------
        payload : dict
            Dict with at least ``reason`` key; may include ``record``
            and ``field_name`` entries.

        Returns
        -------
        str
            New UUID record id.
        """
        record_id = str(uuid.uuid4())
        self._items[record_id] = {
            "id": record_id,
            "payload": payload,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        self._order.append(record_id)
        return record_id

    def list_items(self) -> List[dict]:
        """Return all queue items in insertion order."""
        return [self._items[rid] for rid in self._order if rid in self._items]

    def get_queue(self) -> List[dict]:
        """Alias for list_items() — kept for Flask endpoint compatibility."""
        return self.list_items()

    def resolve(
        self,
        record_id: str,
        selection_vector=None,
        resolution: str = "ACCEPTED",
    ) -> bool:
        """Mark a record as resolved.

        Parameters
        ----------
        record_id : str
        selection_vector : any, optional
            Corrected selection vector supplied by the human adjudicator.
        resolution : str
            Resolution disposition ("ACCEPTED" or "REJECTED").

        Returns
        -------
        bool
            True if found and resolved; False if record_id not found.
        """
        item = self._items.get(record_id)
        if item is None:
            return False
        item["status"] = "resolved"
        item["resolution"] = resolution
        item["resolved_at"] = datetime.now(timezone.utc).isoformat()
        if selection_vector is not None:
            item["corrected_selection_vector"] = selection_vector
        return True

    def queue_depth(self) -> int:
        pending = sum(1 for v in self._items.values() if v["status"] == "pending")
        return pending

    def __len__(self) -> int:
        return len(self._items)


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
    q = queue if queue is not None else _global_queue

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "queue_depth": q.queue_depth()})

    @app.route("/adjudicate", methods=["POST"])
    def adjudicate():
        """Accept an AdmissibilityError payload and add it to the queue."""
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        if not data.get("reason") and not data.get("record") and not data.get("field_name"):
            return jsonify({"error": "payload must include at least one field"}), 400

        record_id = q.enqueue(payload=data)
        return jsonify({"status": "QUEUED", "record_id": record_id}), 201

    @app.route("/queue", methods=["GET"])
    def get_queue():
        """Return the current adjudicator queue."""
        items = q.list_items()
        return jsonify({"items": items, "count": len(items)})

    @app.route("/resolve/<record_id>", methods=["POST"])
    def resolve(record_id: str):
        """Mark a queued record as human-reviewed."""
        data = request.get_json(force=True, silent=True) or {}
        selection_vector = data.get("selection_vector", None)
        resolution = data.get("resolution", "ACCEPTED")

        success = q.resolve(
            record_id=record_id,
            selection_vector=selection_vector,
            resolution=resolution,
        )
        if not success:
            return jsonify({"error": f"record_id {record_id!r} not found"}), 404

        return jsonify({
            "status": "resolved",
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
