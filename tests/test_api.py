from fastapi.testclient import TestClient

from remotefit.api import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "remote-job-fit",
    }
