from fastapi.testclient import TestClient

from fast import app

def test_heath_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "docverse-api"
    assert body["embedding_device"] in {"cpu","cuda"}
    