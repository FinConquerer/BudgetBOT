"""Mô hình dữ liệu người dùng."""
from dataclasses import dataclass


@dataclass
class UserProfile:
    monthly_income: float
    essential_expenses: float = 0.0      # nhu cầu thiết yếu (needs)
    discretionary_expenses: float = 0.0  # mong muốn (wants)
    monthly_savings: float = 0.0
    age: int | None = None
    dependents: int = 0
    location: str | None = None
