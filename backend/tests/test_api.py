"""Smoke test cho rulebase API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_plan_endpoint(client):
    r = client.post(
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


def test_plan_endpoint_extended_contract(client):
    r = client.post(
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


def test_what_if_endpoint(client):
    r = client.post(
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


def test_mock_profiles_endpoint(client):
    r = client.get("/api/mock-profiles")
    assert r.status_code == 200
    assert len(r.json()) > 0
