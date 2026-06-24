"""Rule Engine — điều phối các rule để tạo budget plan deterministic."""

from app.core.rules.calculators import (
    calculate_50_30_20_allocation,
    calculate_monthly_surplus,
    calculate_ratio,
    calculate_required_monthly_saving,
    calculate_total_expenses,
)
from app.core.rules.constants import NEEDS_RATIO, SAVINGS_RATIO, WANTS_RATIO
from app.core.rules.evaluators import evaluate_goal_feasibility, evaluate_warnings
from app.core.rules.exceptions import RuleValidationError
from app.core.rules.models import (
    BudgetPlan,
    BudgetProfile,
    FinancialMetrics,
    FinancialSummary,
    UserProfile,
)
from app.core.rules.recommendations import generate_action_items

RULE_50_30_20 = {"needs": NEEDS_RATIO, "wants": WANTS_RATIO, "savings": SAVINGS_RATIO}


def savings_rate(income: float, savings: float) -> float:
    """Tỷ lệ tiết kiệm = savings / income (0..1)."""
    if income <= 0:
        raise ValueError("income must be positive")
    return savings / income


def allocation_50_30_20(income: float) -> dict[str, float]:
    """Phân bổ gợi ý theo 50/30/20."""
    if income <= 0:
        raise ValueError("income must be positive")
    allocation = calculate_50_30_20_allocation(income)
    return {
        "needs": allocation.needs,
        "wants": allocation.wants,
        "savings": allocation.savings,
    }


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


def validate_budget_profile(profile: BudgetProfile) -> None:
    """Kiểm tra input chính trước khi chạy rulebase."""
    if profile.monthly_income <= 0:
        raise RuleValidationError("monthly_income must be positive")
    numeric_fields = {
        "fixed_expenses": profile.fixed_expenses,
        "variable_expenses": profile.variable_expenses,
        "debt_payment": profile.debt_payment,
        "debt_outstanding": profile.debt_outstanding,
        "current_savings": profile.current_savings,
        "goal_amount": profile.goal_amount,
    }
    invalid_fields = [name for name, value in numeric_fields.items() if value < 0]
    if invalid_fields:
        raise RuleValidationError(f"{', '.join(invalid_fields)} must be non-negative")
    if profile.goal_amount > 0 and not profile.goal_deadline_months:
        raise RuleValidationError("goal_deadline_months is required when goal_amount is provided")
    if profile.goal_deadline_months is not None and profile.goal_deadline_months <= 0:
        raise RuleValidationError("goal_deadline_months must be positive")


def create_budget_plan(profile: BudgetProfile) -> BudgetPlan:
    """Tạo budget plan đầy đủ từ thông tin tài chính người dùng."""
    validate_budget_profile(profile)

    total_expenses = calculate_total_expenses(
        profile.fixed_expenses,
        profile.variable_expenses,
        profile.debt_payment,
    )
    monthly_surplus = calculate_monthly_surplus(profile.monthly_income, total_expenses)
    allocation = calculate_50_30_20_allocation(profile.monthly_income)
    required_monthly_saving = calculate_required_monthly_saving(
        profile.goal_amount,
        profile.goal_deadline_months,
    )
    goal_assessment = evaluate_goal_feasibility(
        profile.financial_goal,
        monthly_surplus,
        required_monthly_saving,
    )

    metrics = FinancialMetrics(
        savings_rate=calculate_ratio(max(monthly_surplus, 0.0), profile.monthly_income),
        expense_ratio=calculate_ratio(total_expenses, profile.monthly_income),
        debt_payment_ratio=calculate_ratio(profile.debt_payment, profile.monthly_income),
    )
    warnings = evaluate_warnings(
        monthly_surplus=monthly_surplus,
        savings_rate=metrics.savings_rate,
        fixed_expense_ratio=calculate_ratio(profile.fixed_expenses, profile.monthly_income),
        debt_payment_ratio=metrics.debt_payment_ratio,
    )
    action_items = generate_action_items(
        profile=profile,
        monthly_surplus=monthly_surplus,
        savings_rate=metrics.savings_rate,
        goal_assessment=goal_assessment,
    )

    return BudgetPlan(
        type="budget_plan",
        summary=FinancialSummary(
            monthly_income=profile.monthly_income,
            total_expenses=total_expenses,
            monthly_surplus=monthly_surplus,
        ),
        metrics=metrics,
        allocation=allocation,
        goal_assessment=goal_assessment,
        warnings=warnings,
        action_items=action_items,
    )
