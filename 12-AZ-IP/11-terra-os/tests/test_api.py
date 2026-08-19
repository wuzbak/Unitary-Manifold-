"""
TerraOS — API Tests (27)
"""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "test_terra.db"
    monkeypatch.setenv("TERRA_DB_PATH", str(db))
    import terra.app.config as cfg_module
    cfg_module._config = None
    from terra.app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c
    cfg_module._config = None


# ---- Health ----
def test_health_ok(client):
    r = client.get("/api/v1/")
    assert r.status_code == 200


def test_health_app_name(client):
    r = client.get("/api/v1/")
    assert r.json()["app"] == "terra-os"


def test_health_db_count(client):
    r = client.get("/api/v1/")
    assert r.json()["db_profile_count"] >= 0


def test_health_status_field(client):
    r = client.get("/api/v1/")
    assert r.json()["status"] == "ok"


def test_health_version_field(client):
    r = client.get("/api/v1/")
    assert "version" in r.json()


# ---- Ask ----
def test_ask_basic(client):
    r = client.post("/api/v1/ask", json={"question": "What is clay soil?"})
    assert r.status_code == 200


def test_ask_returns_agent(client):
    r = client.post("/api/v1/ask", json={"question": "What is clay soil?"})
    data = r.json()
    assert "agent" in data
    assert data["agent"] in ["SoilAnalyst", "WaterChemist", "AgronomistAdvisor", "EcologyGuide", "RemediationOfficer"]


def test_ask_returns_answer(client):
    r = client.post("/api/v1/ask", json={"question": "How does pH affect crops?"})
    assert len(r.json()["answer"]) > 0


def test_ask_water_question(client):
    r = client.post("/api/v1/ask", json={"question": "What is TDS in drinking water?"})
    assert r.json()["agent"] == "WaterChemist"


def test_ask_remediation_question(client):
    r = client.post("/api/v1/ask", json={"question": "How to remediate lead contamination?"})
    assert r.json()["agent"] == "RemediationOfficer"


def test_ask_top_k_param(client):
    r = client.post("/api/v1/ask", json={"question": "soil organic matter", "top_k": 2})
    assert r.status_code == 200


def test_ask_empty_question_rejected(client):
    r = client.post("/api/v1/ask", json={"question": ""})
    assert r.status_code == 422


# ---- Soil Analysis ----
def test_analyze_soil_basic(client):
    r = client.post("/api/v1/analyze/soil", json={"ph": 6.5, "organic_matter_pct": 3.0})
    assert r.status_code == 200


def test_analyze_soil_returns_score(client):
    r = client.post("/api/v1/analyze/soil", json={"ph": 6.5})
    data = r.json()
    assert "score" in data
    assert 0 <= data["score"] <= 100


def test_analyze_soil_acid_issues(client):
    r = client.post("/api/v1/analyze/soil", json={"ph": 4.5})
    data = r.json()
    assert len(data["issues"]) > 0


def test_analyze_soil_empty_ok(client):
    r = client.post("/api/v1/analyze/soil", json={})
    assert r.status_code == 200


# ---- Water Analysis ----
def test_analyze_water_basic(client):
    r = client.post("/api/v1/analyze/water", json={"ph": 7.2, "tds_ppm": 300})
    assert r.status_code == 200


def test_analyze_water_high_nitrate(client):
    r = client.post("/api/v1/analyze/water", json={"nitrate_ppm": 80})
    data = r.json()
    assert len(data["issues"]) > 0


def test_analyze_water_score(client):
    r = client.post("/api/v1/analyze/water", json={"ph": 7.0, "tds_ppm": 200})
    assert r.json()["score"] >= 70


# ---- Profile ----
def test_get_profile_exists(client):
    r = client.get("/api/v1/profile/1")
    assert r.status_code == 200


def test_get_profile_fields(client):
    r = client.get("/api/v1/profile/1")
    data = r.json()
    assert "name" in data and "type" in data


def test_get_profile_not_found(client):
    r = client.get("/api/v1/profile/99999")
    assert r.status_code == 404


# ---- Amendments ----
def test_list_amendments(client):
    r = client.get("/api/v1/amendments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_amendments_have_fields(client):
    r = client.get("/api/v1/amendments")
    for item in r.json():
        assert "name" in item and "type" in item


# ---- Search ----
def test_search_profiles(client):
    r = client.post("/api/v1/search", json={"query": "clay"})
    assert r.status_code == 200
    data = r.json()
    assert "results" in data and "total" in data


# ---- Sync ----
def test_sync_soil_profiles(client):
    r = client.post("/api/v1/sync", json={"table": "soil_profiles"})
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_sync_status(client):
    r = client.get("/api/v1/sync/status")
    assert r.status_code == 200
    assert "tables" in r.json()
