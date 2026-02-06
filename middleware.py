from aiogram import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        print(f"Получено сообщение: {event.text}")
        return await handler(event, data)
