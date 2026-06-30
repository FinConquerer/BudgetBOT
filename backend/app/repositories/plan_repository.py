"""Interface truy xuất dữ liệu và adapter SQLAlchemy cho lịch sử kế hoạch ngân sách."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import BudgetPlanHistory


@dataclass(frozen=True)
class PlanRecord:
    id: str
    user_id: str
    input_data: dict[str, Any]
    result: dict[str, Any]
    created_at: datetime
    deleted_at: datetime | None = None


class PlanRepository(Protocol):
    def create_plan(
        self,
        *,
        user_id: str,
        input_data: dict[str, Any],
        result: dict[str, Any],
    ) -> PlanRecord:
        """Lưu một kế hoạch ngân sách đã tính cho một user."""

    def list_plans(self, *, user_id: str, limit: int, offset: int) -> list[PlanRecord]:
        """Lấy danh sách kế hoạch chưa xóa thuộc một user."""

    def count_plans(self, *, user_id: str) -> int:
        """Đếm số kế hoạch chưa xóa thuộc một user."""

    def get_plan(self, *, user_id: str, plan_id: str) -> PlanRecord | None:
        """Lấy một kế hoạch chưa xóa theo id và chủ sở hữu."""

    def delete_plan(self, *, user_id: str, plan_id: str) -> bool:
        """Đánh dấu xóa mềm một kế hoạch theo id và chủ sở hữu."""


class SQLAlchemyPlanRepository:
    """Lớp truy xuất SQLAlchemy cho bảng thật `budget_plans`."""

    def __init__(self, db: Session):
        self.db = db

    def create_plan(
        self,
        *,
        user_id: str,
        input_data: dict[str, Any],
        result: dict[str, Any],
    ) -> PlanRecord:
        plan = BudgetPlanHistory(
            id=str(uuid4()),
            user_id=user_id,
            input_data=input_data,
            result=result,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return self._to_record(plan)

    def list_plans(self, *, user_id: str, limit: int, offset: int) -> list[PlanRecord]:
        plans = (
            self.db.query(BudgetPlanHistory)
            .filter(
                BudgetPlanHistory.user_id == user_id,
                BudgetPlanHistory.deleted_at.is_(None),
            )
            .order_by(BudgetPlanHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_record(plan) for plan in plans]

    def count_plans(self, *, user_id: str) -> int:
        return (
            self.db.query(BudgetPlanHistory)
            .filter(
                BudgetPlanHistory.user_id == user_id,
                BudgetPlanHistory.deleted_at.is_(None),
            )
            .count()
        )

    def get_plan(self, *, user_id: str, plan_id: str) -> PlanRecord | None:
        plan = (
            self.db.query(BudgetPlanHistory)
            .filter(
                BudgetPlanHistory.id == plan_id,
                BudgetPlanHistory.user_id == user_id,
                BudgetPlanHistory.deleted_at.is_(None),
            )
            .first()
        )
        return self._to_record(plan) if plan else None

    def delete_plan(self, *, user_id: str, plan_id: str) -> bool:
        plan = (
            self.db.query(BudgetPlanHistory)
            .filter(
                BudgetPlanHistory.id == plan_id,
                BudgetPlanHistory.user_id == user_id,
                BudgetPlanHistory.deleted_at.is_(None),
            )
            .first()
        )
        if not plan:
            return False
        plan.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

    def _to_record(self, plan: BudgetPlanHistory) -> PlanRecord:
        return PlanRecord(
            id=plan.id,
            user_id=plan.user_id,
            input_data=plan.input_data,
            result=plan.result,
            created_at=plan.created_at,
            deleted_at=plan.deleted_at,
        )
