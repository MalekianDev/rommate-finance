from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from db.enums import ProviderEnum
from db.models import Account, User
from repositories.user import UserRepository


def _integrity_error(constraint_name: str) -> IntegrityError:
    orig = MagicMock()
    orig.constraint_name = constraint_name
    return IntegrityError("INSERT", {}, orig)


@pytest.mark.asyncio
async def test_register_user_makes_first_user_a_superuser(session):
    session.scalar = AsyncMock(return_value=False)
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    repo = UserRepository()

    user = await repo.register_user(
        name="Sam",
        username="sam",
        provider=ProviderEnum.TELEGRAM,
        uid="7",
    )

    assert isinstance(user, User)
    assert user.name == "Sam"
    assert user.username == "sam"
    assert user.is_superuser is True
    added = [call.args[0] for call in session.add.call_args_list]
    assert added[0] is user
    assert isinstance(added[1], Account)
    assert added[1].user is user
    assert added[1].provider == ProviderEnum.TELEGRAM
    assert added[1].uid == "7"
    session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_register_user_does_not_make_later_users_superuser(session):
    session.scalar = AsyncMock(return_value=True)
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    user = await UserRepository().register_user(
        name="Alex",
        username="alex",
        provider=ProviderEnum.TELEGRAM,
        uid="8",
    )

    assert user.is_superuser is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("constraint", "message"),
    [
        ("users_username_key", "Username already taken."),
        ("accounts_provider_uid_key", "Account already registered."),
    ],
)
async def test_register_user_maps_known_integrity_errors(session, constraint, message):
    session.scalar = AsyncMock(return_value=True)
    session.flush = AsyncMock()
    session.commit = AsyncMock(side_effect=_integrity_error(constraint))
    session.rollback = AsyncMock()

    with pytest.raises(ValueError, match=message):
        await UserRepository().register_user(
            name="Sam",
            username="sam",
            provider=ProviderEnum.TELEGRAM,
            uid="7",
        )


@pytest.mark.asyncio
async def test_register_user_reraises_unknown_integrity_errors(session):
    session.scalar = AsyncMock(return_value=True)
    session.flush = AsyncMock()
    session.commit = AsyncMock(side_effect=_integrity_error("some_other_constraint"))
    session.rollback = AsyncMock()

    with pytest.raises(IntegrityError):
        await UserRepository().register_user(
            name="Sam",
            username="sam",
            provider=ProviderEnum.TELEGRAM,
            uid="7",
        )


@pytest.mark.asyncio
async def test_has_active_room_returns_boolean(session):
    session.scalar = AsyncMock(return_value=1)
    repo = UserRepository()

    assert await repo.has_active_room(7) is True

    session.scalar = AsyncMock(return_value=None)
    assert await repo.has_active_room(7) is False
    stmt = session.scalar.await_args.args[0]
    assert "room_members" in str(stmt)
