"""Rule Engine — tính chỉ số & đề xuất phân bổ ngân sách (deterministic)."""
from budgetbot.rules.models import UserProfile

RULE_50_30_20 = {"needs": 0.50, "wants": 0.30, "savings": 0.20}


def savings_rate(income: float, savings: float) -> float:
    """Tỷ lệ tiết kiệm = savings / income (0..1)."""
    if income <= 0:
        raise ValueError("income must be positive")
    return savings / income


def allocation_50_30_20(income: float) -> dict[str, float]:
    """Phân bổ gợi ý theo 50/30/20."""
    if income <= 0:
        raise ValueError("income must be positive")
    return {k: round(income * r, 2) for k, r in RULE_50_30_20.items()}


def emergency_fund_target(monthly_essential: float, months: int = 6) -> float:
    """Quỹ khẩn cấp mục tiêu = chi phí thiết yếu * số tháng (khuyến nghị 3-6)."""
    if monthly_essential < 0 or months <= 0:
        raise ValueError("invalid input")
    return round(monthly_essential * months, 2)


def goal_timeline(target_amount: float, monthly_savings: float) -> float:
    """Số tháng để đạt mục tiêu = target / tiết kiệm hằng tháng."""
    if monthly_savings <= 0:
        raise ValueError("monthly_savings must be positive")
    return round(target_amount / monthly_savings, 1)


def evaluate_allocation(profile: UserProfile) -> dict:
    """So phân bổ thực tế với 50/30/20, gắn cờ vượt/thấp hơn khuyến nghị."""
    income = profile.monthly_income
    if income <= 0:
        raise ValueError("income must be positive")
    actual = {
        "needs": profile.essential_expenses / income,
        "wants": profile.discretionary_expenses / income,
        "savings": profile.monthly_savings / income,
    }
    result = {}
    for cat, target in RULE_50_30_20.items():
        a = round(actual[cat], 3)
        if cat == "savings":
            status = "ok" if a >= target else "thấp hơn khuyến nghị"
        else:
            status = "ok" if a <= target else "vượt khuyến nghị"
        result[cat] = {"actual": a, "target": target, "status": status}
    return result
