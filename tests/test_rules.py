import pytest

from budgetbot.rules.engine import (
    allocation_50_30_20,
    emergency_fund_target,
    evaluate_allocation,
    goal_timeline,
    savings_rate,
)
from budgetbot.rules.models import UserProfile


def test_savings_rate():
    assert savings_rate(1000, 200) == 0.2


def test_savings_rate_invalid():
    with pytest.raises(ValueError):
        savings_rate(0, 100)


def test_allocation_50_30_20():
    a = allocation_50_30_20(1000)
    assert a == {"needs": 500.0, "wants": 300.0, "savings": 200.0}
    assert round(sum(a.values()), 2) == 1000.0


def test_emergency_fund_target():
    assert emergency_fund_target(5_000_000, 6) == 30_000_000.0


def test_goal_timeline():
    assert goal_timeline(120_000_000, 10_000_000) == 12.0


def test_goal_timeline_invalid():
    with pytest.raises(ValueError):
        goal_timeline(100, 0)


def test_evaluate_allocation_flags():
    p = UserProfile(1000, essential_expenses=700, discretionary_expenses=200, monthly_savings=100)
    r = evaluate_allocation(p)
    assert r["needs"]["status"] == "vượt khuyến nghị"
    assert r["savings"]["status"] == "thấp hơn khuyến nghị"
