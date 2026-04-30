from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"] == "devops-app is running"

def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"app_requests_total" in r.content
