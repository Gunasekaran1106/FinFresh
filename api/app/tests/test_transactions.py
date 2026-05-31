import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

INCOME_PAYLOAD = {
    "type": "income",
    "category": "Salary",
    "amount": 5000.00,
    "description": "Monthly salary",
    "date": "2025-06-01T00:00:00Z",
}

EXPENSE_PAYLOAD = {
    "type": "expense",
    "category": "Rent",
    "amount": 1500.00,
    "description": "Monthly rent",
    "date": "2025-06-02T00:00:00Z",
}


class TestCreateTransaction:
    async def test_create_income_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["type"] == "income"
        assert body["amount"] == 5000.00
        assert body["category"] == "Salary"
        assert "id" in body
        assert "user_id" in body

    async def test_create_expense_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.post(
            "/api/v1/transactions/", json=EXPENSE_PAYLOAD, headers=auth_headers
        )
        assert resp.status_code == 201
        assert resp.json()["type"] == "expense"

    async def test_create_transaction_no_token_returns_401(
        self, client: AsyncClient
    ):
        resp = await client.post("/api/v1/transactions/", json=INCOME_PAYLOAD)
        assert resp.status_code == 401

    async def test_create_transaction_negative_amount_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = {**INCOME_PAYLOAD, "amount": -100}
        resp = await client.post(
            "/api/v1/transactions/", json=payload, headers=auth_headers
        )
        assert resp.status_code == 422

    async def test_create_transaction_zero_amount_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = {**INCOME_PAYLOAD, "amount": 0}
        resp = await client.post(
            "/api/v1/transactions/", json=payload, headers=auth_headers
        )
        assert resp.status_code == 422

    async def test_create_transaction_invalid_type_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = {**INCOME_PAYLOAD, "type": "savings"}
        resp = await client.post(
            "/api/v1/transactions/", json=payload, headers=auth_headers
        )
        assert resp.status_code == 422


class TestListTransactions:
    async def test_list_returns_all(
        self, client: AsyncClient, auth_headers: dict
    ):
        await client.post("/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers)
        await client.post("/api/v1/transactions/", json=EXPENSE_PAYLOAD, headers=auth_headers)

        resp = await client.get("/api/v1/transactions/", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        assert len(body["transactions"]) == 2

    async def test_filter_by_income(
        self, client: AsyncClient, auth_headers: dict
    ):
        await client.post("/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers)
        await client.post("/api/v1/transactions/", json=EXPENSE_PAYLOAD, headers=auth_headers)

        resp = await client.get(
            "/api/v1/transactions/?type=income", headers=auth_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["transactions"][0]["type"] == "income"

    async def test_filter_by_expense(
        self, client: AsyncClient, auth_headers: dict
    ):
        await client.post("/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers)
        await client.post("/api/v1/transactions/", json=EXPENSE_PAYLOAD, headers=auth_headers)

        resp = await client.get(
            "/api/v1/transactions/?type=expense", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    async def test_pagination(
        self, client: AsyncClient, auth_headers: dict
    ):
        for i in range(5):
            await client.post(
                "/api/v1/transactions/",
                json={**INCOME_PAYLOAD, "description": f"Payment {i}"},
                headers=auth_headers,
            )

        resp = await client.get(
            "/api/v1/transactions/?skip=0&limit=2", headers=auth_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert len(body["transactions"]) == 2

    async def test_empty_list_for_new_user(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.get("/api/v1/transactions/", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    async def test_data_isolation_between_users(
        self, client: AsyncClient, auth_headers: dict
    ):
        # Create transaction as user 1
        await client.post(
            "/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers
        )

        # Register and login as user 2
        await client.post("/api/v1/auth/register", json={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "Str0ng!Pass2",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "bob@example.com",
            "password": "Str0ng!Pass2",
        })
        bob_token = login_resp.json()["token"]["access_token"]
        bob_headers = {"Authorization": f"Bearer {bob_token}"}

        # Bob must see zero transactions
        resp = await client.get("/api/v1/transactions/", headers=bob_headers)
        assert resp.json()["total"] == 0


class TestDeleteTransaction:
    async def test_delete_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        create_resp = await client.post(
            "/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers
        )
        txn_id = create_resp.json()["id"]

        del_resp = await client.delete(
            f"/api/v1/transactions/{txn_id}", headers=auth_headers
        )
        assert del_resp.status_code == 200
        assert del_resp.json()["transaction_id"] == txn_id

        list_resp = await client.get("/api/v1/transactions/", headers=auth_headers)
        assert list_resp.json()["total"] == 0

    async def test_delete_nonexistent_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.delete(
            "/api/v1/transactions/000000000000000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_delete_invalid_id_returns_400(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.delete(
            "/api/v1/transactions/not-a-valid-id",
            headers=auth_headers,
        )
        assert resp.status_code == 400

    async def test_cannot_delete_another_users_transaction(
        self, client: AsyncClient, auth_headers: dict
    ):
        # Create transaction as user 1
        create_resp = await client.post(
            "/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers
        )
        txn_id = create_resp.json()["id"]

        # Register user 2
        reg_resp = await client.post("/api/v1/auth/register", json={
            "name": "Eve",
            "email": "eve@example.com",
            "password": "Str0ng!Pass3",
        })
        eve_token = reg_resp.json()["token"]["access_token"]
        eve_headers = {"Authorization": f"Bearer {eve_token}"}

        # Eve tries to delete user 1's transaction
        resp = await client.delete(
            f"/api/v1/transactions/{txn_id}", headers=eve_headers
        )
        assert resp.status_code == 404   # ownership enforced — not 403