"""Điểm vào FastAPI. Chạy: uvicorn app.main:app --reload"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(title="BudgetBOT Rulebase API", version="0.1.0")

# Cho phép Frontend React (Vite dev server) gọi API.
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/", tags=["meta"])
def root() -> dict[str, str | list[str]]:
    """Trang kiểm tra nhanh khi mở API từ trình duyệt."""
    return {
        "name": "BudgetBOT Rulebase API",
        "status": "ok",
        "docs": "/docs",
        "endpoints": ["/health", "/api/plan", "/api/what-if", "/api/mock-profiles"],
    }


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
