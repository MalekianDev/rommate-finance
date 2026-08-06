import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from settings import Settings
from telegram.handlers import back_router, room_router, start_router, transaction_router
from telegram.middlewares.db import DBSessionMiddleware

settings = Settings()
dispatcher = Dispatcher()
dispatcher.update.middleware(DBSessionMiddleware())

dispatcher.include_router(start_router)
dispatcher.include_router(back_router)
dispatcher.include_router(room_router)
dispatcher.include_router(transaction_router)


async def main() -> None:
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
