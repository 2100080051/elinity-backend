import pytest
import jwt
from fastapi.testclient import TestClient
from settings import SECRET_KEY, JWT_HASH_ALGORITHM


def test_register_login_refresh(client: TestClient):
    email = "user@example.com"
    password = "securepass"

    # Register new user
    res = client.post("/register", json={"email": email, "password": password})
    assert res.status_code == 200
    tokens = res.json()
    assert "access_token" in tokens and "refresh_token" in tokens

    # Login with credentials
    res2 = client.post("/login", json={"email": email, "password": password})
    assert res2.status_code == 200
    tokens2 = res2.json()
    assert tokens2["access_token"] != tokens["access_token"]

    # Refresh token
    res3 = client.post("/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert res3.status_code == 200
    tokens3 = res3.json()
    assert tokens3["access_token"] != tokens["access_token"]
