"""Pydantic schemas — hợp đồng dữ liệu giữa Frontend và API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

IncomeStability = Literal["stable", "unstable", "seasonal"]
GoalStatus = Literal["none", "feasible", "tight", "not_feasible"]
WhatIfField = Literal["monthly_income", "fixed_expenses", "variable_expenses", "debt_payment"]


class PlanRequest(BaseModel):
    """Thông tin người dùng để tạo budget plan."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "monthly_income": 20_000_000,
                    "fixed_expenses": 7_000_000,
                    "variable_expenses": 5_000_000,
                    "debt_payment": 1_000_000,
                    "debt_outstanding": 20_000_000,
                    "current_savings": 30_000_000,
                    "financial_goal": "mua laptop",
                    "goal_amount": 25_000_000,
                    "goal_deadline_months": 10,
                    "income_stability": "stable",
                }
            ]
        }
    )

    monthly_income: float = Field(..., gt=0)
    fixed_expenses: float | None = Field(None, ge=0)
    variable_expenses: float | None = Field(None, ge=0)
    debt_payment: float = Field(0.0, ge=0)
    debt_outstanding: float = Field(0.0, ge=0)
    current_savings: float = Field(0.0, ge=0)
    financial_goal: str | None = None
    goal_amount: float = Field(0.0, ge=0)
    goal_deadline_months: int | None = Field(None, ge=1)
    income_stability: IncomeStability = "stable"

    # Backward-compatible fields used by the first API version.
    essential_expenses: float | None = Field(None, ge=0)
    discretionary_expenses: float | None = Field(None, ge=0)
    monthly_savings: float | None = Field(None, ge=0)

    @model_validator(mode="after")
    def normalize_legacy_fields(self) -> "PlanRequest":
        """Map field cũ sang field mới để không phá API/test hiện có."""
        if self.fixed_expenses is None:
            self.fixed_expenses = self.essential_expenses or 0.0
        if self.variable_expenses is None:
            self.variable_expenses = self.discretionary_expenses or 0.0
        if self.current_savings == 0.0 and self.monthly_savings is not None:
            self.current_savings = self.monthly_savings
        return self


class FinancialSummaryResponse(BaseModel):
    monthly_income: float
    total_expenses: float
    monthly_surplus: float


class FinancialMetricsResponse(BaseModel):
    savings_rate: float
    expense_ratio: float
    debt_payment_ratio: float


class BudgetAllocationResponse(BaseModel):
    needs: float
    wants: float
    savings: float


class GoalAssessmentResponse(BaseModel):
    status: GoalStatus
    required_monthly_saving: float
    message: str


class CategoryEval(BaseModel):
    actual: float
    target: float
    status: str


class PlanResponse(BaseModel):
    type: Literal["budget_plan"] = "budget_plan"
    summary: FinancialSummaryResponse
    metrics: FinancialMetricsResponse
    allocation: BudgetAllocationResponse
    goal_assessment: GoalAssessmentResponse
    warnings: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)

    # Backward-compatible fields for the current tests/frontend prototype.
    allocation_50_30_20: dict[str, float]
    evaluation: dict[str, CategoryEval] = Field(default_factory=dict)
    savings_rate: float


class WhatIfChange(BaseModel):
    field: WhatIfField
    delta: float


class WhatIfRequest(BaseModel):
    profile: PlanRequest
    change: WhatIfChange


class WhatIfComparisonResponse(BaseModel):
    monthly_surplus_delta: float
    savings_rate_delta: float


class WhatIfResponse(BaseModel):
    type: Literal["what_if"] = "what_if"
    before: PlanResponse
    after: PlanResponse
    comparison: WhatIfComparisonResponse


class MockProfileResponse(BaseModel):
    id: str
    name: str
    description: str
    profile: PlanRequest
