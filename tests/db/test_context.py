from unittest.mock import AsyncMock, MagicMock

import pytest

from db.context import DBContext, get_current_session


@pytest.mark.asyncio
async def test_get_current_session_requires_active_context():
    with pytest.raises(RuntimeError, match="No active database session context found"):
        get_current_session()


@pytest.mark.asyncio
async def test_db_context_binds_session_and_closes_it(monkeypatch):
    session = MagicMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    monkeypatch.setattr("db.context.session_maker", lambda: session)

    async with DBContext() as bound:
        assert bound is session
        assert get_current_session() is session

    session.close.assert_awaited_once()
    session.rollback.assert_not_called()
    with pytest.raises(RuntimeError, match="No active database session context found"):
        get_current_session()


@pytest.mark.asyncio
async def test_db_context_rolls_back_on_error(monkeypatch):
    session = MagicMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    monkeypatch.setattr("db.context.session_maker", lambda: session)

    with pytest.raises(RuntimeError, match="boom"):
        async with DBContext():
            raise RuntimeError("boom")

    session.rollback.assert_awaited_once()
    session.close.assert_awaited_once()
