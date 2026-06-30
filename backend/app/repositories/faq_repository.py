"""Lớp truy xuất tìm kiếm FAQ bằng khớp từ khóa cho MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Faq

_FAQ_JSON = Path(__file__).resolve().parents[2] / "data" / "faq.json"


@dataclass(frozen=True)
class FaqMatchRecord:
    faq_id: str
    question: str
    answer: str


class FaqSearchRepository(Protocol):
    def find_best_match(self, message: str) -> FaqMatchRecord | None:
        """Tìm câu trả lời FAQ phù hợp nhất bằng khớp từ khóa."""


class JsonFaqSearchRepository:
    """Bộ tìm FAQ dự phòng đọc từ file dataset hiện có."""

    def __init__(self, path: Path | None = None):
        self.path = path or _FAQ_JSON

    def find_best_match(self, message: str) -> FaqMatchRecord | None:
        q = message.lower()
        best: dict | None = None
        best_score = 0
        for index, item in enumerate(self._load_items(), start=1):
            score = self._score(q, item.get("keywords", []))
            if score > best_score:
                best = {**item, "id": item.get("id") or f"faq_{index:03d}"}
                best_score = score
        if not best:
            return None
        return FaqMatchRecord(
            faq_id=str(best["id"]),
            question=str(best["question"]),
            answer=str(best["answer"]),
        )

    def _load_items(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _score(self, message: str, keywords: list[str]) -> int:
        return sum(1 for keyword in keywords if str(keyword).lower() in message)


class SQLAlchemyFaqSearchRepository:
    """Bộ tìm FAQ từ bảng `faqs`, dự phòng bằng JSON khi chưa có dữ liệu."""

    def __init__(
        self,
        db: Session,
        fallback: FaqSearchRepository | None = None,
    ):
        self.db = db
        self.fallback = fallback or JsonFaqSearchRepository()

    def find_best_match(self, message: str) -> FaqMatchRecord | None:
        q = message.lower()
        try:
            faqs = self.db.query(Faq).all()
        except SQLAlchemyError:
            return self.fallback.find_best_match(message)

        best: Faq | None = None
        best_score = 0
        for faq in faqs:
            score = self._score(q, faq.keywords or [])
            if score > best_score:
                best = faq
                best_score = score
        if best:
            return FaqMatchRecord(
                faq_id=str(best.id),
                question=best.question,
                answer=best.answer,
            )
        return self.fallback.find_best_match(message)

    def _score(self, message: str, keywords: list[str]) -> int:
        return sum(1 for keyword in keywords if str(keyword).lower() in message)
