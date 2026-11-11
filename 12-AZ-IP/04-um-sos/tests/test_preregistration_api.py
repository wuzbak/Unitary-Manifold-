# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import create_app


def _payload() -> dict:
    return {
        "title": "Field test of preregistered signal response",
        "authors": ["Researcher A"],
        "hypothesis": "The specified signal will exceed the registered threshold.",
        "methods": "Collect three independent measurements using the documented protocol.",
        "primary_outcomes": ["Peak amplitude in calibrated units"],
        "falsification_criteria": "The hypothesis is falsified if all valid measurements remain below threshold.",
        "planned_start_date": "2027-01-15",
        "related_prediction_id": "P-TEST-1",
    }


def test_local_explorer_and_its_assets_are_served_with_api(tmp_path):
    with TestClient(create_app(tmp_path / "preregistrations.sqlite3")) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert str(page.url).endswith("/frontend/")
        assert "UM-SOS Prediction Explorer" in page.text
        for path in ("/frontend/main.js", "/frontend/styles.css", "/graph/index.html",
                     "/registry/predictions.json", "/api/v1/predictions/all"):
            assert client.get(path).status_code == 200


def test_submission_is_durable_and_digest_verifiable(tmp_path):
    database = tmp_path / "preregistrations.sqlite3"
    with TestClient(create_app(database)) as client:
        created = client.post("/api/v1/preregistered/local", json=_payload())

    assert created.status_code == 201
    result = created.json()
    assert result["payload"] == _payload()
    assert result["identity_status"] == "self-declared"
    assert result["integrity"] == "verified"
    assert len(result["content_sha256"]) == 64

    with TestClient(create_app(database)) as restarted:
        listing = restarted.get("/api/v1/preregistered/local").json()

    assert listing["count"] == 1
    assert listing["records"][0]["id"] == result["id"]
    assert listing["records"][0]["content_sha256"] == result["content_sha256"]
    assert listing["records"][0]["integrity"] == "verified"


def test_invalid_or_unbounded_payload_is_rejected_without_writing(tmp_path):
    database = tmp_path / "preregistrations.sqlite3"
    app = create_app(database)
    with TestClient(app) as client:
        blank_author = _payload()
        blank_author["authors"] = ["  "]
        assert client.post("/api/v1/preregistered/local", json=blank_author).status_code == 422

        too_many_outcomes = _payload()
        too_many_outcomes["primary_outcomes"] = [f"Outcome {i}" for i in range(11)]
        assert client.post("/api/v1/preregistered/local", json=too_many_outcomes).status_code == 422

        extra_field = {**_payload(), "verified_author": True}
        assert client.post("/api/v1/preregistered/local", json=extra_field).status_code == 422

        assert client.get("/api/v1/preregistered/local").json() == {"count": 0, "records": []}


def test_digest_mismatch_is_reported_instead_of_hidden(tmp_path):
    database = tmp_path / "preregistrations.sqlite3"
    with TestClient(create_app(database)) as client:
        created = client.post("/api/v1/preregistered/local", json=_payload()).json()

    conn = sqlite3.connect(database)
    try:
        payload = json.dumps({"altered": "content"}, separators=(",", ":"), sort_keys=True)
        conn.execute(
            "UPDATE preregistrations SET payload_json=? WHERE id=?",
            (payload, created["id"]),
        )
        conn.commit()
    finally:
        conn.close()

    with TestClient(create_app(database)) as client:
        record = client.get("/api/v1/preregistered/local").json()["records"][0]
    assert record["integrity"] == "mismatch"


def test_listing_limit_is_bounded(tmp_path):
    with TestClient(create_app(tmp_path / "preregistrations.sqlite3")) as client:
        assert client.get("/api/v1/preregistered/local?limit=201").status_code == 422
        assert client.get("/api/v1/preregistered/local?limit=0").status_code == 422
