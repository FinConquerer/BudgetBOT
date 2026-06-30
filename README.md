# 💰 BudgetBOT

Chatbot tư vấn & lập kế hoạch ngân sách cá nhân — đồ án **AIO Conquer 2026 (Module 1)**, team **FinConquerer**.

> ⚠️ Chỉ mang tính tham khảo, KHÔNG phải lời khuyên tài chính/đầu tư.

## Chức năng
- **FAQ**: chuẩn hoá câu hỏi → nhận diện intent/sentiment → chấm điểm cụm từ → kiểm tra confidence; có thể kết hợp semantic embedding.
- **Rule Engine**: thu thập thông tin → tính chỉ số (50/30/20, savings rate, quỹ khẩn cấp, tính khả thi mục tiêu) → đề xuất phân bổ. *Deterministic, có test.*

## Kiến trúc (monorepo — tách Frontend / Backend)
```
frontend/                 # React (Vite + TypeScript)  ── UI
  src/{api.ts, App.tsx}
backend/                  # FastAPI (Python)           ── API
  app/
    api/routes.py         # endpoints /api/plan, /api/chats/{chat_id}/ask
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
cp .env.example .env
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

### Bật semantic embedding cho FAQ (tuỳ chọn)

FAQ mặc định chạy bằng phrase/intent scoring và không tải model. Để bật tìm kiếm gần nghĩa:

```bash
pip install sentence-transformers
export FAQ_EMBEDDING_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

Model được tải khi FAQ engine khởi tạo lần đầu. Giữ cùng một engine trong suốt vòng đời app để tái sử dụng embedding của kho FAQ.

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

## Environment config
- Commit `.env.example` so the team knows which variables are required.
- Do not commit `.env`; it stores real secrets such as `DATABASE_URL` and `SECRET_KEY`.
- SQLAlchemy with psycopg v3 uses URLs like `postgresql+psycopg://...`.
- FAQ Q&A uses `POST /api/chats/{chat_id}/ask`; there is no public `POST /api/faq` shortcut.
