# Module `backend/app/repositories`

## Giải thích tổng quan

Repository là lớp che giấu nguồn dữ liệu. Nếu service cần danh sách profile mẫu, service không tự đọc file mock. Service chỉ gọi repository. Repository quyết định lấy dữ liệu từ đâu.

Hiện tại repository trong code chỉ dùng mock data, chưa query database.

## Mục đích

- Tách service khỏi nguồn dữ liệu cụ thể.
- Cho phép dùng mock profiles khi chưa có database active.
- Chuẩn bị interface để sau này có thể thay implementation.

## Cấu trúc thư mục liên quan

```text
backend/app/repositories/
  __init__.py
  profile_repository.py
  mock_profile_repository.py

backend/app/mocks/
  sample_profiles.py
```

## Danh sách file

### `profile_repository.py`

Class:

- `ProfileRepository`

Method yêu cầu:

- `list_profiles()`

Đây là `Protocol`, nghĩa là interface theo kiểu Python.

### `mock_profile_repository.py`

Class:

- `MockProfileRepository`

Method:

- `list_profiles()`

### `__init__.py`

Hiện không có logic đáng kể.

## Ai gọi module

Đường dẫn file: `backend/app/dependencies.py`

Function: `get_budget_service()`

Nó gọi:

- `MockProfileRepository()`

Đường dẫn file: `backend/app/services/budget_service.py`

Class: `BudgetService`

Method:

- `list_mock_profiles()` gọi `self.profile_repository.list_profiles()`.

## Module gọi ai

Đường dẫn file: `backend/app/repositories/mock_profile_repository.py`

Class: `MockProfileRepository`

Method: `list_profiles()`

Nó gọi tiếp:

- `SAMPLE_PROFILES` từ `backend/app/mocks/sample_profiles.py`.
- `MockProfileResponse.model_validate(item)` từ `backend/app/schemas.py`.

## Input và output

### `MockProfileRepository.list_profiles()`

Input:

- Không nhận tham số.

Output:

- `list[MockProfileResponse]`

## Luồng chạy

```text
GET /api/mock-profiles
-> backend/app/api/routes.py
   function list_mock_profiles()
-> BudgetService.list_mock_profiles()
-> MockProfileRepository.list_profiles()
-> SAMPLE_PROFILES
-> MockProfileResponse.model_validate()
-> list[MockProfileResponse]
```

## Ví dụ thực tế

Đường dẫn file: `backend/tests/test_profile_repository.py`

Function test: `test_mock_profile_repository_list_profiles()`

Code test gọi:

```text
profiles = MockProfileRepository().list_profiles()
```

Kết quả mong đợi:

```text
profiles không rỗng
profiles[0].profile.monthly_income > 0
```

## Test liên quan

- `backend/tests/test_profile_repository.py`
- `backend/tests/test_api.py`, function `test_mock_profiles_endpoint()`

## Python cần hiểu

- `Protocol`: mô tả object cần có method gì.
- `list[MockProfileResponse]`: danh sách các object `MockProfileResponse`.
- `model_validate()`: Pydantic validate dict thành schema object.
- Import constant: `SAMPLE_PROFILES` là dữ liệu mock được import từ file khác.

Ví dụ đời thường: `ProfileRepository` giống yêu cầu "kho dữ liệu nào cũng phải có quầy list_profiles". `MockProfileRepository` là một kho giả đang đáp ứng yêu cầu đó.

## Đã có, chưa có, ngoài scope

Đã có trong code:

- Interface `ProfileRepository`.
- Mock implementation `MockProfileRepository`.
- Mock data trong `SAMPLE_PROFILES`.

Chưa có trong code:

- `SqlProfileRepository`.
- Query profile từ PostgreSQL.
- Lưu profile user thật.

Ngoài scope hiện tại:

- Repository cho authentication.
- Repository cho transaction history.

## Lỗi người mới thường gặp

- Tưởng repository hiện tại đang query DB. Thực tế nó đọc mock data.
- Sửa `SAMPLE_PROFILES` nhưng quên schema `MockProfileResponse` sẽ validate dữ liệu.
- Cho service import trực tiếp `SAMPLE_PROFILES`, làm mất ý nghĩa repository.
