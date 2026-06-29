"""REST endpoints — Frontend React gọi vào đây."""

import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.chatbot.router import analyze_message
from app.db.database import get_db
from app.db.models import Faq

from app.dependencies import get_budget_service
from app.schemas import (
    FaqAskRequest,
    FaqAskResponse,
    FaqListResponse,
    FaqResponse,
    MockProfileResponse,
    PlanRequest,
    PlanResponse,
    VersionResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.budget_service import BudgetService

router = APIRouter()


def _faq_response(item: Faq) -> FaqResponse:
    return FaqResponse(
        id=item.faq_key,
        question=item.question,
        answer=item.answer,
        keywords=list(item.keywords or []),
        is_active=item.is_active,
    )


@router.get("/version", response_model=VersionResponse, tags=["meta"])
def version() -> VersionResponse:
    """Lấy version backend/API để FE debug hoặc hiển thị."""
    return VersionResponse(
        name="BudgetBOT Rulebase API",
        version="0.1.0",
        environment=os.getenv("APP_ENV", "development"),
    )


@router.post("/plan", response_model=PlanResponse, tags=["plan"])
def make_plan(
    req: PlanRequest,
    service: BudgetService = Depends(get_budget_service),
) -> PlanResponse:
    """Tạo budget plan bằng rulebase deterministic."""
    return service.create_plan(req)


@router.post("/what-if", response_model=WhatIfResponse, tags=["plan"])
def run_what_if(
    req: WhatIfRequest,
    service: BudgetService = Depends(get_budget_service),
) -> WhatIfResponse:
    """Tính lại budget plan sau một thay đổi giả định."""
    return service.run_what_if(req)


@router.get("/mock-profiles", response_model=list[MockProfileResponse], tags=["mock"])
def list_mock_profiles(
    service: BudgetService = Depends(get_budget_service),
) -> list[MockProfileResponse]:
    """Trả hồ sơ mẫu để test/demo API khi chưa có database profile."""
    return service.list_mock_profiles()


@router.post("/faq", response_model=FaqAskResponse, tags=["faq"])
def ask_faq(req: FaqAskRequest) -> FaqAskResponse:
    """Endpoint tương thích FE hiện tại: hỏi một câu và nhận câu trả lời."""
    result = analyze_message(req.question)
    return FaqAskResponse(
        answer=result.answer,
        intent=result.intent,
        sentiment=result.sentiment,
        confidence=result.confidence,
        status=result.status,
    )


@router.get("/faqs", response_model=FaqListResponse, tags=["faq"])
def list_faqs(
    q: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> FaqListResponse:
    """Lấy danh sách FAQ public, có tìm kiếm theo câu hỏi/answer/keyword."""
    query = db.query(Faq).filter(Faq.is_active.is_(True))
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Faq.faq_key.ilike(pattern),
                Faq.question.ilike(pattern),
                Faq.answer.ilike(pattern),
            )
        )
    total = query.count()
    items = query.order_by(Faq.id).offset(offset).limit(limit).all()
    return FaqListResponse(
        items=[_faq_response(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/faqs/{faq_id}", response_model=FaqResponse, tags=["faq"])
def get_faq(faq_id: str, db: Session = Depends(get_db)) -> FaqResponse:
    """Lấy chi tiết một FAQ public theo id dataset, ví dụ GREET_001."""
    item = db.query(Faq).filter(Faq.faq_key == faq_id, Faq.is_active.is_(True)).first()
    if item is None and faq_id.isdigit():
        item = db.query(Faq).filter(Faq.id == int(faq_id), Faq.is_active.is_(True)).first()
    if item is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return _faq_response(item)
