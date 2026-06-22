from app.repositories.mock_profile_repository import MockProfileRepository


def test_mock_profile_repository_list_profiles():
    profiles = MockProfileRepository().list_profiles()

    assert profiles
    assert profiles[0].profile.monthly_income > 0
