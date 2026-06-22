"""REST endpoints — Frontend React gọi vào đây."""

from fastapi import APIRouter, Depends

from app.dependencies import get_budget_service
from app.schemas import (
    MockProfileResponse,
    PlanRequest,
    PlanResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.budget_service import BudgetService

router = APIRouter()


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
