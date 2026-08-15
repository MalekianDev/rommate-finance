from unittest.mock import MagicMock

import pytest

from repositories.category import CategoryRepository


@pytest.fixture
def session(monkeypatch):
    db_session = MagicMock()
    monkeypatch.setattr("repositories.base.get_current_session", lambda: db_session)
    return db_session


@pytest.fixture
def repository(session):
    return CategoryRepository(), session
