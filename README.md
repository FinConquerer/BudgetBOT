# 💰 BudgetBOT

Chatbot tư vấn & lập kế hoạch ngân sách cá nhân — đồ án **AIO Conquer 2026 (Module 1)**, team **FinConquerer**.

> ⚠️ Chỉ mang tính tham khảo, KHÔNG phải lời khuyên tài chính/đầu tư.

## Chức năng
- **FAQ**: hỏi đáp kiến thức tài chính cá nhân (V1: tra DB từ khoá → V2: RAG/LLM).
- **Rule Engine**: thu thập thông tin → tính chỉ số (50/30/20, savings rate, quỹ khẩn cấp, tính khả thi mục tiêu) → đề xuất phân bổ. *Deterministic, có test.*

## Kiến trúc (monorepo — tách Frontend / Backend)
```
frontend/                 # React (Vite + TypeScript)  ── UI
  src/{api.ts, App.tsx}
backend/                  # FastAPI (Python)           ── API
  app/
    api/routes.py         # endpoints /api/faq, /api/plan
    core/{rules,faq,chatbot}   # business logic (deterministic, có test)
    db/{database,models,seed}  # SQLAlchemy → PostgreSQL
    schemas.py            # Pydantic (hợp đồng FE↔BE)
    main.py               # FastAPI app + CORS
  data/faq.json           # nguồn seed FAQ
  tests/                  # pytest
docker-compose.yml        # postgres + backend + frontend
app.py                    # prototype Streamlit (demo nhanh, không phải FE chính thức)
```

**Stack:** React (FE) · FastAPI (BE) · PostgreSQL (DB).

## Chạy nhanh (Docker)
```bash
docker compose up --build
# Frontend  → http://localhost:5173
# API docs  → http://localhost:8000/docs
```

## Chạy thủ công (dev)
```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL="postgresql+psycopg://budgetbot:budgetbot@localhost:5432/budgetbot"  # bỏ qua → SQLite fallback
pytest -q && ruff check .
uvicorn app.main:app --reload      # API ở :8000

# Frontend
cd ../frontend
npm install && npm run dev          # UI ở :5173 (proxy /api → :8000)
```

## Quy trình (Scrum)
- Branch: `feature/BP-<id>-<mô tả>` · commit: `BP-<id>: ...`
- **PR → `develop`**: CI pass + **Tech Leader** code review → merge → Jira issue Done.
- **PR → `production`**: CI pass + **QA/Reviewer** chốt quality gate (nên + Tech Leader) → merge + tag.
- Chi tiết: note *AIO Conquer 2026 - Setup Jira & GitHub (Agile Scrum)* mục B.4b.

## Team
| Vai trò kỹ thuật | Vai trò Scrum |
|---|---|
| Tech Leader | (Member) |
| QA/Reviewer | Scrum Master |
| AIE Pipeline | Dev |
| AIE Model | Dev |
| AIE Data | Dev |
