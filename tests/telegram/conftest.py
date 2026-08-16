from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def user_id():
    return 7


@pytest.fixture
def message(user_id):
    msg = MagicMock()
    msg.text = "Dinner was 42.5"
    msg.from_user = SimpleNamespace(id=user_id)
    msg.answer = AsyncMock()
    msg.reply = AsyncMock()
    return msg


@pytest.fixture
def state():
    fsm = AsyncMock()
    fsm.get_data = AsyncMock(return_value={})
    fsm.update_data = AsyncMock()
    fsm.set_state = AsyncMock()
    fsm.clear = AsyncMock()
    return fsm


@pytest.fixture
def callback(user_id):
    query = MagicMock()
    query.from_user = SimpleNamespace(id=user_id)
    query.answer = AsyncMock()
    query.message = MagicMock()
    query.message.edit_text = AsyncMock()
    query.message.answer = AsyncMock()
    return query


@pytest.fixture
def account(user_id):
    user = SimpleNamespace(id=user_id, is_superuser=False)
    return SimpleNamespace(user_id=user_id, user=user)
