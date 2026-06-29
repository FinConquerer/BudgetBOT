"""Bảng dữ liệu (SQLAlchemy ORM)."""
from sqlalchemy import Boolean, JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Faq(Base):
    """Một mục hỏi đáp trong DB FAQ."""
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    faq_key: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    question: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(Text)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
