"""Các rule đánh giá tình trạng tài chính."""

from app.core.rules.constants import (
    HIGH_DEBT_PAYMENT_RATIO,
    HIGH_FIXED_EXPENSE_RATIO,
    LOW_SAVINGS_RATE,
    TARGET_SAVINGS_RATE,
    TIGHT_GOAL_SURPLUS_USAGE,
)
from app.core.rules.models import GoalAssessment


def evaluate_goal_feasibility(
    financial_goal: str | None,
    monthly_surplus: float,
    required_monthly_saving: float,
) -> GoalAssessment:
    """Đánh giá mục tiêu tài chính là khả thi, căng hay không khả thi."""
    if not financial_goal or required_monthly_saving <= 0:
        return GoalAssessment(
            status="none",
            required_monthly_saving=0.0,
            message="Chưa có mục tiêu tài chính cụ thể để đánh giá.",
        )

    if monthly_surplus <= 0 or required_monthly_saving > monthly_surplus:
        return GoalAssessment(
            status="not_feasible",
            required_monthly_saving=required_monthly_saving,
            message="Mục tiêu chưa khả thi với dòng tiền hiện tại.",
        )

    usage_ratio = required_monthly_saving / monthly_surplus
    if usage_ratio >= TIGHT_GOAL_SURPLUS_USAGE:
        return GoalAssessment(
            status="tight",
            required_monthly_saving=required_monthly_saving,
            message="Mục tiêu có thể đạt được nhưng sẽ dùng gần hết dòng tiền dư.",
        )

    return GoalAssessment(
        status="feasible",
        required_monthly_saving=required_monthly_saving,
        message="Mục tiêu có khả thi với dòng tiền hiện tại.",
    )


def evaluate_warnings(
    monthly_surplus: float,
    savings_rate: float,
    fixed_expense_ratio: float,
    debt_payment_ratio: float,
) -> list[str]:
    """Tạo danh sách cảnh báo tài chính từ các chỉ số chính."""
    warnings: list[str] = []
    if monthly_surplus < 0:
        warnings.append("Dòng tiền hàng tháng đang âm, cần giảm chi hoặc tăng thu nhập.")
    if savings_rate < LOW_SAVINGS_RATE:
        warnings.append("Tỷ lệ tiết kiệm đang thấp hơn 10% thu nhập.")
    elif savings_rate < TARGET_SAVINGS_RATE:
        warnings.append("Tỷ lệ tiết kiệm chưa đạt mức khuyến nghị 20%.")
    if fixed_expense_ratio > HIGH_FIXED_EXPENSE_RATIO:
        warnings.append("Chi phí cố định đang chiếm hơn 50% thu nhập.")
    if debt_payment_ratio > HIGH_DEBT_PAYMENT_RATIO:
        warnings.append("Tỷ lệ trả nợ hàng tháng đang cao, cần theo dõi áp lực nợ.")
    return warnings
