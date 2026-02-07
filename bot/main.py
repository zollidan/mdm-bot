import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

env_file = Path(__file__).parent.parent / ".env"

load_dotenv(dotenv_path=env_file)

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
WEBAPP_URL: str = os.getenv("WEBAPP_URL", "http://localhost:3000")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Open Web App",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )

    await message.answer(
        "Welcome! Click the button to open the web app:",
        reply_markup=keyboard
    )


async def main():
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
