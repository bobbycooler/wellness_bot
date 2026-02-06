import asyncio
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers.registration import registration_router
from handlers.loggers import logger_router
from middleware import LoggingMiddleware

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(LoggingMiddleware())
dp.include_router(logger_router)
dp.include_router(registration_router)


async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
