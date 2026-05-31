import pytest
from httpx import AsyncClient
from app.services.finance_service import calculate_financial_health_score

pytestmark = pytest.mark.asyncio

INCOME_PAYLOAD = {
    "type": "income", "category": "Salary",
    "amount": 5000.00, "description": "Salary",
    "date": "2025-06-01T00:00:00Z",
}
EXPENSE_PAYLOAD = {
    "type": "expense", "category": "Rent",
    "amount": 1800.00, "description": "Rent",
    "date": "2025-06-02T00:00:00Z",
}


class TestHealthScore:
    """Pure unit tests — no DB required."""

    def test_no_income_returns_zero(self):
        assert calculate_financial_health_score(0, 500) == 0

    def test_negative_income_returns_zero(self):
        assert calculate_financial_health_score(-100, 0) == 0

    def test_perfect_savings_returns_100(self):
        assert calculate_financial_health_score(5000, 0) == 100

    def test_break_even_returns_50(self):
        assert calculate_financial_health_score(5000, 5000) == 50

    def test_heavy_overspending_returns_zero(self):
        assert calculate_financial_health_score(1000, 9000) == 0

    def test_typical_scenario(self):
        # income=5000, expense=1800 → savings_rate=0.64, expense_ratio=0.36
        # score = 50 + 0.64*40 + max(0, (1-0.36)*10) = 50 + 25.6 + 6.4 = 82
        score = calculate_financial_health_score(5000, 1800)
        assert 80 <= score <= 85

    def test_result_always_in_range(self):
        for income, expense in [
            (0, 0), (1, 0), (0, 1), (10000, 1), (1, 10000), (5000, 2500),
        ]:
            score = calculate_financial_health_score(income, expense)
            assert 0 <= score <= 100


class TestDashboardAPI:
    async def test_empty_dashboard_for_new_user(
        self, client: AsyncClient, auth_headers: dict
    ):
        resp = await client.get(
            "/api/v1/dashboard/summary", headers=auth_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_income"] == 0.0
        assert body["total_expense"] == 0.0
        assert body["current_balance"] == 0.0
        assert body["financial_health_score"] == 0
        assert body["transaction_count"] == 0

    async def test_dashboard_with_transactions(
        self, client: AsyncClient, auth_headers: dict
    ):
        await client.post(
            "/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers
        )
        await client.post(
            "/api/v1/transactions/", json=EXPENSE_PAYLOAD, headers=auth_headers
        )

        resp = await client.get(
            "/api/v1/dashboard/summary", headers=auth_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_income"] == 5000.0
        assert body["total_expense"] == 1800.0
        assert body["current_balance"] == 3200.0
        assert body["income_transaction_count"] == 1
        assert body["expense_transaction_count"] == 1
        assert body["transaction_count"] == 2
        assert 0 <= body["financial_health_score"] <= 100

    async def test_dashboard_no_token_returns_401(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/summary")
        assert resp.status_code == 401

    async def test_dashboard_data_isolation(
        self, client: AsyncClient, auth_headers: dict
    ):
        # User 1 adds income
        await client.post(
            "/api/v1/transactions/", json=INCOME_PAYLOAD, headers=auth_headers
        )

        # User 2 registers and checks their dashboard
        reg_resp = await client.post("/api/v1/auth/register", json={
            "name": "Charlie",
            "email": "charlie@example.com",
            "password": "Str0ng!Pass4",
        })
        charlie_token = reg_resp.json()["token"]["access_token"]
        charlie_headers = {"Authorization": f"Bearer {charlie_token}"}

        resp = await client.get(
            "/api/v1/dashboard/summary", headers=charlie_headers
        )
        assert resp.json()["total_income"] == 0.0
        assert resp.json()["transaction_count"] == 0