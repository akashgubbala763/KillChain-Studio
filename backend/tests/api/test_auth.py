import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.core.security import verify_password
from backend.app.main import app

pytestmark = pytest.mark.asyncio


async def test_register_user(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@soc.local",
            "password": "StrongPassword123!",
            "full_name": "New User",
            "role": "ANALYST"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@soc.local"
    assert data["full_name"] == "New User"
    assert data["role"] == "ANALYST"
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_user(client: AsyncClient, db_session: AsyncSession):
    # Register first time
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dupuser@soc.local",
            "password": "StrongPassword123!",
            "full_name": "New User",
            "role": "ANALYST"
        },
    )
    # Register second time
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dupuser@soc.local",
            "password": "StrongPassword123!",
            "full_name": "New User",
            "role": "ANALYST"
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    # First register
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@soc.local",
            "password": "StrongPassword123!",
            "full_name": "Login User",
            "role": "ANALYST"
        },
    )
    
    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@soc.local",
            "password": "StrongPassword123!"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "loginuser@soc.local"


async def test_login_failure(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wronguser@soc.local",
            "password": "wrongpassword"
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


async def test_get_me(client: AsyncClient, db_session: AsyncSession):
    # Register & Login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "meuser@soc.local",
            "password": "StrongPassword123!",
            "full_name": "Me User",
            "role": "VIEWER"
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "meuser@soc.local",
            "password": "StrongPassword123!"
        },
    )
    token = login_response.json()["access_token"]
    
    # Get Me
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "meuser@soc.local"
    assert data["role"] == "VIEWER"
