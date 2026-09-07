"""Endpoint tests for production-suite screenplay upgrade routes."""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    from desktop.app.config import FilmConfig
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.router import router

    db_path = tmp_path / "api_suite.db"
    init_db(db_path)
    cfg = FilmConfig(db_path=db_path)
    monkeypatch.setattr("desktop.app.config.get_config", lambda: cfg)

    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app)


def test_import_fountain_endpoint(api_client):
    response = api_client.post(
        "/api/production-suite/script/import-fountain",
        json={
            "project_id": "api-fountain-001",
            "title": "API Fountain",
            "content": "INT. LAB - DAY\nNOVA\nReady.",
            "replace_existing": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["import_format"] == "fountain"
    assert payload["scene_count"] == 1


def test_import_fdx_endpoint_success(api_client):
    response = api_client.post(
        "/api/production-suite/script/import-fdx",
        json={
            "project_id": "api-fdx-001",
            "title": "API FDX",
            "content": (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<FinalDraft DocumentType="Script"><Content>'
                '<Paragraph Type="Scene Heading"><Text>INT. HQ - DAY</Text></Paragraph>'
                '<Paragraph Type="Character"><Text>NOVA</Text></Paragraph>'
                '<Paragraph Type="Dialogue"><Text>Proceed.</Text></Paragraph>'
                "</Content></FinalDraft>"
            ),
            "replace_existing": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["import_format"] == "fdx"
    assert payload["scene_count"] == 1


def test_import_fdx_endpoint_invalid_xml_returns_422(api_client):
    response = api_client.post(
        "/api/production-suite/script/import-fdx",
        json={
            "project_id": "api-fdx-002",
            "title": "Invalid",
            "content": "<FinalDraft><Content><Paragraph>",
            "replace_existing": True,
        },
    )
    assert response.status_code == 422
    assert "Invalid FDX payload" in response.json()["detail"]
