from unittest.mock import AsyncMock, MagicMock

import pytest

from telegram.handlers.back_handler import handle_back


@pytest.mark.asyncio
async def test_handle_back_replies_with_first_stage(monkeypatch, message, state):
    keyboard = MagicMock()
    monkeypatch.setattr(
        "telegram.handlers.back_handler.get_first_stage",
        AsyncMock(return_value=("Main menu:", keyboard)),
    )

    await handle_back(message, state)

    message.reply.assert_awaited_once_with("Main menu:", reply_markup=keyboard)
