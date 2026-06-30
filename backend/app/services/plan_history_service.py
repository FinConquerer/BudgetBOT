"""Service xử lý lịch sử kế hoạch ngân sách."""

from typing import Any

from fastapi import HTTPException, status

from app.repositories.plan_repository import PlanRecord, PlanRepository
from app.repositories.user_repository import UserRecord
from app.schemas import (
    DeletePlanResponse,
    PlanListItemResponse,
    PlanListResponse,
    PlanRequest,
    PlanResponse,
    SavedPlanResponse,
)
from app.services.budget_service import BudgetService


class PlanHistoryService:
    """Trường hợp sử dụng lưu, đọc danh sách, xem chi tiết và xóa lịch sử kế hoạch."""

    def __init__(
        self,
        *,
        plan_repository: PlanRepository,
        budget_service: BudgetService,
    ):
        self.plan_repository = plan_repository
        self.budget_service = budget_service

    def create_plan(
        self,
        *,
        current_user: UserRecord,
        request: PlanRequest,
    ) -> SavedPlanResponse:
        calculated_plan = self.budget_service.create_plan(request)
        record = self.plan_repository.create_plan(
            user_id=current_user.id,
            input_data=self._input_data(request),
            result=calculated_plan.model_dump(mode="json"),
        )
        return self._detail_response(record)

    def list_plans(
        self,
        *,
        current_user: UserRecord,
        limit: int,
        offset: int,
    ) -> PlanListResponse:
        records = self.plan_repository.list_plans(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
        total = self.plan_repository.count_plans(user_id=current_user.id)
        return PlanListResponse(
            items=[self._list_item_response(record) for record in records],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_plan(
        self,
        *,
        current_user: UserRecord,
        plan_id: str,
    ) -> SavedPlanResponse:
        record = self.plan_repository.get_plan(
            user_id=current_user.id,
            plan_id=plan_id,
        )
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )
        return self._detail_response(record)

    def delete_plan(
        self,
        *,
        current_user: UserRecord,
        plan_id: str,
    ) -> DeletePlanResponse:
        deleted = self.plan_repository.delete_plan(
            user_id=current_user.id,
            plan_id=plan_id,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )
        return DeletePlanResponse(id=plan_id, deleted=True)

    def _detail_response(self, record: PlanRecord) -> SavedPlanResponse:
        return SavedPlanResponse(
            id=record.id,
            user_id=record.user_id,
            input_data=record.input_data,
            result=PlanResponse.model_validate(record.result),
            created_at=record.created_at,
        )

    def _list_item_response(self, record: PlanRecord) -> PlanListItemResponse:
        summary = record.result.get("summary", {})
        return PlanListItemResponse(
            id=record.id,
            financial_goal=self._str_or_none(record.input_data.get("financial_goal")),
            monthly_income=float(summary.get("monthly_income", 0.0)),
            monthly_surplus=float(summary.get("monthly_surplus", 0.0)),
            created_at=record.created_at,
        )

    def _input_data(self, request: PlanRequest) -> dict[str, Any]:
        return {
            "monthly_income": request.monthly_income,
            "fixed_expenses": request.fixed_expenses or 0.0,
            "variable_expenses": request.variable_expenses or 0.0,
            "debt_payment": request.debt_payment,
            "debt_outstanding": request.debt_outstanding,
            "current_savings": request.current_savings,
            "financial_goal": request.financial_goal,
            "goal_amount": request.goal_amount,
            "goal_deadline_months": request.goal_deadline_months,
            "income_stability": request.income_stability,
        }

    def _str_or_none(self, value: Any) -> str | None:
        return value if isinstance(value, str) else None
