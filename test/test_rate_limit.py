from fastapi.testclient import TestClient


def test_auth_endpoint_rate_limited(client: TestClient):
    """Verify auth endpoints are rate limited after exceeding the burst."""
    # Exhaust auth bucket (burst = 5)
    for i in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": f"burst{i}@example.com", "password": "wrong"},
        )
        assert response.status_code == 401

    # 6th request should be rate limited
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "burst5@example.com", "password": "wrong"},
    )
    assert response.status_code == 429
    assert response.headers.get("X-RateLimit-Remaining") == "0"


def test_public_endpoint_not_rate_limited(client: TestClient):
    """Verify that /docs and /openapi.json are excluded from rate limiting."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200

    response = client.get("/")
    # / returns 404 with the current app (no root endpoint), but should not be 429
    assert response.status_code != 429
