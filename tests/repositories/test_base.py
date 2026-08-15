from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.orm import joinedload

from db.models import Account, Category
from repositories.base import BaseRepository
from repositories.category import CategoryRepository


def test_subclass_must_define_model():
    with pytest.raises(TypeError, match="must define a 'model' class attribute"):

        class BrokenRepository(BaseRepository):
            pass


def test_build_select_uses_scalar_query_for_models_and_single_columns(repository):
    repo, _ = repository

    model_stmt, model_is_scalar = repo._build_select()
    column_stmt, column_is_scalar = repo._build_select([Category.name])
    multi_column_stmt, multi_column_is_scalar = repo._build_select([Category.id, Category.name])

    assert model_is_scalar is True
    assert column_is_scalar is True
    assert multi_column_is_scalar is False
    assert str(model_stmt) == "SELECT categories.name, categories.color, categories.id \nFROM categories"
    assert str(column_stmt) == "SELECT categories.name \nFROM categories"
    assert str(multi_column_stmt) == "SELECT categories.id, categories.name \nFROM categories"


@pytest.mark.asyncio
async def test_find_all_uses_scalars_for_model_queries(repository):
    repo, session = repository
    scalar_result = MagicMock()
    scalar_result.all.return_value = ["food", "rent"]
    session.scalars = AsyncMock(return_value=scalar_result)

    result = await repo.find_all(columns=[Category.name])

    assert result == ["food", "rent"]
    session.scalars.assert_awaited_once()
    session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_find_all_uses_execute_for_multiple_columns(repository):
    repo, session = repository
    row_result = MagicMock()
    row_result.all.return_value = [(1, "food")]
    session.execute = AsyncMock(return_value=row_result)

    result = await repo.find_all(columns=[Category.id, Category.name])

    assert result == [(1, "food")]
    session.execute.assert_awaited_once()
    session.scalars.assert_not_called()


@pytest.mark.asyncio
async def test_find_returns_scalar_for_single_column_lookups(repository):
    repo, session = repository
    session.scalar = AsyncMock(return_value="food")

    result = await repo.find(filters=[Category.id == 1], columns=[Category.name])

    assert result == "food"
    stmt = session.scalar.await_args.args[0]
    assert "categories.name" in str(stmt)
    assert "categories.id" in str(stmt)
    session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_find_uses_execute_for_multiple_columns_and_applies_options(repository):
    repo, session = repository
    row_result = MagicMock()
    row_result.first.return_value = (1, "food")
    session.execute = AsyncMock(return_value=row_result)

    result = await repo.find(
        filters=[Category.id == 1],
        columns=[Category.id, Category.name],
        options=[joinedload(Account.user)],
    )

    assert result == (1, "food")
    session.execute.assert_awaited_once()
    session.scalar.assert_not_called()


@pytest.mark.asyncio
async def test_get_by_id_delegates_to_session(repository):
    repo, session = repository
    category = MagicMock()
    session.get = AsyncMock(return_value=category)

    result = await repo.get_by_id(3)

    assert result is category
    session.get.assert_awaited_once_with(Category, 3)


@pytest.mark.asyncio
async def test_create_adds_and_refreshes_object(repository):
    repo, session = repository
    obj = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    result = await repo.create(obj)

    assert result is obj
    session.add.assert_called_once_with(obj)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(obj)


@pytest.mark.asyncio
async def test_update_merges_then_refreshes(repository):
    repo, session = repository
    obj = MagicMock()
    merged = MagicMock()
    session.merge = AsyncMock(return_value=merged)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    result = await repo.update(obj)

    assert result is merged
    session.merge.assert_awaited_once_with(obj)
    session.refresh.assert_awaited_once_with(merged)


@pytest.mark.asyncio
async def test_delete_and_delete_by_id_commit_the_change(repository):
    repo, session = repository
    obj = MagicMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    await repo.delete(obj)
    await repo.delete_by_id(9)

    session.delete.assert_awaited_once_with(obj)
    session.execute.assert_awaited_once()
    assert session.commit.await_count == 2
    assert "DELETE FROM categories" in str(session.execute.await_args.args[0])


@pytest.mark.asyncio
async def test_commit_rolls_back_and_reraises_on_failure(repository):
    repo, session = repository
    failure = RuntimeError("database unavailable")
    session.commit = AsyncMock(side_effect=failure)
    session.rollback = AsyncMock()

    with pytest.raises(RuntimeError, match="database unavailable"):
        await repo._commit()

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_commit_and_refresh_honors_repository_options(repository):
    repo, session = repository
    obj = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    await repo._commit_and_refresh(obj)

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(obj)

    no_commit_repo = CategoryRepository(commit=False, refresh=False)
    await no_commit_repo._commit_and_refresh(obj)

    assert session.commit.await_count == 1
    assert session.refresh.await_count == 1
