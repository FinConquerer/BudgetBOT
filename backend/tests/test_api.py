"""Test API cho auth, plan history, chat history và rulebase."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.dependencies import (
    get_chat_repository,
    get_faq_search_repository,
    get_plan_repository,
    get_user_repository,
)
from app.main import app
from app.repositories.chat_repository import ChatMessageRecord, ChatSessionRecord
from app.repositories.faq_repository import FaqMatchRecord
from app.repositories.plan_repository import PlanRecord
from app.repositories.user_repository import DuplicateUserError, UserRecord


class InMemoryUserRepository:
    def __init__(self):
        self.users: dict[str, UserRecord] = {}

    def get_by_id(self, user_id: str) -> UserRecord | None:
        return self.users.get(user_id)

    def get_by_username(self, username: str) -> UserRecord | None:
        return next(
            (user for user in self.users.values() if user.username == username),
            None,
        )

    def get_by_email(self, email: str) -> UserRecord | None:
        return next(
            (user for user in self.users.values() if user.email == email),
            None,
        )

    def create_user(
        self,
        *,
        username: str,
        email: str | None,
        password_hash: str,
    ) -> UserRecord:
        if self.get_by_username(username) or (email and self.get_by_email(email)):
            raise DuplicateUserError
        now = datetime.now(timezone.utc)
        user = UserRecord(
            id=str(uuid4()),
            username=username,
            email=email,
            password_hash=password_hash,
            role="user",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.users[user.id] = user
        return user


class InMemoryPlanRepository:
    def __init__(self):
        self.plans: dict[str, PlanRecord] = {}

    def create_plan(
        self,
        *,
        user_id: str,
        input_data: dict,
        result: dict,
    ) -> PlanRecord:
        now = datetime.now(timezone.utc)
        plan = PlanRecord(
            id=str(uuid4()),
            user_id=user_id,
            input_data=input_data,
            result=result,
            created_at=now,
        )
        self.plans[plan.id] = plan
        return plan

    def list_plans(self, *, user_id: str, limit: int, offset: int) -> list[PlanRecord]:
        plans = [
            plan
            for plan in self.plans.values()
            if plan.user_id == user_id and plan.deleted_at is None
        ]
        plans.sort(key=lambda plan: plan.created_at, reverse=True)
        return plans[offset : offset + limit]

    def count_plans(self, *, user_id: str) -> int:
        return len(
            [
                plan
                for plan in self.plans.values()
                if plan.user_id == user_id and plan.deleted_at is None
            ]
        )

    def get_plan(self, *, user_id: str, plan_id: str) -> PlanRecord | None:
        plan = self.plans.get(plan_id)
        if not plan or plan.user_id != user_id or plan.deleted_at is not None:
            return None
        return plan

    def delete_plan(self, *, user_id: str, plan_id: str) -> bool:
        plan = self.get_plan(user_id=user_id, plan_id=plan_id)
        if plan is None:
            return False
        self.plans[plan_id] = PlanRecord(
            id=plan.id,
            user_id=plan.user_id,
            input_data=plan.input_data,
            result=plan.result,
            created_at=plan.created_at,
            deleted_at=datetime.now(timezone.utc),
        )
        return True


class InMemoryChatRepository:
    def __init__(self):
        self.chats: dict[str, ChatSessionRecord] = {}
        self.messages: dict[str, ChatMessageRecord] = {}

    def create_chat(self, *, user_id: str, title: str | None) -> ChatSessionRecord:
        now = datetime.now(timezone.utc)
        chat = ChatSessionRecord(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            created_at=now,
            updated_at=now,
        )
        self.chats[chat.id] = chat
        return chat

    def list_chats(
        self,
        *,
        user_id: str,
        limit: int,
        offset: int,
    ) -> list[ChatSessionRecord]:
        chats = [
            chat
            for chat in self.chats.values()
            if chat.user_id == user_id and chat.deleted_at is None
        ]
        chats.sort(key=lambda chat: chat.updated_at, reverse=True)
        return chats[offset : offset + limit]

    def count_chats(self, *, user_id: str) -> int:
        return len(
            [
                chat
                for chat in self.chats.values()
                if chat.user_id == user_id and chat.deleted_at is None
            ]
        )

    def get_chat(self, *, user_id: str, chat_id: str) -> ChatSessionRecord | None:
        chat = self.chats.get(chat_id)
        if not chat or chat.user_id != user_id or chat.deleted_at is not None:
            return None
        return chat

    def update_chat(
        self,
        *,
        user_id: str,
        chat_id: str,
        title: str,
    ) -> ChatSessionRecord | None:
        chat = self.get_chat(user_id=user_id, chat_id=chat_id)
        if chat is None:
            return None
        updated = ChatSessionRecord(
            id=chat.id,
            user_id=chat.user_id,
            title=title,
            created_at=chat.created_at,
            updated_at=datetime.now(timezone.utc),
        )
        self.chats[chat_id] = updated
        return updated

    def delete_chat(self, *, user_id: str, chat_id: str) -> bool:
        chat = self.get_chat(user_id=user_id, chat_id=chat_id)
        if chat is None:
            return False
        self.chats[chat_id] = ChatSessionRecord(
            id=chat.id,
            user_id=chat.user_id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=datetime.now(timezone.utc),
            deleted_at=datetime.now(timezone.utc),
        )
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
        message = ChatMessageRecord(
            id=str(uuid4()),
            chat_id=chat_id,
            role=role,
            content=content,
            sources=sources,
            created_at=now,
        )
        self.messages[message.id] = message
        chat = self.chats[chat_id]
        self.chats[chat_id] = ChatSessionRecord(
            id=chat.id,
            user_id=chat.user_id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=now,
        )
        return message

    def list_messages(
        self,
        *,
        chat_id: str,
        limit: int,
        offset: int,
    ) -> list[ChatMessageRecord]:
        messages = [
            message for message in self.messages.values() if message.chat_id == chat_id
        ]
        messages.sort(key=lambda message: message.created_at)
        return messages[offset : offset + limit]

    def count_messages(self, *, chat_id: str) -> int:
        return len(
            [
                message
                for message in self.messages.values()
                if message.chat_id == chat_id
            ]
        )

    def get_last_message(self, *, chat_id: str) -> ChatMessageRecord | None:
        messages = self.list_messages(chat_id=chat_id, limit=1_000, offset=0)
        return messages[-1] if messages else None


class InMemoryFaqSearchRepository:
    def find_best_match(self, message: str) -> FaqMatchRecord | None:
        if "50/30/20" in message or "tiet kiem" in message.lower():
            return FaqMatchRecord(
                faq_id="SAVE_001",
                question="Quy tac 50/30/20 la gi?",
                answer="50% nhu cau, 30% mong muon, 20% tiet kiem va tra no.",
            )
        return None


@pytest.fixture
def client():
    user_repository = InMemoryUserRepository()
    plan_repository = InMemoryPlanRepository()
    chat_repository = InMemoryChatRepository()
    faq_repository = InMemoryFaqSearchRepository()
    app.dependency_overrides[get_user_repository] = lambda: user_repository
    app.dependency_overrides[get_plan_repository] = lambda: plan_repository
    app.dependency_overrides[get_chat_repository] = lambda: chat_repository
    app.dependency_overrides[get_faq_search_repository] = lambda: faq_repository
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def auth_headers(client, username: str = "duc") -> dict[str, str]:
    client.post(
        "/api/auth/register",
        json={"username": username, "password": "12345678"},
    )
    login = client.post(
        "/api/auth/login",
        json={"username": username, "password": "12345678"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def plan_payload(financial_goal: str = "mua laptop") -> dict:
    return {
        "monthly_income": 20_000_000,
        "fixed_expenses": 7_000_000,
        "variable_expenses": 5_000_000,
        "debt_payment": 1_000_000,
        "debt_outstanding": 20_000_000,
        "current_savings": 30_000_000,
        "financial_goal": financial_goal,
        "goal_amount": 25_000_000,
        "goal_deadline_months": 10,
        "income_stability": "stable",
    }


def create_chat(client, headers: dict[str, str], title: str = "Tu van ngan sach") -> dict:
    response = client.post("/api/chats", json={"title": title}, headers=headers)
    assert response.status_code == 200
    return response.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_version_endpoint(client):
    r = client.get("/api/version")
    assert r.status_code == 200
    assert r.json()["name"] == "BudgetBOT API"


def test_register_endpoint_creates_normal_user_with_hashed_password(client):
    r = client.post(
        "/api/auth/register",
        json={
            "username": "duc",
            "password": "12345678",
            "email": "duc@example.com",
        },
    )

    assert r.status_code == 200
    body = r.json()
    assert body["username"] == "duc"
    assert body["email"] == "duc@example.com"
    assert body["role"] == "user"
    assert "password" not in body

    repository = app.dependency_overrides[get_user_repository]()
    stored_user = repository.get_by_username("duc")
    assert stored_user.password_hash != "12345678"


def test_login_endpoint_returns_bearer_token(client):
    client.post(
        "/api/auth/register",
        json={"username": "duc", "password": "12345678"},
    )

    r = client.post(
        "/api/auth/login",
        json={"username": "duc", "password": "12345678"},
    )

    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2
    assert body["expires_in"] > 0
    assert body["user"]["username"] == "duc"


def test_me_endpoint_returns_current_user(client):
    client.post(
        "/api/auth/register",
        json={"username": "duc", "password": "12345678"},
    )
    login = client.post(
        "/api/auth/login",
        json={"username": "duc", "password": "12345678"},
    )
    token = login.json()["access_token"]

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 200
    assert r.json()["username"] == "duc"


def test_create_chat_requires_auth_and_attaches_current_user(client):
    unauthorized = client.post("/api/chats", json={"title": "Tu van ngan sach"})
    headers = auth_headers(client)

    created = client.post(
        "/api/chats",
        json={"title": "Tu van ngan sach"},
        headers=headers,
    )

    assert unauthorized.status_code == 401
    assert created.status_code == 200
    body = created.json()
    assert body["user_id"]
    assert body["title"] == "Tu van ngan sach"


def test_chat_ask_saves_user_and_assistant_messages(client):
    headers = auth_headers(client)
    chat = create_chat(client, headers)

    response = client.post(
        f"/api/chats/{chat['id']}/ask",
        json={"message": "Quy tac 50/30/20 la gi?"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["chat_id"] == chat["id"]
    assert body["user_message"]["role"] == "user"
    assert body["user_message"]["content"] == "Quy tac 50/30/20 la gi?"
    assert body["assistant_message"]["role"] == "assistant"
    assert body["assistant_message"]["sources"][0]["faq_id"] == "SAVE_001"
    assert "20% tiet kiem" in body["assistant_message"]["content"]


def test_chat_ask_requires_authentication(client):
    headers = auth_headers(client)
    chat = create_chat(client, headers)

    response = client.post(
        f"/api/chats/{chat['id']}/ask",
        json={"message": "Quy tac 50/30/20 la gi?"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_load_chat_message_history(client):
    headers = auth_headers(client)
    chat = create_chat(client, headers)
    client.post(
        f"/api/chats/{chat['id']}/ask",
        json={"message": "Quy tac 50/30/20 la gi?"},
        headers=headers,
    )

    response = client.get(f"/api/chats/{chat['id']}/messages", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["role"] for item in body["items"]] == ["user", "assistant"]


def test_chat_list_detail_update_delete(client):
    headers = auth_headers(client)
    chat = create_chat(client, headers)

    list_response = client.get("/api/chats", headers=headers)
    detail_response = client.get(f"/api/chats/{chat['id']}", headers=headers)
    update_response = client.put(
        f"/api/chats/{chat['id']}",
        json={"title": "Ke hoach tiet kiem"},
        headers=headers,
    )
    delete_response = client.delete(f"/api/chats/{chat['id']}", headers=headers)
    deleted_detail_response = client.get(f"/api/chats/{chat['id']}", headers=headers)

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == chat["id"]
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Ke hoach tiet kiem"
    assert delete_response.status_code == 200
    assert delete_response.json() == {"id": chat["id"], "deleted": True}
    assert deleted_detail_response.status_code == 404


def test_user_cannot_access_chat_owned_by_another_user(client):
    user_a_headers = auth_headers(client, "duc")
    user_b_headers = auth_headers(client, "canh")
    chat = create_chat(client, user_a_headers)

    detail_response = client.get(f"/api/chats/{chat['id']}", headers=user_b_headers)
    update_response = client.put(
        f"/api/chats/{chat['id']}",
        json={"title": "Khong duoc sua"},
        headers=user_b_headers,
    )
    messages_response = client.get(
        f"/api/chats/{chat['id']}/messages",
        headers=user_b_headers,
    )
    ask_response = client.post(
        f"/api/chats/{chat['id']}/ask",
        json={"message": "Quy tac 50/30/20 la gi?"},
        headers=user_b_headers,
    )
    delete_response = client.delete(f"/api/chats/{chat['id']}", headers=user_b_headers)

    assert detail_response.status_code == 404
    assert update_response.status_code == 404
    assert messages_response.status_code == 404
    assert ask_response.status_code == 404
    assert delete_response.status_code == 404
    assert detail_response.json() == {"detail": "Chat not found"}


def test_saved_plan_endpoints_require_auth(client):
    r = client.get("/api/plans")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not authenticated"}


def test_create_saved_plan_uses_rulebase_and_persists_result(client):
    headers = auth_headers(client)

    r = client.post("/api/plans", json=plan_payload(), headers=headers)

    assert r.status_code == 200
    body = r.json()
    assert body["user_id"]
    assert body["input_data"]["financial_goal"] == "mua laptop"
    assert body["result"]["summary"]["monthly_surplus"] == 7_000_000
    assert body["result"]["type"] == "budget_plan"


def test_list_saved_plans_returns_current_user_history(client):
    headers = auth_headers(client)
    client.post("/api/plans", json=plan_payload("mua laptop"), headers=headers)

    r = client.get("/api/plans", headers=headers)

    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["financial_goal"] == "mua laptop"
    assert body["items"][0]["monthly_surplus"] == 7_000_000


def test_get_saved_plan_detail(client):
    headers = auth_headers(client)
    created = client.post("/api/plans", json=plan_payload(), headers=headers).json()

    r = client.get(f"/api/plans/{created['id']}", headers=headers)

    assert r.status_code == 200
    body = r.json()
    assert body["id"] == created["id"]
    assert body["input_data"]["monthly_income"] == 20_000_000
    assert body["result"]["metrics"]["savings_rate"] == 0.35


def test_delete_saved_plan_hides_it_from_history(client):
    headers = auth_headers(client)
    created = client.post("/api/plans", json=plan_payload(), headers=headers).json()

    delete_response = client.delete(f"/api/plans/{created['id']}", headers=headers)
    detail_response = client.get(f"/api/plans/{created['id']}", headers=headers)
    list_response = client.get("/api/plans", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.json() == {"id": created["id"], "deleted": True}
    assert detail_response.status_code == 404
    assert list_response.json()["total"] == 0


def test_user_cannot_get_plan_owned_by_another_user(client):
    user_a_headers = auth_headers(client, "duc")
    user_b_headers = auth_headers(client, "canh")
    created = client.post(
        "/api/plans",
        json=plan_payload("mua laptop"),
        headers=user_a_headers,
    ).json()

    r = client.get(f"/api/plans/{created['id']}", headers=user_b_headers)

    assert r.status_code == 404
    assert r.json() == {"detail": "Plan not found"}


def test_user_cannot_list_or_delete_plan_owned_by_another_user(client):
    user_a_headers = auth_headers(client, "duc")
    user_b_headers = auth_headers(client, "canh")
    created = client.post(
        "/api/plans",
        json=plan_payload("mua laptop"),
        headers=user_a_headers,
    ).json()

    list_response = client.get("/api/plans", headers=user_b_headers)
    delete_response = client.delete(f"/api/plans/{created['id']}", headers=user_b_headers)
    owner_detail_response = client.get(f"/api/plans/{created['id']}", headers=user_a_headers)

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0
    assert delete_response.status_code == 404
    assert delete_response.json() == {"detail": "Plan not found"}
    assert owner_detail_response.status_code == 200


def test_plan_endpoint(client):
    r = client.post(
        "/api/plan",
        json={
            "monthly_income": 20_000_000,
            "essential_expenses": 12_000_000,
            "discretionary_expenses": 4_000_000,
            "monthly_savings": 4_000_000,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["allocation_50_30_20"]["savings"] == 4_000_000
    assert body["savings_rate"] == 0.2


def test_plan_endpoint_extended_contract(client):
    r = client.post(
        "/api/plan",
        json={
            "monthly_income": 20_000_000,
            "fixed_expenses": 7_000_000,
            "variable_expenses": 5_000_000,
            "debt_payment": 1_000_000,
            "debt_outstanding": 20_000_000,
            "current_savings": 30_000_000,
            "financial_goal": "mua laptop",
            "goal_amount": 25_000_000,
            "goal_deadline_months": 10,
            "income_stability": "stable",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["type"] == "budget_plan"
    assert body["summary"]["monthly_surplus"] == 7_000_000
    assert body["goal_assessment"]["status"] == "feasible"


def test_what_if_endpoint(client):
    r = client.post(
        "/api/what-if",
        json={
            "profile": {
                "monthly_income": 20_000_000,
                "fixed_expenses": 7_000_000,
                "variable_expenses": 5_000_000,
                "debt_payment": 1_000_000,
            },
            "change": {"field": "variable_expenses", "delta": -1_000_000},
        },
    )
    assert r.status_code == 200
    assert r.json()["comparison"]["monthly_surplus_delta"] == 1_000_000


def test_mock_profiles_endpoint(client):
    r = client.get("/api/mock-profiles")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert body
    assert {"id", "name", "description", "profile"} <= set(body[0].keys())
