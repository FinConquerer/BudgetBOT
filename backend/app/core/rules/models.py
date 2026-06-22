"""Mô hình dữ liệu nội bộ cho rulebase ngân sách."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class UserProfile:
    """Model cũ dùng cho rule 50/30/20 hiện có."""

    monthly_income: float
    essential_expenses: float = 0.0  # nhu cầu thiết yếu (needs)
    discretionary_expenses: float = 0.0  # mong muốn (wants)
    monthly_savings: float = 0.0
    age: int | None = None
    dependents: int = 0
    location: str | None = None


IncomeStability = Literal["stable", "unstable", "seasonal"]
GoalStatus = Literal["none", "feasible", "tight", "not_feasible"]


@dataclass(frozen=True)
class BudgetProfile:
    """Thông tin tài chính đầu vào cho rulebase budget planner."""

    monthly_income: float
    fixed_expenses: float = 0.0
    variable_expenses: float = 0.0
    debt_payment: float = 0.0
    debt_outstanding: float = 0.0
    current_savings: float = 0.0
    financial_goal: str | None = None
    goal_amount: float = 0.0
    goal_deadline_months: int | None = None
    income_stability: IncomeStability = "stable"


@dataclass(frozen=True)
class FinancialSummary:
    """Tổng quan dòng tiền hàng tháng."""

    monthly_income: float
    total_expenses: float
    monthly_surplus: float


@dataclass(frozen=True)
class FinancialMetrics:
    """Các chỉ số tài chính chính để frontend hiển thị."""

    savings_rate: float
    expense_ratio: float
    debt_payment_ratio: float


@dataclass(frozen=True)
class BudgetAllocation:
    """Phân bổ ngân sách gợi ý."""

    needs: float
    wants: float
    savings: float


@dataclass(frozen=True)
class GoalAssessment:
    """Kết quả đánh giá mức độ khả thi của mục tiêu tài chính."""

    status: GoalStatus
    required_monthly_saving: float
    message: str


@dataclass(frozen=True)
class BudgetPlan:
    """Kết quả cuối cùng từ rulebase."""

    type: str
    summary: FinancialSummary
    metrics: FinancialMetrics
    allocation: BudgetAllocation
    goal_assessment: GoalAssessment
    warnings: list[str]
    action_items: list[str]
