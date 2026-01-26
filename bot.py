import asyncio
import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
WEBAPP_URL: str = os.getenv("WEBAPP_URL", "http://localhost:5173")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Initialize bot and dispatcher
bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    """Handler for /start command."""
    # Create keyboard with WebApp button
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛍️ Открыть каталог",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        text=(
            "👋 Добро пожаловать в MDM Bot!\n\n"
            "Нажмите кнопку ниже, чтобы открыть каталог товаров."
        ),
        reply_markup=keyboard
    )


async def main() -> None:
    """Main function to start the bot."""
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
