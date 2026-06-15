"""REST endpoints — Frontend React gọi vào đây."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.faq.faq import answer as faq_answer
from app.core.rules.engine import (
    allocation_50_30_20,
    evaluate_allocation,
    savings_rate,
)
from app.core.rules.models import UserProfile
from app.db.database import get_db
from app.db.models import Faq
from app.schemas import FaqAnswer, FaqQuery, PlanRequest, PlanResponse

router = APIRouter()


@router.post("/faq", response_model=FaqAnswer, tags=["faq"])
def ask_faq(query: FaqQuery, db: Session = Depends(get_db)) -> FaqAnswer:
    """Tra cứu FAQ từ Postgres (fallback faq.json nếu DB rỗng)."""
    rows = db.query(Faq).all()
    faqs = [{"question": r.question, "answer": r.answer, "keywords": r.keywords} for r in rows]
    return FaqAnswer(answer=faq_answer(query.question, faqs or None))


@router.post("/plan", response_model=PlanResponse, tags=["plan"])
def make_plan(req: PlanRequest) -> PlanResponse:
    """Tính phân bổ 50/30/20, đánh giá phân bổ hiện tại và tỷ lệ tiết kiệm."""
    profile = UserProfile(
        monthly_income=req.monthly_income,
        essential_expenses=req.essential_expenses,
        discretionary_expenses=req.discretionary_expenses,
        monthly_savings=req.monthly_savings,
    )
    return PlanResponse(
        allocation_50_30_20=allocation_50_30_20(req.monthly_income),
        evaluation=evaluate_allocation(profile),
        savings_rate=round(savings_rate(req.monthly_income, req.monthly_savings), 3),
    )
