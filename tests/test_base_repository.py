from unittest.mock import AsyncMock, MagicMock

import pytest

from db.models import Category
from repositories.category import CategoryRepository


@pytest.fixture
def repository(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr("repositories.base.get_current_session", lambda: session)
    return CategoryRepository(), session


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
