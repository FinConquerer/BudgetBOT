"""Rule tạo gợi ý hành động cho budget plan."""

from app.core.rules.models import BudgetProfile, GoalAssessment


def generate_action_items(
    profile: BudgetProfile,
    monthly_surplus: float,
    savings_rate: float,
    goal_assessment: GoalAssessment,
) -> list[str]:
    """Tạo 3-5 hành động ưu tiên dựa trên tình trạng tài chính."""
    actions: list[str] = []

    if monthly_surplus < 0:
        actions.append("Ưu tiên đưa dòng tiền về dương bằng cách giảm chi linh hoạt.")
    if profile.debt_outstanding > 0 and profile.debt_payment > 0:
        actions.append("Theo dõi lịch trả nợ và tránh phát sinh thêm nợ mới.")
    if savings_rate < 0.2:
        actions.append("Tăng dần tỷ lệ tiết kiệm hướng tới mức 20% thu nhập.")
    if profile.income_stability != "stable":
        actions.append("Tăng quỹ khẩn cấp vì thu nhập chưa ổn định.")
    if goal_assessment.status == "not_feasible":
        actions.append(
            "Điều chỉnh deadline, giảm quy mô mục tiêu hoặc tăng khoản tiết kiệm mỗi tháng."
        )
    elif goal_assessment.status == "feasible":
        actions.append("Duy trì khoản tiết kiệm mục tiêu theo kế hoạch hiện tại.")

    actions.append("Theo dõi chi tiêu cố định và chi tiêu linh hoạt hằng tháng.")
    return actions[:5]
