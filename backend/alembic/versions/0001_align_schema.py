"""Align existing DB with ORM: add missing columns (idempotent).

Adopts Alembic on a database whose tables were created outside of migrations
(via create_all) and had drifted from the models — notably `users.role` was
missing, breaking every auth endpoint. Uses ADD COLUMN IF NOT EXISTS so it is
safe to run on a partially-correct or already-correct database (PostgreSQL).

Revision ID: 0001_align_schema
Revises:
Create Date: 2026-07-01
"""
from alembic import op

revision = "0001_align_schema"
down_revision = None
branch_labels = None
depends_on = None

# (table, column, column definition) — only audit/extra columns prone to drift.
COLUMNS = [
    ("users", "role", "VARCHAR(20) NOT NULL DEFAULT 'user'"),
    ("users", "is_active", "BOOLEAN NOT NULL DEFAULT TRUE"),
    ("users", "created_at", "TIMESTAMPTZ NOT NULL DEFAULT now()"),
    ("users", "updated_at", "TIMESTAMPTZ NOT NULL DEFAULT now()"),
    ("budget_plans", "input_data", "JSON NOT NULL DEFAULT '{}'::json"),
    ("budget_plans", "result", "JSON NOT NULL DEFAULT '{}'::json"),
    ("budget_plans", "created_at", "TIMESTAMPTZ NOT NULL DEFAULT now()"),
    ("budget_plans", "deleted_at", "TIMESTAMPTZ"),
    ("chat_sessions", "title", "VARCHAR(255)"),
    ("chat_sessions", "created_at", "TIMESTAMPTZ NOT NULL DEFAULT now()"),
    ("chat_sessions", "updated_at", "TIMESTAMPTZ NOT NULL DEFAULT now()"),
    ("chat_sessions", "deleted_at", "TIMESTAMPTZ"),
    ("chat_messages", "role", "VARCHAR(20) NOT NULL DEFAULT 'user'"),
    ("chat_messages", "content", "TEXT NOT NULL DEFAULT ''"),
    ("chat_messages", "sources", "JSON NOT NULL DEFAULT '[]'::json"),
    ("chat_messages", "created_at", "TIMESTAMPTZ NOT NULL DEFAULT now()"),
]


def upgrade() -> None:
    for table, column, definition in COLUMNS:
        op.execute(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {definition}')


def downgrade() -> None:
    # Repair/adopt migration — không tự động xoá cột để tránh mất dữ liệu của
    # cột vốn đã tồn tại trước khi áp dụng Alembic.
    pass
