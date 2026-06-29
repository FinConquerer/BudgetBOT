"""Interface truy xuất dữ liệu và adapter SQLAlchemy cho phiên chat/tin nhắn."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import ChatMessage, ChatSession


@dataclass(frozen=True)
class ChatSessionRecord:
    id: str
    user_id: str
    title: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


@dataclass(frozen=True)
class ChatMessageRecord:
    id: str
    chat_id: str
    role: str
    content: str
    sources: list[dict]
    created_at: datetime


class ChatRepository(Protocol):
    def create_chat(self, *, user_id: str, title: str | None) -> ChatSessionRecord:
        """Tạo một chat session cho user."""

    def list_chats(self, *, user_id: str, limit: int, offset: int) -> list[ChatSessionRecord]:
        """Lấy danh sách chat session chưa xóa thuộc một user."""

    def count_chats(self, *, user_id: str) -> int:
        """Đếm số chat session chưa xóa thuộc một user."""

    def get_chat(self, *, user_id: str, chat_id: str) -> ChatSessionRecord | None:
        """Lấy một chat session chưa xóa theo id và chủ sở hữu."""

    def update_chat(
        self,
        *,
        user_id: str,
        chat_id: str,
        title: str,
    ) -> ChatSessionRecord | None:
        """Cập nhật tiêu đề chat theo id và chủ sở hữu."""

    def delete_chat(self, *, user_id: str, chat_id: str) -> bool:
        """Đánh dấu xóa mềm một phiên chat theo id và chủ sở hữu."""

    def create_message(
        self,
        *,
        chat_id: str,
        role: str,
        content: str,
        sources: list[dict],
    ) -> ChatMessageRecord:
        """Tạo một chat message."""

    def list_messages(self, *, chat_id: str, limit: int, offset: int) -> list[ChatMessageRecord]:
        """Lấy danh sách message trong một chat."""

    def count_messages(self, *, chat_id: str) -> int:
        """Đếm số message trong một chat."""

    def get_last_message(self, *, chat_id: str) -> ChatMessageRecord | None:
        """Trả message mới nhất để hiển thị preview trong danh sách."""


class SQLAlchemyChatRepository:
    """Lớp truy xuất SQLAlchemy cho phiên chat và tin nhắn."""

    def __init__(self, db: Session):
        self.db = db

    def create_chat(self, *, user_id: str, title: str | None) -> ChatSessionRecord:
        now = datetime.now(timezone.utc)
        chat = ChatSession(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return self._chat_record(chat)

    def list_chats(self, *, user_id: str, limit: int, offset: int) -> list[ChatSessionRecord]:
        chats = (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id, ChatSession.deleted_at.is_(None))
            .order_by(ChatSession.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._chat_record(chat) for chat in chats]

    def count_chats(self, *, user_id: str) -> int:
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id, ChatSession.deleted_at.is_(None))
            .count()
        )

    def get_chat(self, *, user_id: str, chat_id: str) -> ChatSessionRecord | None:
        chat = self._query_owned_chat(user_id=user_id, chat_id=chat_id).first()
        return self._chat_record(chat) if chat else None

    def update_chat(
        self,
        *,
        user_id: str,
        chat_id: str,
        title: str,
    ) -> ChatSessionRecord | None:
        chat = self._query_owned_chat(user_id=user_id, chat_id=chat_id).first()
        if not chat:
            return None
        chat.title = title
        chat.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(chat)
        return self._chat_record(chat)

    def delete_chat(self, *, user_id: str, chat_id: str) -> bool:
        chat = self._query_owned_chat(user_id=user_id, chat_id=chat_id).first()
        if not chat:
            return False
        now = datetime.now(timezone.utc)
        chat.deleted_at = now
        chat.updated_at = now
        self.db.commit()
        return True

    def create_message(
        self,
        *,
        chat_id: str,
        role: str,
        content: str,
        sources: list[dict],
    ) -> ChatMessageRecord:
        now = datetime.now(timezone.utc)
        message = ChatMessage(
            id=str(uuid4()),
            chat_id=chat_id,
            role=role,
            content=content,
            sources=sources,
            created_at=now,
        )
        chat = self.db.get(ChatSession, chat_id)
        if chat:
            chat.updated_at = now
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return self._message_record(message)

    def list_messages(self, *, chat_id: str, limit: int, offset: int) -> list[ChatMessageRecord]:
        messages = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._message_record(message) for message in messages]

    def count_messages(self, *, chat_id: str) -> int:
        return self.db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).count()

    def get_last_message(self, *, chat_id: str) -> ChatMessageRecord | None:
        message = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        return self._message_record(message) if message else None

    def _query_owned_chat(self, *, user_id: str, chat_id: str):
        return self.db.query(ChatSession).filter(
            ChatSession.id == chat_id,
            ChatSession.user_id == user_id,
            ChatSession.deleted_at.is_(None),
        )

    def _chat_record(self, chat: ChatSession) -> ChatSessionRecord:
        return ChatSessionRecord(
            id=chat.id,
            user_id=chat.user_id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            deleted_at=chat.deleted_at,
        )

    def _message_record(self, message: ChatMessage) -> ChatMessageRecord:
        return ChatMessageRecord(
            id=message.id,
            chat_id=message.chat_id,
            role=message.role,
            content=message.content,
            sources=message.sources or [],
            created_at=message.created_at,
        )
