# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Tests for EIGE/src/adjudicator_api.py — Flask adjudicator queue API.
"""

from __future__ import annotations

import json
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from EIGE.src.adjudicator_api import create_app, AdjudicatorQueue


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def queue():
    return AdjudicatorQueue()


@pytest.fixture
def client(queue):
    app = create_app(queue=queue)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# AdjudicatorQueue unit tests
# ---------------------------------------------------------------------------

class TestAdjudicatorQueue:
    def test_initial_queue_empty(self, queue):
        assert queue.list_items() == []

    def test_enqueue_returns_id(self, queue):
        record_id = queue.enqueue({"record": "R1", "reason": "bad_fill", "field_name": "choice"})
        assert isinstance(record_id, str)
        assert len(record_id) > 0

    def test_enqueue_two_items(self, queue):
        id1 = queue.enqueue({"record": "R1", "reason": "bad_fill", "field_name": "choice"})
        id2 = queue.enqueue({"record": "R2", "reason": "ambiguous", "field_name": "candidate_a"})
        assert id1 != id2
        assert len(queue.list_items()) == 2

    def test_resolve_marks_item(self, queue):
        record_id = queue.enqueue({"record": "R3", "reason": "bad_fill", "field_name": "choice"})
        result = queue.resolve(record_id, selection_vector={"choice": 1})
        assert result is True

    def test_resolve_nonexistent_returns_false(self, queue):
        result = queue.resolve("nonexistent-id", selection_vector={})
        assert result is False

    def test_resolved_item_status(self, queue):
        record_id = queue.enqueue({"record": "R4", "reason": "bad_fill", "field_name": "choice"})
        queue.resolve(record_id, selection_vector={"choice": 0})
        items = queue.list_items()
        item = next(i for i in items if i["id"] == record_id)
        assert item["status"] == "resolved"

    def test_unresolved_item_status(self, queue):
        record_id = queue.enqueue({"record": "R5", "reason": "bad_fill", "field_name": "choice"})
        items = queue.list_items()
        item = next(i for i in items if i["id"] == record_id)
        assert item["status"] == "pending"

    def test_list_preserves_order(self, queue):
        ids = []
        for i in range(5):
            ids.append(queue.enqueue({"record": f"R{i}", "reason": "x", "field_name": "f"}))
        listed_ids = [i["id"] for i in queue.list_items()]
        assert listed_ids == ids


# ---------------------------------------------------------------------------
# POST /adjudicate
# ---------------------------------------------------------------------------

class TestAdjudicateEndpoint:
    def test_post_adjudicate_returns_201(self, client):
        resp = client.post(
            "/adjudicate",
            data=json.dumps({"record": "R1", "reason": "bad_fill", "field_name": "choice"}),
            content_type="application/json",
        )
        assert resp.status_code == 201

    def test_post_adjudicate_returns_record_id(self, client):
        resp = client.post(
            "/adjudicate",
            data=json.dumps({"record": "R2", "reason": "ambiguous", "field_name": "c"}),
            content_type="application/json",
        )
        body = resp.get_json()
        assert "record_id" in body
        assert isinstance(body["record_id"], str)

    def test_post_adjudicate_missing_body_returns_400(self, client):
        resp = client.post("/adjudicate", data="", content_type="application/json")
        assert resp.status_code in (400, 422)

    def test_post_adjudicate_empty_json_returns_400(self, client):
        resp = client.post(
            "/adjudicate",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_post_adjudicate_adds_to_queue(self, client, queue):
        client.post(
            "/adjudicate",
            data=json.dumps({"record": "R3", "reason": "bad_fill", "field_name": "choice"}),
            content_type="application/json",
        )
        assert len(queue.list_items()) == 1


# ---------------------------------------------------------------------------
# GET /queue
# ---------------------------------------------------------------------------

class TestQueueEndpoint:
    def test_get_queue_empty(self, client):
        resp = client.get("/queue")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["items"] == []

    def test_get_queue_after_enqueue(self, client):
        client.post(
            "/adjudicate",
            data=json.dumps({"record": "R1", "reason": "bad_fill", "field_name": "choice"}),
            content_type="application/json",
        )
        resp = client.get("/queue")
        body = resp.get_json()
        assert len(body["items"]) == 1

    def test_get_queue_count_field(self, client):
        for i in range(3):
            client.post(
                "/adjudicate",
                data=json.dumps({"record": f"R{i}", "reason": "x", "field_name": "f"}),
                content_type="application/json",
            )
        resp = client.get("/queue")
        body = resp.get_json()
        assert body["count"] == 3

    def test_get_queue_items_have_required_fields(self, client):
        client.post(
            "/adjudicate",
            data=json.dumps({"record": "R1", "reason": "bad_fill", "field_name": "choice"}),
            content_type="application/json",
        )
        resp = client.get("/queue")
        item = resp.get_json()["items"][0]
        for field in ("id", "status", "payload"):
            assert field in item


# ---------------------------------------------------------------------------
# POST /resolve/<record_id>
# ---------------------------------------------------------------------------

class TestResolveEndpoint:
    def test_resolve_valid_record(self, client):
        enqueue_resp = client.post(
            "/adjudicate",
            data=json.dumps({"record": "R1", "reason": "bad_fill", "field_name": "choice"}),
            content_type="application/json",
        )
        record_id = enqueue_resp.get_json()["record_id"]
        resp = client.post(
            f"/resolve/{record_id}",
            data=json.dumps({"selection_vector": {"choice": 1}}),
            content_type="application/json",
        )
        assert resp.status_code == 200

    def test_resolve_nonexistent_returns_404(self, client):
        resp = client.post(
            "/resolve/nonexistent-uuid",
            data=json.dumps({"selection_vector": {}}),
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_resolve_returns_status_resolved(self, client):
        enqueue_resp = client.post(
            "/adjudicate",
            data=json.dumps({"record": "R2", "reason": "ambiguous", "field_name": "c"}),
            content_type="application/json",
        )
        record_id = enqueue_resp.get_json()["record_id"]
        resp = client.post(
            f"/resolve/{record_id}",
            data=json.dumps({"selection_vector": {"c": 0}}),
            content_type="application/json",
        )
        body = resp.get_json()
        assert body.get("status") == "resolved"


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_ok(self, client):
        body = resp = client.get("/health")
        body = resp.get_json()
        assert body.get("status") == "ok"
