from telegram.keyboards import (
    main_menu_keyboard,
    manage_rooms_keyboard,
    transaction_confirmation_keyboard,
)


def _button_texts(keyboard):
    return [button.text for row in keyboard.keyboard for button in row]


def test_main_menu_keyboard_adds_settings_only_for_superusers():
    regular = _button_texts(main_menu_keyboard())
    superuser = _button_texts(main_menu_keyboard(is_superuser=True))

    assert "📝 Add Transaction" in regular
    assert "⚙️ Settings" not in regular
    assert "⚙️ Settings" in superuser


def test_manage_rooms_keyboard_shows_room_list_only_when_user_has_a_room():
    without_room = _button_texts(manage_rooms_keyboard(has_active_room=False))
    with_room = _button_texts(manage_rooms_keyboard(has_active_room=True))

    assert without_room == ["🤝 Create Room"]
    assert "🧑‍💻 Rooms list" in with_room
    assert "🔙 Back" in with_room


def test_transaction_confirmation_keyboard_uses_callback_data():
    buttons = transaction_confirmation_keyboard().inline_keyboard[0]

    assert [button.callback_data for button in buttons] == ["transaction:confirm", "transaction:cancel"]
