"""Điểm vào FastAPI. Chạy: uvicorn app.main:app --reload"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Tạo schema + seed FAQ khi khởi động (idempotent)."""
    from app.db.seed import seed

    seed()
    yield


app = FastAPI(title="BudgetBOT API", version="0.1.0", lifespan=lifespan)

# Cho phép Frontend React (Vite dev server) gọi API.
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
