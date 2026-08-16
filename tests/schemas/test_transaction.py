import pytest
from pydantic import ValidationError

from schemas.transaction import Payment, Split, Transaction


def test_transaction_accepts_valid_payload():
    draft = Transaction(
        room_id=10,
        created_by_id=7,
        description="Dinner",
        category_id=1,
        total_amount=42.5,
        payments=[Payment(user_id=7, amount=42.5)],
        splits=[Split(user_id=7, amount=21.25), Split(user_id=8, amount=21.25)],
    )

    assert draft.room_id == 10
    assert draft.category_id == 1
    assert draft.payments[0].user_id == 7
    assert len(draft.splits) == 2


def test_transaction_defaults_optional_fields():
    draft = Transaction(
        room_id=None,
        created_by_id=7,
        description="Coffee",
        total_amount=10,
        payments=[{"user_id": 7, "amount": 10}],
    )

    assert draft.id is None
    assert draft.room_id is None
    assert draft.category_id is None
    assert draft.splits == []


def test_transaction_model_validate_json_round_trip():
    payload = """
    {
        "room_id": 10,
        "created_by_id": 7,
        "description": "Dinner",
        "category_id": null,
        "total_amount": 20,
        "payments": [{"user_id": 7, "amount": 20}],
        "splits": []
    }
    """

    draft = Transaction.model_validate_json(payload)

    assert draft.room_id == 10
    assert draft.category_id is None
    assert draft.total_amount == 20
    assert draft.splits == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"created_by_id": 7, "description": "Dinner", "total_amount": 10},
        {"created_by_id": 7, "description": "Dinner", "payments": []},
        {"description": "Dinner", "total_amount": 10, "payments": [{"user_id": 7, "amount": 10}]},
    ],
)
def test_transaction_requires_core_fields(payload):
    with pytest.raises(ValidationError):
        Transaction.model_validate(payload)
