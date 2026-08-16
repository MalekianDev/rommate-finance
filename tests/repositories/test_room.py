from unittest.mock import AsyncMock, MagicMock

import pytest

from db.models import Room, RoomMember, User
from repositories.room import RoomRepository


@pytest.mark.asyncio
async def test_get_rooms_with_members_for_user_returns_unique_rooms(session):
    rooms = [MagicMock(), MagicMock()]
    scalar_result = MagicMock()
    scalar_result.unique.return_value.all.return_value = rooms
    session.scalars = AsyncMock(return_value=scalar_result)
    repo = RoomRepository()

    result = await repo.get_rooms_with_members_for_user(7)

    assert result == rooms
    stmt = session.scalars.await_args.args[0]
    compiled = str(stmt)
    assert "FROM rooms" in compiled
    assert "room_members" in compiled
    params = stmt.compile().params
    assert 7 in params.values()


@pytest.mark.asyncio
async def test_register_room_adds_creator_as_member_and_refreshes(session):
    creator = User(name="Sam", username="sam")
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    repo = RoomRepository()

    room = await repo.register_room(name="Flat", created_by=creator)

    assert isinstance(room, Room)
    assert room.name == "Flat"
    assert room.created_by is creator
    added = [call.args[0] for call in session.add.call_args_list]
    assert added[0] is room
    assert isinstance(added[1], RoomMember)
    assert added[1].room is room
    assert added[1].user is creator
    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(room)
