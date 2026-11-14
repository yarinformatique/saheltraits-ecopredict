import pytest
from fastapi import status


def test_register_user_success(client):
    payload = {
        "username": "new_researcher",
        "email": "new.researcher@ujkz.bf",
        "password": "SecurePassword123!",
        "role": "Chercheur",
        "full_name": "Nouveau Chercheur",
        "institution": "UJKZ-ICC",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "new_researcher"
    assert data["role"] == "Chercheur"
    assert "user_id" in data


def test_register_duplicate_username(client, seed_users):
    payload = {
        "username": "admin_user",
        "email": "diff@test.bf",
        "password": "Password123!",
        "role": "Admin",
        "full_name": "Duplicate User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "existe déjà" in response.json()["detail"]


def test_login_success(client, seed_users):
    payload = {
        "username": "admin_user",
        "password": "AdminPass123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "Admin"


def test_login_invalid_password(client, seed_users):
    payload = {
        "username": "admin_user",
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_me(client, admin_headers):
    response = client.get("/api/v1/auth/me", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "admin_user"
    assert data["role"] == "Admin"


def test_unauthenticated_me_access(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
