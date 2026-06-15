"""Tạo bảng và nạp faq.json vào DB (chạy 1 lần khi khởi động / setup).

Dùng: python -m app.db.seed
"""
import json
from pathlib import Path

from app.db.database import Base, SessionLocal, engine
from app.db.models import Faq

_FAQ_JSON = Path(__file__).resolve().parents[2] / "data" / "faq.json"


def seed() -> int:
    """Tạo schema + nạp FAQ nếu bảng đang rỗng. Trả về số bản ghi sau seed."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.query(Faq).count() == 0:
            items = json.loads(_FAQ_JSON.read_text(encoding="utf-8"))
            db.add_all(
                Faq(question=i["question"], answer=i["answer"], keywords=i["keywords"])
                for i in items
            )
            db.commit()
        return db.query(Faq).count()


if __name__ == "__main__":
    print(f"Seed xong, tổng {seed()} FAQ.")
