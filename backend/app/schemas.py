"""Pydantic schemas — hợp đồng dữ liệu giữa Frontend (React) và API."""
from pydantic import BaseModel, Field


class FaqQuery(BaseModel):
    question: str = Field(..., min_length=1, examples=["Nên tiết kiệm bao nhiêu %?"])


class FaqAnswer(BaseModel):
    answer: str


class PlanRequest(BaseModel):
    """Thông tin người dùng để đánh giá phân bổ ngân sách."""
    monthly_income: float = Field(..., gt=0)
    essential_expenses: float = Field(0.0, ge=0)
    discretionary_expenses: float = Field(0.0, ge=0)
    monthly_savings: float = Field(0.0, ge=0)


class CategoryEval(BaseModel):
    actual: float
    target: float
    status: str


class PlanResponse(BaseModel):
    allocation_50_30_20: dict[str, float]
    evaluation: dict[str, CategoryEval]
    savings_rate: float
