"""Test configuration shared across API tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_budgetbot.db")


def pytest_configure() -> None:
    from app.db.seed import seed

    seed()


@pytest.fixture
def anyio_backend():
    return "asyncio"


def pytest_sessionfinish() -> None:
    Path("test_budgetbot.db").unlink(missing_ok=True)
