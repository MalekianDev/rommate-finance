from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import ReplyKeyboardRemove

from telegram.helpers import _format_draft_summary, get_first_stage
from telegram.states import RegistrationStates


def test_format_draft_summary_includes_category_payments_and_splits(transaction_draft, users_map):
    summary = _format_draft_summary(transaction_draft, users_map, category_name="Food")

    assert "Dinner" in summary
    assert "Food" in summary
    assert "Sam: 42" in summary
    assert "Alex: 21" in summary
    assert "Confirm to save this transaction." in summary


def test_format_draft_summary_escapes_html_in_user_controlled_fields(transaction_draft, users_map):
    transaction_draft.description = "Lunch at H&M <store>"
    users_map[7] = "Sam & Alex"
    users_map[8] = "Ali > Sara"
    summary = _format_draft_summary(transaction_draft, users_map, category_name="Food & Drink")

    assert "Lunch at H&amp;M &lt;store&gt;" in summary
    assert "Sam &amp; Alex" in summary
    assert "Ali &gt; Sara" in summary
    assert "Food &amp; Drink" in summary
    assert "H&M" not in summary
    assert "<store>" not in summary
    assert "Sam & Alex" not in summary


def test_format_draft_summary_falls_back_for_unknown_users_and_omits_empty_sections(transaction_draft):
    transaction_draft.splits = []
    transaction_draft.category_id = None
    summary = _format_draft_summary(transaction_draft, {})

    assert "Category:" not in summary
    assert "Splits:" not in summary
    assert "User #7: 42" in summary


@pytest.mark.asyncio
async def test_get_first_stage_returns_main_menu_for_users_with_an_active_room(monkeypatch, account, state):
    account.user.is_superuser = True
    account_repo = MagicMock()
    account_repo.get_by_chat_id = AsyncMock(return_value=account)
    user_repo = MagicMock()
    user_repo.has_active_room = AsyncMock(return_value=True)
    monkeypatch.setattr("telegram.helpers.AccountRepository", lambda: account_repo)
    monkeypatch.setattr("telegram.helpers.UserRepository", lambda: user_repo)

    text, keyboard = await get_first_stage(chat_id=7, state=state)

    assert text == "Main menu:"
    assert any("⚙️ Settings" in button.text for row in keyboard.keyboard for button in row)
    state.clear.assert_awaited_once()
    state.set_state.assert_not_called()


@pytest.mark.asyncio
async def test_get_first_stage_returns_manage_rooms_when_user_has_no_active_room(monkeypatch, account, state):
    account_repo = MagicMock()
    account_repo.get_by_chat_id = AsyncMock(return_value=account)
    user_repo = MagicMock()
    user_repo.has_active_room = AsyncMock(return_value=False)
    monkeypatch.setattr("telegram.helpers.AccountRepository", lambda: account_repo)
    monkeypatch.setattr("telegram.helpers.UserRepository", lambda: user_repo)

    text, keyboard = await get_first_stage(chat_id=7, state=state, custom_text="Need a room")

    assert text == "Need a room"
    assert any("🤝 Create Room" in button.text for row in keyboard.keyboard for button in row)
    assert not any("🧑‍💻 Rooms list" in button.text for row in keyboard.keyboard for button in row)
    account_repo.get_by_chat_id.assert_awaited_once_with(7)


@pytest.mark.asyncio
async def test_get_first_stage_starts_registration_for_unknown_users(monkeypatch, state):
    account_repo = MagicMock()
    account_repo.get_by_chat_id = AsyncMock(return_value=None)
    monkeypatch.setattr("telegram.helpers.AccountRepository", lambda: account_repo)

    text, keyboard = await get_first_stage(chat_id=7, state=state)

    assert "Welcome" in text
    assert isinstance(keyboard, ReplyKeyboardRemove)
    state.set_state.assert_awaited_once_with(RegistrationStates.name)
    state.clear.assert_not_called()


@pytest.mark.asyncio
async def test_get_first_stage_reuses_provided_account(monkeypatch, account, state):
    account_repo = MagicMock()
    account_repo.get_by_chat_id = AsyncMock()
    user_repo = MagicMock()
    user_repo.has_active_room = AsyncMock(return_value=True)
    monkeypatch.setattr("telegram.helpers.AccountRepository", lambda: account_repo)
    monkeypatch.setattr("telegram.helpers.UserRepository", lambda: user_repo)

    await get_first_stage(chat_id=7, state=state, account=account)

    account_repo.get_by_chat_id.assert_not_called()
    user_repo.has_active_room.assert_awaited_once_with(account.user_id)
