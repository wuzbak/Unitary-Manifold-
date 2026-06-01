from fastapi.testclient import TestClient

from src.core.um_sos_api import create_app


client = TestClient(create_app())


def test_predictions_endpoint():
    r = client.get('/api/v1/predictions/all')
    assert r.status_code == 200
    payload = r.json()
    assert payload['count'] > 0


def test_gaps_endpoint():
    r = client.get('/api/v1/gaps')
    assert r.status_code == 200
    assert r.json()['count'] > 0


def test_governance_endpoint():
    r = client.post('/api/v1/governance/classify', json={'text': 'publish falsification override immediately'})
    assert r.status_code == 200
    assert r.json()['lane'] == 'CRITICAL'


def test_preregistered_endpoint():
    r = client.get('/api/v1/preregistered')
    assert r.status_code == 200
    assert r.json()['entry_count'] >= 8


def test_ai_query_endpoint():
    r = client.post('/api/v1/ai/query', json={'question': 'Should we publish a falsification override now?'})
    assert r.status_code == 200
    out = r.json()
    assert out['governance_lane'] in {'CRITICAL','SENSITIVE','ROUTINE'}
    assert "epistemic_label" in out
