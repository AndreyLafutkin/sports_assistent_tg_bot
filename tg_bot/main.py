import asyncio
import logging
import os
import csv
import pandas as pd
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

# Импорт файлов проекта
from src.handlers.handlers import router
from src.handlers.handlers_profile import router_profile
from src.handlers.handlers_timer import router_timer
from src.handlers.handlers_workout import router_workout
from src.handlers.handlers_virtual_assistant import router_virtual_assistant
import src.settings.settings as settings
from src.middleware.middleware import AuthMiddleware, RateLimitMiddleware

# Подключение переменных окружения
load_dotenv('config/.env')
TOKEN = os.getenv('TOKEN')


# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def init_db():
    """
    Функция инициализации базы данных
    """
    if not os.path.exists(settings.path_users_db):
        with open(settings.path_users_db, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(settings.parameters_users_db)


async def send_message_to_users():
    """
    Функция отправки сообщения всем пользователям о начале работы бота
    """
    df = pd.read_csv(settings.path_users_db)
    for user in df['user_id']:
        await bot.send_message(chat_id=user, text=f"Бот снова активирован!\n"
                               "Используйте команду /menu для начала работы\n")


async def setup_commands():
    """
    Функция установки команд бота
    """
    bot_commands = []
    for command in settings.list_commands.items():
        bot_commands.append(BotCommand(command=command[0], description=command[1]))
    await bot.set_my_commands(bot_commands)


async def main():
    """
    Основная функция запуска бота
    """
    init_db()
    # Настройка логирования
    logging.basicConfig(force=True, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    dp.startup.register(setup_commands)
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.include_router(router)
    dp.include_router(router_profile)
    dp.include_router(router_timer)
    dp.include_router(router_virtual_assistant)
    dp.include_router(router_workout)
    try:
        print("Бот запущен...")
        await send_message_to_users()
        await dp.start_polling(bot)
    finally:
        print("Бот остановлен")


# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())