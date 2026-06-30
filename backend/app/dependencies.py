"""Các hàm cung cấp dependency dùng cho FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.chat_repository import (
    ChatRepository,
    SQLAlchemyChatRepository,
)
from app.repositories.faq_repository import (
    FaqSearchRepository,
    SQLAlchemyFaqSearchRepository,
)
from app.repositories.mock_profile_repository import MockProfileRepository
from app.repositories.plan_repository import (
    PlanRepository,
    SQLAlchemyPlanRepository,
)
from app.repositories.user_repository import (
    SQLAlchemyUserRepository,
    UserRecord,
    UserRepository,
)
from app.services.auth_service import AuthService
from app.services.budget_service import BudgetService
from app.services.chat_history_service import ChatHistoryService
from app.services.plan_history_service import PlanHistoryService

bearer_scheme = HTTPBearer(auto_error=False)


def get_budget_service() -> BudgetService:
    """Tạo service ngân sách với nguồn hồ sơ mẫu khi chưa có DB."""
    return BudgetService(profile_repository=MockProfileRepository())


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(db)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository=user_repository)


def get_plan_repository(db: Session = Depends(get_db)) -> PlanRepository:
    return SQLAlchemyPlanRepository(db)


def get_plan_history_service(
    plan_repository: PlanRepository = Depends(get_plan_repository),
    budget_service: BudgetService = Depends(get_budget_service),
) -> PlanHistoryService:
    return PlanHistoryService(
        plan_repository=plan_repository,
        budget_service=budget_service,
    )


def get_chat_repository(db: Session = Depends(get_db)) -> ChatRepository:
    return SQLAlchemyChatRepository(db)


def get_faq_search_repository(db: Session = Depends(get_db)) -> FaqSearchRepository:
    return SQLAlchemyFaqSearchRepository(db)


def get_chat_history_service(
    chat_repository: ChatRepository = Depends(get_chat_repository),
    faq_repository: FaqSearchRepository = Depends(get_faq_search_repository),
) -> ChatHistoryService:
    return ChatHistoryService(
        chat_repository=chat_repository,
        faq_repository=faq_repository,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserRecord:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return service.get_current_user(credentials.credentials)
