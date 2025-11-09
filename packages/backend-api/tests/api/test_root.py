from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "service": "UP2D8 Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
