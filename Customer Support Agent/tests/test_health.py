from app.main import app
from fastapi.testclient import TestClient


def test_liveness_is_available_without_dependencies() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]

