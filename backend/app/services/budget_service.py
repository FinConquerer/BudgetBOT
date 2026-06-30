"""Service xử lý nghiệp vụ kế hoạch ngân sách và what-if."""

from dataclasses import asdict, replace

from app.core.rules.engine import create_budget_plan, evaluate_allocation
from app.core.rules.models import BudgetPlan, BudgetProfile, UserProfile
from app.repositories.profile_repository import ProfileRepository
from app.schemas import (
    BudgetAllocationResponse,
    FinancialMetricsResponse,
    FinancialSummaryResponse,
    GoalAssessmentResponse,
    MockProfileResponse,
    PlanRequest,
    PlanResponse,
    WhatIfRequest,
    WhatIfResponse,
    WhatIfComparisonResponse,
)


class BudgetService:
    """Điều phối nghiệp vụ API và gọi rulebase."""

    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository

    def create_plan(self, request: PlanRequest) -> PlanResponse:
        """Tạo kế hoạch ngân sách từ yêu cầu đã được kiểm tra hợp lệ."""
        profile = self._profile_from_request(request)
        plan = create_budget_plan(profile)
        return self._response_from_plan(plan, request)

    def run_what_if(self, request: WhatIfRequest) -> WhatIfResponse:
        """Chạy kịch bản what-if và trả so sánh trước/sau."""
        before = self.create_plan(request.profile)
        base_profile = self._profile_from_request(request.profile)
        current_value = getattr(base_profile, request.change.field)
        updated_profile = replace(
            base_profile,
            **{request.change.field: max(0.0, current_value + request.change.delta)},
        )
        after_request = PlanRequest(**asdict(updated_profile))
        after = self.create_plan(after_request)
        return WhatIfResponse(
            before=before,
            after=after,
            comparison=WhatIfComparisonResponse(
                monthly_surplus_delta=round(
                    after.summary.monthly_surplus - before.summary.monthly_surplus,
                    2,
                ),
                savings_rate_delta=round(
                    after.metrics.savings_rate - before.metrics.savings_rate, 3
                ),
            ),
        )

    def list_mock_profiles(self) -> list[MockProfileResponse]:
        """Trả danh sách hồ sơ mẫu qua lớp truy xuất dữ liệu."""
        return self.profile_repository.list_profiles()

    def _profile_from_request(self, request: PlanRequest) -> BudgetProfile:
        return BudgetProfile(
            monthly_income=request.monthly_income,
            fixed_expenses=request.fixed_expenses or 0.0,
            variable_expenses=request.variable_expenses or 0.0,
            debt_payment=request.debt_payment,
            debt_outstanding=request.debt_outstanding,
            current_savings=request.current_savings,
            financial_goal=request.financial_goal,
            goal_amount=request.goal_amount,
            goal_deadline_months=request.goal_deadline_months,
            income_stability=request.income_stability,
        )

    def _response_from_plan(self, plan: BudgetPlan, request: PlanRequest) -> PlanResponse:
        user_profile = UserProfile(
            monthly_income=request.monthly_income,
            essential_expenses=request.fixed_expenses or 0.0,
            discretionary_expenses=request.variable_expenses or 0.0,
            monthly_savings=plan.summary.monthly_surplus,
        )
        allocation_dict = {
            "needs": plan.allocation.needs,
            "wants": plan.allocation.wants,
            "savings": plan.allocation.savings,
        }
        return PlanResponse(
            type=plan.type,
            summary=FinancialSummaryResponse(**asdict(plan.summary)),
            metrics=FinancialMetricsResponse(**asdict(plan.metrics)),
            allocation=BudgetAllocationResponse(**asdict(plan.allocation)),
            goal_assessment=GoalAssessmentResponse(**asdict (plan.goal_assessment)),
            warnings=plan.warnings,
            action_items=plan.action_items,
            allocation_50_30_20=allocation_dict,
            evaluation=evaluate_allocation(user_profile),
            savings_rate=plan.metrics.savings_rate,
        )
