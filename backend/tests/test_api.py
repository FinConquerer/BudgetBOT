"""Smoke test cho API (dùng SQLite fallback; context manager để lifespan seed chạy)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:  # kích hoạt lifespan -> tạo bảng + seed FAQ
        yield c


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_faq_endpoint(client):
    r = client.post("/api/faq", json={"question": "Nên tiết kiệm bao nhiêu phần trăm?"})
    assert r.status_code == 200
    assert "20%" in r.json()["answer"]


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
