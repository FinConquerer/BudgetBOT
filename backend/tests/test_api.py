"""Smoke test cho rulebase API."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c


pytestmark = pytest.mark.anyio


async def test_health(client):
    r = await client.get("/health")
    assert r.json() == {"status": "ok"}


async def test_version_endpoint(client):
    r = await client.get("/api/version")
    assert r.status_code == 200
    assert r.json()["name"] == "BudgetBOT Rulebase API"


async def test_plan_endpoint(client):
    r = await client.post(
        "/api/plan",
        json={
            "monthly_income": 20_000_000,
            "essential_expenses": 12_000_000,
            "discretionary_expenses": 4_000_000,
            "monthly_savings": 4_000_000,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["allocation_50_30_20"]["savings"] == 4_000_000
    assert body["savings_rate"] == 0.2


async def test_plan_endpoint_extended_contract(client):
    r = await client.post(
        "/api/plan",
        json={
            "monthly_income": 20_000_000,
            "fixed_expenses": 7_000_000,
            "variable_expenses": 5_000_000,
            "debt_payment": 1_000_000,
            "debt_outstanding": 20_000_000,
            "current_savings": 30_000_000,
            "financial_goal": "mua laptop",
            "goal_amount": 25_000_000,
            "goal_deadline_months": 10,
            "income_stability": "stable",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["type"] == "budget_plan"
    assert body["summary"]["monthly_surplus"] == 7_000_000
    assert body["goal_assessment"]["status"] == "feasible"


async def test_what_if_endpoint(client):
    r = await client.post(
        "/api/what-if",
        json={
            "profile": {
                "monthly_income": 20_000_000,
                "fixed_expenses": 7_000_000,
                "variable_expenses": 5_000_000,
                "debt_payment": 1_000_000,
            },
            "change": {"field": "variable_expenses", "delta": -1_000_000},
        },
    )
    assert r.status_code == 200
    assert r.json()["comparison"]["monthly_surplus_delta"] == 1_000_000


async def test_mock_profiles_endpoint(client):
    r = await client.get("/api/mock-profiles")
    assert r.status_code == 200
    assert len(r.json()) > 0


async def test_faq_ask_endpoint(client):
    r = await client.post("/api/faq", json={"question": "Xin chào"})
    assert r.status_code == 200
    assert r.json()["answer"]


async def test_faq_list_endpoint(client):
    r = await client.get("/api/faqs", params={"q": "chào"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] > 0
    assert body["items"][0]["id"]


async def test_faq_detail_endpoint(client):
    r = await client.get("/api/faqs/GREET_001")
    assert r.status_code == 200
    assert r.json()["question"] == "Xin chào"
