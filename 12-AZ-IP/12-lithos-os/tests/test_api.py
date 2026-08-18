"""
LithosOS — API Tests (27 tests)
"""
from __future__ import annotations
import pytest

@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "test_lithos.db"
    monkeypatch.setenv("LITHOS_DB_PATH", str(db))
    import lithic.app.config as cfg_module
    cfg_module._config = None
    from fastapi.testclient import TestClient
    from lithic.app.main import create_app
    app = create_app()
    with TestClient(app) as c:
        yield c
    cfg_module._config = None

class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/api/v1/")
        assert resp.status_code == 200

    def test_health_has_status_field(self, client):
        resp = client.get("/api/v1/")
        assert resp.json()["status"] == "ok"

    def test_health_service_name(self, client):
        resp = client.get("/api/v1/")
        assert resp.json()["service"] == "lithos-os"

class TestAsk:
    def test_basic_ask(self, client):
        resp = client.post("/api/v1/ask", json={"question": "What is quartz?"})
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "agents_used" in data

    def test_ask_with_agent(self, client):
        resp = client.post("/api/v1/ask", json={"question": "Crystal systems?", "agent": "Geologist"})
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data

    def test_ask_invalid_agent_graceful(self, client):
        resp = client.post("/api/v1/ask", json={"question": "What is gold?", "agent": "NonexistentAgent"})
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data

    def test_ask_empty_question_fails(self, client):
        resp = client.post("/api/v1/ask", json={"question": ""})
        assert resp.status_code == 422

    def test_ask_with_context(self, client):
        resp = client.post("/api/v1/ask", json={"question": "Is it toxic?", "context": "Malachite specimen"})
        assert resp.status_code == 200
        assert "answer" in resp.json()

class TestSearch:
    def test_search_returns_results(self, client):
        resp = client.post("/api/v1/search", json={"query": "quartz"})
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "total" in data

    def test_search_empty_query_fails(self, client):
        resp = client.post("/api/v1/search", json={"query": ""})
        assert resp.status_code == 422

    def test_search_no_results(self, client):
        resp = client.post("/api/v1/search", json={"query": "xyznotamineral999abc"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_search_limit_param(self, client):
        resp = client.post("/api/v1/search", json={"query": "mineral", "limit": 5})
        assert resp.status_code == 200

    def test_search_json_structure(self, client):
        resp = client.post("/api/v1/search", json={"query": "gold"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["results"], list)
        assert isinstance(data["query"], str)

class TestSpecimen:
    def test_get_specimen_by_id(self, client):
        resp = client.get("/api/v1/specimen/1")
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "minerals" in data

    def test_get_specimen_404(self, client):
        resp = client.get("/api/v1/specimen/99999")
        assert resp.status_code == 404

    def test_list_minerals_endpoint(self, client):
        resp = client.get("/api/v1/minerals")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_market_endpoint(self, client):
        resp = client.get("/api/v1/market")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_identify_endpoint(self, client):
        resp = client.post("/api/v1/identify", json={"description": "shiny yellow mineral"})
        assert resp.status_code == 200
        data = resp.json()
        assert "candidates" in data
        assert "summary" in data

class TestSync:
    def test_sync_endpoint_returns_state(self, client):
        resp = client.post("/api/v1/sync", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "completed" in data

    def test_sync_status_endpoint(self, client):
        resp = client.get("/api/v1/sync/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "completed" in data

    def test_sync_offline_graceful(self, client):
        resp = client.post("/api/v1/sync", json={"since": "2024-01-01T00:00:00Z", "tables": ["specimens"]})
        assert resp.status_code == 200

class TestModels:
    def test_ask_request_valid(self):
        from lithic.app.api.models import AskRequest
        req = AskRequest(question="What is pyrite?")
        assert req.question == "What is pyrite?"

    def test_ask_request_empty_fails(self):
        from lithic.app.api.models import AskRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            AskRequest(question="")

    def test_ask_response_structure(self):
        from lithic.app.api.models import AskResponse
        resp = AskResponse(answer="Pyrite is FeS2.", agents_used=["Geologist"], question="What is pyrite?")
        assert resp.answer.startswith("Pyrite")
        assert "Geologist" in resp.agents_used

    def test_search_request_defaults(self):
        from lithic.app.api.models import SearchRequest
        req = SearchRequest(query="gold")
        assert req.limit == 20

    def test_health_response(self):
        from lithic.app.api.models import HealthResponse
        resp = HealthResponse(status="ok", service="lithos-os", version="1.0.0", offline_mode=False, db_specimen_count=22)
        assert resp.db_specimen_count == 22

    def test_sync_request_defaults(self):
        from lithic.app.api.models import SyncRequest
        req = SyncRequest()
        assert req.since.startswith("2000")
        assert req.tables == []
