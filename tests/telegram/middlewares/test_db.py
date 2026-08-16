from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram.middlewares.db import DBSessionMiddleware


@pytest.mark.asyncio
async def test_middleware_runs_handler_inside_db_context(monkeypatch):
    entered = []

    class FakeDBContext:
        async def __aenter__(self):
            entered.append("enter")
            return MagicMock()

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            entered.append("exit")
            return False

    monkeypatch.setattr("telegram.middlewares.db.DBContext", FakeDBContext)
    handler = AsyncMock(return_value="ok")
    event = MagicMock()
    data = {"foo": 1}

    result = await DBSessionMiddleware()(handler, event, data)

    assert result == "ok"
    handler.assert_awaited_once_with(event, data)
    assert entered == ["enter", "exit"]
