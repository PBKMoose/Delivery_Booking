from fastapi.testclient import TestClient

from app.main import app


def test_health_reports_ok_and_database():
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "sqlite"
