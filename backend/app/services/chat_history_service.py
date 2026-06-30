"""Service xử lý lịch sử chat và chatbot MVP."""

from fastapi import HTTPException, status

from app.repositories.chat_repository import (
    ChatMessageRecord,
    ChatRepository,
    ChatSessionRecord,
)
from app.repositories.faq_repository import FaqMatchRecord, FaqSearchRepository
from app.repositories.user_repository import UserRecord
from app.schemas import (
    ChatAskRequest,
    ChatAskResponse,
    ChatCreateRequest,
    ChatListItemResponse,
    ChatListResponse,
    ChatMessageResponse,
    ChatMessagesResponse,
    ChatMessageSourceResponse,
    ChatSessionResponse,
    ChatUpdateRequest,
    DeleteChatResponse,
)

_FAQ_FALLBACK_ANSWER = (
    "Hien toi toi chua tim thay cau tra loi phu hop trong du lieu FAQ. "
    "Ban co the hoi lai ro hon hoac cung cap them thong tin."
)


class ChatHistoryService:
    """Trường hợp sử dụng cho phiên chat, tin nhắn và hỏi đáp dựa trên FAQ."""

    def __init__(
        self,
        *,
        chat_repository: ChatRepository,
        faq_repository: FaqSearchRepository,
    ):
        self.chat_repository = chat_repository
        self.faq_repository = faq_repository

    def create_chat(
        self,
        *,
        current_user: UserRecord,
        request: ChatCreateRequest,
    ) -> ChatSessionResponse:
        chat = self.chat_repository.create_chat(
            user_id=current_user.id,
            title=request.title,
        )
        return self._chat_response(chat)

    def list_chats(
        self,
        *,
        current_user: UserRecord,
        limit: int,
        offset: int,
    ) -> ChatListResponse:
        chats = self.chat_repository.list_chats(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
        )
        total = self.chat_repository.count_chats(user_id=current_user.id)
        return ChatListResponse(
            items=[self._chat_list_item(chat) for chat in chats],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_chat(
        self,
        *,
        current_user: UserRecord,
        chat_id: str,
    ) -> ChatSessionResponse:
        return self._chat_response(self._get_owned_chat(current_user, chat_id))

    def update_chat(
        self,
        *,
        current_user: UserRecord,
        chat_id: str,
        request: ChatUpdateRequest,
    ) -> ChatSessionResponse:
        chat = self.chat_repository.update_chat(
            user_id=current_user.id,
            chat_id=chat_id,
            title=request.title,
        )
        if chat is None:
            raise self._not_found()
        return self._chat_response(chat)

    def delete_chat(
        self,
        *,
        current_user: UserRecord,
        chat_id: str,
    ) -> DeleteChatResponse:
        deleted = self.chat_repository.delete_chat(
            user_id=current_user.id,
            chat_id=chat_id,
        )
        if not deleted:
            raise self._not_found()
        return DeleteChatResponse(id=chat_id, deleted=True)

    def list_messages(
        self,
        *,
        current_user: UserRecord,
        chat_id: str,
        limit: int,
        offset: int,
    ) -> ChatMessagesResponse:
        self._get_owned_chat(current_user, chat_id)
        messages = self.chat_repository.list_messages(
            chat_id=chat_id,
            limit=limit,
            offset=offset,
        )
        total = self.chat_repository.count_messages(chat_id=chat_id)
        return ChatMessagesResponse(
            items=[self._message_response(message) for message in messages],
            total=total,
            limit=limit,
            offset=offset,
        )

    def ask(
        self,
        *,
        current_user: UserRecord,
        chat_id: str,
        request: ChatAskRequest,
    ) -> ChatAskResponse:
        self._get_owned_chat(current_user, chat_id)
        user_message = self.chat_repository.create_message(
            chat_id=chat_id,
            role="user",
            content=request.message,
            sources=[],
        )
        faq_match = self.faq_repository.find_best_match(request.message)
        assistant_message = self.chat_repository.create_message(
            chat_id=chat_id,
            role="assistant",
            content=self._answer_from_match(faq_match),
            sources=self._sources_from_match(faq_match),
        )
        return ChatAskResponse(
            chat_id=chat_id,
            user_message=self._message_response(user_message),
            assistant_message=self._message_response(assistant_message),
        )

    def _get_owned_chat(
        self,
        current_user: UserRecord,
        chat_id: str,
    ) -> ChatSessionRecord:
        chat = self.chat_repository.get_chat(
            user_id=current_user.id,
            chat_id=chat_id,
        )
        if chat is None:
            raise self._not_found()
        return chat

    def _chat_response(self, chat: ChatSessionRecord) -> ChatSessionResponse:
        return ChatSessionResponse(
            id=chat.id,
            user_id=chat.user_id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )

    def _chat_list_item(self, chat: ChatSessionRecord) -> ChatListItemResponse:
        last_message = self.chat_repository.get_last_message(chat_id=chat.id)
        return ChatListItemResponse(
            id=chat.id,
            title=chat.title,
            last_message_preview=last_message.content if last_message else None,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )

    def _message_response(self, message: ChatMessageRecord) -> ChatMessageResponse:
        return ChatMessageResponse(
            id=message.id,
            chat_id=message.chat_id,
            role=message.role,
            content=message.content,
            sources=[
                ChatMessageSourceResponse(
                    faq_id=str(source["faq_id"]),
                    question=str(source["question"]),
                )
                for source in message.sources
            ],
            created_at=message.created_at,
        )

    def _answer_from_match(self, match: FaqMatchRecord | None) -> str:
        return match.answer if match else _FAQ_FALLBACK_ANSWER

    def _sources_from_match(self, match: FaqMatchRecord | None) -> list[dict]:
        if match is None:
            return []
        return [{"faq_id": match.faq_id, "question": match.question}]

    def _not_found(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )
