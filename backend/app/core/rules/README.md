# Module `backend/app/core/rules`

## Giải thích tổng quan

Module này là rulebase tính toán ngân sách. Rulebase nghĩa là backend dùng công thức và điều kiện cố định để tạo kết quả, không dùng AI.

Ví dụ đời thường: đây là máy tính công thức. Service đưa dữ liệu tài chính vào, rulebase trả ra kế hoạch ngân sách, cảnh báo và hành động đề xuất.

## Mục đích

- Validate dữ liệu đầu vào nội bộ.
- Tính tổng chi phí.
- Tính dòng tiền dư hoặc âm.
- Tính phân bổ 50/30/20.
- Tính các tỷ lệ tài chính.
- Đánh giá mục tiêu tài chính.
- Tạo cảnh báo.
- Tạo action items.

## Cấu trúc thư mục liên quan

```text
backend/app/core/rules/
  __init__.py
  constants.py
  models.py
  exceptions.py
  calculators.py
  evaluators.py
  recommendations.py
  engine.py
```

## Danh sách file

### `constants.py`

Chứa hằng số:

- `NEEDS_RATIO = 0.50`
- `WANTS_RATIO = 0.30`
- `SAVINGS_RATIO = 0.20`
- `LOW_SAVINGS_RATE = 0.10`
- `TARGET_SAVINGS_RATE = 0.20`
- `HIGH_DEBT_PAYMENT_RATIO = 0.20`
- `HIGH_FIXED_EXPENSE_RATIO = 0.50`
- `TIGHT_GOAL_SURPLUS_USAGE = 0.80`

### `models.py`

Dataclass:

- `UserProfile`
- `BudgetProfile`
- `FinancialSummary`
- `FinancialMetrics`
- `BudgetAllocation`
- `GoalAssessment`
- `BudgetPlan`

### `exceptions.py`

Class:

- `RuleValidationError`

### `calculators.py`

Function:

- `calculate_total_expenses()`
- `calculate_monthly_surplus()`
- `calculate_ratio()`
- `calculate_required_monthly_saving()`
- `calculate_50_30_20_allocation()`
- `calculate_emergency_fund_target()`

### `evaluators.py`

Function:

- `evaluate_goal_feasibility()`
- `evaluate_warnings()`

### `recommendations.py`

Function:

- `generate_action_items()`

### `engine.py`

Function:

- `savings_rate()`
- `allocation_50_30_20()`
- `emergency_fund_target()`
- `goal_timeline()`
- `evaluate_allocation()`
- `validate_budget_profile()`
- `create_budget_plan()`

Trong flow `/api/plan`, function trung tâm là `create_budget_plan()`.

## Ai gọi module

Đường dẫn file: `backend/app/services/budget_service.py`

Class: `BudgetService`

Method `create_plan()` gọi:

- `create_budget_plan()`.

Method `_response_from_plan()` gọi:

- `evaluate_allocation()`.

Tests cũng gọi trực tiếp các function rulebase:

- `backend/tests/test_rules.py`
- `backend/tests/test_rules_calculators.py`
- `backend/tests/test_rules_engine.py`

## Module gọi ai

`engine.py` gọi các module nội bộ:

```text
create_budget_plan()
-> validate_budget_profile()
-> calculate_total_expenses()
-> calculate_monthly_surplus()
-> calculate_50_30_20_allocation()
-> calculate_required_monthly_saving()
-> evaluate_goal_feasibility()
-> calculate_ratio()
-> evaluate_warnings()
-> generate_action_items()
```

Rulebase không gọi:

- FastAPI.
- SQLAlchemy.
- Frontend.
- Database session.

## Input và output

### `create_budget_plan()`

Input:

- `BudgetProfile`

Output:

- `BudgetPlan`

### `evaluate_allocation()`

Input:

- `UserProfile`

Output:

- `dict` gồm trạng thái `needs`, `wants`, `savings`.

## Luồng chạy

```text
BudgetProfile
-> validate_budget_profile()
-> total_expenses
-> monthly_surplus
-> allocation 50/30/20
-> required_monthly_saving
-> goal_assessment
-> metrics
-> warnings
-> action_items
-> BudgetPlan
```

## Ví dụ thực tế

Đường dẫn file: `backend/tests/test_rules_engine.py`

Function test: `test_create_budget_plan_feasible_goal()`

Input:

```text
monthly_income = 20000000
fixed_expenses = 7000000
variable_expenses = 5000000
debt_payment = 1000000
goal_amount = 25000000
goal_deadline_months = 10
```

Tính toán:

```text
total_expenses = 7000000 + 5000000 + 1000000 = 13000000
monthly_surplus = 20000000 - 13000000 = 7000000
required_monthly_saving = 25000000 / 10 = 2500000
```

Kết quả test mong đợi:

```text
plan.type == "budget_plan"
plan.summary.monthly_surplus == 7000000
plan.goal_assessment.status == "feasible"
```

## Test liên quan

- `backend/tests/test_rules.py`
- `backend/tests/test_rules_calculators.py`
- `backend/tests/test_rules_engine.py`
- `backend/tests/test_budget_service.py`

## Python cần hiểu

- Function thuần: nhận input, trả output, không phụ thuộc API/DB.
- Dataclass: dùng làm object dữ liệu nội bộ.
- Constant: hằng số nghiệp vụ viết hoa trong `constants.py`.
- Exception: `RuleValidationError` dùng khi input nội bộ không hợp lệ.
- `round()`: làm tròn tỷ lệ/số tiền ở một số function.

## Đã có, chưa có, ngoài scope

Đã có trong code:

- Rule 50/30/20.
- Savings rate.
- Expense ratio.
- Debt payment ratio.
- Goal feasibility.
- Warnings.
- Action items.
- What-if dùng lại rulebase thông qua service.

Chưa có trong code:

- Rule theo từng quốc gia/vùng.
- Rule cá nhân hóa theo user history trong DB.
- Machine learning hoặc LLM.

Ngoài scope hiện tại:

- Tư vấn đầu tư.
- Gợi ý sản phẩm tài chính.
- Phân tích giao dịch ngân hàng thật.

## Lỗi người mới thường gặp

- Đưa FastAPI vào rulebase. Rulebase hiện phải độc lập.
- Đưa SQLAlchemy vào rulebase. DB không thuộc module này.
- Sửa `constants.py` nhưng quên cập nhật test kỳ vọng.
- Nhầm `current_savings` với `monthly_surplus`. Rulebase hiện tính savings rate từ `monthly_surplus`, không từ `current_savings`.
