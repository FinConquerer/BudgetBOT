# Kế Hoạch Backend Cuối Cùng - Rulebase Và API Trước

## 1. Hướng Làm Đã Chốt

Nhiệm vụ lần này là phát triển **output API backend cho rulebase budget planner**. Hiện tại **Frontend và Database chưa sẵn sàng**, nên backend sẽ được làm theo hướng:

- Bám sát cây thư mục hiện tại của dự án.
- Làm rulebase trước như lõi nghiệp vụ độc lập.
- Làm API contract rõ ràng để Frontend có thể tích hợp sau.
- Giả lập dữ liệu bằng mock profiles trong lúc chưa có Database.
- Kiểm thử API bằng Swagger, Postman hoặc FastAPI `TestClient`.

Mục tiêu là backend chạy độc lập được, có endpoint rõ ràng, có response mẫu ổn định, không phụ thuộc vào FE/DB trong giai đoạn hiện tại.

Scope hiện tại chỉ tập trung vào **rulebase budget planner**.

Active API trong branch này chỉ gồm:

```text
GET  /health
POST /api/plan
POST /api/what-if
GET  /api/mock-profiles
```

Phần FAQ và DB có thể còn tồn tại trong cây thư mục của repo để dùng cho task sau, nhưng **không nằm trong active runtime của nhánh rulebase này**:

- Không expose `/api/faq`.
- Không seed DB khi app khởi động.
- Không chạy test FAQ trong scope hiện tại.
- Không để rulebase API phụ thuộc SQLAlchemy/PostgreSQL.

## 1.1. Môi Trường Python Và Dependency Đã Chốt

Backend phải chạy trong virtual environment riêng, không cài dependency trực tiếp vào Python hệ thống.

Version đã chốt:

```text
Python: 3.11
FastAPI: 0.115.8
Pydantic: 2.13.1
Uvicorn: 0.44.0
Pytest: 9.0.1
HTTPX: 0.28.1
Ruff: 0.13.2
```

Cơ sở chốt:

- `backend/Dockerfile` đang dùng `python:3.11-slim`.
- `backend/.python-version` đặt là `3.11`.
- `backend/requirements.txt` và `backend/requirements-dev.txt` đã pin version cụ thể để tái lập môi trường ổn định.
- SQLAlchemy/PostgreSQL chưa nằm trong runtime hiện tại vì task này là rulebase-only. Khi task DB bắt đầu, thêm lại dependency DB ở branch/task riêng.

Quy trình tạo môi trường local chuẩn:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest
ruff check .
```

Lưu ý:

- Nếu máy chưa có Python 3.11 thì cần cài Python 3.11 trước.
- Không tạo `.venv` bằng Python 3.10 nếu mục tiêu là khớp Docker/runtime.
- `.venv` đã nằm trong `.gitignore`, không commit lên GitHub.

## 2. Cây Thư Mục Hiện Tại Cần Bám Theo

Dự án hiện đang có cấu trúc backend như sau:

```text
BudgetBOT/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   ├── faq/        # Có sẵn trong repo, không active trong task này
│   │   │   └── rules/
│   │   │       ├── engine.py
│   │   │       └── models.py
│   │   ├── db/             # Có sẵn trong repo, không active trong task này
│   │   ├── main.py
│   │   └── schemas.py
│   └── tests/
├── frontend/
└── docker-compose.yml
```

Khi phát triển, không tạo cấu trúc tách rời bên ngoài repo. Code backend sẽ nằm trong:

```text
backend/app/
```

Test backend sẽ nằm trong:

```text
backend/tests/
```

## 2.1. Cây Thư Mục Mục Tiêu Sau Khi Cải Thiện

Dựa trên hướng dẫn FastAPI về ứng dụng nhiều file và `APIRouter`, backend nên được tách rõ hơn theo domain thay vì dồn toàn bộ endpoint vào một file `routes.py`.

Cây thư mục mục tiêu:

```text
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── plan.py
│   │   ├── what_if.py
│   │   ├── mock_profiles.py
│   │   └── faq.py          # Không làm trong task rulebase-only
│   ├── core/
│   │   ├── faq/            # Có sẵn trong repo, không active trong task này
│   │   └── rules/
│   │       ├── __init__.py
│   │       ├── constants.py
│   │       ├── models.py
│   │       ├── calculators.py
│   │       ├── evaluators.py
│   │       ├── recommendations.py
│   │       ├── engine.py
│   │       └── exceptions.py
│   ├── dependencies.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── budget_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── mock_profile_repository.py
│   ├── mocks/
│   │   ├── __init__.py
│   │   └── sample_profiles.py
│   ├── db/                 # Có sẵn trong repo, không active trong task này
│   ├── main.py
│   └── schemas.py
└── tests/
    ├── test_rules_calculators.py
    ├── test_rules_engine.py
    ├── test_budget_service.py
    ├── test_profile_repository.py
    ├── test_api_plan.py
    └── test_api_what_if.py
```

Lưu ý:

- Nếu muốn thay đổi ít trong MVP, có thể giữ `routes.py` tạm thời.
- Nhưng hướng tốt hơn là tách `plan.py`, `what_if.py`, `mock_profiles.py` trước; `faq.py` để sau khi quay lại scope FAQ.
- `main.py` chỉ nên khởi tạo app, cấu hình middleware và include router.

## 3. Nguyên Tắc Kiến Trúc

Backend FastAPI sẽ được tổ chức theo kiểu **router - service - repository**:

```text
Router
  -> Service
  -> Repository nếu cần dữ liệu
  -> Rulebase
```

Nguyên tắc chính:

- Dùng Pydantic schema cho request/response.
- Giữ router mỏng.
- Đưa business logic vào service.
- Đưa rule tính toán vào rulebase.
- Đưa nguồn dữ liệu vào repository.
- Dùng type hints để code rõ ràng và dễ review.
- Dùng dependency injection để dễ thay mock repository bằng database repository sau này.
- Thiết kế để test riêng được rulebase, service và API.

## 3.0. Cải Thiện Theo Tài Liệu FastAPI

Dựa trên tài liệu FastAPI chính thức, dự án cần cải thiện các điểm sau:

### 3.0.1. Tách API Bằng `APIRouter`

FastAPI khuyến nghị với web API lớn hơn thì không nên để mọi endpoint trong một file. Với scope hiện tại, ưu tiên tách các endpoint rulebase theo domain:

```text
backend/app/api/plan.py
backend/app/api/what_if.py
backend/app/api/mock_profiles.py
backend/app/api/health.py
```

`backend/app/api/faq.py` chưa cần làm trong task này và không expose route FAQ trong branch rulebase-only.

Mỗi file tạo một `router = APIRouter()`.

Ví dụ:

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/plan", tags=["plan"])
```

Sau đó `main.py` include router:

```python
app.include_router(plan.router, prefix="/api")
app.include_router(what_if.router, prefix="/api")
app.include_router(mock_profiles.router, prefix="/api")
```

### 3.0.2. Dùng Dependency Injection Qua `dependencies.py`

FastAPI có hệ thống dependency injection để inject service, repository, database session hoặc shared logic.

Nên thêm:

```text
backend/app/dependencies.py
```

Ví dụ:

```python
def get_budget_service() -> BudgetService:
    repository = MockProfileRepository()
    return BudgetService(profile_repository=repository)
```

Router sẽ dùng:

```python
def create_plan(
    request: PlanRequest,
    service: BudgetService = Depends(get_budget_service),
) -> PlanResponse:
    return service.create_plan(request)
```

Lợi ích:

- Router không tự khởi tạo service.
- Test API có thể override dependency.
- Sau này đổi mock repository sang PostgreSQL repository dễ hơn.

### 3.0.3. Dùng `response_model` Cho Mọi Endpoint

FastAPI dùng response model để validate output, tạo OpenAPI schema và lọc dữ liệu trả về.

Mọi endpoint nên khai báo rõ:

```python
@router.post("/plan", response_model=PlanResponse)
def create_plan(...) -> PlanResponse:
    ...
```

Không nên trả dict tuỳ ý nếu đã có schema.

### 3.0.4. Mở Rộng Pydantic Schema

`backend/app/schemas.py` hiện còn đơn giản. Cần bổ sung schema cho nhiệm vụ API backend:

```text
PlanRequest
PlanResponse
FinancialSummaryResponse
FinancialMetricsResponse
BudgetAllocationResponse
GoalAssessmentResponse
WhatIfRequest
WhatIfResponse
MockProfileResponse
ErrorResponse nếu cần
```

Schema nên có:

- Type hints rõ ràng.
- `Field(...)` để validate min/max.
- Example data để Swagger dễ dùng.
- Response tách rõ input/output.

### 3.0.5. Test API Bằng `TestClient`

FastAPI hỗ trợ test bằng `fastapi.testclient.TestClient` kết hợp `pytest`.

Cần bổ sung test:

```text
backend/tests/test_api_plan.py
backend/tests/test_api_what_if.py
backend/tests/test_api_mock_profiles.py
```

Các test này dùng JSON request giống request từ FE/Swagger.

### 3.0.6. Cải Thiện Swagger/OpenAPI

Vì FE chưa có, Swagger sẽ là công cụ demo API chính.

Cần làm:

- Đặt `tags` rõ ràng cho endpoint.
- Thêm docstring ngắn cho endpoint.
- Thêm example trong Pydantic schema.
- Trả response model nhất quán.
- Giữ endpoint dễ thử trực tiếp ở `/docs`.

### 3.1. Maintainable Code

- Mỗi file có một trách nhiệm rõ ràng.
- Mỗi hàm chỉ nên làm một việc chính.
- Tên biến, tên hàm, tên model phải thể hiện đúng nghiệp vụ.
- Không viết logic tính toán trực tiếp trong API route.
- Không để magic numbers rải rác trong code.
- Các ngưỡng như tỷ lệ `50/30/20`, savings rate, goal feasibility nên đưa vào constants.
- Có test cho rulebase và API endpoint quan trọng.

### 3.2. Modular Code

Rulebase được chia thành các module nhỏ, dễ sửa và dễ test:

```text
backend/app/core/rules/
├── engine.py
├── models.py
├── constants.py
├── calculators.py
├── evaluators.py
├── recommendations.py
└── exceptions.py
```

Ý nghĩa:

- `models.py`: định nghĩa model nội bộ cho rulebase.
- `constants.py`: chứa các hằng số nghiệp vụ.
- `calculators.py`: chứa các phép tính tài chính.
- `evaluators.py`: đánh giá tình trạng tài chính.
- `recommendations.py`: tạo gợi ý hành động.
- `engine.py`: phối hợp các module để tạo budget plan cuối cùng.
- `exceptions.py`: định nghĩa lỗi nghiệp vụ riêng của rulebase.

### 3.3. Layered Architecture

Luồng xử lý backend sẽ đi theo các tầng:

```text
FastAPI Route Layer
  -> Schema Layer
  -> Service Layer
  -> Rulebase Core Layer
  -> Data Layer sau này
```

Trong giai đoạn hiện tại, vì chưa có DB và FE, trọng tâm là:

```text
API Route
  -> Schema
  -> Service
  -> Rulebase
  -> Mock Data nếu cần
```

### 3.4. Clean Architecture

Dependency chỉ đi từ ngoài vào trong:

```text
API phụ thuộc Service
Service phụ thuộc Rulebase
Rulebase không phụ thuộc API, DB hoặc FE
```

Rulebase không được import:

- FastAPI.
- SQLAlchemy.
- Streamlit.
- React/frontend logic.
- Database session.

Rulebase chỉ nhận input, xử lý nghiệp vụ và trả output.

## 4. Các File Sẽ Chỉnh Hoặc Thêm

### 4.1. `backend/app/api/routes.py`

Đây là nơi khai báo API endpoint.

Endpoint cần ưu tiên:

```text
GET  /health
POST /api/plan
POST /api/what-if
GET  /api/mock-profiles
```

Nếu còn thời gian, có thể thêm:

```text
POST /api/chat
```

Vai trò của `routes.py`:

- Nhận HTTP request.
- Validate qua Pydantic schema.
- Gọi service layer.
- Trả response chuẩn cho frontend sau này.

Không đặt rule tính toán phức tạp trong file này.

### 4.2. `backend/app/schemas.py`

Đây là nơi định nghĩa API contract giữa backend và frontend.

Schema cần có:

- `PlanRequest`
- `PlanResponse`
- `WhatIfRequest`
- `WhatIfResponse`
- `MockProfileResponse`
- `ApiMessageResponse` nếu làm thêm `/api/chat`

Mục tiêu là frontend sau này chỉ cần nhìn schema/Swagger là biết phải gửi gì và nhận gì.

### 4.3. `backend/app/services/budget_service.py`

Thêm service layer để tách API khỏi rulebase.

Vai trò:

- Nhận dữ liệu từ API.
- Chuyển dữ liệu sang model nội bộ nếu cần.
- Gọi rulebase.
- Trả kết quả về API.

Sau này nếu có DB, service layer sẽ là nơi thêm:

- Lưu lịch sử budget plan.
- Ghi log.
- Lấy profile từ database.
- Gọi repository.

Rulebase không cần biết DB tồn tại.

### 4.4. `backend/app/repositories/mock_profile_repository.py`

Thêm repository layer để tách service khỏi nguồn dữ liệu.

Vì hiện tại chưa có Database, repository trước mắt sẽ đọc dữ liệu từ mock profiles.

Vai trò:

- Cung cấp danh sách hồ sơ mẫu.
- Cung cấp hồ sơ mẫu theo mã case nếu cần.
- Giữ cho service không phụ thuộc trực tiếp vào file mock data.

Sau này khi có PostgreSQL, có thể thêm:

```text
backend/app/repositories/profile_repository.py
```

hoặc:

```text
backend/app/repositories/sql_profile_repository.py
```

Khi đó service chỉ đổi repository implementation, không cần đổi rulebase.

### 4.5. `backend/app/core/rules/`

Đây là phần chính cần phát triển trong nhiệm vụ rulebase.

Các module nên có:

```text
backend/app/core/rules/
├── engine.py
├── models.py
├── constants.py
├── calculators.py
├── evaluators.py
├── recommendations.py
└── exceptions.py
```

### 4.6. `backend/app/mocks/sample_profiles.py`

Vì chưa có DB và FE, cần tạo dữ liệu giả lập.

Mock profiles nên gồm:

- Hồ sơ bình thường.
- Hồ sơ tiết kiệm thấp.
- Hồ sơ chi tiêu vượt thu nhập.
- Hồ sơ có nợ cao.
- Hồ sơ thu nhập không ổn định.
- Hồ sơ có mục tiêu tài chính không khả thi.

Mock data chỉ dùng cho test/demo API, không được trộn vào rulebase.

### 4.7. `backend/tests/`

Test cần đặt trong thư mục test hiện có của backend.

Các test nên có:

```text
backend/tests/test_rules_calculators.py
backend/tests/test_rules_evaluators.py
backend/tests/test_rules_engine.py
backend/tests/test_api_plan.py
backend/tests/test_api_what_if.py
backend/tests/test_mock_profiles.py
backend/tests/test_budget_service.py
backend/tests/test_profile_repository.py
```

## 5. Luồng Xử Lý Theo Router - Service - Repository

### 5.1. Luồng `/api/plan`

```text
Client hoặc Swagger gửi request mẫu
  -> routes.py nhận request
  -> schemas.py validate input qua PlanRequest
  -> budget_service.py xử lý use case
  -> core/rules/engine.py tạo budget plan
  -> calculators/evaluators/recommendations xử lý chi tiết
  -> budget_service.py chuyển kết quả sang PlanResponse
  -> routes.py trả PlanResponse
```

Router không xử lý tính toán.

Service chịu trách nhiệm điều phối use case.

Rulebase chịu trách nhiệm tính toán nghiệp vụ.

### 5.2. Luồng `/api/mock-profiles`

```text
Client hoặc Swagger gọi API
  -> routes.py nhận request
  -> BudgetService.list_mock_profiles()
  -> MockProfileRepository.list_profiles()
  -> trả danh sách mock profiles
```

Repository chịu trách nhiệm lấy dữ liệu.

Hiện tại dữ liệu lấy từ file mock. Sau này có thể đổi sang DB mà không ảnh hưởng route/rulebase.

### 5.3. Luồng `/api/what-if`

```text
Client gửi profile hiện tại và thay đổi giả định
  -> routes.py nhận request
  -> WhatIfRequest validate bằng Pydantic
  -> BudgetService.run_what_if()
  -> Service tạo profile mới sau thay đổi
  -> Rulebase tính plan cũ và plan mới
  -> Service tạo phần so sánh trước/sau
  -> routes.py trả WhatIfResponse
```

## 6. Dependency Injection

FastAPI sẽ dùng dependency injection để inject service vào router.

Ví dụ ý tưởng:

```python
def get_budget_service() -> BudgetService:
    repository = MockProfileRepository()
    return BudgetService(profile_repository=repository)
```

Router dùng service qua `Depends`:

```python
@router.post("/plan", response_model=PlanResponse)
def create_plan(
    request: PlanRequest,
    service: BudgetService = Depends(get_budget_service),
) -> PlanResponse:
    return service.create_plan(request)
```

Lợi ích:

- Router không tự khởi tạo logic phức tạp.
- Khi test API có thể override dependency.
- Khi có DB thật, chỉ thay repository implementation.
- Service có thể test riêng bằng fake repository.
- Rulebase vẫn độc lập, không phụ thuộc FastAPI.

## 7. Input API Giả Định Cho Rulebase

API `/api/plan` sẽ nhận dữ liệu dạng:

```json
{
  "monthly_income": 20000000,
  "fixed_expenses": 7000000,
  "variable_expenses": 5000000,
  "debt_payment": 1000000,
  "debt_outstanding": 20000000,
  "current_savings": 30000000,
  "financial_goal": "mua laptop",
  "goal_amount": 25000000,
  "goal_deadline_months": 10,
  "income_stability": "stable"
}
```

Ý nghĩa:

- `monthly_income`: thu nhập hàng tháng.
- `fixed_expenses`: chi phí cố định.
- `variable_expenses`: chi phí linh hoạt.
- `debt_payment`: tiền trả nợ mỗi tháng.
- `debt_outstanding`: tổng nợ còn lại.
- `current_savings`: tiền tiết kiệm hiện có.
- `financial_goal`: tên mục tiêu tài chính.
- `goal_amount`: số tiền cần đạt cho mục tiêu.
- `goal_deadline_months`: deadline theo tháng.
- `income_stability`: `stable`, `unstable`, hoặc `seasonal`.

## 8. Output API Cần Trả Về Cho Frontend Sau Này

API `/api/plan` nên trả response có cấu trúc:

```json
{
  "type": "budget_plan",
  "summary": {
    "monthly_income": 20000000,
    "total_expenses": 13000000,
    "monthly_surplus": 7000000
  },
  "metrics": {
    "savings_rate": 0.35,
    "expense_ratio": 0.65,
    "debt_payment_ratio": 0.05
  },
  "allocation": {
    "needs": 10000000,
    "wants": 6000000,
    "savings": 4000000
  },
  "goal_assessment": {
    "status": "feasible",
    "required_monthly_saving": 2500000,
    "message": "Mục tiêu có khả thi với dòng tiền hiện tại."
  },
  "warnings": [],
  "action_items": [
    "Duy trì mức tiết kiệm hiện tại.",
    "Theo dõi chi phí linh hoạt hằng tháng.",
    "Ưu tiên giữ quỹ khẩn cấp tối thiểu 3 tháng chi phí thiết yếu."
  ]
}
```

Response này giúp frontend dễ render:

- Metric cards.
- Allocation chart.
- Goal progress.
- Warning box.
- Action items.

## 9. API Cần Làm Trong Nhiệm Vụ Này

### 9.1. `GET /health`

Mục đích:

- Kiểm tra backend đang chạy.

Response:

```json
{
  "status": "ok"
}
```

### 9.2. `POST /api/plan`

Mục đích:

- Nhận thông tin tài chính.
- Gọi rulebase.
- Trả budget plan có cấu trúc rõ ràng.

Đây là endpoint quan trọng nhất trong nhiệm vụ hiện tại.

### 9.3. `POST /api/what-if`

Mục đích:

- Nhận profile hiện tại.
- Nhận một thay đổi giả định, ví dụ giảm chi linh hoạt 1 triệu.
- Tính lại plan.
- Trả so sánh trước/sau.

Các trường hợp MVP:

- Tăng/giảm thu nhập.
- Tăng/giảm chi phí cố định.
- Tăng/giảm chi phí linh hoạt.
- Tăng/giảm tiền trả nợ hàng tháng.

### 9.4. `GET /api/mock-profiles`

Mục đích:

- Trả danh sách hồ sơ mẫu để test/demo API.
- Giúp người làm FE sau này có dữ liệu mẫu để gọi thử.
- Giúp backend test được khi chưa có Database.

### 9.5. `POST /api/chat` Chưa Làm Trong Task Này

Mục đích:

- Nhận message từ chatbox.
- Tạm thời route đơn giản sang rulebase hoặc fallback.
- Sau này có thể mở rộng để phân loại FAQ, rulebase, what-if.

Trong scope hiện tại, chưa cần làm `/api/chat` vì nhiệm vụ đang là rulebase API trước.

## 10. Cách Giả Lập Khi Chưa Có DB Và FE

### 10.1. Giả Lập Database

Tạm thời dùng:

```text
backend/app/mocks/sample_profiles.py
```

Không viết code phụ thuộc PostgreSQL trong rulebase.

Sau này khi có DB, chỉ thay nguồn dữ liệu:

```text
Mock profiles hiện tại
  -> Repository đọc từ PostgreSQL sau này
```

API contract không đổi.

### 10.2. Giả Lập Frontend

Vì chưa có FE, kiểm thử API bằng:

- Swagger UI: `http://localhost:8000/docs`
- Postman.
- `pytest` với FastAPI `TestClient`.

Test API cần xác minh:

- Status code đúng.
- Response có đủ field.
- Kiểu dữ liệu đúng.
- Case lỗi trả message rõ ràng.

## 11. Có Thể Test Riêng Rulebase/Service Không?

Có. Đây là mục tiêu chính của kiến trúc router - service - repository.

Backend cần test theo từng tầng:

```text
Rulebase test
  -> Service test
  -> Repository test
  -> API test
```

### 11.1. Test Riêng Rulebase

Rulebase phải test được mà không cần:

- FastAPI.
- TestClient.
- Database.
- Repository.
- Frontend.

Ví dụ các hàm trong `calculators.py` có thể test trực tiếp:

```python
def test_calculate_savings_rate():
    assert calculate_savings_rate(20_000_000, 4_000_000) == 0.2
```

Test engine có thể truyền model nội bộ:

```python
def test_engine_create_plan_feasible_goal():
    profile = BudgetProfile(
        monthly_income=20_000_000,
        fixed_expenses=7_000_000,
        variable_expenses=5_000_000,
        debt_payment=1_000_000,
        debt_outstanding=20_000_000,
        current_savings=30_000_000,
        financial_goal="mua laptop",
        goal_amount=25_000_000,
        goal_deadline_months=10,
        income_stability="stable",
    )

    plan = create_budget_plan(profile)

    assert plan.goal_assessment.status == "feasible"
    assert plan.summary.monthly_surplus > 0
```

### 11.2. Test Riêng Service

Service test bằng fake repository hoặc mock repository.

Ví dụ:

```python
class FakeProfileRepository:
    def list_profiles(self):
        return [
            {
                "id": "normal",
                "name": "Hồ sơ bình thường",
                "profile": {
                    "monthly_income": 20_000_000,
                    "fixed_expenses": 7_000_000,
                    "variable_expenses": 5_000_000,
                    "debt_payment": 1_000_000,
                    "debt_outstanding": 20_000_000,
                    "current_savings": 30_000_000,
                    "financial_goal": "mua laptop",
                    "goal_amount": 25_000_000,
                    "goal_deadline_months": 10,
                    "income_stability": "stable",
                },
            }
        ]
```

Sau đó test service:

```python
def test_budget_service_create_plan():
    service = BudgetService(profile_repository=FakeProfileRepository())
    response = service.create_plan(valid_request)

    assert response.type == "budget_plan"
    assert response.summary.monthly_surplus > 0
```

Service test cần kiểm tra:

- Service gọi rulebase đúng.
- Service format response đúng.
- What-if xử lý đúng.
- Mock profiles trả đúng.
- Không cần FastAPI hoặc DB để test service.

### 11.3. Test Riêng Repository

Repository hiện tại là mock repository.

Test cần kiểm tra:

- `list_profiles()` trả danh sách hồ sơ mẫu.
- Mỗi hồ sơ có đủ field bắt buộc.
- Không có profile invalid trong mock data.

Sau này khi có PostgreSQL repository, có thể test repository riêng với test database.

### 11.4. Test API/Router

Router test bằng FastAPI `TestClient`.

Ví dụ:

```python
def test_create_plan_api(client):
    response = client.post("/api/plan", json={
        "monthly_income": 20_000_000,
        "fixed_expenses": 7_000_000,
        "variable_expenses": 5_000_000,
        "debt_payment": 1_000_000,
        "debt_outstanding": 20_000_000,
        "current_savings": 30_000_000,
        "financial_goal": "mua laptop",
        "goal_amount": 25_000_000,
        "goal_deadline_months": 10,
        "income_stability": "stable"
    })

    assert response.status_code == 200
    assert response.json()["type"] == "budget_plan"
```

API test cần kiểm tra:

- Endpoint tồn tại.
- Status code đúng.
- Request invalid trả lỗi đúng.
- Response đúng schema.
- Có thể override dependency nếu cần mock service.

## 12. Các Trường Hợp Test Cần Có

### 12.1. Test Rulebase

- Thu nhập hợp lệ tạo được plan.
- Thu nhập bằng 0 trả lỗi validation.
- Chi phí âm trả lỗi validation.
- Chi tiêu vượt thu nhập tạo warning.
- Savings rate thấp tạo warning.
- Có nợ cao tạo warning.
- Mục tiêu khả thi trả status `feasible`.
- Mục tiêu căng trả status `tight`.
- Mục tiêu không khả thi trả status `not_feasible`.

### 12.2. Test Service

- `BudgetService.create_plan()` trả `PlanResponse` đúng.
- `BudgetService.run_what_if()` trả so sánh trước/sau đúng.
- `BudgetService.list_mock_profiles()` lấy dữ liệu qua repository.
- Service test được bằng fake repository.

### 12.3. Test Repository

- Mock repository trả danh sách profile mẫu.
- Profile mẫu có đủ field.
- Profile mẫu có thể dùng để gọi `/api/plan`.

### 12.4. Test API

- `GET /health` trả `status = ok`.
- `POST /api/plan` với input hợp lệ trả `type = budget_plan`.
- `POST /api/plan` với input thiếu/invalid trả lỗi 422 hoặc lỗi nghiệp vụ rõ ràng.
- `POST /api/what-if` trả được so sánh trước/sau.
- `GET /api/mock-profiles` trả danh sách hồ sơ mẫu.

## 13. Nguyên Tắc Thiết Kế Hàm Và Class

Khi bắt đầu code backend, các hàm và class cần tuân theo các nguyên tắc sau để code dễ đọc, dễ test, dễ maintain và dễ mở rộng.

### 13.1. Single Responsibility Principle

Một hàm hoặc class chỉ nên làm một nhiệm vụ chính.

Áp dụng trong BudgetBOT:

- `routes.py` hoặc từng router như `plan.py` chỉ nhận request, gọi service và trả response.
- `budget_service.py` xử lý use case như tạo plan, chạy what-if, lấy mock profiles.
- `engine.py` điều phối rulebase để tạo budget plan.
- `calculators.py` chỉ chứa phép tính tài chính.
- `evaluators.py` chỉ đánh giá tình trạng tài chính.
- `recommendations.py` chỉ tạo gợi ý hành động.

Ví dụ tốt:

```python
def calculate_monthly_surplus(monthly_income: float, total_expenses: float) -> float:
    return monthly_income - total_expenses
```

Hàm trên chỉ tính dòng tiền dư. Nó không tạo warning, không tạo response API và không đọc dữ liệu từ repository.

### 13.2. DRY - Don’t Repeat Yourself

Không lặp code.

Các logic dùng nhiều nơi cần tách thành hàm hoặc constant dùng chung.

Ví dụ:

```python
def calculate_total_expenses(
    fixed_expenses: float,
    variable_expenses: float,
    debt_payment: float,
) -> float:
    return fixed_expenses + variable_expenses + debt_payment
```

`/api/plan` và `/api/what-if` đều nên dùng lại rulebase thay vì tự tính tổng chi ở nhiều nơi.

Các tỷ lệ như `50/30/20` không viết rải rác:

```python
NEEDS_RATIO = 0.50
WANTS_RATIO = 0.30
SAVINGS_RATIO = 0.20
```

### 13.3. KISS - Keep It Simple

Giữ code đơn giản, dễ hiểu.

Vì hiện tại chưa có FE và DB thật, backend chỉ cần các tầng cần thiết:

```text
router
service
repository mock
rulebase
schema
```

Không thêm kiến trúc phức tạp như event bus, abstract factory, domain event hoặc unit of work nếu chưa có nhu cầu thật.

Rulebase nên ưu tiên hàm thuần, input rõ ràng và output rõ ràng.

### 13.4. YAGNI - You Aren’t Gonna Need It

Chưa cần thì chưa code.

Trong giai đoạn hiện tại chưa làm:

- Authentication.
- User account.
- Phân quyền.
- Lưu session dài hạn.
- PostgreSQL thật cho profile.
- Admin dashboard.
- Background job.
- LLM.

Chỉ chừa cấu trúc để mở rộng sau, không viết sẵn code phức tạp cho phần chưa được chốt.

Ví dụ:

- Hiện tại dùng `MockProfileRepository`.
- Sau này có DB thì thêm `SqlProfileRepository`.
- Không viết database logic khi schema DB chưa chốt.

### 13.5. Separation of Concerns

Tách trách nhiệm rõ ràng giữa các tầng.

Áp dụng:

```text
schemas.py
  -> định nghĩa request/response

api/
  -> HTTP endpoint

services/
  -> use case logic

repositories/
  -> nguồn dữ liệu

core/rules/
  -> nghiệp vụ tính toán ngân sách

mocks/
  -> dữ liệu giả lập

tests/
  -> kiểm thử
```

Không để mock data trong rulebase.

Không để router chứa công thức tài chính chi tiết.

Không để service phụ thuộc trực tiếp vào file dữ liệu nếu có repository.

### 13.6. High Cohesion

Code trong cùng một module phải liên quan chặt chẽ với nhau.

Ví dụ `calculators.py` chỉ nên chứa các hàm tính toán:

```text
calculate_total_expenses
calculate_monthly_surplus
calculate_savings_rate
calculate_debt_payment_ratio
calculate_50_30_20_allocation
```

`evaluators.py` chỉ nên chứa các hàm đánh giá:

```text
evaluate_cashflow
evaluate_savings_rate
evaluate_goal_feasibility
evaluate_debt_pressure
```

`recommendations.py` chỉ nên chứa logic tạo action items.

### 13.7. Low Coupling

Các phần của hệ thống nên ít phụ thuộc lẫn nhau.

Rulebase không được import:

- FastAPI.
- SQLAlchemy.
- TestClient.
- Request.
- Response.

Luồng phụ thuộc nên là:

```text
api -> service -> repository
api -> service -> rulebase
```

Không để phụ thuộc ngược:

```text
rulebase -> api
rulebase -> db
service -> FastAPI Request
```

Lợi ích:

- Test rulebase không cần chạy API.
- Test service không cần DB thật.
- Đổi mock repository sang SQL repository không ảnh hưởng rulebase.
- FE thay đổi không ảnh hưởng core logic.

### 13.8. Cách Áp Dụng Vào Luồng `/api/plan`

```text
POST /api/plan
  -> plan.py hoặc routes.py nhận request
  -> PlanRequest validate input
  -> BudgetService.create_plan()
  -> engine.create_budget_plan()
  -> calculators/evaluators/recommendations xử lý
  -> BudgetService tạo PlanResponse
  -> router trả response
```

Kết luận: mỗi tầng làm đúng việc của nó, tránh lặp code, tránh code thừa, giữ rulebase độc lập và dễ test.

## 14. Cách Áp Dụng OOP Và Class Trong Dự Án

Backend BudgetBOT sẽ dùng OOP ở mức vừa đủ. Không OOP hóa toàn bộ dự án một cách máy móc.

Nguyên tắc:

- Dùng class cho service, repository và dependency có thể thay thế.
- Dùng function thuần cho rulebase/calculator nếu logic chỉ là tính toán.
- Ưu tiên composition và dependency injection hơn inheritance phức tạp.
- Giữ class nhỏ, rõ trách nhiệm và dễ test.

### 14.1. Class

Class là khuôn mẫu tạo object.

Trong BudgetBOT, class nên dùng cho:

```text
BudgetService
MockProfileRepository
SqlProfileRepository sau này
```

Ví dụ:

```python
class BudgetService:
    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository

    def create_plan(self, request: PlanRequest) -> PlanResponse:
        ...
```

`BudgetService` là class xử lý use case liên quan đến budget.

### 14.2. Object

Object là đối tượng được tạo từ class.

Ví dụ:

```python
repository = MockProfileRepository()
service = BudgetService(profile_repository=repository)
```

Trong đó:

- `repository` là object của `MockProfileRepository`.
- `service` là object của `BudgetService`.

Các object này sẽ được tạo qua dependency injection trong FastAPI.

### 14.3. Encapsulation

Encapsulation là đóng gói dữ liệu và hành vi liên quan lại với nhau.

Ví dụ `MockProfileRepository` tự quản lý cách lấy mock profiles:

```python
class MockProfileRepository:
    def list_profiles(self) -> list[MockProfileResponse]:
        return SAMPLE_PROFILES
```

Service không cần biết dữ liệu mẫu nằm ở file nào. Service chỉ gọi:

```python
self.profile_repository.list_profiles()
```

Nhờ vậy chi tiết nguồn dữ liệu được đóng gói trong repository.

### 14.4. Inheritance

Inheritance là kế thừa.

Trong dự án này, inheritance sẽ dùng hạn chế. Không tạo cây kế thừa phức tạp nếu chưa cần.

Nếu cần thống nhất interface repository, có thể dùng base class:

```python
class BaseProfileRepository:
    def list_profiles(self) -> list[MockProfileResponse]:
        raise NotImplementedError
```

Sau đó class con implement:

```python
class MockProfileRepository(BaseProfileRepository):
    def list_profiles(self) -> list[MockProfileResponse]:
        return SAMPLE_PROFILES
```

Tuy nhiên, với Python hiện đại, nên ưu tiên `Protocol` nếu chỉ cần định nghĩa interface nhẹ.

### 14.5. Polymorphism

Polymorphism là đa hình: nhiều class khác nhau cùng tuân theo một interface, nên service có thể dùng thay thế cho nhau.

Ví dụ:

```text
MockProfileRepository
SqlProfileRepository
```

Cả hai đều có:

```python
def list_profiles(self) -> list[MockProfileResponse]:
    ...
```

`BudgetService` không cần biết repository là mock hay database:

```python
class BudgetService:
    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository
```

Khi chưa có DB:

```python
BudgetService(MockProfileRepository())
```

Sau này có DB:

```python
BudgetService(SqlProfileRepository(db_session))
```

Service không cần đổi logic.

### 14.6. Abstraction

Abstraction là trừu tượng hóa: code cấp cao làm việc với interface, không phụ thuộc chi tiết implementation.

Nên có repository interface:

```python
class ProfileRepository(Protocol):
    def list_profiles(self) -> list[MockProfileResponse]:
        ...
```

Service chỉ phụ thuộc vào `ProfileRepository`, không phụ thuộc trực tiếp vào `MockProfileRepository`.

Lợi ích:

- Dễ thay mock bằng database.
- Dễ test bằng fake repository.
- Giảm coupling giữa service và nguồn dữ liệu.

### 14.7. Overriding

Overriding là class con ghi đè hàm của class cha.

Nếu dùng base class, `MockProfileRepository` có thể override `list_profiles()`:

```python
class MockProfileRepository(BaseProfileRepository):
    def list_profiles(self) -> list[MockProfileResponse]:
        return SAMPLE_PROFILES
```

Tuy nhiên, không nên lạm dụng overriding nếu chỉ cần interface đơn giản. Với dự án hiện tại, `Protocol` hoặc composition thường phù hợp hơn.

### 14.8. Composition

Composition là class này chứa class khác để dùng.

Trong BudgetBOT, `BudgetService` chứa repository:

```python
class BudgetService:
    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository
```

Đây là quan hệ:

```text
BudgetService có một ProfileRepository
```

Nên ưu tiên composition hơn inheritance vì:

- Dễ thay dependency.
- Dễ test.
- Không tạo cây kế thừa sâu.
- Phù hợp kiến trúc router - service - repository.

### 14.9. Dependency Injection

Dependency Injection là truyền dependency từ ngoài vào class hoặc hàm.

FastAPI sẽ inject service vào router:

```python
def get_budget_service() -> BudgetService:
    repository = MockProfileRepository()
    return BudgetService(profile_repository=repository)
```

Router dùng:

```python
@router.post("/plan", response_model=PlanResponse)
def create_plan(
    request: PlanRequest,
    service: BudgetService = Depends(get_budget_service),
) -> PlanResponse:
    return service.create_plan(request)
```

Lợi ích:

- Router không tự tạo service.
- Service không tự tạo repository cứng.
- Test dễ thay bằng fake service hoặc fake repository.
- Sau này đổi mock repository sang database repository ít sửa code.

### 14.10. Khi Nào Không Dùng Class

Không phải logic nào cũng cần class.

Rulebase tính toán nên ưu tiên function thuần:

```python
def calculate_savings_rate(monthly_income: float, monthly_savings: float) -> float:
    if monthly_income <= 0:
        raise ValueError("monthly_income must be positive")
    return monthly_savings / monthly_income
```

Các module nên dùng function thuần:

```text
core/rules/calculators.py
core/rules/evaluators.py
core/rules/recommendations.py
```

Lý do:

- Dễ test.
- Ít dependency.
- Dễ đọc.
- Không tạo object không cần thiết.

### 14.11. Kết Luận OOP Cho BudgetBOT

OOP sẽ được dùng cho:

- `BudgetService`
- `MockProfileRepository`
- `SqlProfileRepository` sau này
- Repository interface hoặc `Protocol`

Function thuần sẽ được dùng cho:

- Calculator.
- Evaluator.
- Recommendation rule.
- Rule helper.

Cách này tận dụng được encapsulation, abstraction, polymorphism, composition và dependency injection, nhưng vẫn giữ rulebase đơn giản và dễ test.

## 15. Chuẩn Viết Code Python Và Clean Code

Khi triển khai backend, code cần tuân theo chuẩn Python và nguyên tắc clean code để dễ đọc, dễ test, dễ maintain và dễ mở rộng.

### 15.1. PEP 8

Toàn bộ backend Python sẽ theo PEP 8:

- Import gọn, không import thừa.
- Khoảng trắng nhất quán.
- Tên biến, tên hàm, tên class đúng convention.
- Không để file hoặc hàm quá dài.
- Dùng linter/formatter để giữ style ổn định.

Repo hiện có `ruff.toml`, nên ưu tiên dùng Ruff:

```bash
ruff check .
ruff format .
```

### 15.2. Naming Convention

Tên biến, hàm, class, file phải thể hiện đúng nghiệp vụ.

Nên dùng tên rõ nghĩa:

```python
calculate_total_expenses()
evaluate_goal_feasibility()
create_budget_plan()
run_what_if_analysis()
```

Tránh tên mơ hồ nếu không có ngữ cảnh rõ:

```text
data
result
temp
handler
process()
```

Tên file nên rõ trách nhiệm:

```text
calculators.py
evaluators.py
recommendations.py
budget_service.py
mock_profile_repository.py
```

### 15.3. snake_case

Biến và hàm dùng `snake_case`:

```python
monthly_income = 20_000_000

def calculate_savings_rate(monthly_income: float, monthly_savings: float) -> float:
    ...
```

Field API cũng nên dùng `snake_case` để nhất quán với Python backend:

```json
{
  "monthly_income": 20000000,
  "fixed_expenses": 7000000
}
```

### 15.4. PascalCase

Class dùng `PascalCase`:

```python
class BudgetService:
    ...

class MockProfileRepository:
    ...

class PlanRequest(BaseModel):
    ...
```

Pydantic schema cũng là class nên dùng `PascalCase`.

### 15.5. UPPER_CASE

Constant dùng `UPPER_CASE`:

```python
NEEDS_RATIO = 0.50
WANTS_RATIO = 0.30
SAVINGS_RATIO = 0.20
TARGET_SAVINGS_RATE = 0.20
```

Không viết các con số nghiệp vụ rải rác trong nhiều file.

### 15.6. Type Hint

Mọi hàm public trong service, repository và rulebase nên có type hints:

```python
def create_plan(self, request: PlanRequest) -> PlanResponse:
    ...

def calculate_total_expenses(
    fixed_expenses: float,
    variable_expenses: float,
    debt_payment: float,
) -> float:
    ...
```

Lợi ích:

- Đọc code nhanh hơn.
- IDE hỗ trợ tốt hơn.
- Test dễ viết hơn.
- Sau này có thể thêm static analysis bằng `mypy`.

### 15.7. Docstring

Docstring dùng cho:

- Module quan trọng.
- Class public.
- Hàm public.
- Hàm có logic nghiệp vụ không hiển nhiên.

Ví dụ:

```python
def evaluate_goal_feasibility(
    monthly_surplus: float,
    required_monthly_saving: float,
) -> GoalAssessment:
    """Đánh giá mục tiêu tài chính là khả thi, căng hay không khả thi."""
```

Không cần viết docstring dài cho hàm quá rõ nếu tên hàm đã đủ nghĩa.

### 15.8. Clean Code

Code sạch cần:

- Hàm ngắn.
- Tên rõ nghĩa.
- Ít nesting.
- Ít side effect.
- Không lặp code.
- Module có trách nhiệm rõ.
- Dễ test.

Áp dụng trong BudgetBOT:

```text
router -> service -> repository/rulebase
```

Không viết toàn bộ logic trong router.

### 15.9. Readable Code

Ưu tiên code dễ đọc khi review.

Ví dụ nên tách điều kiện phức tạp thành biến có tên rõ:

```python
required_saving_exceeds_surplus = required_monthly_saving > monthly_surplus
```

Cách này giúp người đọc hiểu điều kiện nghiệp vụ mà không phải tự suy luận lại.

### 15.10. Maintainable Code

Code dễ bảo trì bằng cách:

- Tách module theo trách nhiệm.
- Giữ API contract ổn định.
- Viết test cho rulebase, service và API.
- Tránh phụ thuộc chéo.
- Để constants ở một nơi.

Ví dụ sau này sửa ngưỡng savings rate thì chỉ sửa trong:

```text
backend/app/core/rules/constants.py
```

### 15.11. Extensible Code

Code dễ mở rộng bằng cách:

- Service nhận repository qua dependency injection.
- Rulebase độc lập với API/DB.
- Response schema rõ ràng.
- Mock repository có thể thay bằng SQL repository.

Hiện tại:

```python
BudgetService(MockProfileRepository())
```

Sau này:

```python
BudgetService(SqlProfileRepository(db_session))
```

Service và router không phải đổi nhiều.

### 15.12. Reusable Code

Các hàm tính toán trong rulebase phải tái sử dụng được ở nhiều API:

```text
/api/plan
/api/what-if
/api/chat sau này
```

Ví dụ:

```python
calculate_total_expenses()
calculate_savings_rate()
evaluate_goal_feasibility()
```

Không copy logic tính toán sang từng endpoint.

### 15.13. Refactor

Refactor là sửa cấu trúc code cho sạch hơn nhưng không đổi chức năng.

Nên refactor khi thấy:

- Router quá dài.
- Một hàm làm nhiều việc.
- Logic bị lặp.
- Tên hàm không rõ.
- Test khó viết.
- Rulebase phụ thuộc API/DB.

Refactor phải đi kèm test để đảm bảo hành vi không đổi.

### 15.14. Code Smell

Các dấu hiệu code đang xấu cần tránh:

```text
routes.py quá dài
hàm hơn 50-70 dòng
if/else lồng quá sâu
copy-paste công thức
tên biến chung chung: data, result, temp
magic number: 0.2, 0.5 rải rác
rulebase import FastAPI hoặc SQLAlchemy
service tự đọc file mock trực tiếp
test phụ thuộc thứ tự chạy
```

Gặp các dấu hiệu này thì cần tách hàm, tách module hoặc đưa logic về đúng tầng.

### 15.15. Technical Debt

Vì đang làm MVP, có thể có phần làm tạm, nhưng phải quản lý rõ.

Chấp nhận tạm:

```text
MockProfileRepository thay cho DB thật
/api/mock-profiles để demo
```

Không chấp nhận:

```text
hard-code công thức trong router
response API thay đổi tùy tiện
không có test cho rulebase chính
```

Nếu có nợ kỹ thuật, cần ghi rõ trong comment ngắn hoặc issue/todo để xử lý sau.

## 16. Thứ Tự Thực Hiện

1. Kiểm tra lại branch đang làm là `feature/BP-2-backend-api`.
2. Bám theo cấu trúc hiện tại trong `backend/app`.
3. Cập nhật `schemas.py` cho `PlanRequest`, `PlanResponse`, `WhatIfRequest`, `WhatIfResponse`.
4. Mở rộng `backend/app/core/rules`.
5. Thêm `backend/app/services/budget_service.py`.
6. Thêm `backend/app/repositories/mock_profile_repository.py`.
7. Thêm mock profiles trong `backend/app/mocks/sample_profiles.py`.
8. Cập nhật dependency injection cho service.
9. Cập nhật `backend/app/api/routes.py`.
10. Viết test cho rulebase.
11. Viết test cho service.
12. Viết test cho repository.
13. Viết test cho API.
14. Chạy `pytest`.
15. Kiểm tra Swagger UI.
16. Cập nhật README nếu cần.

## 17. Phạm Vi Chưa Làm Lúc Này

- Chưa làm Frontend.
- Chưa tích hợp PostgreSQL thật.
- Chưa làm authentication.
- Chưa lưu user/session dài hạn.
- Chưa dùng LLM.
- Chưa làm dashboard.
- Chưa làm tư vấn đầu tư, cổ phiếu, crypto, bảo hiểm.

## 18. Kết Luận

Backend sẽ được phát triển theo hướng **router - service - repository**, dùng Pydantic schema cho request/response, giữ router mỏng, đưa business logic vào service, đưa rule tính toán vào rulebase, và dùng mock repository để giả lập Database trong giai đoạn hiện tại.

Cách tổ chức này giúp test riêng được rulebase, service, repository và API. Khi FE và DB sẵn sàng, đội khác có thể tích hợp dựa trên API contract đã ổn định mà không cần viết lại lõi xử lý.
