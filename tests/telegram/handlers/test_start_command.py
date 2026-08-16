import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from db.enums import ProviderEnum
from telegram.handlers.start_command import (
    handle_join_start,
    handle_name,
    handle_wrong_type_name,
    start_handler,
)
from telegram.states import RegistrationStates


@pytest.fixture
def command():
    return MagicMock(args="payload")


@pytest.fixture
def invite_token():
    return uuid.uuid4()


@pytest.mark.asyncio
async def test_handle_join_start_rejects_invalid_invite(monkeypatch, message, command, invite_token):
    room_repo = MagicMock()
    room_repo.find = AsyncMock(return_value=None)
    monkeypatch.setattr("telegram.handlers.start_command.decode_payload", lambda _: str(invite_token))
    monkeypatch.setattr("telegram.handlers.start_command.RoomRepository", lambda: room_repo)
    monkeypatch.setattr("telegram.handlers.start_command.RoomMemberRepository", lambda: MagicMock())

    await handle_join_start(message, command, MagicMock())

    message.answer.assert_awaited_once_with("Invalid invite token.")


@pytest.mark.asyncio
async def test_handle_join_start_asks_unregistered_users_to_start_first(
    monkeypatch,
    message,
    command,
    invite_token,
):
    room_repo = MagicMock()
    room_repo.find = AsyncMock(return_value=10)
    account_repo = MagicMock()
    account_repo.find = AsyncMock(return_value=None)
    monkeypatch.setattr("telegram.handlers.start_command.decode_payload", lambda _: str(invite_token))
    monkeypatch.setattr("telegram.handlers.start_command.RoomRepository", lambda: room_repo)
    monkeypatch.setattr("telegram.handlers.start_command.AccountRepository", lambda: account_repo)
    monkeypatch.setattr("telegram.handlers.start_command.RoomMemberRepository", lambda: MagicMock())
    monkeypatch.setattr(
        "telegram.handlers.start_command.create_start_link",
        AsyncMock(return_value="https://t.me/bot?start=invite"),
    )

    await handle_join_start(message, command, MagicMock())

    assert "register first" in message.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_handle_join_start_skips_users_already_in_the_room(
    monkeypatch,
    message,
    command,
    invite_token,
):
    room_repo = MagicMock()
    room_repo.find = AsyncMock(return_value=10)
    account_repo = MagicMock()
    account_repo.find = AsyncMock(return_value=7)
    room_member_repo = MagicMock()
    room_member_repo.find = AsyncMock(return_value=99)
    monkeypatch.setattr("telegram.handlers.start_command.decode_payload", lambda _: str(invite_token))
    monkeypatch.setattr("telegram.handlers.start_command.RoomRepository", lambda: room_repo)
    monkeypatch.setattr("telegram.handlers.start_command.AccountRepository", lambda: account_repo)
    monkeypatch.setattr("telegram.handlers.start_command.RoomMemberRepository", lambda: room_member_repo)

    await handle_join_start(message, command, MagicMock())

    message.answer.assert_awaited_once_with("You are already in this room.")
    room_member_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_handle_join_start_adds_new_member(monkeypatch, message, command, invite_token):
    room_repo = MagicMock()
    room_repo.find = AsyncMock(return_value=10)
    account_repo = MagicMock()
    account_repo.find = AsyncMock(return_value=7)
    room_member_repo = MagicMock()
    room_member_repo.find = AsyncMock(return_value=None)
    room_member_repo.create = AsyncMock()
    monkeypatch.setattr("telegram.handlers.start_command.decode_payload", lambda _: str(invite_token))
    monkeypatch.setattr("telegram.handlers.start_command.RoomRepository", lambda: room_repo)
    monkeypatch.setattr("telegram.handlers.start_command.AccountRepository", lambda: account_repo)
    monkeypatch.setattr("telegram.handlers.start_command.RoomMemberRepository", lambda: room_member_repo)

    await handle_join_start(message, command, MagicMock())

    room_member_repo.create.assert_awaited_once()
    created = room_member_repo.create.await_args.args[0]
    assert created.room_id == 10
    assert created.user_id == 7
    assert "✅ You have joined the room." in message.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_start_handler_replies_with_first_stage(monkeypatch, message, state):
    monkeypatch.setattr(
        "telegram.handlers.start_command.get_first_stage",
        AsyncMock(return_value=("👋 Hey", MagicMock())),
    )

    await start_handler(message, state)

    message.reply.assert_awaited_once()
    assert message.reply.await_args.args[0] == "👋 Hey"


@pytest.mark.asyncio
async def test_wrong_type_name_prompts_again(message, state):
    await handle_wrong_type_name(message, state)

    message.answer.assert_awaited_once_with("Please enter a valid name.")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["", " ", "A"])
async def test_handle_name_rejects_short_names(message, state, text):
    message.text = text

    await handle_name(message, state)

    message.answer.assert_awaited_once_with("Please enter a valid name (at least 2 characters).")
    state.clear.assert_not_called()


@pytest.mark.asyncio
async def test_handle_name_registers_user_and_clears_state(monkeypatch, message, state):
    message.text = "  Sam  "
    user_repo = MagicMock()
    user_repo.register_user = AsyncMock()
    monkeypatch.setattr("telegram.handlers.start_command.UserRepository", lambda: user_repo)

    await handle_name(message, state)

    user_repo.register_user.assert_awaited_once_with(
        name="Sam",
        username="7",
        provider=ProviderEnum.TELEGRAM,
        uid="7",
    )
    state.clear.assert_awaited_once()
    assert "active room" in message.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_handle_name_surfaces_registration_errors(monkeypatch, message, state):
    message.text = "Sam"
    user_repo = MagicMock()
    user_repo.register_user = AsyncMock(side_effect=ValueError("Username already taken."))
    monkeypatch.setattr("telegram.handlers.start_command.UserRepository", lambda: user_repo)

    await handle_name(message, state)

    message.answer.assert_awaited_once_with("❌ Registration failed: Username already taken.")
    state.clear.assert_not_called()
