"""Interface truy xuất dữ liệu cho hồ sơ mẫu."""

from typing import Protocol

from app.schemas import MockProfileResponse


class ProfileRepository(Protocol):
    """Quy định hành vi truy xuất hồ sơ cần có."""

    def list_profiles(self) -> list[MockProfileResponse]:
        """Trả danh sách hồ sơ mẫu."""
