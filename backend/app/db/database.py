"""Kết nối PostgreSQL qua SQLAlchemy.

DATABASE_URL ví dụ: postgresql+psycopg://budgetbot:budgetbot@localhost:5432/budgetbot
Local dev không có Postgres -> mặc định SQLite file để vẫn chạy được.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./budgetbot.db")

# check_same_thread chỉ cần cho SQLite (fallback dev).
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Phụ thuộc FastAPI: mở phiên làm việc cho mỗi yêu cầu và đóng khi xong."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
