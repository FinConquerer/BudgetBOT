# 💰 BudgetBOT

Chatbot tư vấn & lập kế hoạch ngân sách cá nhân — đồ án **AIO Conquer 2026 (Module 1)**, team **FinConquerer**.

> ⚠️ Chỉ mang tính tham khảo, KHÔNG phải lời khuyên tài chính/đầu tư.

## Chức năng
- **FAQ**: hỏi đáp kiến thức tài chính cá nhân (V1: tra DB từ khoá → V2: RAG/LLM).
- **Rule Engine**: thu thập thông tin → tính chỉ số (50/30/20, savings rate, quỹ khẩn cấp, tính khả thi mục tiêu) → đề xuất phân bổ. *Deterministic, có test.*

## Cấu trúc
```
budgetbot/
  rules/    # Rule Engine (engine.py, models.py)
  faq/      # FAQ Engine (faq.py)
  chatbot/  # router hội thoại
  data/     # faq.json (DB hỏi đáp)
tests/      # pytest
app.py      # MVP UI (Streamlit)
```

## Cài đặt & chạy
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q            # test
ruff check .         # lint
streamlit run app.py # chạy UI
```

## Quy trình (Scrum)
- Branch: `feature/BP-<id>-<mô tả>` · commit: `BP-<id>: ...`
- PR vào `develop` → CI pass + **Đức review** → merge → Jira issue Done.

## Team
| Người | Vai trò |
|---|---|
| Lê Quang Cảnh | Tech Leader |
| Trần Xuân Đức | QA/Reviewer (Scrum Master) |
| Hồ Mai Thảo Nguyên | AIE Pipeline |
| Phạm Viết Trường | AIE Model |
| Nguyễn Thị Phương | AIE Data |
