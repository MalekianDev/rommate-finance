import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.transaction import build_transaction_draft


@pytest.mark.asyncio
async def test_build_transaction_draft_builds_context_and_enforces_creator(
    monkeypatch,
    transaction_draft,
    users_map,
    room_with_members,
):
    categories = [(1, "Food"), (2, "Transport")]
    category_repo = MagicMock()
    category_repo.find_all = AsyncMock(return_value=categories)
    room_repo = MagicMock()
    room_repo.get_rooms_with_members_for_user = AsyncMock(return_value=[room_with_members])
    response = MagicMock()
    response.text = transaction_draft.model_dump_json()
    client = MagicMock()
    client.models.generate_content.return_value = response

    monkeypatch.setattr("services.transaction.CategoryRepository", lambda: category_repo)
    monkeypatch.setattr("services.transaction.RoomRepository", lambda: room_repo)
    monkeypatch.setattr("services.transaction.genai.Client", lambda **_: client)
    monkeypatch.setattr("services.transaction.Settings", lambda: SimpleNamespace(gemini_api_key="test-key"))

    draft, users = await build_transaction_draft("Dinner was 42.5", created_by_id=7)

    assert draft.created_by_id == 7
    assert draft.description == "Dinner"
    assert users == users_map
    category_repo.find_all.assert_awaited_once()
    room_repo.get_rooms_with_members_for_user.assert_awaited_once_with(7)

    prompt = client.models.generate_content.call_args.kwargs["contents"]
    assert '"name": "Food"' in prompt
    assert '"room_id": 10' in prompt
    assert "Set created_by_id to 7" in prompt
    assert json.dumps({"user_id": 7, "name": "Sam"}, ensure_ascii=False) in prompt


@pytest.mark.asyncio
async def test_build_transaction_draft_overrides_model_created_by_id(monkeypatch, transaction_draft, room_with_members):
    transaction_draft.created_by_id = 999
    category_repo = MagicMock()
    category_repo.find_all = AsyncMock(return_value=[])
    room_repo = MagicMock()
    room_repo.get_rooms_with_members_for_user = AsyncMock(return_value=[room_with_members])
    response = MagicMock()
    response.text = transaction_draft.model_dump_json()
    client = MagicMock()
    client.models.generate_content.return_value = response

    monkeypatch.setattr("services.transaction.CategoryRepository", lambda: category_repo)
    monkeypatch.setattr("services.transaction.RoomRepository", lambda: room_repo)
    monkeypatch.setattr("services.transaction.genai.Client", lambda **_: client)
    monkeypatch.setattr("services.transaction.Settings", lambda: SimpleNamespace(gemini_api_key="test-key"))

    draft, users = await build_transaction_draft("Dinner", created_by_id=7)

    assert draft.created_by_id == 7
    assert users == {7: "Sam", 8: "Alex"}
