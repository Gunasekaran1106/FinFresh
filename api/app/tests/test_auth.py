import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Str0ng!Pass",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["user"]["email"] == "jane@example.com"
        assert body["user"]["name"] == "Jane Doe"
        assert "id" in body["user"]
        assert "password_hash" not in body["user"]
        assert body["token"]["token_type"] == "bearer"
        assert len(body["token"]["access_token"]) > 20

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient):
        payload = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Str0ng!Pass",
        }
        await client.post("/api/v1/auth/register", json=payload)
        resp = await client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"]

    async def test_register_email_case_insensitive(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "name": "Jane Doe",
            "email": "Jane@Example.COM",
            "password": "Str0ng!Pass",
        })
        resp = await client.post("/api/v1/auth/register", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Str0ng!Pass",
        })
        assert resp.status_code == 409

    async def test_register_short_password_returns_422(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "abc",
        })
        assert resp.status_code == 422

    async def test_register_weak_password_no_uppercase_returns_422(
        self, client: AsyncClient
    ):
        resp = await client.post("/api/v1/auth/register", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "weakpassword1",
        })
        assert resp.status_code == 422

    async def test_register_missing_fields_returns_422(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={"name": "Jane"})
        assert resp.status_code == 422

    async def test_register_invalid_email_returns_422(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "name": "Jane Doe",
            "email": "not-an-email",
            "password": "Str0ng!Pass",
        })
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient, registered_user: dict):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "Str0ng!Pass",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["token"]["token_type"] == "bearer"
        assert len(body["token"]["access_token"]) > 20

    async def test_login_wrong_password_returns_401(
        self, client: AsyncClient, registered_user: dict
    ):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword1",
        })
        assert resp.status_code == 401

    async def test_login_unknown_email_returns_401(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "Str0ng!Pass",
        })
        assert resp.status_code == 401
        # Must be same message as wrong password — prevents user enumeration
        wrong_pass_resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword1",
        })
        assert resp.json()["detail"] == wrong_pass_resp.json()["detail"]

    async def test_login_case_insensitive_email(
        self, client: AsyncClient, registered_user: dict
    ):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "TEST@EXAMPLE.COM",
            "password": "Str0ng!Pass",
        })
        assert resp.status_code == 200


class TestGetMe:
    async def test_get_me_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "test@example.com"
        assert "password_hash" not in body

    async def test_get_me_no_token_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    async def test_get_me_invalid_token_returns_401(self, client: AsyncClient):
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401