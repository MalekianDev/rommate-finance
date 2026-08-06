from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from db.models import Account
from repositories import AccountRepository, UserRepository
from schemas import TransactionDraft
from telegram.keyboards import main_menu_keyboard, manage_rooms_keyboard
from telegram.states import RegistrationStates


def _format_draft_summary(
    draft: TransactionDraft,
    users_map: dict[int, str],
    category_name: str | None = None,
) -> str:
    lines = [
        "📋 <b>Transaction preview</b>",
        "",
        f"<b>Description:</b> {draft.description}",
        f"<b>Total:</b> {draft.total_amount:,.0f}",
    ]

    if category_name:
        lines.append(f"<b>Category:</b> {category_name}")

    lines.append("")
    lines.append("<b>Payments:</b>")
    for payment in draft.payments:
        name = users_map.get(payment.user_id, f"User #{payment.user_id}")
        lines.append(f"  • {name}: {payment.amount:,.0f}")

    if draft.splits:
        lines.append("")
        lines.append("<b>Splits:</b>")
        for split in draft.splits:
            name = users_map.get(split.user_id, f"User #{split.user_id}")
            lines.append(f"  • {name}: {split.amount:,.0f}")

    lines.append("")
    lines.append("Confirm to save this transaction.")
    return "\n".join(lines)


async def get_first_stage(
    chat_id: int,
    state: FSMContext | None = None,
    account: Account | None = None,
    custom_text: str | None = None,
) -> tuple[str, ReplyKeyboardRemove] | tuple[str, ReplyKeyboardMarkup]:
    """
    Get the first stage of the conversation.

    If the user is not registered, return the registration state.
    If the user has an active room, return the main menu.
    If not has an active room, return the manage rooms keyboard.
    If user is registered and state is not None, clear the state.

    args:
        chat_id: The chat ID.
        state: The FSM context.
        custom_text: The custom text to show to the user.

    Returns:
        tuple[str, None]: If user is not registered.
        tuple[str, ReplyKeyboardMarkup]: The text and keyboard to show to the user.
    """
    if account is None:
        account = await AccountRepository().get_by_chat_id(chat_id)

    if account:
        user_has_active_room = await UserRepository().has_active_room(account.user_id)

        if user_has_active_room:
            text, keyboard = custom_text or "Main menu:", main_menu_keyboard(is_superuser=account.user.is_superuser)
        else:
            text, keyboard = custom_text or "You need an active room:", manage_rooms_keyboard(has_active_room=False)

        if state:
            await state.clear()
    else:
        text, keyboard = "👋 Welcome! Let's get you registered.\n\nWhat's your name?", ReplyKeyboardRemove()
        await state.set_state(RegistrationStates.name)

    return text, keyboard
