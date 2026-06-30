from app.repositories.mock_profile_repository import MockProfileRepository
from app.schemas import PlanRequest, WhatIfChange, WhatIfRequest
from app.services.budget_service import BudgetService


def test_budget_service_create_plan():
    service = BudgetService(profile_repository=MockProfileRepository())
    response = service.create_plan(
        PlanRequest(
            monthly_income=20_000_000,
            fixed_expenses=7_000_000,
            variable_expenses=5_000_000,
            debt_payment=1_000_000,
            financial_goal="mua laptop",
            goal_amount=25_000_000,
            goal_deadline_months=10,
        )
    )

    assert response.type == "budget_plan"
    assert response.summary.monthly_surplus == 7_000_000


def test_budget_service_run_what_if():
    service = BudgetService(profile_repository=MockProfileRepository())
    response = service.run_what_if(
        WhatIfRequest(
            profile=PlanRequest(
                monthly_income=20_000_000,
                fixed_expenses=7_000_000,
                variable_expenses=5_000_000,
                debt_payment=1_000_000,
            ),
            change=WhatIfChange(field="variable_expenses", delta=-1_000_000),
        )
    )

    assert response.type == "what_if"
    assert response.comparison.monthly_surplus_delta == 1_000_000
