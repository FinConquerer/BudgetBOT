# Module `backend/app/api`

## Giải thích tổng quan

Module này là lớp API route. Nếu backend là một văn phòng, `api/routes.py` là quầy tiếp nhận hồ sơ. Nó nhận HTTP request, để FastAPI validate input bằng schema, gọi service xử lý, rồi trả response.

Module này không chứa công thức tài chính chi tiết. Công thức nằm ở `backend/app/core/rules/`.

## Mục đích

- Khai báo endpoint backend active.
- Nhận request từ client, Swagger hoặc frontend.
- Gọi `BudgetService`.
- Trả response model rõ ràng.

## Cấu trúc thư mục liên quan

```text
backend/app/api/
  __init__.py
  routes.py
```

## Danh sách file

### `routes.py`

Function:

- `make_plan()`
- `run_what_if()`
- auth/chat/plan-history handlers

Object:

- `router = APIRouter()`

### `__init__.py`

Hiện không có logic.

## Ai gọi module

Đường dẫn file: `backend/app/main.py`

Object/function:

- `app.include_router(router, prefix="/api")`

Nó gọi module này để gắn các route vào FastAPI app.

Client gọi gián tiếp qua HTTP:

```text
POST /api/plan
POST /api/what-if
POST /api/chats/{chat_id}/ask
```

## Module gọi ai

Đường dẫn file: `backend/app/api/routes.py`

Function: `make_plan()`

Gọi tiếp:

- `get_budget_service()` qua `Depends`.
- `BudgetService.create_plan()`.

Function: `run_what_if()`

Gọi tiếp:

- `get_budget_service()` qua `Depends`.
- `BudgetService.run_what_if()`.

Function: `list_mock_profiles()`

Gọi tiếp:

- `get_budget_service()` qua `Depends`.
- `BudgetService.list_mock_profiles()`.

## Input và output

### `make_plan()`

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

- Không có request body.

Output:

- `list[MockProfileResponse]`

## Luồng chạy

```text
HTTP request
-> FastAPI route decorator
-> Pydantic schema validate input
-> Depends(get_budget_service)
-> BudgetService method
-> response_model serialize output
-> HTTP response JSON
```

## Ví dụ thực tế

Request:

```http
POST /api/plan
Content-Type: application/json
```

Body:

```json
{
  "monthly_income": 20000000,
  "fixed_expenses": 7000000,
  "variable_expenses": 5000000,
  "debt_payment": 1000000,
  "financial_goal": "mua laptop",
  "goal_amount": 25000000,
  "goal_deadline_months": 10
}
```

Route thực tế:

```text
backend/app/api/routes.py
function make_plan()
-> BudgetService.create_plan()
```

## Test liên quan

Đường dẫn file: `backend/tests/test_api.py`

Test:

- `test_plan_endpoint()`
- `test_plan_endpoint_extended_contract()`
- `test_what_if_endpoint()`
- `test_mock_profiles_endpoint()`

## Python cần hiểu

- `@router.post(...)`: decorator đăng ký endpoint POST.
- `response_model=PlanResponse`: ép output theo schema.
- `Depends(get_budget_service)`: FastAPI tự gọi dependency để lấy service.
- Type hint `-> PlanResponse`: nói function trả về `PlanResponse`.

## Lỗi người mới thường gặp

- Quên prefix `/api`. Trong file là `"/plan"`, URL thật là `"/api/plan"`.
- Viết công thức tài chính trực tiếp trong route.
- Không còn public `/api/faq`; hỏi đáp FAQ chính thức đi qua `/api/chats/{chat_id}/ask`.
- Tự tạo `BudgetService()` trong route thay vì dùng dependency đã có.
