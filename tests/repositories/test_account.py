from unittest.mock import AsyncMock, MagicMock

import pytest

from db.enums import ProviderEnum
from repositories.account import AccountRepository


@pytest.mark.asyncio
async def test_get_by_chat_id_loads_telegram_account_with_user(session):
    account = MagicMock()
    session.scalar = AsyncMock(return_value=account)
    repo = AccountRepository()

    result = await repo.get_by_chat_id(12345)

    assert result is account
    stmt = session.scalar.await_args.args[0]
    compiled = str(stmt)
    assert "accounts.provider" in compiled
    assert "accounts.uid" in compiled
    assert stmt._with_options
    params = stmt.compile().params
    print(f"logging params: {params}")
    assert ProviderEnum.TELEGRAM in params.values()
    assert "12345" in params.values()
