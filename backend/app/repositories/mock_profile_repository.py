"""Repository đọc profile mẫu từ mock data."""

from app.mocks.sample_profiles import SAMPLE_PROFILES
from app.schemas import MockProfileResponse


class MockProfileRepository:
    """Cung cấp mock profiles khi database chưa sẵn sàng."""

    def list_profiles(self) -> list[MockProfileResponse]:
        """Trả danh sách hồ sơ mẫu để test/demo API."""
        return [MockProfileResponse.model_validate(item) for item in SAMPLE_PROFILES]
