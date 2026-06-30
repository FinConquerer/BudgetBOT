import pytest

from app.core.rules.engine import create_budget_plan
from app.core.rules.exceptions import RuleValidationError
from app.core.rules.models import BudgetProfile


def test_create_budget_plan_feasible_goal():
    plan = create_budget_plan(
        BudgetProfile(
            monthly_income=20_000_000,
            fixed_expenses=7_000_000,
            variable_expenses=5_000_000,
            debt_payment=1_000_000,
            debt_outstanding=20_000_000,
            current_savings=30_000_000,
            financial_goal="mua laptop",
            goal_amount=25_000_000,
            goal_deadline_months=10,
            income_stability="stable",
        )
    )

    assert plan.type == "budget_plan"
    assert plan.summary.monthly_surplus == 7_000_000
    assert plan.goal_assessment.status == "feasible"


def test_create_budget_plan_negative_cashflow_warning():
    plan = create_budget_plan(
        BudgetProfile(
            monthly_income=15_000_000,
            fixed_expenses=9_000_000,
            variable_expenses=6_000_000,
            debt_payment=2_000_000,
            financial_goal="lập quỹ khẩn cấp",
            goal_amount=30_000_000,
            goal_deadline_months=8,
        )
    )

    assert plan.summary.monthly_surplus < 0
    assert plan.goal_assessment.status == "not_feasible"
    assert plan.warnings


def test_create_budget_plan_invalid_income():
    with pytest.raises(RuleValidationError):
        create_budget_plan(BudgetProfile(monthly_income=0))
