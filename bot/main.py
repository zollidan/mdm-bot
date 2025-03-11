from os.path import abspath, dirname
import sys
sys.path.insert(0, dirname(dirname(abspath(__file__))))

import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from bot.config import bot, dp, admin
from bot.database_middleware import DatabaseMiddlewareWithCommit, DatabaseMiddlewareWithoutCommit

from bot.handlers.start import start_router

async def start_bot():
    # try:
    #     await bot.send_message(admin, f'Бот запущен.')
    # except:
    #     pass
    logger.info("Бот запущен.")

async def stop_bot():
    # try:
    #     await bot.send_message(admin, 'Бот остановлен.')
    # except:
    #     pass
    logger.error("Бот остановлен.")

async def main():
    
    # добавление блок управления сессиями и бд 
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    # роутеры
    dp.include_router(start_router)
    
    # команлды старт/стоп
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())