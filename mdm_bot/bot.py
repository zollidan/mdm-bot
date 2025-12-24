"""
Main bot application entry point
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from art import tprint

from mdm_bot.core import create_tables, settings
from mdm_bot.handlers import start_router

logger = logging.getLogger(__name__)


def setup_logging():
    """Configure logging for the bot"""
    logging.basicConfig(
        filename='mdm_bot.log',
        level=logging.INFO,
        encoding='utf-8',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


async def main() -> None:
    """Initialize and start the bot"""
    # Setup logging
    setup_logging()
    logger.info('Bot started')

    # Print banner
    tprint("MDM BOT")

    # Create database tables
    await create_tables()
    logger.info("Database tables created")

    # Create bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Register routers
    dp.include_router(start_router)

    # Start polling
    logger.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
