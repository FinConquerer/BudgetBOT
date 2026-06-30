"""Các phép tính tài chính thuần cho rulebase."""

from app.core.rules.constants import NEEDS_RATIO, SAVINGS_RATIO, WANTS_RATIO
from app.core.rules.models import BudgetAllocation


def calculate_total_expenses(
    fixed_expenses: float,
    variable_expenses: float,
    debt_payment: float,
) -> float:
    """Tính tổng chi phí hàng tháng."""
    return fixed_expenses + variable_expenses + debt_payment


def calculate_monthly_surplus(monthly_income: float, total_expenses: float) -> float:
    """Tính dòng tiền dư hàng tháng."""
    return monthly_income - total_expenses


def calculate_ratio(amount: float, base: float) -> float:
    """Tính tỷ lệ amount/base, trả 0 nếu base không dương."""
    if base <= 0:
        return 0.0
    return round(amount / base, 3)


def calculate_required_monthly_saving(goal_amount: float, deadline_months: int | None) -> float:
    """Tính số tiền cần tiết kiệm mỗi tháng để đạt mục tiêu."""
    if goal_amount <= 0 or not deadline_months:
        return 0.0
    return round(goal_amount / deadline_months, 2)


def calculate_50_30_20_allocation(monthly_income: float) -> BudgetAllocation:
    """Tính phân bổ ngân sách theo 50/30/20."""
    return BudgetAllocation(
        needs=round(monthly_income * NEEDS_RATIO, 2),
        wants=round(monthly_income * WANTS_RATIO, 2),
        savings=round(monthly_income * SAVINGS_RATIO, 2),
    )


def calculate_emergency_fund_target(monthly_essential: float, months: int) -> float:
    """Tính mức quỹ khẩn cấp mục tiêu."""
    return round(monthly_essential * months, 2)
