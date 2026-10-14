from fastapi.testclient import TestClient

from backend.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "mcp-webpilot"
        assert "mcp_endpoint" in body
        assert body["mcp_endpoint"] == "/mcp"
