from types import SimpleNamespace

import pytest

from schemas.transaction import Transaction as TransactionDraft


@pytest.fixture
def users_map():
    return {7: "Sam", 8: "Alex"}


@pytest.fixture
def transaction_draft():
    return TransactionDraft(
        room_id=10,
        created_by_id=7,
        description="Dinner",
        category_id=1,
        total_amount=42.5,
        payments=[{"user_id": 7, "amount": 42.5}],
        splits=[{"user_id": 7, "amount": 21.25}, {"user_id": 8, "amount": 21.25}],
    )


@pytest.fixture
def room_with_members(users_map):
    return SimpleNamespace(
        id=10,
        name="Flat",
        members=[
            SimpleNamespace(user_id=user_id, user=SimpleNamespace(name=name))
            for user_id, name in users_map.items()
        ],
    )
