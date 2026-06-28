from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "nombre": "Test",
            "apellido": "User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["usuario"]["email"] == "test@example.com"


def test_login_success(client: TestClient):
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "securepass",
            "nombre": "Login",
            "apellido": "Test",
        },
    )
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "securepass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "noexiste@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_rate_limit_auth(client: TestClient):
    # Send 6 rapid login requests with wrong password
    for i in range(6):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": f"ratelimit{i}@example.com", "password": "wrong"},
        )
        if i < 5:
            assert response.status_code == 401, f"Request {i + 1} expected 401, got {response.status_code}"
        else:
            assert response.status_code == 429, f"Request {i + 1} expected 429, got {response.status_code}"
            assert "Retry-After" in response.headers
