"""Interface repository cho profile mẫu."""

from typing import Protocol

from app.schemas import MockProfileResponse


class ProfileRepository(Protocol):
    """Quy định hành vi repository profile cần có."""

    def list_profiles(self) -> list[MockProfileResponse]:
        """Trả danh sách profile mẫu."""
