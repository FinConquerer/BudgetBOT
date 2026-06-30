"""Interface truy xuất dữ liệu và adapter SQLAlchemy cho user."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import User


@dataclass(frozen=True)
class UserRecord:
    id: str
    username: str
    email: str | None
    password_hash: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserRepository(Protocol):
    def get_by_id(self, user_id: str) -> UserRecord | None:
        """Tìm user theo id."""

    def get_by_username(self, username: str) -> UserRecord | None:
        """Tìm user theo username."""

    def get_by_email(self, email: str) -> UserRecord | None:
        """Tìm user theo email."""

    def create_user(
        self,
        *,
        username: str,
        email: str | None,
        password_hash: str,
    ) -> UserRecord:
        """Tạo tài khoản user thường."""


class DuplicateUserError(Exception):
    """Lỗi khi username hoặc email vi phạm ràng buộc unique."""


class SQLAlchemyUserRepository:
    """Lớp truy xuất SQLAlchemy cho bảng thật `users`."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> UserRecord | None:
        user = self.db.get(User, user_id)
        return self._to_record(user) if user else None

    def get_by_username(self, username: str) -> UserRecord | None:
        user = self.db.query(User).filter(User.username == username).first()
        return self._to_record(user) if user else None

    def get_by_email(self, email: str) -> UserRecord | None:
        user = self.db.query(User).filter(User.email == email).first()
        return self._to_record(user) if user else None

    def create_user(
        self,
        *,
        username: str,
        email: str | None,
        password_hash: str,
    ) -> UserRecord:
        now = datetime.now(timezone.utc)
        user = User(
            id=str(uuid4()),
            username=username,
            email=email,
            password_hash=password_hash,
            role="user",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise DuplicateUserError from exc
        self.db.refresh(user)
        return self._to_record(user)

    def _to_record(self, user: User) -> UserRecord:
        return UserRecord(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
