import time
import asyncio
from aiogram import BaseMiddleware
from aiogram.types import Message
import pandas as pd
import src.settings.settings as settings
from aiogram.fsm.context import FSMContext
from aiogram.types.base import TelegramObject
from src.handlers.handlers import Form


class AuthMiddleware(BaseMiddleware):
    """
    Middleware для проверки авторизации пользователя
    """
    async def __call__(self, handler, event: TelegramObject, data: dict):
        if isinstance(event, Message):
            user_id = event.from_user.id
            df = pd.read_csv(settings.path_users_db)

            current_state = await data['state'].get_state()
            if user_id not in df['user_id'].values:
                if event.text == '/start' or current_state == Form.name:
                    return await handler(event, data)
                else:
                    await event.answer('Пожалуйста, зарегистрируйтесь, используя команду /start.')
                    return

        return await handler(event, data)
    

class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты отправки сообщений
    """
    def __init__(self):
        super().__init__()
        self.last_message_time = {}

    async def __call__(self, handler, event: TelegramObject, data: dict):
        if isinstance(event, Message):
            user_id = event.from_user.id
            current_time = time.time()

            # Проверка времени последнего сообщения
            if user_id in self.last_message_time:
                elapsed_time = current_time - self.last_message_time[user_id]
                if elapsed_time < 2:
                    message = await event.answer('Подождите 1 секунду перед отправкой следующего сообщения')
                    asyncio.create_task(self.notify_user(event, 1 - elapsed_time, message))
                    return

            # Обновление времени последнего сообщения
            self.last_message_time[user_id] = current_time

        return await handler(event, data)

    async def notify_user(self, event: Message, delay: float, message: Message):
        await asyncio.sleep(delay)
        await event.answer('Можно отправлять сообщения')
        await message.delete()