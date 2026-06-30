"""Các điểm cuối REST để Frontend React gọi vào."""

import os

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_auth_service,
    get_budget_service,
    get_chat_history_service,
    get_current_user,
    get_plan_history_service,
)
from app.repositories.user_repository import UserRecord
from app.schemas import (
    ChatAskRequest,
    ChatAskResponse,
    ChatCreateRequest,
    ChatListResponse,
    ChatMessagesResponse,
    ChatSessionResponse,
    ChatUpdateRequest,
    DeleteChatResponse,
    DeletePlanResponse,
    LoginResponse,
    PlanListResponse,
    PlanRequest,
    PlanResponse,
    SavedPlanResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    VersionResponse,
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.auth_service import AuthService
from app.services.budget_service import BudgetService
from app.services.chat_history_service import ChatHistoryService
from app.services.plan_history_service import PlanHistoryService

router = APIRouter()


@router.get("/version", response_model=VersionResponse, tags=["meta"])
def version() -> VersionResponse:
    return VersionResponse(environment=os.getenv("ENVIRONMENT", "development"))


@router.post("/auth/register", response_model=UserResponse, tags=["auth"])
def register(
    req: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    return service.register(req)


@router.post("/auth/login", response_model=LoginResponse, tags=["auth"])
def login(
    req: UserLoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    return service.login(req)


@router.get("/auth/me", response_model=UserResponse, tags=["auth"])
def read_me(current_user: UserRecord = Depends(get_current_user)) -> UserRecord:
    return current_user


@router.post("/chats", response_model=ChatSessionResponse, tags=["chat"])
def create_chat(
    req: ChatCreateRequest,
    current_user: UserRecord = Depends(get_current_user),
    service: ChatHistoryService = Depends(get_chat_history_service),
) -> ChatSessionResponse:
    return service.create_chat(current_user=current_user, request=req)


@router.get("/chats", response_model=ChatListResponse, tags=["chat"])
def list_chats(
    limit: int = 20,
    offset: int = 0,
    current_user: UserRecord = Depends(get_current_user),
    service: ChatHistoryService = Depends(get_chat_history_service),
) -> ChatListResponse:
    return service.list_chats(current_user=current_user, limit=limit, offset=offset)


@router.get("/chats/{chat_id}", response_model=ChatSessionResponse, tags=["chat"])
def get_chat(
    chat_id: str,
    current_user: UserRecord = Depends(get_current_user),
    service: ChatHistoryService = Depends(get_chat_history_service),
) -> ChatSessionResponse:
    return service.get_chat(current_user=current_user, chat_id=chat_id)


@router.put("/chats/{chat_id}", response_model=ChatSessionResponse, tags=["chat"])
def update_chat(
    chat_id: str,
    req: ChatUpdateRequest,
    current_user: UserRecord = Depends(get_current_user),
    service: ChatHistoryService = Depends(get_chat_history_service),
) -> ChatSessionResponse:
    return service.update_chat(current_user=current_user, chat_id=chat_id, request=req)


@router.delete("/chats/{chat_id}", response_model=DeleteChatResponse, tags=["chat"])
def delete_chat(
    chat_id: str,
    current_user: UserRecord = Depends(get_current_user),
    service: ChatHistoryService = Depends(get_chat_history_service),
) -> DeleteChatResponse:
    return service.delete_chat(current_user=current_user, chat_id=chat_id)


@router.get(
    "/chats/{chat_id}/messages",
    response_model=ChatMessagesResponse,
    tags=["chat"],
)
def list_chat_messages(
    chat_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: UserRecord = Depends(get_current_user),
    service: ChatHistoryService = Depends(get_chat_history_service),
) -> ChatMessagesResponse:
    return service.list_messages(
        current_user=current_user,
        chat_id=chat_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/chats/{chat_id}/ask",
    response_model=ChatAskResponse,
    tags=["chat"],
)
def ask_chat(
    chat_id: str,
    req: ChatAskRequest,
    current_user: UserRecord = Depends(get_current_user),
    service: ChatHistoryService = Depends(get_chat_history_service),
) -> ChatAskResponse:
    return service.ask(current_user=current_user, chat_id=chat_id, request=req)


@router.post("/plans", response_model=SavedPlanResponse, tags=["plan-history"])
def create_saved_plan(
    req: PlanRequest,
    current_user: UserRecord = Depends(get_current_user),
    service: PlanHistoryService = Depends(get_plan_history_service),
) -> SavedPlanResponse:
    return service.create_plan(current_user=current_user, request=req)


@router.get("/plans", response_model=PlanListResponse, tags=["plan-history"])
def list_saved_plans(
    limit: int = 20,
    offset: int = 0,
    current_user: UserRecord = Depends(get_current_user),
    service: PlanHistoryService = Depends(get_plan_history_service),
) -> PlanListResponse:
    return service.list_plans(current_user=current_user, limit=limit, offset=offset)


@router.get("/plans/{plan_id}", response_model=SavedPlanResponse, tags=["plan-history"])
def get_saved_plan(
    plan_id: str,
    current_user: UserRecord = Depends(get_current_user),
    service: PlanHistoryService = Depends(get_plan_history_service),
) -> SavedPlanResponse:
    return service.get_plan(current_user=current_user, plan_id=plan_id)


@router.delete(
    "/plans/{plan_id}",
    response_model=DeletePlanResponse,
    tags=["plan-history"],
)
def delete_saved_plan(
    plan_id: str,
    current_user: UserRecord = Depends(get_current_user),
    service: PlanHistoryService = Depends(get_plan_history_service),
) -> DeletePlanResponse:
    return service.delete_plan(current_user=current_user, plan_id=plan_id)


@router.post("/plan", response_model=PlanResponse, tags=["plan"])
def make_plan(
    req: PlanRequest,
    service: BudgetService = Depends(get_budget_service),
) -> PlanResponse:
    """Tạo kế hoạch ngân sách bằng rulebase xác định."""
    return service.create_plan(req)


@router.post("/what-if", response_model=WhatIfResponse, tags=["plan"])
def run_what_if(
    req: WhatIfRequest,
    service: BudgetService = Depends(get_budget_service),
) -> WhatIfResponse:
    """Tính lại kế hoạch ngân sách sau một thay đổi giả định."""
    return service.run_what_if(req)
