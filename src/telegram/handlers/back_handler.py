from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram.helpers import get_first_stage

router = Router()


@router.message(F.text == "🔙 Back")
async def handle_back(message: Message, state: FSMContext | None = None) -> tuple[bool, bool]:
    text, keybaord = await get_first_stage(chat_id=message.from_user.id, state=state)
    await message.reply(text, reply_markup=keybaord)
