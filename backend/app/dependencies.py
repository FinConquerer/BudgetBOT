"""FastAPI dependency providers."""

from app.repositories.mock_profile_repository import MockProfileRepository
from app.services.budget_service import BudgetService


def get_budget_service() -> BudgetService:
    """Tạo BudgetService với mock repository trong giai đoạn chưa có DB profile."""
    return BudgetService(profile_repository=MockProfileRepository())
