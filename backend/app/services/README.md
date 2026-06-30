# Module `backend/app/services`

## Giải thích tổng quan

Service là lớp điều phối use case. Nếu route là quầy tiếp nhận, service là người xử lý hồ sơ: chuyển dữ liệu sang dạng nội bộ, gọi rulebase, gọi repository nếu cần, rồi đóng gói kết quả.

Trong code hiện tại, service chính là `BudgetService`.

## Mục đích

- Tách logic use case khỏi API route.
- Chuyển `PlanRequest` sang `BudgetProfile`.
- Gọi rulebase để tạo budget plan.
- Xử lý what-if.
- Lấy mock profiles thông qua repository.

## Cấu trúc thư mục liên quan

```text
backend/app/services/
  __init__.py
  budget_service.py
```

## Danh sách file

### `budget_service.py`

Class:

- `BudgetService`

Method:

- `__init__()`
- `create_plan()`
- `run_what_if()`
- `list_mock_profiles()`
- `_profile_from_request()`
- `_response_from_plan()`

### `__init__.py`

Hiện chỉ là file package, không có business logic đáng kể.

## Ai gọi module

Đường dẫn file: `backend/app/api/routes.py`

Function:

- `make_plan()` gọi `BudgetService.create_plan()`.
- `run_what_if()` gọi `BudgetService.run_what_if()`.
- `list_mock_profiles()` gọi `BudgetService.list_mock_profiles()`.

Đường dẫn file: `backend/app/dependencies.py`

Function:

- `get_budget_service()` tạo object `BudgetService`.

## Module gọi ai

Đường dẫn file: `backend/app/services/budget_service.py`

Class: `BudgetService`

Method `create_plan()` gọi:

- `self._profile_from_request()`
- `create_budget_plan()` từ `backend/app/core/rules/engine.py`
- `self._response_from_plan()`

Method `run_what_if()` gọi:

- `self.create_plan()`
- `self._profile_from_request()`
- `getattr()`
- `replace()`
- `PlanRequest(**asdict(updated_profile))`

Method `list_mock_profiles()` gọi:

- `self.profile_repository.list_profiles()`

Method `_response_from_plan()` gọi:

- `evaluate_allocation()` từ `backend/app/core/rules/engine.py`
- Các response schema trong `backend/app/schemas.py`

## Input và output

### `create_plan()`

Input:

- `PlanRequest`

Output:

- `PlanResponse`

### `run_what_if()`

Input:

- `WhatIfRequest`

Output:

- `WhatIfResponse`

### `list_mock_profiles()`

Input:

- Không có tham số.

Output:

- `list[MockProfileResponse]`

## Luồng chạy

### `create_plan()`

```text
PlanRequest
-> _profile_from_request()
-> BudgetProfile
-> create_budget_plan()
-> BudgetPlan
-> _response_from_plan()
-> PlanResponse
```

### `run_what_if()`

```text
WhatIfRequest
-> create_plan() cho before
-> lấy field cần thay đổi bằng getattr()
-> tạo BudgetProfile mới bằng replace()
-> create_plan() cho after
-> tính monthly_surplus_delta và savings_rate_delta
-> WhatIfResponse
```

### `list_mock_profiles()`

```text
BudgetService.list_mock_profiles()
-> profile_repository.list_profiles()
-> list[MockProfileResponse]
```

## Ví dụ thực tế

Đường dẫn file: `backend/tests/test_budget_service.py`

Function test: `test_budget_service_create_plan()`

Test tạo:

```text
BudgetService(profile_repository=MockProfileRepository())
```

Sau đó gọi:

```text
service.create_plan(PlanRequest(...))
```

Kết quả mong đợi:

```text
response.type == "budget_plan"
response.summary.monthly_surplus == 7000000
```

## Test liên quan

Đường dẫn file: `backend/tests/test_budget_service.py`

Test:

- `test_budget_service_create_plan()`
- `test_budget_service_run_what_if()`

## Python cần hiểu

- `self`: object hiện tại của class.
- `__init__`: method khởi tạo object.
- Dependency truyền từ ngoài vào: `profile_repository`.
- Method bắt đầu bằng `_`: convention nói rằng đây là helper nội bộ.
- `asdict()`: chuyển dataclass sang dict.
- `replace()`: tạo bản dataclass mới với field được thay đổi.

## Lỗi người mới thường gặp

- Nhầm service với rulebase. Service điều phối, rulebase tính toán.
- Cho service tự đọc file mock data trực tiếp. Code hiện dùng repository để tách nguồn dữ liệu.
- Sửa `run_what_if()` mà quên nó gọi lại `create_plan()` hai lần.
- Nhầm `current_savings` với `monthly_surplus`. `monthly_surplus` được rulebase tính từ income trừ expenses.
