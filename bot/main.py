from os.path import abspath, dirname
import sys

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger

from bot.config import bot, admins, dp
from bot.dao.database_middleware import DatabaseMiddlewareWithoutCommit, DatabaseMiddlewareWithCommit
from bot.user.user_router import user_router

from art import tprint

# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())



async def main():
    
    tprint("mdm-bot")
    
    # Регистрация мидлварей
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    # Регистрация роутеров
    dp.include_router(user_router)

    # Запуск бота в режиме long polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())